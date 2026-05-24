# vision-caption — Briefing Iniziale

## Contesto

Sto sviluppando il progetto di tesi magistrale "vision-caption" — un server WebSocket
per audio-descrizione ambientale in tempo reale destinato a utenti non vedenti / ipovedenti
con visore Meta Quest 3.

Il server riceve frame JPEG via WebSocket, rileva cambi di scena, genera una descrizione
testuale in italiano tramite un VLM (Gemma 4 via Ollama), sintetizza la voce con Chatterbox
TTS, e rimanda l'audio WAV/Opus al client.

---

## Cosa devi fare

Crea la struttura del progetto con:
- tutte le cartelle
- tutti i file Python con SOLO docstring e `raise NotImplementedError` (niente logica)
- `pyproject.toml` completo con le dipendenze
- `config.yaml` con valori di default commentati
- `README.md` (contenuto nel file README.md di questa cartella)
- `plan.md` (contenuto nel file plan.md di questa cartella)

**IMPORTANTE: Non scrivere nessuna logica di implementazione.**
Ogni funzione/metodo deve avere solo la firma, il docstring che descrive cosa fa,
e `raise NotImplementedError`. Il codice lo scrivo io seguendo il plan.md.

---

## Architettura

Il progetto usa **Hexagonal Architecture** (Ports & Adapters) in un singolo package
Python standalone. Non c'è nessuna libreria condivisa esterna.

```
┌─────────────────────────────────────────────────┐
│  infrastructure  (FastAPI, DI container, config) │
│  ┌───────────────────────────────────────────┐   │
│  │  adapters  (OpenCV, Ollama, Chatterbox)   │   │
│  │  ┌─────────────────────────────────────┐  │   │
│  │  │  core  (domain, ports, services)    │  │   │
│  │  └─────────────────────────────────────┘  │   │
│  └───────────────────────────────────────────┘   │
└─────────────────────────────────────────────────┘
```

Regola fondamentale: `core/` non importa MAI librerie esterne (solo stdlib e Pydantic
per i domain model).

---

## Tecnologie

| Componente | Tecnologia |
|---|---|
| Package manager | uv |
| Web server | FastAPI + uvicorn |
| Scene change (base) | scikit-image (SSIM) |
| Scene change (avanzato) | RF-DETR (`rfdetr` package) |
| VLM captioning | Ollama REST API (Gemma 4) |
| TTS | Chatterbox TTS |
| Frame processing | OpenCV (headless) |
| Config | Pydantic Settings v2 + YAML |
| Logging | structlog |
| Testing | pytest + pytest-asyncio |
| Linting | ruff |

---

## Struttura cartelle

```
vision-caption/
├── src/
│   └── vision_caption/
│       ├── core/
│       │   ├── domain/
│       │   │   ├── __init__.py
│       │   │   ├── frame.py          # FrameData, FrameMetadata, CaptureMode
│       │   │   ├── caption.py        # Caption, CaptionRequest
│       │   │   └── audio.py          # AudioResult, AudioFormat
│       │   ├── ports/
│       │   │   ├── __init__.py
│       │   │   ├── scene_detector.py    # SceneDetectorPort (Protocol)
│       │   │   ├── caption_generator.py # CaptionGeneratorPort (Protocol)
│       │   │   └── speech_synthesizer.py # SpeechSynthesizerPort (Protocol)
│       │   └── services/
│       │       ├── __init__.py
│       │       ├── caption_pipeline.py  # CaptionPipeline — orchestratore
│       │       └── rate_limiter.py      # RateLimiter
│       ├── adapters/
│       │   ├── __init__.py
│       │   ├── scene/
│       │   │   ├── __init__.py
│       │   │   └── ssim_detector.py     # SSIMSceneDetector
│       │   ├── vlm/
│       │   │   ├── __init__.py
│       │   │   └── ollama_caption.py    # OllamaCaptionGenerator
│       │   └── tts/
│       │       ├── __init__.py
│       │       └── chatterbox_synth.py  # ChatterboxSynthesizer
│       ├── infrastructure/
│       │   ├── __init__.py
│       │   ├── settings.py              # AppSettings
│       │   ├── container.py             # ApplicationContainer (DI)
│       │   └── server/
│       │       ├── __init__.py
│       │       ├── app.py               # FastAPI factory
│       │       └── ws_handler.py        # WebSocket handler
│       ├── __init__.py
│       └── __main__.py
├── tests/
│   ├── unit/
│   │   ├── test_caption_pipeline.py
│   │   ├── test_rate_limiter.py
│   │   └── test_ssim_detector.py
│   └── integration/
│       └── test_ws_e2e.py
├── scripts/
│   ├── test_client_webcam.py
│   └── benchmark_latency.py
├── config.yaml
├── pyproject.toml
├── README.md
└── plan.md
```
