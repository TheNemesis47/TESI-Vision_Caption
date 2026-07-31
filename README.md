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
- **POINTING**: MediaPipe analizza la mano; soltanto una gesture di puntamento
  stabile attiva corridoio visivo, VLM strutturato e una singola sintesi TTS

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

La configurazione è centralizzata e validata dai modelli definiti in
`src/vision_caption/infrastructure/settings.py`. `AppSettings.from_env()` legge
le variabili d'ambiente una sola volta all'avvio e distribuisce le sezioni
tipizzate ai componenti.

`.env.example` contiene l'elenco completo, organizzato nelle sezioni:

- server e runtime;
- OpenRouter;
- AUTO/SSIM/RF-DETR;
- POINTING/MediaPipe;
- gesture e temporizzazione;
- cono/corridoio;
- salvataggio debug delle tre immagini POINTING;
- VLM POINTING;
- TTS.

Valori principali:

- `SERVER_HOST` / `SERVER_PORT` — binding del server WebSocket;
- `SSIM_THRESHOLD` — soglia SSIM per il cambio scena;
- `RFDETR_THRESHOLD` / `RFDETR_CUSTOM_THRESHOLD` — confidence delle detection;
- `SUPPRESS_UNCHANGED_CLASS_COUNTS` — abilita il filtro semantico corrente;
- `MIN_CAPTION_INTERVAL_SECONDS` — intervallo minimo fra caption AUTO;
- `CAPTION_SIMILARITY_THRESHOLD` — deduplicazione testuale;
- `MAX_FRAME_AGE_S` / `VLM_TIMEOUT_S` — freshness e timeout AUTO;
- `VLM_MODEL` — modello OpenRouter condiviso.

### Configurazione POINTING

La modalità POINTING usa il modello MediaPipe
`models/hand_tracking/hand_landmarker.task`. Il percorso può essere cambiato
con `HAND_LANDMARKER_MODEL_PATH`.

MediaPipe è inizializzato in modo lazy: una connessione che usa soltanto AUTO
non carica il modello. Tracker, cooldown, timestamp VIDEO e landmarker sono
creati per singola connessione WebSocket e vengono chiusi alla disconnessione.

Variabili principali:

- `HAND_INFERENCE_MAX_SIDE` — lato massimo del frame passato a MediaPipe;
- `HAND_MIN_DETECTION_CONFIDENCE` — soglia di rilevamento;
- `HAND_MIN_PRESENCE_CONFIDENCE` — soglia di presenza;
- `HAND_MIN_TRACKING_CONFIDENCE` — soglia di tracking;
- `POINTING_EVENT_COOLDOWN_SECONDS` — intervallo minimo fra due eventi;
- `POINTING_CONFIRMATION_SECONDS` — stabilità richiesta prima dell'attivazione;
- `POINTING_RAY_EMA_ALPHA` — smoothing del raggio;
- `POINTING_CORRIDOR_*` — geometria e stile del cono;
- `POINTING_VLM_TIMEOUT_SECONDS` — timeout della richiesta VLM dedicata;
- `POINTING_VLM_MAX_OUTPUT_TOKENS` — limite della risposta JSON.

Per acquisire materiale diagnostico o figure per la tesi è possibile abilitare:

```env
POINTING_DEBUG_SAVE_IMAGES=true
POINTING_DEBUG_OUTPUT_DIR=artifacts/pointing_debug
```

Per ogni gesture confermata, prima della richiesta OpenRouter, viene creata una
cartella contenente gli stessi tre JPEG inseriti nel payload VLM:

1. `01_context_with_corridor.jpg` — scena completa con cono;
2. `02_focus_darkened_and_cropped.jpg` — area esterna oscurata e crop;
3. `03_clean_original.jpg` — frame originale, usato anche per OCR.

Il flag è disattivato di default. La cartella predefinita è ignorata da Git
perché le acquisizioni possono contenere persone o informazioni sensibili.

### Messaggi WebSocket in uscita

Il server invia tre tipi JSON sullo stesso endpoint `/ws/vision`:

- `audio`;
- `detections`;
- `pointing_overlay`.

`pointing_overlay` contiene coordinate normalizzate, stato
`CANDIDATE`/`ACTIVE`, progresso di conferma e stile del corridoio. Il contratto
frontend completo è in `Docs/handoff_frontend_pointing_overlay.md`.

---

## Deploy — Cluster HPC (PurpleJeans)

```bash
sbatch deploy/slurm_job.sh
```

```bash
# Oppure Docker
docker compose -f deploy/docker-compose.yml up
```
