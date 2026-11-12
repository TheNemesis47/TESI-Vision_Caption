from datetime import datetime
from dataclasses import replace
from fastapi import FastAPI
from loguru import logger
from vision_caption.infrastructure.settings import AppSettings
from vision_caption.infrastructure.server.ws_handler import router as ws_router
from vision_caption.infrastructure.server.static_frontend import mount_frontend
from vision_caption.infrastructure.server.research import (
    ResearchSessions,
    app_version,
    router as research_router,
)

# Import dei componenti di dominio e porte
from vision_caption.core.domain.sceneAnalysisResult import SceneAnalysisResult
from vision_caption.core.domain.audio import Audio, AudioFormat
from vision_caption.core.domain.frame import Frame
from vision_caption.core.domain.hand_pose import HandPoseResult
from vision_caption.core.domain.pointing import PointingEvent
from vision_caption.core.domain.pointing_caption import PointingCaption
from vision_caption.core.ports.pointing_image_preparer_port import PointingImages
from vision_caption.core.ports.research_recorder_port import ResearchRecorderPort
from vision_caption.core.ports.caption_sample_store_port import (
    CaptionSampleStorePort,
    NullCaptionSampleStore,
)
from vision_caption.adapters.research.file_caption_sample_store import (
    FileCaptionSampleStore,
)

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
from vision_caption.adapters.vlm.prompts import auto_prompt, register_profile
from vision_caption.adapters.vlm.OpenRouterPointingCaptionGenerator import (
    OpenRouterPointingCaptionGenerator,
)
from vision_caption.adapters.tts.ChatterboxSynthesizer import ChatterboxSynthesizer
from vision_caption.adapters.tts.ElevenLabsSynthesizer import ElevenLabsSynthesizer
from vision_caption.adapters.tts.FishSpeechSynthesizer import FishSpeechSynthesizer
from vision_caption.core.services.rate_limiter import RateLimiter
from vision_caption.core.services.caption_pipeline import CaptionPipeline
from vision_caption.core.domain.mode_profile import BUILTIN_CONTEXTS
from vision_caption.core.services.described_scene_cache import (
    DescribedSceneCache,
)
from vision_caption.core.services.lesson_memory import LessonMemory
from vision_caption.infrastructure.mode_profiles import load_profiles
from vision_caption.core.services.pointing.mode_gesture import (
    ModeGestureDetector,
    ModeGestureSettings,
)
from vision_caption.core.services.speech_text import lesson_speech
from vision_caption.core.services.pointing.stop_gesture import (
    StopGestureDetector,
    StopGestureSettings,
)
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

def _memory_item(context: str, profiles: dict) -> str:
    """La parola con cui la memoria chiama una cosa già descritta."""
    if context == "museum":
        return "opera"
    if context in profiles:
        return profiles[context].memory_item
    return "slide"


