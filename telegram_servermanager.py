import os
import configparser
import subprocess
from cryptography.fernet import Fernet
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Configuration file
CONFIG_FILE = "config.ini"
KEY_FILE = "secret.key"

def load_key():
    """Loads the encryption key"""
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

    # Load blacklisted commands from config
    BLACKLISTED_COMMANDS = config["Security"]["blacklisted_commands"].split(",")

except (KeyError, ValueError):
    print("Error: Configuration file not found or invalid. Please run setup.py first.")
    exit(1)

async def run_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Executes a shell command and returns the output"""
    user_id = update.effective_user.id

    if user_id not in ALLOWED_USERS:
        await update.message.reply_text("Access denied.")
        return

    command = " ".join(context.args)
    if not command:
        await update.message.reply_text("Please provide a command to execute.")
        return

    # Check if the command contains any blacklisted keywords
    for bad_cmd in BLACKLISTED_COMMANDS:
        if bad_cmd in command:
            await update.message.reply_text(f"Command '{command}' is not allowed.")
            return

    try:
        # Execute the shell command
        output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT, text=True, timeout=10)
        output = output.strip() if output else "Command executed successfully, but no output was returned."
    except subprocess.CalledProcessError as e:
        output = f"Error:\n{e.output}"
    except Exception as e:
        output = f"Error: {str(e)}"

    # Limit output length to avoid exceeding Telegram message size
    if len(output) > 4000:
        output = output[:4000] + "\n... [truncated]"

    await update.message.reply_text(f"Output:\n{output}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles the /start command"""
    await update.message.reply_text("Welcome! Use /run <command> to execute a shell command on your server.")

def main():
    """Starts the Telegram bot"""
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("run", run_command))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
