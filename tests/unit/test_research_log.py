import json
from datetime import UTC, datetime
from unittest.mock import AsyncMock, Mock

import pytest

from vision_caption.adapters.research.jsonl_research_recorder import (
    JsonlResearchRecorder,
)
from vision_caption.core.domain.frame import CaptionMode, Frame
from vision_caption.core.domain.sceneAnalysisResult import SceneAnalysisResult
from vision_caption.core.ports.SceneDetectorPort import SceneDetectorPort
from vision_caption.core.ports.research_recorder_port import (
    NullResearchRecorder,
)
from vision_caption.core.services.caption_pipeline import CaptionPipeline
from vision_caption.core.services.pointing.pointing_event_gate import (
    PointingEventGate,
)
from vision_caption.core.services.pointing.pointing_pipeline import (
    PointingPipeline,
)
from vision_caption.core.services.rate_limiter import RateLimiter
from vision_caption.infrastructure.server.research import (
    ResearchSessions,
    config_snapshot,
)
from vision_caption.infrastructure.settings import (
    AppSettings,
    ResearchSettings,
    TtsSettings,
    VlmSettings,
)

from tests.unit.test_caption_pipeline import (
    FakeCaptionGenerator,
    FakeSpeechSynthesizer,
)
from tests.unit.test_pointing_pipeline import (
    FakeEstimator,
    FakeGenerator,
    FakePreparer,
    FakeSpeech,
    StubRecognizer,
    _activation,
    _caption,
    _frame,
)


class MemoryRecorder:
    def __init__(self) -> None:
        self.events: list[dict] = []

    def record(self, event: str, **fields) -> None:
        self.events.append({"event": event, **fields})

    def named(self, event: str) -> list[dict]:
        return [item for item in self.events if item["event"] == event]


def _lines(path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines()]


def test_every_line_carries_session_order_and_time(tmp_path) -> None:
    ticks = iter([100.0, 100.5, 102.25])
    recorder = JsonlResearchRecorder(
        tmp_path / "s.jsonl",
        session_id="abc",
        clock=lambda: next(ticks),
        wall_clock=lambda: datetime(2026, 11, 3, 9, 0, tzinfo=UTC),
    )

    recorder.record("mode_change", current="AUTO")
    recorder.record("utterance", text="Una sedia.", chars=10)
    recorder.close()

    first, second = _lines(tmp_path / "s.jsonl")
    assert first == {
        "schema_version": 1,
        "session_id": "abc",
        "seq": 1,
        "ts": "2026-11-03T09:00:00.000+00:00",
        "t": 0.5,
        "event": "mode_change",
        "current": "AUTO",
    }
    assert second["seq"] == 2
    assert second["t"] == 2.25
    assert second["text"] == "Una sedia."


def test_text_can_be_left_out_keeping_lengths(tmp_path) -> None:
    recorder = JsonlResearchRecorder(
        tmp_path / "s.jsonl",
        session_id="abc",
        include_text=False,
    )

    recorder.record(
        "pointing_result",
        text="Un libro. C'è scritto: Mario Rossi",
        visible_text="Mario Rossi",
        chars=34,
        confidence=0.9,
    )
    recorder.close()

    (line,) = _lines(tmp_path / "s.jsonl")
    assert line["text"] is None
    assert line["visible_text"] is None
    assert line["chars"] == 34
    assert line["confidence"] == 0.9


def test_recording_after_close_is_ignored(tmp_path) -> None:
    recorder = JsonlResearchRecorder(tmp_path / "s.jsonl", session_id="abc")
    recorder.close()

    recorder.record("utterance", text="tardi")

    assert (tmp_path / "s.jsonl").read_text() == ""


def test_config_snapshot_never_contains_api_keys() -> None:
    settings = AppSettings(
        vlm=VlmSettings(api_key="sk-segreta"),
        tts=TtsSettings(elevenlabs_api_key="el-segreta"),
    )

    dumped = json.dumps(config_snapshot(settings))

    assert "segreta" not in dumped
    assert "api_key" not in dumped
    assert "gesture" in dumped


