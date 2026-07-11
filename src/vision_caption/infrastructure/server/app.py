import os
from fastapi import FastAPI
from loguru import logger
from vision_caption.infrastructure.server.ws_handler import router as ws_router

# Import dei componenti di dominio e porte
from vision_caption.core.domain.sceneAnalysisResult import SceneAnalysisResult
from vision_caption.core.domain.audio import Audio, AudioFormat
from vision_caption.core.domain.frame import Frame

# Import dei componenti reali (adapters e services)
from vision_caption.adapters.scene.SsimSceneDetectorAdapter import SsimSceneDetectorAdapter
from vision_caption.adapters.scene.RfdetrSceneDetectorAdapter import RfdetrSceneDetectorAdapter
from vision_caption.adapters.scene.RfdetrCustomSceneDetectorAdapter import RfdetrCustomSceneDetectorAdapter
from vision_caption.adapters.scene.HybridSceneDetectorAdapter import HybridSceneDetectorAdapter
from vision_caption.adapters.vlm.OpenRouterCaptionGenerator import OpenRouterCaptionGenerator
from vision_caption.adapters.tts.ChatterboxSynthesizer import ChatterboxSynthesizer
from vision_caption.adapters.tts.ElevenLabsSynthesizer import ElevenLabsSynthesizer
from vision_caption.core.services.rate_limiter import RateLimiter
from vision_caption.core.services.caption_pipeline import CaptionPipeline

# --- CLASSI MOCK PER TEST RAPIDI SENZA GPU O SERVIZI ESTERNI ---

class MockSceneDetector:
    async def analyze(self, frame: Frame) -> SceneAnalysisResult:
        logger.warning("[MOCK] Scene Detector: Rilevato cambio scena simulato.")
        return SceneAnalysisResult(is_change=True, detections=(), execution_ms=0.5)

    async def commit(self):
        # No-op: il mock non mantiene stato di keyframe/oggetti.
        ...

class MockCaptionGenerator:
    async def generate(self, frame: Frame) -> str:
        logger.warning("[MOCK] VLM Caption Generator: Generata didascalia simulata.")
        return "Questo è un test simulato del server WebSocket."

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

def create_app() -> FastAPI:
    app = FastAPI(title="Vision Caption WebSocket Server")

    use_mocks = os.environ.get("USE_MOCKS", "false").lower() == "true"
    
    if use_mocks:
        logger.info("Initializing server in MOCK MODE (no external dependencies needed)...")
        scene_detector = MockSceneDetector()
        caption_generator = MockCaptionGenerator()
        speech_synthesizer = MockSpeechSynthesizer()
    else:
        logger.info("Initializing server in PRODUCTION MODE (loading neural network and adapters)...")
        
        # Recupero variabili d'ambiente
        openrouter_api_key = os.environ.get("OPENROUTER_API_KEY", "")
        elevenlabs_api_key = os.environ.get("ELEVENLABS_API_KEY", "")
        chatterbox_url = os.environ.get("CHATTERBOX_URL", "http://localhost:4123")
        
        if not openrouter_api_key:
            logger.error("OPENROUTER_API_KEY environment variable is not set!")
            raise ValueError("OPENROUTER_API_KEY is required in production mode.")

        # Inizializzazione SSIM e RF-DETR
        ssim_detector = SsimSceneDetectorAdapter(threshold=0.58)

        # Permettiamo di selezionare il device (cpu, cuda) per supportare hardware AMD/CPU
        device = os.environ.get("DEVICE", "cuda")

        # Se è impostato RFDETR_CHECKPOINT usiamo il modello addestrato su dataset
        # custom; altrimenti ripieghiamo sul modello COCO pre-addestrato.
        rfdetr_checkpoint = os.environ.get("RFDETR_CHECKPOINT", "")
        if rfdetr_checkpoint:
            logger.info(f"Loading CUSTOM RF-DETR checkpoint on device: {device}...")
            rfdetr_detector = RfdetrCustomSceneDetectorAdapter.from_checkpoint(
                checkpoint_path=rfdetr_checkpoint,
                device=device,
                threshold=0.5,
            )
        else:
            logger.info(f"Loading default COCO RF-DETR model weights on device: {device}...")
            from rfdetr import RFDETRMedium
            rfdetr_model = RFDETRMedium(device=device)
            use_gpu_inference = device.lower() != "cpu"
            inference_dtype = "float16" if use_gpu_inference else "float32"
            logger.info(
                f"Optimizing RF-DETR for inference "
                f"(compile={use_gpu_inference}, batch_size=1, dtype={inference_dtype})..."
            )
            rfdetr_model.optimize_for_inference(
                compile=use_gpu_inference,
                batch_size=1,
                dtype=inference_dtype,
            )
            rfdetr_detector = RfdetrSceneDetectorAdapter(model=rfdetr_model)

        # Rilevatore Ibrido
        scene_detector = HybridSceneDetectorAdapter(
            ssim_detector=ssim_detector,
            rfdetr_detector=rfdetr_detector
        )
        
        # Adapters per VLM (OpenRouter) e TTS
        vlm_model = os.environ.get("VLM_MODEL", "google/gemini-2.5-flash")
        logger.info(f"Using VLM model for captioning: {vlm_model}")
        caption_generator = OpenRouterCaptionGenerator(
            api_key=openrouter_api_key,
            model_name=vlm_model,
        )
        
        if elevenlabs_api_key:
            logger.info("ELEVENLABS_API_KEY found. Using ultra-fast ElevenLabs TTS engine.")
            speech_synthesizer = ElevenLabsSynthesizer(api_key=elevenlabs_api_key)
        else:
            logger.info("ELEVENLABS_API_KEY missing. Falling back to local Chatterbox TTS.")
            speech_synthesizer = ChatterboxSynthesizer(base_url=chatterbox_url)

    # Il RateLimiter è comune ad entrambe le modalità
    rate_limiter = RateLimiter(min_interval_seconds=5)

    # Pipeline
    pipeline = CaptionPipeline(
        scene_detector=scene_detector,
        caption_generator=caption_generator,
        speech_synthesizer=speech_synthesizer,
        rate_limiter=rate_limiter
    )

    # Salviamo la pipeline nello stato globale di FastAPI per renderla accessibile agli handler
    app.state.pipeline = pipeline

    # Registriamo le rotte del websocket
    app.include_router(ws_router)

    # Health check
    @app.get("/health")
    def health():
        return {"status": "ok", "mode": "mock" if use_mocks else "production"}

    return app
