from fastapi import FastAPI
from loguru import logger
from vision_caption.infrastructure.settings import AppSettings
from vision_caption.infrastructure.server.ws_handler import router as ws_router

# Import dei componenti di dominio e porte
from vision_caption.core.domain.sceneAnalysisResult import SceneAnalysisResult
from vision_caption.core.domain.audio import Audio, AudioFormat
from vision_caption.core.domain.frame import Frame
from vision_caption.core.domain.hand_pose import HandPoseResult
from vision_caption.core.domain.pointing import PointingEvent
from vision_caption.core.domain.pointing_caption import PointingCaption
from vision_caption.core.ports.pointing_image_preparer_port import PointingImages

# Import dei componenti reali (adapters e services)
from vision_caption.adapters.hand_tracking.mediapipe_hand_pose_estimator import (
    MediaPipeHandPoseEstimator,
    MediaPipeHandPoseSettings,
)
from vision_caption.adapters.pointing.opencv_pointing_image_preparer import (
    OpenCVPointingImagePreparer,
    PointingImageSettings,
)
from vision_caption.adapters.scene.SsimSceneDetectorAdapter import SsimSceneDetectorAdapter
from vision_caption.adapters.scene.RfdetrSceneDetectorAdapter import RfdetrSceneDetectorAdapter
from vision_caption.adapters.scene.RfdetrCustomSceneDetectorAdapter import RfdetrCustomSceneDetectorAdapter
from vision_caption.adapters.scene.HybridSceneDetectorAdapter import HybridSceneDetectorAdapter
from vision_caption.adapters.vlm.OpenRouterCaptionGenerator import OpenRouterCaptionGenerator
from vision_caption.adapters.vlm.OpenRouterPointingCaptionGenerator import (
    OpenRouterPointingCaptionGenerator,
)
from vision_caption.adapters.tts.ChatterboxSynthesizer import ChatterboxSynthesizer
from vision_caption.adapters.tts.ElevenLabsSynthesizer import ElevenLabsSynthesizer
from vision_caption.core.services.rate_limiter import RateLimiter
from vision_caption.core.services.caption_pipeline import CaptionPipeline
from vision_caption.core.services.pointing.gesture_recognizer import (
    GestureRecognizerSettings,
    PointingGestureRecognizer,
)
from vision_caption.core.services.pointing.pointing_event_gate import (
    PointingEventGate,
)
from vision_caption.core.services.pointing.pointing_pipeline import (
    PointingPipeline,
)

# --- CLASSI MOCK PER TEST RAPIDI SENZA GPU O SERVIZI ESTERNI ---

class MockSceneDetector:
    async def analyze(self, frame: Frame) -> SceneAnalysisResult:
        logger.warning("[MOCK] Scene Detector: Rilevato cambio scena simulato.")
        return SceneAnalysisResult(is_change=True, detections=(), execution_ms=0.5)

    async def commit(self):
        # No-op: il mock non mantiene stato di keyframe/oggetti.
        ...

class MockCaptionGenerator:
    async def generate(self, frame: Frame):
        logger.warning("[MOCK] VLM Caption Generator: Generata didascalia simulata.")
        yield "Questo è un test simulato del server WebSocket."


class MockHandPoseEstimator:
    async def estimate(self, frame: Frame) -> HandPoseResult:
        return HandPoseResult(frame_id=frame.frame_id)

    async def close(self) -> None:
        ...


class MockPointingCaptionGenerator:
    async def generate(
        self,
        event: PointingEvent,
        images: PointingImages,
    ) -> PointingCaption:
        return PointingCaption(
            target="oggetto simulato",
            description="Un oggetto indicato dalla mano.",
            visible_text=None,
            text_confidence=0.0,
            text_complete=False,
            confidence=1.0,
            needs_repointing=False,
            needs_closer_view=False,
        )

class MockSpeechSynthesizer:
    async def synthesize(self, text: str, language: str = "en") -> Audio:
        logger.warning("[MOCK] TTS: Generato audio silenzioso simulato.")
        # Generiamo un file WAV vuoto minimo (44 byte di intestazione RIFF/WAVE standard)
        dummy_wav = (
            b'RIFF\x24\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00'
            b'\x22\x56\x00\x00\x44\xAC\x00\x00\x02\x00\x10\x00data\x00\x00\x00\x00'
        )
        return Audio(
            audio_format=AudioFormat.WAV,
            audio_bytes=dummy_wav,
            audio_duration=1.0
        )

# --- APP FACTORY ---

