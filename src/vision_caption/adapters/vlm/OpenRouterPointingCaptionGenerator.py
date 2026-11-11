import asyncio
import base64
import json

import httpx
from loguru import logger
from pydantic import ValidationError

from vision_caption.adapters.vlm.prompts import CaptionContext, pointing_context
from vision_caption.core.domain.pointing import PointingEvent
from vision_caption.core.domain.pointing_caption import PointingCaption
from vision_caption.core.ports.pointing_caption_generator_port import (
    PointingCaptionGeneratorPort,
)
from vision_caption.core.ports.pointing_image_preparer_port import PointingImages


SAFETY_FINISH_REASONS = {
    "content_filter",
    "prohibited_content",
    "safety",
}


def build_pointing_prompt(
    event: PointingEvent,
    context: CaptionContext = "general",
    memory: str | None = None,
) -> str:
    return f"""Sei il modulo visivo di un assistente per l'accessibilità.
Ricevi tre immagini dello stesso istante:
1. CONTESTO: scena completa con il corridoio giallo di puntamento.
2. FOCUS: ritaglio del corridoio; le zone esterne sono oscurate.
3. PULITA PER OCR: scena originale senza guide grafiche.

La linea gialla parte dalla punta dell'indice e indica una direzione, non
necessariamente un oggetto sul bordo.

Informazioni geometriche:
- mano rilevata: {event.handedness.value}
- origine normalizzata: ({event.ray.start.x:.4f}, {event.ray.start.y:.4f})
- fine normalizzata: ({event.ray.end.x:.4f}, {event.ray.end.y:.4f})

Analizza il corridoio dalla punta verso il bordo, includendo ciò che si trova
subito alla punta. Scegli il bersaglio delimitato più allineato con la linea
centrale. Non scegliere testo o immagini fuori dal corridoio solo perché
sono leggibili o già descritti nella memoria. Se nessun bersaglio è
identificabile, usa target=null, description="", needs_repointing=true.
Ignora la mano e il corpo della
persona che punta. Non inventare dettagli e non inferire attributi personali.
Non elencare assenze come "senza bottoni". Per comandi piccoli non
distinguibili usa "controlli", senza indovinare joystick o manopole.
Se il bersaglio è una persona, usa soltanto il termine neutro "persona".
{pointing_context(context)}
Usa il CONTESTO per riconoscere la scena, il FOCUS per verificare
l'allineamento e l'immagine PULITA per trascrivere esclusivamente il testo che
appartiene al bersaglio. Non tradurre né completare testo incerto. Se non c'è
testo leggibile e completo usa null. Non includere frammenti del titolo
che non appartengono al bersaglio. Se due oggetti sono indistinguibili, usa confidence
bassa, inseriscili nelle alternatives e imposta needs_repointing=true.

VERIFICA GEOMETRICA PRIMA DI RISPONDERE:
- La punta è all'origine numerica indicata sopra, non sul testo più evidente.
- Se la punta si sovrappone già a un oggetto o a una figura, considera quel
  bersaglio per primo. Una figura toccata dalla punta ha precedenza sul
  titolo della slide distante dalla punta.
- Un bersaglio interamente dietro l'origine, nel verso opposto al raggio,
  non è indicato. Non leggere titoli o parole esterni al corridoio.
- L'immagine PULITA serve a descrivere il bersaglio selezionato, non a
  sostituirlo con un altro più leggibile. In dubbio chiedi di ripuntare.

Rispondi esclusivamente con un oggetto JSON nel formato:
{{
  "target_kind": "object oppure educational_content oppure unknown",
  "target": "nome sintetico oppure null",
  "description": "descrizione breve dell'oggetto",
  "visible_text": "testo esatto con \\n fra le righe oppure null",
  "text_confidence": 0.0,
  "text_complete": false,
  "confidence": 0.0,
  "candidates": [
    {{
      "label": "nome oggetto",
      "position_along_ray": 0.0,
      "intersects_centerline": true,
      "confidence": 0.0
    }}
  ],
  "alternatives": [],
  "needs_repointing": false,
  "needs_closer_view": false
}}""" + (f"\n\n{memory}" if memory else "")


def _image_content(label: str, image: bytes) -> list[dict]:
    encoded = base64.b64encode(image).decode("ascii")
    return [
        {"type": "text", "text": label},
        {
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{encoded}",
            },
        },
    ]


