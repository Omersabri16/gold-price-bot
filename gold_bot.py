import requests
import os

TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

def get_gold_price():
    url = "https://api.metals.live/v1/spot/gold"
    r = requests.get(url)
    data = r.json()
    # data örnek: [{"metal":"gold","price":1964.12}]
    if isinstance(data, list) and len(data) > 0:
        return data[0].get("price")
    return None

def send_message(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text}
    requests.post(url, data=payload)

try:
    price = get_gold_price()
    if price:
        message = f"🌕 Ons Altın Fiyatı: {price:,.2f} USD"
        send_message(message)
    else:
        send_message("⚠️ Fiyat alınamadı.")
except Exception as e:
    send_message(f"❌ Hata: {type(e).__name__} - {str(e)}")