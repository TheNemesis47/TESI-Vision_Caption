from math import acos, degrees, sqrt

from vision_caption.core.domain.hand_pose import (
    HandLandmark,
    ImageLandmark,
    WorldLandmark,
)
from vision_caption.core.domain.pointing import (
    FingerAngles,
    NormalizedPoint,
    PointingRay,
    PointingVector,
)


FINGER_JOINTS: dict[
    str,
    tuple[HandLandmark, HandLandmark, HandLandmark, HandLandmark],
] = {
    "INDICE": (
        HandLandmark.INDEX_FINGER_MCP,
        HandLandmark.INDEX_FINGER_PIP,
        HandLandmark.INDEX_FINGER_DIP,
        HandLandmark.INDEX_FINGER_TIP,
    ),
    "MEDIO": (
        HandLandmark.MIDDLE_FINGER_MCP,
        HandLandmark.MIDDLE_FINGER_PIP,
        HandLandmark.MIDDLE_FINGER_DIP,
        HandLandmark.MIDDLE_FINGER_TIP,
    ),
    "ANULARE": (
        HandLandmark.RING_FINGER_MCP,
        HandLandmark.RING_FINGER_PIP,
        HandLandmark.RING_FINGER_DIP,
        HandLandmark.RING_FINGER_TIP,
    ),
    "MIGNOLO": (
        HandLandmark.PINKY_MCP,
        HandLandmark.PINKY_PIP,
        HandLandmark.PINKY_DIP,
        HandLandmark.PINKY_TIP,
    ),
}

PALM_MCP_INDICES = (
    HandLandmark.INDEX_FINGER_MCP,
    HandLandmark.MIDDLE_FINGER_MCP,
    HandLandmark.RING_FINGER_MCP,
    HandLandmark.PINKY_MCP,
)


def ema(previous: float, current: float, alpha: float) -> float:
    """Applica una media mobile esponenziale a un valore scalare."""
    return previous * (1.0 - alpha) + current * alpha


def angle3d(point_a: WorldLandmark, vertex: WorldLandmark, point_c: WorldLandmark) -> float:
    """Calcola in gradi l'angolo A-vertice-C usando coordinate 3D."""
    vector_a = (
        point_a.x - vertex.x,
        point_a.y - vertex.y,
        point_a.z - vertex.z,
    )
    vector_c = (
        point_c.x - vertex.x,
        point_c.y - vertex.y,
        point_c.z - vertex.z,
    )

    dot_product = sum(a * c for a, c in zip(vector_a, vector_c))
    length_a = sqrt(sum(component * component for component in vector_a))
    length_c = sqrt(sum(component * component for component in vector_c))

    if length_a == 0 or length_c == 0:
        return 0.0

    cosine = dot_product / (length_a * length_c)
    cosine = max(-1.0, min(1.0, cosine))
    return degrees(acos(cosine))


def distance3d(point_a: WorldLandmark, point_b: WorldLandmark) -> float:
    return sqrt(
        (point_a.x - point_b.x) ** 2
        + (point_a.y - point_b.y) ** 2
        + (point_a.z - point_b.z) ** 2
    )


def calculate_finger_angles(
    world_hand: tuple[WorldLandmark, ...],
) -> dict[str, FingerAngles]:
    angles: dict[str, FingerAngles] = {}

    for finger_name, joint_indices in FINGER_JOINTS.items():
        mcp_index, pip_index, dip_index, tip_index = joint_indices
        mcp = world_hand[mcp_index.value]
        pip = world_hand[pip_index.value]
        dip = world_hand[dip_index.value]
        tip = world_hand[tip_index.value]

        angles[finger_name] = FingerAngles(
            pip=angle3d(mcp, pip, dip),
            dip=angle3d(pip, dip, tip),
        )

    return angles


def calculate_thumb_palm_ratio(
    world_hand: tuple[WorldLandmark, ...],
) -> float:
    """Misura la distanza del pollice rispetto alla larghezza del palmo."""
    index_mcp = world_hand[HandLandmark.INDEX_FINGER_MCP.value]
    pinky_mcp = world_hand[HandLandmark.PINKY_MCP.value]
    palm_width = distance3d(index_mcp, pinky_mcp)
    if palm_width == 0:
        return float("inf")

    thumb_tip = world_hand[HandLandmark.THUMB_TIP.value]
    nearest_palm_distance = min(
        distance3d(thumb_tip, world_hand[landmark.value])
        for landmark in PALM_MCP_INDICES
    )
    return nearest_palm_distance / palm_width


def calculate_pointing_vector(
    image_hand: tuple[ImageLandmark, ...],
    min_length: float = 0.0125,
) -> PointingVector | None:
    """Crea un vettore normalizzato dalla falange PIP alla punta dell'indice."""
    pip = image_hand[HandLandmark.INDEX_FINGER_PIP.value]
    tip = image_hand[HandLandmark.INDEX_FINGER_TIP.value]

    direction_x = tip.x - pip.x
    direction_y = tip.y - pip.y
    direction_length = sqrt(direction_x * direction_x + direction_y * direction_y)
    if direction_length < min_length:
        return None

    return PointingVector(
        origin=NormalizedPoint(
            x=max(0.0, min(1.0, tip.x)),
            y=max(0.0, min(1.0, tip.y)),
        ),
        direction_x=direction_x / direction_length,
        direction_y=direction_y / direction_length,
    )


def project_vector_to_frame(vector: PointingVector) -> PointingRay | None:
    """Estende un vettore normalizzato fino al primo bordo dell'immagine."""
    origin_x = vector.origin.x
    origin_y = vector.origin.y
    distances: list[float] = []

    if vector.direction_x > 0:
        distances.append((1.0 - origin_x) / vector.direction_x)
    elif vector.direction_x < 0:
        distances.append((0.0 - origin_x) / vector.direction_x)

    if vector.direction_y > 0:
        distances.append((1.0 - origin_y) / vector.direction_y)
    elif vector.direction_y < 0:
        distances.append((0.0 - origin_y) / vector.direction_y)

    positive_distances = [distance for distance in distances if distance >= 0]
    if not positive_distances:
        return None

    projection_length = min(positive_distances)
    end_x = origin_x + vector.direction_x * projection_length
    end_y = origin_y + vector.direction_y * projection_length

    return PointingRay(
        start=vector.origin,
        end=NormalizedPoint(
            x=max(0.0, min(1.0, end_x)),
            y=max(0.0, min(1.0, end_y)),
        ),
    )
