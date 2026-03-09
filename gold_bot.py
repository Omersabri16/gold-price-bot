import requests
import os

TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

def get_gold_price():
    url = "https://api.metals.live/v1/spot/gold"
    r = requests.get(url)
    data = r.json()
    return data[0]["price"]

def send_message(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text
    }
    requests.post(url, data=payload)

price = get_gold_price()
message = f"Ons Altın Fiyatı: {price} USD"

send_message(message)