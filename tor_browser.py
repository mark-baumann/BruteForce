#!/usr/bin/env python3
"""
Tor Browser - Chrome mit Tor-Proxy
Einfacher Einstiegspunkt für anonymes Browsing
"""

import subprocess
import time
import os
import signal
import psutil
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

class TorBrowser:
    def __init__(self):
        self.tor_process = None
        self.driver = None
        self.tor_dir = os.path.expanduser("~/.tor")
        
    def cleanup_tor(self):
        """Beendet alle laufenden Tor-Prozesse"""
        print("🧹 Bereinige alte Tor-Prozesse...")
        for proc in psutil.process_iter(['pid', 'name']):
            if proc.info['name'] == 'tor':
                try:
                    os.kill(proc.info['pid'], signal.SIGTERM)
                    time.sleep(1)
                except:
                    pass

    def start_tor(self):
        """Startet Tor mit optimaler Konfiguration"""
        self.cleanup_tor()
        time.sleep(2)
        
        # DataDirectory erstellen
        os.makedirs(self.tor_dir, exist_ok=True)
        
        # Tor-Konfiguration
        config_content = f"""
SocksPort 127.0.0.1:9050
DataDirectory {self.tor_dir}
Log notice stdout
ClientOnly 1
"""
        
        config_path = "/tmp/torrc_browser"
        with open(config_path, 'w') as f:
            f.write(config_content)
        
        print("🚀 Starte Tor...")
        
        # Tor-Prozess starten
        self.tor_process = subprocess.Popen([
            'tor', '-f', config_path
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Warte bis Tor bereit ist
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

    def get_current_ip(self):
        """Holt die aktuelle IP-Adresse über Tor"""
        try:
            session = requests.Session()
            session.proxies = {
                'http': 'socks5://127.0.0.1:9050',
                'https': 'socks5://127.0.0.1:9050'
            }
            response = session.get('http://httpbin.org/ip', timeout=10)
            if response.status_code == 200:
                return response.json().get('origin', 'Unknown')
        except:
            pass
        return 'Unknown'

    def start_chrome(self):
        """Startet Chrome mit Tor-Proxy - komplett unabhängig"""
        print("🌐 Starte Chrome mit Tor-Proxy...")
        
        options = ChromeOptions()
        
        # Tor SOCKS5 Proxy
        options.add_argument('--proxy-server=socks5://127.0.0.1:9050')
        
        # Browser-Optionen
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1200,800')
        
        # User Agent für Anonymität
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        options.add_argument(f'--user-agent={user_agent}')
        
        # WICHTIG: Browser unabhängig machen
        options.add_experimental_option("detach", True)
        
        try:
            self.driver = webdriver.Chrome(options=options)
            print("✅ Chrome gestartet")
            
            # Zeige aktuelle IP
            current_ip = self.get_current_ip()
            print(f"🔒 Aktuelle IP über Tor: {current_ip}")
            
            # Browser ist bereit - keine automatische Navigation
            print("🌍 Browser bereit zum Surfen!")
            print("👍 Browser läuft jetzt unabhängig - Sie können ihn normal verwenden!")
            
            return True
            
        except WebDriverException as e:
            print(f"❌ Fehler beim Starten von Chrome: {e}")
            return False

    def new_identity(self):
        """Erneuert die Tor-Identität (neue IP)"""
        print("🔄 Erneuere Tor-Identität...")
        old_ip = self.get_current_ip()
        
        # Tor neustarten für neue IP
        if self.tor_process:
            self.tor_process.terminate()
            time.sleep(2)
        
        if self.start_tor():
            new_ip = self.get_current_ip()
            print(f"🔄 IP geändert: {old_ip} → {new_ip}")
            
            # Browser-Seite neu laden
            if self.driver:
                try:
                    self.driver.refresh()
                except:
                    pass
        else:
            print("❌ Fehler beim Erneuern der Identität")

    def stop(self):
        """Beendet nur Tor - Browser bleibt offen"""
        print("🛑 Beende Tor-Prozess...")
        print("📱 Browser bleibt geöffnet und kann weiter verwendet werden!")
        
        # Browser NICHT schließen - er soll offen bleiben!
        # if self.driver:
        #     self.driver.quit()
        
        if self.tor_process:
            self.tor_process.terminate()
            try:
                self.tor_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.tor_process.kill()
        
        self.cleanup_tor()
        print("✅ Tor gestoppt")
        print("🌍 Chrome-Browser läuft weiter mit Tor-Proxy!")
    
    def close_browser(self):
        """Schließt den Browser explizit"""
        if self.driver:
            try:
                self.driver.quit()
                print("✅ Chrome-Browser geschlossen")
            except:
                print("⚠️  Browser war bereits geschlossen")
        else:
            print("⚠️  Kein Browser-Prozess gefunden")

    def start_chrome_headless(self):
        """Startet Chrome headless für HTML-Ausgabe"""
        print("🤖 Starte Chrome headless für HTML-Ausgabe...")
        
        options = ChromeOptions()
        
        # Tor SOCKS5 Proxy
        options.add_argument('--proxy-server=socks5://127.0.0.1:9050')
        
        # Headless Optionen
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        
        # User Agent für Anonymität
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        options.add_argument(f'--user-agent={user_agent}')
        
        try:
            self.driver = webdriver.Chrome(options=options)
            print("✅ Chrome headless gestartet")
            return True
        except WebDriverException as e:
            print(f"❌ Fehler beim Starten von Chrome headless: {e}")
            return False
    
    def get_html(self, url):
        """Holt HTML von einer URL"""
        if not self.driver:
            print("❌ Kein Browser verfügbar")
            return None
            
        try:
            print(f"🌍 Lade: {url}")
            self.driver.get(url)
            
            # Warte kurz auf Seitenladung
            time.sleep(3)
            
            html = self.driver.page_source
            print(f"✅ HTML geladen ({len(html)} Zeichen)")
            return html
            
        except Exception as e:
            print(f"❌ Fehler beim Laden der Seite: {e}")
            return None
    
    def run(self):
        """Hauptfunktion - startet Browser"""
        try:
            print("🎭 === Tor Browser System ===")
            print()
            
            # Normale IP anzeigen
            try:
                normal_response = requests.get('http://httpbin.org/ip', timeout=10)
                normal_ip = normal_response.json().get('origin', 'Unknown')
                print(f"🏠 Normale IP-Adresse: {normal_ip}")
            except:
                print("🏠 Normale IP-Adresse: Nicht verfügbar")
            
            print()
            
            # Tor starten
            if not self.start_tor():
                return
            
            # Zeige Tor-IP
            tor_ip = self.get_current_ip()
            print(f"🔒 Tor IP-Adresse: {tor_ip}")
            print()
            
            # Versuche normalen Chrome zu starten
            print("🚀 Versuche Chrome normal zu starten...")
            if self.start_chrome():
                print("🎉 Chrome gestartet! Sie können jetzt normal surfen.")
                print("📱 Der Browser läuft unabhängig - schließen Sie das Terminal wenn gewünscht.")
                
                # Browser läuft, Script beendet sich
                print("✅ Script beendet - Browser und Tor laufen weiter!")
                return
            
            # Falls normaler Chrome nicht funktioniert, versuche headless
            print("⚠️  Normaler Chrome konnte nicht gestartet werden.")
            print("🤖 Starte headless Mode für HTML-Ausgabe...")
            
            if not self.start_chrome_headless():
                print("❌ Auch headless Chrome konnte nicht gestartet werden.")
                return
            
            # Demo: HTML von einer Seite holen
            print("\n📝 Beispiel: HTML-Ausgabe von httpbin.org")
            html = self.get_html("http://httpbin.org/ip")
            
            if html:
                print("\n" + "="*50)
                print("HTML-INHALT:")
                print("="*50)
                print(html[:1000])  # Erste 1000 Zeichen
                if len(html) > 1000:
                    print(f"\n... (weitere {len(html)-1000} Zeichen)")
                print("="*50)
            
            print("\n🚀 Headless Browser bereit für weitere Anfragen!")
            
        except Exception as e:
            print(f"❌ Fehler: {e}")
        
        finally:
            # Tor läuft weiter, nur Script beendet sich
            print("\n📊 Tor läuft weiter im Hintergrund.")

def main():
    browser = TorBrowser()
    browser.run()

if __name__ == "__main__":
    main()