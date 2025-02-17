import os
import configparser
from cryptography.fernet import Fernet

CONFIG_FILE = "config.ini"
KEY_FILE = "secret.key"
DEFAULT_BLACKLIST = ["rm -rf", "shutdown", "reboot", "poweroff", "halt", "cat", "vim", "nano"]

def generate_key():
    # Generates a secret key and saves it to a file
    key = Fernet.generate_key()
    with open(KEY_FILE, "wb") as key_file:
        key_file.write(key)
    return key

def load_key():
    # Loads the secret key from a file
    if not os.path.exists(KEY_FILE):
        return generate_key()
    with open(KEY_FILE, "rb") as key_file:
        return key_file.read()

def encrypt_token(token, key):
    # Encrypts the Bot Token using AES
    cipher = Fernet(key)
    return cipher.encrypt(token.encode()).decode()

def get_user_input():
    # Asks for the Telegram Bot Token, allowed user IDs, blacklisted commands, WOL clients, and services
    bot_token = input("Enter your Telegram Bot Token: ").strip()
    user_id = input("Enter your Telegram User ID(s) (comma-separated): ").strip()

    key = load_key()  # Load or generate encryption key
    encrypted_token = encrypt_token(bot_token, key)

    print("\nDefault blacklisted commands:")
    print(", ".join(DEFAULT_BLACKLIST))
    use_default_blacklist = input("Do you want to use the default blacklist? (yes/no): ").strip().lower()
    
    if use_default_blacklist == "yes":
        blacklist = DEFAULT_BLACKLIST.copy()
    else:
        blacklist = []
    
    extra_blacklist = input("Enter additional commands to blacklist (comma-separated, or press Enter to skip): ").strip()
    
    if extra_blacklist:
        blacklist.extend([cmd.strip() for cmd in extra_blacklist.split(",")])
    
    config = configparser.ConfigParser()
    config["Telegram"] = {
        "bot_token": encrypted_token,
        "allowed_users": user_id
    }
    config["Security"] = {
        "blacklisted_commands": ",".join(blacklist)
    }
    
    # Ask for Wake-on-LAN clients
    config["WakeOnLAN"] = {}
    while True:
        client_input = input("Enter a client name and MAC address (format: Name=MAC), or press Enter to finish: ").strip()
        if not client_input:
            break
        try:
            name, mac = client_input.split("=")
            config["WakeOnLAN"][name.strip()] = mac.strip()
        except ValueError:
            print("Invalid format. Please use Name=MAC.")
    
    # Ask for systemd services
    config["SystemdServices"] = {}
    while True:
        service_input = input("Enter a service name and systemd service file (format: name=service.service), or press Enter to finish: ").strip()
        if not service_input:
            break
        try:
            name, service = service_input.split("=")
            config["SystemdServices"][name.strip()] = service.strip()
        except ValueError:
            print("Invalid format. Please use name=service.service.")
    
    with open(CONFIG_FILE, "w") as f:
        config.write(f)

    print(f"Configuration saved in {CONFIG_FILE}")

def main():
    # Runs the setup process
    get_user_input()
    print("Setup completed. Start the bot with: python3 telegram_servermanager.py")

if __name__ == "__main__":
    main()
