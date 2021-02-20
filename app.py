from flask import Flask, request
import os
import telegram
from credentials import BOT_TOKEN, URL
import buda


global bot
global TOKEN

TOKEN = BOT_TOKEN
bot = telegram.Bot(token=TOKEN)

app = Flask(__name__)


@app.route('/{}'.format(TOKEN), methods=['POST'])
def respond():
    update = telegram.Update.de_json(request.get_json(force=True), bot)

    chat_id = update.message.chat_id

    incoming_message = update.message.text.encode("utf-8").decode().lower()
    command = incoming_message.split()[0]
    response_message = ""

    # Check the incoming command and create response
    if command == "/info":
        try:
            data = buda.btc_data()
            response_message = f"Min ask: {data['min_ask']}, \n24h vol: {data['vol']}, \n24h var: {data['var_24h']}, \n7d var: {data['var_7d']}"
        except Exception as e:
            response_message = f"An error has occurred: {str(e)}"
    elif command == "/balance":
        try:
            data = buda.current_balance()
            response_message = f"BTC: {data['BTC']} ({data['converted_btc']}CLP), \nCLP: {data['CLP']}"
        except Exception as e:
            response_message = f"An error has occurred: {str(e)}"
    elif command == "/convert":
        try:
            split_message = incoming_message.split()
            amount = split_message[1]
            currency = split_message[2]
            converted = buda.convert(split_message[1], split_message[2])

            if currency == "clp":
                response_message = f"{amount}{currency} is equal to {converted}BTC"
            elif currency == "btc":
                response_message = f"{amount}{currency} is equal to {converted}CLP"
            else:
                response_message = f"Error: The currency youre converting must be either CLP or BTC"
        except Exception as e:
            response_message = f"An error has occurred: {str(e)}"
    elif command == "/order":
        try:
            split_message = incoming_message.split()

            if split_message[1] == "create":
                data = buda.generate_order(
                    direction=split_message[2],
                    btc_amount=split_message[3]
                )

                response_message = f"""Order created successfully! \n Order details: \n \nOrder ID: {data['order_id']}, 
                \nMarket ID: {data['market_id']}, \nType: {data['type']}, \nStatus: {data['status']}, \nOrdered: {data['amount']}"""
            elif split_message[1] == "status":
                data = buda.order_status(
                    order_id=split_message[2]
                )

                response_message = f"""Order ID: {data['order_id']}, \nMarket ID: {data['market_id']}, \nType: {data['type']}, 
                \nStatus: {data['status']}, \nTraded: {data['traded_amount']}, \nPaid: {data['paid']}, \nFee: {data['fee']}"""
            elif split_message[1] == "cancel":
                data = buda.cancel_order(
                    order_id=split_message[2]
                )

                response_message = data
            else:
                # Cuando split_message[1] existe pero no es un subcommand valido
                response_message = "I can't understand. \nCommand should be: /order [create | status | cancel]."
        except IndexError:
            # Cuando split_message[1] no existe
            response_message = "I can't understand. \nCommand should be: /order [create | status | cancel]."
    else:
        # Cuando el main command no es uno valido
        response_message = "I don't understand :("

    # Send response
    try:
        bot.sendMessage(chat_id=chat_id, text=response_message)
        return "Response sent successfully"
    except Exception as e:
        print(f"Error: {str(e)}")
        return f"Failed to send response. An error has occurred. Error: {str(e)}"


@app.route('/set_webhook', methods=['GET', 'POST'])
def set_webhook():
    s = bot.setWebhook('{URL}{HOOK}'.format(URL=URL, HOOK=TOKEN))

    if s:
        return "Webhook setup successful"
    else:
        return "Webhook setup failed"


@app.route('/')
def index():
    return '.'


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, threaded=True)
