import httpx
from loguru import logger
from vision_caption.core.ports.SpeechSynthesizerPort import SpeechSynthesizerPort
from vision_caption.core.domain.audio import Audio, AudioFormat

class ElevenLabsSynthesizer(SpeechSynthesizerPort):
    def __init__(self, api_key: str, voice_id: str = "21m00Tcm4TlvDq8ikWAM", model_id: str = "eleven_turbo_v2_5"):
        # "eleven_turbo_v2_5" è il modello a bassissima latenza (~250ms) che supporta 32 lingue incluso l'Italiano.
        self._api_key = api_key
        self._voice_id = voice_id
        self._model_id = model_id
        self._base_url = "https://api.elevenlabs.io/v1/text-to-speech"
        
    async def synthesize(self, text: str, language: str = "it") -> Audio:
        url = f"{self._base_url}/{self._voice_id}?output_format=mp3_44100_128"
        headers = {
            "xi-api-key": self._api_key,
            "Content-Type": "application/json"
        }
        payload = {
            "text": text,
            "model_id": self._model_id,
            # Niente settings complessi, lasciamo il default del modello per la massima velocità
        }
        
        async with httpx.AsyncClient() as client:
            # Tempo di timeout breve, ElevenLabs deve rispondere quasi istantaneamente
            response = await client.post(url, headers=headers, json=payload, timeout=10.0)
            
            if response.status_code != 200:
                logger.error(f"ElevenLabs API Error: {response.text}")
                response.raise_for_status()
                
            audio_bytes = response.content
            
            # Stima algoritmica della durata dell'audio per l'MP3 (usata per i ritardi del FE)
            word_count = len(text.split())
            estimated_duration = max(1.0, word_count / 2.16)
            
            return Audio(
                audio_format=AudioFormat.MP3,
                audio_bytes=audio_bytes,
                audio_duration=estimated_duration
            )
