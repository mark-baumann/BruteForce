@echo off
REM start.bat - Einfache Version
REM Nutzung: start.bat https://example.com

IF "%~1"=="" (
    ECHO Bitte eine URL als Parameter angeben.
    ECHO Beispiel: start.bat https://example.com
    EXIT /B 1
)

REM Aktuelles Script-Verzeichnis ermitteln
SET SCRIPT_DIR=%~dp0
CD /D "%SCRIPT_DIR%"

REM Virtuelle Umgebung aktivieren
IF EXIST ".venv\Scripts\activate.bat" (
    CALL .venv\Scripts\activate.bat
) ELSE (
    ECHO Erstelle virtuelle Umgebung...
    python -m venv .venv
    CALL .venv\Scripts\activate.bat
    pip install -r requirements.txt
)

REM Python-Skript starten
ECHO Starte Browser mit Tor-Proxy...
python browser/run_browser.py "%~1"

PAUSE
