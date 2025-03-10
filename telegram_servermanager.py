import os
import configparser
import subprocess
import logging
from cryptography.fernet import Fernet
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Configuration file
CONFIG_FILE = "config.ini"
KEY_FILE = "secret.key"
LOG_FILE = "bot_activity.log"

# Logging setup
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# deactivate info logs from httpx and telegram
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("telegram").setLevel(logging.WARNING)

def user_info(update: Update) -> str:
    # Returns a standardized string with user information for logging.
    user = update.effective_user
    username = user.username if user.username else f"{user.first_name} {user.last_name or ''}".strip()
    return f"User {username} (ID: {user.id})"

def load_key():
    # Loads the encryption key
    if not os.path.exists(KEY_FILE):
        print("Error: Encryption key not found. Run setup.py first.")
        exit(1)
    with open(KEY_FILE, "rb") as key_file:
        return key_file.read()

def decrypt_token(encrypted_token, key):
    """Decrypts the Bot Token"""
    cipher = Fernet(key)
    return cipher.decrypt(encrypted_token.encode()).decode()

try:
    # Load configuration file
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)

    # Load encryption key
    key = load_key()
    encrypted_token = config["Telegram"]["bot_token"]
    BOT_TOKEN = decrypt_token(encrypted_token, key)
    ALLOWED_USERS = set(map(int, config["Telegram"]["allowed_users"].split(",")))

    MODE = config["Security"].get("mode", "whitelist")  # Standard: Whitelist
    
    if MODE == "blacklist":
        BLOCKED_COMMANDS = config["Security"].get("commands", "").split(",")
    else:
        ALLOWED_COMMANDS = config["Security"].get("commands", "").split(",")
    
    # Load Wake-on-LAN clients
    WOL_CLIENTS = dict(config["WakeOnLAN"]) if "WakeOnLAN" in config else {}

    # Load systemd services
    SYSTEMD_SERVICES = dict(config["SystemdServices"]) if "SystemdServices" in config else {}

except (KeyError, ValueError):
    print("Error: Configuration file not found or invalid. Please run setup.py first.")
    exit(1)


async def run_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id

    if user_id not in ALLOWED_USERS:
        logging.warning(f"{user_info(update)} attempted to run command and is not in ALLOWED_USERS")
        await update.message.reply_text("Access denied.")
        return

    command = " ".join(context.args)
    if not command:
        logging.info(f"{user_info(update)} attempted to run an empty command.")
        await update.message.reply_text("Please provide a command to execute.")
        return

    if MODE == "blacklist":
        for bad_cmd in BLOCKED_COMMANDS:
            if bad_cmd in command:
               logging.warning(f"{user_info(update)} executed blacklisted command: '{command}'") 
               await update.message.reply_text(f"Command '{command}' is not allowed.")
               return
    else:
        if command not in ALLOWED_COMMANDS:
            logging.warning(f"{user_info(update)} executed forbidden command: '{command}'.")
            await update.message.reply_text(f"Command '{command}' is not in the whitelist.")
            return

    try:
        output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT, text=True, timeout=10)
        output = output.strip() if output else "Command executed successfully, but no output was returned."
    except subprocess.CalledProcessError as e:
        output = f"Error:\n{e.output}"
    except Exception as e:
        output = f"Error: {str(e)}"

    if len(output) > 4000:
        output = output[:4000] + "\n... [truncated]"

    logging.info(f"{user_info(update)} executed command: '{command}'")
    await update.message.reply_text(f"Output:\n{output}")

async def wake_on_lan(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Sends a Wake-on-LAN packet to a predefined machine
    user_id = update.effective_user.id

    if user_id not in ALLOWED_USERS:
        logging.warning(f"{user_info(update)} attempted to run command and is not in ALLOWED_USERS")
        await update.message.reply_text("Access denied.")
        return

    if not context.args:
        logging.info(f"{user_info(update)} attempted to run an empty WakeOnLan command.")
        await update.message.reply_text("Usage: /wake <ClientName>")
        return

    client_name = context.args[0]
    
    if client_name not in WOL_CLIENTS:
        logging.info(f"{user_info(update)} attempted to wake a unknown client '{client_name}'.")
        await update.message.reply_text(f"Client '{client_name}' not found in Wake-on-LAN list.")
        return

    mac_address = WOL_CLIENTS[client_name]
    try:
        subprocess.run(["wakeonlan", mac_address], check=True)
        logging.info(f"{user_info(update)} executed /wake command: '{client_name}'")
        await update.message.reply_text(f"Wake-on-LAN packet sent to {client_name}.")
    except Exception as e:
        logging.info(f"{user_info(update)} executed /wake command, but it failed. ")
        await update.message.reply_text(f"Failed to send Wake-on-LAN packet: {str(e)}")

async def manage_service(update: Update, context: ContextTypes.DEFAULT_TYPE, action: str) -> None:
    # checks the status of a systemd service
    user_id = update.effective_user.id

    if user_id not in ALLOWED_USERS:
        logging.warning(f"{user_info(update)} attempted to run command and is not in ALLOWED_USERS")
        await update.message.reply_text("Access denied.")
        return

    if not context.args:
        logging.info(f"{user_info(update)} attempted to run an empty /status command.")
        await update.message.reply_text(f"Usage: /status <ServiceName>")
        return

    service_name = context.args[0]
    
    if service_name not in SYSTEMD_SERVICES:
        logging.info(f"{user_info(update)} attempted to check status of unknown service '{service_name}'.")
        await update.message.reply_text(f"Service '{service_name}' not found in service list.")
        return

    service_file = SYSTEMD_SERVICES[service_name]
    try:
        if action == "status":
            result = subprocess.run(["systemctl", "status", service_file], capture_output=True, text=True)
            output = result.stdout.split("\n")[:10]  # Limit output to avoid long messages
            logging.info(f"{user_info(update)} executed /status command: '{service_name}'")
            await update.message.reply_text(f"Status of '{service_name}':\n" + "\n".join(output))
    except Exception as e:
        logging.info(f"{user_info(update)} executed /status command, but it failed.")
        await update.message.reply_text(f"Failed to /status service: {str(e)}")

async def status_service(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await manage_service(update, context, "status")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Welcome! Use /run <command> to execute a shell command on your server. Use /wake <ClientName> to wake up a machine.")

def main():
    # Starts the Telegram bot
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("status", status_service))
    app.add_handler(CommandHandler("run", run_command))
    app.add_handler(CommandHandler("wake", wake_on_lan))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
