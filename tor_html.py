#!/usr/bin/env python3
"""
Tor HTML Fetcher - Holt HTML-Inhalte über Tor
"""

import subprocess
import time
import os
import signal
import psutil
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions

class TorHTMLFetcher:
    def __init__(self):
        self.tor_process = None
        self.driver = None
        self.tor_dir = os.path.expanduser("~/.tor")
        self.session = None
    
    def cleanup_tor(self):
        """Beendet alle Tor-Prozesse"""
        for proc in psutil.process_iter(['pid', 'name']):
            if proc.info['name'] == 'tor':
                try:
                    os.kill(proc.info['pid'], signal.SIGTERM)
                    time.sleep(1)
                except:
                    pass
    
    def start_tor(self):
        """Startet Tor"""
        self.cleanup_tor()
        time.sleep(2)
        
        os.makedirs(self.tor_dir, exist_ok=True)
        
        config_content = f"""
SocksPort 127.0.0.1:9050
DataDirectory {self.tor_dir}
Log notice stdout
ClientOnly 1
"""
        
        config_path = "/tmp/torrc_html"
        with open(config_path, 'w') as f:
            f.write(config_content)
        
        print("🚀 Starte Tor...")
        
        self.tor_process = subprocess.Popen([
            'tor', '-f', config_path
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        for i in range(30):
            try:
                import socket
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex(('127.0.0.1', 9050))
                sock.close()
                
                if result == 0:
                    print(f"✅ Tor bereit nach {i+1} Sekunden")
                    return True
            except:
                pass
            time.sleep(1)
        
        print("❌ Tor konnte nicht gestartet werden")
        return False
    
    def create_session(self):
        """Erstellt requests Session mit Tor"""
        self.session = requests.Session()
        self.session.proxies = {
            'http': 'socks5://127.0.0.1:9050',
            'https': 'socks5://127.0.0.1:9050'
        }
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def get_html_requests(self, url):
        """Holt HTML mit requests (schneller)"""
        if not self.session:
            self.create_session()
        
        try:
            print(f"🌍 Lade mit requests: {url}")
            response = self.session.get(url, timeout=30)
            if response.status_code == 200:
                html = response.text
                print(f"✅ HTML geladen ({len(html)} Zeichen)")
                return html
            else:
                print(f"❌ HTTP {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ Fehler: {e}")
            return None
    
    def start_chrome_headless(self):
        """Startet headless Chrome für JavaScript-Seiten"""
        options = ChromeOptions()
        options.add_argument('--proxy-server=socks5://127.0.0.1:9050')
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        options.add_argument(f'--user-agent={user_agent}')
        
        try:
            self.driver = webdriver.Chrome(options=options)
            print("✅ Chrome headless gestartet")
            return True
        except Exception as e:
            print(f"❌ Chrome headless fehler: {e}")
            return False
    
    def get_html_selenium(self, url):
        """Holt HTML mit Selenium (für JavaScript)"""
        if not self.driver:
            if not self.start_chrome_headless():
                return None
        
        try:
            print(f"🌍 Lade mit Selenium: {url}")
            self.driver.get(url)
            time.sleep(3)  # Warte auf JavaScript
            
            html = self.driver.page_source
            print(f"✅ HTML geladen ({len(html)} Zeichen)")
            return html
        except Exception as e:
            print(f"❌ Fehler: {e}")
            return None
    
    def fetch_url(self, url, use_selenium=False):
        """Holt HTML von URL"""
        if use_selenium:
            return self.get_html_selenium(url)
        else:
            return self.get_html_requests(url)
    
    def stop(self):
        """Bereinigung"""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
        
        if self.tor_process:
            self.tor_process.terminate()
            try:
                self.tor_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.tor_process.kill()
        
        self.cleanup_tor()

def main():
    fetcher = TorHTMLFetcher()
    
    try:
        print("🎭 === Tor HTML Fetcher ===")
        
        # Tor starten
        if not fetcher.start_tor():
            return
        
        # Beispiele
        print("\n📝 Beispiel-URLs:")
        
        # 1. Einfache Seite mit requests
        html1 = fetcher.fetch_url("http://httpbin.org/ip")
        if html1:
            print(f"\n--- httpbin.org/ip ---\n{html1[:500]}\n")
        
        # 2. Seite mit Selenium (falls JavaScript benötigt)
        print("\n🤖 Teste mit Selenium...")
        html2 = fetcher.fetch_url("http://httpbin.org/headers", use_selenium=True)
        if html2:
            print(f"\n--- httpbin.org/headers (Selenium) ---\n{html2[:500]}\n")
        
        print("🎉 Fertig! Sie können die Funktionen jetzt verwenden.")
        
    except KeyboardInterrupt:
        print("\n🛑 Beendet...")
    finally:
        fetcher.stop()

if __name__ == "__main__":
    main()