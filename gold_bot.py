import requests
import os
import sys
from datetime import datetime

# Telegram bilgileri
TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")


def get_gold_price():
    """
    Altın fiyatını al - SADECE ÇALIŞTIĞI TEST EDİLMİŞ API'LER
    """

    # API 1: metals.live - EN GÜVENİLİR (test edildi, çalışıyor)
    try:
        print("🟢 metals.live deneniyor...", file=sys.stderr)
        url = "https://api.metals.live/v1/spot/gold"

        # User-Agent ekle (bazı API'ler ister)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        response = requests.get(url, headers=headers, timeout=10)

        print(f"   Status: {response.status_code}", file=sys.stderr)

        if response.status_code == 200:
            data = response.json()
            print(f"   Yanıt: {data}", file=sys.stderr)

            # metals.live formatı: [{"gold": 1945.67, "silver": 23.45}]
            if isinstance(data, list) and len(data) > 0:
                price = data[0].get('gold')
                if price and float(price) > 0:
                    print(f"✅ metals.live'den alındı: {price} USD", file=sys.stderr)
                    return float(price)
    except Exception as e:
        print(f"   metals.live hatası: {e}", file=sys.stderr)

    # API 2: Günlük altın fiyatı - YEDEK
    try:
        print("🟢 goldprice.org deneniyor...", file=sys.stderr)
        url = "https://data-asg.goldprice.org/dbXRates/USD"

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        response = requests.get(url, headers=headers, timeout=10)

        print(f"   Status: {response.status_code}", file=sys.stderr)

        if response.status_code == 200:
            data = response.json()
            print(f"   Yanıt anahtarları: {data.keys() if data else 'Yok'}", file=sys.stderr)

            # goldprice.org formatı
            if data.get('items') and len(data['items']) > 0:
                price = data['items'][0].get('xauPrice')
                if price and float(price) > 0:
                    print(f"✅ goldprice.org'dan alındı: {price} USD", file=sys.stderr)
                    return float(price)
    except Exception as e:
        print(f"   goldprice.org hatası: {e}", file=sys.stderr)

    # API 3: ALTIN.CO.IN - SON ÇARE
    try:
        print("🟢 altin.co.in deneniyor...", file=sys.stderr)
        url = "https://api.altin.co.in/v1/gold/rate"

        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            data = response.json()
            print(f"   Yanıt: {data}", file=sys.stderr)

            price = data.get('gold_rate')
            if price and float(price) > 0:
                print(f"✅ altin.co.in'den alındı: {price} USD", file=sys.stderr)
                return float(price)
    except Exception as e:
        print(f"   altin.co.in hatası: {e}", file=sys.stderr)

    print("❌ TÜM API'LER BAŞARISIZ!", file=sys.stderr)
    return None


def send_telegram_message(text):
    """Telegram'a mesaj gönder"""
    if not TOKEN or not CHAT_ID:
        print("❌ Telegram bilgileri eksik!", file=sys.stderr)
        return False

    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

        payload = {
            "chat_id": CHAT_ID,
            "text": text,
            "parse_mode": "HTML"
        }

        response = requests.post(url, json=payload, timeout=10)

        if response.status_code == 200:
            result = response.json()
            if result.get("ok"):
                print("✅ Mesaj GÖNDERİLDİ!", file=sys.stderr)
                return True

        print(f"❌ Telegram hatası: {response.text}", file=sys.stderr)
        return False

    except Exception as e:
        print(f"❌ Mesaj gönderilemedi: {e}", file=sys.stderr)
        return False


def main():
    """Ana fonksiyon"""
    print("=" * 60, file=sys.stderr)
    print("🤖 ALTIN BOTU BAŞLATILDI", file=sys.stderr)
    print("=" * 60, file=sys.stderr)

    # Token kontrolü
    if not TOKEN:
        print("❌ BOT_TOKEN bulunamadı! GitHub Secrets'a BOT_TOKEN ekleyin.", file=sys.stderr)
        print("   Örnek: 1234567890:ABCdefGHIJklmNOPqrstUVwxyz", file=sys.stderr)
        sys.exit(1)

    if not CHAT_ID:
        print("❌ CHAT_ID bulunamadı! GitHub Secrets'a CHAT_ID ekleyin.", file=sys.stderr)
        print("   Örnek: 123456789", file=sys.stderr)
        sys.exit(1)

    print(f"📱 Chat ID: {CHAT_ID}", file=sys.stderr)
    print("🔍 Altın fiyatı alınıyor...", file=sys.stderr)
    print("-" * 60, file=sys.stderr)

    # Fiyatı al
    price = get_gold_price()

    print("-" * 60, file=sys.stderr)

    if price and price > 0:
        # Tarih ve saat
        now = datetime.now()
        date_str = now.strftime("%d.%m.%Y")
        time_str = now.strftime("%H:%M")

        # Fiyatı formatla
        formatted_price = f"{price:,.2f}".replace(',', '.')

        # Mesajı oluştur
        message = f"""🏆 <b>ONS ALTIN FİYATI</b> 🏆

💰 <b>{formatted_price} USD</b>

📅 {date_str} - ⏰ {time_str}

🔗 Kaynak: Uluslararası piyasalar

#altın #onsaltın #gold #xauusd"""

        print(f"✅ Fiyat bulundu: {price} USD", file=sys.stderr)
        print("📤 Mesaj gönderiliyor...", file=sys.stderr)

        # Telegram'a gönder
        success = send_telegram_message(message)

        if success:
            print("✅ BOT BAŞARIYLA TAMAMLANDI!", file=sys.stderr)
            sys.exit(0)
        else:
            print("❌ Mesaj gönderilemedi!", file=sys.stderr)
            sys.exit(1)
    else:
        print("❌ Altın fiyatı alınamadı!", file=sys.stderr)

        # Basit hata mesajı
        error_message = """⚠️ <b>ALTIN FİYATI ALINAMADI</b> ⚠️

Şu anda fiyat bilgisine ulaşılamıyor.

🔄 Yarın tekrar denenecek:
• Sabah 10:00
• Akşam 17:00"""

        send_telegram_message(error_message)
        sys.exit(1)


if __name__ == "__main__":
    main()