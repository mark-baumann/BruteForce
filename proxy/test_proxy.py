#!/usr/bin/env python3
"""
Proxy Test Script
Testet die Tor-Proxy-Verbindung und zeigt die Exit-IP an.
"""

import socket
import requests
import sys
import time

def test_tor_connection():
    """Testet ob Tor auf Port 9050 läuft"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex(('127.0.0.1', 9050))
        sock.close()
        return result == 0
    except Exception:
        return False

def get_exit_ip():
    """Ermittelt die Exit-IP über Tor-Proxy"""
    if not test_tor_connection():
        print("FEHLER: Tor-Proxy auf Port 9050 nicht erreichbar!")
        return None
    
    try:
        proxies = {
            'http': 'socks5://127.0.0.1:9050',
            'https': 'socks5://127.0.0.1:9050'
        }
        
        # Test mit mehreren Services
        services = [
            'https://api.ipify.org',
            'https://httpbin.org/ip',
            'https://icanhazip.com'
        ]
        
        for service in services:
            try:
                print(f"Teste {service}...")
                response = requests.get(service, proxies=proxies, timeout=15)
                if response.status_code == 200:
                    ip = response.text.strip()
                    print(f"✓ Tor Exit-IP: {ip}")
                    return ip
            except Exception as e:
                print(f"✗ {service} fehlgeschlagen: {e}")
                continue
        
        print("FEHLER: Alle IP-Services fehlgeschlagen")
        return None
        
    except Exception as e:
        print(f"FEHLER beim Testen der Proxy-Verbindung: {e}")
        return None

def main():
    print("=== Tor Proxy Test ===")
    
    # Teste lokale Verbindung
    if test_tor_connection():
        print("✓ Tor-Proxy auf Port 9050 erreichbar")
    else:
        print("✗ Tor-Proxy auf Port 9050 NICHT erreichbar")
        print("Bitte stelle sicher, dass Tor läuft!")
        sys.exit(1)
    
    # Teste Exit-IP
    print("\nTeste Exit-IP...")
    exit_ip = get_exit_ip()
    
    if exit_ip:
        print(f"\n✓ Erfolgreich! Tor Exit-IP: {exit_ip}")
        sys.exit(0)
    else:
        print("\n✗ Fehler beim Ermitteln der Exit-IP")
        sys.exit(1)

if __name__ == "__main__":
    main()
