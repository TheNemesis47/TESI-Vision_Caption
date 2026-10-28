import io
import wave

import httpx

from vision_caption.core.domain.audio import Audio, AudioFormat
from vision_caption.core.ports.SpeechSynthesizerPort import SpeechSynthesizerPort


class FishSpeechSynthesizer(SpeechSynthesizerPort):
    """Voce locale con il server di Fish Speech (modello OpenAudio S1-mini).

    Senza una voce di riferimento il modello ne inventa una a ogni frase: il
    seme fisso la tiene uguale fra una frase e l'altra. Con ``reference_id``
    si usa invece una voce registrata nella cartella references del server.
    """

    def __init__(
        self,
        base_url: str = "http://localhost:8080",
        *,
        timeout_seconds: float = 60.0,
        reference_id: str = "",
        seed: int | None = 42,
        temperature: float = 0.7,
        top_p: float = 0.7,
        chunk_length: int = 200,
    ):
        self._base_url = base_url.rstrip("/")
        self._timeout_seconds = timeout_seconds
        self._reference_id = reference_id or None
        self._seed = seed
        self._temperature = temperature
        self._top_p = top_p
        self._chunk_length = chunk_length

    async def synthesize(self, text: str, language: str = "it") -> Audio:
        payload = {
            "text": text,
            "format": "wav",
            "reference_id": self._reference_id,
            "seed": self._seed,
            # La normalizzazione del server riguarda solo inglese e cinese.
            "normalize": False,
            "streaming": False,
            "chunk_length": self._chunk_length,
            "temperature": self._temperature,
            "top_p": self._top_p,
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self._base_url}/v1/tts",
                json=payload,
                timeout=self._timeout_seconds,
            )
            response.raise_for_status()
            audio_bytes = response.content

        return Audio(
            audio_format=AudioFormat.WAV,
            audio_bytes=audio_bytes,
            audio_duration=wav_duration(audio_bytes),
        )


def wav_duration(audio_bytes: bytes) -> float:
    with wave.open(io.BytesIO(audio_bytes)) as audio:
        return audio.getnframes() / audio.getframerate()
