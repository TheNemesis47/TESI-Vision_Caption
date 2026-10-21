import math

import pytest

from vision_caption.core.domain.hand_pose import (
    HandObservation,
    HandLandmark,
    Handedness,
    ImageLandmark,
    WorldLandmark,
)
from vision_caption.core.domain.pointing import (
    FingerAngles,
    PointingOverlayState,
)
from vision_caption.core.services.pointing.gesture_recognizer import (
    GestureRecognizerSettings,
    PointingGestureRecognizer,
    is_pointing_pose,
    time_scaled_alpha,
)


def _set_world_finger(
    landmarks: list[WorldLandmark],
    indices: tuple[HandLandmark, HandLandmark, HandLandmark, HandLandmark],
    positions: tuple[WorldLandmark, WorldLandmark, WorldLandmark, WorldLandmark],
) -> None:
    for index, position in zip(indices, positions, strict=True):
        landmarks[index.value] = position


def _pointing_hand() -> HandObservation:
    world = [WorldLandmark(x=0.0, y=0.0, z=0.0) for _ in range(21)]
    image = [ImageLandmark(x=0.0, y=0.0, z=0.0) for _ in range(21)]

    _set_world_finger(
        world,
        (
            HandLandmark.INDEX_FINGER_MCP,
            HandLandmark.INDEX_FINGER_PIP,
            HandLandmark.INDEX_FINGER_DIP,
            HandLandmark.INDEX_FINGER_TIP,
        ),
        (
            WorldLandmark(x=0.0, y=0.0, z=0.0),
            WorldLandmark(x=1.0, y=0.0, z=0.0),
            WorldLandmark(x=2.0, y=0.0, z=0.0),
            WorldLandmark(x=3.0, y=0.0, z=0.0),
        ),
    )

    folded_positions = (
        WorldLandmark(x=0.0, y=1.0, z=0.0),
        WorldLandmark(x=1.0, y=1.0, z=0.0),
        WorldLandmark(x=1.0, y=2.0, z=0.0),
        WorldLandmark(x=2.0, y=2.0, z=0.0),
    )
    for indices in (
        (
            HandLandmark.MIDDLE_FINGER_MCP,
            HandLandmark.MIDDLE_FINGER_PIP,
            HandLandmark.MIDDLE_FINGER_DIP,
            HandLandmark.MIDDLE_FINGER_TIP,
        ),
        (
            HandLandmark.RING_FINGER_MCP,
            HandLandmark.RING_FINGER_PIP,
            HandLandmark.RING_FINGER_DIP,
            HandLandmark.RING_FINGER_TIP,
        ),
        (
            HandLandmark.PINKY_MCP,
            HandLandmark.PINKY_PIP,
            HandLandmark.PINKY_DIP,
            HandLandmark.PINKY_TIP,
        ),
    ):
        _set_world_finger(world, indices, folded_positions)

    world[HandLandmark.THUMB_TIP.value] = world[
        HandLandmark.INDEX_FINGER_MCP.value
    ]
    image[HandLandmark.INDEX_FINGER_PIP.value] = ImageLandmark(
        x=0.35,
        y=0.5,
        z=0.0,
    )
    image[HandLandmark.INDEX_FINGER_TIP.value] = ImageLandmark(
        x=0.55,
        y=0.5,
        z=0.0,
    )

    return HandObservation(
        handedness=Handedness.RIGHT,
        image_landmarks=tuple(image),
        world_landmarks=tuple(world),
        confidence=0.99,
    )


def test_pose_hysteresis_is_more_tolerant_while_active() -> None:
    settings = GestureRecognizerSettings()
    angles = {
        "INDICE": FingerAngles(pip=128.0, dip=128.0),
        "MEDIO": FingerAngles(pip=148.0, dip=148.0),
        "ANULARE": FingerAngles(pip=148.0, dip=148.0),
        "MIGNOLO": FingerAngles(pip=148.0, dip=148.0),
    }

    assert not is_pointing_pose(
        angles,
        1.7,
        active=False,
        settings=settings,
    )
    assert is_pointing_pose(
        angles,
        1.7,
        active=True,
        settings=settings,
    )


