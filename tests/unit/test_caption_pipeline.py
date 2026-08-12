import asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, Mock

import pytest

from vision_caption.core.domain.audio import Audio, AudioFormat
from vision_caption.core.domain.captionResult import CaptionResult
from vision_caption.core.domain.frame import CaptionMode, Frame
from vision_caption.core.domain.sceneAnalysisResult import SceneAnalysisResult
from vision_caption.core.ports.CaptionGeneratorPort import CaptionGeneratorPort
from vision_caption.core.ports.SceneDetectorPort import SceneDetectorPort
from vision_caption.core.ports.SpeechSynthesizerPort import SpeechSynthesizerPort
from vision_caption.core.services.caption_pipeline import CaptionPipeline
from vision_caption.core.services.rate_limiter import RateLimiter


class FakePointingPipeline:
    def __init__(self) -> None:
        self.processed_frames: list[Frame] = []
        self.reset_calls = 0
        self.closed = False

    async def process(self, frame: Frame, on_overlay=None):
        self.processed_frames.append(frame)
        if on_overlay is not None:
            await on_overlay((), frame.frame_id)
        yield CaptionResult(
            frame_id=frame.frame_id,
            caption="Oggetto indicato.",
            audio=Audio(
                audio_format=AudioFormat.WAV,
                audio_bytes=b"audio",
                audio_duration=0.5,
            ),
        )

    def reset(self) -> None:
        self.reset_calls += 1

    async def close(self) -> None:
        self.closed = True


class FakeCaptionGenerator:
    def __init__(self, text: str = "Una sedia davanti a un tavolo.") -> None:
        self.text = text

    async def generate(self, frame: Frame):
        yield self.text


class SlowCaptionGenerator:
    async def generate(self, frame: Frame):
        await asyncio.sleep(0.05)
        yield "Questa risposta arriva troppo tardi."


class FakeSpeechSynthesizer:
    async def synthesize(self, text: str) -> Audio:
        return Audio(
            audio_format=AudioFormat.WAV,
            audio_bytes=b"audio",
            audio_duration=0.5,
        )


@pytest.mark.asyncio
async def test_auto_mode_stops_when_scene_is_unchanged() -> None:
    scene_detector = Mock(spec=SceneDetectorPort)
    scene_detector.analyze = AsyncMock(
        return_value=SceneAnalysisResult(is_change=False)
    )
    caption_generator = Mock(spec=CaptionGeneratorPort)
    speech_synthesizer = Mock(spec=SpeechSynthesizerPort)
    rate_limiter = Mock(spec=RateLimiter)

    pipeline = CaptionPipeline(
        scene_detector=scene_detector,
        caption_generator=caption_generator,
        speech_synthesizer=speech_synthesizer,
        rate_limiter=rate_limiter,
    )
    frame = Frame(
        frame_id=1,
        image_bytes=b"fake-jpeg",
        caption_mode=CaptionMode.AUTO,
    )

    results = [result async for result in pipeline.process(frame)]

    assert results == []
    scene_detector.analyze.assert_awaited_once_with(frame)
    rate_limiter.can_execute.assert_not_called()
    caption_generator.generate.assert_not_called()
    speech_synthesizer.synthesize.assert_not_called()


@pytest.mark.asyncio
async def test_pointing_mode_delegates_without_calling_auto_dependencies() -> None:
    scene_detector = Mock(spec=SceneDetectorPort)
    caption_generator = Mock(spec=CaptionGeneratorPort)
    speech_synthesizer = Mock(spec=SpeechSynthesizerPort)
    rate_limiter = Mock(spec=RateLimiter)
    pointing_pipeline = FakePointingPipeline()
    pipeline = CaptionPipeline(
        scene_detector=scene_detector,
        caption_generator=caption_generator,
        speech_synthesizer=speech_synthesizer,
        rate_limiter=rate_limiter,
        pointing_pipeline=pointing_pipeline,
    )
    frame = Frame(
        frame_id=9,
        image_bytes=b"fake-jpeg",
        caption_mode=CaptionMode.POINTING,
    )

    results = [result async for result in pipeline.process(frame)]

    assert len(results) == 1
    assert results[0].frame_id == 9
    assert pointing_pipeline.processed_frames == [frame]
    scene_detector.analyze.assert_not_called()
    rate_limiter.can_execute.assert_not_called()
    caption_generator.generate.assert_not_called()
    speech_synthesizer.synthesize.assert_not_called()


