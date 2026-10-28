import pytest
from pydantic import ValidationError

from vision_caption.infrastructure.settings import (
    AppSettings,
    BACKEND_ROOT,
    PointingCorridorSettings,
)


def test_app_settings_loads_nested_values_from_environment() -> None:
    settings = AppSettings.from_env(
        {
            "USE_MOCKS": "true",
            "FRONTEND_DIST_PATH": "../frontend/dist",
            "SSIM_THRESHOLD": "0.72",
            "RFDETR_THRESHOLD": "0.51",
            "RFDETR_WARMUP_ENABLED": "false",
            "AUTO_INPUT_FPS": "1.5",
            "POINTING_INPUT_FPS": "8",
            "WS_OPTIONAL_SEND_TIMEOUT_SECONDS": "0.4",
            "MIN_CAPTION_INTERVAL_SECONDS": "2.5",
            "SEMANTIC_BOX_IOU_THRESHOLD": "0.7",
            "POINTING_CONFIRMATION_SECONDS": "0.15",
            "POINTING_EVENT_COOLDOWN_SECONDS": "1.5",
            "POINTING_CORRIDOR_COLOR_HEX": "#12abef",
            "POINTING_DEBUG_SAVE_IMAGES": "true",
            "POINTING_DEBUG_OUTPUT_DIR": "tesi/immagini-pointing",
        }
    )

    assert settings.runtime.use_mocks
    assert settings.server.host == "127.0.0.1"
    assert settings.server.frontend_dist_path == (
        BACKEND_ROOT / "../frontend/dist"
    ).resolve()
    assert settings.auto.ssim.threshold == 0.72
    assert settings.auto.rfdetr.confidence_threshold == 0.51
    assert not settings.auto.rfdetr.warmup_enabled
    assert settings.server.auto_input_fps == 1.5
    assert settings.server.pointing_input_fps == 8.0
    assert settings.server.websocket_optional_send_timeout_seconds == 0.4
    assert settings.auto.min_caption_interval_seconds == 2.5
    assert settings.auto.semantic_box_iou_threshold == 0.7
    assert settings.pointing.gesture.confirmation_seconds == 0.15
    assert settings.pointing.gesture.event_cooldown_seconds == 1.5
    assert settings.pointing.corridor.color_hex == "#12ABEF"
    assert settings.pointing.corridor.color_bgr == (239, 171, 18)
    assert settings.pointing.debug.save_prepared_images
    assert str(settings.pointing.debug.output_dir) == "tesi/immagini-pointing"


def test_corridor_settings_exposes_frontend_contract() -> None:
    payload = PointingCorridorSettings().websocket_payload()

    assert payload == {
        "coordinate_space": "normalized",
        "width_reference": "short_side",
        "start_half_width_ratio": 0.008,
        "min_end_half_width_ratio": 0.03,
        "expansion_ratio": 0.04,
        "fill_alpha": 0.14,
        "color": "#FFFF00",
        "line_width_px": 2.0,
    }


def test_invalid_settings_fail_during_startup() -> None:
    with pytest.raises(ValidationError):
        AppSettings.from_env({"SSIM_THRESHOLD": "2.0"})


def test_senza_chiavi_si_va_sui_servizi_locali() -> None:
    settings = AppSettings.from_env({})

    assert settings.vlm.resolved_provider == "local"
    assert settings.vlm.resolved_base_url == "http://localhost:11434/v1"
    assert settings.vlm.resolved_model_name == "gemma3:4b"
    assert settings.tts.resolved_provider == "local"


def test_con_le_chiavi_si_va_sui_servizi_cloud() -> None:
    settings = AppSettings.from_env(
        {"OPENROUTER_API_KEY": "chiave", "ELEVENLABS_API_KEY": "chiave"}
    )

    assert settings.vlm.resolved_provider == "openrouter"
    assert settings.vlm.resolved_base_url == "https://openrouter.ai/api/v1"
    assert settings.vlm.resolved_model_name == "google/gemini-2.5-flash"
    assert settings.tts.resolved_provider == "elevenlabs"


def test_il_provider_dichiarato_vince_sulla_presenza_della_chiave() -> None:
    settings = AppSettings.from_env(
        {
            "VLM_PROVIDER": "local",
            "OPENROUTER_API_KEY": "chiave",
            "TTS_PROVIDER": "local",
            "ELEVENLABS_API_KEY": "chiave",
        }
    )

    assert settings.vlm.resolved_provider == "local"
    assert settings.tts.resolved_provider == "local"


def test_un_provider_cloud_senza_la_sua_chiave_ferma_l_avvio() -> None:
    with pytest.raises(ValidationError):
        AppSettings.from_env({"VLM_PROVIDER": "openrouter"})
    with pytest.raises(ValidationError):
        AppSettings.from_env({"TTS_PROVIDER": "elevenlabs"})


def test_gli_endpoint_locali_restano_configurabili() -> None:
    settings = AppSettings.from_env(
        {
            "VLM_PROVIDER": "local",
            "VLM_BASE_URL": "http://ollama:11434/v1",
            "VLM_MODEL": "qwen2.5vl:7b",
            "CHATTERBOX_URL": "http://chatterbox:4123",
        }
    )

    assert settings.vlm.resolved_base_url == "http://ollama:11434/v1"
    assert settings.vlm.resolved_model_name == "qwen2.5vl:7b"
    assert settings.tts.chatterbox_url == "http://chatterbox:4123"


def test_il_vecchio_nome_dell_endpoint_continua_a_valere() -> None:
    settings = AppSettings.from_env(
        {"OPENROUTER_API_KEY": "chiave", "OPENROUTER_BASE_URL": "http://proxy/v1"}
    )

    assert settings.vlm.resolved_base_url == "http://proxy/v1"


def test_fish_si_sceglie_dichiarandolo() -> None:
    settings = AppSettings.from_env(
        {
            "TTS_PROVIDER": "fish",
            "FISH_URL": "http://fish:8080",
            "FISH_SEED": "",
        }
    )

    assert settings.tts.resolved_provider == "fish"
    assert settings.tts.fish_url == "http://fish:8080"
    assert settings.tts.fish_seed is None


def test_il_contesto_predefinito_e_la_lezione() -> None:
    settings = AppSettings.from_env({})

    assert settings.vlm.context == "lesson"
    assert settings.samples.enabled is False
    assert AppSettings.from_env({"CAPTION_CONTEXT": "general"}).vlm.context == "general"
