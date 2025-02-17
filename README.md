# telegram-servermanager
Run shell commands on a linux host from a telegram bot.

## Description
Gives you the possibility to **run shell commands** on a linux host from a telegram bot with `/run`.  
You can also **manage services** with `/start`, `/stop` and `/run`, **WakeOnLan** is added by using `/wake`.  
It also **blacklists dangerous commands** like `rm -rf`, `shutdown`, `reboot`, `poweroff` and `halt`. You can extend this list!   

## Examples
/run:  
![tg-run](https://github.com/user-attachments/assets/255c3930-17c2-49aa-8b9a-46a951861286)

blacklisted command:  
![tgbot-blacklist](https://github.com/user-attachments/assets/6530fbe3-1c07-451f-8df9-4eb1e85959ec)

/wake (WakeOnLan):  
![tgbot-wol](https://github.com/user-attachments/assets/6f900c60-3cd5-4f5d-885d-64ee3eddd4ba)

/start (managing services):  
![tgbot-service](https://github.com/user-attachments/assets/65470b3b-2583-4879-96fb-26ed72c659d0)


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
  Select clients, that can get waked up with WakeOnLan and services, which can be managed with start, stop and status.  
     ```sh
     python3 setup.py  
     ```
* After the setup has finished, you can start the bot with telegram_servermanager.py  
     ```sh
     python3 telegram_servermanager.py  
     ```

#### Telegram bot:
* After starting `telegram_servermanager.py` your bot should say `Welcome! Use /run <command> to execute a shell command on your server.`
* Now you can start running commands with `/run`!

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

## Version History
* 1.1
    * change: blacklist is now optional and not forced
    * added: /wake to wake a client with WakeOnLan
    * added: /stop, /start, /status to manage system services
* 1.0
    * Initial Release

## Acknowledgments
* [Github - xgaia/serverbot](https://github.com/xgaia/serverbot?tab=readme-ov-file) for inspiration
* ChatGPT for helping me