def test_slightly_bent_hand_still_activates() -> None:
    """Indice non del tutto dritto, dita semichiuse e pollice scostato."""
    angles = {
        "INDICE": FingerAngles(pip=140.0, dip=138.0),
        "MEDIO": FingerAngles(pip=135.0, dip=135.0),
        "ANULARE": FingerAngles(pip=135.0, dip=135.0),
        "MIGNOLO": FingerAngles(pip=135.0, dip=135.0),
    }

    assert is_pointing_pose(
        angles,
        1.5,
        active=False,
        settings=GestureRecognizerSettings(),
    )


def test_open_hand_is_not_pointing() -> None:
    angles = {
        finger: FingerAngles(pip=172.0, dip=172.0)
        for finger in ("INDICE", "MEDIO", "ANULARE", "MIGNOLO")
    }

    assert not is_pointing_pose(
        angles,
        1.0,
        active=False,
        settings=GestureRecognizerSettings(),
    )


def test_time_scaled_alpha_matches_reference_rate_and_grows_with_gaps() -> None:
    assert time_scaled_alpha(0.35, 1.0 / 30.0) == pytest.approx(0.35)
    assert time_scaled_alpha(0.35, 0.25) == pytest.approx(
        1.0 - 0.65**7.5
    )
    assert time_scaled_alpha(0.35, 0.25) > 0.9
    assert time_scaled_alpha(1.0, 0.0) == 1.0


def test_single_bad_frame_does_not_reset_confirmation() -> None:
    settings = GestureRecognizerSettings(
        angle_ema_alpha=1.0,
        ray_ema_alpha=1.0,
        confirmation_seconds=0.3,
        release_seconds=0.15,
    )
    recognizer = PointingGestureRecognizer(settings)
    hand = _pointing_hand()

    assert recognizer.update((hand,), timestamp=0.0).activations == ()
    assert recognizer.update((), timestamp=0.1).activations == ()
    assert len(recognizer.update((hand,), timestamp=0.3).activations) == 1


def test_prolonged_loss_resets_confirmation() -> None:
    settings = GestureRecognizerSettings(
        angle_ema_alpha=1.0,
        ray_ema_alpha=1.0,
        confirmation_seconds=0.3,
        release_seconds=0.15,
    )
    recognizer = PointingGestureRecognizer(settings)
    hand = _pointing_hand()

    recognizer.update((hand,), timestamp=0.0)
    recognizer.update((), timestamp=0.1)
    recognizer.update((), timestamp=0.25)
    assert recognizer.update((hand,), timestamp=0.3).activations == ()
    assert len(recognizer.update((hand,), timestamp=0.6).activations) == 1


def test_handedness_flip_keeps_confirmation() -> None:
    settings = GestureRecognizerSettings(
        angle_ema_alpha=1.0,
        ray_ema_alpha=1.0,
        confirmation_seconds=0.2,
    )
    recognizer = PointingGestureRecognizer(settings)
    right_hand = _pointing_hand()
    left_hand = right_hand.model_copy(update={"handedness": Handedness.LEFT})

    assert recognizer.update((right_hand,), timestamp=0.0).activations == ()
    activated = recognizer.update((left_hand,), timestamp=0.25)
    assert len(activated.activations) == 1
    assert activated.activations[0].handedness == Handedness.LEFT


def test_stable_pose_activates_once_then_requires_release() -> None:
    settings = GestureRecognizerSettings(
        angle_ema_alpha=1.0,
        ray_ema_alpha=1.0,
        confirmation_seconds=0.2,
        release_seconds=0.1,
    )
    recognizer = PointingGestureRecognizer(settings)
    hand = _pointing_hand()

    first_candidate = recognizer.update((hand,), timestamp=0.0)
    assert first_candidate.activations == ()
    assert len(first_candidate.overlays) == 1
    assert first_candidate.overlays[0].state == PointingOverlayState.CANDIDATE
    assert first_candidate.overlays[0].confirmation_progress == 0.0

    second_candidate = recognizer.update((hand,), timestamp=0.1)
    assert second_candidate.activations == ()
    assert second_candidate.overlays[0].confirmation_progress == 0.5

    activated = recognizer.update((hand,), timestamp=0.21)
    assert len(activated.activations) == 1
    assert activated.activations[0].handedness == Handedness.RIGHT
    assert activated.overlays[0].state == PointingOverlayState.ACTIVE
    assert activated.overlays[0].confirmation_progress == 1.0

    assert recognizer.update((hand,), timestamp=0.3).activations == ()
    assert recognizer.update((), timestamp=0.31).overlays == ()
    assert recognizer.update((), timestamp=0.42).overlays == ()

    assert recognizer.update((hand,), timestamp=0.5).activations == ()
    second_activation = recognizer.update((hand,), timestamp=0.71)
    assert len(second_activation.activations) == 1


