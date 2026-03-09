import requests
import os
import sys
import re
from datetime import datetime

# Telegram bilgileri
TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")


def get_gold_price():
    """
    Altın fiyatını HTML scraping ile al
    """

    print("🟢 Altın fiyatı alınıyor...", file=sys.stderr)

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    # KAYNAK 1: bloomberght.com (Türk sitesi, güvenilir)
    try:
        print("   📡 bloomberght.com deneniyor...", file=sys.stderr)
        url = "https://www.bloomberght.com/altin"
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code == 200:
            html = response.text
            # Ons altın fiyatı pattern'i
            patterns = [
                r'ons-altin.*?(\d+[.,]\d+)',
                r'ONS Altın.*?(\d+[.,]\d+)',
                r'XAU/USD.*?(\d+[.,]\d+)',
                r'data-price="(\d+[.,\d]+)"',
                r'(\d+[.,]\d+)\s*USD.*?ons'
            ]

            for pattern in patterns:
                matches = re.findall(pattern, html, re.IGNORECASE | re.DOTALL)
                if matches:
                    price_str = matches[0].replace(',', '').strip()
                    try:
                        price = float(price_str)
                        if 1500 < price < 2500:  # Mantıklı aralık kontrolü
                            print(f"   ✅ bloomberght.com: {price} USD", file=sys.stderr)
                            return price
                    except:
                        continue
    except Exception as e:
        print(f"   bloomberght.com hatası: {e}", file=sys.stderr)

    # KAYNAK 2: bigpara.hurriyet.com.tr
    try:
        print("   📡 bigpara.hurriyet.com.tr deneniyor...", file=sys.stderr)
        url = "https://bigpara.hurriyet.com.tr/altin/"
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code == 200:
            html = response.text
            # Ons altın fiyatı pattern'i
            patterns = [
                r'ons-altin.*?data-value="([^"]+)"',
                r'ONS ALTIN.*?<span[^>]*>([0-9.,]+)',
                r'XAUUSD.*?>([0-9.,]+)<'
            ]

            for pattern in patterns:
                matches = re.findall(pattern, html, re.IGNORECASE | re.DOTALL)
                if matches:
                    price_str = matches[0].replace(',', '').replace('.', '')
                    try:
                        price = float(price_str) / 100 if len(price_str) > 4 else float(price_str)
                        if 1500 < price < 2500:
                            print(f"   ✅ bigpara: {price} USD", file=sys.stderr)
                            return price
                    except:
                        continue
    except Exception as e:
        print(f"   bigpara hatası: {e}", file=sys.stderr)

    # KAYNAK 3: dolar.tlkur.com (basit ve hızlı)
    try:
        print("   📡 dolar.tlkur.com deneniyor...", file=sys.stderr)
        url = "https://dolar.tlkur.com/ons-altin"
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code == 200:
            html = response.text
            # Çok basit pattern
            pattern = r'ONS ALTIN.*?(\d+[.,]\d+)'
            matches = re.findall(pattern, html, re.IGNORECASE | re.DOTALL)

            if matches:
                price_str = matches[0].replace(',', '').strip()
                try:
                    price = float(price_str)
                    if 1500 < price < 2500:
                        print(f"   ✅ dolar.tlkur.com: {price} USD", file=sys.stderr)
                        return price
                except:
                    pass
    except Exception as e:
        print(f"   dolar.tlkur.com hatası: {e}", file=sys.stderr)

    # KAYNAK 4: investing.com (uluslararası)
    try:
        print("   📡 investing.com deneniyor...", file=sys.stderr)
        url = "https://www.investing.com/commodities/gold"
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code == 200:
            html = response.text
            pattern = r'instrument-price.*?>([0-9.,]+)<'
            matches = re.findall(pattern, html)

            if matches:
                price_str = matches[0].replace(',', '')
                try:
                    price = float(price_str)
                    if 1500 < price < 2500:
                        print(f"   ✅ investing.com: {price} USD", file=sys.stderr)
                        return price
                except:
                    pass
    except Exception as e:
        print(f"   investing.com hatası: {e}", file=sys.stderr)

    print("   ❌ TÜM KAYNAKLAR BAŞARISIZ!", file=sys.stderr)
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
                print("✅ Mesaj gönderildi!", file=sys.stderr)
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
        print("❌ BOT_TOKEN bulunamadı!", file=sys.stderr)
        sys.exit(1)

    if not CHAT_ID:
        print("❌ CHAT_ID bulunamadı!", file=sys.stderr)
        sys.exit(1)

    print(f"📱 Chat ID: {CHAT_ID}", file=sys.stderr)
    print("=" * 60, file=sys.stderr)

    # Fiyatı al
    price = get_gold_price()

    print("=" * 60, file=sys.stderr)

    if price and price > 0:
        # Tarih ve saat
        now = datetime.now()
        date_str = now.strftime("%d.%m.%Y")
        time_str = now.strftime("%H:%M")

        # Fiyatı formatla
        formatted_price = f"{price:,.2f}".replace(',', '.')

        # Gram altın hesapla (1 ons = 31.1035 gram)
        gram_price = price / 31.1035
        formatted_gram = f"{gram_price:,.2f}".replace(',', '.')

        # Mesajı oluştur
        message = f"""🏆 <b>ONS ALTIN FİYATI</b> 🏆

💰 <b>{formatted_price} USD</b>

📊 <b>Gram Altın:</b> {formatted_gram} USD

📅 {date_str} - ⏰ {time_str}

📡 Kaynak: Uluslararası piyasalar

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

        # Daha basit hata mesajı
        error_message = """⚠️ <b>ALTIN FİYATI ALINAMADI</b> ⚠️

Fiyat bilgisine ulaşılamıyor.

🔧 Manuel test için GitHub Actions'da 'Run workflow' butonuna tıklayın.

🔄 Yarın tekrar denenecek: 10:00 ve 17:00"""

        send_telegram_message(error_message)
        sys.exit(1)


if __name__ == "__main__":
    main()