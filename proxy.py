#!/usr/bin/env python3
"""
Tor Proxy Manager
Verwaltet Tor-Verbindungen und stellt Proxy-Sessions bereit.
"""

import subprocess
import time
import socket
import requests
import logging
from typing import Optional, Dict, Any
import psutil
import signal
import os
from stem import Signal
from stem.control import Controller

# Logging konfigurieren
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TorProxy:
    """
    Tor Proxy Manager für macOS mit Homebrew Installation
    """
    
    def __init__(self):
        self.tor_process = None
        self.tor_port = 9050  # SOCKS5 Port
        self.control_port = 9051  # Control Port
        self.tor_password = None
        self.tor_data_dir = os.path.expanduser("~/.tor")
        self.tor_config_file = "/usr/local/etc/tor/torrc"
        self.session = None
        
    def check_tor_installed(self) -> bool:
        """Überprüft ob Tor über Homebrew installiert ist"""
        try:
            result = subprocess.run(['which', 'tor'], capture_output=True, text=True)
            if result.returncode == 0:
                logger.info(f"Tor gefunden unter: {result.stdout.strip()}")
                return True
            else:
                logger.error("Tor nicht gefunden. Bitte mit 'brew install tor' installieren.")
                return False
        except Exception as e:
            logger.error(f"Fehler beim Überprüfen der Tor-Installation: {e}")
            return False
    
    def is_tor_running(self) -> bool:
        """Überprüft ob Tor bereits läuft"""
        for proc in psutil.process_iter(['pid', 'name']):
            if proc.info['name'] == 'tor':
                return True
        return False
    
    def check_port_available(self, port: int) -> bool:
        """Überprüft ob ein Port verfügbar ist"""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            try:
                sock.bind(('127.0.0.1', port))
                return True
            except OSError:
                return False
    
    def create_tor_config(self) -> str:
        """Erstellt eine temporäre Tor-Konfigurationsdatei"""
        # Stelle sicher, dass das DataDirectory existiert
        os.makedirs(self.tor_data_dir, exist_ok=True)
        
        config_content = f"""
# Tor Konfiguration für Python Proxy
SocksPort 127.0.0.1:{self.tor_port}
ControlPort 127.0.0.1:{self.control_port}
HashedControlPassword 16:872860B76453A77D60CA2BB8C1A7042072093276A3D701AD684053EC4C
DataDirectory {self.tor_data_dir}
Log notice stdout
ClientOnly 1
"""
        
        config_path = "/tmp/torrc_python"
        with open(config_path, 'w') as f:
            f.write(config_content)
        
        logger.info(f"Tor-Konfiguration erstellt: {config_path}")
        return config_path
    
    def start_tor(self) -> bool:
        """Startet den Tor-Service"""
        if not self.check_tor_installed():
            return False
        
        if self.is_tor_running():
            logger.info("Tor läuft bereits")
            return True
        
        # Prüfe ob Ports verfügbar sind
        if not self.check_port_available(self.tor_port):
            logger.error(f"Port {self.tor_port} bereits belegt")
            return False
        
        if not self.check_port_available(self.control_port):
            logger.error(f"Port {self.control_port} bereits belegt")
            return False
        
        try:
            # Erstelle Tor-Konfiguration
            config_path = self.create_tor_config()
            
            # Starte Tor
            logger.info("Starte Tor...")
            self.tor_process = subprocess.Popen([
                'tor', '-f', config_path
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Warte bis Tor bereit ist
            max_wait = 30
            for i in range(max_wait):
                if self.check_tor_connection():
                    logger.info("Tor erfolgreich gestartet")
                    return True
                time.sleep(1)
            
            logger.error("Tor konnte nicht gestartet werden")
            return False
            
        except Exception as e:
            logger.error(f"Fehler beim Starten von Tor: {e}")
            return False
    
    def check_tor_connection(self) -> bool:
        """Überprüft die Tor-Verbindung"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex(('127.0.0.1', self.tor_port))
            sock.close()
            return result == 0
        except Exception:
            return False
    
    def stop_tor(self):
        """Stoppt den Tor-Service"""
        if self.tor_process:
            try:
                self.tor_process.terminate()
                self.tor_process.wait(timeout=10)
                logger.info("Tor-Prozess beendet")
            except subprocess.TimeoutExpired:
                self.tor_process.kill()
                logger.info("Tor-Prozess zwangsweise beendet")
            except Exception as e:
                logger.error(f"Fehler beim Beenden von Tor: {e}")
            finally:
                self.tor_process = None
        
        # Beende alle Tor-Prozesse
        for proc in psutil.process_iter(['pid', 'name']):
            if proc.info['name'] == 'tor':
                try:
                    os.kill(proc.info['pid'], signal.SIGTERM)
                    logger.info(f"Tor-Prozess {proc.info['pid']} beendet")
                except Exception as e:
                    logger.error(f"Fehler beim Beenden des Tor-Prozesses {proc.info['pid']}: {e}")
    
    def create_session(self) -> Optional[requests.Session]:
        """Erstellt eine requests Session mit Tor Proxy"""
        if not self.check_tor_connection():
            logger.error("Keine Tor-Verbindung verfügbar")
            return None
        
        try:
            session = requests.Session()
            
            # Tor SOCKS5 Proxy konfigurieren
            proxies = {
                'http': f'socks5://127.0.0.1:{self.tor_port}',
                'https': f'socks5://127.0.0.1:{self.tor_port}'
            }
            session.proxies.update(proxies)
            
            # Headers für Anonymität
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
            session.headers.update(headers)
            
            self.session = session
            logger.info("Proxy-Session erstellt")
            return session
            
        except Exception as e:
            logger.error(f"Fehler beim Erstellen der Session: {e}")
            return None
    
    def test_connection(self) -> Dict[str, Any]:
        """Testet die Tor-Verbindung und gibt Informationen zurück"""
        if not self.session:
            self.session = self.create_session()
        
        if not self.session:
            return {"status": "error", "message": "Keine Session verfügbar"}
        
        try:
            # Test mit httpbin.org
            response = self.session.get('http://httpbin.org/ip', timeout=30)
            if response.status_code == 200:
                ip_info = response.json()
                
                # Zusätzliche Informationen abrufen
                try:
                    geo_response = self.session.get('http://httpbin.org/headers', timeout=15)
                    headers_info = geo_response.json() if geo_response.status_code == 200 else {}
                except:
                    headers_info = {}
                
                return {
                    "status": "success",
                    "ip": ip_info.get("origin", "Unknown"),
                    "headers": headers_info.get("headers", {}),
                    "message": "Tor-Verbindung erfolgreich"
                }
            else:
                return {"status": "error", "message": f"HTTP {response.status_code}"}
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Verbindungstest fehlgeschlagen: {e}")
            return {"status": "error", "message": str(e)}
    
    def new_identity(self) -> bool:
        """Erneuert die Tor-Identität (neue IP)"""
        try:
            with Controller.from_port(port=self.control_port) as controller:
                controller.authenticate()
                controller.signal(Signal.NEWNYM)
                logger.info("Neue Tor-Identität angefordert")
                time.sleep(5)  # Warte bis neue Verbindung aufgebaut ist
                return True
        except Exception as e:
            logger.error(f"Fehler beim Erneuern der Identität: {e}")
            return False
    
    def get_proxy_settings(self) -> Dict[str, str]:
        """Gibt die Proxy-Einstellungen zurück"""
        return {
            'http_proxy': f'socks5://127.0.0.1:{self.tor_port}',
            'https_proxy': f'socks5://127.0.0.1:{self.tor_port}',
            'socks_proxy': f'127.0.0.1:{self.tor_port}'
        }
    
    def __enter__(self):
        """Context Manager Eingang"""
        self.start_tor()
        self.create_session()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context Manager Ausgang"""
        self.stop_tor()


def main():
    """Hauptfunktion für Tests"""
    proxy = TorProxy()
    
    try:
        print("Starte Tor...")
        if proxy.start_tor():
            print("✓ Tor gestartet")
            
            print("Erstelle Session...")
            session = proxy.create_session()
            if session:
                print("✓ Session erstellt")
                
                print("Teste Verbindung...")
                result = proxy.test_connection()
                print(f"Status: {result['status']}")
                if result['status'] == 'success':
                    print(f"IP-Adresse: {result['ip']}")
                    print(f"Message: {result['message']}")
                else:
                    print(f"Fehler: {result['message']}")
            else:
                print("✗ Session konnte nicht erstellt werden")
        else:
            print("✗ Tor konnte nicht gestartet werden")
            
    except KeyboardInterrupt:
        print("\nBeende...")
    finally:
        proxy.stop_tor()
        print("Tor gestoppt")


if __name__ == "__main__":
    main()