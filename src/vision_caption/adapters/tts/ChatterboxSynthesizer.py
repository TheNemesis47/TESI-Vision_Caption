import io
import wave
import httpx
from vision_caption.core.domain.audio import Audio, AudioFormat
from vision_caption.core.ports.SpeechSynthesizerPort import SpeechSynthesizerPort

class ChatterboxSynthesizer(SpeechSynthesizerPort):
    def __init__(self, base_url: str = "http://localhost:4123"):
        self._base_url = base_url

    async def synthesize(self, text: str, language: str = "it") -> Audio:
        url = f"{self._base_url}/v1/audio/speech"
        
        # Struttura del payload richiesto dalle API di Chatterbox
        payload = {
            "input": text,
            "voice": "alloy",
            "response_format": "wav",
            "speed": 1.0,
            "exaggeration": 0.7,
            "cfg_weight": 0.4,
            "temperature": 0.9
        }
        
        # Inviamo la richiesta POST asincrona
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, timeout=30.0)
            response.raise_for_status()
            audio_bytes = response.content

        # Calcoliamo la durata reale dell'audio leggendo i metadati del formato WAV
        duration = 0.0
        try:
            with wave.open(io.BytesIO(audio_bytes), "rb") as wav_file:
                frames = wav_file.getnframes()
                rate = wav_file.getframerate()
                if rate > 0:
                    duration = frames / float(rate)
        except Exception:
            # Fallback se i byte ricevuti non sono un WAV valido o fallisce la lettura
            duration = 0.0

        return Audio(
            audio_format=AudioFormat.WAV,
            audio_bytes=audio_bytes,
            audio_duration=duration
        )
