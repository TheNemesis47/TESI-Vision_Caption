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
        "INDICE": FingerAngles(pip=140.0, dip=140.0),
        "MEDIO": FingerAngles(pip=130.0, dip=130.0),
        "ANULARE": FingerAngles(pip=130.0, dip=130.0),
        "MIGNOLO": FingerAngles(pip=130.0, dip=130.0),
    }

    assert not is_pointing_pose(
        angles,
        1.3,
        active=False,
        settings=settings,
    )
    assert is_pointing_pose(
        angles,
        1.3,
        active=True,
        settings=settings,
    )


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
