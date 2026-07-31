from collections.abc import AsyncIterator, Awaitable, Callable
from time import monotonic

from vision_caption.core.domain.captionResult import CaptionResult
from vision_caption.core.domain.frame import Frame
from vision_caption.core.domain.pointing import PointingEvent, PointingOverlay
from vision_caption.core.domain.pointing_caption import PointingCaption
from vision_caption.core.ports.SpeechSynthesizerPort import (
    SpeechSynthesizerPort,
)
from vision_caption.core.ports.hand_pose_estimator_port import (
    HandPoseEstimatorPort,
)
from vision_caption.core.ports.pointing_caption_generator_port import (
    PointingCaptionGeneratorPort,
)
from vision_caption.core.ports.pointing_image_preparer_port import (
    PointingImagePreparerPort,
)
from vision_caption.core.services.pointing.gesture_recognizer import (
    PointingGestureRecognizer,
)
from vision_caption.core.services.pointing.pointing_event_gate import (
    PointingEventGate,
)


def compose_accessibility_caption(
    caption: PointingCaption,
) -> str | None:
    description = caption.description.strip()
    target = caption.target.strip() if caption.target else ""
    object_caption = description or target
    visible_text = caption.visible_text.strip() if caption.visible_text else ""

    if not visible_text:
        return object_caption or None
    if not object_caption:
        return f"C'è scritto: {visible_text}"

    separator = (
        " " if object_caption.endswith((".", "!", "?", ":")) else ". "
    )
    return f"{object_caption}{separator}C'è scritto: {visible_text}"


class PointingPipeline:
    """Orchestra un evento POINTING completo per una singola sessione."""

    def __init__(
        self,
        hand_pose_estimator: HandPoseEstimatorPort,
        gesture_recognizer: PointingGestureRecognizer,
        event_gate: PointingEventGate,
        image_preparer: PointingImagePreparerPort,
        caption_generator: PointingCaptionGeneratorPort,
        speech_synthesizer: SpeechSynthesizerPort,
        clock: Callable[[], float] = monotonic,
    ) -> None:
        self._hand_pose_estimator = hand_pose_estimator
        self._gesture_recognizer = gesture_recognizer
        self._event_gate = event_gate
        self._image_preparer = image_preparer
        self._caption_generator = caption_generator
        self._speech_synthesizer = speech_synthesizer
        self._clock = clock

    async def process(
        self,
        frame: Frame,
        on_overlay: Callable[
            [tuple[PointingOverlay, ...], int],
            Awaitable[None],
        ]
        | None = None,
    ) -> AsyncIterator[CaptionResult]:
        pose_result = await self._hand_pose_estimator.estimate(frame)
        timestamp = self._clock()
        recognition = self._gesture_recognizer.update(
            pose_result.hands,
            timestamp=timestamp,
        )
        if on_overlay is not None:
            await on_overlay(recognition.overlays, frame.frame_id)

        activation = next(
            (
                candidate
                for candidate in recognition.activations
                if self._event_gate.allow(timestamp)
            ),
            None,
        )
        if activation is None:
            return

        event = PointingEvent(
            handedness=activation.handedness,
            ray=activation.ray,
            frame_id=frame.frame_id,
        )
        images = await self._image_preparer.prepare(frame, event)
        caption = await self._caption_generator.generate(event, images)
        if caption is None:
            return

        spoken_caption = compose_accessibility_caption(caption)
        if spoken_caption is None:
            return

        audio = await self._speech_synthesizer.synthesize(spoken_caption)
        yield CaptionResult(
            frame_id=frame.frame_id,
            caption=spoken_caption,
            audio=audio,
        )

    def reset(self) -> None:
        self._gesture_recognizer.reset()
        self._event_gate.reset()

    async def close(self) -> None:
        await self._hand_pose_estimator.close()
