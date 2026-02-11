#!/usr/bin/env bash
set -euo pipefail

# ============================================
# Mervellous — OpenClaw Multi-Agent Setup
# ============================================

MERVELLOUS_DIR="$(cd "$(dirname "$0")/.." && pwd)"
OPENCLAW_DIR="${HOME}/.openclaw"
INSTALL_DIR="${OPENCLAW_DIR}/mervellous"

echo "================================================"
echo "  Mervellous — Multi-Agent Framework Setup"
echo "================================================"
echo ""

# --- Check prerequisites ---
echo "[1/6] Checking prerequisites..."

if ! command -v node &>/dev/null; then
    echo "ERROR: Node.js is required (>= 22). Install it first."
    exit 1
fi

NODE_VERSION=$(node -v | sed 's/v//' | cut -d. -f1)
if [ "$NODE_VERSION" -lt 22 ]; then
    echo "ERROR: Node.js >= 22 required. Found: $(node -v)"
    exit 1
fi

if ! command -v openclaw &>/dev/null; then
    echo "OpenClaw not found. Installing..."
    npm install -g openclaw@latest
else
    echo "OpenClaw found: $(openclaw --version 2>/dev/null || echo 'installed')"
fi

echo "  OK"
echo ""

# --- Create directory structure ---
echo "[2/6] Creating directory structure..."

mkdir -p "${INSTALL_DIR}"
mkdir -p "${OPENCLAW_DIR}/credentials"

echo "  OK — ${INSTALL_DIR}"
echo ""

# --- Copy workspace files ---
echo "[3/6] Copying workspace files..."

AGENTS=("merv" "linus" "finch" "otto" "iris" "nova" "forge")

for agent in "${AGENTS[@]}"; do
    src="${MERVELLOUS_DIR}/workspace-${agent}"
    dest="${INSTALL_DIR}/workspace-${agent}"

    if [ -d "$src" ]; then
        mkdir -p "$dest"
        cp -r "$src"/* "$dest"/
        echo "  Copied workspace-${agent}"
    fi
done

echo "  OK"
echo ""

# --- Copy config ---
echo "[4/6] Setting up configuration..."

CONFIG_FILE="${OPENCLAW_DIR}/openclaw.json"

if [ -f "$CONFIG_FILE" ]; then
    echo "  WARNING: ${CONFIG_FILE} already exists."
    echo "  Backing up to ${CONFIG_FILE}.backup"
    cp "$CONFIG_FILE" "${CONFIG_FILE}.backup"
fi

cp "${MERVELLOUS_DIR}/openclaw.example.json" "$CONFIG_FILE"

echo "  Config written to ${CONFIG_FILE}"
echo "  IMPORTANT: Edit this file to add your API keys and tokens."
echo ""

# --- Setup environment ---
echo "[5/6] Setting up environment..."

ENV_FILE="${OPENCLAW_DIR}/.env"
if [ ! -f "$ENV_FILE" ]; then
    cp "${MERVELLOUS_DIR}/.env.example" "$ENV_FILE"
    echo "  Created ${ENV_FILE} — fill in your API keys"
else
    echo "  ${ENV_FILE} already exists, skipping"
fi

echo "  OK"
echo ""

# --- Register agents ---
echo "[6/6] Registering agents..."

echo ""
echo "================================================"
echo "  Setup Complete!"
echo "================================================"
echo ""
echo "Next steps:"
echo ""
echo "  1. Edit your config:"
echo "     nano ~/.openclaw/openclaw.json"
echo ""
echo "  2. Add your API key:"
echo "     openclaw auth add anthropic"
echo ""
echo "  3. Enable a channel (e.g., Telegram):"
echo "     - Set TELEGRAM_BOT_TOKEN in config"
echo "     - Set telegram.enabled to true"
echo ""
echo "  4. Validate your setup:"
echo "     openclaw doctor --fix"
echo ""
echo "  5. Start the gateway:"
echo "     openclaw gateway start"
echo ""
echo "  6. Test with CLI (no channel needed):"
echo "     openclaw chat"
echo ""
echo "Agents available:"
echo "  - Merv (orchestrator) — routes everything"
echo "  - Linus (coder) — writes code"
echo "  - Finch (researcher) — finds information"
echo "  - Otto (automation) — automates tasks"
echo "  - Iris (writer) — writes content"
echo "  - Nova (analyst) — analyzes data"
echo "  - Forge (devops) — manages infrastructure"
echo ""
