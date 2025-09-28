#!/usr/bin/env python3
"""
Einfacher Tor-Test für Windows
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from proxy.tor_proxy import TorProxy

def main():
    print("=== Tor Test für Windows ===")
    
    tor = TorProxy()
    
    print("1. Prüfe Tor-Installation...")
    if not tor.check_tor_installed():
        print("✗ Tor nicht gefunden!")
        return False
    print("✓ Tor gefunden")
    
    print("2. Starte Tor...")
    if not tor.start_tor():
        print("✗ Tor konnte nicht gestartet werden!")
        return False
    print("✓ Tor gestartet")
    
    print("3. Teste Verbindung...")
    result = tor.test_connection()
    if result['status'] == 'success':
        print(f"✓ Tor funktioniert! Exit-IP: {result['ip']}")
        return True
    else:
        print(f"✗ Tor-Test fehlgeschlagen: {result['message']}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

