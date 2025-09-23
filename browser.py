#!/usr/bin/env python3
"""
Browser Proxy Session Manager
Verwendet die proxy.py für Tor-Verbindungen und stellt Browser-Sessions bereit.
"""

import time
import json
import logging
from typing import Optional, Dict, Any, List
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
import requests
from proxy import TorProxy

# Logging konfigurieren
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class BrowserProxy:
    """
    Browser Proxy Manager mit Tor-Integration
    """
    
    def __init__(self, browser_type: str = "chrome"):
        self.browser_type = browser_type.lower()
        self.tor_proxy = TorProxy()
        self.driver = None
        self.session = None
        
    def setup_chrome_proxy(self) -> ChromeOptions:
        """Konfiguriert Chrome mit Tor-Proxy"""
        options = ChromeOptions()
        
        # Proxy-Einstellungen
        proxy_settings = self.tor_proxy.get_proxy_settings()
        socks_proxy = proxy_settings['socks_proxy']
        
        options.add_argument(f'--proxy-server=socks5://{socks_proxy}')
        
        # Anonymitäts-Einstellungen
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-web-security')
        options.add_argument('--disable-features=VizDisplayCompositor')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-plugins')
        options.add_argument('--disable-images')
        options.add_argument('--disable-javascript')  # Optional, für mehr Anonymität
        
        # User Agent für Anonymität
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        options.add_argument(f'--user-agent={user_agent}')
        
        # Headless Mode (optional)
        # options.add_argument('--headless')
        
        # Weitere Datenschutz-Einstellungen
        prefs = {
            "profile.default_content_setting_values": {
                "cookies": 2,  # Blockiere alle Cookies
                "images": 2,   # Blockiere Bilder
                "plugins": 2,  # Blockiere Plugins
                "popups": 2,   # Blockiere Popups
                "geolocation": 2,  # Blockiere Geolocation
                "notifications": 2,  # Blockiere Benachrichtigungen
                "media_stream": 2,  # Blockiere Media Stream
            },
            "profile.managed_default_content_settings": {
                "images": 2
            }
        }
        options.add_experimental_option("prefs", prefs)
        
        return options
    
    def setup_firefox_proxy(self) -> FirefoxOptions:
        """Konfiguriert Firefox mit Tor-Proxy"""
        options = FirefoxOptions()
        
        # Profile für erweiterte Konfiguration
        profile = webdriver.FirefoxProfile()
        
        # Proxy-Einstellungen
        proxy_settings = self.tor_proxy.get_proxy_settings()
        socks_proxy_parts = proxy_settings['socks_proxy'].split(':')
        socks_host = socks_proxy_parts[0]
        socks_port = int(socks_proxy_parts[1])
        
        profile.set_preference("network.proxy.type", 1)
        profile.set_preference("network.proxy.socks", socks_host)
        profile.set_preference("network.proxy.socks_port", socks_port)
        profile.set_preference("network.proxy.socks_version", 5)
        profile.set_preference("network.proxy.socks_remote_dns", True)
        
        # Datenschutz-Einstellungen
        profile.set_preference("privacy.trackingprotection.enabled", True)
        profile.set_preference("dom.webnotifications.enabled", False)
        profile.set_preference("geo.enabled", False)
        profile.set_preference("media.navigator.enabled", False)
        profile.set_preference("network.cookie.cookieBehavior", 2)  # Blockiere alle Cookies
        profile.set_preference("javascript.enabled", False)  # Optional
        
        # User Agent
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0"
        profile.set_preference("general.useragent.override", user_agent)
        
        # Headless Mode (optional)
        # options.add_argument('--headless')
        
        options.profile = profile
        return options
    
    def start_browser(self) -> bool:
        """Startet den Browser mit Proxy"""
        try:
            # Starte Tor zuerst
            logger.info("Starte Tor...")
            if not self.tor_proxy.start_tor():
                logger.error("Tor konnte nicht gestartet werden")
                return False
            
            # Erstelle Session
            self.session = self.tor_proxy.create_session()
            if not self.session:
                logger.error("Proxy-Session konnte nicht erstellt werden")
                return False
            
            # Starte Browser
            logger.info(f"Starte {self.browser_type} Browser...")
            
            if self.browser_type == "chrome":
                options = self.setup_chrome_proxy()
                self.driver = webdriver.Chrome(options=options)
            elif self.browser_type == "firefox":
                options = self.setup_firefox_proxy()
                self.driver = webdriver.Firefox(options=options)
            else:
                logger.error(f"Nicht unterstützter Browser: {self.browser_type}")
                return False
            
            # Teste Browser-Proxy-Verbindung
            return self.test_browser_proxy()
            
        except WebDriverException as e:
            logger.error(f"Fehler beim Starten des Browsers: {e}")
            return False
        except Exception as e:
            logger.error(f"Unerwarteter Fehler: {e}")
            return False
    
    def test_browser_proxy(self) -> bool:
        """Testet die Browser-Proxy-Verbindung"""
        try:
            logger.info("Teste Browser-Proxy-Verbindung...")
            
            # Navigiere zu IP-Check Seite
            self.driver.get("http://httpbin.org/ip")
            
            # Warte auf Seiteninhalt
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Prüfe ob IP-Information angezeigt wird
            body_text = self.driver.find_element(By.TAG_NAME, "body").text
            if "origin" in body_text:
                logger.info("✓ Browser-Proxy-Verbindung erfolgreich")
                logger.info(f"IP-Info: {body_text[:100]}...")
                return True
            else:
                logger.error("Keine IP-Information gefunden")
                return False
                
        except TimeoutException:
            logger.error("Timeout beim Laden der Test-Seite")
            return False
        except Exception as e:
            logger.error(f"Fehler beim Testen der Browser-Verbindung: {e}")
            return False
    
    def navigate_to(self, url: str, timeout: int = 30) -> bool:
        """Navigiert zu einer URL"""
        if not self.driver:
            logger.error("Browser nicht gestartet")
            return False
        
        try:
            logger.info(f"Navigiere zu: {url}")
            self.driver.get(url)
            
            # Warte auf Seitenladung
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            logger.info("✓ Seite geladen")
            return True
            
        except TimeoutException:
            logger.error(f"Timeout beim Laden von {url}")
            return False
        except Exception as e:
            logger.error(f"Fehler beim Navigieren zu {url}: {e}")
            return False
    
    def get_page_source(self) -> Optional[str]:
        """Gibt den Quellcode der aktuellen Seite zurück"""
        if not self.driver:
            return None
        
        try:
            return self.driver.page_source
        except Exception as e:
            logger.error(f"Fehler beim Abrufen des Quellcodes: {e}")
            return None
    
    def take_screenshot(self, filename: str) -> bool:
        """Erstellt einen Screenshot der aktuellen Seite"""
        if not self.driver:
            return False
        
        try:
            self.driver.save_screenshot(filename)
            logger.info(f"Screenshot gespeichert: {filename}")
            return True
        except Exception as e:
            logger.error(f"Fehler beim Erstellen des Screenshots: {e}")
            return False
    
    def find_element_by_selector(self, selector: str, timeout: int = 10):
        """Findet ein Element per CSS-Selektor"""
        if not self.driver:
            return None
        
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
            )
            return element
        except TimeoutException:
            logger.error(f"Element nicht gefunden: {selector}")
            return None
        except Exception as e:
            logger.error(f"Fehler beim Suchen des Elements: {e}")
            return None
    
    def click_element(self, selector: str, timeout: int = 10) -> bool:
        """Klickt auf ein Element"""
        element = self.find_element_by_selector(selector, timeout)
        if element:
            try:
                element.click()
                logger.info(f"Element geklickt: {selector}")
                return True
            except Exception as e:
                logger.error(f"Fehler beim Klicken auf Element: {e}")
                return False
        return False
    
    def send_keys_to_element(self, selector: str, text: str, timeout: int = 10) -> bool:
        """Sendet Text an ein Element"""
        element = self.find_element_by_selector(selector, timeout)
        if element:
            try:
                element.clear()
                element.send_keys(text)
                logger.info(f"Text gesendet an {selector}: {text[:20]}...")
                return True
            except Exception as e:
                logger.error(f"Fehler beim Senden von Text: {e}")
                return False
        return False
    
    def new_tor_identity(self) -> bool:
        """Erneuert die Tor-Identität und startet Browser neu"""
        logger.info("Erneuere Tor-Identität...")
        
        if self.tor_proxy.new_identity():
            logger.info("✓ Neue Tor-Identität")
            # Optional: Browser neu starten für neue IP
            # self.restart_browser()
            return True
        else:
            logger.error("Fehler beim Erneuern der Tor-Identität")
            return False
    
    def restart_browser(self) -> bool:
        """Startet den Browser neu"""
        logger.info("Starte Browser neu...")
        self.close_browser()
        time.sleep(2)
        return self.start_browser()
    
    def make_request(self, url: str, method: str = "GET", **kwargs) -> Optional[requests.Response]:
        """Macht eine HTTP-Anfrage über die Tor-Session"""
        if not self.session:
            logger.error("Keine Session verfügbar")
            return None
        
        try:
            if method.upper() == "GET":
                response = self.session.get(url, **kwargs)
            elif method.upper() == "POST":
                response = self.session.post(url, **kwargs)
            else:
                logger.error(f"Nicht unterstützte HTTP-Methode: {method}")
                return None
            
            logger.info(f"{method} {url} -> {response.status_code}")
            return response
            
        except requests.exceptions.RequestException as e:
            logger.error(f"HTTP-Anfrage fehlgeschlagen: {e}")
            return None
    
    def get_current_ip(self) -> Optional[str]:
        """Gibt die aktuelle IP-Adresse zurück"""
        result = self.tor_proxy.test_connection()
        if result['status'] == 'success':
            return result['ip']
        return None
    
    def close_browser(self):
        """Schließt den Browser"""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("Browser geschlossen")
            except Exception as e:
                logger.error(f"Fehler beim Schließen des Browsers: {e}")
            finally:
                self.driver = None
    
    def close(self):
        """Schließt Browser und Tor"""
        self.close_browser()
        self.tor_proxy.stop_tor()
        logger.info("Browser und Tor gestoppt")
    
    def __enter__(self):
        """Context Manager Eingang"""
        self.start_browser()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context Manager Ausgang"""
        self.close()


class BrowserSession:
    """
    Vereinfachte Browser-Session Klasse für einfache Anwendung
    """
    
    def __init__(self, browser_type: str = "chrome", headless: bool = False):
        self.browser_proxy = BrowserProxy(browser_type)
        self.headless = headless
    
    def start(self) -> bool:
        """Startet die Browser-Session"""
        return self.browser_proxy.start_browser()
    
    def visit(self, url: str) -> bool:
        """Besucht eine URL"""
        return self.browser_proxy.navigate_to(url)
    
    def get_ip(self) -> Optional[str]:
        """Gibt die aktuelle IP zurück"""
        return self.browser_proxy.get_current_ip()
    
    def new_identity(self) -> bool:
        """Erneuert die Tor-Identität"""
        return self.browser_proxy.new_tor_identity()
    
    def screenshot(self, filename: str = None) -> bool:
        """Erstellt einen Screenshot"""
        if not filename:
            filename = f"screenshot_{int(time.time())}.png"
        return self.browser_proxy.take_screenshot(filename)
    
    def close(self):
        """Schließt die Session"""
        self.browser_proxy.close()


def main():
    """Beispiel für die Verwendung"""
    # Einfache Verwendung
    with BrowserSession("chrome") as session:
        if session.start():
            print(f"✓ Browser gestartet")
            print(f"Aktuelle IP: {session.get_ip()}")
            
            if session.visit("https://httpbin.org/headers"):
                print("✓ Seite besucht")
                session.screenshot("test.png")
                
                # Neue Identität
                session.new_identity()
                print(f"Neue IP: {session.get_ip()}")
            else:
                print("✗ Fehler beim Besuchen der Seite")
        else:
            print("✗ Browser konnte nicht gestartet werden")


if __name__ == "__main__":
    main()