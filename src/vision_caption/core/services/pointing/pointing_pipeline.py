import re
from collections.abc import AsyncIterator, Awaitable, Callable
from time import monotonic, perf_counter

from loguru import logger

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
    PointingImages,
)
from vision_caption.core.ports.caption_sample_store_port import (
    CaptionSampleStorePort,
    NullCaptionSampleStore,
)
from vision_caption.core.ports.research_recorder_port import (
    NullResearchRecorder,
    ResearchRecorderPort,
)
from vision_caption.core.services.lesson_memory import LessonMemory
from vision_caption.core.services.pointing.gesture_recognizer import (
    PointingGestureRecognizer,
)
from vision_caption.core.services.pointing.pointing_event_gate import (
    PointingEventGate,
)


LANDMARK_DECIMALS = 4

# Un gesto confermato merita sempre una risposta: senza, chi punta non sa se
# il sistema ha visto il gesto e se deve ripuntare.
REPOINT_PROMPT = "Non capisco cosa stai indicando. Prova a puntare di nuovo."
CLOSER_VIEW_PROMPT = "Il dettaglio non è leggibile. Avvicina la fotocamera e punta di nuovo."


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


# A lezione il testo letto sul bersaglio si legge solo se è breve: una
# formula, una riga, un'etichetta. Le etichette di un grafico in fila ("60 57
# 47 1950 1970") non aiutano, la descrizione del grafico sì.
LESSON_MAX_VISIBLE_LINES = 2
LESSON_MAX_VISIBLE_WORDS = 20
_FORMULA_SIGNS = re.compile(r"[=+^²³√±≤≥<>∫∑π]")
_GENERIC_SLIDE_DESCRIPTION = re.compile(
    r"(?i)^(?:testo|blocco di testo|etichetta)"
    r"(?: (?:sulla|su una|della|di una) (?:slide|diapositiva)(?: proiettata)?)?\.?$"
)


def compose_lesson_caption(caption: PointingCaption) -> str | None:
    if caption.target_kind == "object":
        return compose_accessibility_caption(caption)
    description = caption.description.strip()
    target = caption.target.strip() if caption.target else ""
    lines = [
        line.strip()
        for line in (caption.visible_text or "").splitlines()
        if line.strip()
    ]
    visible_text = ", ".join(lines)
    if visible_text and not caption.text_complete and description:
        # Il frame 799 aveva OCR "deogioco" dal titolo tagliato: si conserva
        # la descrizione del bersaglio senza leggere parole incomplete.
        return description
    readable = (
        visible_text
        and len(lines) <= LESSON_MAX_VISIBLE_LINES
        and len(visible_text.split()) <= LESSON_MAX_VISIBLE_WORDS
    )
    if not readable:
        return description or target or None
    if _GENERIC_SLIDE_DESCRIPTION.fullmatch(description):
        return visible_text
    # Una formula è già letta a parole nella descrizione: rileggerla scritta
    # la direbbe due volte.
    if description and _FORMULA_SIGNS.search(visible_text):
        return description
    # Se la descrizione si limita a ripetere il testo (un'etichetta), basta il
    # testo: "Evaporazione" invece di "Etichetta di un nodo… C'è scritto:
    # Evaporazione".
    if not description or visible_text.casefold() in description.casefold():
        return description or visible_text
    if caption.target_kind == "educational_content":
        # Anche una figura descritta in tre parole è informativa. Non usare
        # la vecchia euristica delle etichette per scartarla; testo prima.
        separator = " " if visible_text.endswith((".", "!", "?", ":")) else ". "
        return f"{visible_text}{separator}{description}"
    if len(description.split()) <= 3 or description.casefold() == target.casefold():
        return visible_text
    separator = " " if description.endswith((".", "!", "?", ":")) else ". "
    return f"{description}{separator}C'è scritto: {visible_text}"