def create_app(settings: AppSettings | None = None) -> FastAPI:
    settings = settings or AppSettings.from_env()
    app = FastAPI(title="Vision Caption WebSocket Server")
    app.state.settings = settings

    use_mocks = settings.runtime.use_mocks
    
    if use_mocks:
        logger.info("Initializing server in MOCK MODE (no external dependencies needed)...")
        scene_detector = MockSceneDetector()
        caption_generator = MockCaptionGenerator()
        pointing_caption_generator = MockPointingCaptionGenerator()
        speech_synthesizer = MockSpeechSynthesizer()
        media_pipe_settings = None
    else:
        logger.info("Initializing server in PRODUCTION MODE (loading neural network and adapters)...")
        
        openrouter_api_key = settings.openrouter.api_key
        if not openrouter_api_key:
            logger.error("OPENROUTER_API_KEY environment variable is not set!")
            raise ValueError("OPENROUTER_API_KEY is required in production mode.")

        # Inizializzazione SSIM e RF-DETR
        ssim_detector = SsimSceneDetectorAdapter(
            threshold=settings.auto.ssim.threshold
        )

        # Permettiamo di selezionare il device (cpu, cuda) per supportare hardware AMD/CPU
        device = settings.runtime.device

        # Se è impostato RFDETR_CHECKPOINT usiamo il modello addestrato su dataset
        # custom; altrimenti ripieghiamo sul modello COCO pre-addestrato.
        rfdetr_checkpoint = settings.auto.rfdetr.checkpoint_path
        if rfdetr_checkpoint:
            logger.info(f"Loading CUSTOM RF-DETR checkpoint on device: {device}...")
            rfdetr_detector = RfdetrCustomSceneDetectorAdapter.from_checkpoint(
                checkpoint_path=rfdetr_checkpoint,
                device=device,
                threshold=settings.auto.rfdetr.custom_confidence_threshold,
                optimize=settings.auto.rfdetr.optimize_for_inference,
            )
        else:
            logger.info(f"Loading default COCO RF-DETR model weights on device: {device}...")
            from rfdetr import RFDETRMedium
            rfdetr_model = RFDETRMedium(device=device)
            use_gpu_inference = device.lower() != "cpu"
            inference_dtype = "float16" if use_gpu_inference else "float32"
            if settings.auto.rfdetr.optimize_for_inference:
                logger.info(
                    f"Optimizing RF-DETR for inference "
                    f"(compile={use_gpu_inference}, batch_size=1, "
                    f"dtype={inference_dtype})..."
                )
                rfdetr_model.optimize_for_inference(
                    compile=use_gpu_inference,
                    batch_size=1,
                    dtype=inference_dtype,
                )
            rfdetr_detector = RfdetrSceneDetectorAdapter(
                model=rfdetr_model,
                threshold=settings.auto.rfdetr.confidence_threshold,
            )

        if settings.auto.rfdetr.warmup_enabled:
            logger.info("Warming up RF-DETR before accepting user frames...")
            rfdetr_detector.warm_up(
                width=settings.auto.rfdetr.warmup_width,
                height=settings.auto.rfdetr.warmup_height,
            )

        # Rilevatore Ibrido
        scene_detector = HybridSceneDetectorAdapter(
            ssim_detector=ssim_detector,
            rfdetr_detector=rfdetr_detector,
            suppress_unchanged_class_counts=(
                settings.auto.suppress_unchanged_class_counts
            ),
            semantic_box_iou_threshold=(
                settings.auto.semantic_box_iou_threshold
            ),
        )
        
        # Adapters per VLM (OpenRouter) e TTS
        vlm_model = settings.openrouter.model_name
        logger.info(f"Using VLM model for captioning: {vlm_model}")
        caption_generator = OpenRouterCaptionGenerator(
            api_key=openrouter_api_key,
            model_name=vlm_model,
            base_url=settings.openrouter.base_url,
            max_tokens=settings.auto.vlm.max_output_tokens,
            temperature=settings.auto.vlm.temperature,
            timeout_seconds=settings.auto.vlm.http_timeout_seconds,
        )
        pointing_caption_generator = OpenRouterPointingCaptionGenerator(
            api_key=openrouter_api_key,
            model_name=vlm_model,
            base_url=settings.openrouter.base_url,
            timeout_seconds=settings.pointing.vlm.timeout_seconds,
            max_tokens=settings.pointing.vlm.max_output_tokens,
            temperature=settings.pointing.vlm.temperature,
        )
        media_pipe_settings = MediaPipeHandPoseSettings(
            model_path=settings.pointing.media_pipe.model_path,
            inference_max_side=settings.pointing.media_pipe.inference_max_side,
            num_hands=settings.pointing.media_pipe.num_hands,
            min_hand_detection_confidence=(
                settings.pointing.media_pipe.min_hand_detection_confidence
            ),
            min_hand_presence_confidence=(
                settings.pointing.media_pipe.min_hand_presence_confidence
            ),
            min_tracking_confidence=(
                settings.pointing.media_pipe.min_tracking_confidence
            ),
        )
        
        if settings.tts.elevenlabs_api_key:
            logger.info("ELEVENLABS_API_KEY found. Using ultra-fast ElevenLabs TTS engine.")
            speech_synthesizer = ElevenLabsSynthesizer(
                api_key=settings.tts.elevenlabs_api_key,
                voice_id=settings.tts.elevenlabs_voice_id,
                model_id=settings.tts.elevenlabs_model_id,
                timeout_seconds=settings.tts.elevenlabs_timeout_seconds,
            )
        else:
            logger.info("ELEVENLABS_API_KEY missing. Falling back to local Chatterbox TTS.")
            speech_synthesizer = ChatterboxSynthesizer(
                base_url=settings.tts.chatterbox_url,
                timeout_seconds=settings.tts.chatterbox_timeout_seconds,
                voice=settings.tts.chatterbox_voice,
                speed=settings.tts.chatterbox_speed,
                exaggeration=settings.tts.chatterbox_exaggeration,
                cfg_weight=settings.tts.chatterbox_cfg_weight,
                temperature=settings.tts.chatterbox_temperature,
            )

    image_preparer = OpenCVPointingImagePreparer(
        settings=PointingImageSettings(
            start_half_width_ratio=(
                settings.pointing.corridor.start_half_width_ratio
            ),
            min_end_half_width_ratio=(
                settings.pointing.corridor.min_end_half_width_ratio
            ),
            expansion_ratio=settings.pointing.corridor.expansion_ratio,
            overlay_alpha=settings.pointing.corridor.overlay_alpha,
            outside_brightness=(
                settings.pointing.corridor.outside_brightness
            ),
            crop_padding_ratio=(
                settings.pointing.corridor.crop_padding_ratio
            ),
            jpeg_quality=settings.pointing.corridor.jpeg_quality,
            guide_color_bgr=settings.pointing.corridor.color_bgr,
            debug_save_images=(
                settings.pointing.debug.save_prepared_images
            ),
            debug_output_dir=settings.pointing.debug.output_dir,
        )
    )
    gesture_settings = GestureRecognizerSettings(
        index_activation_min_angle_deg=(
            settings.pointing.gesture.index_activation_min_angle_deg
        ),
        index_hold_min_angle_deg=(
            settings.pointing.gesture.index_hold_min_angle_deg
        ),
        other_finger_activation_max_angle_deg=(
            settings.pointing.gesture.other_finger_activation_max_angle_deg
        ),
        other_finger_hold_max_angle_deg=(
            settings.pointing.gesture.other_finger_hold_max_angle_deg
        ),
        thumb_activation_max_palm_ratio=(
            settings.pointing.gesture.thumb_activation_max_palm_ratio
        ),
        thumb_hold_max_palm_ratio=(
            settings.pointing.gesture.thumb_hold_max_palm_ratio
        ),
        angle_ema_alpha=settings.pointing.gesture.angle_ema_alpha,
        ray_ema_alpha=settings.pointing.gesture.ray_ema_alpha,
        confirmation_seconds=settings.pointing.gesture.confirmation_seconds,
        release_seconds=settings.pointing.gesture.release_seconds,
        min_pointing_vector_length=(
            settings.pointing.gesture.min_pointing_vector_length
        ),
    )

    def create_pipeline() -> CaptionPipeline:
        if use_mocks:
            hand_pose_estimator = MockHandPoseEstimator()
        else:
            hand_pose_estimator = MediaPipeHandPoseEstimator(
                settings=media_pipe_settings
            )

        pointing_pipeline = PointingPipeline(
            hand_pose_estimator=hand_pose_estimator,
            gesture_recognizer=PointingGestureRecognizer(
                settings=gesture_settings
            ),
            event_gate=PointingEventGate(
                cooldown_seconds=(
                    settings.pointing.gesture.event_cooldown_seconds
                )
            ),
            image_preparer=image_preparer,
            caption_generator=pointing_caption_generator,
            speech_synthesizer=speech_synthesizer,
        )
        return CaptionPipeline(
            scene_detector=scene_detector,
            caption_generator=caption_generator,
            speech_synthesizer=speech_synthesizer,
            rate_limiter=RateLimiter(
                min_interval_seconds=(
                    settings.auto.min_caption_interval_seconds
                )
            ),
            pointing_pipeline=pointing_pipeline,
            max_frame_age_seconds=settings.auto.max_frame_age_seconds,
            vlm_chunk_timeout_seconds=settings.auto.vlm.chunk_timeout_seconds,
            caption_similarity_threshold=(
                settings.auto.caption_similarity_threshold
            ),
        )

    # Lo stato temporale POINTING e il rate limiter nascono per connessione.
    app.state.pipeline_factory = create_pipeline
    # Compatibilità con integrazioni che recuperano ancora una pipeline diretta.
    app.state.pipeline = create_pipeline()

    # Registriamo le rotte del websocket
    app.include_router(ws_router)

    # Health check
    @app.get("/health")
    def health():
        return {"status": "ok", "mode": "mock" if use_mocks else "production"}

    return app
