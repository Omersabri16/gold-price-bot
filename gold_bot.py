import requests
import os
import sys
from datetime import datetime

# Telegram bilgileri
TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")


def get_gold_price():
    """
    Altın fiyatını almak için 3 farklı API dener
    """

    # API 1: Gold API (ücretsiz, demo token ile)
    try:
        print("GoldAPI.io deneniyor...", file=sys.stderr)
        url = "https://www.goldapi.io/api/XAU/USD"
        headers = {
            'x-access-token': 'goldapi-3s8c0do3hn6opd9-io',  # Demo token - ücretsiz
            'Content-Type': 'application/json'
        }
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code == 200:
            data = response.json()
            if data.get('price'):
                price = float(data['price'])
                print(f"GoldAPI'den alındı: {price}", file=sys.stderr)
                return price
    except Exception as e:
        print(f"GoldAPI hatası: {e}", file=sys.stderr)

    # API 2: Metals-API (ücretsiz)
    try:
        print("Metals-API deneniyor...", file=sys.stderr)
        # metals-api.com'a ücretsiz kayıt olup API key alın
        # Şimdilik demo kullanıyoruz
        url = "https://api.metals.live/v1/spot/gold"
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            data = response.json()
            # Metals.live'dan gelen veri formatı: [{"gold": 1945.67, "silver": 23.45, ...}]
            if isinstance(data, list) and len(data) > 0:
                price = float(data[0].get('gold', 0))
                if price > 0:
                    print(f"Metals.live'dan alındı: {price}", file=sys.stderr)
                    return price
    except Exception as e:
        print(f"Metals-API hatası: {e}", file=sys.stderr)

    # API 3: Günlük ons altın fiyatı (başka bir kaynak)
    try:
        print("Günlük altın fiyatı deneniyor...", file=sys.stderr)
        url = "https://data-asg.goldprice.org/dbXRates/USD"
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            data = response.json()
            # items array'inde fiyat bilgisi var
            if data.get('items') and len(data['items']) > 0:
                price = float(data['items'][0].get('xauPrice', 0))
                if price > 0:
                    print(f"Goldprice.org'dan alındı: {price}", file=sys.stderr)
                    return price
    except Exception as e:
        print(f"Goldprice.org hatası: {e}", file=sys.stderr)

    # API 4: Son çare - Kraken'den PAXG (altın tokenı)
    try:
        print("Kraken PAXG deneniyor...", file=sys.stderr)
        url = "https://api.kraken.com/0/public/Ticker?pair=PAXGUSD"
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            data = response.json()
            if not data.get('error'):
                result = data.get('result', {})
                # Kraken'de pair adı değişebilir, ilk key'i al
                for pair_key in result:
                    price = float(result[pair_key].get('c', [0])[0])
                    if price > 0:
                        print(f"Kraken'den alındı: {price}", file=sys.stderr)
                        return price
    except Exception as e:
        print(f"Kraken hatası: {e}", file=sys.stderr)

    print("TÜM API'LER BAŞARISIZ!", file=sys.stderr)
    return None


def send_telegram_message(text):
    """Telegram'a mesaj gönderir"""
    if not TOKEN or not CHAT_ID:
        print("Telegram bilgileri eksik!", file=sys.stderr)
        return False

    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

        # Mesajı düzenle - emojiler ve formatlama
        formatted_text = text.replace('USD', '🇺🇸 USD')

        payload = {
            "chat_id": CHAT_ID,
            "text": formatted_text,
            "parse_mode": "HTML",
            "disable_web_page_preview": True
        }

        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()

        result = response.json()
        if result.get("ok"):
            print("✅ Mesaj başarıyla gönderildi", file=sys.stderr)
            return True
        else:
            print(f"❌ Telegram hatası: {result}", file=sys.stderr)
            return False

    except Exception as e:
        print(f"❌ Mesaj gönderilemedi: {e}", file=sys.stderr)
        return False


def format_price_message(price):
    """Fiyat mesajını formatlar"""

    # Tarih ve saat
    now = datetime.now()
    date_str = now.strftime("%d %B %Y")
    time_str = now.strftime("%H:%M")

    # Altın fiyatını formatla
    if price >= 1000:
        formatted_price = f"{price:,.2f}".replace(',', '.')
    else:
        formatted_price = f"{price:.2f}"

    # Mesajı oluştur
    message = f"""🏆 <b>ONS ALTIN FİYATI</b> 🏆

💰 <b>{formatted_price} USD</b>

📅 {date_str} - ⏰ {time_str}

📊 <i>Güncel spot altın fiyatı</i>

#altın #onsaltın #gold #xauusd"""

    return message


def main():
    """Ana fonksiyon"""
    print("=" * 50, file=sys.stderr)
    print("🤖 ALTIN BOTU BAŞLATILDI", file=sys.stderr)
    print("=" * 50, file=sys.stderr)

    # Token kontrolü
    if not TOKEN:
        print("❌ BOT_TOKEN bulunamadı! GitHub Secrets'a ekleyin.", file=sys.stderr)
        sys.exit(1)

    if not CHAT_ID:
        print("❌ CHAT_ID bulunamadı! GitHub Secrets'a ekleyin.", file=sys.stderr)
        sys.exit(1)

    print(f"📱 Chat ID: {CHAT_ID}", file=sys.stderr)
    print("🔍 Altın fiyatı alınıyor...", file=sys.stderr)

    # Fiyatı al
    price = get_gold_price()

    if price and price > 0:
        print(f"✅ Güncel altın fiyatı: {price} USD", file=sys.stderr)

        # Mesajı hazırla
        message = format_price_message(price)

        # Telegram'a gönder
        success = send_telegram_message(message)

        if success:
            print("✅ Bot başarıyla tamamlandı!", file=sys.stderr)
            sys.exit(0)
        else:
            print("❌ Mesaj gönderilemedi!", file=sys.stderr)
            sys.exit(1)
    else:
        print("❌ Altın fiyatı alınamadı!", file=sys.stderr)

        # Hata mesajı gönder
        error_message = """⚠️ <b>ONS ALTIN FİYATI ALINAMADI</b> ⚠️

Şu anda altın fiyat bilgisine ulaşılamıyor.

🔄 Bot tekrar deneyecek:
• Yarın sabah 10:00'da
• Yarın akşam 17:00'de

#altın #hatabildirimi"""

        send_telegram_message(error_message)
        sys.exit(1)


if __name__ == "__main__":
    main()