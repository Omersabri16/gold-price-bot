import requests
import os

TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

def get_gold_price():
    # Alternatif ve daha stabil bir API (Binance üzerinden ons altın/dolar takibi gibi)
    url = "https://api.binance.com/api/v3/ticker/price?symbol=PAXGUSDT"
    r = requests.get(url)
    data = r.json()
    # PAXG, altına endeksli bir kripto paradır ve ons altın fiyatını birebir takip eder
    return data["price"]

def send_message(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text
    }
    requests.post(url, data=payload)

try:
    price = get_gold_price()
    message = f"📊 Ons Altın (PAXG) Fiyatı: {float(price):.2f} USD"
    send_message(message)
except Exception as e:
    send_message(f"Hata oluştu: {str(e)}")