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


def test_stop_gesture_is_active_only_in_lesson_mode() -> None:
    assert _pipeline("lesson")._stop_gesture is not None
    assert _pipeline("general")._stop_gesture is None


def test_pointing_diagnostics_and_gap_reach_the_pipeline() -> None:
    settings = AppSettings.from_env({
        "USE_MOCKS": "true", "RESEARCH_LOG_ENABLED": "false",
        "POINTING_CANDIDATE_GAP_SECONDS": "0.4", "POINTING_GESTURE_DIAGNOSTICS": "true",
    })
    pipeline = create_app(settings).state.pipeline_factory(None)._pointing_pipeline
    assert pipeline._diagnostics_enabled
    assert pipeline._gesture_recognizer._settings.candidate_gap_seconds == 0.4


def test_mirror_recovery_has_a_separate_estimator_and_does_not_change_auto():
    settings=AppSettings.from_env({'USE_MOCKS':'true','RESEARCH_LOG_ENABLED':'false','POINTING_MIRROR_RECOVERY':'true'})
    pipeline=create_app(settings).state.pipeline_factory(None)
    pointing=pipeline._pointing_pipeline
    assert pointing._recovery_pose_estimator is not None
    assert pointing._recovery_pose_estimator is not pipeline._hand_pose_estimator
    assert pointing._hand_pose_estimator is pipeline._hand_pose_estimator
    assert _pipeline('lesson')._pointing_pipeline._recovery_pose_estimator is None
