#!/bin/bash

# ===== Anonymer Browser mit Tor-Proxy =====
# Automatisches Start-Script
# 
# Funktionen:
# - Startet Tor automatisch
# - Öffnet Chrome mit Tor-Proxy
# - Zeigt IP-Adressen an
# - Ermöglicht IP-Wechsel

echo "🎭 === Anonymer Browser mit Tor-Proxy ==="
echo "📦 Initialisiere..."

# Wechsel ins Script-Verzeichnis
cd "$(dirname "$0")"

# Farben für die Ausgabe
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Funktion: Colored echo
color_echo() {
    color=$1
    shift
    echo -e "${color}$@${NC}"
}

# Prüfung: Homebrew installiert?
if ! command -v brew &> /dev/null; then
    color_echo $RED "❌ Homebrew nicht gefunden!"
    echo "   Installiere Homebrew: /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
    exit 1
fi

# Prüfung: Tor installiert?
if ! command -v tor &> /dev/null; then
    color_echo $YELLOW "⚠️  Tor nicht gefunden. Installiere Tor..."
    brew install tor
    if [ $? -ne 0 ]; then
        color_echo $RED "❌ Tor-Installation fehlgeschlagen!"
        exit 1
    fi
fi

# Prüfung: ChromeDriver installiert?
if ! command -v chromedriver &> /dev/null; then
    color_echo $YELLOW "⚠️  ChromeDriver nicht gefunden. Installiere ChromeDriver..."
    brew install chromedriver
    if [ $? -ne 0 ]; then
        color_echo $RED "❌ ChromeDriver-Installation fehlgeschlagen!"
        exit 1
    fi
fi

# Prüfung: Python Virtual Environment
if [ ! -d "venv" ]; then
    color_echo $YELLOW "⚠️  Virtual Environment nicht gefunden. Erstelle venv..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        color_echo $RED "❌ venv konnte nicht erstellt werden!"
        exit 1
    fi
fi

# Virtual Environment aktivieren
source venv/bin/activate

# Python-Pakete installieren
if [ ! -f "venv/.packages_installed" ]; then
    color_echo $BLUE "📦 Installiere Python-Pakete..."
    pip install -q --upgrade pip
    pip install -q -r requirements.txt
    if [ $? -eq 0 ]; then
        touch venv/.packages_installed
        color_echo $GREEN "✅ Pakete installiert"
    else
        color_echo $RED "❌ Paket-Installation fehlgeschlagen!"
        exit 1
    fi
else
    color_echo $GREEN "✅ Pakete bereits installiert"
fi

# Cleanup alte Prozesse
color_echo $BLUE "🧹 Bereinige alte Prozesse..."
pkill -f tor &> /dev/null
sleep 2

echo ""
color_echo $GREEN "🚀 Wählen Sie den Modus:"
color_echo $BLUE "1) Normal: Chrome Browser öffnet sich zum Surfen"
color_echo $BLUE "2) Headless: Nur HTML-Output ohne Browser-Fenster"
echo ""

read -p "Wählen Sie (1 oder 2): " choice

case $choice in
  1)
    color_echo $GREEN "🌍 Starte normalen Browser..."
    python3 tor_browser.py
    ;;
  2)
    color_echo $GREEN "🤖 Starte HTML-Fetcher..."
    python3 tor_html.py
    ;;
  *)
    color_echo $GREEN "🌍 Starte normalen Browser (Standard)..."
    python3 tor_browser.py
    ;;
esac

# Cleanup nach Beendigung
color_echo $BLUE "🧹 Bereinigung..."
pkill -f tor &> /dev/null

echo ""
color_echo $GREEN "✅ Alle Prozesse beendet. Auf Wiedersehen!"