#!/usr/bin/env python3
"""
Tor Proxy Manager - Platform Detector
Lädt automatisch die richtige Tor-Proxy-Implementierung für das aktuelle Betriebssystem.
"""

import platform
import sys
import os

# Füge den proxy-Ordner zum Python-Pfad hinzu
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def get_tor_proxy():
    """
    Lädt die richtige Tor-Proxy-Implementierung basierend auf dem Betriebssystem.
    
    Returns:
        TorProxy-Klasse für das aktuelle Betriebssystem
    """
    system = platform.system().lower()
    
    if system == "windows":
        try:
            from tor_proxy_windows import TorProxy
            return TorProxy
        except ImportError as e:
            print(f"Fehler beim Laden der Windows Tor-Proxy-Implementierung: {e}")
            print("Falling back to macOS/Linux implementation...")
            from tor_proxy_mac import TorProxy
            return TorProxy
    else:
        # macOS, Linux, etc.
        try:
            from tor_proxy_mac import TorProxy
            return TorProxy
        except ImportError as e:
            print(f"Fehler beim Laden der macOS/Linux Tor-Proxy-Implementierung: {e}")
            print("Falling back to Windows implementation...")
            from tor_proxy_windows import TorProxy
            return TorProxy

# Lade die richtige TorProxy-Klasse
TorProxy = get_tor_proxy()

# Exportiere die Klasse für einfache Verwendung
__all__ = ['TorProxy']