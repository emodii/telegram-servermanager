# telegram-servermanager
Run shell commands on a linux host from a telegram bot.

## Description
Gives you the possibility to run shell commands on a linux host from a telegram bot with `/run`.  
It also blacklists dangerous commands like "rm -rf", "shutdown", "reboot", "poweroff", "halt". You can add more commands while running setup.py.  
The user_id and bot token get encrypted with AES.  

Example:  
![telegram-servermanager_example](https://github.com/user-attachments/assets/b988d424-66a0-4aec-a461-3ff9e092a38f)
  
Tested with:    
* Debian 12 Server  
* Python3: python-telegram-bot==21.10, cryptography==44.0.1
* Telegram

## Getting Started  
### Dependencies  
* Linux server with root shell access  
* Python3 installed on the server 
* Telegram bot  

### Installing
#### Get a Telegram bot token:  
* You need a telegram bot. To do this, send the command `/newbot` to [BotFather](https://t.me/botfather). Safely secure your token.  

#### Get your Telegram user_id:  
* Send the message `/start` to [userinfobot](https://t.me/userinfobot) to get your user id. Safely secure your user_id.  

#### On your linux server:

* Security notice: Create a new user with low privileges to run the bot.  
     ```sh
     sudo adduser tgbot
     ```  
* Install dependencies:  
     ```sh
     # Debian/Ubuntu
     sudo apt install python3 python3-pip python3-venv
     ```
* Clone the repository: 
     ```sh
     git clone https://github.com/emodii/telegram-servermanager.git
     # give your new user permission to the scripts and login as tgbot
     chown -R tgbot:tgbot servermanager && su - tgbot
     cd servermanager
     ``` 
* Create a new python3 venv and activate it
     ```sh
     mkdir venv
     python3 -m venv venv
     source venv/bin/activate
     ```  
* Install the python3 requirements  
     ```sh
     pip install -r requirements.txt
     ```
* Run setup.py to start the setup. You will get asked for your `bot-token`, `user_id` and additional `blacklist commands`. This will create a config.ini file.  
     ```sh
     python3 setup.py  
     ```
* Secure your config.ini and secret.key
     ```sh
     chmod 600 config.ini secret.key
     ```
* After the setup has finished, you can start the bot with telegram_shell_bot.py
     ```sh
     python3 telegram_servermanager.py  
     ```

#### Telegram bot:
* After starting `telegram_servermanager.py` your bot should say `Welcome! Use /run <command> to execute a shell command on your server.`
* Now you can start running commands with `/run`!

---

### Run the servermanger as a service

Create the file `/etc/systemd/system/tg-servermanager.service` with following input. Replace `/path/to` with your path, where the directory `servermanger` is placed.    

```
[Unit]
Description=Telegram Servermanager
After=network.target
[Service]
ExecStart=/path/to/servermanager/venv/bin/python /path/to/servermanager/telegram_shell_bot.py
WorkingDirectory=/path/to/servermanager/
Restart=always
User=tgbot
Group=tgbot
[Install]
WantedBy=multi-user.target
```

Now you can use the service via systemctl like any other!
```sh
systemctl start tg-servermanager.service
```

## Version History
* 0.1
    * Initial Release

## Acknowledgments
* [Github - xgaia/serverbot](https://github.com/xgaia/serverbot?tab=readme-ov-file) for inspiration
