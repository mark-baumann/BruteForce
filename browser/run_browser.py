#!/usr/bin/env python3
"""
CLI: Startet Chrome (sichtbar) mit Tor-Proxy und öffnet angegebene URL.
"""

import sys
import logging
from urllib.parse import urlparse

# Pfad zum Projekt-Root anpassen
from browser.session import BrowserSession
from proxy import TorProxy

logger = logging.getLogger(__name__)
if not logger.handlers:
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    sh = logging.StreamHandler()
    sh.setFormatter(formatter)
    logger.addHandler(sh)
    try:
        fh = logging.FileHandler('network.log')
        fh.setFormatter(formatter)
        logger.addHandler(fh)
    except Exception:
        pass

def normalize_url(arg: str) -> str:
    parsed = urlparse(arg)
    if not parsed.scheme:
        return f"https://{arg}"
    return arg

def main():
    if len(sys.argv) < 2:
        print("Nutzung: python -m browser.run_browser <url>")
        sys.exit(1)

    target = normalize_url(sys.argv[1])
    tor = TorProxy()
    session = BrowserSession(tor_proxy=tor)

    if not session.start():
        print("✗ Browser konnte nicht gestartet werden")
        sys.exit(2)

    # Tor Exit-IP über Control Port abfragen (warten bis Circuit fertig)
    def wait_for_tor_exit_ip(tor_proxy, timeout=30):
        import time
        for _ in range(timeout):
            exit_ip = tor_proxy.get_exit_ip()
            if exit_ip:
                return exit_ip
            time.sleep(1)
        return None

    print("Warte auf Tor-Circuit...")
    exit_ip = wait_for_tor_exit_ip(tor)
    if exit_ip:
        print(f"Tor Exit-IP: {exit_ip}")
        logger.info(f"Tor Exit-IP: {exit_ip}")
    else:
        print("Tor Exit-IP unbekannt (Timeout)")
        logger.warning("Tor Exit-IP unbekannt")

    if not session.visit(target):
        print(f"✗ Konnte URL nicht laden: {target}")
        session.close()
        sys.exit(3)

    print(f"✓ Geöffnet: {target}")
    # Browserfenster offen halten, bis manueller Schließvorgang
    session.wait_until_closed()
    session.close()

if __name__ == "__main__":
    main()
