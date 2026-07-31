import pytest
from pydantic import ValidationError

from vision_caption.infrastructure.settings import (
    AppSettings,
    PointingCorridorSettings,
)


def test_app_settings_loads_nested_values_from_environment() -> None:
    settings = AppSettings.from_env(
        {
            "USE_MOCKS": "true",
            "SSIM_THRESHOLD": "0.72",
            "RFDETR_THRESHOLD": "0.51",
            "MIN_CAPTION_INTERVAL_SECONDS": "2.5",
            "POINTING_CONFIRMATION_SECONDS": "0.15",
            "POINTING_EVENT_COOLDOWN_SECONDS": "1.5",
            "POINTING_CORRIDOR_COLOR_HEX": "#12abef",
            "POINTING_DEBUG_SAVE_IMAGES": "true",
            "POINTING_DEBUG_OUTPUT_DIR": "tesi/immagini-pointing",
        }
    )

    assert settings.runtime.use_mocks
    assert settings.auto.ssim.threshold == 0.72
    assert settings.auto.rfdetr.confidence_threshold == 0.51
    assert settings.auto.min_caption_interval_seconds == 2.5
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
