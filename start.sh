#!/bin/zsh
set -euo pipefail

# start.sh
# Startet den sichtbaren Chrome-Browser über Tor-Proxy und zeigt die Exit-IP.

SCRIPT_DIR="$(cd "$(dirname "$0")" >/dev/null 2>&1 && pwd)"
echo "[start.sh] Script-Verzeichnis: $SCRIPT_DIR"
cd "$SCRIPT_DIR"

# Virtuelle Umgebung erstellen, falls nicht vorhanden
if [[ ! -d .venv ]]; then
  echo "[start.sh] Erstelle .venv..."
  python3 -m venv .venv
fi

# Aktivieren der virtuellen Umgebung
. .venv/bin/activate
echo "[start.sh] Python: $(python --version)"

# Pip aktualisieren
echo "[start.sh] Aktualisiere pip..."
pip install --upgrade pip

# Dependencies aus requirements.txt installieren
if [[ -f requirements.txt ]]; then
  echo "[start.sh] Installiere Abhängigkeiten aus requirements.txt..."
  pip install -r requirements.txt
else
  echo "[start.sh] Keine requirements.txt gefunden, überspringe Installation"
fi

# PYTHONPATH setzen
export PYTHONPATH="$SCRIPT_DIR"

# URL-Argument prüfen
if [[ $# -lt 1 ]]; then
  echo "Nutzung: ./start.sh <url>"
  exit 1
fi

URL_ARG="$1"

# Browser starten
echo "[start.sh] Starte Browser über Tor..."
python -m browser.run_browser "$URL_ARG"
