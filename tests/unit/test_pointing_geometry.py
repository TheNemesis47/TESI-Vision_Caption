import pytest

from vision_caption.core.domain.hand_pose import (
    HandLandmark,
    ImageLandmark,
    WorldLandmark,
)
from vision_caption.core.services.pointing.pointing_geometry import (
    angle3d,
    calculate_finger_angles,
    calculate_pointing_vector,
    calculate_thumb_palm_ratio,
    distance3d,
    ema,
    project_vector_to_frame,
)


def _world_hand_with_joint_positions(
    joint_indices: tuple[HandLandmark, ...],
    joint_positions: tuple[WorldLandmark, ...],
) -> tuple[WorldLandmark, ...]:
    world_hand = [WorldLandmark(x=0.0, y=0.0, z=0.0) for _ in range(21)]

    for index, position in zip(joint_indices, joint_positions, strict=True):
        world_hand[index.value] = position

    return tuple(world_hand)


def test_distance3d_between_identical_points_is_zero() -> None:
    point = WorldLandmark(x=0.0, y=0.0, z=0.0)

    assert distance3d(point, point) == pytest.approx(0.0)


def test_distance3d_uses_all_coordinates() -> None:
    point_a = WorldLandmark(x=0.0, y=0.0, z=0.0)
    point_b = WorldLandmark(x=2.0, y=3.0, z=6.0)

    assert distance3d(point_a, point_b) == pytest.approx(7.0)


def test_angle3d_for_perpendicular_vectors_is_90_degrees() -> None:
    point_a = WorldLandmark(x=1.0, y=0.0, z=0.0)
    vertex = WorldLandmark(x=0.0, y=0.0, z=0.0)
    point_c = WorldLandmark(x=0.0, y=1.0, z=0.0)

    assert angle3d(point_a, vertex, point_c) == pytest.approx(90.0)


def test_angle3d_for_opposite_vectors_is_180_degrees() -> None:
    point_a = WorldLandmark(x=-1.0, y=0.0, z=0.0)
    vertex = WorldLandmark(x=0.0, y=0.0, z=0.0)
    point_c = WorldLandmark(x=1.0, y=0.0, z=0.0)

    assert angle3d(point_a, vertex, point_c) == pytest.approx(180.0)


def test_angle3d_with_zero_length_vector_is_zero() -> None:
    vertex = WorldLandmark(x=0.0, y=0.0, z=0.0)
    point_c = WorldLandmark(x=1.0, y=0.0, z=0.0)

    assert angle3d(vertex, vertex, point_c) == pytest.approx(0.0)


@pytest.mark.parametrize(
    ("finger_name", "joint_indices"),
    [
        (
            "INDICE",
            (
                HandLandmark.INDEX_FINGER_MCP,
                HandLandmark.INDEX_FINGER_PIP,
                HandLandmark.INDEX_FINGER_DIP,
                HandLandmark.INDEX_FINGER_TIP,
            ),
        ),
        (
            "MEDIO",
            (
                HandLandmark.MIDDLE_FINGER_MCP,
                HandLandmark.MIDDLE_FINGER_PIP,
                HandLandmark.MIDDLE_FINGER_DIP,
                HandLandmark.MIDDLE_FINGER_TIP,
            ),
        ),
        (
            "ANULARE",
            (
                HandLandmark.RING_FINGER_MCP,
                HandLandmark.RING_FINGER_PIP,
                HandLandmark.RING_FINGER_DIP,
                HandLandmark.RING_FINGER_TIP,
            ),
        ),
        (
            "MIGNOLO",
            (
                HandLandmark.PINKY_MCP,
                HandLandmark.PINKY_PIP,
                HandLandmark.PINKY_DIP,
                HandLandmark.PINKY_TIP,
            ),
        ),
    ],
)
def test_calculate_finger_angles_for_straight_finger(
    finger_name: str,
    joint_indices: tuple[HandLandmark, ...],
) -> None:
    straight_positions = (
        WorldLandmark(x=0.0, y=0.0, z=0.0),
        WorldLandmark(x=1.0, y=0.0, z=0.0),
        WorldLandmark(x=2.0, y=0.0, z=0.0),
        WorldLandmark(x=3.0, y=0.0, z=0.0),
    )
    world_hand = _world_hand_with_joint_positions(
        joint_indices,
        straight_positions,
    )

    angles = calculate_finger_angles(world_hand)

    assert set(angles) == {"INDICE", "MEDIO", "ANULARE", "MIGNOLO"}
    assert angles[finger_name].pip == pytest.approx(180.0)
    assert angles[finger_name].dip == pytest.approx(180.0)
    assert angles[finger_name].extension == pytest.approx(180.0)


