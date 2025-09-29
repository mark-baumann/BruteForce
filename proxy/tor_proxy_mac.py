#!/usr/bin/env python3
"""
Tor Proxy Manager für macOS/Linux
Verwaltet Tor-Verbindungen, stellt Proxy-Sessions bereit und arbeitet kompatibel
zur Windows-Implementierung.
"""

import subprocess
import time
import socket
import requests
import logging
from typing import Optional, Dict, Any
import psutil
import os
from shutil import which
from stem import Signal
from stem.control import Controller

# Logging konfigurieren
logger = logging.getLogger(__name__)
if not logger.handlers:
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    # Console
    sh = logging.StreamHandler()
    sh.setFormatter(formatter)
    logger.addHandler(sh)
    # File network.log
    try:
        fh = logging.FileHandler('network.log')
        fh.setFormatter(formatter)
        logger.addHandler(fh)
    except Exception:
        pass


class TorProxy:
    """
    Tor Proxy Manager für macOS/Linux
    """

    def __init__(self):
        self.tor_process: Optional[subprocess.Popen] = None
        self.tor_port = 9050  # SOCKS5 Port
        self.control_port = 9051  # Control Port
        self.session: Optional[requests.Session] = None
        self.tor_data_dir = os.path.join('/tmp', 'tor_data')
        self.tor_config_file = os.path.join('/tmp', 'torrc_bruteforce')
        self.tor_exe_path = self._find_tor_executable()

    def _find_tor_executable(self) -> Optional[str]:
        """Findet die Tor-Executable auf macOS/Linux"""
        candidates = [
            '/opt/homebrew/bin/tor',  # Apple Silicon Homebrew
            '/usr/local/bin/tor',     # Intel Homebrew
            '/usr/bin/tor',           # System tor
        ]
        for path in candidates:
            if os.path.exists(path):
                logger.info(f"Tor gefunden unter: {path}")
                return path
        in_path = which('tor')
        if in_path:
            logger.info(f"Tor im PATH gefunden: {in_path}")
            return in_path
        logger.error("Tor nicht gefunden. Bitte Tor installieren (z.B. brew install tor)")
        return None

    def check_tor_installed(self) -> bool:
        return bool(self.tor_exe_path and os.path.exists(self.tor_exe_path))

    def is_tor_running(self) -> bool:
        for proc in psutil.process_iter(['pid', 'name', 'exe']):
            try:
                name = (proc.info.get('name') or '').lower()
                exe = (proc.info.get('exe') or '').lower()
                if 'tor' == name or exe.endswith('/tor'):
                    return True
            except Exception:
                continue
        return False

    def check_port_available(self, port: int) -> bool:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            try:
                sock.bind(('127.0.0.1', port))
                return True
            except OSError:
                return False

    def create_tor_config(self) -> str:
        os.makedirs(self.tor_data_dir, exist_ok=True)
        config_content = f"""SocksPort 127.0.0.1:{self.tor_port}
ControlPort 127.0.0.1:{self.control_port}
DataDirectory {self.tor_data_dir}
Log notice stdout
ClientOnly 1
CookieAuthentication 1
ExitPolicy accept *:80
ExitPolicy accept *:443
ExitPolicy accept *:53
ExitPolicy accept *:8080
ExitPolicy accept *:8443
ExitPolicy reject *:*
"""
        with open(self.tor_config_file, 'w') as f:
            f.write(config_content)
        logger.info(f"Tor-Konfiguration erstellt: {self.tor_config_file}")
        return self.tor_config_file

    def start_tor(self) -> bool:
        if not self.check_tor_installed():
            return False
        if self.is_tor_running():
            logger.info("Tor läuft bereits")
            return True
        if not self.check_port_available(self.tor_port):
            logger.error(f"Port {self.tor_port} bereits belegt")
            return False
        if not self.check_port_available(self.control_port):
            logger.error(f"Port {self.control_port} bereits belegt")
            return False
        try:
            config_path = self.create_tor_config()
            logger.info("Starte Tor...")
            self.tor_process = subprocess.Popen(
                [self.tor_exe_path, '-f', config_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            max_wait = 30
            for _ in range(max_wait):
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
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex(('127.0.0.1', self.tor_port))
            sock.close()
            return result == 0
        except Exception:
            return False

    def stop_tor(self):
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
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if (proc.info.get('name') or '').lower() == 'tor':
                    proc.terminate()
            except Exception:
                continue

    def create_session(self) -> Optional[requests.Session]:
        if not self.check_tor_connection():
            logger.error("Keine Tor-Verbindung verfügbar")
            return None
        try:
            session = requests.Session()
            proxies = {
                'http': f'socks5://127.0.0.1:{self.tor_port}',
                'https': f'socks5://127.0.0.1:{self.tor_port}',
            }
            session.proxies.update(proxies)
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
            session.headers.update(headers)
            self.session = session
            logger.info("Proxy-Session erstellt")
            return session
        except Exception as e:
            logger.error(f"Fehler beim Erstellen der Session: {e}")
            return None

    def test_connection(self) -> Dict[str, Any]:
        if not self.session:
            self.session = self.create_session()
        if not self.session:
            return {"status": "error", "message": "Keine Session verfügbar"}
        try:
            response = self.session.get('http://httpbin.org/ip', timeout=30)
            if response.status_code == 200:
                ip_info = response.json()
                return {
                    "status": "success",
                    "ip": ip_info.get("origin", "Unknown"),
                    "message": "Tor-Verbindung erfolgreich",
                }
            else:
                return {"status": "error", "message": f"HTTP {response.status_code}"}
        except requests.exceptions.RequestException as e:
            logger.error(f"Verbindungstest fehlgeschlagen: {e}")
            return {"status": "error", "message": str(e)}

    def new_identity(self) -> bool:
        try:
            with Controller.from_port(port=self.control_port) as controller:
                self._authenticate_controller(controller)
                controller.signal(Signal.NEWNYM)
                logger.info("Neue Tor-Identität angefordert")
                time.sleep(5)
                return True
        except Exception as e:
            logger.error(f"Fehler beim Erneuern der Identität: {e}")
            return False

    def get_proxy_settings(self) -> Dict[str, str]:
        return {
            'http_proxy': f'socks5://127.0.0.1:{self.tor_port}',
            'https_proxy': f'socks5://127.0.0.1:{self.tor_port}',
            'socks_proxy': f'127.0.0.1:{self.tor_port}',
        }

    def _authenticate_controller(self, controller: Controller):
        try:
            controller.authenticate()  # Cookie-Auth
            return
        except Exception:
            try:
                controller.authenticate("")
            except Exception:
                raise

    def get_exit_fingerprint(self) -> Optional[str]:
        try:
            with Controller.from_port(port=self.control_port) as controller:
                self._authenticate_controller(controller)
                circuits = controller.get_circuits()
                built = [c for c in circuits if c.status == 'BUILT' and c.purpose == 'GENERAL' and c.path]
                if not built:
                    return None
                exit_fp = built[0].path[-1][0]
                return exit_fp
        except Exception as e:
            logger.error(f"Fehler beim Ermitteln des Exit-Fingerprints: {e}")
            return None

    def get_exit_ip(self) -> Optional[str]:
        try:
            with Controller.from_port(port=self.control_port) as controller:
                self._authenticate_controller(controller)
                circuits = controller.get_circuits()
                built = [c for c in circuits if c.status == 'BUILT' and c.purpose == 'GENERAL' and c.path]
                if not built:
                    logger.warning("Keine gebaute Circuit gefunden, Exit-IP unbekannt")
                    return None
                exit_fp = built[0].path[-1][0]
                desc = controller.get_network_status(exit_fp)
                if desc and getattr(desc, 'address', None):
                    logger.info(f"Exit-Node: {desc.nickname} ({desc.fingerprint}) {desc.address}")
                    return desc.address
                return None
        except Exception as e:
            logger.error(f"Fehler beim Ermitteln der Exit-IP: {e}")
            return None

    def __enter__(self):
        self.start_tor()
        self.create_session()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop_tor()


