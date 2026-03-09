import requests
import os

TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

def get_gold_price():
    # Binance API - PAXG (Altın endeksli kripto varlık) ons altın fiyatını verir
    url = "https://api.binance.com/api/v3/ticker/price?symbol=PAXGUSDT"
    r = requests.get(url)
    data = r.json()
    # Hata buradaydı, direkt "price" anahtarını alıyoruz
    return data["price"]

def send_message(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": f"🌕 {text}"
    }
    requests.post(url, data=payload)

# Ana akış
try:
    price_raw = get_gold_price()
    # Gelen veriyi sayıya çevirip güzelleştirelim
    price_final = float(price_raw)
    message = f"Ons Altın Fiyatı: {price_final:.2f} USD"
    send_message(message)
except Exception as e:
    send_message(f"Botta bir hata oluştu: {str(e)}")