def test_calculate_finger_angles_for_bent_index() -> None:
    index_joints = (
        HandLandmark.INDEX_FINGER_MCP,
        HandLandmark.INDEX_FINGER_PIP,
        HandLandmark.INDEX_FINGER_DIP,
        HandLandmark.INDEX_FINGER_TIP,
    )
    bent_positions = (
        WorldLandmark(x=0.0, y=0.0, z=0.0),
        WorldLandmark(x=1.0, y=0.0, z=0.0),
        WorldLandmark(x=1.0, y=1.0, z=0.0),
        WorldLandmark(x=2.0, y=1.0, z=0.0),
    )
    world_hand = _world_hand_with_joint_positions(
        index_joints,
        bent_positions,
    )

    angles = calculate_finger_angles(world_hand)

    assert angles["INDICE"].pip == pytest.approx(90.0)
    assert angles["INDICE"].dip == pytest.approx(90.0)
    assert angles["INDICE"].extension == pytest.approx(90.0)


def test_ema_weights_the_current_value() -> None:
    assert ema(previous=10.0, current=20.0, alpha=0.25) == pytest.approx(12.5)


def test_calculate_thumb_palm_ratio_is_scale_independent() -> None:
    world_hand = [WorldLandmark(x=0.0, y=0.0, z=0.0) for _ in range(21)]
    world_hand[HandLandmark.INDEX_FINGER_MCP.value] = WorldLandmark(
        x=0.0,
        y=0.0,
        z=0.0,
    )
    world_hand[HandLandmark.MIDDLE_FINGER_MCP.value] = WorldLandmark(
        x=2.0 / 3.0,
        y=0.0,
        z=0.0,
    )
    world_hand[HandLandmark.RING_FINGER_MCP.value] = WorldLandmark(
        x=4.0 / 3.0,
        y=0.0,
        z=0.0,
    )
    world_hand[HandLandmark.PINKY_MCP.value] = WorldLandmark(
        x=2.0,
        y=0.0,
        z=0.0,
    )
    world_hand[HandLandmark.THUMB_TIP.value] = WorldLandmark(
        x=0.0,
        y=1.0,
        z=0.0,
    )

    ratio = calculate_thumb_palm_ratio(tuple(world_hand))

    assert ratio == pytest.approx(0.5)


def test_calculate_thumb_palm_ratio_with_zero_width_is_infinite() -> None:
    world_hand = tuple(
        WorldLandmark(x=0.0, y=0.0, z=0.0)
        for _ in range(21)
    )

    assert calculate_thumb_palm_ratio(world_hand) == float("inf")


def test_pointing_vector_is_projected_to_the_frame_border() -> None:
    image_hand = [ImageLandmark(x=0.0, y=0.0, z=0.0) for _ in range(21)]
    image_hand[HandLandmark.INDEX_FINGER_PIP.value] = ImageLandmark(
        x=0.2,
        y=0.5,
        z=0.0,
    )
    image_hand[HandLandmark.INDEX_FINGER_TIP.value] = ImageLandmark(
        x=0.4,
        y=0.5,
        z=0.0,
    )

    vector = calculate_pointing_vector(tuple(image_hand))

    assert vector is not None
    assert vector.origin.x == pytest.approx(0.4)
    assert vector.origin.y == pytest.approx(0.5)
    assert vector.direction_x == pytest.approx(1.0)
    assert vector.direction_y == pytest.approx(0.0)

    ray = project_vector_to_frame(vector)
    assert ray is not None
    assert ray.start == vector.origin
    assert ray.end.x == pytest.approx(1.0)
    assert ray.end.y == pytest.approx(0.5)


def test_pointing_vector_rejects_a_degenerate_index_axis() -> None:
    image_hand = tuple(
        ImageLandmark(x=0.5, y=0.5, z=0.0)
        for _ in range(21)
    )

    assert calculate_pointing_vector(image_hand) is None
