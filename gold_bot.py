import requests
import os

TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")


def get_gold_price():
    # Binance PAXG/USDT (Altın endeksli varlık)
    url = "https://api.binance.com/api/v3/ticker/price?symbol=PAXGUSDT"
    r = requests.get(url)
    data = r.json()

    # Veri sözlük (dict) olarak gelirse direkt al, liste gelirse ilk elemanı al
    if isinstance(data, dict):
        return data.get("price")
    elif isinstance(data, list):
        return data[0].get("price")
    return None


def send_message(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text}
    requests.post(url, data=payload)


# Ana Akış
try:
    price_raw = get_gold_price()
    if price_raw:
        price_float = float(price_raw)
        message = f"🌕 Ons Altın Fiyatı: {price_float:,.2f} USD"
        send_message(message)
    else:
        send_message("⚠️ Fiyat bilgisi alınamadı.")
except Exception as e:
    # Hatanın ne olduğunu tam anlamak için detayı gönderiyoruz
    send_message(f"❌ Hata detayı: {type(e).__name__} - {str(e)}")