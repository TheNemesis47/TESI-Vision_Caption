import os
import time
import asyncio
import difflib
from datetime import datetime
from difflib import SequenceMatcher

from loguru import logger
from vision_caption.core.ports.SceneDetectorPort import SceneDetectorPort
from vision_caption.core.ports.CaptionGeneratorPort import CaptionGeneratorPort
from vision_caption.core.ports.SpeechSynthesizerPort import SpeechSynthesizerPort
from vision_caption.core.services.rate_limiter import RateLimiter
from vision_caption.core.domain.frame import Frame, CaptionMode
from vision_caption.core.domain.audio import Audio
from vision_caption.core.domain.captionResult import CaptionResult

# --- Soglie di FRESHNESS (configurabili via env) ---
# Età massima di un frame (in secondi) misurata lato server: oltre questa soglia
# caption/audio sono considerati obsoleti e non vengono sintetizzati/inviati.
MAX_FRAME_AGE_S = float(os.environ.get("MAX_FRAME_AGE_S", "3.0"))
# Timeout massimo di attesa per un chunk dal VLM: evita caption che restano
# appese 10s bloccando la pipeline.
VLM_TIMEOUT_S = float(os.environ.get("VLM_TIMEOUT_S", "3.0"))

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
        self._last_caption = ""

    async def process(self, frame: Frame, on_detections=None):
        t_start = time.perf_counter()
        
        #t 1. Se siamo in modalità manuale (POINTING), bypassiamo SSIM e Rae Limiter
        if frame.caption_mode == CaptionMode.POINTING:
            logger.info("Processing manual POINTING frame...")
            
            logger.info("Calling VLM Caption Generator...")
            caption_text = ""
            async for frase in self._caption_generator.generate(frame):
                if not frase:
                    continue
                logger.info(f"VLM Chunk generated: \"{frase}\"")
                caption_text += frase

                logger.info("Calling TTS Speech Synthesizer...")
                t_tts_start = time.perf_counter()
                audio_result = await self._speech_synthesizer.synthesize(frase)
                t_tts_end = time.perf_counter()
                logger.info(f"TTS Speech synthesized in {t_tts_end - t_tts_start:.2f}s (Audio duration: {audio_result.audio_duration:.2f}s)")
                yield CaptionResult(frame_id=frame.frame_id, caption=frase, audio=audio_result)

            logger.info(f"Total POINTING frame processing time: {time.perf_counter() - t_start:.2f}s")
            yield CaptionResult(frame_id=frame.frame_id, caption=caption_text, audio=audio_result)
            return
            
        # 2. Altrimenti (modalità AUTO), eseguiamo i controlli a cascata
        # Analizziamo la scena per rilevare cambiamenti
        logger.debug("Analyzing scene for changes...")
        t_detect_start = time.perf_counter()
        scene_result = await self._scene_detector.analyze(frame)
        # eseguo la callback
        if on_detections:
            await on_detections(scene_result.detections, frame.frame_id)
        t_detect_end = time.perf_counter()
        logger.debug(f"Scene detection completed in {(t_detect_end - t_detect_start) * 1000:.1f}ms (SSIM score: {scene_result.ssim_score or 1.0:.3f})")
        
        if not scene_result.is_change:
            return
            
        # Verifichiamo se è trascorso l'intervallo minimo di rate limit
        if not self._rate_limiter.can_execute():
            logger.info("Change detected, but rate limiter blocked execution (too frequent).")
            return
            
        # Registriamo l'esecuzione corrente nel rate limiter
        self._rate_limiter.record()
        
        logger.info("Significant scene change detected! Starting captioning pipeline...")
        if scene_result.detections:
            detections_summary = ", ".join([d.class_name for d in scene_result.detections])
            logger.info(f"Detections found: {detections_summary}")

        def frame_age() -> float:
            """Età del frame in secondi, misurata con l'orologio del server."""
            return (datetime.now() - frame.timestamp).total_seconds()

        # FRESHNESS GUARD (pre-VLM): se il frame è già vecchio prima ancora di
        # iniziare, non ha senso spendere VLM+TTS su una scena superata.
        if frame_age() > MAX_FRAME_AGE_S:
            logger.warning(
                f"Frame {frame.frame_id} già obsoleto ({frame_age():.2f}s > "
                f"{MAX_FRAME_AGE_S}s) prima del VLM. Pipeline saltata."
            )
            return

        # Chiamata al generatore di didascalie (passando il frame) IN STREAMING
        await self._scene_detector.commit()
        logger.info("Calling VLM Caption Generator (Streaming)...")


        # Iteriamo manualmente sul generatore per poter imporre un TIMEOUT VLM
        # su ogni chunk: se un chunk non arriva entro VLM_TIMEOUT_S, abortiamo.
        agen = self._caption_generator.generate(frame)
        try:
            while True:
                try:
                    chunk_text = await asyncio.wait_for(agen.__anext__(), timeout=VLM_TIMEOUT_S)
                except StopAsyncIteration:
                    break
                except asyncio.TimeoutError:
                    logger.warning(
                        f"VLM timeout ({VLM_TIMEOUT_S}s) sul frame {frame.frame_id}. "
                        f"Caption abortita per non bloccare la pipeline."
                    )
                    break

                if not chunk_text:
                    continue

                # FRESHNESS GUARD (pre-TTS): non sintetizziamo audio per una scena
                # ormai superata (es. VLM lento cumulativo).
                if frame_age() > MAX_FRAME_AGE_S:
                    logger.warning(
                        f"Frame {frame.frame_id} obsoleto ({frame_age():.2f}s) prima del TTS. "
                        f"Chunk scartato e pipeline interrotta."
                    )
                    break

                # Controllo di similarità sul singolo chunk
                caption_difference = SequenceMatcher(None, self._last_caption, chunk_text).ratio()
                if caption_difference > 0.85:
                    logger.info(f"Chunk '{chunk_text}' is too similar to the previous one, skipping.")
                    continue

                self._last_caption = chunk_text

                # Sintesi vocale per il pezzettino
                logger.info(f"Calling TTS for chunk: '{chunk_text}'")
                t_tts_start = time.perf_counter()
                audio_result = await self._speech_synthesizer.synthesize(chunk_text)
                t_tts_end = time.perf_counter()

                # FRESHNESS GUARD (post-TTS): il TTS potrebbe aver spinto il frame
                # oltre soglia. Non inviamo audio obsoleto (caso frame_id=119).
                if frame_age() > MAX_FRAME_AGE_S:
                    logger.warning(
                        f"Audio del frame {frame.frame_id} obsoleto ({frame_age():.2f}s) "
                        f"dopo il TTS. Scartato invece di essere inviato."
                    )
                    break

                # Invece di un return finale, facciamo lo yield per spedire il frammento audio!
                yield CaptionResult(frame_id=frame.frame_id, caption=chunk_text, audio=audio_result)
        finally:
            await agen.aclose()

        logger.info(f"Total AUTO streaming frame processing completed.")

