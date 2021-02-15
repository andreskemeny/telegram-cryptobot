# Telegram Cryptobot

Turn Telegram into a Buda.com interface.

## Getting Started

### Setting up your files

To get the bot working the first thing you need to do is clone the repo:

```console
git clone https://github.com/andreskemeny/telegram-cryptobot.git
```

Create a `credentials.py` file with the following structure:

```python
API_KEY = 'your buda api key'
SECRET = 'your buda secret key'

BOT_TOKEN = 'your telegram bot token'
URL = 'your heroku app url'
``` 
You'll get the `API_KEY` and `SECRET` from your [Buda.com](https://www.buda.com/) account, the `BOT_TOKEN` from Telegram and `URL` from your Heroku app.

### Uploading the bot to Heroku

With a Heroku app created, get the Heroku Git URL and push your changes there — assuming your `credentials.py` file was set up correctly, once you push to Heroku, the bot should be deployed.


## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.


## License
[MIT](https://choosealicense.com/licenses/mit/)
