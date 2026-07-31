import io
import wave
import httpx
from vision_caption.core.domain.audio import Audio, AudioFormat
from vision_caption.core.ports.SpeechSynthesizerPort import SpeechSynthesizerPort

class ChatterboxSynthesizer(SpeechSynthesizerPort):
    def __init__(
        self,
        base_url: str = "http://localhost:4123",
        *,
        timeout_seconds: float = 120.0,
        voice: str = "alloy",
        speed: float = 1.0,
        exaggeration: float = 0.7,
        cfg_weight: float = 0.4,
        temperature: float = 0.9,
    ):
        self._base_url = base_url
        self._timeout_seconds = timeout_seconds
        self._voice = voice
        self._speed = speed
        self._exaggeration = exaggeration
        self._cfg_weight = cfg_weight
        self._temperature = temperature

    async def synthesize(self, text: str, language: str = "it") -> Audio:
        url = f"{self._base_url}/v1/audio/speech"
        
        # Struttura del payload richiesto dalle API di Chatterbox
        payload = {
            "input": text,
            "voice": self._voice,
            "response_format": "mp3",
            "speed": self._speed,
            "exaggeration": self._exaggeration,
            "cfg_weight": self._cfg_weight,
            "temperature": self._temperature,
        }
        
        # Inviamo la richiesta POST asincrona
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                json=payload,
                timeout=self._timeout_seconds,
            )
            response.raise_for_status()
            audio_bytes = response.content

        # Calcoliamo una durata approssimativa visto che non usiamo più wave
        # Assumiamo circa 15 caratteri al secondo come media di lettura
        duration = len(text) / 15.0

        return Audio(
            audio_format=AudioFormat.MP3,
            audio_bytes=audio_bytes,
            audio_duration=duration
        )
