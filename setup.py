import os
import configparser
from cryptography.fernet import Fernet

CONFIG_FILE = "config.ini"
KEY_FILE = "secret.key"
DEFAULT_BLACKLIST = ["rm -rf", "shutdown", "reboot", "poweroff", "halt", "cat", "vim", "nano"]
DEFAULT_WHITELIST = ["uptime", "free -h", "df -ah"]

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

print("\nWelcome to the setup of your Telegram-Servermanager Bot!")
print("Installation guide / Repo: https://github.com/emodii/telegram-servermanager")

def get_user_input():
    # get bot_token and user-id from user
    bot_token = input("\nEnter your Telegram Bot Token: ").strip()
    user_id = input("Enter your Telegram User ID(s) (comma-separated): ").strip()
    
    key = load_key()
    encrypted_token = encrypt_token(bot_token, key)
    
    # Ask for whitelist or blacklist
    list_type = input("Do you want to use a whitelist or a blacklist? A whitelist is recommended and more secure! (Enter whitelist or blacklist): ").strip().lower()
    if list_type not in ["whitelist", "blacklist"]:
        list_type = "whitelist"
    
    if list_type == "whitelist":
        print("\nDefault whitelisted commands: " +  ", ".join(DEFAULT_WHITELIST))
        use_default_list = input("Do you want to use the default whitelist? (yes/no): ").strip().lower()
        command_list = DEFAULT_WHITELIST.copy() if use_default_list == "yes" else []
    else:
        print("\nDefault blacklisted commands: " + ", ".join(DEFAULT_BLACKLIST))
        use_default_list = input("Do you want to use the default blacklist? (yes/no): ").strip().lower()
        command_list = DEFAULT_BLACKLIST.copy() if use_default_list == "yes" else []

    print("\nNow you can enter additional commands to your " + (list_type) + ".")   
    extra_commands = input("Please enter the commands comma-separated, or press Enter to skip): ").strip()
    if extra_commands:
        command_list.extend([cmd.strip() for cmd in extra_commands.split(",")])
    
    config = configparser.ConfigParser()
    config["Telegram"] = {
        "bot_token": encrypted_token,
        "allowed_users": user_id
    }
    config["Security"] = {
        "list_type": list_type,
        "commands": ",".join(command_list)
    }
    
    # Ask for Wake-on-LAN clients
    print ("\nAdd clients you want to be able to wake up with WakeOnLan. Please make sure, that WakeOnLan is configured on your client!")
    config["WakeOnLAN"] = {}
    while True:
        client_input = input("Enter a client name and MAC address (example: gaming-server=01:12:23:34:45:56), or press Enter to finish: ").strip()
        if not client_input:
            break
        try:
            name, mac = client_input.split("=")
            config["WakeOnLAN"][name.strip()] = mac.strip()
        except ValueError:
            print("Invalid format. Please use Name=MAC.")
    
    # Ask for systemd services
    print ("\nAdd services you want to check with /status.")
    config["SystemdServices"] = {}
    while True:
        service_input = input("Enter a service name and systemd service file (example: zabbix=zabbix-agent2.service), or press Enter to finish: ").strip()
        if not service_input:
            break
        try:
            name, service = service_input.split("=")
            config["SystemdServices"][name.strip()] = service.strip()
        except ValueError:
            print("Invalid format. Please use Name=service.service.")
    
    with open(CONFIG_FILE, "w") as f:
        config.write(f)

    print(f"Configuration saved in {CONFIG_FILE}")

def main():
    # Runs the setup process
    get_user_input()
    print("Setup completed. Start the bot with: python3 telegram_servermanager.py")

if __name__ == "__main__":
    main()
