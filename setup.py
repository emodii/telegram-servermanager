import os
import configparser
import subprocess
from cryptography.fernet import Fernet

CONFIG_FILE = "config.ini"
KEY_FILE = "secret.key"
DEFAULT_BLACKLIST = ["rm -rf", "shutdown", "reboot", "poweroff", "halt"]

def generate_key():
    """Generates a secret key and saves it to a file"""
    key = Fernet.generate_key()
    with open(KEY_FILE, "wb") as key_file:
        key_file.write(key)
    return key

def load_key():
    """Loads the secret key from a file"""
    if not os.path.exists(KEY_FILE):
        return generate_key()
    with open(KEY_FILE, "rb") as key_file:
        return key_file.read()

def encrypt_token(token, key):
    """Encrypts the Bot Token using AES"""
    cipher = Fernet(key)
    return cipher.encrypt(token.encode()).decode()

def get_user_input():
    """Asks for the Telegram Bot Token, allowed user IDs, and blacklisted commands"""
    bot_token = input("Enter your Telegram Bot Token: ").strip()
    user_id = input("Enter your Telegram User ID(s) (comma-separated): ").strip()

    key = load_key()  # Load or generate encryption key
    encrypted_token = encrypt_token(bot_token, key)

    print("\nDefault blacklisted commands:")
    print(", ".join(DEFAULT_BLACKLIST))
    extra_blacklist = input("\nEnter additional commands to blacklist (comma-separated, or press Enter to skip): ").strip()

    # Merge default blacklist with user input
    blacklist = DEFAULT_BLACKLIST.copy()
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

    with open(CONFIG_FILE, "w") as f:
        config.write(f)

    print(f"Configuration saved in {CONFIG_FILE}")

def main():
    """Runs the setup process"""
    get_user_input()
    print("Setup completed. Start the bot with: python3 telegram_servermanager.py")

if __name__ == "__main__":
    main()
