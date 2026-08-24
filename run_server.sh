#!/usr/bin/env bash

set -euo pipefail

BACKEND_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd "$BACKEND_DIR"

# Colors for premium look
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Vision Caption Server AMD ROCm Launcher ===${NC}"

# Load .env if it exists
if [ -f "$BACKEND_DIR/.env" ]; then
    echo -e "${GREEN}[INFO] Loading environment variables from .env${NC}"
    set -a
    # shellcheck disable=SC1091
    source "$BACKEND_DIR/.env"
    set +a
fi

# Il servizio è raggiungibile soltanto dal tunnel locale. TLS termina su
# Cloudflare, quindi Uvicorn non espone porte sulla LAN e non carica certificati.
export SERVER_HOST="127.0.0.1"
export SERVER_PORT="${SERVER_PORT:-8765}"

FRONTEND_DIST_PATH="${FRONTEND_DIST_PATH:-$BACKEND_DIR/../TESI-Vision_Caption_Client/dist}"
if [[ "$FRONTEND_DIST_PATH" != /* ]]; then
    FRONTEND_DIST_PATH="$BACKEND_DIR/$FRONTEND_DIST_PATH"
fi
export FRONTEND_DIST_PATH

if [ ! -f "$FRONTEND_DIST_PATH/index.html" ]; then
    echo -e "${RED}[ERROR] Frontend build not found: $FRONTEND_DIST_PATH/index.html${NC}"
    echo -e "${YELLOW}[HINT] Run: $BACKEND_DIR/scripts/deploy_frontend.sh${NC}"
    exit 1
fi

# Check for OpenRouter API Key
if [ -z "${OPENROUTER_API_KEY:-}" ]; then
    echo -e "${YELLOW}[WARNING] OPENROUTER_API_KEY is not set. The server might fail in production mode unless set.${NC}"
fi

# Set AMD GFX override and visible device
export HSA_OVERRIDE_GFX_VERSION=${HSA_OVERRIDE_GFX_VERSION:-10.3.0}
export HIP_VISIBLE_DEVICES=${HIP_VISIBLE_DEVICES:-0}
export DEVICE=${DEVICE:-cuda}

echo -e "${GREEN}[INFO] AMD GPU configuration:${NC}"
echo -e "  - HSA_OVERRIDE_GFX_VERSION = $HSA_OVERRIDE_GFX_VERSION"
echo -e "  - HIP_VISIBLE_DEVICES      = $HIP_VISIBLE_DEVICES"
echo -e "  - DEVICE                   = $DEVICE"
echo -e "  - SERVER                   = http://$SERVER_HOST:$SERVER_PORT"
echo -e "  - FRONTEND_DIST_PATH       = $FRONTEND_DIST_PATH"

# Auto-detect ROCm library path
ROCM_LIB=""
if [ -d "/opt/rocm-7.2.3/lib" ]; then
    ROCM_LIB="/opt/rocm-7.2.3/lib"
elif [ -d "/opt/rocm/lib" ]; then
    ROCM_LIB="/opt/rocm/lib"
else
    # Look for any rocm-* library folder
    LATEST_ROCM=$(ls -d /opt/rocm-* 2>/dev/null | sort -V | tail -n 1 || true)
    if [ -n "$LATEST_ROCM" ] && [ -d "$LATEST_ROCM/lib" ]; then
        ROCM_LIB="$LATEST_ROCM/lib"
    fi
fi

if [ -n "$ROCM_LIB" ]; then
    echo -e "${GREEN}[INFO] Found ROCm libraries at: $ROCM_LIB${NC}"
    export LD_LIBRARY_PATH="$ROCM_LIB:${LD_LIBRARY_PATH:-}"
else
    echo -e "${YELLOW}[WARNING] No ROCm installation found in /opt. PyTorch will rely on system-default loader paths.${NC}"
fi

# Check if PyTorch can see the AMD GPU
echo -e "${BLUE}[INFO] Verifying PyTorch ROCm status...${NC}"
TEST_GPU=$(uv run python -c "import torch; print(f'OK:{torch.cuda.is_available()}:{torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"None\"}')" 2>/dev/null || true)

if [[ "$TEST_GPU" == OK:True:* ]]; then
    GPU_NAME=$(echo "$TEST_GPU" | cut -d: -f3)
    echo -e "${GREEN}[SUCCESS] PyTorch successfully initialized ROCm GPU: $GPU_NAME${NC}"
else
    echo -e "${RED}[ERROR] PyTorch ROCm initialization failed or GPU not found. Running tests or server might fall back to CPU.${NC}"
fi

echo -e "${BLUE}[INFO] Starting Vision Caption server...${NC}"
echo ""
exec uv run python -m vision_caption "$@"
