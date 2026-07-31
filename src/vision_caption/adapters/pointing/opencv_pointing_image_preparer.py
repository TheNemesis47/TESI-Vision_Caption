from dataclasses import dataclass
from datetime import datetime, timezone
from math import sqrt
from pathlib import Path
from uuid import uuid4

import cv2
from loguru import logger
import numpy as np

from vision_caption.core.domain.frame import Frame
from vision_caption.core.domain.pointing import PointingEvent, PointingRay
from vision_caption.core.ports.pointing_image_preparer_port import (
    PointingImagePreparerPort,
    PointingImages,
)


@dataclass(frozen=True)
class PointingImageSettings:
    start_half_width_ratio: float = 0.008
    min_end_half_width_ratio: float = 0.03
    expansion_ratio: float = 0.04
    overlay_alpha: float = 0.14
    outside_brightness: float = 0.14
    crop_padding_ratio: float = 0.025
    jpeg_quality: int = 90
    guide_color_bgr: tuple[int, int, int] = (0, 255, 255)
    debug_save_images: bool = False
    debug_output_dir: Path = Path("artifacts/pointing_debug")

    def __post_init__(self) -> None:
        ratio_values = (
            self.start_half_width_ratio,
            self.min_end_half_width_ratio,
            self.expansion_ratio,
            self.overlay_alpha,
            self.outside_brightness,
            self.crop_padding_ratio,
        )
        if any(value < 0.0 for value in ratio_values):
            raise ValueError("I parametri geometrici non possono essere negativi")
        if not 0.0 <= self.overlay_alpha <= 1.0:
            raise ValueError("overlay_alpha deve essere compreso fra 0 e 1")
        if not 0.0 <= self.outside_brightness <= 1.0:
            raise ValueError("outside_brightness deve essere compreso fra 0 e 1")
        if not 1 <= self.jpeg_quality <= 100:
            raise ValueError("jpeg_quality deve essere compreso fra 1 e 100")
        if (
            len(self.guide_color_bgr) != 3
            or any(not 0 <= component <= 255 for component in self.guide_color_bgr)
        ):
            raise ValueError("guide_color_bgr deve contenere tre valori fra 0 e 255")


def normalized_ray_to_pixels(
    ray: PointingRay,
    frame_width: int,
    frame_height: int,
) -> tuple[tuple[int, int], tuple[int, int]]:
    def to_pixel(x: float, y: float) -> tuple[int, int]:
        return (
            round(x * max(0, frame_width - 1)),
            round(y * max(0, frame_height - 1)),
        )

    return (
        to_pixel(ray.start.x, ray.start.y),
        to_pixel(ray.end.x, ray.end.y),
    )


def build_corridor_polygon(
    ray: PointingRay,
    frame_width: int,
    frame_height: int,
    settings: PointingImageSettings,
) -> np.ndarray | None:
    start, end = normalized_ray_to_pixels(ray, frame_width, frame_height)
    start_x, start_y = start
    end_x, end_y = end
    direction_x = end_x - start_x
    direction_y = end_y - start_y
    ray_length = sqrt(direction_x * direction_x + direction_y * direction_y)
    if ray_length == 0:
        return None

    short_side = max(1, min(frame_width, frame_height))
    start_half_width = settings.start_half_width_ratio * short_side
    end_half_width = max(
        settings.min_end_half_width_ratio * short_side,
        ray_length * settings.expansion_ratio,
    )
    perpendicular_x = -direction_y / ray_length
    perpendicular_y = direction_x / ray_length

    points = (
        (
            start_x + perpendicular_x * start_half_width,
            start_y + perpendicular_y * start_half_width,
        ),
        (
            start_x - perpendicular_x * start_half_width,
            start_y - perpendicular_y * start_half_width,
        ),
        (
            end_x - perpendicular_x * end_half_width,
            end_y - perpendicular_y * end_half_width,
        ),
        (
            end_x + perpendicular_x * end_half_width,
            end_y + perpendicular_y * end_half_width,
        ),
    )
    clipped = [
        (
            round(max(0.0, min(frame_width - 1.0, x))),
            round(max(0.0, min(frame_height - 1.0, y))),
        )
        for x, y in points
    ]
    return np.asarray(clipped, dtype=np.int32)