def _caption_fields(caption: PointingCaption) -> dict:
    """Ciò che il modello ha capito del bersaglio, per l'analisi dello studio."""
    return {
        "target_kind": caption.target_kind,
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
        sample_store: CaptionSampleStorePort | None = None,
        lesson_memory: LessonMemory | None = None,
        speech_text: Callable[[str], str] | None = None,
        diagnostics_enabled: bool = False,
        recovery_pose_estimator: HandPoseEstimatorPort | None = None,
    ) -> None:
        self._hand_pose_estimator = hand_pose_estimator
        self._recovery_pose_estimator = recovery_pose_estimator
        self._gesture_recognizer = gesture_recognizer
        self._event_gate = event_gate
        self._image_preparer = image_preparer
        self._caption_generator = caption_generator
        self._speech_synthesizer = speech_synthesizer
        self._clock = clock
        self._research = research_recorder or NullResearchRecorder()
        self._samples = sample_store or NullCaptionSampleStore()
        # A lezione il gesto vede le slide già descritte e la frase segue le
        # regole della lezione (breve, simboli letti a parole).
        self._lesson_memory = lesson_memory
        self._speech_text = speech_text
        self._diagnostics_enabled = diagnostics_enabled
        self._previous_pose_timestamp: float | None = None

    async def process(
        self,
        frame: Frame,
        on_overlay: Callable[
            [tuple[PointingOverlay, ...], int, tuple[HandLandmarks, ...]],
            Awaitable[None],
        ]
        | None = None,
    ) -> AsyncIterator[CaptionResult]:
        pose_started_at = perf_counter()
        pose_result = await self._hand_pose_estimator.estimate(frame)
        recovery_used = False
        if self._recovery_pose_estimator is not None and not self._gesture_recognizer.has_pointing_pose(pose_result.hands):
            recovery_error = None
            try:
                recovered = await self._recovery_pose_estimator.estimate(frame)
            except Exception as error:
                recovered = None
                recovery_error = type(error).__name__
                logger.warning("Recupero della mano non disponibile sul frame {}: {}", frame.frame_id, recovery_error)
            recovery_used = recovered is not None and self._gesture_recognizer.has_pointing_pose(recovered.hands)
            self._research.record(
                "pointing_recovery", frame_id=frame.frame_id,
                primary_hands=len(pose_result.hands), recovery_hands=len(recovered.hands) if recovered else 0,
                selected="mirror" if recovery_used else "primary",
                error_type=recovery_error,
            )
            if recovery_used:
                pose_result = recovered
        pose_ms = round((perf_counter()-pose_started_at)*1000, 1)
        timestamp = self._clock()
        recognition = self._gesture_recognizer.update(
            pose_result.hands,
            timestamp=timestamp,
        )
        if self._diagnostics_enabled:
            self._research.record(
                "pointing_frame",
                frame_id=frame.frame_id,
                interval_ms=(
                    round((timestamp - self._previous_pose_timestamp) * 1000, 1)
                    if self._previous_pose_timestamp is not None else None
                ),
                reason="no_hand" if not pose_result.hands else "hands_observed",
                hands=list(recognition.diagnostics),
                recovery_used=recovery_used,
                pose_ms=pose_ms,
            )
        self._previous_pose_timestamp = timestamp
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
            recovery_used=recovery_used,
            pose_ms=pose_ms,
        )

        event = PointingEvent(
            handedness=activation.handedness,
            ray=activation.ray,
            frame_id=frame.frame_id,
        )
        started_at = perf_counter()
        images = await self._image_preparer.prepare(frame, event)
        prepared_at = perf_counter()
        try:
            memory_context = (
                self._lesson_memory.context() if self._lesson_memory else None
            )
            caption = await self._caption_generator.generate(
                event, images, memory_context
            )
        except Exception as error:
            # Il gesto è perso, la sessione no: si può ripuntare subito.
            logger.exception(
                f"VLM POINTING non disponibile sul frame {frame.frame_id}."
            )
            self._result(
                frame,
                images,
                outcome="vlm_error",
                error_type=type(error).__name__,
            )
            yield await self._repoint_prompt(frame)
            return
        captioned_at = perf_counter()
        timings = {
            "prepare_ms": round((prepared_at - started_at) * 1000.0, 1),
            "vlm_ms": round((captioned_at - prepared_at) * 1000.0, 1),
        }
        if caption is None:
            self._result(frame, images, outcome="no_caption", **timings)
            yield await self._repoint_prompt(frame)
            return

        if caption.needs_repointing or caption.needs_closer_view:
            self._result(
                frame, images,
                outcome="needs_closer_view" if caption.needs_closer_view else "needs_repointing",
                **timings, **_caption_fields(caption),
            )
            yield await self._repoint_prompt(
                frame, CLOSER_VIEW_PROMPT if caption.needs_closer_view else REPOINT_PROMPT
            )
            return

        if self._speech_text is not None:
            spoken_caption = compose_lesson_caption(caption)
            if spoken_caption is not None:
                spoken_caption = self._speech_text(spoken_caption)
        else:
            spoken_caption = compose_accessibility_caption(caption)
        if spoken_caption is None:
            self._result(
                frame,
                images,
                outcome="empty_caption",
                **timings,
                **_caption_fields(caption),
            )
            yield await self._repoint_prompt(frame)
            return

        audio = await self._speech_synthesizer.synthesize(spoken_caption)
        self._result(
            frame,
            images,
            outcome="spoken",
            **timings,
            tts_ms=round((perf_counter() - captioned_at) * 1000.0, 1),
            **_caption_fields(caption),
            text=spoken_caption,
        )
        yield CaptionResult(
            frame_id=frame.frame_id,
            caption=spoken_caption,
            audio=audio,
        )

    async def _repoint_prompt(self, frame: Frame, text: str = REPOINT_PROMPT) -> CaptionResult:
        audio = await self._speech_synthesizer.synthesize(text)
        return CaptionResult(
            frame_id=frame.frame_id,
            caption=text,
            audio=audio,
        )

    def _result(
        self,
        frame: Frame,
        images: PointingImages,
        **fields,
    ) -> None:
        """Registra l'esito del gesto e ne conserva le immagini."""
        self._research.record("pointing_result", frame_id=frame.frame_id, **fields)
        self._samples.save(
            f"pointing_{frame.frame_id:06d}",
            {
                "01_context.jpg": images.context_jpeg,
                "02_focus.jpg": images.focus_jpeg,
                "03_clean.jpg": images.clean_jpeg,
            },
            {"mode": "POINTING", "frame_id": frame.frame_id, **fields},
        )

    def reset(self) -> None:
        self._gesture_recognizer.reset()
        self._event_gate.reset()
        self._previous_pose_timestamp = None

    async def close(self) -> None:
        await self._hand_pose_estimator.close()
        if self._recovery_pose_estimator is not None and self._recovery_pose_estimator is not self._hand_pose_estimator:
            await self._recovery_pose_estimator.close()