def pointing_recovery_prompt(event: PointingEvent) -> str:
    """Richiesta breve per recuperare una risposta vuota, senza memoria."""
    return f"""Descrivi in italiano il bersaglio indicato dalla linea gialla.
Tre immagini: CONTESTO completo, FOCUS del corridoio, PULITA senza guide.
La punta è ({event.ray.start.x:.4f}, {event.ray.start.y:.4f}); la linea va
verso ({event.ray.end.x:.4f}, {event.ray.end.y:.4f}), coordinate normalizzate.
Segui il corridoio dalla punta: scegli il primo oggetto identificabile che
intercetta. Basta attraversarne una parte, non occorre colpirne il centro.
Ignora la mano e chi punta. Non scegliere un oggetto laterale fuori dal
corridoio solo perché è più evidente. Se due oggetti sono equivalenti,
usa il nome comune senza inventare particolari. Per una persona usa persona.
Se sul bersaglio c'è testo leggibile - etichetta, cartello, confezione,
titolo, riga di una slide - trascrivilo esattamente in visible_text.
Può essere un oggetto reale oppure il contenuto di una slide: una lezione
non obbliga a scegliere una slide. Descrivi oggetto e colori certi in massimo
venti parole. Non descrivere l'ambiente né testi estranei al bersaglio.
Rispondi solo JSON, senza copiare un elenco di proprietà o uno schema:
{{"target_kind":"object o educational_content o unknown",
"target":"nome del bersaglio oppure null",
"description":"frase breve concreta oppure stringa vuota",
"visible_text":"testo esatto sul bersaglio oppure null",
"text_complete":false,"text_confidence":0.0,
"confidence":0.0,"needs_repointing":false,"needs_closer_view":false}}
Se non puoi riconoscere alcun bersaglio, needs_repointing=true.
"""


