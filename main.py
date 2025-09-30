#!/usr/bin/env python3
import os
import subprocess
import sys


def create_venv():
    if not os.path.exists(".venv"):
        print("[Setup] Erstelle virtuelle Umgebung (.venv)...")
        subprocess.run([sys.executable, "-m", "venv", ".venv"])
    print("[Setup] Aktiviere virtuelle Umgebung...")
    activate_script = ".venv/bin/activate"
    command = f"source {activate_script}"
    subprocess.call(command, shell=True)


def install_requirements():
    print("[Setup] Upgrade pip und installiere Requirements...")
    subprocess.run([".venv/bin/pip", "install", "--upgrade", "pip"])
    if os.path.exists("requirements.txt"):
        subprocess.run([".venv/bin/pip", "install", "-r", "requirements.txt"])
    else:
        print("[Setup] Keine requirements.txt gefunden.")


def check_tor():
    print("[Tor] Prüfe ob Tor läuft...")
    result = subprocess.run(["pgrep", "tor"], capture_output=True, text=True)
    if result.returncode != 0:
        print("[Tor] Starte Tor-Proxy...")
        subprocess.Popen(["tor"])
        return True
    else:
        print("[Tor] Tor läuft bereits.")
        return True


def run_browser_with_proxy(url):
    # Browser mit Proxy starten
    print(f"[Proxy] Starte Browser mit Proxy für: {url}")
    subprocess.call([sys.executable, "-m", "browser.run_browser", url])


def run_instahack(url):
    # Instahack mit URL starten
    print(f"[Instahack] Starte Instahack für: {url}")
    subprocess.call([sys.executable, "instahack.py", url])


def cool_banner():
    print(r"""
  _____           _     _               _         _             
 |_   _|         | |   | |             (_)       | |            
   | |  _ __  ___| |__ | |__   ___  ___ _   ___ | | _____ _ __ 
   | | | '_ \/ __| '_ \| '_ \ / _ \/ __| | / _ \| |/ / _ \ '__|
  _| |_| | | \__ \ | | | | | |  __/\__ \ | | (_) |   <  __/ |   
 |_____|_| |_|___/_| |_|_| |_|\___||___/_|  \___/|_|\_\___|_|   

    """)


def main_menu():
    cool_banner()
    print("Wähle eine Option:")
    print("[1] Browser mit Proxy starten")
    print("[2] Instagram hacken")
    print("[3] Beenden")
    choice = input("\nEingabe (1/2/3): ").strip()
    return choice


def main():
    create_venv()
    install_requirements()
    os.environ["PYTHONPATH"] = os.path.dirname(os.path.abspath(__file__))
    check_tor()
    while True:
        choice = main_menu()
        if choice == "1":
            url = input("URL für Browser: ").strip()
            run_browser_with_proxy(url)
        elif choice == "2":
            url = input("Instagram-Profil-URL: ").strip()
            run_instahack(url)
        elif choice == "3":
            print("Beende das Programm.")
            break
        else:
            print("Ungültige Eingabe. Bitte erneut versuchen.")


if __name__ == "__main__":
    main()
