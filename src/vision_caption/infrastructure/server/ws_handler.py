import base64
import asyncio
from loguru import logger
from fastapi import WebSocket, APIRouter, WebSocketDisconnect

from vision_caption.core.domain.detection import Detection
from vision_caption.core.domain.frame import Frame

router = APIRouter()

@router.websocket("/ws/vision")
async def vision_websocket(websocket: WebSocket):
    await websocket.accept()
    logger.info("New client connected via WebSocket.")
    try:
        # Recuperiamo la pipeline dallo stato dell'applicazione FastAPI
        pipeline = websocket.app.state.pipeline
        while True:
            # Ricezione bloccante del primo frame
            data = await websocket.receive_json()
            
            # --- DRAIN QUEUE ---
            # Se ci sono altri frame già arrivati nel buffer, li leggiamo tutti 
            # e teniamo solo l'ULTIMO, scartando quelli vecchi per azzerare il lag.
            skipped_frames = 0
            while True:
                try:
                    next_data = await asyncio.wait_for(websocket.receive_json(), timeout=0.005)
                    data = next_data
                    skipped_frames += 1
                except (asyncio.TimeoutError, TimeoutError):
                    break
                    
            if skipped_frames > 0:
                logger.warning(f"Skipped {skipped_frames} outdated frames to reduce lag. Processing only frame_id: {data.get('frame_id')}")
            # -------------------
            logger.debug(f"Received frame. Mode: {data['caption_mode']}")
            
            image_bytes = base64.b64decode(data["image"])
            frame: Frame = Frame(
                frame_id=data.get("frame_id", 0),
                image_bytes=image_bytes,
                caption_mode=data["caption_mode"],
                pointing_coordinates=data.get("pointing_coordinates"),
            )

            # Elaborazione del frame attraverso la pipeline
            async def send_detections(detections: list[Detection], frame_id: int):
                    #invio dei bbox
                    await websocket.send_json({
                        "type": "detections",
                        "frame_id": frame_id,
                        "detections": [d.model_dump() for d in detections]
                    })
            has_audio = False
            async for result in pipeline.process(frame, on_detections=send_detections):
                has_audio = True
                audio_base64 = base64.b64encode(result.audio.audio_bytes).decode("utf-8")
                await websocket.send_json({
                    "type": "audio",
                    "frame_id": result.frame_id,
                    "caption": result.caption,
                    "audio": audio_base64,
                    "duration": result.audio.audio_duration,
                    "format": result.audio.audio_format
                })
                logger.info(f"Sending audio response chunk: {result.audio.audio_duration:.2f}s ({len(result.audio.audio_bytes)} bytes)")
                
            if not has_audio:
                logger.debug("No audio generated (no change or rate limited).")

    except WebSocketDisconnect:
        logger.warning("Client disconnected from WebSocket.")
    except Exception as e:
        logger.exception("Error in WebSocket processing")