def build_pointing_payload(
    *,
    event: PointingEvent,
    images: PointingImages,
    model_name: str,
    max_tokens: int,
    temperature: float = 0.1,
    context: CaptionContext = "general",
    json_mode: bool = True,
    memory: str | None = None,
) -> dict:
    content: list[dict] = [
        {"type": "text", "text": build_pointing_prompt(event, context, memory)},
    ]
    content.extend(
        _image_content("IMMAGINE 1 - CONTESTO COMPLETO", images.context_jpeg)
    )
    content.extend(
        _image_content("IMMAGINE 2 - FOCUS DEL CORRIDOIO", images.focus_jpeg)
    )
    content.extend(
        _image_content("IMMAGINE 3 - SCENA PULITA PER OCR", images.clean_jpeg)
    )
    payload = {
        "model": model_name,
        "messages": [{"role": "user", "content": content}],
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    # Con Ollama la modalità JSON vincolata può non chiudere mai l'oggetto e
    # generare spazi fino a riempire il contesto: in locale basta il prompt,
    # e parse_pointing_caption accetta anche il JSON fra backtick.
    if json_mode:
        payload["response_format"] = {"type": "json_object"}
    return payload


def _extract_assistant_content(payload: dict) -> str | None:
    choices = payload.get("choices")
    if not isinstance(choices, list) or not choices:
        return None
    first_choice = choices[0]
    if not isinstance(first_choice, dict):
        return None
    if first_choice.get("finish_reason") in SAFETY_FINISH_REASONS:
        return None

    message = first_choice.get("message")
    if not isinstance(message, dict):
        return None
    content = message.get("content")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = [
            part["text"]
            for part in content
            if isinstance(part, dict) and isinstance(part.get("text"), str)
        ]
        return "\n".join(parts) if parts else None
    return None


# Campi che un modello locale tende a omettere o a riempire male: mancanti o
# nulli prendono un valore prudente invece di far scartare tutta la risposta.
_CAPTION_DEFAULTS = {
    "target_kind": "unknown",
    "target": None,
    "description": "",
    "visible_text": None,
    "text_confidence": 0.0,
    "text_complete": False,
    "confidence": 0.0,
    "candidates": [],
    "alternatives": [],
    "needs_repointing": False,
    "needs_closer_view": False,
}


def _clamp_unit(value) -> float:
    try:
        return min(1.0, max(0.0, float(value)))
    except (TypeError, ValueError):
        return 0.0


def _normalize_caption_payload(payload: dict) -> dict:
    normalized = {
        key: payload.get(key) if payload.get(key) is not None else default
        for key, default in _CAPTION_DEFAULTS.items()
    }
    if normalized["target_kind"] not in ("object", "educational_content", "unknown"):
        normalized["target_kind"] = "unknown"
    for key in ("text_confidence", "confidence"):
        normalized[key] = _clamp_unit(normalized[key])
    for key in ("text_complete", "needs_repointing", "needs_closer_view"):
        normalized[key] = bool(normalized[key])
    if not isinstance(normalized["description"], str):
        normalized["description"] = str(normalized["description"])
    normalized["alternatives"] = [
        str(item) for item in normalized["alternatives"] or [] if item
    ] if isinstance(normalized["alternatives"], list) else []
    candidates = []
    for item in normalized["candidates"] if isinstance(normalized["candidates"], list) else []:
        if not isinstance(item, dict) or not item.get("label"):
            continue
        candidates.append(
            {
                "label": str(item["label"]),
                "position_along_ray": _clamp_unit(item.get("position_along_ray")),
                "intersects_centerline": bool(item.get("intersects_centerline")),
                "confidence": _clamp_unit(item.get("confidence")),
            }
        )
    normalized["candidates"] = candidates
    return normalized


def parse_pointing_caption(content: str) -> PointingCaption | None:
    # Il JSON può arrivare fra backtick o con una frase prima e dopo: conta
    # l'oggetto fra la prima graffa aperta e l'ultima chiusa.
    start = content.find("{")
    end = content.rfind("}")
    if start == -1 or end <= start:
        return None

    try:
        payload = json.loads(content[start : end + 1])
    except json.JSONDecodeError:
        return None
    if not isinstance(payload, dict):
        return None
    try:
        return PointingCaption.model_validate(_normalize_caption_payload(payload))
    except ValidationError:
        return None


class OpenRouterPointingCaptionGenerator(PointingCaptionGeneratorPort):
    def __init__(
        self,
        api_key: str,
        model_name: str = "google/gemini-2.5-flash",
        base_url: str = "https://openrouter.ai/api/v1",
        timeout_seconds: float = 30.0,
        max_tokens: int = 1200,
        temperature: float = 0.1,
        client: httpx.AsyncClient | None = None,
        context: CaptionContext = "general",
        json_mode: bool = True,
        retry_empty_response: bool = True,
    ) -> None:
        self._api_key = api_key
        self._context = context
        self._json_mode = json_mode
        self._model_name = model_name
        self._url = f"{base_url.rstrip('/')}/chat/completions"
        self._timeout_seconds = timeout_seconds
        self._max_tokens = max_tokens
        self._temperature = temperature
        self._client = client
        self._retry_empty_response = retry_empty_response

    async def generate(
        self,
        event: PointingEvent,
        images: PointingImages,
        context: str | None = None,
    ) -> PointingCaption | None:
        payload = build_pointing_payload(
            event=event,
            images=images,
            model_name=self._model_name,
            max_tokens=self._max_tokens,
            temperature=self._temperature,
            context=self._context,
            json_mode=self._json_mode,
            memory=context,
        )
        headers = {
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/vision-caption",
            "X-Title": "Vision Caption Server",
        }
        # Un server locale come Ollama non vuole chiavi: "Bearer " vuoto è
        # un header non valido e la richiesta non partirebbe nemmeno.
        if self._api_key:
            headers["Authorization"] = f"Bearer {self._api_key}"

        # Il timeout copre entrambi i tentativi: una risposta vuota non deve
        # raddoppiare il tempo massimo di attesa del gesto.
        async with asyncio.timeout(self._timeout_seconds):
            for attempt in range(2 if self._retry_empty_response else 1):
                response_payload = await self._request(payload, headers)
                content = _extract_assistant_content(response_payload)
                caption = parse_pointing_caption(content) if content else None
                if caption is not None and (caption.needs_repointing or caption.needs_closer_view or any((
                    (caption.target or "").strip(), caption.description.strip(),
                    (caption.visible_text or "").strip(),
                ))):
                    if attempt:
                        logger.info("POINTING risposta recuperata: frame={} modello={} tentativo={}", event.frame_id, self._model_name, attempt+1)
                    return caption
                choices = response_payload.get("choices")
                first = choices[0] if isinstance(choices,list) and choices else {}
                finish_reason = first.get("finish_reason") if isinstance(first,dict) else None
                if finish_reason in SAFETY_FINISH_REASONS:
                    return None
                logger.warning(
                    "POINTING senza contenuto utile: frame={} modello={} tentativo={} finish={} risposta={!r}",
                    event.frame_id, self._model_name, attempt+1, finish_reason, (content or "")[:600],
                )
                payload["messages"][0]["content"][0]["text"] = pointing_recovery_prompt(event)
        return None

    async def _request(self, payload: dict, headers: dict) -> dict:
        if self._client is not None:
            response = await self._client.post(
                self._url,
                headers=headers,
                json=payload,
                timeout=self._timeout_seconds,
            )
        else:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self._url,
                    headers=headers,
                    json=payload,
                    timeout=self._timeout_seconds,
                )

        response.raise_for_status()
        payload = response.json()
        return payload if isinstance(payload, dict) else {}
