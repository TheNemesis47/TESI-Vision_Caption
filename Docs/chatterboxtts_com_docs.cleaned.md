

--- DOCUMENT: https://chatterboxtts.com/docs/ ---
# Chatterbox TTS API
[ ![GitHub stars](https://img.shields.io/github/stars/travisvn/chatterbox-tts-api?style=social)](https://github.com/travisvn/chatterbox-tts-api) [ ![GitHub forks](https://img.shields.io/github/forks/travisvn/chatterbox-tts-api)](https://github.com/travisvn/chatterbox-tts-api) [ ![GitHub issues](https://img.shields.io/github/issues/travisvn/chatterbox-tts-api)](https://github.com/travisvn/chatterbox-tts-api/issues) ![GitHub last commit](https://img.shields.io/github/last-commit/travisvn/chatterbox-tts-api?color=red) [ ![Discord](https://img.shields.io/badge/Discord-Voice_AI_%26_TTS_Tools-blue?logo=discord&logoColor=white) ](http://chatterboxtts.com/discord)
**FastAPI** -powered REST API for [Chatterbox TTS](https://github.com/resemble-ai/chatterbox), providing OpenAI-compatible text-to-speech endpoints with voice cloning capabilities and additional features on top of the `chatterbox-tts` base package.
## Features
🚀 **OpenAI-Compatible API** - Drop-in replacement for OpenAI's TTS API
⚡ **FastAPI Performance** - High-performance async API with automatic documentation
🌍 **Multilingual Support** - Generate speech in 22 languages with language-aware voice cloning
🎨 **React Frontend** - Includes an optional, ready-to-use web interface
🎭 **Voice Cloning** - Use your own voice samples for personalized speech
🎤 **Voice Library Management** - Upload, manage, and use custom voices by name
📝 **Smart Text Processing** - Automatic chunking for long texts
📊 **Real-time Status** - Monitor TTS progress, statistics, and request history
🐳 **Docker Ready** - Full containerization with persistent voice storage
⚙️ **Configurable** - Extensive environment variable configuration
🎛️ **Parameter Control** - Real-time adjustment of speech characteristics
📚 **Auto Documentation** - Interactive API docs at `/docs` and `/redoc`
🔧 **Type Safety** - Full Pydantic validation for requests and responses
🧠 **Memory Management** - Advanced memory monitoring and automatic cleanup
NOTE
_Support for Chatterbox Turbo coming soon_
IMPORTANT
`resemble-ai/chatterbox` is currently broken for non-CUDA setups (see [chatterbox issues](https://github.com/resemble-ai/chatterbox/issues))
Revert to non-multilingual by using the `stable` branch of this repo
[View more instructions](https://chatterboxtts.com/docs#issues-with-multilingual)
## ⚡️ Quick Start

```
git clone https://github.com/travisvn/chatterbox-tts-api
cd chatterbox-tts-api
uv sync
uv run main.py

```

TIP
[uv](https://docs.astral.sh/uv/) installed with `curl -LsSf https://astral.sh/uv/install.sh | sh`
### Local Installation with Python 🐍
#### Option A: Using uv (Recommended - Faster & Better Dependencies)

```
# Clone the repository
git clone https://github.com/travisvn/chatterbox-tts-api
cd chatterbox-tts-api

# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies with uv (automatically creates venv)
uv sync

# Copy and customize environment variables
cp .env.example .env

# Start the API with FastAPI
uv run uvicorn app.main:app --host 0.0.0.0 --port 4123
# Or use the main script
uv run main.py

```

> 💡 **Why uv?** Users report better compatibility with `chatterbox-tts`, 25-40% faster installs, and superior dependency resolution. [See migration guide →](https://github.com/travisvn/chatterbox-tts-api/blob/main/docs/UV_MIGRATION.md)
#### Option B: Using pip (Traditional)

```
# Clone the repository
git clone https://github.com/travisvn/chatterbox-tts-api
cd chatterbox-tts-api

# Setup environment — using Python 3.11
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy and customize environment variables
cp .env.example .env

# Add your voice sample (or use the provided one)
# cp your-voice.mp3 voice-sample.mp3

# Start the API with FastAPI
uvicorn app.main:app --host 0.0.0.0 --port 4123
# Or use the main script
python main.py

```

> Ran into issues? Check the [troubleshooting section](https://github.com/travisvn/chatterbox-tts-api?tab=readme-ov-file#common-issues)
### 🐳 Docker (Recommended)

```
# Clone and start with Docker Compose
git clone https://github.com/travisvn/chatterbox-tts-api
cd chatterbox-tts-api

# Use Docker-optimized environment variables
cp .env.example.docker .env  # Docker-specific paths, ready to use
# Or: cp .env.example .env    # Local development paths, needs customization

# Choose your deployment method:

# API Only (default)
docker compose -f docker/docker-compose.yml up -d             # Standard (pip-based)
docker compose -f docker/docker-compose.uv.yml up -d          # uv-optimized (faster builds)
docker compose -f docker/docker-compose.gpu.yml up -d         # Standard + GPU
docker compose -f docker/docker-compose.uv.gpu.yml up -d      # uv + GPU (recommended for GPU users)
docker compose -f docker/docker-compose.cpu.yml up -d         # CPU-only
docker compose -f docker/docker-compose.blackwell.yml up -d   # Blackwell (50XX) NVIDIA GPUs

# API + Frontend (add --profile frontend to any of the above)
docker compose -f docker/docker-compose.yml --profile frontend up -d             # Standard + Frontend
docker compose -f docker/docker-compose.gpu.yml --profile frontend up -d         # GPU + Frontend
docker compose -f docker/docker-compose.uv.gpu.yml --profile frontend up -d      # uv + GPU + Frontend
docker compose -f docker/docker-compose.blackwell.yml --profile frontend up -d   # (Blackwell) uv + GPU + Frontend

# Watch the logs as it initializes (the first use of TTS takes the longest)
docker logs chatterbox-tts-api -f

# Test the API
curl -X POST http://localhost:4123/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{"input": "Hello from Chatterbox TTS!"}' \
  --output test.wav

```
**🚀 Running with the Web UI (Full Stack)**
This project includes an optional React-based web UI. Use Docker Compose profiles to easily opt in or out of the frontend:
### With Docker Compose Profiles

```
# API only (default behavior)
docker compose -f docker/docker-compose.yml up -d

# API + Frontend + Web UI (with --profile frontend)
docker compose -f docker/docker-compose.yml --profile frontend up -d

# Or use the convenient helper script for fullstack:
python start.py fullstack

# Same pattern works with all deployment variants:
docker compose -f docker/docker-compose.gpu.yml --profile frontend up -d    # GPU + Frontend
docker compose -f docker/docker-compose.uv.yml --profile frontend up -d     # uv + Frontend
docker compose -f docker/docker-compose.cpu.yml --profile frontend up -d    # CPU + Frontend

```

### Local Development
For local development, you can run the API and frontend separately:

```
# Start the API first (follow earlier instructions)
# Then run the frontend:
cd frontend && npm install && npm run dev

```

Click the link provided from Vite to access the web UI.
### Build for Production
Build the frontend for production deployment:

```
cd frontend && npm install && npm run build

```

You can then access it directly from your local file system at `/dist/index.html`.
### Port Configuration
  * **API Only** : Accessible at `http://localhost:4123` (direct API access)
  * **With Frontend** : Web UI at `http://localhost:4321`, API requests routed via proxy


The frontend uses a reverse proxy to route requests, so when running with `--profile frontend`, the web interface will be available at `http://localhost:4321` while the API runs behind the proxy.
## Screenshots of Frontend (Web UI)
![Chatterbox TTS API - Frontend - Dark Mode](https://lm17s1uz51.ufs.sh/f/EsgO8cDHBTOUS62gM9PGyDAvTxnjVKQO0Zz5uI6Jg4UodHEa) ![Chatterbox TTS API - Frontend - Light Mode](https://lm17s1uz51.ufs.sh/f/EsgO8cDHBTOUXYXF1ekWhMaPnZ3rSTRIEkDzvKwGU05qjAol)
![Chatterbox TTS API - Frontend Processing - Dark Mode](https://lm17s1uz51.ufs.sh/f/EsgO8cDHBTOUt4kJ0goXPb09QmDchfSoNxgB3KLETFyvnsU5) ![Chatterbox TTS API - Frontend Processing - Light Mode](https://lm17s1uz51.ufs.sh/f/EsgO8cDHBTOU0v7EUEwi1efdOvQm6TrWKoPuX7xEl4pc8RVw)
> 🖼️ View screenshot of full frontend web UI — [light mode](https://lm17s1uz51.ufs.sh/f/EsgO8cDHBTOUoONOy6UZv2m8CUjqGrBbDy4aXzNV9Rl1ZAgQ) / [dark mode](https://lm17s1uz51.ufs.sh/f/EsgO8cDHBTOU7RmQRTFVcR8ntzKQs0IxJ6ibFrq2hjCSadUG)
## API Usage
### Basic Text-to-Speech (Default Voice)
This endpoint works for both the API-only and full-stack setups.

```
curl -X POST http://localhost:4123/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{"input": "Your text here"}' \
  --output speech.wav

```

### Using Custom Parameters (JSON)

```
curl -X POST http://localhost:4123/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{"input": "Dramatic speech!", "exaggeration": 1.2, "cfg_weight": 0.3, "temperature": 0.9}' \
  --output dramatic.wav

```

### Custom Voice Upload
Upload your own voice sample for personalized speech:

```
curl -X POST http://localhost:4123/v1/audio/speech/upload \
  -F "input=Hello with my custom voice!" \
  -F "exaggeration=0.8" \
  -F "voice_file=@my_voice.mp3" \
  --output custom_voice_speech.wav

```

### With Custom Parameters and Voice Upload

```
curl -X POST http://localhost:4123/v1/audio/speech/upload \
  -F "input=Dramatic speech!" \
  -F "exaggeration=1.2" \
  -F "cfg_weight=0.3" \
  -F "temperature=0.9" \
  -F "voice_file=@dramatic_voice.wav" \
  --output dramatic.wav

```

### Voice Library Management
Store and manage custom voices by name for reuse across requests:

```
# Upload a voice to the library
curl -X POST http://localhost:4123/voices \
  -F "voice_file=@my_voice.wav" \
  -F "voice_name=my-custom-voice"

# Upload a voice with language (multilingual support)
curl -X POST http://localhost:4123/voices \
  -F "voice_file=@french_voice.wav" \
  -F "voice_name=french-speaker" \
  -F "language=fr"

# Use the voice by name in speech generation
curl -X POST http://localhost:4123/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{"input": "Hello with my custom voice!", "voice": "my-custom-voice"}' \
  --output custom_voice_output.wav

# Generate French speech (language auto-detected from voice)
curl -X POST http://localhost:4123/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{"input": "Bonjour, comment allez-vous?", "voice": "french-speaker"}' \
  --output french_speech.wav

# List all available voices (includes language metadata)
curl http://localhost:4123/voices

# Get supported languages
curl http://localhost:4123/languages

```

**🔧[Complete Voice Library Documentation →](https://github.com/travisvn/chatterbox-tts-api/blob/main/docs/VOICE_LIBRARY_MANAGEMENT.md)**
## 🌍 Multilingual Support
Generate speech in **22 languages** with language-aware voice cloning and automatic language detection.
### Supported Languages
Arabic (ar) • Danish (da) • German (de) • Greek (el) • **English (en)** • Spanish (es) • Finnish (fi) • French (fr) • Hebrew (he) • Hindi (hi) • Italian (it) • Japanese (ja) • Korean (ko) • Malay (ms) • Dutch (nl) • Norwegian (no) • Polish (pl) • Portuguese (pt) • Russian (ru) • Swedish (sv) • Swahili (sw) • Turkish (tr)
### Quick Start

```
# Get supported languages
curl http://localhost:4123/languages

# Upload voice with language
curl -X POST http://localhost:4123/voices \
  -F "voice_name=spanish_speaker" \
  -F "language=es" \
  -F "voice_file=@spanish_voice.wav"

# Generate multilingual speech
curl -X POST http://localhost:4123/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{"input": "¡Hola! ¿Cómo estás hoy?", "voice": "spanish_speaker"}' \
  --output spanish_speech.wav

```

### Key Features
  * 🎯 **Language Auto-Detection** - Voices store language metadata, automatically used in generation
  * 🌐 **No API Changes** - Maintains OpenAI compatibility, language determined from voice metadata
  * 🔄 **Configurable** - Enable/disable with `USE_MULTILINGUAL_MODEL` environment variable
  * 📚 **Voice Library Integration** - Language badges and filtering in web UI
  * 🧠 **Smart Fallback** - Defaults to English for backward compatibility


**📚[Complete Multilingual Documentation →](https://github.com/travisvn/chatterbox-tts-api/blob/main/docs/MULTILINGUAL.md)**
## 🎵 Real-time Audio Streaming
The API supports multiple streaming formats for lower latency and better user experience:
  * **Raw Audio Streaming** : Traditional audio chunks (WAV format)
  * **Server-Side Events (SSE)** : OpenAI-compatible format with base64-encoded audio chunks


### Quick Start

```
# Basic audio streaming
curl -X POST http://localhost:4123/v1/audio/speech/stream \
  -H "Content-Type: application/json" \
  -d '{"input": "This streams in real-time!"}' \
  --output streaming.wav

# SSE streaming (OpenAI compatible)
curl -X POST http://localhost:4123/v1/audio/speech \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -d '{"input": "This streams as Server-Side Events!", "stream_format": "sse"}' \
  --no-buffer

# Real-time playback
curl -X POST http://localhost:4123/v1/audio/speech/stream \
  -H "Content-Type: application/json" \
  -d '{"input": "Play as it generates!"}' \
  | ffplay -f wav -i pipe:0 -autoexit -nodisp

```

### 🚀 **[Complete Streaming Documentation →](https://github.com/travisvn/chatterbox-tts-api/blob/main/docs/STREAMING_API.md)**
For comprehensive streaming features including:
  * **Advanced chunking strategies** (sentence, paragraph, word, fixed)
  * **Quality presets** (fast, balanced, high)
  * **Configurable parameters** and performance tuning
  * **Real-time progress monitoring**
  * **Python, JavaScript, and cURL examples**
  * **Integration patterns** for different use cases


**Key Benefits:**
  * ⚡ **Lower latency** - Start hearing audio in 1-2 seconds
  * 🎯 **Better UX** - No waiting for complete generation
  * 💾 **Memory efficient** - Process chunks individually
  * 🎛️ **Configurable** - Choose speed vs quality trade-offs

**🐍 Python Examples**
### Default Voice (JSON)

```
import requests

response = requests.post(
    "http://localhost:4123/v1/audio/speech",
    json={
        "input": "Hello world!",
        "exaggeration": 0.8
    }
)

with open("output.wav", "wb") as f:
    f.write(response.content)

```

### Upload Voice with Language (Multilingual)

```
import requests

# Upload a multilingual voice
with open("german_voice.wav", "rb") as voice_file:
    response = requests.post(
        "http://localhost:4123/voices",
        data={
            "voice_name": "german_speaker",
            "language": "de"
        },
        files={
            "voice_file": ("german_voice.wav", voice_file, "audio/wav")
        }
    )

print(f"Upload status: {response.status_code}")

# Generate German speech
response = requests.post(
    "http://localhost:4123/v1/audio/speech",
    json={
        "input": "Guten Tag! Wie geht es Ihnen?",
        "voice": "german_speaker",
        "exaggeration": 0.8
    }
)

with open("german_output.wav", "wb") as f:
    f.write(response.content)

```

### Upload Endpoint (Default Voice)

```
import requests

response = requests.post(
    "http://localhost:4123/v1/audio/speech/upload",
    data={
        "input": "Hello world!",
        "exaggeration": 0.8
    }
)

with open("output.wav", "wb") as f:
    f.write(response.content)

```

### Custom Voice Upload

```
import requests

with open("my_voice.mp3", "rb") as voice_file:
    response = requests.post(
        "http://localhost:4123/v1/audio/speech/upload",
        data={
            "input": "Hello with my custom voice!",
            "exaggeration": 0.8,
            "temperature": 1.0
        },
        files={
            "voice_file": ("my_voice.mp3", voice_file, "audio/mpeg")
        }
    )

with open("custom_output.wav", "wb") as f:
    f.write(response.content)

```

### Basic Streaming Example

```
import requests

# Stream audio generation in real-time
response = requests.post(
    "http://localhost:4123/v1/audio/speech/stream",
    json={
        "input": "This will stream as it's generated!",
        "exaggeration": 0.8
    },
    stream=True  # Enable streaming mode
)

with open("streaming_output.wav", "wb") as f:
    for chunk in response.iter_content(chunk_size=8192):
        if chunk:
            f.write(chunk)
            print(f"Received chunk: {len(chunk)} bytes")

```

### SSE Streaming Example (OpenAI Compatible)

```
import requests
import json
import base64

# Stream audio using Server-Side Events format
response = requests.post(
    "http://localhost:4123/v1/audio/speech",
    json={
        "input": "This streams as Server-Side Events!",
        "stream_format": "sse",
        "exaggeration": 0.8
    },
    stream=True,
    headers={'Accept': 'text/event-stream'}
)

audio_chunks = []

for line in response.iter_lines(decode_unicode=True):
    if line.startswith('data: '):
        event_data = line[6:]  # Remove 'data: ' prefix

        try:
            event = json.loads(event_data)

            if event.get('type') == 'speech.audio.delta':
                # Decode base64 audio chunk
                audio_data = base64.b64decode(event['audio'])
                audio_chunks.append(audio_data)
                print(f"Received audio chunk: {len(audio_data)} bytes")

            elif event.get('type') == 'speech.audio.done':
                usage = event.get('usage', {})
                print(f"Complete! Tokens: {usage.get('total_tokens', 0)}")
                break
        except:
            continue

print(f"Received {len(audio_chunks)} audio chunks")

```

**📚[Complete Streaming Examples & Documentation →](https://github.com/travisvn/chatterbox-tts-api/blob/main/docs/STREAMING_API.md)**
Including real-time playback, progress monitoring, custom voice uploads, and advanced integration patterns.
### Voice File Requirements
**Supported Formats:**
  * MP3 (.mp3)
  * WAV (.wav)
  * FLAC (.flac)
  * M4A (.m4a)
  * OGG (.ogg)


**Requirements:**
  * Maximum file size: 10MB
  * Recommended duration: 10-30 seconds of clear speech
  * Avoid background noise for best results
  * Higher quality audio produces better voice cloning


## 🎛️ Configuration
The project provides two environment example files:
  * **`.env.example`**- For local development (uses`./models` , `./voice-sample.mp3`)
  * **`.env.example.docker`**- For Docker deployment (uses`/cache` , `/app/voice-sample.mp3`)


Choose the appropriate one for your setup:

```
# For local development
cp .env.example .env

# For Docker deployment
cp .env.example.docker .env

```

Key environment variables (see the example files for full list):
| Variable  | Default  | Description  |
| --- | --- | --- |
| `PORT`  | `4123`  | API server port  |
| `USE_MULTILINGUAL_MODEL`  | `true`  | Enable 23-language support  |
| `EXAGGERATION`  | `0.5`  | Emotion intensity (0.25-2.0)  |
| `CFG_WEIGHT`  | `0.5`  | Pace control (0.0-1.0)  |
| `TEMPERATURE`  | `0.8`  | Sampling randomness (0.05-5.0)  |
| `VOICE_SAMPLE_PATH`  | `./voice-sample.mp3`  | Voice sample for cloning  |
| `DEVICE`  | `auto`  | Device (auto/cuda/mps/cpu)  |
**🎭 Voice Cloning**
Replace the default voice sample:

```
# Replace the default voice sample
cp your-voice.mp3 voice-sample.mp3

# Or set a custom path
echo "VOICE_SAMPLE_PATH=/path/to/your/voice.mp3" >> .env

```

For best results:
  * Use 10-30 seconds of clear speech
  * Avoid background noise
  * Prefer WAV or high-quality MP3


**🐳 Docker Deployment**
### Development

```
docker compose -f docker/docker-compose.yml up

```

### Production

```
# Create production environment
cp .env.example.docker .env
nano .env  # Set production values

# Deploy
docker compose -f docker/docker-compose.yml up -d

```

### With GPU Support

```
# Use GPU-enabled compose file
# Ensure NVIDIA Container Toolkit is installed
docker compose -f docker/docker-compose.gpu.yml up -d

```

**📚 API Reference**
## API Endpoints
| Endpoint  | Method  | Description  |
| --- | --- | --- |
| `/audio/speech`  | POST  | Generate speech from text (complete)  |
| `/audio/speech/upload`  | POST  | Generate speech with voice upload  |
| `/audio/speech/stream`  | POST  |  **Stream** speech generation ([docs](https://github.com/travisvn/chatterbox-tts-api/blob/main/docs/STREAMING_API.md))  |
| `/audio/speech/stream/upload`  | POST  |  **Stream** speech with voice upload ([docs](https://github.com/travisvn/chatterbox-tts-api/blob/main/docs/STREAMING_API.md))  |
| `/voices`  | GET  | List voices in library (with language metadata)  |
| `/voices`  | POST  | Upload voice to library (with language support)  |
| `/languages`  | GET  |  **Get supported languages** ([docs](https://github.com/travisvn/chatterbox-tts-api/blob/main/docs/MULTILINGUAL.md))  |
| `/health`  | GET  | Health check and status  |
| `/config`  | GET  | Current configuration  |
| `/v1/models`  | GET  | Available models (OpenAI compat)  |
| `/status`  | GET  | TTS processing status & progress  |
| `/status/progress`  | GET  | Real-time progress (lightweight)  |
| `/status/statistics`  | GET  | Processing statistics  |
| `/status/history`  | GET  | Recent request history  |
| `/info`  | GET  | Complete API information  |
| `/docs`  | GET  | Interactive API documentation  |
| `/redoc`  | GET  | Alternative API documentation  |
## Parameters Reference
### Speech Generation Parameters
**Exaggeration (0.25-2.0)**
  * `0.3-0.4`: Professional, neutral
  * `0.5`: Default balanced
  * `0.7-0.8`: More expressive
  * `1.0+`: Very dramatic


**CFG Weight (0.0-1.0)**
  * `0.2-0.3`: Faster speech
  * `0.5`: Default pace
  * `0.7-0.8`: Slower, deliberate


**Temperature (0.05-5.0)**
  * `0.4-0.6`: More consistent
  * `0.8`: Default balance
  * `1.0+`: More creative/random


**Stream Format**
  * `audio`: Raw audio streaming (default)
  * `sse`: Server-Side Events with base64-encoded audio chunks (OpenAI compatible)


**🧠 Memory Management**
The API includes advanced memory management to prevent memory leaks and optimize performance:
### Memory Management Features
  * **Automatic Cleanup** : Periodic garbage collection and tensor cleanup
  * **CUDA Memory Management** : Automatic GPU cache clearing
  * **Memory Monitoring** : Real-time memory usage tracking
  * **Manual Controls** : API endpoints for manual cleanup operations


### Memory Configuration
| Variable  | Default  | Description  |
| --- | --- | --- |
| `MEMORY_CLEANUP_INTERVAL`  | `5`  | Cleanup memory every N requests  |
| `CUDA_CACHE_CLEAR_INTERVAL`  | `3`  | Clear CUDA cache every N requests  |
| `ENABLE_MEMORY_MONITORING`  | `true`  | Enable detailed memory logging  |
### Memory Monitoring Endpoints

```
# Get memory status
curl http://localhost:4123/memory

# Trigger manual cleanup
curl "http://localhost:4123/memory?cleanup=true&force_cuda_clear=true"

# Reset memory tracking (with confirmation)
curl -X POST "http://localhost:4123/memory/reset?confirm=true"

```

### Real-time Status Tracking
Monitor TTS processing in real-time:

```
# Check current processing status
curl "http://localhost:4123/v1/status/progress"

# Get detailed status with memory and stats
curl "http://localhost:4123/v1/status?include_memory=true&include_stats=true"

# View processing statistics
curl "http://localhost:4123/v1/status/statistics"

# Check request history
curl "http://localhost:4123/v1/status/history?limit=5"

# Get comprehensive API information
curl "http://localhost:4123/info"

```

**Status Response Example:**

```
{
  "is_processing": true,
  "status": "generating_audio",
  "current_step": "Generating audio for chunk 2/4",
  "current_chunk": 2,
  "total_chunks": 4,
  "progress_percentage": 50.0,
  "duration_seconds": 2.5,
  "text_preview": "Your text being processed..."
}

```

See [Status API Documentation](https://github.com/travisvn/chatterbox-tts-api/blob/main/docs/STATUS_API.md) for complete details.
### Memory Testing
Run the memory management test suite:

```
# Test memory patterns and cleanup
python tests/test_memory.py  # or: uv run tests/test_memory.py

# Monitor memory during testing
watch -n 1 'curl -s http://localhost:4123/memory | jq .memory_info'

```

### Memory Optimization Tips
**For High-Volume Production:**

```
MEMORY_CLEANUP_INTERVAL=3
CUDA_CACHE_CLEAR_INTERVAL=2
ENABLE_MEMORY_MONITORING=false  # Reduce logging overhead
MAX_CHUNK_LENGTH=200             # Smaller chunks for less memory usage

```

**For Development/Debugging:**

```
MEMORY_CLEANUP_INTERVAL=1
CUDA_CACHE_CLEAR_INTERVAL=1
ENABLE_MEMORY_MONITORING=true

```

**Memory Leak Prevention:**
  * Tensors are automatically moved to CPU before deletion
  * Gradient tracking is disabled during inference
  * Audio chunks are cleaned up after concatenation
  * CUDA cache is periodically cleared
  * Python garbage collection is triggered regularly


**🧪 Testing**
Run the test script to verify the API functionality:

```
python tests/test_api.py

```

The test script will:
  * Test health check endpoint
  * Test models endpoint
  * Test API documentation endpoints (new!)
  * Generate speech for various text lengths
  * Test custom parameter validation
  * Test error handling with validation
  * Save generated audio files as `test_output_*.wav`


**⚡ Performance**
**FastAPI Benefits:**
  * **Async support** : Better concurrent request handling
  * **Faster serialization** : JSON responses ~25% faster than Flask
  * **Type validation** : Pydantic models prevent invalid requests
  * **Auto documentation** : No manual API doc maintenance


**Hardware Recommendations:**
  * **CPU** : Works but slower, reduce chunk size for better memory usage
  * **GPU** : Recommended for production, significantly faster
  * **Memory** : 4GB minimum, 8GB+ recommended
  * **Concurrency** : Async support allows better multi-request handling


**🔧 Troubleshooting**
### Common Issues
**CUDA/CPU Compatibility Error**

```
RuntimeError: Attempting to deserialize object on a CUDA device but torch.cuda.is_available() is False

```

This happens because `chatterbox-tts` models require PyTorch with CUDA support, even when running on CPU. Solutions:

```
# Option 1: Use default setup (now includes CUDA-enabled PyTorch)
docker compose -f docker/docker-compose.yml up -d

# Option 2: Use explicit CUDA setup (traditional)
docker compose -f docker/docker-compose.gpu.yml up -d

# Option 3: Use uv + GPU setup (recommended for GPU users)
docker compose -f docker/docker-compose.uv.gpu.yml up -d

# Option 4: Use CPU-only setup (may have compatibility issues)
docker compose -f docker/docker-compose.cpu.yml up -d

# Option 5: Clear model cache and retry with CUDA-enabled setup
docker volume rm chatterbox-tts-api_chatterbox-models
docker compose -f docker/docker-compose.yml up -d --build

# Option 6: Try uv for better dependency resolution
uv sync
uv run uvicorn app.main:app --host 0.0.0.0 --port 4123

```

**For local development** , install PyTorch with CUDA support:

```
# With pip
pip uninstall torch torchvision torchaudio
pip install torch==2.6.0 torchvision==0.21.0 torchaudio==2.6.0 --index-url https://download.pytorch.org/whl/cu124
pip install git+https://github.com/travisvn/chatterbox-multilingual.git@exp

# With uv (handles this automatically)
uv sync

```

**Windows Users** , using pip & having issues:

```
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121 --force-reinstall
pip install --force-reinstall typing_extensions

```

**Port conflicts**

```
# Change port
echo "PORT=4124" >> .env

```

**GPU not detected**

```
# Force CPU mode
echo "DEVICE=cpu" >> .env

```

**Out of memory**

```
# Reduce chunk size
echo "MAX_CHUNK_LENGTH=200" >> .env

```

**Model download fails**

```
# Clear cache and retry
rm -rf models/
uvicorn app.main:app --host 0.0.0.0 --port 4123  # or: uv run main.py

```

**FastAPI startup issues**

```
# Check if uvicorn is installed
uvicorn --version

# Run with verbose logging
uvicorn app.main:app --host 0.0.0.0 --port 4123 --log-level debug

# Alternative startup method
python main.py

```

**💻 Development**
### Project Structure
This project follows a clean, modular architecture for maintainability:

```
app/                     # FastAPI backend application
├── __init__.py           # Main package
├── config.py            # Configuration management
├── main.py              # FastAPI application
├── models/              # Pydantic models
│   ├── requests.py      # Request models
│   └── responses.py     # Response models
├── core/                # Core functionality
│   ├── memory.py        # Memory management
│   ├── text_processing.py # Text processing utilities
│   └── tts_model.py     # TTS model management
└── api/                 # API endpoints
    ├── router.py        # Main router
    └── endpoints/       # Individual endpoint modules
        ├── speech.py    # TTS endpoint
        ├── health.py    # Health check
        ├── models.py    # Model listing
        ├── memory.py    # Memory management
        └── config.py    # Configuration

frontend/                # React frontend application
├── src/
├── Dockerfile
├── nginx.conf          # Integrated proxy configuration
└── package.json

docker/                  # Docker files consolidated
├── Dockerfile
├── Dockerfile.uv       # uv-optimized image
├── Dockerfile.gpu      # GPU-enabled image
├── Dockerfile.cpu      # CPU-only image
├── Dockerfile.uv.gpu   # uv + GPU image
├── docker-compose.yml  # Standard deployment
├── docker-compose.uv.yml # uv deployment
├── docker-compose.gpu.yml # GPU deployment
├── docker-compose.uv.gpu.yml # uv + GPU deployment
└── docker-compose.cpu.yml # CPU-only deployment

tests/                   # Test suite
├── test_api.py         # API tests
└── test_memory.py      # Memory tests

main.py                  # Main entry point
start.py                 # Development helper script

```

### Quick Start Scripts

```
# Development mode with auto-reload
python start.py dev

# Production mode
python start.py prod

# Full Stack mode with UI (using Docker)
python start.py fullstack

# Run tests
python start.py test

# View project structure
python start.py info

```

### Local Development

```
# Install in development mode (pip)
pip install -e .

# Or with uv (basic development tools)
uv sync

# Or with test dependencies (for contributors)
uv sync --group test

# Start with auto-reload (FastAPI development)
uvicorn app.main:app --host 0.0.0.0 --port 4123 --reload

# Or use the main script
python main.py

# Or use the development helper
python start.py dev

```

### Testing

```
# Run API tests
python tests/test_api.py  # or: uv run tests/test_api.py

# Run memory tests
python tests/test_memory.py

# Test specific endpoint
curl http://localhost:4123/health

# Check API documentation
curl http://localhost:4123/openapi.json

```

### FastAPI Development Features
  * **Auto-reload** : Use `--reload` flag for development
  * **Interactive docs** : Visit `/docs` for live API testing
  * **Type hints** : Full IDE support with Pydantic models
  * **Validation** : Automatic request/response validation
  * **Modular structure** : Easy to extend and maintain


**🤝 Contributing**
  1. Fork the repository
  2. Create a feature branch
  3. Make your changes
  4. Add tests if applicable
  5. Ensure FastAPI docs are updated
  6. Submit a pull request


## Issues with Multilingual?
Fallback to the LKG (last known good) for the pre-multilingual release

```
git clone --branch stable https://github.com/travisvn/chatterbox-tts-api

```

[View `stable` branch](https://github.com/travisvn/chatterbox-tts-api/tree/stable) to see proper install / troubleshooting documentation
## Support
  * 📖 **Documentation** : See [API Documentation](https://github.com/travisvn/chatterbox-tts-api/blob/main/docs/API_README.md) and [Docker Guide](https://github.com/travisvn/chatterbox-tts-api/blob/main/docs/DOCKER_README.md)
  * 🐛 **Issues** : Report bugs via GitHub issues or on [our Discord](http://chatterboxtts.com/discord)
  * 💬 **Discord** : [Join the Discord for this project](http://chatterboxtts.com/discord)


* * *
## 🔗 Integrations
### Open WebUI
TIP
Customize available voices first by using the frontend at `http://localhost:4321`
To use Chatterbox TTS API with Open WebUI, follow these steps:
  * Open the Admin Panel and go to `Settings` -> `Audio`
  * Set your TTS Settings to match the following:
    * Text-to-Speech Engine: _OpenAI_
    * API Base URL: `http://localhost:4123/v1` # alternatively, try `http://host.docker.internal:4123/v1`
    * API Key: `none`
    * TTS Model: `tts-1` or `tts-1-hd`
    * TTS Voice: _Name of the voice you've cloned_ (can also include aliases, defined in the frontend)
    * Response splitting: `Paragraphs`


![Settings to integrate Chatterbox TTS API with Open WebUI](https://lm17s1uz51.ufs.sh/f/EsgO8cDHBTOUjUe3QjHytHQ0xqn2CishmXgGfeJ4o983TUMO)
### ➡️ View the [Open WebUI docs for installing Chatterbox TTS API](https://docs.openwebui.com/tutorials/text-to-speech/chatterbox-tts-api-integration)
[Star on GitHub](https://github.com/travisvn/chatterbox-tts-api)
© 2026 Chatterbox TTS API
Not affiliated with Resemble AI
[Join our Discord](https://chatterboxtts.com/discord)[View on GitHub](https://github.com/travisvn/chatterbox-tts-api)


--- DOCUMENT: https://chatterboxtts.com/docs/api-readme ---
# Chatterbox TTS FastAPI
This API provides a **FastAPI** -based web service for the Chatterbox TTS text-to-speech system, designed to be compatible with OpenAI's TTS API format.
## Features
  * **OpenAI-compatible API** : Uses similar endpoint structure to OpenAI's text-to-speech API
  * **FastAPI Performance** : High-performance async API with automatic documentation
  * **Type Safety** : Full Pydantic validation for requests and responses
  * **Interactive Documentation** : Automatic Swagger UI and ReDoc generation
  * **Automatic text chunking** : Automatically breaks long text into manageable chunks to handle character limits
  * **Voice cloning** : Uses the pre-specified `voice-sample.mp3` file for voice conditioning
  * **Async Support** : Non-blocking request handling with better concurrency
  * **Error handling** : Comprehensive error handling with appropriate HTTP status codes
  * **Health monitoring** : Health check endpoint for monitoring service status
  * **Environment-based configuration** : Fully configurable via environment variables
  * **Docker support** : Ready for containerized deployment


## Setup
### Prerequisites
  1. Ensure you have the Chatterbox TTS package installed:

```
pip install chatterbox-tts==0.1.2

```

  2. Install FastAPI and other required dependencies:

```
pip install fastapi uvicorn[standard] torchaudio requests python-dotenv

```

  3. Ensure you have a `voice-sample.mp3` file in the project root directory for voice conditioning


### Configuration
Copy the example environment file and customize it:

```
cp .env.example .env
nano .env  # Edit with your preferred settings

```

Key environment variables:
  * `PORT=4123` - API server port
  * `EXAGGERATION=0.5` - Default emotion intensity (0.25-2.0)
  * `CFG_WEIGHT=0.5` - Default pace control (0.0-1.0)
  * `TEMPERATURE=0.8` - Default sampling temperature (0.05-5.0)
  * `VOICE_SAMPLE_PATH=./voice-sample.mp3` - Path to voice sample file
  * `DEVICE=auto` - Device selection (auto/cuda/mps/cpu)


See `.env.example` for all available options.
### Running the API
Start the API server:

```
# Method 1: Direct uvicorn (recommended for development)
uvicorn app.main:app --host 0.0.0.0 --port 4123

# Method 2: Using the main script
python main.py

# Method 3: With auto-reload for development
uvicorn app.main:app --host 0.0.0.0 --port 4123 --reload

```

The server will:
  * Automatically detect the best available device (CUDA, MPS, or CPU)
  * Load the Chatterbox TTS model asynchronously
  * Start the FastAPI server on `http://localhost:4123` (or your configured port)
  * Provide interactive documentation at `/docs` and `/redoc`


### API Documentation
Once running, you can access:
  * **Interactive API Docs (Swagger UI)** : <http://localhost:4123/docs>
  * **Alternative Documentation (ReDoc)** : <http://localhost:4123/redoc>
  * **OpenAPI Schema** : <http://localhost:4123/openapi.json>


## API Endpoints
### 1. Text-to-Speech Generation
**POST** `/v1/audio/speech`
Generate speech from text using the Chatterbox TTS model.
**Request Body (Pydantic Model):**

```
{
  "input": "Text to convert to speech",
  "voice": "alloy", // OpenAI voice name or custom voice library name
  "response_format": "wav", // Ignored - always returns WAV
  "speed": 1.0, // Ignored - use model's built-in parameters
  "exaggeration": 0.7, // Optional - override default (0.25-2.0)
  "cfg_weight": 0.4, // Optional - override default (0.0-1.0)
  "temperature": 0.9 // Optional - override default (0.05-5.0)
}

```

**Validation:**
  * `input`: Required, 1-3000 characters, automatically trimmed
  * `exaggeration`: Optional, 0.25-2.0 range validation
  * `cfg_weight`: Optional, 0.0-1.0 range validation
  * `temperature`: Optional, 0.05-5.0 range validation


**Response:**
  * Content-Type: `audio/wav`
  * Binary audio data in WAV format via StreamingResponse


**Example:**

```
curl -X POST http://localhost:4123/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{"input": "Hello, this is a test of the text to speech system."}' \
  --output speech.wav

```

**With custom parameters:**

```
curl -X POST http://localhost:4123/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{"input": "Dramatic speech!", "exaggeration": 1.2, "cfg_weight": 0.3}' \
  --output dramatic.wav

```

**Using a voice from the voice library:**

```
curl -X POST http://localhost:4123/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{"input": "Hello with custom voice!", "voice": "my-uploaded-voice"}' \
  --output custom_voice.wav

```

> **Note:** See [Voice Library Management Documentation](https://github.com/travisvn/chatterbox-tts-api/blob/main/VOICE_LIBRARY_MANAGEMENT.md) for complete voice management API details.
### 2. Health Check
**GET** `/health`
Check if the API is running and the model is loaded.
**Response (HealthResponse model):**

```
{
  "status": "healthy",
  "model_loaded": true,
  "device": "cuda",
  "config": {
    "max_chunk_length": 280,
    "max_total_length": 3000,
    "voice_sample_path": "./voice-sample.mp3",
    "default_exaggeration": 0.5,
    "default_cfg_weight": 0.5,
    "default_temperature": 0.8
  }
}

```

### 3. List Models
**GET** `/v1/models`
List available models (OpenAI API compatibility).
**Response (ModelsResponse model):**

```
{
  "object": "list",
  "data": [
    {
      "id": "chatterbox-tts-1",
      "object": "model",
      "created": 1677649963,
      "owned_by": "resemble-ai"
    }
  ]
}

```

### 4. Configuration Info
**GET** `/config`
Get current configuration (useful for debugging).
**Response (ConfigResponse model):**

```
{
  "server": {
    "host": "0.0.0.0",
    "port": 4123
  },
  "model": {
    "device": "cuda",
    "voice_sample_path": "./voice-sample.mp3",
    "model_cache_dir": "./models"
  },
  "defaults": {
    "exaggeration": 0.5,
    "cfg_weight": 0.5,
    "temperature": 0.8,
    "max_chunk_length": 280,
    "max_total_length": 3000
  }
}

```

### 5. API Documentation Endpoints
**GET** `/docs` - Interactive Swagger UI documentation
**GET** `/redoc` - Alternative ReDoc documentation
**GET** `/openapi.json` - OpenAPI schema specification
## Text Processing
### Automatic Chunking
The API automatically handles long text inputs by:
  1. **Character limit** : Splits text longer than the configured chunk size (default: 280 characters)
  2. **Sentence preservation** : Attempts to split at sentence boundaries (`.`, `!`, `?`)
  3. **Fallback splitting** : If sentences are too long, splits at commas, semicolons, or other natural breaks
  4. **Audio concatenation** : Seamlessly combines audio from multiple chunks


### Maximum Limits
  * **Soft limit** : Configurable characters per chunk (default: 280)
  * **Hard limit** : Configurable total characters (default: 3000)
  * **Automatic processing** : No manual intervention required


## Error Handling
FastAPI provides enhanced error handling with automatic validation:
  * **422 Unprocessable Entity** : Invalid input validation (Pydantic errors)
  * **400 Bad Request** : Business logic errors (text too long, etc.)
  * **500 Internal Server Error** : Model or processing errors


**Error Response Format:**

```
{
  "error": {
    "message": "Missing required field: 'input'",
    "type": "invalid_request_error"
  }
}

```

**Validation Error Example:**

```
{
  "detail": [
    {
      "type": "greater_equal",
      "loc": ["body", "exaggeration"],
      "msg": "Input should be greater than or equal to 0.25",
      "input": 0.1
    }
  ]
}

```

## Testing
Use the enhanced test script to verify the API functionality:

```
python tests/test_api.py

```

The test script will:
  * Test health check endpoint
  * Test models endpoint
  * Test API documentation endpoints (new!)
  * Generate speech for various text lengths
  * Test custom parameter validation
  * Test error handling with validation
  * Save generated audio files as `test_output_*.wav`


## Configuration
You can configure the API through environment variables or by modifying `.env.example`:

```
# Server Configuration
PORT=4123
HOST=0.0.0.0

# TTS Model Settings
EXAGGERATION=0.5          # Emotion intensity (0.25-2.0)
CFG_WEIGHT=0.5            # Pace control (0.0-1.0)
TEMPERATURE=0.8           # Sampling temperature (0.05-5.0)

# Text Processing
MAX_CHUNK_LENGTH=280      # Characters per chunk
MAX_TOTAL_LENGTH=3000     # Total character limit

# Voice and Model Settings
VOICE_SAMPLE_PATH=./voice-sample.mp3
VOICE_LIBRARY_DIR=./voices
DEVICE=auto               # auto/cuda/mps/cpu
MODEL_CACHE_DIR=./models

```

### Parameter Effects
**Exaggeration (0.25-2.0):**
  * `0.3-0.4`: Very neutral, professional
  * `0.5`: Neutral (default)
  * `0.7-0.8`: More expressive
  * `1.0+`: Very dramatic (may be unstable)


**CFG Weight (0.0-1.0):**
  * `0.2-0.3`: Faster speech
  * `0.5`: Balanced (default)
  * `0.7-0.8`: Slower, more deliberate


**Temperature (0.05-5.0):**
  * `0.4-0.6`: More consistent
  * `0.8`: Balanced (default)
  * `1.0+`: More creative/random


## Docker Deployment
For Docker deployment, see [DOCKER_README.md](https://github.com/travisvn/chatterbox-tts-api/blob/main/DOCKER_README.md) for complete instructions.
**Quick start with Docker Compose:**

```
cp .env.example .env  # Customize as needed
docker compose up -d

```

**Quick start with Docker:**

```
docker build -t chatterbox-tts .
docker run -d -p 4123:4123 \
  -v ./voice-sample.mp3:/app/voice-sample.mp3:ro \
  -e EXAGGERATION=0.7 \
  chatterbox-tts

```

## Performance Notes
**FastAPI Benefits:**
  * **Async performance** : Better handling of concurrent requests
  * **Faster JSON serialization** : ~25% faster than Flask
  * **Type validation** : Prevents invalid requests at the API level
  * **Auto documentation** : No manual API doc maintenance


**Hardware Recommendations:**
  * **Model loading** : The model is loaded once at startup (can take 30-60 seconds)
  * **First request** : May be slower due to initial model warm-up
  * **Subsequent requests** : Should be faster due to model caching
  * **Memory usage** : Varies by device (GPU recommended for best performance)
  * **Concurrent requests** : FastAPI async support allows better multi-request handling


## Integration Examples
### Python with requests

```
import requests

# Basic request
response = requests.post(
    "http://localhost:4123/v1/audio/speech",
    json={"input": "Hello world!"}
)

with open("output.wav", "wb") as f:
    f.write(response.content)

# With custom parameters and validation
response = requests.post(
    "http://localhost:4123/v1/audio/speech",
    json={
        "input": "Exciting news!",
        "exaggeration": 0.8,
        "cfg_weight": 0.4,
        "temperature": 1.0
    }
)

# Handle validation errors
if response.status_code == 422:
    print("Validation error:", response.json())

```

### JavaScript/Node.js

```
const response = await fetch('http://localhost:4123/v1/audio/speech', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    input: 'Hello world!',
    exaggeration: 0.7,
  }),
});

if (response.status === 422) {
  const error = await response.json();
  console.log('Validation error:', error);
} else {
  const audioBuffer = await response.arrayBuffer();
  // Save or play the audio buffer
}

```

### cURL

```
# Basic usage
curl -X POST http://localhost:4123/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{"input": "Your text here"}' \
  --output output.wav

# With custom parameters
curl -X POST http://localhost:4123/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{"input": "Dramatic text!", "exaggeration": 1.0, "cfg_weight": 0.3}' \
  --output dramatic.wav

# Test the interactive documentation
curl http://localhost:4123/docs

```

## Development Features
### FastAPI Development Tools
  * **Auto-reload** : Use `--reload` flag for development
  * **Interactive testing** : Use `/docs` for live API testing
  * **Type hints** : Full IDE support with Pydantic models
  * **Validation** : Automatic request/response validation
  * **OpenAPI** : Machine-readable API specification


### Development Mode

```
# Start with auto-reload
uvicorn app.main:app --host 0.0.0.0 --port 4123 --reload

# Or with verbose logging
uvicorn app.main:app --host 0.0.0.0 --port 4123 --log-level debug

```

## Troubleshooting
### Common Issues
  1. **Model not loading** : Ensure Chatterbox TTS is properly installed
  2. **Voice sample missing** : Verify `voice-sample.mp3` exists at the configured path
  3. **CUDA out of memory** : Try using CPU device (`DEVICE=cpu`)
  4. **Slow performance** : GPU recommended; ensure CUDA/MPS is available
  5. **Port conflicts** : Change `PORT` environment variable to an available port
  6. **Uvicorn not found** : Install with `pip install uvicorn[standard]`


### FastAPI Specific Issues
**Startup Issues:**

```
# Check if uvicorn is installed
uvicorn --version

# Run with verbose logging
uvicorn app.main:app --host 0.0.0.0 --port 4123 --log-level debug

# Alternative startup method
python main.py

```

**Validation Errors:**
Visit `/docs` to see the interactive API documentation and test your requests.
### Checking Configuration

```
# Check if API is running
curl http://localhost:4123/health

# View current configuration
curl http://localhost:4123/config

# Check API documentation
curl http://localhost:4123/openapi.json

# Test with simple text
curl -X POST http://localhost:4123/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{"input": "Test"}' \
  --output test.wav

```

## Migration from Flask
If you're migrating from the previous Flask version:
  1. **Dependencies** : Update to `fastapi` and `uvicorn` instead of `flask`
  2. **Startup** : Use `uvicorn app.main:app` instead of `python api.py`
  3. **Documentation** : Visit `/docs` for interactive API testing
  4. **Validation** : Error responses now use HTTP 422 for validation errors
  5. **Performance** : Expect 25-40% better performance for JSON responses


All existing API endpoints and request/response formats remain compatible.
[Star on GitHub](https://github.com/travisvn/chatterbox-tts-api)
© 2026 Chatterbox TTS API
Not affiliated with Resemble AI
[Join our Discord](https://chatterboxtts.com/discord)[View on GitHub](https://github.com/travisvn/chatterbox-tts-api)


--- DOCUMENT: https://chatterboxtts.com/docs/docker-readme ---
# Chatterbox TTS API Docker Deployment Guide
This guide covers how to run the Chatterbox TTS FastAPI using Docker and Docker Compose v2.
## 🚀 Quick Start
### Option 1: Docker Compose (Recommended)
  1. **Clone and prepare:**

```
git clone https://github.com/travisvn/chatterbox-tts-api
cd chatterbox-tts-api

# For Docker deployment (recommended)
cp .env.example.docker .env

# Or for local development
# cp .env.example .env

```

  2. **Choose your Docker Compose variant:**

```
# Standard setup (pip-based, auto-detects device)
docker compose -f docker/docker-compose.yml up -d

# uv-optimized setup (faster builds, better dependencies)
docker compose -f docker/docker-compose.uv.yml up -d

# GPU-optimized (traditional pip + NVIDIA GPU)
docker compose -f docker/docker-compose.gpu.yml up -d

# uv + GPU optimized (fastest builds + NVIDIA GPU)
docker compose -f docker/docker-compose.uv.gpu.yml up -d

# CPU-only (forced CPU, no GPU dependencies)
docker compose -f docker/docker-compose.cpu.yml up -d

```

> [!NOTE]
>  It's recommended to run `docker compose` from the parent directory and to specify the `.yml` file by referencing it in the docker subfolder (i.e. `-f docker/docker-compose*.yml`)
  3. **Test the API:**

```
curl -X POST http://localhost:4123/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{"input": "Hello from Docker!"}' \
  --output test.wav

```

  4. **Explore the API Documentation:**

```
# Interactive Swagger UI
open http://localhost:4123/docs

# Alternative ReDoc documentation
open http://localhost:4123/redoc

```


### Docker Compose Variants
| File  | Description  | Use Case  |
| --- | --- | --- |
| `docker-compose.yml`  | Standard pip-based build, auto device  | General use  |
| `docker-compose.uv.yml`  | uv-optimized build, auto device  | Faster builds, better deps  |
| `docker-compose.gpu.yml`  | Standard build with GPU enabled  | NVIDIA GPU users  |
| `docker-compose.uv.gpu.yml`  | uv-optimized build with GPU enabled  | Best of both worlds  |
| `docker-compose.cpu.yml`  | CPU-only build (no GPU dependencies)  | CPU-only environments  |
### Option 2: Docker Run

```
# Build the image
docker build -t chatterbox-tts-api .

# Run the container
docker run -d \
  --name chatterbox-tts-api \
  -p 4123:4123 \
  -v ./voice-sample.mp3:/app/voice-sample.mp3:ro \
  -v chatterbox-models:/cache \
  -e EXAGGERATION=0.7 \
  -e CFG_WEIGHT=0.4 \
  chatterbox-tts-api

```

## 📋 Prerequisites
  * Docker Engine 20.10+
  * Docker Compose v2 (comes with Docker Desktop)
  * At least 4GB RAM (8GB+ recommended)
  * GPU support (optional but recommended)


### For GPU Support
**NVIDIA GPU (Linux):**

```
# Install NVIDIA Container Toolkit
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
  sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
  sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list

sudo apt-get update && sudo apt-get install -y nvidia-container-toolkit
sudo systemctl restart docker

```

Then enable the GPU section in the appropriate `docker-compose.yml`.
## ⚙️ Configuration
### Environment Files
The project provides two environment example files:
  * **`.env.example.docker`**- Pre-configured for Docker with container paths (`/cache` , `/app/voice-sample.mp3`)
  * **`.env.example`**- Configured for local development with relative paths (`./models` , `./voice-sample.mp3`)


For Docker deployment, use the Docker-specific version:

```
cp .env.example.docker .env

```

### Environment Variables
Copy the appropriate environment file and customize:

```
# For Docker (recommended)
cp .env.example.docker .env

# For local development
cp .env.example .env

# Edit as needed
nano .env  # or your preferred editor

```

**Key variables:**
| Variable  | Default  | Description  |
| --- | --- | --- |
| `PORT`  | `4123`  | API server port  |
| `EXAGGERATION`  | `0.5`  | Emotion intensity (0.25-2.0)  |
| `CFG_WEIGHT`  | `0.5`  | Pace control (0.0-1.0)  |
| `TEMPERATURE`  | `0.8`  | Sampling temperature (0.05-5.0)  |
| `VOICE_SAMPLE_PATH`  | `./voice-sample.mp3`  | Path to voice sample  |
| `VOICE_LIBRARY_DIR`  | `/voices`  | Directory for voice library  |
| `DEVICE`  | `auto`  | Device: auto/cuda/mps/cpu  |
| `MAX_CHUNK_LENGTH`  | `280`  | Max characters per chunk  |
### Voice Configuration
#### Default Voice Sample

```
# Place your voice sample in the project root
cp your-voice.mp3 voice-sample.mp3

```

Or use environment variables for custom paths:

```
VOICE_SAMPLE_PATH=/app/voice-samples/custom-voice.mp3
VOICE_SAMPLE_HOST_PATH=./my-voices/custom-voice.mp3

```

#### Voice Library Management
The voice library allows you to upload and manage multiple voices that persist across container restarts:

```
# Upload a voice to the library
curl -X POST http://localhost:4123/v1/voices \
  -F "voice_file=@my-voice.wav" \
  -F "name=my-custom-voice"

# Use the voice by name in speech generation
curl -X POST http://localhost:4123/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{"input": "Hello!", "voice": "my-custom-voice"}' \
  --output output.wav

# List available voices
curl http://localhost:4123/v1/voices

```

**Voice Storage:** Voices are stored in the persistent `chatterbox-voices` Docker volume mounted at `/voices` inside the container.
## 🏗️ Build Options
### Standard Build

```
docker build -t chatterbox-tts .

```

### Build with Custom Base Image

```
docker build --build-arg BASE_IMAGE=python:3.11-bullseye -t chatterbox-tts .

```

### Multi-stage Build (Smaller Image)

```
docker build -f Dockerfile.slim -t chatterbox-tts:slim .

```

## 🚢 Deployment Examples
### Development Setup

```
# docker-compose.dev.yml
services:
  chatterbox-tts:
    build: .
    ports:
      - '4123:4123'
    environment:
      - EXAGGERATION=0.7
    volumes:
      - .:/app
      - chatterbox-models:/cache
    command: uvicorn api:app --host=0.0.0.0 --port=4123 --reload

```

```
docker compose -f docker-compose.dev.yml up

```

### Production Setup

```
# docker-compose.prod.yml
services:
  chatterbox-tts:
    image: chatterbox-tts:latest
    restart: always
    ports:
      - '4123:4123'
    environment:
      - EXAGGERATION=0.5
      - CFG_WEIGHT=0.5
    volumes:
      - ./voice-sample.mp3:/app/voice-sample.mp3:ro
      - chatterbox-models:/cache
    deploy:
      resources:
        limits:
          memory: 8G
        reservations:
          memory: 4G

```

### Multiple Instances (Load Balancing)

```
services:
  chatterbox-tts-1:
    build: .
    ports:
      - '4123:4123'
    # ... config

  chatterbox-tts-2:
    build: .
    ports:
      - '5124:4123'
    # ... config

  nginx:
    image: nginx:alpine
    ports:
      - '80:80'
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - chatterbox-tts-1
      - chatterbox-tts-2

```

## 📊 Monitoring and Logs
### View Logs

```
# Real-time logs
docker compose logs -f chatterbox-tts

# Last 100 lines
docker compose logs --tail=100 chatterbox-tts

```

### Health Checks

```
# Check container health
docker compose ps

# Manual health check
curl http://localhost:4123/health

# Get configuration
curl http://localhost:4123/config

# Check API documentation
curl http://localhost:4123/docs

```

### Resource Monitoring

```
# Container stats
docker stats chatterbox-tts-api

# Detailed info
docker inspect chatterbox-tts-api

```

## 🔧 Troubleshooting
### Common Issues
**1. Model Download Fails**

```
# Check internet connectivity
docker compose exec chatterbox-tts curl -I https://huggingface.co

# Clear model cache
docker volume rm chatterbox_chatterbox-models
docker compose up --build

```

**2. Voice Sample Not Found**

```
# Check file permissions
ls -la voice-sample.mp3

# Verify mount
docker compose exec chatterbox-tts ls -la /app/voice-sample.mp3

```

**3. Out of Memory**

```
# Check memory usage
docker stats

# Increase Docker memory limit or use CPU device
echo 'DEVICE=cpu' >> .env
docker compose up -d

```

**4. GPU Not Detected**

```
# Check NVIDIA runtime
docker run --rm --gpus all nvidia/cuda:11.8-base-ubuntu20.04 nvidia-smi

# Verify GPU setup in container
docker compose exec chatterbox-tts python -c "import torch; print(torch.cuda.is_available())"

```

**5. FastAPI/Uvicorn Issues**

```
# Check if uvicorn is running
docker compose exec chatterbox-tts ps aux | grep uvicorn

# Check FastAPI logs
docker compose logs chatterbox-tts | grep "Application startup complete"

# Test API endpoints
curl http://localhost:4123/openapi.json

```

### Performance Tuning
**For CPU-only systems:**

```
DEVICE=cpu
MAX_CHUNK_LENGTH=200  # Smaller chunks
TEMPERATURE=0.6       # Less random sampling

```

**For GPU systems:**

```
DEVICE=cuda
MAX_CHUNK_LENGTH=300  # Can handle larger chunks

```

**For faster inference:**

```
CFG_WEIGHT=0.3        # Faster speech
TEMPERATURE=0.5       # More deterministic

```

**FastAPI Performance:**

```
# Production settings
HOST=0.0.0.0
PORT=4123

# Development settings (Docker dev setup)
UVICORN_RELOAD=true
UVICORN_LOG_LEVEL=debug

```

## 🔒 Security Considerations
### Production Security

```
# Disable debug mode (production)
UVICORN_LOG_LEVEL=info

# Bind to specific interface
HOST=127.0.0.1  # localhost only

# Use secrets for sensitive config
VOICE_SAMPLE_PATH=/run/secrets/voice_sample

```

### Docker Secrets Example

```
services:
  chatterbox-tts:
    # ... other config
    secrets:
      - voice_sample
    environment:
      - VOICE_SAMPLE_PATH=/run/secrets/voice_sample

secrets:
  voice_sample:
    file: ./secrets/voice-sample.mp3

```

## 📈 Scaling
### Horizontal Scaling

```
services:
  chatterbox-tts:
    # ... config
    deploy:
      replicas: 3
      resources:
        limits:
          memory: 4G
        reservations:
          memory: 2G

```

### Using External Load Balancer

```
# HAProxy example
docker run -d --name haproxy \
  -p 80:80 \
  -v ./haproxy.cfg:/usr/local/etc/haproxy/haproxy.cfg:ro \
  haproxy:alpine

```

### FastAPI Scaling Benefits
  * **Better async performance** : FastAPI handles more concurrent requests efficiently
  * **Lower memory overhead** : More efficient than Flask for JSON serialization
  * **Built-in monitoring** : OpenAPI metrics available at `/openapi.json`


## 🧪 Testing
### Automated Testing

```
# Run test suite
docker compose exec chatterbox-tts python tests/test_api.py

# Test FastAPI specific features
docker compose exec chatterbox-tts python -c "
import requests
# Test documentation endpoints
resp = requests.get('http://localhost:4123/docs')
print(f'Docs Status: {resp.status_code}')

resp = requests.get('http://localhost:4123/openapi.json')
print(f'OpenAPI Status: {resp.status_code}')
"

```

### Performance Testing

```
# Stress test with multiple requests
for i in {1..10}; do
  curl -X POST http://localhost:4123/v1/audio/speech \
    -H "Content-Type: application/json" \
    -d '{"input": "Performance test '$i'"}' \
    --output test_$i.wav &
done
wait

```

### API Documentation Testing

```
# Test interactive docs
curl -f http://localhost:4123/docs

# Test API schema
curl http://localhost:4123/openapi.json | jq '.info.title'

# Test ReDoc
curl -f http://localhost:4123/redoc

```

## 📝 Advanced Configuration
### Custom Dockerfile for FastAPI

```
# Dockerfile.custom
FROM chatterbox-tts:latest

# Add custom FastAPI middleware
COPY custom_middleware.py /app/
ENV PYTHONPATH="/app:$PYTHONPATH"

# Custom uvicorn settings
ENV UVICORN_WORKERS=1
ENV UVICORN_LOG_LEVEL=info

```

### Multi-architecture Build

```
# Build for multiple platforms
docker buildx create --use
docker buildx build --platform linux/amd64,linux/arm64 -t chatterbox-tts:multi .

```

### CI/CD Integration

```
# .github/workflows/docker.yml
name: Docker Build
on: [push]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Build and test
        run: |
          docker compose up -d
          sleep 30
          curl -f http://localhost:4123/health
          curl -f http://localhost:4123/docs
          docker compose down

```

## 🆕 FastAPI Migration Notes
If you're upgrading from the Flask version:
### Key Changes
  1. **Startup Command** :
     * Current: `CMD ["python", "main.py"]` (FastAPI with uvicorn)
     * Previous: `CMD ["python", "api.py"]` (Flask)
  2. **Dependencies** :
     * Removed: `flask`
     * Added: `fastapi`, `uvicorn[standard]`, `pydantic`
  3. **New Features** :
     * Interactive API docs at `/docs`
     * Alternative docs at `/redoc`
     * OpenAPI schema at `/openapi.json`
     * Better async performance
     * Automatic request validation


### Compatibility
  * ✅ All existing API endpoints work the same
  * ✅ Request/response formats unchanged
  * ✅ Docker Compose files updated automatically
  * ✅ Environment variables remain the same
  * ⚡ Performance improved by 25-40%


For more information, see the main [API_README.md](https://github.com/travisvn/chatterbox-tts-api/blob/main/API_README.md) for API usage details.
[Star on GitHub](https://github.com/travisvn/chatterbox-tts-api)
© 2026 Chatterbox TTS API
Not affiliated with Resemble AI
[Join our Discord](https://chatterboxtts.com/discord)[View on GitHub](https://github.com/travisvn/chatterbox-tts-api)


--- DOCUMENT: https://chatterboxtts.com/docs/endpoint-aliasing ---
# Endpoint Aliasing in FastAPI
This document explains how to create endpoint aliases in your FastAPI application, allowing multiple URLs to point to the same endpoint function.
## Why Endpoint Aliasing?
Endpoint aliasing is useful for:
  * **API Versioning** : Supporting both `/v1/endpoint` and `/endpoint` patterns
  * **Backward Compatibility** : Maintaining old endpoints while introducing new ones
  * **OpenAI Compatibility** : Matching OpenAI API paths while providing your own convention


## Method 1: Multiple Decorators (Simple)
The most straightforward approach is using multiple decorators on the same function:

```
@router.post(
    "/v1/audio/speech",
    response_class=StreamingResponse,
    summary="Generate speech from text"
)
@router.post("/audio/speech", include_in_schema=False)  # Alias endpoint
async def text_to_speech(request: TTSRequest):
    """Generate speech from text"""
    # Implementation here
    pass

```

**Pros:**
  * Simple and explicit
  * Easy to understand
  * No additional dependencies


**Cons:**
  * Repetitive for many endpoints
  * Easy to forget `include_in_schema=False`
  * Harder to maintain large numbers of aliases


## Method 2: Centralized Aliasing System (Recommended)
We've created a centralized system in `app/core/aliases.py`:
### Configuration

```
# app/core/aliases.py
# Format: "primary_endpoint": ["alias1", "alias2", ...]
ENDPOINT_ALIASES = {
    "/audio/speech": ["/v1/audio/speech"],
    "/audio/speech/upload": ["/v1/audio/speech/upload"],
    "/health": ["/v1/health"],
    "/models": ["/v1/models"],
    "/config": ["/v1/config"],
    "/endpoints": ["/v1/endpoints"],
    "/memory": ["/v1/memory"],
    "/memory/reset": ["/v1/memory/reset"],
}

```

### Usage Example

```
from fastapi import APIRouter
from app.core import add_route_aliases

# Create router with aliasing support
base_router = APIRouter()
router = add_route_aliases(base_router)

@router.get(
    "/config",
    response_model=ConfigResponse,
    summary="Get configuration"
)
async def get_config():
    """Get current configuration"""
    # Implementation here
    pass

# This automatically creates both:
# - /config (primary, included in schema)
# - /v1/config (alias, excluded from schema)

```

### Important: Export base_router
When using the aliasing system, export the `base_router` for the main application:

```
# At the end of your endpoint file
__all__ = ["base_router"]

```

And update your main router:

```
# app/api/router.py
api_router.include_router(config.base_router, tags=["Configuration"])

```

## Method 3: Manual Alias Route Decorator
For one-off aliases or custom behavior:

```
from app.core import alias_route

@alias_route("/v1/custom/endpoint", "/custom/endpoint")
@router.get()
async def custom_endpoint():
    pass

```

## Managing Aliases
### View All Aliases

```
from app.core import get_all_aliases

aliases = get_all_aliases()
print(aliases)

```

### Add Runtime Aliases

```
from app.core import add_custom_alias

add_custom_alias("/v1/new/endpoint", "/new/endpoint")

```

### Remove Aliases

```
from app.core import remove_alias

remove_alias("/v1/endpoint")

```

## Current Project Structure
Your project now uses **Method 2** consistently across all endpoints:
  * **Speech endpoints** : `speech.py`
    * `/audio/speech` → ["/v1/audio/speech"]
    * `/audio/speech/upload` → ["/v1/audio/speech/upload"]
  * **Health endpoint** : `health.py`
    * `/health` → ["/v1/health"]
  * **Models endpoint** : `models.py`
    * `/models` → ["/v1/models"]
  * **Config endpoint** : `config.py`
    * `/config` → ["/v1/config"]
    * `/endpoints` → ["/v1/endpoints"]
  * **Memory endpoints** : `memory.py`
    * `/memory` → ["/v1/memory"]
    * `/memory/reset` → ["/v1/memory/reset"]


## Migration Recommendations
### For New Endpoints
Use **Method 2** (centralized system) for consistency and maintainability.
### For Existing Endpoints
You can keep using **Method 1** or gradually migrate to **Method 2**. Both approaches work seamlessly together.
### Best Practices
  1. **Primary endpoints** should use clean, short paths (no `/v1/` prefix) and be included in schema
  2. **Alias endpoints** should use `/v1/` prefix for OpenAI compatibility and be excluded from schema
  3. **Document your aliases** in the `ENDPOINT_ALIASES` configuration
  4. **Use consistent naming** across your API
  5. **Support multiple aliases** per endpoint for maximum flexibility


## Testing Aliases
Both endpoints should work identically:

```
# Primary endpoint (recommended)
curl -X POST "http://localhost:8000/audio/speech" \
  -H "Content-Type: application/json" \
  -d '{"input": "Hello world"}'

# Alias endpoint (OpenAI compatibility - same result)
curl -X POST "http://localhost:8000/v1/audio/speech" \
  -H "Content-Type: application/json" \
  -d '{"input": "Hello world"}'

```

## OpenAPI Schema
Only primary endpoints appear in the automatically generated documentation at `/docs`, keeping it clean while maintaining backward compatibility.
[Star on GitHub](https://github.com/travisvn/chatterbox-tts-api)
© 2026 Chatterbox TTS API
Not affiliated with Resemble AI
[Join our Discord](https://chatterboxtts.com/discord)[View on GitHub](https://github.com/travisvn/chatterbox-tts-api)


--- DOCUMENT: https://chatterboxtts.com/docs/multilingual ---
# Multilingual Support Documentation
![22 Languages Supported](https://img.shields.io/badge/Languages-22%20Supported-brightgreen) ![chatterbox-tts v0.1.4](https://img.shields.io/badge/chatterbox--tts-v0.1.4-blue) ![OpenAI Compatible](https://img.shields.io/badge/API-OpenAI%20Compatible-orange)
## Overview
Chatterbox TTS API supports multilingual text-to-speech generation across **22 languages** using the enhanced `chatterbox-tts` v0.1.4 multilingual model. This feature enables high-quality voice cloning and speech synthesis in multiple languages while maintaining full OpenAI API compatibility.
### Key Features
🌍 **22 Languages Supported** - Generate speech in Arabic, Chinese, English, French, German, Italian, Japanese, Spanish, and more
🎭 **Language-Aware Voice Cloning** - Upload voices with specific language assignments
🔄 **Automatic Language Detection** - Speech generation automatically uses the voice's assigned language
🧠 **Smart Fallbacks** - Graceful handling of missing languages with English fallback
📚 **Voice Library Integration** - Language metadata stored with each voice
⚙️ **Configurable** - Enable/disable multilingual mode via environment variables
🔗 **OpenAI Compatible** - No breaking changes to existing API endpoints
📱 **Frontend Support** - Language selection UI with flags and native names
## Supported Languages
The multilingual model supports the following 22 languages:
| Code  | Language  | Native Name  | Flag  |
| --- | --- | --- | --- |
| `ar`  | Arabic  | العربية  | 🇸🇦  |
| `da`  | Danish  | Dansk  | 🇩🇰  |
| `de`  | German  | Deutsch  | 🇩🇪  |
| `el`  | Greek  | Ελληνικά  | 🇬🇷  |
| `en`  | English  | English  | 🇺🇸  |
| `es`  | Spanish  | Español  | 🇪🇸  |
| `fi`  | Finnish  | Suomi  | 🇫🇮  |
| `fr`  | French  | Français  | 🇫🇷  |
| `he`  | Hebrew  | עברית  | 🇮🇱  |
| `hi`  | Hindi  | हिन्दी  | 🇮🇳  |
| `it`  | Italian  | Italiano  | 🇮🇹  |
| `ja`  | Japanese  | 日本語  | 🇯🇵  |
| `ko`  | Korean  | 한국어  | 🇰🇷  |
| `ms`  | Malay  | Bahasa Melayu  | 🇲🇾  |
| `nl`  | Dutch  | Nederlands  | 🇳🇱  |
| `no`  | Norwegian  | Norsk  | 🇳🇴  |
| `pl`  | Polish  | Polski  | 🇵🇱  |
| `pt`  | Portuguese  | Português  | 🇵🇹  |
| `ru`  | Russian  | Русский  | 🇷🇺  |
| `sv`  | Swedish  | Svenska  | 🇸🇪  |
| `sw`  | Swahili  | Kiswahili  | 🇹🇿  |
| `tr`  | Turkish  | Türkçe  | 🇹🇷  |
> **Note** : Chinese (`zh`) support is available in the model but currently disabled. Contact support if you need Chinese language support.
## Configuration
### Enable/Disable Multilingual Mode
Multilingual support is controlled by the `USE_MULTILINGUAL_MODEL` environment variable:

```
# Enable multilingual support (default)
USE_MULTILINGUAL_MODEL=true

# Disable multilingual support (English only)
USE_MULTILINGUAL_MODEL=false

```

**Default Behavior:**
  * Multilingual mode is **enabled by default** (`true`)
  * When disabled, only English is supported
  * Existing installations automatically get multilingual support


### Environment Variables
Add to your `.env` file:

```
# Multilingual TTS Configuration
USE_MULTILINGUAL_MODEL=true   # Enable 23-language support (default: true)

```

## API Usage
### 1. Get Supported Languages
Retrieve the list of languages supported by your current configuration:

```
curl http://localhost:4123/languages

```

**Response (Multilingual Mode):**

```
{
  "languages": [
    { "code": "ar", "name": "Arabic" },
    { "code": "da", "name": "Danish" },
    { "code": "de", "name": "German" }
    // ... all 23 languages
  ],
  "count": 23,
  "model_type": "multilingual"
}

```

**Response (Standard Mode):**

```
{
  "languages": [{ "code": "en", "name": "English" }],
  "count": 1,
  "model_type": "standard"
}

```

### 2. Upload Voice with Language
Upload a voice sample and assign a specific language:

```
curl -X POST http://localhost:4123/voices \
  -F "voice_name=french_speaker" \
  -F "language=fr" \
  -F "voice_file=@french_voice.wav"

```

**Parameters:**
  * `voice_name`: Unique identifier for the voice
  * `language`: ISO 639-1 language code (e.g., `fr`, `de`, `ja`)
  * `voice_file`: Audio file in supported format


**Language Validation:**
  * Language codes are validated against supported languages
  * Invalid codes return a clear error message
  * Defaults to `"en"` if not specified


### 3. Generate Multilingual Speech
Once a voice is uploaded with a language, speech generation automatically uses the correct language:

```
# Generate French speech using French voice
curl -X POST http://localhost:4123/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{
    "input": "Bonjour, comment allez-vous?",
    "voice": "french_speaker"
  }' \
  --output french_speech.wav

```

**Key Points:**
  * **No language parameter needed** in speech requests (OpenAI compatibility)
  * Language is automatically determined from voice metadata
  * Text can be in any language - the model handles cross-lingual synthesis
  * All standard TTS parameters work with multilingual voices


### 4. Voice Library with Language Metadata
List voices to see language information:

```
curl http://localhost:4123/voices

```

**Response:**

```
{
  "voices": [
    {
      "name": "french_speaker",
      "file_path": "/voices/french_speaker.wav",
      "aliases": [],
      "metadata": {
        "language": "fr",
        "created_at": "2024-01-15T10:30:00Z",
        "file_size": 2048576,
        "duration": 12.5
      }
    }
  ],
  "count": 1
}

```

## Advanced Usage Examples
### Python Examples
#### Upload and Use Multilingual Voice

```
import requests

# Upload a German voice
with open("german_speaker.wav", "rb") as voice_file:
    response = requests.post(
        "http://localhost:4123/voices",
        data={
            "voice_name": "german_narrator",
            "language": "de"
        },
        files={
            "voice_file": ("german_speaker.wav", voice_file, "audio/wav")
        }
    )

print(f"Upload status: {response.status_code}")

# Generate German speech
response = requests.post(
    "http://localhost:4123/v1/audio/speech",
    json={
        "input": "Guten Tag! Wie geht es Ihnen heute?",
        "voice": "german_narrator",
        "exaggeration": 0.8
    }
)

with open("german_output.wav", "wb") as f:
    f.write(response.content)

```

#### Batch Upload Multiple Languages

```
import requests
import os

voices = [
    {"file": "spanish_voice.wav", "name": "spanish_speaker", "lang": "es"},
    {"file": "italian_voice.wav", "name": "italian_speaker", "lang": "it"},
    {"file": "japanese_voice.wav", "name": "japanese_speaker", "lang": "ja"},
]

for voice in voices:
    with open(voice["file"], "rb") as f:
        response = requests.post(
            "http://localhost:4123/voices",
            data={
                "voice_name": voice["name"],
                "language": voice["lang"]
            },
            files={"voice_file": f}
        )
    print(f"Uploaded {voice['name']}: {response.status_code}")

```

#### Generate Speech in Multiple Languages

```
import requests

texts = [
    {"text": "Hello, how are you today?", "voice": "english_speaker"},
    {"text": "Hola, ¿cómo estás hoy?", "voice": "spanish_speaker"},
    {"text": "Ciao, come stai oggi?", "voice": "italian_speaker"},
    {"text": "こんにちは、今日はいかがですか？", "voice": "japanese_speaker"},
]

for i, item in enumerate(texts):
    response = requests.post(
        "http://localhost:4123/v1/audio/speech",
        json={
            "input": item["text"],
            "voice": item["voice"]
        }
    )

    with open(f"multilingual_output_{i+1}.wav", "wb") as f:
        f.write(response.content)

```

### Streaming with Multilingual Voices

```
# Stream Japanese speech
curl -X POST http://localhost:4123/v1/audio/speech/stream \
  -H "Content-Type: application/json" \
  -d '{
    "input": "こんにちは。私の名前は田中です。よろしくお願いします。",
    "voice": "japanese_speaker",
    "chunk_strategy": "sentence"
  }' \
  --output japanese_stream.wav

```

### Voice Upload with Custom Parameters

```
# Upload with additional metadata and parameters
curl -X POST http://localhost:4123/voices \
  -F "voice_name=professional_german" \
  -F "language=de" \
  -F "voice_file=@professional_voice.wav"

```

## Frontend Integration
The web UI includes comprehensive multilingual support:
### Language Selection
  * Dropdown with native language names and flag emojis
  * Automatic validation against supported languages
  * Default selection to English


### Voice Library Display
  * Language badges next to each voice
  * Flag emojis for visual identification
  * Sorting and filtering by language


### Upload Interface
  * Language selection integrated into voice upload modal
  * Real-time validation and feedback
  * Intuitive language picker with search


## Technical Implementation
### Architecture
The multilingual implementation consists of several key components:
  1. **Model Loading** : Automatic detection and loading of multilingual vs standard TTS model
  2. **Language Detection** : Voice metadata stores language information
  3. **Speech Generation** : Automatic language parameter injection based on voice metadata
  4. **API Compatibility** : Maintains OpenAI API format without breaking changes


### Model Switching

```
# Automatic model selection based on configuration
if Config.USE_MULTILINGUAL_MODEL:
    model = ChatterboxMultilingualTTS(...)
    supported_languages = SUPPORTED_LANGUAGES
else:
    model = ChatterboxTTS(...)
    supported_languages = {"en": "English"}

```

### Language Resolution

```
def resolve_voice_path_and_language(voice_name_or_path):
    """Resolve voice path and extract language metadata"""
    if voice_name_or_path in voice_library:
        voice_info = voice_library.get_voice_info(voice_name_or_path)
        return voice_info.path, voice_info.language
    else:
        return voice_name_or_path, "en"  # Default to English

```

### Backward Compatibility
  * **Existing voices** : Automatically assigned English (`"en"`) language
  * **Existing API calls** : Continue to work without modification
  * **Configuration** : Multilingual mode can be disabled for compatibility
  * **Graceful degradation** : Falls back to English for unsupported languages


## Performance Considerations
### Memory Usage
  * Multilingual model requires slightly more memory than standard model
  * Language switching doesn't require model reloading
  * Voice library scales efficiently with multiple languages


### Generation Speed
  * Multilingual generation performance is comparable to standard model
  * Language-specific optimizations built into the model
  * Streaming maintains low latency across all languages


### Storage
  * Voice files stored with language metadata in JSON format
  * No additional storage overhead for multilingual support
  * Efficient indexing by language for large voice libraries


## Troubleshooting
### Common Issues
**Languages endpoint returns only English**

```
# Check multilingual configuration
curl http://localhost:4123/config | grep USE_MULTILINGUAL_MODEL

```

**Voice upload fails with language validation error**

```
{
  "error": {
    "message": "Unsupported language code: xx. Supported: ar, da, de, ...",
    "type": "language_validation_error"
  }
}

```

**Speech generation ignores voice language**
  * Ensure voice was uploaded with correct language parameter
  * Check voice metadata: `curl http://localhost:4123/voices`
  * Verify multilingual mode is enabled


### Debugging
Enable debug logging for multilingual operations:

```
# Check current configuration
curl http://localhost:4123/config

# Verify supported languages
curl http://localhost:4123/languages

# Check voice metadata
curl http://localhost:4123/voices

```

## Migration Guide
### From Standard to Multilingual
  1. **Update dependencies** (already done in v0.1.4):

```
uv sync  # or pip install -r requirements.txt

```

  2. **Enable multilingual mode** :

```
echo "USE_MULTILINGUAL_MODEL=true" >> .env

```

  3. **Restart the API** :

```
uv run main.py  # or python main.py

```

  4. **Upload new voices with languages** :

```
curl -X POST http://localhost:4123/voices \
  -F "voice_name=multilingual_voice" \
  -F "language=fr" \
  -F "voice_file=@voice.wav"

```


### Existing Voice Library
  * Existing voices continue to work unchanged
  * All existing voices default to English (`"en"`)
  * Optionally re-upload voices with correct language assignments
  * No data loss or corruption


## Best Practices
### Voice Quality Guidelines
  1. **Language-Specific Recordings** :
     * Use native speakers for each language
     * Record in the target language for best results
     * Avoid mixing languages within a single voice sample
  2. **Audio Quality** :
     * 10-30 seconds of clear speech
     * Consistent speaking pace and tone
     * Minimal background noise
     * High-quality audio format (WAV preferred)
  3. **Voice Naming** :
     * Include language in voice names: `french_narrator`, `spanish_casual`
     * Use descriptive names for different styles: `german_formal`, `italian_cheerful`
     * Consider voice characteristics: `japanese_female_young`, `arabic_male_deep`


### Multilingual Workflows
  1. **Development** :
     * Test with multiple languages during development
     * Validate language assignment for uploaded voices
     * Use streaming for better user experience with longer texts
  2. **Production** :
     * Monitor memory usage with multiple language models
     * Implement proper error handling for unsupported languages
     * Consider caching frequently used voice/language combinations
  3. **Content Management** :
     * Organize voices by language and use case
     * Document voice characteristics and appropriate use cases
     * Maintain consistent quality standards across languages


## API Reference
### Endpoints
| Endpoint  | Method  | Description  |
| --- | --- | --- |
| `/languages`  | GET  | Get supported languages  |
| `/voices`  | POST  | Upload voice with language  |
| `/voices`  | GET  | List voices with language metadata  |
| `/v1/audio/speech`  | POST  | Generate speech (language auto-detected)  |
| `/v1/audio/speech/stream`  | POST  | Stream speech generation  |
### Request/Response Models
#### SupportedLanguageItem

```
{
  "code": "fr",
  "name": "French"
}

```

#### SupportedLanguagesResponse

```
{
  "languages": [SupportedLanguageItem],
  "count": 23,
  "model_type": "multilingual"
}

```

#### VoiceLibraryItem

```
{
  "name": "french_speaker",
  "file_path": "/voices/french_speaker.wav",
  "aliases": [],
  "metadata": {
    "language": "fr",
    "created_at": "2024-01-15T10:30:00Z",
    "file_size": 2048576,
    "duration": 12.5
  }
}

```

## Examples Repository
For more examples and integration patterns, see:
  * [Basic multilingual examples](https://github.com/travisvn/chatterbox-tts-api/blob/main/../tests/test_api.py)
  * [Frontend implementation](https://github.com/travisvn/chatterbox-tts-api/blob/main/../frontend/src/components/VoiceUploadModal.tsx)
  * [Testing guide](https://github.com/travisvn/chatterbox-tts-api/blob/main/./MULTILINGUAL_TESTING_GUIDE.md)


## Support
  * 📖 **Documentation** : [Main README](https://github.com/travisvn/chatterbox-tts-api/blob/main/../README.md) | [API Documentation](https://github.com/travisvn/chatterbox-tts-api/blob/main/./API_README.md)
  * 💬 **Discord** : [Join the community](http://chatterboxtts.com/discord)


* * *
_Built with`chatterbox-tts` v0.1.4 • Supports 22 languages • OpenAI API Compatible_
[Star on GitHub](https://github.com/travisvn/chatterbox-tts-api)
© 2026 Chatterbox TTS API
Not affiliated with Resemble AI
[Join our Discord](https://chatterboxtts.com/discord)[View on GitHub](https://github.com/travisvn/chatterbox-tts-api)


--- DOCUMENT: https://chatterboxtts.com/docs/status-api ---
# TTS Status API Documentation
This document describes the new status tracking endpoints that provide real-time information about TTS processing.
## Overview
The status API allows you to monitor TTS request processing in real-time, view progress information, check statistics, and review request history.
## Endpoints
### 🔍 GET `/status`
Get comprehensive TTS processing status information.
**Query Parameters:**
  * `include_memory` (boolean): Include memory usage information
  * `include_history` (boolean): Include recent request history
  * `include_stats` (boolean): Include processing statistics
  * `history_limit` (integer): Number of history records to return (1-20)


**Example:**

```
curl "http://localhost:4123/status?include_memory=true&include_stats=true"

```

**Response:**

```
{
  "status": "generating_audio",
  "is_processing": true,
  "request_id": "abc12345",
  "start_time": 1704067200.0,
  "duration_seconds": 2.5,
  "text_length": 156,
  "text_preview": "This is the text being processed...",
  "voice_source": "default",
  "parameters": {
    "exaggeration": 0.7,
    "cfg_weight": 0.5,
    "temperature": 0.8
  },
  "progress": {
    "current_chunk": 2,
    "total_chunks": 4,
    "current_step": "Generating audio for chunk 2/4",
    "progress_percentage": 50.0,
    "estimated_completion": 1704067205.0
  },
  "total_requests": 42
}

```

### ⚡ GET `/status/progress`
Get lightweight progress information (optimized for polling).
**Example:**

```
curl "http://localhost:4123/status/progress"

```

**Response when processing:**

```
{
  "is_processing": true,
  "status": "generating_audio",
  "current_step": "Generating audio for chunk 2/4",
  "current_chunk": 2,
  "total_chunks": 4,
  "progress_percentage": 50.0,
  "duration_seconds": 2.5,
  "estimated_completion": 1704067205.0,
  "text_preview": "This is the text being processed..."
}

```

**Response when idle:**

```
{
  "is_processing": false,
  "status": "idle",
  "message": "No active TTS requests"
}

```

### 📊 GET `/status/statistics`
Get comprehensive processing statistics.
**Query Parameters:**
  * `include_memory` (boolean): Include current memory usage


**Example:**

```
curl "http://localhost:4123/status/statistics?include_memory=true"

```

**Response:**

```
{
  "total_requests": 42,
  "completed_requests": 38,
  "error_requests": 4,
  "success_rate": 90.5,
  "average_duration_seconds": 3.2,
  "average_text_length": 124.5,
  "is_processing": false,
  "current_memory": {
    "cpu_memory_mb": 256.7,
    "gpu_memory_allocated_mb": 1024.3
  }
}

```

### 📝 GET `/status/history`
Get recent TTS request history.
**Query Parameters:**
  * `limit` (integer): Number of records to return (1-50, default: 10)


**Example:**

```
curl "http://localhost:4123/status/history?limit=5"

```

**Response:**

```
{
  "request_history": [
    {
      "request_id": "abc12345",
      "status": "completed",
      "start_time": 1704067200.0,
      "end_time": 1704067203.5,
      "duration_seconds": 3.5,
      "text_length": 156,
      "text_preview": "Hello world, this is a test...",
      "voice_source": "default",
      "parameters": {
        "exaggeration": 0.7,
        "cfg_weight": 0.5,
        "temperature": 0.8
      }
    }
  ],
  "total_records": 5,
  "limit": 5
}

```

### 🗑️ POST `/status/history/clear`
Clear TTS request history.
**Query Parameters:**
  * `confirm` (boolean): Required confirmation flag


**Example:**

```
curl -X POST "http://localhost:4123/status/history/clear?confirm=true"

```

### 📋 GET `/info`
Get comprehensive API information including status, memory, and statistics.
**Example:**

```
curl "http://localhost:4123/info"

```

**Response:**

```
{
  "api_name": "Chatterbox TTS API",
  "version": "1.0.0",
  "status": "operational",
  "tts_status": {
    /* current status */
  },
  "statistics": {
    /* processing stats */
  },
  "memory_info": {
    /* memory usage */
  },
  "recent_requests": [
    /* last 3 requests */
  ],
  "uptime_info": {
    "total_requests": 42,
    "success_rate": 90.5,
    "is_processing": false
  }
}

```

## Status Values
The `status` field can have these values:
  * `idle`: No active requests
  * `initializing`: Starting request processing
  * `processing_text`: Validating and preparing text
  * `chunking`: Splitting text into chunks
  * `generating_audio`: Generating audio for chunks
  * `concatenating`: Combining audio chunks
  * `finalizing`: Converting to output format
  * `completed`: Request completed successfully
  * `error`: Request failed with error


## Endpoint Aliases
All endpoints support multiple path formats for compatibility:
| Primary Path  | Aliases  |
| --- | --- |
| `/status`  |  `/v1/status`, `/processing`, `/processing/status`  |
| `/status/progress`  |  `/v1/status/progress`, `/progress`  |
| `/status/history`  |  `/v1/status/history`, `/history`  |
| `/status/statistics`  |  `/v1/status/statistics`, `/stats`  |
| `/info`  |  `/v1/info`, `/api/info`  |
## Frontend Integration
### Real-time Progress Monitoring

```
import { createTTSService } from './services/tts';

const ttsService = createTTSService('http://localhost:4123');

// Monitor progress during generation
const monitorProgress = async () => {
  const interval = setInterval(async () => {
    try {
      const progress = await ttsService.getProgress();
      if (progress.is_processing) {
        console.log(`Progress: ${progress.progress_percentage}%`);
        console.log(`Step: ${progress.current_step}`);
      } else {
        clearInterval(interval);
        console.log('Processing complete');
      }
    } catch (error) {
      console.error('Failed to get progress:', error);
    }
  }, 1000);
};

```

### React Hook Example

```
import { useQuery } from '@tanstack/react-query';

const useProcessingStatus = () => {
  return useQuery({
    queryKey: ['tts-status'],
    queryFn: () => ttsService.getProgress(),
    refetchInterval: 1000, // Poll every second
    enabled: true,
  });
};

// Usage in component
const { data: status } = useProcessingStatus();
if (status?.is_processing) {
  // Show progress UI
}

```

## Testing
Run the status endpoint tests:

```
python tests/test_status.py

```

This will test:
  * ✅ All status endpoints
  * 🎤 Status tracking during TTS generation
  * 🔄 Concurrent request handling
  * 📊 Real-time progress monitoring


## Notes
  * Status information is thread-safe for concurrent requests
  * Progress percentages are calculated based on chunk processing
  * Memory information requires memory monitoring to be enabled
  * History is limited to the last 10 requests by default
  * Estimated completion times are calculated based on current progress


## Error Handling
All endpoints return appropriate HTTP status codes:
  * `200`: Success
  * `400`: Bad request (invalid parameters)
  * `500`: Internal server error


Error responses follow this format:

```
{
  "error": {
    "message": "Error description",
    "type": "error_type"
  }
}

```

[Star on GitHub](https://github.com/travisvn/chatterbox-tts-api)
© 2026 Chatterbox TTS API
Not affiliated with Resemble AI
[Join our Discord](https://chatterboxtts.com/discord)[View on GitHub](https://github.com/travisvn/chatterbox-tts-api)


--- DOCUMENT: https://chatterboxtts.com/docs/streaming-api ---
# Streaming TTS API Documentation
## 🎵 Overview
The Chatterbox TTS API supports real-time audio streaming, allowing clients to receive audio data as it's generated rather than waiting for complete processing. This significantly reduces perceived latency and improves user experience, especially for longer texts.
## ✨ Key Benefits
  * **Lower Latency** : Start receiving audio before full generation is complete
  * **Better User Experience** : Perceived faster response times for long texts
  * **Resource Efficiency** : Lower memory usage as chunks are processed individually
  * **Real-time Processing** : Audio generation happens progressively
  * **Interruption Support** : Can potentially stop generation mid-stream if needed
  * **Memory Optimization** : Automatic cleanup of processed chunks


## 🚀 Streaming Endpoints
### Basic Streaming
**POST** `/audio/speech/stream`
Generate and stream speech audio in real-time using the configured voice sample.
**Request Body (JSON):**

```
{
  "input": "Text to convert to speech",
  "exaggeration": 0.7,
  "cfg_weight": 0.4,
  "temperature": 0.9,
  "streaming_chunk_size": 200,
  "streaming_strategy": "sentence"
}

```

### Server-Side Events (SSE) Streaming
**POST** `/audio/speech`
Generate speech using Server-Side Events format (OpenAI compatible) by setting `stream_format` to `"sse"`.
**Request Body (JSON):**

```
{
  "input": "Text to convert to speech",
  "stream_format": "sse",
  "exaggeration": 0.7,
  "cfg_weight": 0.4,
  "temperature": 0.9,
  "streaming_chunk_size": 200,
  "streaming_strategy": "sentence"
}

```

**Response Format:** Returns `text/event-stream` with JSON events:

```
data: {"type": "speech.audio.delta", "audio": "base64_encoded_audio_chunk"}

data: {"type": "speech.audio.delta", "audio": "base64_encoded_audio_chunk"}

data: {"type": "speech.audio.done", "usage": {"input_tokens": 10, "output_tokens": 150, "total_tokens": 160}}

```

### Streaming with Voice Upload
**POST** `/audio/speech/stream/upload`
Generate and stream speech audio with optional custom voice file upload.
**Request (Multipart Form):**
  * `input` (string): Text to convert to speech
  * `voice_file` (file, optional): Custom voice sample file
  * `exaggeration` (float, optional): Emotion intensity (0.25-2.0)
  * `cfg_weight` (float, optional): Pace control (0.0-1.0)
  * `temperature` (float, optional): Sampling randomness (0.05-5.0)
  * `streaming_chunk_size` (int, optional): Characters per streaming chunk
  * `streaming_strategy` (string, optional): Chunking strategy


## 🎛️ Streaming Parameters
### Core TTS Parameters
| Parameter  | Type  | Range  | Default  | Description  |
| --- | --- | --- | --- | --- |
| `exaggeration`  | float  | 0.25-2.0  | 0.5  | Emotion intensity  |
| `cfg_weight`  | float  | 0.0-1.0  | 0.5  | Pace control  |
| `temperature`  | float  | 0.05-5.0  | 0.8  | Sampling randomness  |
### Streaming-Specific Parameters
| Parameter  | Type  | Options  | Default  | Description  |
| --- | --- | --- | --- | --- |
| `streaming_chunk_size`  | int  | 50-500  | 200  | Characters per streaming chunk  |
| `streaming_strategy`  | string  | sentence, paragraph, fixed, word  | "sentence"  | How to break up text for streaming  |
| `streaming_buffer_size`  | int  | 1-10  | 3  | Number of chunks to buffer  |
| `streaming_quality`  | string  | fast, balanced, high  | "balanced"  | Speed vs quality trade-off  |
## 📝 Streaming Strategies
### Sentence Strategy (Default)

```
{
  "streaming_strategy": "sentence",
  "streaming_chunk_size": 200
}

```

  * Splits at sentence boundaries (`.`, `!`, `?`)
  * Respects sentence integrity
  * Good balance of latency and naturalness
  * **Best for** : General use, reading content


### Paragraph Strategy

```
{
  "streaming_strategy": "paragraph",
  "streaming_chunk_size": 400
}

```

  * Splits at paragraph breaks (`\n\n`, double line breaks)
  * Maintains paragraph context
  * Longer chunks, more natural flow
  * **Best for** : Articles, stories, structured content


### Fixed Strategy

```
{
  "streaming_strategy": "fixed",
  "streaming_chunk_size": 150
}

```

  * Fixed character count chunks
  * Predictable timing
  * May break mid-sentence
  * **Best for** : Consistent streaming timing, testing


### Word Strategy

```
{
  "streaming_strategy": "word",
  "streaming_chunk_size": 100
}

```

  * Splits at word boundaries
  * Very fine-grained streaming
  * Maximum responsiveness
  * **Best for** : Real-time chat, interactive applications


## 🎯 Quality vs Speed Settings
### Fast Mode

```
{
  "streaming_quality": "fast",
  "streaming_chunk_size": 100,
  "streaming_strategy": "word"
}

```

  * Smaller chunks for faster initial response
  * Lower quality synthesis parameters
  * **Use case** : Chat applications, real-time feedback


### Balanced Mode (Default)

```
{
  "streaming_quality": "balanced",
  "streaming_chunk_size": 200,
  "streaming_strategy": "sentence"
}

```

  * Good balance of speed and quality
  * Sentence-aware chunking
  * **Use case** : General applications


### High Quality Mode

```
{
  "streaming_quality": "high",
  "streaming_chunk_size": 300,
  "streaming_strategy": "paragraph"
}

```

  * Larger chunks for better context
  * Higher quality synthesis
  * **Use case** : Audiobooks, professional content


## 💻 Usage Examples
### Basic cURL Examples
**Simple Streaming:**

```
curl -X POST http://localhost:4123/v1/audio/speech/stream \
  -H "Content-Type: application/json" \
  -d '{"input": "This will stream as it generates!"}' \
  --output streaming.wav

```

**SSE Streaming (OpenAI Compatible):**

```
curl -X POST http://localhost:4123/v1/audio/speech \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -d '{"input": "This streams as Server-Side Events!", "stream_format": "sse"}' \
  --no-buffer

```

**Advanced Streaming with Custom Settings:**

```
curl -X POST http://localhost:4123/v1/audio/speech/stream \
  -H "Content-Type: application/json" \
  -d '{
    "input": "Long text that will be streamed efficiently...",
    "exaggeration": 0.8,
    "streaming_strategy": "sentence",
    "streaming_chunk_size": 150,
    "streaming_quality": "balanced"
  }' \
  --output advanced_stream.wav

```

**Real-time Playback:**

```
curl -X POST http://localhost:4123/v1/audio/speech/stream \
  -H "Content-Type: application/json" \
  -d '{"input": "Play this as it streams!", "streaming_quality": "fast"}' \
  | ffplay -f wav -i pipe:0 -autoexit -nodisp

```

### Python Examples
#### Basic Streaming

```
import requests

response = requests.post(
    "http://localhost:4123/v1/audio/speech/stream",
    json={
        "input": "This streams as it's generated!",
        "streaming_strategy": "sentence",
        "streaming_chunk_size": 200
    },
    stream=True
)

# The response is a single, continuous WAV stream.
# You can write it directly to a file.
with open("streaming_output.wav", "wb") as f:
    for chunk in response.iter_content(chunk_size=8192):
        if chunk:
            f.write(chunk)
            print(f"Received chunk: {len(chunk)} bytes")

```

#### SSE Streaming (OpenAI Compatible)

```
import requests
import json
import base64
import wave
import io

def create_wav_from_pcm(pcm_data, sample_rate, channels, bits_per_sample):
    """Creates a WAV file in memory from raw PCM data."""
    wav_file = io.BytesIO()
    with wave.open(wav_file, 'wb') as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(bits_per_sample // 8)
        wf.setframerate(sample_rate)
        wf.writeframes(pcm_data)
    wav_file.seek(0)
    return wav_file.getvalue()

response = requests.post(
    "http://localhost:4123/v1/audio/speech",
    json={
        "input": "This streams as Server-Side Events with raw audio!",
        "stream_format": "sse"
    },
    stream=True,
    headers={'Accept': 'text/event-stream'}
)

audio_chunks = []
audio_info = {}

for line in response.iter_lines(decode_unicode=True):
    if line.startswith('data: '):
        event_data = line[6:]

        try:
            event = json.loads(event_data)

            # First event contains audio metadata
            if event.get('type') == 'speech.audio.info':
                audio_info = {
                    "sample_rate": event['sample_rate'],
                    "channels": event['channels'],
                    "bits_per_sample": event['bits_per_sample']
                }
                print(f"Received audio info: {audio_info}")

            # Subsequent events contain raw audio data
            elif event.get('type') == 'speech.audio.delta':
                audio_data = base64.b64decode(event['audio'])
                audio_chunks.append(audio_data)
                print(f"Received audio chunk: {len(audio_data)} bytes")

            # Final event indicates completion
            elif event.get('type') == 'speech.audio.done':
                usage = event.get('usage', {})
                print(f"Streaming complete. Usage: {usage}")
                break

        except json.JSONDecodeError:
            continue

# Combine raw PCM data and create a valid WAV file
if audio_chunks and audio_info:
    combined_pcm_data = b"".join(audio_chunks)

    wav_data = create_wav_from_pcm(
        combined_pcm_data,
        sample_rate=audio_info['sample_rate'],
        channels=audio_info['channels'],
        bits_per_sample=audio_info['bits_per_sample']
    )

    with open("sse_output.wav", "wb") as f:
        f.write(wav_data)
    print(f"Saved {len(audio_chunks)} audio chunks to sse_output.wav")
else:
    print("No audio data was received.")

```

#### Real-time Playback with sounddevice

```
import requests
import sounddevice as sd
import wave
import io

def stream_and_play_realtime(text, **params):
    """Stream TTS and play audio in real-time using sounddevice"""

    print("Requesting audio stream...")
    # Start streaming request
    response = requests.post(
        "http://localhost:4123/v1/audio/speech/stream",
        json={"input": text, **params},
        stream=True
    )

    if response.status_code != 200:
        print(f"Error from server: {response.status_code}")
        print(response.text)
        return

    # The first part of the stream is the WAV header.
    # We can read it to determine the audio format.
    try:
        header = response.raw.read(44)
    except Exception as e:
        print(f"Failed to read header from stream: {e}")
        return

    # Use the header to get audio properties
    try:
        with wave.open(io.BytesIO(header)) as wf:
            channels = wf.getnchannels()
            samplerate = wf.getframerate()
            sampwidth = wf.getsampwidth()

            # Map sample width to numpy dtype
            if sampwidth == 2:
                dtype = 'int16'
            elif sampwidth == 1:
                dtype = 'int8'
            elif sampwidth == 3: # 24-bit
                dtype = 'int24'
            elif sampwidth == 4:
                dtype = 'int32'
            else:
                raise ValueError(f"Unsupported sample width: {sampwidth}")

            print(f"Audio stream info: {samplerate}Hz, {channels}ch, {dtype}")
    except Exception as e:
        print(f"Failed to parse WAV header: {e}")
        return

    # Create and start the output stream
    try:
        with sd.RawOutputStream(
            samplerate=samplerate,
            channels=channels,
            dtype=dtype
        ) as stream:
            print("Playback started... press Ctrl+C to stop.")
            # Read the rest of the stream (raw PCM data) and play it
            while True:
                chunk = response.raw.read(1024)
                if not chunk:
                    break
                stream.write(chunk)
            print("Playback finished.")
    except Exception as e:
        print(f"An error occurred during playback: {e}")
    except KeyboardInterrupt:
        print("\nPlayback stopped by user.")


# Usage
# Note: You may need to install sounddevice: pip install sounddevice
stream_and_play_realtime(
    "This plays in real-time as it streams using the sounddevice library!",
    streaming_quality="fast"
)

```

### JavaScript/TypeScript Examples
#### Basic Streaming

```
async function streamTTS(text: string, options: any = {}) {
  const response = await fetch('/v1/audio/speech/stream', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      input: text,
      streaming_strategy: 'sentence',
      streaming_chunk_size: 200,
      ...options,
    }),
  });

  const reader = response.body?.getReader();
  const chunks: Uint8Array[] = [];

  while (true) {
    const { done, value } = await reader!.read();
    if (done) break;

    chunks.push(value);
    console.log(`Received chunk: ${value.length} bytes`);
  }

  // Combine chunks into final audio
  const totalLength = chunks.reduce((sum, chunk) => sum + chunk.length, 0);
  const audioData = new Uint8Array(totalLength);
  let offset = 0;

  for (const chunk of chunks) {
    audioData.set(chunk, offset);
    offset += chunk.length;
  }

  return audioData;
}

```

#### Real-time Audio Playback

```
async function streamAndPlayTTS(text: string) {
  const audio = new Audio();
  const mediaSource = new MediaSource();
  audio.src = URL.createObjectURL(mediaSource);
  audio.play().catch((e) => console.error('Autoplay was prevented:', e));

  mediaSource.addEventListener(
    'sourceopen',
    async () => {
      // The MIME type for WAV audio is 'audio/wav'. For MSE, specifying codecs
      // can be helpful, e.g., 'audio/wav; codecs=1' for PCM.
      const sourceBuffer = mediaSource.addSourceBuffer('audio/wav');

      try {
        const response = await fetch('/v1/audio/speech/stream', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            input: text,
            streaming_quality: 'fast',
          }),
        });

        const reader = response.body!.getReader();

        while (true) {
          const { done, value } = await reader.read();
          if (done) {
            // Ensure all buffered data is processed before ending the stream
            if (!sourceBuffer.updating && mediaSource.readyState === 'open') {
              mediaSource.endOfStream();
            }
            break;
          }

          // Wait for previous append to finish
          if (sourceBuffer.updating) {
            await new Promise((resolve) =>
              sourceBuffer.addEventListener('updateend', resolve, {
                once: true,
              })
            );
          }
          sourceBuffer.appendBuffer(value);
        }
      } catch (e) {
        console.error('Streaming failed:', e);
        if (mediaSource.readyState === 'open' && !sourceBuffer.updating) {
          mediaSource.endOfStream();
        }
      }
    },
    { once: true }
  );
}

```

## 📊 Performance Optimization
### Choosing Optimal Settings
**For Lowest Latency:**

```
{
  "streaming_quality": "fast",
  "streaming_strategy": "word",
  "streaming_chunk_size": 80,
  "streaming_buffer_size": 1
}

```

**For Best Quality:**

```
{
  "streaming_quality": "high",
  "streaming_strategy": "paragraph",
  "streaming_chunk_size": 350,
  "streaming_buffer_size": 5
}

```

**For Balanced Performance:**

```
{
  "streaming_quality": "balanced",
  "streaming_strategy": "sentence",
  "streaming_chunk_size": 200,
  "streaming_buffer_size": 3
}

```

### Memory Optimization
The streaming implementation includes automatic memory management:
  * Chunks are processed and freed immediately
  * GPU memory is cleared periodically
  * Temporary files are cleaned up automatically
  * Progress tracking prevents memory leaks


## 🔄 Progress Monitoring
### Real-time Progress API
While streaming is active, you can monitor progress:

```
curl "http://localhost:4123/v1/status/progress"

```

**Response:**

```
{
  "is_processing": true,
  "status": "generating_audio",
  "current_step": "Streaming audio for chunk 3/8",
  "current_chunk": 3,
  "total_chunks": 8,
  "progress_percentage": 37.5,
  "duration_seconds": 2.1,
  "estimated_completion": 1704067205.0,
  "text_preview": "This is the text being streamed..."
}

```

### Integration with Frontend

```
// Monitor streaming progress
const monitorStreaming = async () => {
  const interval = setInterval(async () => {
    try {
      const response = await fetch('/v1/status/progress');
      const progress = await response.json();

      if (progress.is_processing) {
        updateProgressBar(progress.progress_percentage);
        updateStatus(progress.current_step);
      } else {
        clearInterval(interval);
        onStreamingComplete();
      }
    } catch (error) {
      console.error('Progress monitoring failed:', error);
    }
  }, 500);
};

```

## 🛠️ Troubleshooting
### Common Issues
**Streaming Stops Unexpectedly:**
  * Check network stability
  * Verify streaming headers are set correctly
  * Ensure client supports chunked transfer encoding


**Audio Quality Issues:**
  * Try larger `streaming_chunk_size`
  * Use "sentence" or "paragraph" strategy
  * Increase `streaming_quality` to "balanced" or "high"


**High Latency:**
  * Reduce `streaming_chunk_size`
  * Use "word" strategy for maximum responsiveness
  * Set `streaming_quality` to "fast"


**Memory Issues:**
  * Reduce `streaming_buffer_size`
  * Use smaller `streaming_chunk_size`
  * Monitor memory usage via `/memory` endpoint


### Debugging Commands

```
# Test streaming endpoint
curl -v -X POST http://localhost:4123/v1/audio/speech/stream \
  -H "Content-Type: application/json" \
  -d '{"input": "Test streaming"}' \
  --output debug_stream.wav

# Monitor memory during streaming
watch -n 1 'curl -s http://localhost:4123/memory | jq .memory_info'

# Check streaming progress
watch -n 0.5 'curl -s http://localhost:4123/v1/status/progress | jq .'

```

## 🔄 Comparison: Streaming vs Standard
### When to Use Streaming
**Use Streaming When:**
  * Text length > 500 characters
  * Building real-time applications
  * Memory usage is a concern
  * Users expect immediate audio feedback
  * Implementing chat or interactive features


**Use Standard When:**
  * Text length < 200 characters
  * Need complete audio file before processing
  * Working with simple integrations
  * Bandwidth is limited
  * Processing batch content


### Performance Comparison
| Aspect  | Standard Generation  | Streaming Generation  |
| --- | --- | --- |
| **Initial Latency**  | Full generation time  | ~1-2 seconds  |
| **Memory Usage**  | Peak during concat  | Constant low usage  |
| **User Experience**  | Wait then play  | Progressive playback  |
| **Network Usage**  | Single large transfer  | Multiple small chunks  |
| **Complexity**  | Simple  | Moderate  |
## 🚀 Future Enhancements
Planned improvements to the streaming functionality:
  * **Adaptive Chunking** : Automatically adjust chunk size based on content
  * **Quality Adaptation** : Dynamic quality adjustment based on network conditions
  * **Interruption Support** : Ability to stop streaming mid-generation
  * **Buffer Prediction** : Intelligent buffering based on generation speed
  * **Multi-voice Streaming** : Stream different voices for different speakers
  * **WebSocket Support** : Real-time bidirectional streaming


## 📖 API Reference
For complete API documentation including all endpoints, parameters, and examples, visit:
  * **Interactive Documentation** : <http://localhost:4123/docs>
  * **Alternative Documentation** : <http://localhost:4123/redoc>
  * **OpenAPI Schema** : <http://localhost:4123/openapi.json>


The streaming endpoints are fully documented with request/response schemas, parameter validation, and example payloads.
[Star on GitHub](https://github.com/travisvn/chatterbox-tts-api)
© 2026 Chatterbox TTS API
Not affiliated with Resemble AI
[Join our Discord](https://chatterboxtts.com/discord)[View on GitHub](https://github.com/travisvn/chatterbox-tts-api)


--- DOCUMENT: https://chatterboxtts.com/docs/uv-migration ---
# Migration Guide: From pip to uv
This guide explains how to migrate the Chatterbox TTS FastAPI from pip to uv for better dependency management, faster installations, and improved PyTorch/CUDA compatibility.
## Why Migrate to uv?
Based on user feedback and testing, uv provides several advantages for this project:
  1. **Better PyTorch/CUDA handling** : Native support for PyTorch indexes and variants
  2. **Faster installations** : 25-40% faster than pip in benchmarks
  3. **Superior dependency resolution** : SAT-based resolver prevents conflicts
  4. **Git dependency support** : Better handling of `chatterbox-tts` from GitHub
  5. **Cross-platform consistency** : Environment markers handle CPU/GPU variants automatically
  6. **Docker optimizations** : Better caching and faster container builds
  7. **FastAPI compatibility** : Excellent support for FastAPI and Pydantic dependencies


## FastAPI + uv Benefits
The combination of FastAPI and uv provides:
  * **Faster builds** : uv resolves FastAPI dependencies more efficiently
  * **Better type checking** : Enhanced support for Pydantic and type hint libraries
  * **Cleaner environments** : More reliable async dependency management
  * **Development speed** : Faster dependency installation during development


## Docker GPU Issues (Fixed)
**Previous Problem** : The original uv Docker implementations were failing because:
  1. **Missing CUDA Index** : `pyproject.toml` only defined CPU PyTorch indexes
  2. **Incorrect Configuration** : Assumed PyTorch would "auto-detect CUDA" (which doesn't work with uv)
  3. **Complex Index Logic** : Overly complicated platform markers that didn't work reliably
  4. **Missing Dependency** : `resemble-perth` watermarker dependency was not explicitly included


**Solution Implemented** : The fixed uv Dockerfiles now:
  1. **Explicit PyTorch Installation** : Install PyTorch with correct CUDA/CPU versions first
  2. **Direct Index Usage** : Use `uv pip install` with explicit `--index-url` flags
  3. **Simplified Configuration** : Removed complex pyproject.toml index configurations
  4. **Complete Dependencies** : Added `resemble-perth` for watermarker functionality
  5. **FastAPI Optimization** : Optimized for FastAPI and async dependencies


**Fixed Commands** :

```
# GPU version (Dockerfile.uv.gpu)
RUN uv venv --python 3.11 && \
    uv pip install torch==2.6.0 torchvision==0.21.0 torchaudio==2.6.0 --index-url https://download.pytorch.org/whl/cu124 && \
    uv pip install resemble-perth && \
    uv pip install "chatterbox-tts @ git+https://github.com/resemble-ai/chatterbox.git@v0.1.2" && \
    uv pip install fastapi uvicorn[standard] python-dotenv requests

# CPU version (Dockerfile.uv)
RUN uv venv --python 3.11 && \
    uv pip install torch==2.6.0 torchvision==0.21.0 torchaudio==2.6.0 --index-url https://download.pytorch.org/whl/cpu && \
    uv pip install resemble-perth && \
    uv pip install "chatterbox-tts @ git+https://github.com/resemble-ai/chatterbox.git@v0.1.2" && \
    uv pip install fastapi uvicorn[standard] python-dotenv requests

```

**Common Error Fixed** :

```
TypeError: 'NoneType' object is not callable
self.watermarker = perth.PerthImplicitWatermarker()

```

This was caused by missing `resemble-perth` package that provides the watermarker functionality.
## Pre-Migration Checklist
  * Backup your current `.venv` directory (if using virtual environments)
  * Note your current Python version (`python --version`)
  * Save current package versions (`pip freeze > backup-requirements.txt`)
  * Check if you're using the Flask or FastAPI version (this guide assumes FastAPI)


## Step 1: Install uv
### macOS/Linux:

```
curl -LsSf https://astral.sh/uv/install.sh | sh

```

### Windows:

```
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

```

### Alternative (via pip):

```
pip install uv

```

## Step 2: Local Development Migration
### Option A: Quick Migration (Recommended)
  1. **Remove old virtual environment** :

```
rm -rf .venv

```

  2. **Install dependencies with uv** :

```
uv sync

```

  3. **Test the installation** :

```
uv run python -c "import chatterbox; print('✓ chatterbox-tts installed')"
uv run python -c "import torch; print(f'✓ PyTorch {torch.__version__} - CUDA: {torch.cuda.is_available()}')"
uv run python -c "import fastapi; print(f'✓ FastAPI {fastapi.__version__}')"

```

  4. **Run the FastAPI server** :

```
uv run uvicorn app.main:app --host 0.0.0.0 --port 4123
# or
uv run main.py

```


### Option B: Manual Migration
  1. **Initialize uv project** (if you want to customize):

```
uv init --no-readme --no-workspace

```

  2. **Add dependencies** :

```
uv add "chatterbox-tts @ git+https://github.com/resemble-ai/chatterbox.git@v0.1.2"
uv add "torch>=2.0.0,<2.7.0"
uv add "torchaudio>=2.0.0,<2.7.0"
uv add "fastapi>=0.104.0"
uv add "uvicorn[standard]>=0.24.0"
uv add "pydantic>=2.0.0"
uv add "python-dotenv>=1.0.0"
uv add "requests>=2.28.0" --optional dev

```


## Step 3: PyTorch Configuration
The provided `pyproject.toml` automatically handles PyTorch variants:
  * **Linux** : Uses CUDA-enabled PyTorch
  * **macOS/Windows** : Uses CPU-only PyTorch
  * **Manual override** : Set environment variables if needed


### Force CPU version:

```
UV_EXTRA_INDEX_URL=https://download.pytorch.org/whl/cpu uv sync

```

### Force CUDA version:

```
UV_EXTRA_INDEX_URL=https://download.pytorch.org/whl/cu124 uv sync

```

## Step 4: Docker Migration
### Using the new uv-based Docker setup:
  1. **Build with uv** :

```
docker build -f Dockerfile.uv -t chatterbox-tts-uv .

```

  2. **Or use docker-compose** :

```
docker-compose -f docker-compose.uv.yml up -d

```

  3. **GPU variant** :

```
docker build -f Dockerfile.uv.gpu -t chatterbox-tts-uv-gpu .

```


## Step 5: Verify Migration
### Test basic functionality:

```
# Health check
uv run python -c "
import requests
r = requests.get('http://localhost:4123/health')
print(f'Status: {r.status_code}')
print(r.json())
"

# Test FastAPI documentation
uv run python -c "
import requests
r = requests.get('http://localhost:4123/docs')
print(f'Docs available: {r.status_code == 200}')
"

# Test TTS generation
uv run python tests/test_api.py

```

### Performance comparison:

```
# Time the installation
time uv sync --reinstall
# vs
time pip install -r requirements.txt

```

## Step 6: Update Development Workflow
### New commands:
| Old pip command  | New uv command  |
| --- | --- |
| `pip install package`  | `uv add package`  |
| `pip install -r requirements.txt`  | `uv sync`  |
| `python script.py`  | `uv run script.py`  |
| `pip freeze`  | `uv pip freeze`  |
| `flask run --debug`  | N/A (now FastAPI)  |
| `python main.py`  | `uv run main.py`  |
### FastAPI with uv commands:

```
# Start FastAPI development server
uv run uvicorn app.main:app --host 0.0.0.0 --port 4123 --reload

# Run with specific Python version
uv run --python 3.11 uvicorn app.main:app --reload

# Install development dependencies (basic tools)
uv sync

# Install test dependencies (for testing/contributing)
uv sync --group test

```

### Environment management:

```
# Create/sync environment
uv sync

# Add new dependency
uv add numpy

# Remove dependency
uv remove numpy

# Update all dependencies
uv sync --upgrade

# Install dev dependencies (basic development tools)
uv sync

# Install test dependencies (for contributors/testing)
uv sync --group test

```

## Step 7: CI/CD Updates
Update your CI/CD pipelines to use uv with FastAPI:

```
# GitHub Actions example
- name: Set up uv
  uses: astral-sh/setup-uv@v2

- name: Install dependencies
  run: uv sync

- name: Run tests
  run: uv run python tests/test_api.py

- name: Test FastAPI endpoints
  run: |
    uv run uvicorn api:app --host 0.0.0.0 --port 4123 &
    sleep 10
    curl -f http://localhost:4123/health
    curl -f http://localhost:4123/docs

```

## Troubleshooting
### Common Issues:
  1. **CUDA compatibility** :

```
# Clear cache and reinstall
uv cache clean
uv sync --reinstall

```

  2. **Git dependency issues** :

```
# Force refresh git dependencies
uv sync --refresh-package chatterbox-tts

```

  3. **Lock file conflicts** :

```
# Regenerate lock file
rm uv.lock
uv sync

```

  4. **Python version mismatch** :

```
# Use specific Python version
uv python install 3.11
uv sync --python 3.11

```

  5. **FastAPI startup issues** :

```
# Check FastAPI dependencies
uv run python -c "import fastapi, uvicorn; print('FastAPI ready')"

# Run with verbose logging
uv run uvicorn api:app --log-level debug --reload

```


## Performance Benefits
Expected improvements after migration:
  * **Installation speed** : 25-40% faster
  * **Dependency resolution** : More reliable, fewer conflicts
  * **Docker builds** : 20-30% faster with better caching
  * **Development workflow** : Faster environment creation
  * **PyTorch compatibility** : Better handling of CUDA variants
  * **FastAPI performance** : Better async dependency management


## FastAPI + uv Specific Benefits
  * **Faster development cycles** : uv's speed + FastAPI's auto-reload
  * **Better type checking** : Enhanced IDE support for async functions
  * **Cleaner dependency trees** : uv resolves FastAPI/Pydantic dependencies better
  * **Improved testing** : Faster test environment setup


## Rollback Plan
If you need to rollback to pip:
  1. **Restore backup** :

```
pip install -r backup-requirements.txt

```

  2. **Remove uv files** :

```
rm pyproject.toml uv.lock

```

  3. **Use original Docker files** :

```
docker-compose -f docker-compose.yml up -d

```


Note: If you're rolling back from FastAPI to Flask, you'll need to restore the previous Flask version of the codebase.
## Additional Resources
  * [uv Documentation](https://docs.astral.sh/uv/)
  * [PyTorch with uv Guide](https://docs.astral.sh/uv/guides/integration/pytorch/)
  * [uv Docker Guide](https://docs.astral.sh/uv/guides/integration/docker/)
  * [FastAPI Documentation](https://fastapi.tiangolo.com/)
  * [FastAPI Deployment Guide](https://fastapi.tiangolo.com/deployment/)


## Support
If you encounter issues during migration:
  1. Check the [uv troubleshooting guide](https://docs.astral.sh/uv/reference/troubleshooting/)
  2. Check the [FastAPI documentation](https://fastapi.tiangolo.com/tutorial/)
  3. Open an issue with reproduction steps
  4. Include `uv.lock` and `pyproject.toml` files
  5. Provide error logs with `--verbose` flag


For FastAPI-specific issues, visit the interactive documentation at `http://localhost:4123/docs` once the server is running.
[Star on GitHub](https://github.com/travisvn/chatterbox-tts-api)
© 2026 Chatterbox TTS API
Not affiliated with Resemble AI
[Join our Discord](https://chatterboxtts.com/discord)[View on GitHub](https://github.com/travisvn/chatterbox-tts-api)


--- DOCUMENT: https://chatterboxtts.com/docs/voice-upload-summary ---
# Voice Upload Feature Implementation Summary
## 🎤 Overview
Successfully implemented voice file upload functionality for the Chatterbox TTS API, allowing users to upload custom voice samples per request while maintaining full backward compatibility.
## 📋 Changes Made
### 1. Core Dependencies Added
**python-multipart >=0.0.6** - Required for FastAPI multipart/form-data support
**Files Updated:**
  * `requirements.txt` - Added python-multipart dependency
  * `pyproject.toml` - Added python-multipart to project dependencies
  * All Docker files - Added python-multipart to pip install commands


### 2. Enhanced Speech Endpoint (`app/api/endpoints/speech.py`)
**New Features:**
  * ✅ **Voice file upload support** - Optional `voice_file` parameter
  * ✅ **Multiple endpoint formats** - Both JSON and form data support
  * ✅ **File validation** - Format, size, and content validation
  * ✅ **Temporary file handling** - Secure file processing with automatic cleanup
  * ✅ **Backward compatibility** - Existing JSON requests continue to work


**Supported File Formats:**
  * MP3 (.mp3)
  * WAV (.wav)
  * FLAC (.flac)
  * M4A (.m4a)
  * OGG (.ogg)
  * Maximum size: 10MB


**New Endpoints:**
  * `POST /v1/audio/speech` - Multipart form data (supports voice upload)
  * `POST /v1/audio/speech/json` - Legacy JSON endpoint (backward compatibility)


### 3. Comprehensive Testing
**New Test Files:**
  * `tests/test_voice_upload.py` - Dedicated voice upload testing
  * Updated `tests/test_api.py` - Tests both JSON and form data endpoints


**Test Coverage:**
  * ✅ Default voice (both endpoints)
  * ✅ Custom voice upload
  * ✅ File format validation
  * ✅ Error handling
  * ✅ Parameter validation
  * ✅ Backward compatibility


### 4. Updated Documentation
**README.md Updates:**
  * Added voice upload examples
  * Documented supported file formats
  * Provided usage examples in multiple languages (Python, cURL)
  * Added file requirements and best practices


## 🚀 Usage Examples
### Basic Usage (Default Voice)

```
# JSON (legacy)
curl -X POST http://localhost:4123/v1/audio/speech/json \
  -H "Content-Type: application/json" \
  -d '{"input": "Hello world!"}' \
  --output output.wav

# Form data (new)
curl -X POST http://localhost:4123/v1/audio/speech \
  -F "input=Hello world!" \
  --output output.wav

```

### Custom Voice Upload

```
curl -X POST http://localhost:4123/v1/audio/speech \
  -F "input=Hello with my custom voice!" \
  -F "exaggeration=0.8" \
  -F "voice_file=@my_voice.mp3" \
  --output custom_voice.wav

```

### Python Example

```
import requests

# With custom voice upload
with open("my_voice.mp3", "rb") as voice_file:
    response = requests.post(
        "http://localhost:4123/v1/audio/speech",
        data={
            "input": "Hello with my custom voice!",
            "exaggeration": 0.8,
            "temperature": 1.0
        },
        files={
            "voice_file": ("my_voice.mp3", voice_file, "audio/mpeg")
        }
    )

with open("output.wav", "wb") as f:
    f.write(response.content)

```

## 🐳 Docker Support
**All Docker files updated with python-multipart:**
  * `docker/Dockerfile` - Standard Docker image
  * `docker/Dockerfile.cpu` - CPU-only image
  * `docker/Dockerfile.gpu` - GPU-enabled image
  * `docker/Dockerfile.uv` - uv-optimized image
  * `docker/Dockerfile.uv.gpu` - uv + GPU image


**Docker Usage:**

```
# Build and run with voice upload support
docker compose -f docker/docker-compose.yml up -d

# Test voice upload
curl -X POST http://localhost:4123/v1/audio/speech \
  -F "input=Hello from Docker!" \
  -F "voice_file=@voice-sample.mp3" \
  --output docker_test.wav

```

## 🔧 Technical Implementation
### File Processing Flow
  1. **Upload** - Receive multipart form data with optional voice file
  2. **Validate** - Check file format, size, and content
  3. **Store** - Create temporary file with secure naming
  4. **Process** - Use uploaded file or default voice sample for TTS
  5. **Cleanup** - Automatically remove temporary files


### Memory Management
  * Temporary files are automatically cleaned up in `finally` blocks
  * File validation prevents oversized uploads
  * Secure temporary file creation with unique names


### Error Handling
  * File format validation with helpful error messages
  * File size limits (10MB maximum)
  * Graceful fallback to default voice on upload errors
  * Comprehensive error responses with error codes


## 🧪 Testing
### Quick Test

```
# Start the API
python main.py

# Run comprehensive tests
python tests/test_voice_upload.py
python tests/test_api.py

```

### Test Results Expected
  * ✅ Health check
  * ✅ API documentation endpoints
  * ✅ Legacy JSON endpoint compatibility
  * ✅ New form data endpoint
  * ✅ Voice file upload functionality
  * ✅ Error handling and validation


## 📚 API Documentation
The API documentation is automatically updated and available at:
  * **Swagger UI** : <http://localhost:4123/docs>
  * **ReDoc** : <http://localhost:4123/redoc>
  * **OpenAPI Schema** : <http://localhost:4123/openapi.json>


The documentation now includes:
  * Multipart form data support
  * File upload parameters
  * Example requests and responses
  * Error codes and descriptions


## ✅ Backward Compatibility
**100% backward compatible:**
  * Existing JSON requests work unchanged
  * All previous API behavior preserved
  * Legacy endpoint (`/v1/audio/speech/json`) maintains exact same interface
  * No breaking changes to existing functionality


## 🔐 Security Considerations
  * File type validation prevents malicious uploads
  * File size limits prevent DoS attacks
  * Temporary files use secure random naming
  * Automatic cleanup prevents file system bloat
  * No persistent storage of uploaded files


## 📈 Performance Impact
  * Minimal overhead for JSON requests (unchanged code path)
  * Temporary file I/O only when voice files are uploaded
  * Efficient memory management with automatic cleanup
  * FastAPI's built-in multipart handling is highly optimized


* * *
**Status: ✅ Complete and Production Ready**
The voice upload feature is fully implemented, tested, and documented. Users can now upload custom voice files for personalized text-to-speech generation while maintaining full backward compatibility with existing implementations.
[Star on GitHub](https://github.com/travisvn/chatterbox-tts-api)
© 2026 Chatterbox TTS API
Not affiliated with Resemble AI
[Join our Discord](https://chatterboxtts.com/discord)[View on GitHub](https://github.com/travisvn/chatterbox-tts-api)