@pytest.mark.asyncio
async def test_mode_change_resets_pointing_session_and_close_releases_it() -> None:
    scene_detector = Mock(spec=SceneDetectorPort)
    scene_detector.analyze = AsyncMock(
        return_value=SceneAnalysisResult(is_change=False)
    )
    pointing_pipeline = FakePointingPipeline()
    pipeline = CaptionPipeline(
        scene_detector=scene_detector,
        caption_generator=Mock(spec=CaptionGeneratorPort),
        speech_synthesizer=Mock(spec=SpeechSynthesizerPort),
        rate_limiter=Mock(spec=RateLimiter),
        pointing_pipeline=pointing_pipeline,
    )
    pointing_frame = Frame(
        frame_id=1,
        image_bytes=b"fake-jpeg",
        caption_mode=CaptionMode.POINTING,
    )
    auto_frame = pointing_frame.model_copy(
        update={"frame_id": 2, "caption_mode": CaptionMode.AUTO}
    )

    _ = [result async for result in pipeline.process(pointing_frame)]

    cleared_overlays: list[tuple[tuple[object, ...], int]] = []

    async def on_pointing_overlay(
        overlays: tuple[object, ...],
        frame_id: int,
    ) -> None:
        cleared_overlays.append((overlays, frame_id))

    _ = [
        result
        async for result in pipeline.process(
            auto_frame,
            on_pointing_overlay=on_pointing_overlay,
        )
    ]
    await pipeline.close()

    assert pointing_pipeline.reset_calls == 1
    assert cleared_overlays == [((), auto_frame.frame_id)]
    assert pointing_pipeline.closed


@pytest.mark.asyncio
async def test_rate_limiter_and_scene_commit_only_on_first_valid_audio() -> None:
    scene_detector = Mock(spec=SceneDetectorPort)
    scene_detector.analyze = AsyncMock(
        return_value=SceneAnalysisResult(is_change=True)
    )
    scene_detector.commit = AsyncMock()
    rate_limiter = Mock(spec=RateLimiter)
    rate_limiter.can_execute.return_value = True
    pipeline = CaptionPipeline(
        scene_detector=scene_detector,
        caption_generator=FakeCaptionGenerator(),
        speech_synthesizer=FakeSpeechSynthesizer(),
        rate_limiter=rate_limiter,
    )
    frame = Frame(
        frame_id=10,
        image_bytes=b"fake-jpeg",
        caption_mode=CaptionMode.AUTO,
    )

    results = [result async for result in pipeline.process(frame)]

    assert len(results) == 1
    scene_detector.commit.assert_awaited_once_with()
    rate_limiter.record.assert_called_once_with()


@pytest.mark.asyncio
async def test_vlm_timeout_does_not_consume_cooldown_or_commit_scene() -> None:
    scene_detector = Mock(spec=SceneDetectorPort)
    scene_detector.analyze = AsyncMock(
        return_value=SceneAnalysisResult(is_change=True)
    )
    scene_detector.commit = AsyncMock()
    rate_limiter = Mock(spec=RateLimiter)
    rate_limiter.can_execute.return_value = True
    pipeline = CaptionPipeline(
        scene_detector=scene_detector,
        caption_generator=SlowCaptionGenerator(),
        speech_synthesizer=FakeSpeechSynthesizer(),
        rate_limiter=rate_limiter,
        vlm_chunk_timeout_seconds=0.001,
    )
    frame = Frame(
        frame_id=11,
        image_bytes=b"fake-jpeg",
        caption_mode=CaptionMode.AUTO,
    )

    results = [result async for result in pipeline.process(frame)]

    assert results == []
    scene_detector.commit.assert_not_awaited()
    rate_limiter.record.assert_not_called()


@pytest.mark.asyncio
async def test_stale_frame_does_not_consume_cooldown_or_commit_scene() -> None:
    scene_detector = Mock(spec=SceneDetectorPort)
    scene_detector.analyze = AsyncMock(
        return_value=SceneAnalysisResult(is_change=True)
    )
    scene_detector.commit = AsyncMock()
    rate_limiter = Mock(spec=RateLimiter)
    rate_limiter.can_execute.return_value = True
    pipeline = CaptionPipeline(
        scene_detector=scene_detector,
        caption_generator=FakeCaptionGenerator(),
        speech_synthesizer=FakeSpeechSynthesizer(),
        rate_limiter=rate_limiter,
        max_frame_age_seconds=3.0,
    )
    frame = Frame(
        frame_id=12,
        image_bytes=b"fake-jpeg",
        caption_mode=CaptionMode.AUTO,
        timestamp=datetime.now() - timedelta(seconds=10),
    )

    results = [result async for result in pipeline.process(frame)]

    assert results == []
    scene_detector.commit.assert_not_awaited()
    rate_limiter.record.assert_not_called()
