#!/usr/bin/env bash

# Colors for premium look
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Vision Caption Server AMD ROCm Launcher ===${NC}"

# Load .env if it exists
if [ -f .env ]; then
    echo -e "${GREEN}[INFO] Loading environment variables from .env${NC}"
    export $(grep -v '^#' .env | xargs)
fi

# Check for OpenRouter API Key
if [ -z "$OPENROUTER_API_KEY" ]; then
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

# Auto-detect ROCm library path
ROCM_LIB=""
if [ -d "/opt/rocm-7.2.3/lib" ]; then
    ROCM_LIB="/opt/rocm-7.2.3/lib"
elif [ -d "/opt/rocm/lib" ]; then
    ROCM_LIB="/opt/rocm/lib"
else
    # Look for any rocm-* library folder
    LATEST_ROCM=$(ls -d /opt/rocm-* 2>/dev/null | sort -V | tail -n 1)
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
TEST_GPU=$(uv run python -c "import torch; print(f'OK:{torch.cuda.is_available()}:{torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"None\"}')" 2>/dev/null)

if [[ "$TEST_GPU" == OK:True:* ]]; then
    GPU_NAME=$(echo "$TEST_GPU" | cut -d: -f3)
    echo -e "${GREEN}[SUCCESS] PyTorch successfully initialized ROCm GPU: $GPU_NAME${NC}"
else
    echo -e "${RED}[ERROR] PyTorch ROCm initialization failed or GPU not found. Running tests or server might fall back to CPU.${NC}"
fi

echo -e "${BLUE}[INFO] Starting Vision Caption server...${NC}"
echo ""
exec uv run python -m vision_caption "$@"
