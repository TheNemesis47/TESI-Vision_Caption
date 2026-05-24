import uvicorn
from loguru import logger
from vision_caption.infrastructure.server.app import create_app

def main():
    logger.info("Initializing Vision Caption Server Application...")
    app = create_app()
    
    logger.info("Starting uvicorn server on http://0.0.0.0:8765...")
    uvicorn.run(app, host="0.0.0.0", port=8765)

if __name__ == '__main__':
    main()