def test_session_opens_with_context_and_receives_markers(tmp_path) -> None:
    sessions = ResearchSessions(
        AppSettings(research=ResearchSettings(output_dir=tmp_path))
    )

    recorder = sessions.open(participant_id="P07", task_id="T2")
    assert sessions.mark("inizio compito 2") == [recorder.session_id]
    sessions.close(recorder)
    assert sessions.mark("dopo la chiusura") == []

    start, marker = _lines(recorder.path)
    assert start["event"] == "session_start"
    assert start["participant_id"] == "P07"
    assert start["task_id"] == "T2"
    assert start["app_version"]
    assert "config" in start
    assert marker["event"] == "marker"
    assert marker["label"] == "inizio compito 2"


def test_disabled_research_log_writes_nothing(tmp_path) -> None:
    sessions = ResearchSessions(
        AppSettings(
            research=ResearchSettings(enabled=False, output_dir=tmp_path)
        )
    )

    recorder = sessions.open(participant_id="P07")

    assert isinstance(recorder, NullResearchRecorder)
    assert list(tmp_path.iterdir()) == []


def _pointing_pipeline(
    recorder: MemoryRecorder,
    caption=None,
    gate: PointingEventGate | None = None,
) -> PointingPipeline:
    return PointingPipeline(
        hand_pose_estimator=FakeEstimator(),
        gesture_recognizer=StubRecognizer((_activation(),)),
        event_gate=gate or PointingEventGate(cooldown_seconds=0.0),
        image_preparer=FakePreparer(),
        caption_generator=FakeGenerator(caption),
        speech_synthesizer=FakeSpeech(),
        clock=lambda: 10.0,
        research_recorder=recorder,
    )


@pytest.mark.asyncio
async def test_pointing_records_activation_and_what_the_model_understood() -> None:
    recorder = MemoryRecorder()
    pipeline = _pointing_pipeline(recorder, _caption())

    [_ async for _ in pipeline.process(_frame())]

    (activation,) = recorder.named("pointing_activation")
    assert activation["handedness"] == "RIGHT"
    assert activation["retarget"] is False
    (result,) = recorder.named("pointing_result")
    assert result["outcome"] == "spoken"
    assert result["target"] == "cartello"
    assert result["visible_text"] == "USCITA\nEXIT"
    assert result["needs_repointing"] is False
    assert {"prepare_ms", "vlm_ms", "tts_ms"} <= result.keys()


@pytest.mark.asyncio
async def test_pointing_records_missing_caption() -> None:
    recorder = MemoryRecorder()
    pipeline = _pointing_pipeline(recorder, caption=None)

    [_ async for _ in pipeline.process(_frame())]

    (result,) = recorder.named("pointing_result")
    assert result["outcome"] == "no_caption"


@pytest.mark.asyncio
async def test_pointing_blocked_by_cooldown_is_recorded() -> None:
    recorder = MemoryRecorder()
    gate = PointingEventGate(cooldown_seconds=5.0)
    assert gate.allow(9.0)
    pipeline = _pointing_pipeline(recorder, _caption(), gate)

    [_ async for _ in pipeline.process(_frame())]

    (blocked,) = recorder.named("pointing_blocked")
    assert blocked["reason"] == "cooldown"
    assert recorder.named("pointing_activation") == []


def _auto_frame(frame_id: int) -> Frame:
    return Frame(
        frame_id=frame_id,
        image_bytes=b"fake-jpeg",
        caption_mode=CaptionMode.AUTO,
    )


@pytest.mark.asyncio
async def test_auto_records_every_frame_and_skipped_repetitions() -> None:
    scene_detector = Mock(spec=SceneDetectorPort)
    scene_detector.analyze = AsyncMock(
        return_value=SceneAnalysisResult(is_change=True)
    )
    scene_detector.commit = AsyncMock()
    rate_limiter = Mock(spec=RateLimiter)
    rate_limiter.can_execute.return_value = True
    recorder = MemoryRecorder()
    pipeline = CaptionPipeline(
        scene_detector=scene_detector,
        caption_generator=FakeCaptionGenerator("Una sedia."),
        speech_synthesizer=FakeSpeechSynthesizer(),
        rate_limiter=rate_limiter,
        research_recorder=recorder,
    )

    [_ async for _ in pipeline.process(_auto_frame(1))]
    [_ async for _ in pipeline.process(_auto_frame(2))]

    frames = recorder.named("auto_frame")
    assert [frame["outcome"] for frame in frames] == ["completed", "no_audio"]
    assert frames[0]["frame_id"] == 1
    (skipped,) = recorder.named("utterance_skipped")
    assert skipped["reason"] == "similar_to_previous"
    assert skipped["text"] == "Una sedia."
