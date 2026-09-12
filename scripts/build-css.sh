#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TOOLS_DIR="$REPO_DIR/tools"
TAILWIND_VERSION="v4.3.3"
DAISYUI_VERSION="v5.7.37"

case "$(uname -s)-$(uname -m)" in
    Darwin-arm64)   TW_ASSET="tailwindcss-macos-arm64" ;;
    Darwin-x86_64)  TW_ASSET="tailwindcss-macos-x64" ;;
    Linux-aarch64)  TW_ASSET="tailwindcss-linux-arm64" ;;
    Linux-x86_64)   TW_ASSET="tailwindcss-linux-x64" ;;
    *) echo "Plateforme non geree : $(uname -s)-$(uname -m)" >&2; exit 1 ;;
esac

TW_BIN="$TOOLS_DIR/tailwindcss"
DAISYUI_PLUGIN="$TOOLS_DIR/daisyui.mjs"
DAISYUI_THEME_PLUGIN="$TOOLS_DIR/daisyui-theme.mjs"

mkdir -p "$TOOLS_DIR" "$REPO_DIR/static/css"

if [ ! -x "$TW_BIN" ]; then
    echo "Telechargement de Tailwind CSS $TAILWIND_VERSION ($TW_ASSET)..."
    curl -sSL -o "$TW_BIN" \
        "https://github.com/tailwindlabs/tailwindcss/releases/download/$TAILWIND_VERSION/$TW_ASSET"
    chmod +x "$TW_BIN"
fi

if [ ! -f "$DAISYUI_PLUGIN" ] || [ ! -f "$DAISYUI_THEME_PLUGIN" ]; then
    echo "Telechargement de daisyUI $DAISYUI_VERSION..."
    curl -sSL -o "$DAISYUI_PLUGIN" \
        "https://github.com/saadeghi/daisyui/releases/download/$DAISYUI_VERSION/daisyui.mjs"
    curl -sSL -o "$DAISYUI_THEME_PLUGIN" \
        "https://github.com/saadeghi/daisyui/releases/download/$DAISYUI_VERSION/daisyui-theme.mjs"
fi

echo "Build de static/css/app.css..."
"$TW_BIN" \
    --input "$REPO_DIR/static/src/input.css" \
    --output "$REPO_DIR/static/css/app.css" \
    --minify \
    "$@"
