import asyncio
import base64
import json
from collections.abc import Callable
from time import perf_counter
from urllib.parse import urlencode

import httpx
from websockets.asyncio.client import connect
from loguru import logger
from vision_caption.core.ports.SpeechSynthesizerPort import SpeechSynthesizerPort
from vision_caption.core.domain.audio import Audio, AudioFormat

class ElevenLabsSynthesizer(SpeechSynthesizerPort):
    def __init__(
        self,
        api_key: str,
        voice_id: str = "21m00Tcm4TlvDq8ikWAM",
        model_id: str = "eleven_turbo_v2_5",
        timeout_seconds: float = 10.0,
        metrics_callback: Callable[[dict], None] | None = None,
    ):
        # "eleven_turbo_v2_5" è il modello a bassissima latenza (~250ms) che supporta 32 lingue incluso l'Italiano.
        self._api_key = api_key
        self._voice_id = voice_id
        self._model_id = model_id
        self._timeout_seconds = timeout_seconds
        self._metrics_callback = metrics_callback
        self._base_url = "https://api.elevenlabs.io/v1/text-to-speech"
        
    async def synthesize(self, text: str, language: str = "it") -> Audio:
        if self._model_id == "eleven_v4_turbo":
            return await self._synthesize_dialogue(text, language)
        started = perf_counter()
        url = f"{self._base_url}/{self._voice_id}?output_format=mp3_44100_128"
        headers = {
            "xi-api-key": self._api_key,
            "Content-Type": "application/json"
        }
        payload = {
            "text": text,
            "model_id": self._model_id,
            "language_code": language,
            "apply_text_normalization": "on",
        }
        
        async with httpx.AsyncClient() as client:
            # Tempo di timeout breve, ElevenLabs deve rispondere quasi istantaneamente
            response = await client.post(
                url,
                headers=headers,
                json=payload,
                timeout=self._timeout_seconds,
            )
            
            if response.status_code != 200:
                logger.error(f"ElevenLabs API Error: {response.text}")
                response.raise_for_status()
                
            audio_bytes = response.content
            if self._metrics_callback:
                self._metrics_callback({
                    "model_id": self._model_id,
                    "first_chunk_ms": None,  # La chiamata HTTP attuale è bufferizzata.
                    "total_ms": round((perf_counter() - started) * 1000, 1),
                })
            
            # Stima algoritmica della durata dell'audio per l'MP3 (usata per i ritardi del FE)
            word_count = len(text.split())
            estimated_duration = max(1.0, word_count / 2.16)
            
            return Audio(
                audio_format=AudioFormat.MP3,
                audio_bytes=audio_bytes,
                audio_duration=estimated_duration
            )

    async def _synthesize_dialogue(self, text: str, language: str) -> Audio:
        """v4 Turbo richiede Text to Dialogue WS, non il vecchio endpoint TTS.

        La porta attuale restituisce un Audio completo: il primo chunk è una
        metrica del provider, non l'avvio della riproduzione sul telefono.
        """
        query = urlencode({
            "model_id": self._model_id, "output_format": "mp3_44100_128",
            "language_code": language,
        })
        uri = f"wss://api.elevenlabs.io/v1/text-to-dialogue/stream-input?{query}"
        started = perf_counter()
        first_chunk_ms = None
        chunks = []
        async with asyncio.timeout(self._timeout_seconds):
            async with connect(uri, additional_headers={"xi-api-key": self._api_key}) as socket:
                await socket.send(json.dumps({"voices": [self._voice_id]}))
                await socket.send(json.dumps({"inputs": [{"text": text, "voice_id": self._voice_id}]}))
                await socket.send(json.dumps({"close_socket": True}))
                async for raw in socket:
                    message = json.loads(raw)
                    if message.get("error") or message.get("error_type"):
                        raise RuntimeError("ElevenLabs Text to Dialogue ha rifiutato la sintesi")
                    if message.get("audio"):
                        chunk = base64.b64decode(message["audio"], validate=True)
                        if chunk:
                            if first_chunk_ms is None:
                                first_chunk_ms = round((perf_counter() - started) * 1000, 1)
                            chunks.append(chunk)
                    if message.get("is_final"):
                        break
        if not chunks:
            raise RuntimeError("ElevenLabs Text to Dialogue non ha restituito audio")
        metrics = {
            "model_id": self._model_id, "first_chunk_ms": first_chunk_ms,
            "total_ms": round((perf_counter() - started) * 1000, 1),
        }
        logger.debug("ELEVENLABS_METRIC {}", metrics)
        if self._metrics_callback:
            self._metrics_callback(metrics)
        return Audio(
            audio_format=AudioFormat.MP3, audio_bytes=b"".join(chunks),
            audio_duration=max(1.0, len(text.split()) / 2.16),
        )
