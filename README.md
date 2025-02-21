# :speech_balloon: telegram-servermanager
Run shell commands on a linux host from a telegram bot.

## Description
This project gives you the possibility to **run shell commands** on a linux host from a telegram bot.  
Functions:
* `/run`: run shell commands
* `/status`: check status of a service
* `/wake`: wake up clients in your network with WakeOnLan
* Choose between **whitelist** or **blacklist** for the commands you want to run. You can add commands to the list in the setup.  
* Logging: check the `bot_activity.log` to see, if someone is trying something evil.  

Use this bot carefully! Dont expose dangerous commands to it.  

## Examples
/run:  
![tg-run](https://github.com/user-attachments/assets/255c3930-17c2-49aa-8b9a-46a951861286)

/wake (WakeOnLan):  
![tgbot-wol](https://github.com/user-attachments/assets/6f900c60-3cd5-4f5d-885d-64ee3eddd4ba)

whitelist:  
![tgbot-whitelist](https://github.com/user-attachments/assets/f833d8c2-38df-478e-a688-a379099555e1)

Logging:  
![tgbot-log](https://github.com/user-attachments/assets/0d081cba-5b31-4002-8573-d746f88e26e1)

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
#### Telegram:
Get a Telegram bot token:  
* You need a telegram bot. To do this, send the command `/newbot` to [BotFather](https://t.me/botfather). Safely secure your token.  
* Add the used commands to your bot with `/setcommands`:
     ```
     run - run a command on your server
     wake - wake a client up with WakeOnLan
     status - get status of a service
     ```
Get your Telegram user_id:  
* Send the message `/start` to [userinfobot](https://t.me/userinfobot) to get your user id. Safely secure your user_id.  

#### On your linux server:
* Security notice: Create a new user with low privileges to run the bot (Example: "tgbot").  
  You can run it as root, but i highly recommend to use a low privilege user!  
     ```sh
     sudo adduser tgbot
     ```  
* Install dependencies:  
     ```sh
     # Debian/Ubuntu
     sudo apt install python3 python3-pip python3-venv wakeonlan
     ```
* Clone the repository, create directory for log and change permissions for your low privilege user
     ```sh
     git clone https://github.com/emodii/telegram-servermanager.git
     # give your new user permission to the scripts and login as tgbot
     chown -R tgbot:tgbot telegram-servermanager && su - tgbot
     cd telegram-servermanager
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
* Run setup.py to start the setup. You will get asked for your `bot-token` and your `user_id`.  
  Choose, if you want to use the blacklist and add more commands to it.  
  Select clients, that can get waked up with WakeOnLan and services, which can be status checked.  
     ```sh
     python3 setup.py  
     ```
* After the setup has finished, you can start the bot with telegram_servermanager.py  
     ```sh
     python3 telegram_servermanager.py  
     ```

#### Telegram bot:
* After starting `telegram_servermanager.py` your bot should say `Welcome! Use /run <command> to execute a shell command on your server.`
* Now you can start running commands with `/run`, use WakeOnLan with `/wake` and check the status of your configured services with `/status`!

#### Logging:  
* You can view your log with `tail -f /var/log/telegram-servermanager/bot_activity.log`
---

### Run the servermanger as a service

Create the file `/etc/systemd/system/tg-servermanager.service` with following input. Replace `/path/to` with your path, where the directory `telegram_servermanager` is placed.    

```
[Unit]
Description=Telegram Servermanager
After=network.target
[Service]
ExecStart=/path/to/telegram-servermanager/venv/bin/python /path/to/telegram-servermanager/telegram_servermanager.py
WorkingDirectory=/path/to/telegram-servermanager/
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

---

## Troubleshooting
If you have any problems, please check:
* if your telegram bot token and user_id is correct
* ensure that the permissions on the scripts are correct
* run the `setup.py` file again
* check the log-file in your telegram-servermanager directory (`bot_activity.log`)

## Version History
* 1.3
    * added: logging, check your log: `bot_activity.log`
* 1.2
    * added: whitelist option, choose between whitelist and blacklist
    * more explanations when running the setup
* 1.1.1
    * removed: /stop and /start to manage system services (due to sudo security issues)
* 1.1
    * change: blacklist is now optional and not forced
    * added: /wake to wake a client with WakeOnLan
    * added: /stop, /start, /status to manage system services
* 1.0
    * Initial Release

## To-Do
* security: get a more secure solution to run sudo commands, maybe with a wrapper script with contolled permissions
* let user add own custom commands for the bot in the setup to the whitelist
* add commands to manage docker containers?

## Acknowledgments
* [Github - xgaia/serverbot](https://github.com/xgaia/serverbot?tab=readme-ov-file) for inspiration
* Reddit: the `r/selfhosted` community
* ChatGPT for helping me
