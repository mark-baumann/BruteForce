#!/bin/zsh
set -euo pipefail

# start.sh
# Startet den sichtbaren Chrome-Browser über Tor-Proxy und zeigt die Exit-IP.

SCRIPT_DIR="$(cd "$(dirname "$0")" >/dev/null 2>&1 && pwd)"
echo "[start.sh] Script-Verzeichnis: $SCRIPT_DIR"
cd "$SCRIPT_DIR"

if [[ ! -d .venv ]]; then
  echo "[start.sh] Erstelle .venv..."
  python3 -m venv .venv
fi
. .venv/bin/activate

echo "[start.sh] Python: $(python --version)"

echo "[start.sh] Aktualisiere pip/Deps (kann 1-2 Min dauern)..."
pip install --upgrade pip --no-input >/dev/null 2>&1 || true
pip install -r requirements.txt --no-input >/dev/null 2>&1 || true

export PYTHONPATH="$SCRIPT_DIR"

if [[ $# -lt 1 ]]; then
  echo "Nutzung: ./start.sh <url>"
  exit 1
fi

URL_ARG="$1"

echo "[start.sh] Starte Browser über Tor..."
python browser.py "$URL_ARG"

