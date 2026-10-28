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

## Avvio con Docker

È la via più breve, e l'unica che non chiede di installare PyTorch a mano.

```bash
cp .env.example .env          # poi si scelgono i due provider, vedi sotto
docker compose up -d          # client su http://localhost:8080
```

Il client va aperto su `http://localhost` o dietro HTTPS: il browser apre la
fotocamera soltanto in contesto sicuro, e un indirizzo IP in chiaro sulla rete
locale non lo è. Per usarlo dal telefono serve un tunnel (vedi in fondo).

**Con GPU NVIDIA** — la workstation, o WSL2 su Windows con i driver NVIDIA
installati lato Windows e `nvidia-container-toolkit` attivo:

```bash
echo 'COMPOSE_FILE=compose.yaml:compose.gpu.yaml' >> .env
docker compose up -d
```

`compose.gpu.yaml` prenota le schede. Con più di una, `SERVER_GPUS=0` lascia la
seconda ai servizi locali: RF-DETR ne usa una sola.

**Con GPU AMD** — l'immagine va ricostruita con le ruote ROCm, che l'immagine
pubblicata non contiene:

```bash
TORCH_VARIANT=rocm7.2 docker compose build server
```

**Senza GPU** — `TORCH_VARIANT=cpu`, senza `compose.gpu.yaml`. Funziona, ma
RF-DETR su processore è molto più lento dei 23 ms misurati su GPU.

Il checkpoint RF-DETR adattato non sta nell'immagine: va messo in `./models`,
che il compose monta in sola lettura.

### Immagini pubblicate

| Immagine | Contenuto |
|---|---|
| `thenemesis47/visioncaption-server` | server, PyTorch per NVIDIA (`cu128`) |
| `thenemesis47/visioncaption-server:latest-cpu` | server, PyTorch per processore |
| `thenemesis47/visioncaption-client` | build del client servita da nginx |

---

## Dove girano i modelli: cloud o in casa

Due modelli costano: quello che guarda le immagini e quello che parla. Ognuno
può stare su un servizio esterno o sulla macchina, e la scelta è una riga.

| | Cloud | In casa |
|---|---|---|
| **Modello visivo** | `VLM_PROVIDER=openrouter` + `OPENROUTER_API_KEY` | `VLM_PROVIDER=local` + Ollama |
| **Voce** | `TTS_PROVIDER=elevenlabs` + `ELEVENLABS_API_KEY` | `TTS_PROVIDER=local` + Chatterbox, oppure `TTS_PROVIDER=fish` + Fish Speech |

Lasciandoli su `auto` decide la presenza della chiave: c'è, si va nel cloud;
non c'è, si va in locale. Dichiarare il provider serve a sbagliare
rumorosamente — chi scrive `openrouter` e dimentica la chiave riceve un errore
all'avvio invece di ritrovarsi su un modello diverso da quello che crede.

I servizi locali si accendono con i profili di compose:

```bash
# Modello visivo in casa: alza Ollama e scarica il modello una volta sola
docker compose --profile local-vlm up -d
docker compose --profile local-vlm run --rm ollama-pull

# Voce in casa: Chatterbox, che va clonato accanto a questo repo
git clone https://github.com/travisvn/chatterbox-tts-api ../chatterbox-tts-api
docker compose --profile local-tts up -d

# Voce in casa con Fish Speech (OpenAudio S1-mini, licenza non commerciale).
# Il modello è ad accesso controllato: accettare le condizioni su
# huggingface.co/fishaudio/openaudio-s1-mini e mettere HF_TOKEN nel .env.
docker compose --profile local-tts-fish run --rm fish-download
docker compose --profile local-tts-fish up -d

# Tutto in casa, niente rete
docker compose --profile local-vlm --profile local-tts up -d
```

Il modello locale deve saper leggere le immagini: `gemma3:4b` è il valore
predefinito, un modello solo testuale non descriverebbe nulla. L'adapter parla
l'API `chat/completions` di OpenAI, quindi va bene qualunque server che la
implementi, non solo Ollama.

---

## Requisiti senza Docker

