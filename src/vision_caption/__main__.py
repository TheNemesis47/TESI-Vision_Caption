import os
import sys
import logging
import uvicorn
from loguru import logger
from vision_caption.infrastructure.server.app import create_app


class InterceptHandler(logging.Handler):
    """Reindirizza i log della libreria standard (uvicorn, asyncio, ...) su loguru."""

    def emit(self, record: logging.LogRecord):
        # Recupera il livello loguru corrispondente, se esiste
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Trova il frame chiamante per mantenere corretti file/riga nel log
        frame, depth = sys._getframe(6), 6
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def _intercept_stdlib_logging():
    """Cattura il logging stdlib e lo instrada verso loguru (uvicorn incluso)."""
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)
    # Sostituisce gli handler dei logger di uvicorn con l'intercettatore
    for name in (
        "uvicorn",
        "uvicorn.error",
        "uvicorn.access",
        "asyncio",
        "websockets",
    ):
        lib_logger = logging.getLogger(name)
        lib_logger.handlers = [InterceptHandler()]
        lib_logger.propagate = False


def _setup_file_logging():
    """Aggiunge un sink su file nella cartella logs/ (oltre alla console).

    - Ruota il file quando supera i 10 MB.
    - Conserva gli ultimi 10 giorni di log, comprimendo i vecchi in .zip.
    Percorso configurabile via env var LOG_DIR (default: ./logs).
    """
    log_dir = os.environ.get("LOG_DIR", "logs")
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, "vision_caption_{time:YYYY-MM-DD}.log")
    logger.add(
        log_path,
        rotation="10 MB",
        retention="10 days",
        compression="zip",
        level=os.environ.get("LOG_LEVEL", "DEBUG"),
        enqueue=True,  # thread/async-safe
        backtrace=True,
        diagnose=True,
    )
    logger.info(f"File logging enabled. Writing logs to: {os.path.abspath(log_dir)}")


def main():
    _setup_file_logging()
    _intercept_stdlib_logging()
    logger.info("Initializing Vision Caption Server Application...")
    app = create_app()
    
    ssl_key = "key.pem"
    ssl_cert = "cert.pem"
    
    if os.path.exists(ssl_key) and os.path.exists(ssl_cert):
        logger.info(f"SSL certificates found ({ssl_key}, {ssl_cert}). Starting uvicorn server on https://0.0.0.0:8765 (WSS enabled)...")
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8765,
            ws_ping_interval=300.0,
            ws_ping_timeout=300.0,
            ssl_keyfile=ssl_key,
            ssl_certfile=ssl_cert,
            log_config=None,  # usa i nostri sink loguru invece di riconfigurare
            access_log=True,
        )
    else:
        logger.info("Starting uvicorn server on http://0.0.0.0:8765...")
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8765,
            ws_ping_interval=300.0,
            ws_ping_timeout=300.0,
            log_config=None,  # usa i nostri sink loguru invece di riconfigurare
            access_log=True,
        )

if __name__ == '__main__':
    main()