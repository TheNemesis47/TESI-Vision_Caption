# vision-caption

Server WebSocket per **audio-descrizione ambientale in tempo reale** destinato
a utenti non vedenti / ipovedenti con visore Meta Quest 3.

Il server riceve frame JPEG via WebSocket, rileva se la scena è cambiata,
genera una descrizione in italiano usando un VLM (Gemma 4 via Ollama),
sintetizza la voce con Chatterbox TTS, e rimanda l'audio WAV al client.

Porta di default: **8765**

---

## Pipeline

```
Frame JPEG  →  WebSocket IN
      ↓
 Scene Change?  (SSIM)   ──no──→  scarta
      ↓ sì
 Rate Limiter   ──troppo presto──→  scarta
      ↓ ok
 VLM Caption   (Gemma 4 / Ollama)
      ↓
 TTS Synthesis  (Chatterbox)
      ↓
Audio WAV/Opus  →  WebSocket OUT  →  Meta Quest 3
```

Modalità di acquisizione:
- **AUTO**: scansione continua, pipeline completa
- **POINTING**: bypassa scene detection e rate limiter, descrive subito l'area indicata

---

## Architettura — Hexagonal (Ports & Adapters)

```
┌──────────────────────────────────────────────────────┐
│  infrastructure                                       │
│  (FastAPI, uvicorn, DI container, AppSettings)        │
│  ┌────────────────────────────────────────────────┐   │
│  │  adapters                                      │   │
│  │  SSIMSceneDetector | OllamaCaptionGenerator    │   │
│  │  ChatterboxSynthesizer                         │   │
│  │  ┌──────────────────────────────────────────┐  │   │
│  │  │  core                                    │  │   │
│  │  │  domain: FrameData, Caption, AudioResult  │  │   │
│  │  │  ports:  SceneDetectorPort,               │  │   │
│  │  │          CaptionGeneratorPort,            │  │   │
│  │  │          SpeechSynthesizerPort            │  │   │
│  │  │  services: CaptionPipeline, RateLimiter   │  │   │
│  │  └──────────────────────────────────────────┘  │   │
│  └────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────┘
```

**Regola fondamentale**: `core/` non importa MAI librerie esterne.
Gli adapters implementano i ports definiti nel core.
L'infrastructure assembla tutto tramite dependency injection.

---

## Requisiti

- Python 3.12
- uv (`brew install uv` oppure `curl -LsSf https://astral.sh/uv/install.sh | sh`)
- GPU NVIDIA con CUDA 12.x (per Chatterbox TTS)
- Ollama installato con `gemma4:e4b` (`ollama pull gemma4:e4b`)

---

## Installazione

```bash
git clone <repo>
cd vision-caption
uv sync
```

---

## Avvio

```bash
# Server (porta 8765)
uv run python -m vision_caption

# Con mock (senza GPU, per sviluppo)
USE_MOCKS=true uv run python -m vision_caption

# Client di test con webcam
uv run python scripts/test_client_webcam.py --host localhost --port 8765
```

---

## Test

```bash
# Unit test (senza GPU)
uv run pytest tests/unit/ -v

# Integration test (richiede Ollama + GPU)
uv run pytest tests/integration/ -v

# Benchmark latenza
uv run python scripts/benchmark_latency.py
```

---

## Struttura

```
src/vision_caption/
├── core/           ← PURO. Solo stdlib + Pydantic. Zero import esterni.
│   ├── domain/     ← Modelli di dominio (FrameData, Caption, AudioResult)
│   ├── ports/      ← Contratti astratti (Protocol classes)
│   └── services/   ← Logica di business (CaptionPipeline, RateLimiter)
├── adapters/       ← Implementazioni concrete dei ports
│   ├── scene/      ← SSIMSceneDetector
│   ├── vlm/        ← OllamaCaptionGenerator
│   └── tts/        ← ChatterboxSynthesizer
└── infrastructure/ ← FastAPI, DI container, AppSettings
    └── server/     ← WebSocket handler, health endpoint
```

---

## Configurazione

Il file `config.yaml` contiene i valori di default. Ogni valore è sovrascrivibile
con variabile d'ambiente (es. `OLLAMA__MODEL_NAME=gemma4:e4b`).

Valori principali:
- `server.host` / `server.port` — binding del server WebSocket
- `scene_detection.ssim_threshold` — soglia SSIM per cambio scena (0–1)
- `scene_detection.min_caption_interval_sec` — throttling caption
- `vlm.model_name` — modello Ollama
- `vlm.language` — lingua descrizioni (`it` per italiano)
- `tts.model` — modello Chatterbox

---

## Deploy — Cluster HPC (PurpleJeans)

```bash
sbatch deploy/slurm_job.sh
```

```bash
# Oppure Docker
docker compose -f deploy/docker-compose.yml up
```
