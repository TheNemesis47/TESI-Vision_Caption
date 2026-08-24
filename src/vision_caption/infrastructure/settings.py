"""Configurazione centralizzata e tipizzata dell'applicazione.

I modelli in questo modulo sono l'unica sorgente dei valori configurabili a
runtime. ``AppSettings.from_env()`` legge le variabili d'ambiente una sola volta
all'avvio; i layer interni ricevono poi soltanto valori già validati.
"""

from collections.abc import Mapping
from os import environ
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


BACKEND_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_FRONTEND_DIST_PATH = (
    BACKEND_ROOT.parent / "TESI-Vision_Caption_Client" / "dist"
)


def resolve_backend_path(value: str | Path) -> Path:
    """Resolve deployment paths independently from the shell working directory."""
    path = Path(value).expanduser()
    if path.is_absolute():
        return path.resolve()
    return (BACKEND_ROOT / path).resolve()


class SettingsModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class ServerSettings(SettingsModel):
    host: str = "127.0.0.1"
    port: int = Field(default=8765, ge=1, le=65535)
    websocket_ping_interval_seconds: float = Field(default=300.0, gt=0.0)
    websocket_ping_timeout_seconds: float = Field(default=300.0, gt=0.0)
    websocket_drain_timeout_seconds: float = Field(default=0.005, ge=0.0)
    frontend_dist_path: Path = DEFAULT_FRONTEND_DIST_PATH
    log_dir: Path = Path("logs")
    log_level: str = "DEBUG"
    auto_input_fps: float = Field(default=2.0, gt=0.0)
    pointing_input_fps: float = Field(default=10.0, gt=0.0)
    websocket_optional_send_timeout_seconds: float = Field(
        default=0.25,
        gt=0.0,
    )


class RuntimeSettings(SettingsModel):
    use_mocks: bool = False
    device: str = "cuda"


class OpenRouterSettings(SettingsModel):
    api_key: str = Field(default="", repr=False)
    base_url: str = "https://openrouter.ai/api/v1"
    model_name: str = "google/gemini-2.5-flash"


class TtsSettings(SettingsModel):
    elevenlabs_api_key: str = Field(default="", repr=False)
    elevenlabs_voice_id: str = "21m00Tcm4TlvDq8ikWAM"
    elevenlabs_model_id: str = "eleven_turbo_v2_5"
    elevenlabs_timeout_seconds: float = Field(default=10.0, gt=0.0)
    chatterbox_url: str = "http://localhost:4123"
    chatterbox_timeout_seconds: float = Field(default=120.0, gt=0.0)
    chatterbox_voice: str = "alloy"
    chatterbox_speed: float = Field(default=1.0, gt=0.0)
    chatterbox_exaggeration: float = Field(default=0.7, ge=0.0)
    chatterbox_cfg_weight: float = Field(default=0.4, ge=0.0)
    chatterbox_temperature: float = Field(default=0.9, ge=0.0)


class SsimSettings(SettingsModel):
    threshold: float = Field(default=0.58, ge=-1.0, le=1.0)


class RfDetrSettings(SettingsModel):
    checkpoint_path: str = ""
    confidence_threshold: float = Field(default=0.60, ge=0.0, le=1.0)
    custom_confidence_threshold: float = Field(default=0.50, ge=0.0, le=1.0)
    optimize_for_inference: bool = True
    warmup_enabled: bool = True
    warmup_width: int = Field(default=640, ge=1)
    warmup_height: int = Field(default=480, ge=1)


class AutoVlmSettings(SettingsModel):
    max_output_tokens: int = Field(default=80, ge=1)
    temperature: float = Field(default=0.1, ge=0.0, le=2.0)
    http_timeout_seconds: float = Field(default=120.0, gt=0.0)
    chunk_timeout_seconds: float = Field(default=3.0, gt=0.0)


