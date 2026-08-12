import time
import asyncio
from datetime import datetime
from difflib import SequenceMatcher

from loguru import logger
from vision_caption.core.ports.SceneDetectorPort import SceneDetectorPort
from vision_caption.core.ports.CaptionGeneratorPort import CaptionGeneratorPort
from vision_caption.core.ports.SpeechSynthesizerPort import SpeechSynthesizerPort
from vision_caption.core.services.pipeline_metrics import FrameMetrics
from vision_caption.core.services.rate_limiter import RateLimiter
from vision_caption.core.domain.frame import Frame, CaptionMode
from vision_caption.core.domain.captionResult import CaptionResult
from vision_caption.core.services.pointing.pointing_pipeline import (
    PointingPipeline,
)

class CaptionPipeline:
    def __init__(
        self,
        scene_detector: SceneDetectorPort,
        caption_generator: CaptionGeneratorPort,
        speech_synthesizer: SpeechSynthesizerPort,
        rate_limiter: RateLimiter,
        pointing_pipeline: PointingPipeline | None = None,
        max_frame_age_seconds: float = 3.0,
        vlm_chunk_timeout_seconds: float = 3.0,
        caption_similarity_threshold: float = 0.85,
    ):
        self._scene_detector = scene_detector
        self._caption_generator = caption_generator
        self._speech_synthesizer = speech_synthesizer
        self._rate_limiter = rate_limiter
        self._pointing_pipeline = pointing_pipeline
        self._max_frame_age_seconds = max_frame_age_seconds
        self._vlm_chunk_timeout_seconds = vlm_chunk_timeout_seconds
        self._caption_similarity_threshold = caption_similarity_threshold
        self._last_caption = ""
        self._last_mode: CaptionMode | None = None

    async def process(
        self,
        frame: Frame,
        on_detections=None,
        on_pointing_overlay=None,
    ):
        previous_mode = self._last_mode
        if previous_mode is not None and frame.caption_mode != previous_mode:
            if self._pointing_pipeline is not None:
                self._pointing_pipeline.reset()
        self._last_mode = frame.caption_mode

        # 1. POINTING usa esclusivamente la pipeline a innesco gestuale.
        if frame.caption_mode == CaptionMode.POINTING:
            if self._pointing_pipeline is None:
                logger.warning(
                    "Frame POINTING ignorato: pipeline POINTING non configurata."
                )
                return
            async for result in self._pointing_pipeline.process(
                frame,
                on_overlay=on_pointing_overlay,
            ):
                yield result
            return

        if previous_mode == CaptionMode.POINTING and on_pointing_overlay:
            await on_pointing_overlay((), frame.frame_id)

        # 2. Altrimenti (modalità AUTO), eseguiamo i controlli a cascata
        # Analizziamo la scena per rilevare cambiamenti
        metrics = FrameMetrics(frame_id=frame.frame_id)

        logger.debug("Analyzing scene for changes...")
        t_detect_start = time.perf_counter()
        scene_result = await self._scene_detector.analyze(frame)
        t_detect_end = time.perf_counter()

        metrics.detect_ms = round(
            (t_detect_end - t_detect_start) * 1000.0,
            1,
        )
        if on_detections:
            await on_detections(
                scene_result.detections,
                frame.frame_id,
            )
        metrics.ssim_score = scene_result.ssim_score
        metrics.detections = len(scene_result.detections)
        logger.debug(
            "Scene detection completed in "
            f"{(t_detect_end - t_detect_start) * 1000:.1f}ms "
            f"(SSIM score: {scene_result.ssim_score or 1.0:.3f})"
        )

        if not scene_result.is_change:
            metrics.emit(f"suppressed_{scene_result.suppressed_by or 'unknown'}")
            return
            
        # Verifichiamo se è trascorso l'intervallo minimo di rate limit
        if not self._rate_limiter.can_execute():
            logger.debug(
                "Change detected, but rate limiter blocked execution "
                "(too frequent)."
            )
            metrics.emit("rate_limited")
            return
        
        logger.info("Significant scene change detected! Starting captioning pipeline...")
        if scene_result.detections:
            detections_summary = ", ".join([d.class_name for d in scene_result.detections])
            logger.info(f"Detections found: {detections_summary}")

        def frame_age() -> float:
            """Età del frame in secondi, misurata con l'orologio del server."""
            return (datetime.now() - frame.timestamp).total_seconds()

        # FRESHNESS GUARD (pre-VLM): se il frame è già vecchio prima ancora di
        # iniziare, non ha senso spendere VLM+TTS su una scena superata.
        if frame_age() > self._max_frame_age_seconds:
            logger.warning(
                f"Frame {frame.frame_id} già obsoleto ({frame_age():.2f}s > "
                f"{self._max_frame_age_seconds}s) prima del VLM. Pipeline saltata."
            )
            metrics.emit("stale_pre_vlm")
            return

        # Chiamata al generatore di didascalie (passando il frame) IN STREAMING
        logger.info("Calling VLM Caption Generator (Streaming)...")


        # Iteriamo manualmente sul generatore per poter imporre un TIMEOUT VLM
        # su ogni chunk: se un chunk non arriva entro il timeout configurato,
        # abortiamo.
        agen = self._caption_generator.generate(frame)
        t_vlm_start = time.perf_counter()
        outcome = "completed"
        try:
            while True:
                try:
                    chunk_text = await asyncio.wait_for(
                        agen.__anext__(),
                        timeout=self._vlm_chunk_timeout_seconds,
                    )
                except StopAsyncIteration:
                    break
                except asyncio.TimeoutError:
                    logger.warning(
                        f"VLM timeout ({self._vlm_chunk_timeout_seconds}s) "
                        f"sul frame {frame.frame_id}. "
                        f"Caption abortita per non bloccare la pipeline."
                    )
                    outcome = "vlm_timeout"
                    break

                if metrics.vlm_first_chunk_ms is None:
                    metrics.vlm_first_chunk_ms = round(
                        (time.perf_counter() - t_vlm_start) * 1000.0, 1
                    )

                if not chunk_text:
                    continue

                # FRESHNESS GUARD (pre-TTS): non sintetizziamo audio per una scena
                # ormai superata (es. VLM lento cumulativo).
                if frame_age() > self._max_frame_age_seconds:
                    logger.warning(
                        f"Frame {frame.frame_id} obsoleto ({frame_age():.2f}s) prima del TTS. "
                        f"Chunk scartato e pipeline interrotta."
                    )
                    outcome = "stale_pre_tts"
                    break

                # Confronto tra caption complete, ignorando maiuscole, spazi e punteggiatura finale
                previous_caption = " ".join(
                    self._last_caption.casefold().split()
                ).strip(".,!?;:")

                current_caption = " ".join(
                    chunk_text.casefold().split()
                ).strip(".,!?;:")

                caption_similarity = SequenceMatcher(
                    None,
                    previous_caption,
                    current_caption,
                    autojunk=False,
                ).ratio()

                if caption_similarity >= self._caption_similarity_threshold:
                    logger.info(
                        f"Caption '{chunk_text}' troppo simile alla precedente "
                        f"({caption_similarity:.3f}); saltata."
                    )
                    metrics.chunks_deduplicated += 1
                    continue

                # Sintesi vocale per il pezzettino
                logger.info(f"Calling TTS for chunk: '{chunk_text}'")
                t_tts_start = time.perf_counter()
                audio_result = await self._speech_synthesizer.synthesize(chunk_text)
                t_tts_end = time.perf_counter()
                metrics.tts_ms.append(round((t_tts_end - t_tts_start) * 1000.0, 1))

                # FRESHNESS GUARD (post-TTS): il TTS potrebbe aver spinto il frame
                # oltre soglia. Non inviamo audio obsoleto (caso frame_id=119).
                if frame_age() > self._max_frame_age_seconds:
                    logger.warning(
                        f"Audio del frame {frame.frame_id} obsoleto ({frame_age():.2f}s) "
                        f"dopo il TTS. Scartato invece di essere inviato."
                    )
                    outcome = "stale_post_tts"
                    break

                if metrics.first_audio_ms is None:
                    metrics.first_audio_ms = round(metrics.elapsed_ms(), 1)
                    metrics.frame_age_at_first_audio_s = round(frame_age(), 3)

                # Il cooldown e la baseline semantica rappresentano ciò che è
                # stato davvero trasformato in audio. Timeout VLM, TTS falliti
                # o frame ormai obsoleti non devono rendere muta la pipeline
                # per i successivi cinque secondi.
                if metrics.chunks_emitted == 0:
                    await self._scene_detector.commit()
                    self._rate_limiter.record()

                self._last_caption = chunk_text
                metrics.chunks_emitted += 1

                # Invece di un return finale, facciamo lo yield per spedire il frammento audio!
                yield CaptionResult(frame_id=frame.frame_id, caption=chunk_text, audio=audio_result)
        finally:
            await agen.aclose()
            metrics.vlm_total_ms = round(
                (time.perf_counter() - t_vlm_start) * 1000.0, 1
            )
            if outcome == "completed" and metrics.chunks_emitted == 0:
                outcome = "no_audio"
            metrics.emit(outcome)

        logger.info("Total AUTO streaming frame processing completed.")

    async def close(self) -> None:
        if self._pointing_pipeline is not None:
            await self._pointing_pipeline.close()
