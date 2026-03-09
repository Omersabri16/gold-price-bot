import requests
import os

TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

def get_gold_price():
    # Yahoo Finance Altın (GC=F)
    url = "https://query1.finance.yahoo.com/v7/finance/quote?symbols=GC=F"
    r = requests.get(url)
    data = r.json()
    try:
        price = data["quoteResponse"]["result"][0]["regularMarketPrice"]
        return price
    except (KeyError, IndexError):
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