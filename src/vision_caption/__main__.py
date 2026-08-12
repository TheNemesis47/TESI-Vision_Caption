import sys
import logging
import uvicorn
from loguru import logger
from vision_caption.infrastructure.settings import AppSettings, ServerSettings
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

    # Queste librerie possono scrivere payload WebSocket Base64 e il trace di
    # ogni richiesta HTTP. Sono utili soltanto in troubleshooting profondo e
    # rendono i log di produzione enormi senza aggiungere segnali operativi.
    for name in ("asyncio", "websockets", "httpcore", "httpx"):
        logging.getLogger(name).setLevel(logging.WARNING)


def _setup_file_logging(settings: ServerSettings):
    """Aggiunge un sink su file nella cartella logs/ (oltre alla console).

    - Ruota il file quando supera i 10 MB.
    - Conserva gli ultimi 10 giorni di log, comprimendo i vecchi in .zip.
    Il percorso e il livello arrivano dalla configurazione centralizzata.
    """
    settings.log_dir.mkdir(parents=True, exist_ok=True)
    log_path = settings.log_dir / "vision_caption_{time:YYYY-MM-DD}.log"
    logger.add(
        str(log_path),
        rotation="10 MB",
        retention="10 days",
        compression="zip",
        level=settings.log_level,
        enqueue=True,  # thread/async-safe
        backtrace=True,
        diagnose=True,
    )
    logger.info(
        f"File logging enabled. Writing logs to: "
        f"{settings.log_dir.resolve()}"
    )


def main():
    settings = AppSettings.from_env()
    _setup_file_logging(settings.server)
    _intercept_stdlib_logging()
    logger.info("Initializing Vision Caption Server Application...")
    app = create_app(settings)

    server = settings.server
    ssl_key = server.ssl_key_path
    ssl_cert = server.ssl_cert_path

    common_options = {
        "host": server.host,
        "port": server.port,
        "ws_ping_interval": server.websocket_ping_interval_seconds,
        "ws_ping_timeout": server.websocket_ping_timeout_seconds,
        "log_config": None,
        "access_log": True,
    }

    if ssl_key.exists() and ssl_cert.exists():
        logger.info(
            f"SSL certificates found ({ssl_key}, {ssl_cert}). "
            f"Starting uvicorn server on https://{server.host}:{server.port} "
            f"(WSS enabled)..."
        )
        uvicorn.run(
            app,
            **common_options,
            ssl_keyfile=str(ssl_key),
            ssl_certfile=str(ssl_cert),
        )
    else:
        logger.info(
            f"Starting uvicorn server on "
            f"http://{server.host}:{server.port}..."
        )
        uvicorn.run(
            app,
            **common_options,
        )

if __name__ == '__main__':
    main()
