#!/usr/bin/env bash

set -euo pipefail

BACKEND_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
FRONTEND_DIR="${FRONTEND_DIR:-$BACKEND_DIR/../TESI-Vision_Caption_Client}"
MINIMUM_COMMIT="cac6631"

if [ ! -d "$FRONTEND_DIR/.git" ]; then
    echo "Frontend repository not found: $FRONTEND_DIR" >&2
    echo "Clone it next to the backend before running this deploy command." >&2
    exit 1
fi

git -C "$FRONTEND_DIR" switch main
git -C "$FRONTEND_DIR" pull --ff-only

if ! git -C "$FRONTEND_DIR" merge-base --is-ancestor "$MINIMUM_COMMIT" HEAD; then
    echo "Frontend HEAD does not include required commit $MINIMUM_COMMIT." >&2
    exit 1
fi

npm --prefix "$FRONTEND_DIR" ci
npm --prefix "$FRONTEND_DIR" run build

test -f "$FRONTEND_DIR/dist/index.html"
echo "Frontend deployed at $FRONTEND_DIR/dist"
