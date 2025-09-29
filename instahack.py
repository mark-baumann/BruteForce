import sys
import logging
import time
from browser.run_browser import BrowserSession  # Deine BrowserSession-Klasse
from proxy import TorProxy  # Deine TorProxy-Klasse

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

# Logging Setup
logger = logging.getLogger(__name__)
if not logger.handlers:
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    sh = logging.StreamHandler()
    sh.setFormatter(formatter)
    logger.addHandler(sh)


def wait_for_tor_circuit(tor_proxy, timeout=30):
    for _ in range(timeout):
        exit_ip = tor_proxy.get_exit_ip()
        if exit_ip:
            return exit_ip
        time.sleep(1)
    return None


def instagram_login_via_browser(session: BrowserSession, username: str, password: str) -> bool:
    driver = session.browser_proxy.driver  # Korrigierter Zugriff auf den Selenium Webdriver

    driver.get("https://www.instagram.com/accounts/login/")
    time.sleep(5)

    user_input = driver.find_element(By.NAME, "username")
    user_input.clear()
    user_input.send_keys(username)

    pass_input = driver.find_element(By.NAME, "password")
    pass_input.clear()
    pass_input.send_keys(password)
    pass_input.send_keys(Keys.RETURN)

    time.sleep(8)

    current_url = driver.current_url
    if "challenge" in current_url:
        print("Login-Challenge erkannt.")
        return False
    elif "two_factor" in current_url:
        print("Zwei-Faktor-Authentifizierung erforderlich.")
        return False
    elif "instagram.com" in current_url:
        print("Login erfolgreich!")
        return True
    else:
        print(f"Login möglicherweise fehlgeschlagen. Aktuelle URL: {current_url}")
        return False



def main():
    import sys
    if len(sys.argv) < 2:
        print("Nutzung: python instagram_selenium_login.py <ziel_url>")
        sys.exit(1)

    target_url = sys.argv[1]

    tor = TorProxy()

    # Prüfen, ob Tor bereits läuft; falls nicht, starten
    if tor.is_tor_running():
        print("Tor läuft bereits.")
    else:
        print("Tor läuft nicht, starte Tor...")
        if tor.start_tor():
            print("Tor erfolgreich gestartet.")
        else:
            print("Fehler beim Starten von Tor.")
            sys.exit(1)

    # BrowserSession mit TorProxy starten (sichtbar)
    session = BrowserSession(tor_proxy=tor)
    if not session.start():
        logger.error("Browser konnte nicht gestartet werden.")
        sys.exit(2)

    logger.info("Warte auf Aufbau der Tor-Circuit...")
    exit_ip = wait_for_tor_circuit(tor, timeout=30)
    if exit_ip:
        print(f"Tor Exit-IP: {exit_ip}")
        logger.info(f"Tor Exit-IP: {exit_ip}")
    else:
        print("Tor Exit-IP unbekannt (Timeout)")
        logger.warning("Tor Exit-IP unbekannt")

    username = input("Instagram Username: ")
    password = input("Instagram Password: ")

    if not instagram_login_via_browser(session, username, password):
        logger.error("Login fehlgeschlagen.")
        session.close()
        sys.exit(3)

    if not session.visit(target_url):
        logger.error(f"Konnte die URL nicht laden: {target_url}")
        session.close()
        sys.exit(4)

    print(f"✓ Zielseite {target_url} geöffnet.")
    print("Bitte schließe den Browser manuell, um das Programm zu beenden.")
    session.wait_until_closed()
    session.close()



if __name__ == "__main__":
    main()
