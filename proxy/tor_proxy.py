#!/usr/bin/env python3
"""
Tor Proxy Manager – Plattformunabhängiger Loader mit eingebauten Klassen
Automatisch wählt das Skript für Windows oder macOS/Linux die richtige TorProxy-Klasse.
"""

import platform
import subprocess
import time

import requests


class TorProxyMac:
    """
    Tor-Proxy für macOS/Linux: Startet Tor und richtet Proxy-Verbindung ein.
    """

    def __init__(self, tor_bin="tor", socks_port=9050):
        self.tor_bin = tor_bin
        self.socks_port = socks_port
        self.tor_process = None

    def is_tor_running(self):
        result = subprocess.run(["pgrep", "tor"], capture_output=True)
        return result.returncode == 0

    def start(self):
        print("[TorProxy-Mac] Starte Tor...")
        try:
            self.tor_process = subprocess.Popen([self.tor_bin])
            # Warte auf Tor-Startup
            for _ in range(10):
                result = subprocess.run(["pgrep", "tor"], capture_output=True)
                if result.returncode == 0:
                    print("[TorProxy-Mac] Tor läuft.")
                    return True
                time.sleep(1)
            print("[TorProxy-Mac] Tor-Start fehlgeschlagen.")
            return False
        except Exception as e:
            print(f"[TorProxy-Mac] Fehler beim Starten: {e}")
            return False

    def stop(self):
        if self.tor_process:
            print("[TorProxy-Mac] Stoppe Tor.")
            self.tor_process.terminate()

    def get_proxy_url(self):
        return f"socks5://127.0.0.1:{self.socks_port}"

    def get_exit_ip(self):
        try:
            proxies = {
                "http": self.get_proxy_url(),
                "https": self.get_proxy_url()
            }
            response = requests.get("http://check.torproject.org/api/ip", proxies=proxies, timeout=5)
            data = response.json()
            return data.get("IP", "Unbekannt")
        except Exception as e:
            print(f"[TorProxyMac] Fehler bei get_exit_ip: {e}")
            return "Unknown"

class TorProxyWindows:
    """
    Tor-Proxy für Windows: Startet Tor und setzt Proxy-Verbindung.
    """
    def __init__(self, tor_bin="tor.exe", socks_port=9050):
        self.tor_bin = tor_bin
        self.socks_port = socks_port
        self.tor_process = None

    def is_tor_running(self):
        result = subprocess.run(["pgrep", "tor"], capture_output=True)
        return result.returncode == 0

    def start(self):
        print("[TorProxy-Windows] Starte Tor...")
        try:
            self.tor_process = subprocess.Popen([self.tor_bin])
            # Warte auf Tor-Startup
            for _ in range(10):
                result = subprocess.run(["tasklist", "/FI", "IMAGENAME eq tor.exe"], capture_output=True)
                if b"tor.exe" in result.stdout:
                    print("[TorProxy-Windows] Tor läuft.")
                    return True
                time.sleep(1)
            print("[TorProxy-Windows] Tor-Start fehlgeschlagen.")
            return False
        except Exception as e:
            print(f"[TorProxy-Windows] Fehler beim Starten: {e}")
            return False

    def stop(self):
        if self.tor_process:
            print("[TorProxy-Windows] Stoppe Tor.")
            self.tor_process.terminate()

    def get_proxy_url(self):
        return f"socks5://127.0.0.1:{self.socks_port}"

    def get_exit_ip(self):
        try:
            proxies = {
                "http": self.get_proxy_url(),
                "https": self.get_proxy_url()
            }
            response = requests.get("http://check.torproject.org/api/ip", proxies=proxies, timeout=5)
            data = response.json()
            return data.get("IP", "Unbekannt")
        except Exception as e:
            print(f"[TorProxyMac] Fehler bei get_exit_ip: {e}")
            return "Unknown"

def get_tor_proxy():
    system = platform.system().lower()
    if system == "windows":
        return TorProxyWindows
    else:
        return TorProxyMac

TorProxy = get_tor_proxy()
__all__ = ["TorProxy"]