def create_app(settings: AppSettings | None = None) -> FastAPI:
    settings = settings or AppSettings.from_env()
    app = FastAPI(title="Vision Caption WebSocket Server")
    app.state.settings = settings

    use_mocks = settings.runtime.use_mocks
    # Le modalità salvate si aggiungono a quelle del codice prima che
    # qualcuno chieda il prompt: da qui in giù una modalità creata
    # dall'utente è indistinguibile da lesson o museum.
    profiles = load_profiles(settings.server.profiles_dir)
    for profile in profiles.values():
        register_profile(profile)
    if settings.vlm.context not in BUILTIN_CONTEXTS and settings.vlm.context not in profiles:
        known = ", ".join([*BUILTIN_CONTEXTS, *sorted(profiles)])
        raise ValueError(
            f"CAPTION_CONTEXT='{settings.vlm.context}' non esiste. "
            f"Modalità disponibili: {known}. "
            f"Le modalità salvate si leggono da {settings.server.profiles_dir}."
        )
    if profiles:
        logger.info(
            "Modalità salvate caricate: {}", ", ".join(sorted(profiles))
        )

    # Le modalità fra cui il telefono può scegliere, col nome da leggere a
    # voce. Viaggiano nella configurazione iniziale del WebSocket: un elenco
    # scritto a mano nel client sarebbe vecchio il giorno dopo.
    available_modes = [
        {"id": name, "label": label}
        for name, label in (
            ("lesson", "Lezione"),
            ("museum", "Museo"),
            ("general", "Generale"),
        )
    ] + [
        {"id": profile.id, "label": profile.name}
        for profile in sorted(profiles.values(), key=lambda item: item.id)
    ]
    app.state.available_modes = available_modes

    # Le funzioni pensate per lo studio (memoria di ciò che è già stato
    # descritto, filtro delle foto mosse, simboli letti a parole, gesto di
    # stop) valgono in ogni contesto guidato: a lezione e al museo cambiano i
    # prompt e le parole della memoria, non la meccanica. La decisione è
    # dentro create_pipeline, perché ora la modalità può essere quella scelta
    # dal telefono e non più soltanto quella dell'avvio.

    if use_mocks:
        logger.info("Initializing server in MOCK MODE (no external dependencies needed)...")
        def make_scene_detector(context: str):
            return MockSceneDetector()

        def make_generators(context: str):
            return MockCaptionGenerator(), MockPointingCaptionGenerator()

        speech_synthesizer = MockSpeechSynthesizer()
        media_pipe_settings = None
    else:
        logger.info("Initializing server in PRODUCTION MODE (loading neural network and adapters)...")
        
        vlm_provider = settings.vlm.resolved_provider
        vlm_base_url = settings.vlm.resolved_base_url
        vlm_model = settings.vlm.resolved_model_name
        logger.info(
            f"VLM: provider={vlm_provider}, modello={vlm_model}, "
            f"endpoint={vlm_base_url}, contesto={settings.vlm.context}"
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

        # Il rilevatore nasce per sessione, non all'avvio: dentro ha la
        # linea di confronto dell'immagine precedente e le classi già
        # annunciate, cioè la memoria di *quella* ripresa. Condividerlo
        # significherebbe che due telefoni collegati insieme si scambiano la
        # scena. Il modello RF-DETR, che è la parte costosa, resta uno solo.
        def make_scene_detector(context: str):
            guided_context = context != "general"
            return HybridSceneDetectorAdapter(
                ssim_detector=SsimSceneDetectorAdapter(
                    threshold=settings.auto.ssim.threshold
                ),
                rfdetr_detector=rfdetr_detector,
                # A lezione la slide cambia mentre gli oggetti restano gli
                # stessi (lo schermo, il docente): il filtro sulle classi
                # tacerebbe ogni nuova slide. Decide SSIM, e la deduplica del
                # testo fa il resto.
                suppress_unchanged_class_counts=(
                    settings.auto.suppress_unchanged_class_counts
                    and not guided_context
                ),
                semantic_box_iou_threshold=(
                    settings.auto.semantic_box_iou_threshold
                ),
                min_sharpness=(
                    settings.auto.lesson_min_sharpness
                    if guided_context and settings.auto.lesson_min_sharpness > 0
                    else None
                ),
            )
        
        # I generatori parlano l'API chat/completions di OpenAI, che vale sia
        # per OpenRouter sia per un Ollama in rete locale: cambia solo
        # l'endpoint. Dentro hanno solo configurazione - nessuna connessione
        # aperta, nessun peso caricato - quindi uno per sessione costa niente,
        # e il prompt può essere quello della modalità che ha scelto chi
        # ascolta invece di quello deciso all'avvio per tutti.
        def make_generators(context: str):
            return (
                OpenRouterCaptionGenerator(
                    api_key=settings.vlm.api_key,
                    model_name=vlm_model,
                    base_url=vlm_base_url,
                    max_tokens=settings.auto.vlm.max_output_tokens,
                    temperature=settings.auto.vlm.temperature,
                    timeout_seconds=settings.auto.vlm.http_timeout_seconds,
                    prompt=auto_prompt(context),
                ),
                OpenRouterPointingCaptionGenerator(
                    api_key=settings.vlm.api_key,
                    model_name=vlm_model,
                    base_url=vlm_base_url,
                    timeout_seconds=settings.pointing.vlm.timeout_seconds,
                    max_tokens=settings.pointing.vlm.max_output_tokens,
                    temperature=settings.pointing.vlm.temperature,
                    context=context,
                    json_mode=vlm_provider == "openrouter",
                    retry_empty_response=(
                        settings.pointing.vlm.retry_empty_response
                    ),
                ),
            )

        if vlm_provider == "local" and settings.vlm.warmup_timeout_seconds > 0:
            logger.info(
                f"Carico il modello visivo {vlm_model}: al primo avvio può "
                "richiedere qualche minuto..."
            )
            make_generators(settings.vlm.context)[0].warm_up(
                settings.vlm.warmup_timeout_seconds
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
        
        if settings.tts.resolved_provider == "elevenlabs":
            logger.info("TTS: ElevenLabs (cloud).")
            speech_synthesizer = ElevenLabsSynthesizer(
                api_key=settings.tts.elevenlabs_api_key,
                voice_id=settings.tts.elevenlabs_voice_id,
                model_id=settings.tts.elevenlabs_model_id,
                timeout_seconds=settings.tts.elevenlabs_timeout_seconds,
            )
        elif settings.tts.resolved_provider == "fish":
            logger.info(f"TTS: Fish Speech locale su {settings.tts.fish_url}.")
            speech_synthesizer = FishSpeechSynthesizer(
                base_url=settings.tts.fish_url,
                timeout_seconds=settings.tts.fish_timeout_seconds,
                reference_id=settings.tts.fish_reference_id,
                seed=settings.tts.fish_seed,
                temperature=settings.tts.fish_temperature,
                top_p=settings.tts.fish_top_p,
            )
        else:
            logger.info(f"TTS: Chatterbox locale su {settings.tts.chatterbox_url}.")
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
        candidate_gap_seconds=settings.pointing.gesture.candidate_gap_seconds,
        min_pointing_vector_length=(
            settings.pointing.gesture.min_pointing_vector_length
        ),
        retarget_enabled=settings.pointing.gesture.retarget_enabled,
        retarget_min_angle_deg=(
            settings.pointing.gesture.retarget_min_angle_deg
        ),
        retarget_min_shift_ratio=(
            settings.pointing.gesture.retarget_min_shift_ratio
        ),
        retarget_stable_angle_deg=(
            settings.pointing.gesture.retarget_stable_angle_deg
        ),
        retarget_stable_shift_ratio=(
            settings.pointing.gesture.retarget_stable_shift_ratio
        ),
    )

    def create_sample_store(
        research_recorder: ResearchRecorderPort | None,
    ) -> CaptionSampleStorePort:
        if not settings.samples.enabled:
            return NullCaptionSampleStore()
        # Stessa sessione del log di ricerca: dalla riga si risale alle immagini.
        session_id = getattr(research_recorder, "session_id", None) or (
            datetime.now().strftime("%Y%m%d-%H%M%S")
        )
        return FileCaptionSampleStore(settings.samples.output_dir / session_id, metadata={
            "app_version": app_version(),
            "vlm_provider": settings.vlm.resolved_provider,
            "vlm_model": settings.vlm.resolved_model_name,
            "caption_context": settings.vlm.context,
            "use_mocks": settings.runtime.use_mocks,
        })

    def create_pipeline(
        research_recorder: ResearchRecorderPort | None = None,
        context: str | None = None,
    ) -> CaptionPipeline:
        """Una pipeline per connessione, nella modalità che le serve.

        La modalità non si cambia dentro una pipeline viva: cambia il prompt,
        la parola con cui la memoria chiama le cose, il filtro sulle classi e
        la soglia di nitidezza. Chi la cambia riceve una pipeline nuova, e
        quello che era stato descritto nel mondo di prima resta lì.
        """
        context = context or settings.vlm.context
        guided_context = context != "general"
        sample_store = create_sample_store(research_recorder)
        # Una memoria per connessione, condivisa fra AUTO e POINTING: le
        # slide di uno studente non finiscono nel contesto di un altro, e il
        # gesto sa a quale slide appartiene la formula indicata.
        lesson_memory = (
            LessonMemory(
                max_notes=settings.auto.lesson_memory_slides,
                max_idle_seconds=settings.auto.lesson_memory_idle_seconds,
                item=_memory_item(context, profiles),
            )
            if guided_context and settings.auto.lesson_memory_slides > 0
            else None
        )
        # L'audio già pronunciato delle slide ricordate: tornare indietro
        # risente quella voce invece di tacere. Una cache per connessione,
        # come la memoria a cui si appoggia.
        scene_cache = (
            DescribedSceneCache(
                max_entries=settings.auto.lesson_memory_slides + 1
            )
            if lesson_memory is not None
            else None
        )
        # Quante parole è una scelta di chi ascolta: la fabbrica resta a
        # disposizione della pipeline, che rifà il filtro quando la scelta
        # cambia a sessione aperta.
        speech_text_factory = lesson_speech if guided_context else None
        speech_text = (
            lesson_speech(settings.auto.lesson_max_words)
            if guided_context
            else None
        )
        caption_generator, pointing_caption_generator = make_generators(context)
        if use_mocks:
            hand_pose_estimator = MockHandPoseEstimator()
        else:
            hand_pose_estimator = MediaPipeHandPoseEstimator(
                settings=media_pipe_settings
            )

        # Uno solo per connessione: il gesto che porta da AUTO a POINTING è
        # lo stesso che riporta indietro, e condividerlo evita il rimbalzo.
        mode_gesture = (
            ModeGestureDetector(
                ModeGestureSettings(
                    hold_seconds=settings.auto.mode_gesture_hold_seconds,
                )
            )
            if settings.auto.mode_gesture
            else None
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
            research_recorder=research_recorder,
            sample_store=sample_store,
            lesson_memory=lesson_memory,
            speech_text=speech_text,
            diagnostics_enabled=settings.pointing.debug.gesture_diagnostics,
            recovery_pose_estimator=(
                MockHandPoseEstimator() if use_mocks else MediaPipeHandPoseEstimator(
                    settings=replace(media_pipe_settings, mirror_input=True, static_image_mode=True)
                )
            ) if settings.pointing.mirror_recovery_enabled else None,
            mode_gesture=mode_gesture,
        )
        return CaptionPipeline(
            scene_detector=make_scene_detector(context),
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
            research_recorder=research_recorder,
            sample_store=sample_store,
            lesson_memory=lesson_memory,
            scene_cache=scene_cache,
            speech_text=speech_text,
            speech_text_factory=speech_text_factory,
            # Lo stesso stimatore delle mani del puntamento: MediaPipe vuole
            # tempi crescenti, e i frame di una connessione arrivano in fila.
            hand_pose_estimator=hand_pose_estimator,
            stop_gesture=(
                StopGestureDetector(
                    StopGestureSettings(
                        hold_seconds=settings.auto.lesson_stop_hold_seconds,
                    )
                )
                if guided_context and settings.auto.lesson_stop_gesture
                else None
            ),
            mode_gesture=mode_gesture,
        )

    # Lo stato temporale POINTING e il rate limiter nascono per connessione.
    app.state.pipeline_factory = create_pipeline
    # Compatibilità con integrazioni che recuperano ancora una pipeline diretta.
    app.state.pipeline = create_pipeline()
    app.state.research_sessions = ResearchSessions(settings)

    # Registriamo le rotte del websocket
    app.include_router(ws_router)
    app.include_router(research_router)

    # Health check
    @app.get("/health")
    def health():
        return {"status": "ok", "mode": "mock" if use_mocks else "production", "app_version": app_version()}

    # Il frontend va montato per ultimo: /health, /docs e /ws/vision devono
    # continuare a essere risolti dalle route backend registrate sopra.
    frontend_dist_path = settings.server.frontend_dist_path
    if mount_frontend(app, frontend_dist_path):
        logger.info(f"Serving frontend build from: {frontend_dist_path}")
    else:
        logger.warning(
            "Frontend build not found at "
            f"{frontend_dist_path}. Backend routes remain available."
        )

    return app
