#!/bin/bash
# Instala el Sonarr Agent como servicio systemd en la Raspberry Pi
# Uso: bash install_agent.sh TU_GITHUB_TOKEN

set -e

TOKEN="${1:-}"
if [ -z "$TOKEN" ]; then
    echo "Uso: bash install_agent.sh <GITHUB_TOKEN>"
    echo "El token necesita permisos: repo (Issues)"
    exit 1
fi

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
SERVICE_SRC="$REPO_DIR/sonarr_agent.service"
SERVICE_DST="/etc/systemd/system/sonarr-agent.service"

echo "→ Copiando servicio a $SERVICE_DST"
sudo cp "$SERVICE_SRC" "$SERVICE_DST"

echo "→ Aplicando token de GitHub"
sudo sed -i "s/TU_GITHUB_TOKEN_AQUI/$TOKEN/" "$SERVICE_DST"

echo "→ Actualizando ruta del script"
sudo sed -i "s|/home/pi/Mervellous|$REPO_DIR|g" "$SERVICE_DST"

echo "→ Habilitando e iniciando servicio"
sudo systemctl daemon-reload
sudo systemctl enable sonarr-agent
sudo systemctl start sonarr-agent

echo ""
echo "✓ Servicio instalado y activo."
echo "  Ver logs:   sudo journalctl -fu sonarr-agent"
echo "  Estado:     sudo systemctl status sonarr-agent"
echo "  Detener:    sudo systemctl stop sonarr-agent"