class AutoCaptionSettings(SettingsModel):
    ssim: SsimSettings = Field(default_factory=SsimSettings)
    rfdetr: RfDetrSettings = Field(default_factory=RfDetrSettings)
    vlm: AutoVlmSettings = Field(default_factory=AutoVlmSettings)
    min_caption_interval_seconds: float = Field(default=5.0, ge=0.0)
    max_frame_age_seconds: float = Field(default=3.0, gt=0.0)
    caption_similarity_threshold: float = Field(default=0.85, ge=0.0, le=1.0)
    suppress_unchanged_class_counts: bool = True
    semantic_box_iou_threshold: float = Field(default=0.65, ge=0.0, le=1.0)


class MediaPipeSettings(SettingsModel):
    model_path: Path = Path("models/hand_tracking/hand_landmarker.task")
    inference_max_side: int = Field(default=960, ge=0)
    num_hands: int = Field(default=1, ge=1)
    min_hand_detection_confidence: float = Field(default=0.60, ge=0.0, le=1.0)
    min_hand_presence_confidence: float = Field(default=0.60, ge=0.0, le=1.0)
    min_tracking_confidence: float = Field(default=0.60, ge=0.0, le=1.0)


class PointingGestureSettings(SettingsModel):
    index_activation_min_angle_deg: float = Field(default=145.0, ge=0.0, le=180.0)
    index_hold_min_angle_deg: float = Field(default=135.0, ge=0.0, le=180.0)
    other_finger_activation_max_angle_deg: float = Field(
        default=125.0,
        ge=0.0,
        le=180.0,
    )
    other_finger_hold_max_angle_deg: float = Field(
        default=140.0,
        ge=0.0,
        le=180.0,
    )
    thumb_activation_max_palm_ratio: float = Field(default=1.25, ge=0.0)
    thumb_hold_max_palm_ratio: float = Field(default=1.45, ge=0.0)
    angle_ema_alpha: float = Field(default=0.35, gt=0.0, le=1.0)
    ray_ema_alpha: float = Field(default=0.25, gt=0.0, le=1.0)
    confirmation_seconds: float = Field(default=8.0 / 30.0, ge=0.0)
    release_seconds: float = Field(default=5.0 / 30.0, ge=0.0)
    min_pointing_vector_length: float = Field(default=0.0125, ge=0.0)
    event_cooldown_seconds: float = Field(default=3.0, ge=0.0)


class PointingCorridorSettings(SettingsModel):
    start_half_width_ratio: float = Field(default=0.008, ge=0.0)
    min_end_half_width_ratio: float = Field(default=0.03, ge=0.0)
    expansion_ratio: float = Field(default=0.04, ge=0.0)
    overlay_alpha: float = Field(default=0.14, ge=0.0, le=1.0)
    outside_brightness: float = Field(default=0.14, ge=0.0, le=1.0)
    crop_padding_ratio: float = Field(default=0.025, ge=0.0)
    jpeg_quality: int = Field(default=90, ge=1, le=100)
    color_hex: str = "#FFFF00"
    line_width_px: float = Field(default=2.0, gt=0.0)

    @field_validator("color_hex")
    @classmethod
    def validate_color_hex(cls, value: str) -> str:
        normalized = value.strip().upper()
        if (
            len(normalized) != 7
            or not normalized.startswith("#")
            or any(character not in "0123456789ABCDEF" for character in normalized[1:])
        ):
            raise ValueError("color_hex deve usare il formato #RRGGBB")
        return normalized

    @property
    def color_bgr(self) -> tuple[int, int, int]:
        red = int(self.color_hex[1:3], 16)
        green = int(self.color_hex[3:5], 16)
        blue = int(self.color_hex[5:7], 16)
        return blue, green, red

    def websocket_payload(self) -> dict[str, Any]:
        return {
            "coordinate_space": "normalized",
            "width_reference": "short_side",
            "start_half_width_ratio": self.start_half_width_ratio,
            "min_end_half_width_ratio": self.min_end_half_width_ratio,
            "expansion_ratio": self.expansion_ratio,
            "fill_alpha": self.overlay_alpha,
            "color": self.color_hex,
            "line_width_px": self.line_width_px,
        }


