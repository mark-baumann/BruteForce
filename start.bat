@echo off
REM start.bat
REM Startet Chrome über Tor-Proxy und zeigt die Exit-IP.
REM Nutzung: start.bat https://example.com

IF "%~1"=="" (
    ECHO Bitte eine URL als Parameter angeben.
    ECHO Beispiel: start.bat https://example.com
    EXIT /B 1
)
SET TARGET_URL=%~1

REM Aktuelles Script-Verzeichnis ermitteln
SET SCRIPT_DIR=%~dp0
ECHO [start.bat] Script-Verzeichnis: %SCRIPT_DIR%
CD /D "%SCRIPT_DIR%"

REM Virtuelle Umgebung erstellen, falls nicht vorhanden
IF NOT EXIST ".venv\Scripts\activate.bat" (
    ECHO [start.bat] Erstelle .venv...
    python -m venv .venv
)

REM Aktivieren der virtuellen Umgebung
CALL .venv\Scripts\activate.bat
ECHO [start.bat] Python: 
python --version

REM Pip aktualisieren
ECHO [start.bat] Aktualisiere pip...
python -m pip install --upgrade pip

REM Dependencies aus requirements.txt installieren
IF EXIST "requirements.txt" (
    ECHO [start.bat] Installiere Abhängigkeiten aus requirements.txt...
    pip install -r requirements.txt
) ELSE (
    ECHO [start.bat] Keine requirements.txt gefunden.
)

REM Prüfen ob Tor installiert ist
SET TOR_PATH="C:\Program Files\Tor Browser\Browser\TorBrowser\Tor\tor.exe"
IF NOT EXIST %TOR_PATH% (
    ECHO [start.bat] Tor wurde nicht gefunden unter %TOR_PATH%.
    ECHO Bitte Tor installieren oder Pfad anpassen.
    EXIT /B 1
)

REM Prüfen ob Chrome installiert ist
SET CHROME_PATH="C:\Program Files\Google\Chrome\Application\chrome.exe"
IF NOT EXIST %CHROME_PATH% (
    ECHO [start.bat] Chrome wurde nicht gefunden unter %CHROME_PATH%.
    ECHO Bitte Chrome installieren oder Pfad anpassen.
    EXIT /B 1
)

REM Chrome über Tor starten
ECHO [start.bat] Starte Chrome über Tor-Proxy mit URL: %TARGET_URL%
START "" %CHROME_PATH% --proxy-server="socks5://127.0.0.1:9050" --new-window "%TARGET_URL%"

REM Exit-IP anzeigen
ECHO [start.bat] Prüfe Exit-IP...
powershell -Command "Invoke-RestMethod -Uri 'https://api.ipify.org'"

ECHO [start.bat] Fertig.
PAUSE
