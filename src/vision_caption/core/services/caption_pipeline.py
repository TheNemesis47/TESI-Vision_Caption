from vision_caption.core.ports.SceneDetectorPort import SceneDetectorPort
from vision_caption.core.ports.CaptionGeneratorPort import CaptionGeneratorPort
from vision_caption.core.ports.SpeechSynthesizerPort import SpeechSynthesizerPort
from vision_caption.core.services.rate_limiter import RateLimiter
from vision_caption.core.domain.frame import Frame, CaptionMode
from vision_caption.core.domain.audio import Audio

class CaptionPipeline:
    def __init__(
        self,
        scene_detector: SceneDetectorPort,
        caption_generator: CaptionGeneratorPort,
        speech_synthesizer: SpeechSynthesizerPort,
        rate_limiter: RateLimiter
    ):
        self._scene_detector = scene_detector
        self._caption_generator = caption_generator
        self._speech_synthesizer = speech_synthesizer
        self._rate_limiter = rate_limiter

    async def process(self, frame: Frame) -> Audio | None:
        # 1. Se siamo in modalità manuale (POINTING), bypassiamo SSIM e Rate Limiter
        if frame.caption_mode == CaptionMode.POINTING:
            # Chiamata al generatore di didascalie (OpenRouter/Gemma)
            caption_text = await self._caption_generator.generate(frame)
            
            # Sintesi vocale dell'output
            audio_result = await self._speech_synthesizer.synthesize(caption_text)
            return audio_result
            
        # 2. Altrimenti (modalità AUTO), eseguiamo i controlli a cascata
        # Analizziamo la scena per rilevare cambiamenti
        scene_result = await self._scene_detector.analyze(frame)
        if not scene_result.is_change:
            return None
            
        # Verifichiamo se è trascorso l'intervallo minimo di rate limit
        if not self._rate_limiter.can_execute():
            return None
            
        # Registriamo l'esecuzione corrente nel rate limiter
        self._rate_limiter.record()
        
        # Chiamata al generatore di didascalie (passando il frame)
        caption_text = await self._caption_generator.generate(frame)
        
        # Sintesi vocale
        audio_result = await self._speech_synthesizer.synthesize(caption_text)
        return audio_result
