from vision_caption.infrastructure.server.app import create_app
from vision_caption.infrastructure.settings import AppSettings


def _pipeline(context: str):
    settings = AppSettings.from_env(
        {
            "USE_MOCKS": "true",
            "CAPTION_CONTEXT": context,
            "RESEARCH_LOG_ENABLED": "false",
            "FRONTEND_DIST_PATH": "/nonexistent",
        }
    )
    return create_app(settings).state.pipeline_factory(None)


def test_lesson_features_are_active_only_in_lesson_mode() -> None:
    lesson = _pipeline("lesson")
    general = _pipeline("general")

    assert lesson._lesson_memory is not None
    assert lesson._speech_text is not None
    # Una sola memoria per connessione, condivisa con il puntamento.
    assert lesson._pointing_pipeline._lesson_memory is lesson._lesson_memory
    assert lesson._pointing_pipeline._speech_text is not None

    assert general._lesson_memory is None
    assert general._speech_text is None
    assert general._pointing_pipeline._lesson_memory is None
    assert general._pointing_pipeline._speech_text is None


def test_each_connection_gets_its_own_memory() -> None:
    settings = AppSettings.from_env(
        {"USE_MOCKS": "true", "RESEARCH_LOG_ENABLED": "false", "FRONTEND_DIST_PATH": "/nonexistent"}
    )
    factory = create_app(settings).state.pipeline_factory

    assert factory(None)._lesson_memory is not factory(None)._lesson_memory