class PointingVlmSettings(SettingsModel):
    timeout_seconds: float = Field(default=30.0, gt=0.0)
    max_output_tokens: int = Field(default=1200, ge=1)
    temperature: float = Field(default=0.1, ge=0.0, le=2.0)


class PointingDebugSettings(SettingsModel):
    save_prepared_images: bool = False
    output_dir: Path = Path("artifacts/pointing_debug")


class PointingSettings(SettingsModel):
    media_pipe: MediaPipeSettings = Field(default_factory=MediaPipeSettings)
    gesture: PointingGestureSettings = Field(default_factory=PointingGestureSettings)
    corridor: PointingCorridorSettings = Field(
        default_factory=PointingCorridorSettings
    )
    vlm: PointingVlmSettings = Field(default_factory=PointingVlmSettings)
    debug: PointingDebugSettings = Field(default_factory=PointingDebugSettings)


class AppSettings(SettingsModel):
    server: ServerSettings = Field(default_factory=ServerSettings)
    runtime: RuntimeSettings = Field(default_factory=RuntimeSettings)
    openrouter: OpenRouterSettings = Field(default_factory=OpenRouterSettings)
    tts: TtsSettings = Field(default_factory=TtsSettings)
    auto: AutoCaptionSettings = Field(default_factory=AutoCaptionSettings)
    pointing: PointingSettings = Field(default_factory=PointingSettings)

    @classmethod
    def from_env(
        cls,
        source: Mapping[str, str] | None = None,
    ) -> "AppSettings":
        env = environ if source is None else source

        def value(name: str, default: Any) -> Any:
            return env.get(name, default)

        return cls(
            server=ServerSettings(
                host=value("SERVER_HOST", "127.0.0.1"),
                port=value("SERVER_PORT", 8765),
                websocket_ping_interval_seconds=value(
                    "WS_PING_INTERVAL_SECONDS",
                    300.0,
                ),
                websocket_ping_timeout_seconds=value(
                    "WS_PING_TIMEOUT_SECONDS",
                    300.0,
                ),
                websocket_drain_timeout_seconds=value(
                    "WS_DRAIN_TIMEOUT_SECONDS",
                    0.005,
                ),
                auto_input_fps=value("AUTO_INPUT_FPS", 2.0),
                pointing_input_fps=value("POINTING_INPUT_FPS", 10.0),
                websocket_optional_send_timeout_seconds=value(
                    "WS_OPTIONAL_SEND_TIMEOUT_SECONDS",
                    0.25,
                ),
                frontend_dist_path=resolve_backend_path(
                    value("FRONTEND_DIST_PATH", DEFAULT_FRONTEND_DIST_PATH)
                ),
                log_dir=value("LOG_DIR", "logs"),
                log_level=value("LOG_LEVEL", "DEBUG"),
            ),
            runtime=RuntimeSettings(
                use_mocks=value("USE_MOCKS", False),
                device=value("DEVICE", "cuda"),
            ),
            openrouter=OpenRouterSettings(
                api_key=value("OPENROUTER_API_KEY", ""),
                base_url=value(
                    "OPENROUTER_BASE_URL",
                    "https://openrouter.ai/api/v1",
                ),
                model_name=value("VLM_MODEL", "google/gemini-2.5-flash"),
            ),
            tts=TtsSettings(
                elevenlabs_api_key=value("ELEVENLABS_API_KEY", ""),
                elevenlabs_voice_id=value(
                    "ELEVENLABS_VOICE_ID",
                    "21m00Tcm4TlvDq8ikWAM",
                ),
                elevenlabs_model_id=value(
                    "ELEVENLABS_MODEL_ID",
                    "eleven_turbo_v2_5",
                ),
                elevenlabs_timeout_seconds=value(
                    "ELEVENLABS_TIMEOUT_SECONDS",
                    10.0,
                ),
                chatterbox_url=value(
                    "CHATTERBOX_URL",
                    "http://localhost:4123",
                ),
                chatterbox_timeout_seconds=value(
                    "CHATTERBOX_TIMEOUT_SECONDS",
                    120.0,
                ),
                chatterbox_voice=value("CHATTERBOX_VOICE", "alloy"),
                chatterbox_speed=value("CHATTERBOX_SPEED", 1.0),
                chatterbox_exaggeration=value(
                    "CHATTERBOX_EXAGGERATION",
                    0.7,
                ),
                chatterbox_cfg_weight=value("CHATTERBOX_CFG_WEIGHT", 0.4),
                chatterbox_temperature=value(
                    "CHATTERBOX_TEMPERATURE",
                    0.9,
                ),
            ),
            auto=AutoCaptionSettings(
                ssim=SsimSettings(
                    threshold=value("SSIM_THRESHOLD", 0.58),
                ),
                rfdetr=RfDetrSettings(
                    checkpoint_path=value("RFDETR_CHECKPOINT", ""),
                    confidence_threshold=value("RFDETR_THRESHOLD", 0.60),
                    custom_confidence_threshold=value(
                        "RFDETR_CUSTOM_THRESHOLD",
                        0.50,
                    ),
                    optimize_for_inference=value(
                        "RFDETR_OPTIMIZE_FOR_INFERENCE",
                        True,
                    ),
                    warmup_enabled=value("RFDETR_WARMUP_ENABLED", True),
                    warmup_width=value("RFDETR_WARMUP_WIDTH", 640),
                    warmup_height=value("RFDETR_WARMUP_HEIGHT", 480),
                ),
                vlm=AutoVlmSettings(
                    max_output_tokens=value("AUTO_VLM_MAX_OUTPUT_TOKENS", 80),
                    temperature=value("AUTO_VLM_TEMPERATURE", 0.1),
                    http_timeout_seconds=value(
                        "AUTO_VLM_HTTP_TIMEOUT_SECONDS",
                        120.0,
                    ),
                    chunk_timeout_seconds=value("VLM_TIMEOUT_S", 3.0),
                ),
                min_caption_interval_seconds=value(
                    "MIN_CAPTION_INTERVAL_SECONDS",
                    5.0,
                ),
                max_frame_age_seconds=value("MAX_FRAME_AGE_S", 3.0),
                caption_similarity_threshold=value(
                    "CAPTION_SIMILARITY_THRESHOLD",
                    0.85,
                ),
                suppress_unchanged_class_counts=value(
                    "SUPPRESS_UNCHANGED_CLASS_COUNTS",
                    True,
                ),
                semantic_box_iou_threshold=value(
                    "SEMANTIC_BOX_IOU_THRESHOLD",
                    0.65,
                ),
            ),
            pointing=PointingSettings(
                media_pipe=MediaPipeSettings(
                    model_path=value(
                        "HAND_LANDMARKER_MODEL_PATH",
                        "models/hand_tracking/hand_landmarker.task",
                    ),
                    inference_max_side=value("HAND_INFERENCE_MAX_SIDE", 960),
                    num_hands=value("HAND_NUM_HANDS", 1),
                    min_hand_detection_confidence=value(
                        "HAND_MIN_DETECTION_CONFIDENCE",
                        0.60,
                    ),
                    min_hand_presence_confidence=value(
                        "HAND_MIN_PRESENCE_CONFIDENCE",
                        0.60,
                    ),
                    min_tracking_confidence=value(
                        "HAND_MIN_TRACKING_CONFIDENCE",
                        0.60,
                    ),
                ),
                gesture=PointingGestureSettings(
                    index_activation_min_angle_deg=value(
                        "POINTING_INDEX_ACTIVATION_MIN_ANGLE_DEG",
                        145.0,
                    ),
                    index_hold_min_angle_deg=value(
                        "POINTING_INDEX_HOLD_MIN_ANGLE_DEG",
                        135.0,
                    ),
                    other_finger_activation_max_angle_deg=value(
                        "POINTING_OTHER_FINGER_ACTIVATION_MAX_ANGLE_DEG",
                        125.0,
                    ),
                    other_finger_hold_max_angle_deg=value(
                        "POINTING_OTHER_FINGER_HOLD_MAX_ANGLE_DEG",
                        140.0,
                    ),
                    thumb_activation_max_palm_ratio=value(
                        "POINTING_THUMB_ACTIVATION_MAX_PALM_RATIO",
                        1.25,
                    ),
                    thumb_hold_max_palm_ratio=value(
                        "POINTING_THUMB_HOLD_MAX_PALM_RATIO",
                        1.45,
                    ),
                    angle_ema_alpha=value("POINTING_ANGLE_EMA_ALPHA", 0.35),
                    ray_ema_alpha=value("POINTING_RAY_EMA_ALPHA", 0.25),
                    confirmation_seconds=value(
                        "POINTING_CONFIRMATION_SECONDS",
                        8.0 / 30.0,
                    ),
                    release_seconds=value(
                        "POINTING_RELEASE_SECONDS",
                        5.0 / 30.0,
                    ),
                    min_pointing_vector_length=value(
                        "POINTING_MIN_VECTOR_LENGTH",
                        0.0125,
                    ),
                    event_cooldown_seconds=value(
                        "POINTING_EVENT_COOLDOWN_SECONDS",
                        3.0,
                    ),
                ),
                corridor=PointingCorridorSettings(
                    start_half_width_ratio=value(
                        "POINTING_CORRIDOR_START_HALF_WIDTH_RATIO",
                        0.008,
                    ),
                    min_end_half_width_ratio=value(
                        "POINTING_CORRIDOR_MIN_END_HALF_WIDTH_RATIO",
                        0.03,
                    ),
                    expansion_ratio=value(
                        "POINTING_CORRIDOR_EXPANSION_RATIO",
                        0.04,
                    ),
                    overlay_alpha=value(
                        "POINTING_CORRIDOR_OVERLAY_ALPHA",
                        0.14,
                    ),
                    outside_brightness=value(
                        "POINTING_CORRIDOR_OUTSIDE_BRIGHTNESS",
                        0.14,
                    ),
                    crop_padding_ratio=value(
                        "POINTING_CORRIDOR_CROP_PADDING_RATIO",
                        0.025,
                    ),
                    jpeg_quality=value(
                        "POINTING_CORRIDOR_JPEG_QUALITY",
                        90,
                    ),
                    color_hex=value(
                        "POINTING_CORRIDOR_COLOR_HEX",
                        "#FFFF00",
                    ),
                    line_width_px=value(
                        "POINTING_CORRIDOR_LINE_WIDTH_PX",
                        2.0,
                    ),
                ),
                vlm=PointingVlmSettings(
                    timeout_seconds=value(
                        "POINTING_VLM_TIMEOUT_SECONDS",
                        30.0,
                    ),
                    max_output_tokens=value(
                        "POINTING_VLM_MAX_OUTPUT_TOKENS",
                        1200,
                    ),
                    temperature=value("POINTING_VLM_TEMPERATURE", 0.1),
                ),
                debug=PointingDebugSettings(
                    save_prepared_images=value(
                        "POINTING_DEBUG_SAVE_IMAGES",
                        False,
                    ),
                    output_dir=value(
                        "POINTING_DEBUG_OUTPUT_DIR",
                        "artifacts/pointing_debug",
                    ),
                ),
            ),
        )