- Python 3.14 e [uv](https://docs.astral.sh/uv/)
- Una GPU per RF-DETR (NVIDIA con CUDA, oppure AMD con ROCm); funziona anche
  su processore, più lentamente
- Il modello dei landmark della mano di MediaPipe in
  `models/hand_tracking/hand_landmarker.task`

```bash
uv sync
cp .env.example .env
./run_server.sh
```

`uv sync` installa PyTorch nella variante ROCm, che è quella della macchina su
cui il progetto è nato. Su NVIDIA va sostituito:

```bash
uv pip install torch torchvision --index-url https://download.pytorch.org/whl/cu128
```

---

## Test

```bash
uv run pytest -q                 # prove unitarie, senza GPU né rete
USE_MOCKS=true uv run python -m vision_caption
uv run python scripts/benchmark_pipeline.py --help
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
- provider del modello visivo (OpenRouter o locale);
- AUTO/SSIM/RF-DETR;
- POINTING/MediaPipe;
- gesture e temporizzazione;
- cono/corridoio;
- salvataggio debug delle tre immagini POINTING;
- VLM POINTING;
- TTS.

Valori principali:

- `SERVER_HOST` / `SERVER_PORT` — binding del server WebSocket;
- `FRONTEND_DIST_PATH` — build Vite servita da FastAPI;
- `SSIM_THRESHOLD` — soglia SSIM per il cambio scena;
- `RFDETR_THRESHOLD` / `RFDETR_CUSTOM_THRESHOLD` — confidence delle detection;
- `SUPPRESS_UNCHANGED_CLASS_COUNTS` — abilita il filtro semantico corrente;
- `MIN_CAPTION_INTERVAL_SECONDS` — intervallo minimo fra caption AUTO;
- `CAPTION_SIMILARITY_THRESHOLD` — deduplicazione testuale;
- `MAX_FRAME_AGE_S` / `VLM_TIMEOUT_S` — freshness e timeout AUTO;
- `VLM_PROVIDER` / `TTS_PROVIDER` — cloud o locale;
- `VLM_BASE_URL` / `VLM_MODEL` — endpoint e modello visivo condiviso.

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

### Log di ricerca

Ogni connessione WebSocket scrive un file `logs/research/<data>_<sessione>.jsonl`,
separato dal log tecnico, con un evento JSON per riga. Ogni riga ha
`schema_version`, `session_id`, `seq`, `ts` (UTC), `t` (secondi dall'inizio
della sessione) ed `event`.

| Evento | Cosa registra |
|---|---|
| `session_start` | partecipante e compito (`/ws/vision?pid=P07&task=T2`), user agent, commit, tutta la configurazione senza chiavi |
| `mode_change` | passaggio fra AUTO e POINTING |
| `auto_frame` | esito della cascata per ogni frame AUTO, tempi, classi rilevate |
| `utterance` | ciò che è stato detto: testo, durata audio, ritardo dal frame all'invio |
| `utterance_skipped` | descrizione AUTO taciuta perché uguale alla precedente |
| `pointing_activation` | gesto confermato, nuovo o spostamento su un altro bersaglio |
| `pointing_blocked` | gesto scartato dall'attesa fra un evento e l'altro |
| `pointing_result` | bersaglio, testo letto, confidenze, richiesta di ripuntare, tempi |
| `frames_dropped` | frame scartati perché il server era indietro |
| `marker` | nota del ricercatore: `curl -X POST .../api/research/marker -H 'Content-Type: application/json' -d '{"label":"inizio compito 2"}'` |
| `error`, `session_end` | errori e riepilogo della connessione |

Non contiene immagini. `RESEARCH_LOG_TEXT=false` toglie anche le parole e
lascia tempi, esiti e lunghezze. `scripts/summarize_research_log.py` ne ricava
una riga per sessione, anche in CSV.

---

## Deploy frontend e Cloudflare Tunnel

Frontend e backend devono essere cartelle sorelle:

```text
Documenti/
├── visionCaption-TESI/
└── TESI-Vision_Caption_Client/
    └── dist/
```

Il deploy è esplicito e non viene eseguito a ogni riavvio:

```bash
./scripts/deploy_frontend.sh
```

Lo script aggiorna `main`, verifica che includa almeno il commit `cac6631`,
esegue `npm ci` e genera `dist/`. In produzione non va definita
`VITE_VISION_WS_URL`: il frontend usa lo stesso host della pagina.

Avvio definitivo:

```bash
./run_server.sh
```

Uvicorn serve frontend, `/health` e `/ws/vision` in HTTP locale su
`127.0.0.1:8765`. Cloudflare Tunnel deve inoltrare l'hostname pubblico
`vision.serverpersonaledomotico95.online` verso `http://127.0.0.1:8765`.
HTTPS e WSS terminano su Cloudflare; il backend non carica certificati TLS.
