import base64
import json

import httpx
from pydantic import ValidationError

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


def build_pointing_prompt(event: PointingEvent) -> str:
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

Analizza il corridoio dalla punta verso il bordo. Scegli l'oggetto fisico
delimitato più allineato con la linea centrale. Ignora la mano e il corpo della
persona che punta. Non inventare dettagli e non inferire attributi personali.
Se il bersaglio è una persona, usa soltanto il termine neutro "persona".

Usa il CONTESTO per riconoscere la scena, il FOCUS per verificare
l'allineamento e l'immagine PULITA per trascrivere esclusivamente il testo che
appartiene al bersaglio. Non tradurre né completare testo incerto. Se non c'è
testo leggibile usa null. Se due oggetti sono indistinguibili, usa confidence
bassa, inseriscili nelle alternatives e imposta needs_repointing=true.

Rispondi esclusivamente con un oggetto JSON nel formato:
{{
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
}}"""


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


def build_pointing_payload(
    *,
    event: PointingEvent,
    images: PointingImages,
    model_name: str,
    max_tokens: int,
    temperature: float = 0.1,
) -> dict:
    content: list[dict] = [
        {"type": "text", "text": build_pointing_prompt(event)},
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
    return {
        "model": model_name,
        "messages": [{"role": "user", "content": content}],
        "temperature": temperature,
        "max_tokens": max_tokens,
        "response_format": {"type": "json_object"},
    }


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


def parse_pointing_caption(content: str) -> PointingCaption | None:
    stripped = content.strip()
    if stripped.startswith("```"):
        lines = stripped.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        stripped = "\n".join(lines).strip()

    try:
        payload = json.loads(stripped)
        return PointingCaption.model_validate(payload)
    except (json.JSONDecodeError, ValidationError):
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
    ) -> None:
        self._api_key = api_key
        self._model_name = model_name
        self._url = f"{base_url.rstrip('/')}/chat/completions"
        self._timeout_seconds = timeout_seconds
        self._max_tokens = max_tokens
        self._temperature = temperature
        self._client = client

    async def generate(
        self,
        event: PointingEvent,
        images: PointingImages,
    ) -> PointingCaption | None:
        payload = build_pointing_payload(
            event=event,
            images=images,
            model_name=self._model_name,
            max_tokens=self._max_tokens,
            temperature=self._temperature,
        )
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/vision-caption",
            "X-Title": "Vision Caption Server",
        }

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
        response_payload = response.json()
        if not isinstance(response_payload, dict):
            return None
        content = _extract_assistant_content(response_payload)
        if content is None:
            return None
        return parse_pointing_caption(content)
