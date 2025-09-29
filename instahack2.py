import requests
import json



def get_instagram_profile(username):
    url = f"https://www.instagram.com/api/v1/users/web_profile_info/?username={username}"
    headers = {
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.9",
        "x-ig-app-id": "936619743392459"
    }
    response = requests.get(url, headers=headers)

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


def instagram_login(username, password):
    session = requests.Session()
    # Holen des CSRF-Tokens
    r = session.get("https://www.instagram.com/accounts/login/")
    csrf_token = r.cookies.get("csrftoken")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36",
        "X-CSRFToken": csrf_token,
        "Referer": "https://www.instagram.com/accounts/login/",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    login_data = {
        "username": username,
        "enc_password": f"#PWD_INSTAGRAM_BROWSER:0:&:{password}",  # Aktuelles Format für Passwort
        "queryParams": "{}",
        "optIntoOneTap": "false"
    }
    login_url = "https://www.instagram.com/accounts/login/ajax/"
    login_response = session.post(login_url, data=login_data, headers=headers)

    try:
        login_json = login_response.json()
    except json.JSONDecodeError:
        print("Fehler beim Verarbeiten der Login-Antwort.")
        return None

    if login_json.get("authenticated"):
        print("Login erfolgreich!")
        return session
    else:
        print("Login fehlgeschlagen:", login_json.get("message", "Unbekannter Fehler"))
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

if __name__ == "__main__":
    username = input("Instagram Username: ")
    password = input("Instagram Password: ")

    sess = instagram_login(username, password)
    if sess:
        print("Profilinformationen abrufen für:", username)
        profile = get_instagram_profile(username)
        if profile:
            for k, v in profile.items():
                print(f"{k}: {v}")
    else:
        print("Konnte kein Profil ohne Login abrufen oder Login fehlgeschlagen.")
