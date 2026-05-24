import base64
from loguru import logger
from fastapi import WebSocket, APIRouter, WebSocketDisconnect
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
            # Ricezione JSON contenente l'immagine in Base64 e la modalità
            data = await websocket.receive_json()
            
            image_bytes = base64.b64decode(data["image"])
            frame: Frame = Frame(
                image_bytes=image_bytes,
                caption_mode=data["caption_mode"],
                pointing_coordinates=data.get("pointing_coordinates"),
            )

            # Elaborazione del frame attraverso la pipeline
            audio = await pipeline.process(frame)
            
            # Se la pipeline ha generato un audio (scena cambiata), inviamo i byte binari WAV al client
            if audio is not None:
                logger.info(f"Sending audio response: {audio.audio_duration:.2f}s")
                await websocket.send_bytes(audio.audio_bytes)

    except WebSocketDisconnect:
        logger.warning("Client disconnected from WebSocket.")
    except Exception as e:
        logger.error(f"Error in WebSocket processing: {e}")
