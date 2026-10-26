from collections.abc import AsyncIterator, Awaitable, Callable
from time import monotonic, perf_counter

from vision_caption.core.domain.captionResult import CaptionResult
from vision_caption.core.domain.frame import Frame
from vision_caption.core.domain.hand_pose import HandObservation
from vision_caption.core.domain.pointing import (
    HandLandmarks,
    ImagePoint,
    PointingEvent,
    PointingOverlay,
)
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
from vision_caption.core.ports.research_recorder_port import (
    NullResearchRecorder,
    ResearchRecorderPort,
)
from vision_caption.core.services.pointing.gesture_recognizer import (
    PointingGestureRecognizer,
)
from vision_caption.core.services.pointing.pointing_event_gate import (
    PointingEventGate,
)


LANDMARK_DECIMALS = 4


def collect_hand_landmarks(
    hands: tuple[HandObservation, ...],
) -> tuple[HandLandmarks, ...]:
    """Estrae i landmark immagine di ogni mano vista, gesture o no.

    Le coordinate viaggiano arrotondate: oltre il decimillesimo si tratta di
    frazioni di pixel, e il messaggio parte a ogni fotogramma POINTING.
    """
    return tuple(
        HandLandmarks(
            handedness=hand.handedness,
            landmarks=tuple(
                ImagePoint(
                    x=round(landmark.x, LANDMARK_DECIMALS),
                    y=round(landmark.y, LANDMARK_DECIMALS),
                )
                for landmark in hand.image_landmarks
            ),
        )
        for hand in hands
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


def _caption_fields(caption: PointingCaption) -> dict:
    """Ciò che il modello ha capito del bersaglio, per l'analisi dello studio."""
    return {
        "target": caption.target,
        "description": caption.description,
        "visible_text": caption.visible_text,
        "confidence": caption.confidence,
        "text_confidence": caption.text_confidence,
        "text_complete": caption.text_complete,
        "needs_repointing": caption.needs_repointing,
        "needs_closer_view": caption.needs_closer_view,
        "alternatives": list(caption.alternatives),
        "candidate_labels": [
            candidate.label for candidate in caption.candidates
        ],
    }


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
        research_recorder: ResearchRecorderPort | None = None,
    ) -> None:
        self._hand_pose_estimator = hand_pose_estimator
        self._gesture_recognizer = gesture_recognizer
        self._event_gate = event_gate
        self._image_preparer = image_preparer
        self._caption_generator = caption_generator
        self._speech_synthesizer = speech_synthesizer
        self._clock = clock
        self._research = research_recorder or NullResearchRecorder()

    async def process(
        self,
        frame: Frame,
        on_overlay: Callable[
            [tuple[PointingOverlay, ...], int, tuple[HandLandmarks, ...]],
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
            await on_overlay(
                recognition.overlays,
                frame.frame_id,
                collect_hand_landmarks(pose_result.hands),
            )

        activation = None
        for candidate in recognition.activations:
            if activation is None and self._event_gate.allow(timestamp):
                activation = candidate
            else:
                # Un'attivazione bloccata dal cooldown non va persa: il
                # riconoscitore la ripropone se il gesto è ancora mantenuto.
                self._gesture_recognizer.cancel(candidate)
                self._research.record(
                    "pointing_blocked",
                    frame_id=frame.frame_id,
                    reason="cooldown" if activation is None else "other_hand",
                    handedness=candidate.handedness.value,
                    retarget=candidate.retarget,
                )
        if activation is None:
            return

        self._research.record(
            "pointing_activation",
            frame_id=frame.frame_id,
            handedness=activation.handedness.value,
            retarget=activation.retarget,
            ray=activation.ray.model_dump(mode="json"),
        )

        event = PointingEvent(
            handedness=activation.handedness,
            ray=activation.ray,
            frame_id=frame.frame_id,
        )
        started_at = perf_counter()
        images = await self._image_preparer.prepare(frame, event)
        prepared_at = perf_counter()
        caption = await self._caption_generator.generate(event, images)
        captioned_at = perf_counter()
        timings = {
            "prepare_ms": round((prepared_at - started_at) * 1000.0, 1),
            "vlm_ms": round((captioned_at - prepared_at) * 1000.0, 1),
        }
        if caption is None:
            self._research.record(
                "pointing_result",
                frame_id=frame.frame_id,
                outcome="no_caption",
                **timings,
            )
            return

        spoken_caption = compose_accessibility_caption(caption)
        if spoken_caption is None:
            self._research.record(
                "pointing_result",
                frame_id=frame.frame_id,
                outcome="empty_caption",
                **timings,
                **_caption_fields(caption),
            )
            return

        audio = await self._speech_synthesizer.synthesize(spoken_caption)
        self._research.record(
            "pointing_result",
            frame_id=frame.frame_id,
            outcome="spoken",
            **timings,
            tts_ms=round((perf_counter() - captioned_at) * 1000.0, 1),
            **_caption_fields(caption),
        )
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
