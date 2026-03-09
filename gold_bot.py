import requests
import os

TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

def get_gold_price():
    url = "https://forex-data-feed.swissquote.com/public-quotes/bboquotes/instrument/XAU/USD"
    r = requests.get(url, timeout=10)
    data = r.json()

    # İlk platformu al
    first_platform = data[0]
    # spreadProfilePrices listesinden "premium" profili bul
    premium_price = next(
        (p for p in first_platform["spreadProfilePrices"] if p["spreadProfile"] == "premium"),
        None
    )
    if premium_price:
        # bid ve ask ortalamasını alabiliriz
        price = (premium_price["bid"] + premium_price["ask"]) / 2
        return price
    return None

def send_message(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text}
    requests.post(url, data=payload)

try:
    price = get_gold_price()
    if price:
        message = f"🌕 Ons Altın Fiyatı (XAU/USD): {price:,.2f} USD"
        send_message(message)
    else:
        send_message("⚠️ Fiyat alınamadı.")
except Exception as e:
    send_message(f"❌ Hata: {type(e).__name__} - {str(e)}")