class OpenCVPointingImagePreparer(PointingImagePreparerPort):
    def __init__(
        self,
        settings: PointingImageSettings | None = None,
    ) -> None:
        self._settings = settings or PointingImageSettings()

    async def prepare(
        self,
        frame: Frame,
        event: PointingEvent,
    ) -> PointingImages:
        # Viene eseguito soltanto all'attivazione del gesto, non su ogni frame.
        return self._prepare_sync(frame, event)

    def _prepare_sync(
        self,
        frame: Frame,
        event: PointingEvent,
    ) -> PointingImages:
        encoded = np.frombuffer(frame.image_bytes, dtype=np.uint8)
        clean_frame = cv2.imdecode(encoded, cv2.IMREAD_COLOR)
        if clean_frame is None:
            raise ValueError("Il frame POINTING non contiene un JPEG valido")

        context_frame = clean_frame.copy()
        focus_frame = self._create_focus_frame(clean_frame, event.ray)
        self._draw_guides(
            context_frame,
            event.ray,
            fill_alpha=self._settings.overlay_alpha,
        )

        images = PointingImages(
            context_jpeg=self._encode_jpeg(context_frame),
            focus_jpeg=self._encode_jpeg(focus_frame),
            clean_jpeg=frame.image_bytes,
        )
        if self._settings.debug_save_images:
            self._save_debug_images(frame.frame_id, images)
        return images

    def _save_debug_images(
        self,
        frame_id: int,
        images: PointingImages,
    ) -> None:
        """Salva gli stessi tre JPEG che verranno inseriti nel payload VLM."""
        timestamp = datetime.now(timezone.utc).strftime(
            "%Y%m%dT%H%M%S_%fZ"
        )
        capture_dir = self._settings.debug_output_dir / (
            f"frame_{frame_id:08d}_{timestamp}_{uuid4().hex[:8]}"
        )

        try:
            capture_dir.mkdir(parents=True, exist_ok=False)
            (capture_dir / "01_context_with_corridor.jpg").write_bytes(
                images.context_jpeg
            )
            (
                capture_dir / "02_focus_darkened_and_cropped.jpg"
            ).write_bytes(images.focus_jpeg)
            (capture_dir / "03_clean_original.jpg").write_bytes(
                images.clean_jpeg
            )
        except OSError:
            logger.exception(
                f"Impossibile salvare le immagini POINTING di debug in "
                f"{capture_dir}"
            )
            return

        logger.info(
            f"Salvate le tre immagini POINTING inviate al VLM in {capture_dir}"
        )

    def _draw_guides(
        self,
        image: np.ndarray,
        ray: PointingRay,
        *,
        fill_alpha: float,
    ) -> np.ndarray | None:
        frame_height, frame_width = image.shape[:2]
        polygon = build_corridor_polygon(
            ray,
            frame_width,
            frame_height,
            self._settings,
        )
        if polygon is None:
            return None

        if fill_alpha > 0.0:
            overlay = image.copy()
            cv2.fillConvexPoly(
                overlay,
                polygon,
                self._settings.guide_color_bgr,
                cv2.LINE_AA,
            )
            cv2.addWeighted(
                overlay,
                fill_alpha,
                image,
                1.0 - fill_alpha,
                0.0,
                dst=image,
            )

        start, end = normalized_ray_to_pixels(
            ray,
            frame_width,
            frame_height,
        )
        cv2.polylines(
            image,
            [polygon],
            True,
            self._settings.guide_color_bgr,
            2,
            cv2.LINE_AA,
        )
        cv2.line(
            image,
            start,
            end,
            self._settings.guide_color_bgr,
            2,
            cv2.LINE_AA,
        )
        cv2.circle(
            image,
            start,
            7,
            self._settings.guide_color_bgr,
            2,
            cv2.LINE_AA,
        )
        return polygon

    def _create_focus_frame(
        self,
        clean_frame: np.ndarray,
        ray: PointingRay,
    ) -> np.ndarray:
        frame_height, frame_width = clean_frame.shape[:2]
        polygon = build_corridor_polygon(
            ray,
            frame_width,
            frame_height,
            self._settings,
        )
        if polygon is None:
            return clean_frame.copy()

        focus_frame = cv2.convertScaleAbs(
            clean_frame,
            alpha=self._settings.outside_brightness,
            beta=0,
        )
        corridor_mask = np.zeros((frame_height, frame_width), dtype=np.uint8)
        cv2.fillConvexPoly(corridor_mask, polygon, 255, cv2.LINE_AA)
        cv2.copyTo(clean_frame, corridor_mask, focus_frame)
        self._draw_guides(focus_frame, ray, fill_alpha=0.0)

        crop_x, crop_y, crop_width, crop_height = cv2.boundingRect(polygon)
        padding = round(
            self._settings.crop_padding_ratio
            * max(1, min(frame_width, frame_height))
        )
        x_min = max(0, crop_x - padding)
        y_min = max(0, crop_y - padding)
        x_max = min(frame_width, crop_x + crop_width + padding)
        y_max = min(frame_height, crop_y + crop_height + padding)
        return focus_frame[y_min:y_max, x_min:x_max].copy()

    def _encode_jpeg(self, image: np.ndarray) -> bytes:
        success, encoded = cv2.imencode(
            ".jpg",
            image,
            [cv2.IMWRITE_JPEG_QUALITY, self._settings.jpeg_quality],
        )
        if not success:
            raise RuntimeError("Impossibile codificare l'immagine POINTING")
        return encoded.tobytes()
