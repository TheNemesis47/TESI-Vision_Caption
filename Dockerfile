# Immagine del server VisionCaption.
#
# Il pacchetto torch cambia con l'acceleratore, e il lock file ne fissa la
# variante ROCm perché è quella della macchina di sviluppo. Qui torch viene
# installato a parte, dall'indice scelto con TORCH_VARIANT:
#
#   cu128     GPU NVIDIA (workstation, WSL2)   <- predefinito
#   rocm7.2   GPU AMD
#   cpu       nessuna GPU, tutto su processore
#
# Le librerie CUDA arrivano dentro le ruote di PyTorch: serve soltanto il
# driver dell'host, esposto da nvidia-container-toolkit con --gpus all.
ARG PYTHON_IMAGE=ghcr.io/astral-sh/uv:python3.14-bookworm-slim

FROM ${PYTHON_IMAGE} AS builder

ARG TORCH_VARIANT=cu128
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never

WORKDIR /app

# Prima le sole dipendenze: cambiando il codice questo livello resta in cache.
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project \
      --no-install-package torch \
      --no-install-package torchvision \
 && uv pip install --no-cache \
      --index-url "https://download.pytorch.org/whl/${TORCH_VARIANT}" \
      torch torchvision

# --inexact: la seconda passata installa il progetto senza portarsi via il
# torch appena messo, che per il lock file è un pacchetto di troppo.
COPY src ./src
RUN uv sync --frozen --no-dev --no-editable --inexact \
      --no-install-package torch \
      --no-install-package torchvision


FROM ${PYTHON_IMAGE} AS runtime

# OpenCV e MediaPipe si appoggiano a queste librerie di sistema; l'immagine
# slim non le contiene.
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      libgl1 \
      libglib2.0-0 \
      curl \
 && rm -rf /var/lib/apt/lists/*

# Il modello dei landmark della mano è un file pubblico e stabile: sta
# nell'immagine, così il contenitore parte senza scaricare nulla.
ADD --chmod=444 \
    https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task \
    /app/models/hand_tracking/hand_landmarker.task

WORKDIR /app
COPY --from=builder /app/.venv /app/.venv
COPY src ./src

# Utente non privilegiato: il contenitore non ha motivo di girare da root.
RUN useradd --create-home --uid 10001 vision \
 && mkdir -p /app/logs /app/artifacts \
 && chown -R vision:vision /app
USER vision

# Il commit da cui è costruita l'immagine: ogni sessione del log di ricerca lo
# riporta, e qui la cartella .git non c'è.
ARG GIT_COMMIT=unknown

ENV GIT_COMMIT=${GIT_COMMIT} \
    PATH="/app/.venv/bin:${PATH}" \
    PYTHONUNBUFFERED=1 \
    SERVER_HOST=0.0.0.0 \
    SERVER_PORT=8765 \
    LOG_DIR=/app/logs \
    HAND_LANDMARKER_MODEL_PATH=/app/models/hand_tracking/hand_landmarker.task \
    FRONTEND_DIST_PATH=/app/frontend

EXPOSE 8765

# Il modello RF-DETR si carica all'avvio: il primo controllo aspetta.
HEALTHCHECK --interval=30s --timeout=5s --start-period=180s --retries=3 \
    CMD curl -fsS http://127.0.0.1:8765/health || exit 1

CMD ["python", "-m", "vision_caption"]
