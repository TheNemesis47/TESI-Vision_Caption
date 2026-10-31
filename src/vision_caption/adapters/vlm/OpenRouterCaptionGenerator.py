import base64
import json
import time

import cv2
import httpx
import numpy as np
from loguru import logger
from vision_caption.core.domain.frame import Frame
from vision_caption.adapters.vlm.prompts import AUTO_PROMPTS
from vision_caption.core.ports.CaptionGeneratorPort import CaptionGeneratorPort

class OpenRouterCaptionGenerator(CaptionGeneratorPort):
    def __init__(
        self,
        api_key: str,
        model_name: str = "google/gemini-2.5-flash",
        base_url: str = "https://openrouter.ai/api/v1",
        max_tokens: int = 80,
        temperature: float = 0.1,
        timeout_seconds: float = 120.0,
        prompt: str = AUTO_PROMPTS["general"],
    ):
        self._api_key = api_key
        self._prompt = prompt
        self._model_name = model_name
        self._base_url = base_url
        self._max_tokens = max_tokens
        self._temperature = temperature
        self._timeout_seconds = timeout_seconds

    def warm_up(self, timeout_seconds: float) -> None:
        """Fa caricare il modello prima che arrivi il primo utente.

        Un server locale come Ollama carica i pesi alla prima richiesta, e da
        un disco lento ci mette più del tempo concesso a una descrizione: le
        prime frasi dopo un riavvio andrebbero perse. Una piccola immagine
        carica anche la parte visiva del modello.
        """
        image = cv2.imencode(".jpg", np.full((64, 64, 3), 255, np.uint8))[1]
        encoded = base64.b64encode(image.tobytes()).decode("ascii")
        headers = {"Content-Type": "application/json"}
        if self._api_key:
            headers["Authorization"] = f"Bearer {self._api_key}"
        payload = {
            "model": self._model_name,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Rispondi solo: ok"},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{encoded}"
                            },
                        },
                    ],
                }
            ],
            "max_tokens": 1,
        }
        started = time.perf_counter()
        try:
            response = httpx.post(
                f"{self._base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=timeout_seconds,
            )
            response.raise_for_status()
        except httpx.HTTPError as error:
            logger.warning(
                f"Modello visivo non pronto dopo il warm-up ({error!r}): "
                "le prime descrizioni potrebbero andare in timeout."
            )
            return
        logger.info(
            f"Modello visivo {self._model_name} pronto in "
            f"{time.perf_counter() - started:.1f}s."
        )

    async def generate(self, frame: Frame, context: str | None = None):
        # Convertiamo i byte JPEG in formato Base64 per la trasmissione HTTP
        base64_image = base64.b64encode(frame.image_bytes).decode("utf-8")
        
        url = f"{self._base_url}/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/vision-caption",  # Tracciamento opzionale richiesto da OpenRouter
            "X-Title": "Vision Caption Server"
        }
        # Un server locale come Ollama non vuole chiavi: "Bearer " vuoto è
        # un header non valido e la richiesta non partirebbe nemmeno.
        if self._api_key:
            headers["Authorization"] = f"Bearer {self._api_key}"
        
        # Struttura del payload
        payload = {
            "model": self._model_name,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": (
                                f"{self._prompt}\n\n{context}"
                                if context
                                else self._prompt
                            ),
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            "max_tokens": self._max_tokens,
            "temperature": self._temperature,
        }

        payload["stream"] = True
        
        async with httpx.AsyncClient() as client:
            # Apriamo uno stream continuo con .stream()
            async with client.stream(
                "POST",
                url,
                headers=headers,
                json=payload,
                timeout=self._timeout_seconds,
            ) as response:
                response.raise_for_status()
                
                buffer = ""
                
                # Leggiamo il flusso riga per riga man mano che i token arrivano via rete
                async for line in response.aiter_lines():
                    line = line.strip()
                    
                    if not line:
                        continue
                        
                    if line == "data: [DONE]":
                        break
                        
                    if line.startswith("data: "):
                        json_str = line[6:] 
                        
                        try:
                            data_chunk = json.loads(json_str)
                            choices = data_chunk.get("choices", [])
                            if choices:
                                delta = choices[0].get("delta", {})
                                if "content" in delta:
                                    frammento = delta["content"]

                                    buffer += frammento
                                    
                        except json.JSONDecodeError:
                            continue
                            
                # Alla fine del ciclo, restituiamo l'ultimo pezzo rimasto
                if buffer.strip():
                    yield buffer.strip()
