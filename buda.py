import requests
import requests.auth
import time
import hmac
import base64

import credentials


class BudaHMACAuth(requests.auth.AuthBase):
    """Adjunta el HMAC auth de buda al request"""

    def __init__(self, api_key: str, secret: str):
        self.api_key = api_key
        self.secret = secret

    def get_nonce(self) -> str:
        # generate nonce using timestamp
        return str(int(time.time() * 1e6))

    def sign(self, r, nonce: str) -> str:
        components = [r.method, r.path_url]

        if r.body:
            encoded_body = base64.b64encode(r.body).decode()
            components.append(encoded_body)

        components.append(nonce)

        msg = " ".join(components)

        h = hmac.new(key=self.secret.encode(),
                     msg=msg.encode(), digestmod="sha384")
        signature = h.hexdigest()
        return signature

    def __call__(self, r):
        nonce = self.get_nonce()
        signature = self.sign(r, nonce)

        r.headers['X-SBTC-APIKEY'] = self.api_key
        r.headers['X-SBTC-NONCE'] = nonce
        r.headers['X-SBTC-SIGNATURE'] = signature
        return r


def btc_data() -> dict:
    """
    Returns a string to be sent in message response through 
    telegram with BTC data (min ask, vol, 24h var, 7d var)
    """

    try:
        url = 'https://www.buda.com/api/v2/markets/btc-clp/ticker'
        res = requests.get(url).json()["ticker"]

        data = {
            "min_ask": res["min_ask"][0] + " CLP",
            "vol": res["volume"][0] + " BTC",
            "var_24h": res["price_variation_24h"] + "%",
            "var_7d": res["price_variation_7d"] + "%"
        }

        return data
    except Exception as e:
        print(f"An error has occurred while calling {url}: {str(e)}")
        return f"An error has occurred in btc_data(), error: {str(e)}"


def convert(amount: float, currency: str) -> str:
    """Convert currencies (BTC to CLP or CLP to BTC), returns str with result"""

    try:
        url = 'https://www.buda.com/api/v2/markets/btc-clp/ticker'
        res = requests.get(url)
        min_ask = res.json()["ticker"]["min_ask"][0]

        if currency == "clp":
            return float(amount)/float(min_ask)
        elif currency == "btc":
            return float(amount)*float(min_ask)
        else:
            return f"Error: The currency youre converting must be either CLP or BTC"
    except Exception as e:
        print(f"An error has occurred in convert_to_btc(), error: {str(e)}")
        return f"An error has occurred in convert_to_btc(), error: {str(e)}"


def current_balance() -> dict:
    """
    Returns a string to be sent in message response through telegram
    with account balance in differenc currencies (BTC and CLP)
    """

    try:
        url = 'https://www.buda.com/api/v2/balances'
        auth = BudaHMACAuth(api_key=credentials.API_KEY,
                            secret=credentials.SECRET)
        res = requests.get(url, auth=auth)
        res = res.json()

        data = {
            "BTC": res["balances"][0]["amount"][0],
            "CLP": res["balances"][2]["amount"][0]
        }

        converted_btc = convert(data["BTC"], "btc")

        data["converted_btc"] = converted_btc

        return data
    except Exception as e:
        print(f"An error has occurred while calling {url}: {str(e)}")
        return f"An error has occurred in current_balance(), error: {str(e)}"


def generate_order(direction: str, btc_amount: float) -> dict:
    """
    Generates a market order to buy/sell amount of BTC, returns string to be
    sent in message response through telegram with Buda.com request response data
    """

    try:
        url = 'https://www.buda.com/api/v2/markets/btc-clp/orders'
        auth = BudaHMACAuth(api_key=credentials.API_KEY,
                            secret=credentials.SECRET)
        res = requests.post(url, auth=auth, json={
            "type": direction,
            "price_type": "market",
            "amount": btc_amount
        }).json()["order"]

        data = {
            "order_id": res["id"],
            "market_id": res["market_id"],
            "type": res["type"],
            "status": res["state"],
            "amount": res["amount"][0] + res["amount"][1],
        }

        return data
    except Exception as e:
        print(f"An error has occurred while calling {url}: {str(e)}")
        return f"An error has occurred in generate_order(), error: {str(e)}"


def order_status(order_id: str) -> dict:
    """Returns obj with data related to the order with order_id"""

    url = f'https://www.buda.com/api/v2/orders/{order_id}'
    auth = BudaHMACAuth(api_key=credentials.API_KEY, secret=credentials.SECRET)
    res = requests.get(url, auth=auth).json()["order"]

    data = {
        "order_id": res["id"],
        "market_id": res["market_id"],
        "type": res["type"],
        "status": res["state"],
        "traded_amount": res["traded_amount"][0] + res["traded_amount"][1],
        "paid": res["total_exchanged"][0] + res["total_exchanged"][1],
        "fee": res["paid_fee"][0] + res["paid_fee"][1]
    }

    return data


def cancel_order(order_id: str) -> str:
    """Cancels the order related to order_id if it hasnt already been completed"""

    url = f'https://www.buda.com/api/v2/orders/{order_id}'
    auth = BudaHMACAuth(api_key=credentials.API_KEY, secret=credentials.SECRET)
    res = requests.put(url, auth=auth, json={
        'state': 'canceling',
    }).json()["order"]

    if res["state"] == "traded":
        return "Unable to cancel order, order was already fulfilled."
    else:
        return "Order cancel in process. Check buda.com or run '/order status [order_id]' to make sure it works."
