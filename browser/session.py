from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import logging
import time

logger = logging.getLogger(__name__)

class BrowserSession:
    def __init__(self, tor_proxy=None):
        self.tor_proxy = tor_proxy
        self.driver = None

    def start(self):
        options = Options()
        options.add_argument("--window-size=1920,1080")
        # Tor Proxy SOCKS5 über localhost 9050, falls TorProxy gesetzt
        if self.tor_proxy:
            options.add_argument("--proxy-server=socks5://127.0.0.1:9050")

        try:
            self.driver = webdriver.Chrome(options=options)
            logger.info("Chrome gestartet")
            return True
        except Exception as e:
            logger.error(f"Fehler beim Starten von Chrome: {e}")
            return False

    def visit(self, url):
        if not self.driver:
            logger.error("Browser nicht gestartet")
            return False
        try:
            self.driver.get(url)
            return True
        except Exception as e:
            logger.error(f"Fehler beim Laden der Seite: {e}")
            return False

    def wait_until_closed(self):
        try:
            while True:
                # Prüfe, ob Browser noch offen ist
                if self.driver.service.process.poll() is not None:
                    break
                time.sleep(1)
        except KeyboardInterrupt:
            self.close()

    def close(self):
        if self.driver:
            self.driver.quit()
            logger.info("Browser geschlossen")