def _aimed(hand: HandObservation, tip_x: float, tip_y: float) -> HandObservation:
    image = list(hand.image_landmarks)
    image[HandLandmark.INDEX_FINGER_TIP.value] = ImageLandmark(
        x=tip_x,
        y=tip_y,
        z=0.0,
    )
    return hand.model_copy(update={"image_landmarks": tuple(image)})


def _retarget_settings() -> GestureRecognizerSettings:
    return GestureRecognizerSettings(
        angle_ema_alpha=1.0,
        ray_ema_alpha=1.0,
        confirmation_seconds=0.2,
        release_seconds=0.1,
    )


def test_moving_held_finger_to_new_target_activates_again() -> None:
    recognizer = PointingGestureRecognizer(_retarget_settings())
    first_target = _pointing_hand()
    second_target = _aimed(first_target, 0.35, 0.7)

    recognizer.update((first_target,), timestamp=0.0)
    assert len(recognizer.update((first_target,), timestamp=0.25).activations) == 1
    assert recognizer.update((first_target,), timestamp=0.35).activations == ()

    assert recognizer.update((second_target,), timestamp=0.45).activations == ()
    assert recognizer.update((second_target,), timestamp=0.55).activations == ()
    retargeted = recognizer.update((second_target,), timestamp=0.7)
    assert len(retargeted.activations) == 1
    assert retargeted.overlays[0].state == PointingOverlayState.ACTIVE

    assert recognizer.update((second_target,), timestamp=1.0).activations == ()


def test_sweeping_finger_does_not_describe_every_object() -> None:
    recognizer = PointingGestureRecognizer(_retarget_settings())
    hand = _pointing_hand()
    recognizer.update((hand,), timestamp=0.0)
    assert len(recognizer.update((hand,), timestamp=0.25).activations) == 1

    for step, angle_deg in enumerate((30, 45, 60, 75, 90, 105)):
        angle = math.radians(angle_deg)
        sweeping = _aimed(
            hand,
            0.35 + 0.2 * math.cos(angle),
            0.5 + 0.2 * math.sin(angle),
        )
        result = recognizer.update((sweeping,), timestamp=0.35 + 0.1 * step)
        assert result.activations == ()


def test_small_tremor_does_not_retarget() -> None:
    recognizer = PointingGestureRecognizer(_retarget_settings())
    hand = _pointing_hand()
    recognizer.update((hand,), timestamp=0.0)
    recognizer.update((hand,), timestamp=0.25)

    trembling = _aimed(hand, 0.55, 0.53)
    for step in range(6):
        result = recognizer.update((trembling,), timestamp=0.35 + 0.1 * step)
        assert result.activations == ()


def test_cancelled_activation_is_retried_while_gesture_is_held() -> None:
    recognizer = PointingGestureRecognizer(_retarget_settings())
    hand = _pointing_hand()

    recognizer.update((hand,), timestamp=0.0)
    blocked = recognizer.update((hand,), timestamp=0.25).activations
    assert len(blocked) == 1
    recognizer.cancel(blocked[0])

    assert recognizer.update((hand,), timestamp=0.35).activations == ()
    assert len(recognizer.update((hand,), timestamp=0.6).activations) == 1


def test_retarget_can_be_disabled() -> None:
    settings = GestureRecognizerSettings(
        angle_ema_alpha=1.0,
        ray_ema_alpha=1.0,
        confirmation_seconds=0.2,
        retarget_enabled=False,
    )
    recognizer = PointingGestureRecognizer(settings)
    hand = _pointing_hand()
    second_target = _aimed(hand, 0.35, 0.7)

    recognizer.update((hand,), timestamp=0.0)
    recognizer.update((hand,), timestamp=0.25)
    for step in range(5):
        result = recognizer.update((second_target,), timestamp=0.35 + 0.1 * step)
        assert result.activations == ()
