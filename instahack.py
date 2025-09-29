from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import time


def selenium_instagram_login(username, password):
    options = Options()
    options.add_argument("--headless")  # Ohne GUI, entferne für Debug
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(options=options)
    driver.get("https://www.instagram.com/accounts/login/")

    time.sleep(5)  # Warte bis Seite geladen

    # Benutzername eingeben
    user_input = driver.find_element(By.NAME, "username")
    user_input.clear()
    user_input.send_keys(username)

    # Passwort eingeben
    pass_input = driver.find_element(By.NAME, "password")
    pass_input.clear()
    pass_input.send_keys(password)

    pass_input.send_keys(Keys.RETURN)

    # Warte auf Login-Prozess
    time.sleep(8)

    # Prüfen, ob Login erfolgreich
    if "accounts/onetap" in driver.current_url or "challenge" in driver.current_url:
        print("Login eventuell blockiert oder Checkpoint erkannt.")
        driver.quit()
        return False

    if "instagram.com" in driver.current_url:
        print("Login erfolgreich!")
        driver.quit()
        return True
    else:
        print("Login fehlgeschlagen oder andere Seite:", driver.current_url)
        driver.quit()
        return False


if __name__ == "__main__":
    username = input("Instagram Username: ")
    password = input("Instagram Password: ")

    success = selenium_instagram_login(username, password)
    print("Ergebnis Login:", success)
