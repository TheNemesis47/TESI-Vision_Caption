import asyncio
import base64

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from loguru import logger

from vision_caption.core.domain.detection import Detection
from vision_caption.core.domain.frame import Frame
from vision_caption.core.domain.pointing import PointingOverlay
from vision_caption.infrastructure.settings import (
    AppSettings,
    PointingCorridorSettings,
)

router = APIRouter()


@router.websocket("/ws/vision")
async def vision_websocket(websocket: WebSocket) -> None:
    await websocket.accept()
    logger.info("New client connected via WebSocket.")
    pipeline_factory = getattr(websocket.app.state, "pipeline_factory", None)
    owns_pipeline = pipeline_factory is not None
    pipeline = pipeline_factory() if owns_pipeline else websocket.app.state.pipeline
    settings = getattr(websocket.app.state, "settings", None)
    if not isinstance(settings, AppSettings):
        settings = AppSettings()
    corridor_settings: PointingCorridorSettings = settings.pointing.corridor

    async def send_detections(
        detections: list[Detection],
        frame_id: int,
    ) -> None:
        await websocket.send_json(
            {
                "type": "detections",
                "frame_id": frame_id,
                "detections": [
                    detection.model_dump() for detection in detections
                ],
            }
        )

    async def send_pointing_overlay(
        overlays: tuple[PointingOverlay, ...],
        frame_id: int,
    ) -> None:
        await websocket.send_json(
            {
                "type": "pointing_overlay",
                "frame_id": frame_id,
                "overlays": [
                    overlay.model_dump(mode="json") for overlay in overlays
                ],
                "corridor": corridor_settings.websocket_payload(),
            }
        )

    try:
        while True:
            # Ricezione bloccante del primo frame
            data = await websocket.receive_json()

            # --- DRAIN QUEUE ---
            # Se ci sono altri frame già arrivati nel buffer, li leggiamo tutti
            # e teniamo solo l'ULTIMO, scartando quelli vecchi per azzerare il lag.
            skipped_frames = 0
            while True:
                try:
                    next_data = await asyncio.wait_for(
                        websocket.receive_json(),
                        timeout=settings.server.websocket_drain_timeout_seconds,
                    )
                    data = next_data
                    skipped_frames += 1
                except (asyncio.TimeoutError, TimeoutError):
                    break

            if skipped_frames > 0:
                logger.warning(
                    f"Skipped {skipped_frames} outdated frames to reduce lag. "
                    f"Processing only frame_id: {data.get('frame_id')}"
                )
            # -------------------
            logger.debug(f"Received frame. Mode: {data['caption_mode']}")

            image_bytes = base64.b64decode(data["image"])
            frame: Frame = Frame(
                frame_id=data.get("frame_id", 0),
                image_bytes=image_bytes,
                caption_mode=data["caption_mode"],
                pointing_coordinates=data.get("pointing_coordinates"),
            )

            has_audio = False
            async for result in pipeline.process(
                frame,
                on_detections=send_detections,
                on_pointing_overlay=send_pointing_overlay,
            ):
                has_audio = True
                audio_base64 = base64.b64encode(
                    result.audio.audio_bytes
                ).decode("utf-8")
                await websocket.send_json(
                    {
                        "type": "audio",
                        "frame_id": result.frame_id,
                        "caption": result.caption,
                        "audio": audio_base64,
                        "duration": result.audio.audio_duration,
                        "format": result.audio.audio_format,
                    }
                )
                logger.info(
                    "Sending audio response chunk: "
                    f"{result.audio.audio_duration:.2f}s "
                    f"({len(result.audio.audio_bytes)} bytes)"
                )

            if not has_audio:
                logger.debug("No audio generated (no change or rate limited).")

    except WebSocketDisconnect:
        logger.warning("Client disconnected from WebSocket.")
    except Exception:
        logger.exception("Error in WebSocket processing")
    finally:
        if owns_pipeline:
            await pipeline.close()
