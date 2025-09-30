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
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                             "AppleWebKit/537.36 (KHTML, like Gecko) "
                             "Chrome/114.0.0.0 Safari/537.36")
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-extensions")
        options.add_argument("--no-sandbox")
        options.add_argument("--incognito")

        # Deaktiviere Automation Flags
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)

        if self.tor_proxy:
            proxy_url = self.tor_proxy.get_proxy_url()
            #options.add_argument(f'--proxy-server={proxy_url}')

        self.driver = webdriver.Chrome(options=options)

        # Anti-Detection Script
        self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': '''
                Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                window.navigator.chrome = { runtime: {} };
                Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
                Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
            '''
        })

        self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': '''
                Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                window.navigator.chrome = { runtime: {} };
                Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
                Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
                const originalQuery = window.navigator.permissions.query;
                window.navigator.permissions.query = (parameters) => (
                    parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
                );
            '''
        })

        # Weitere Detektion abschwächen – setze window.navigator.permissions.query
        self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': '''
                const originalQuery = window.navigator.permissions.query;
                window.navigator.permissions.query = (parameters) => (
                    parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
                );
            '''
        })

        return True

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
