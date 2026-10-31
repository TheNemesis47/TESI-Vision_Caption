import asyncio
import base64
import time

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from loguru import logger

from vision_caption.core.domain.detection import Detection
from vision_caption.core.domain.frame import CaptionMode, Frame
from vision_caption.core.domain.pointing import HandLandmarks, PointingOverlay
from vision_caption.core.ports.research_recorder_port import (
    NullResearchRecorder,
)
from vision_caption.infrastructure.settings import (
    AppSettings,
    PointingCorridorSettings,
)

router = APIRouter()

# Il codice partecipante e il compito arrivano nell'URL del WebSocket
# (?pid=P07&task=T2): sono etichette brevi, non dati da conservare interi.
RESEARCH_LABEL_MAX_LENGTH = 64


def _research_label(websocket: WebSocket, name: str) -> str | None:
    query_params = getattr(websocket, "query_params", None) or {}
    value = (query_params.get(name) or "").strip()
    return value[:RESEARCH_LABEL_MAX_LENGTH] or None


@router.websocket("/ws/vision")
async def vision_websocket(websocket: WebSocket) -> None:
    settings = getattr(websocket.app.state, "settings", None)
    if not isinstance(settings, AppSettings):
        settings = AppSettings()

    await websocket.accept()
    try:
        await websocket.send_json(
            {
                "type": "stream_config",
                "protocol_version": 1,
                "fps": {
                    "AUTO": settings.server.auto_input_fps,
                    "POINTING": settings.server.pointing_input_fps,
                },
                "max_in_flight": 1,
                "max_buffered_amount_bytes": 262_144,
            }
        )
    except WebSocketDisconnect:
        logger.debug(
            "Client disconnected before receiving the initial stream_config."
        )
        return

    logger.info("New client connected via WebSocket.")
    research_sessions = getattr(websocket.app.state, "research_sessions", None)
    headers = getattr(websocket, "headers", None) or {}
    research = (
        research_sessions.open(
            participant_id=_research_label(websocket, "pid"),
            task_id=_research_label(websocket, "task"),
            user_agent=headers.get("user-agent"),
        )
        if research_sessions is not None
        else NullResearchRecorder()
    )
    pipeline_factory = getattr(websocket.app.state, "pipeline_factory", None)
    owns_pipeline = pipeline_factory is not None
    pipeline = (
        pipeline_factory(research)
        if owns_pipeline
        else websocket.app.state.pipeline
    )
    current_mode: CaptionMode | None = None
    frames_processed = 0
    frames_dropped = 0
    utterances = 0
    speech_seconds = 0.0
    end_reason = "client_disconnected"
    corridor_settings: PointingCorridorSettings = settings.pointing.corridor

    async def send_optional_message(message: dict) -> None:
        try:
            await asyncio.wait_for(
                websocket.send_json(message),
                timeout=(
                    settings.server.websocket_optional_send_timeout_seconds
                ),
            )
        except (asyncio.TimeoutError, TimeoutError):
            logger.debug(
                "Optional WebSocket message dropped because client is slow: "
                f"{message.get('type')}"
            )

    async def send_detections(
        detections: list[Detection],
        frame_id: int,
    ) -> None:
        await send_optional_message(
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
        hands: tuple[HandLandmarks, ...] = (),
    ) -> None:
        await send_optional_message(
            {
                "type": "pointing_overlay",
                "frame_id": frame_id,
                "overlays": [
                    overlay.model_dump(mode="json") for overlay in overlays
                ],
                "hands": [hand.model_dump(mode="json") for hand in hands],
                "corridor": corridor_settings.websocket_payload(),
            }
        )

    async def send_stop_audio(frame_id: int) -> None:
        # Non opzionale: se il telefono non lo riceve, la voce continua.
        await websocket.send_json({"type": "stop_audio", "frame_id": frame_id})

    def frame_interval_ms(mode: CaptionMode) -> int:
        fps = (
            settings.server.auto_input_fps
            if mode == CaptionMode.AUTO
            else settings.server.pointing_input_fps
        )
        return round(1000.0 / fps)

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
                frames_dropped += skipped_frames
                research.record(
                    "frames_dropped",
                    count=skipped_frames,
                    kept_frame_id=data.get("frame_id"),
                )
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
            if frame.caption_mode != current_mode:
                research.record(
                    "mode_change",
                    frame_id=frame.frame_id,
                    previous=current_mode.value if current_mode else None,
                    current=frame.caption_mode.value,
                )
                current_mode = frame.caption_mode
            frames_processed += 1

            frame_started_at = time.perf_counter()
            try:
                has_audio = False
                async for result in pipeline.process(
                    frame,
                    on_detections=send_detections,
                    on_pointing_overlay=send_pointing_overlay,
                    on_stop_audio=send_stop_audio,
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
                    utterances += 1
                    speech_seconds += result.audio.audio_duration
                    research.record(
                        "utterance",
                        mode=frame.caption_mode.value,
                        frame_id=result.frame_id,
                        text=result.caption,
                        chars=len(result.caption),
                        audio_duration_s=round(result.audio.audio_duration, 3),
                        # Dalla ricezione del frame all'invio dell'audio: il
                        # tempo di rete e di riproduzione sul telefono resta fuori.
                        frame_to_audio_ms=round(
                            (time.perf_counter() - frame_started_at) * 1000.0,
                            1,
                        ),
                    )
                    logger.info(
                        "Sending audio response chunk: "
                        f"{result.audio.audio_duration:.2f}s "
                        f"({len(result.audio.audio_bytes)} bytes)"
                    )

                if not has_audio:
                    logger.debug(
                        "No audio generated (no change or rate limited)."
                    )
            finally:
                await websocket.send_json(
                    {
                        "type": "frame_done",
                        "frame_id": frame.frame_id,
                        "min_frame_interval_ms": frame_interval_ms(
                            frame.caption_mode
                        ),
                        "processing_ms": round(
                            (time.perf_counter() - frame_started_at) * 1000.0,
                            1,
                        ),
                    }
                )

    except WebSocketDisconnect:
        logger.warning("Client disconnected from WebSocket.")
    except Exception as error:
        if isinstance(error, RuntimeError) and "close message" in str(error):
            # Il telefono ha chiuso mentre il server rispondeva: è una
            # disconnessione, non un errore del server.
            logger.warning("Client disconnected while the server was answering.")
        else:
            end_reason = "server_error"
            research.record(
                "error",
                component="websocket",
                error_type=type(error).__name__,
                message=str(error)[:500],
            )
            logger.exception("Error in WebSocket processing")
    finally:
        research.record(
            "session_end",
            reason=end_reason,
            frames_processed=frames_processed,
            frames_dropped=frames_dropped,
            utterances=utterances,
            speech_seconds=round(speech_seconds, 3),
        )
        if research_sessions is not None:
            research_sessions.close(research)
        if owns_pipeline:
            await pipeline.close()
