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
    Altın fiyatını al - SADECE BİR KAYNAK
    """

    print("🟢 Altın fiyatı alınıyor...", file=sys.stderr)

    # SADECE 1 KAYNAK: canlidoviz.com (Türk sitesi, çalışma garantili)
    try:
        print("   📡 canlidoviz.com deneniyor...", file=sys.stderr)

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'tr-TR,tr;q=0.9,en;q=0.8',
            'Connection': 'keep-alive',
        }

        url = "https://canlidoviz.com/ons-altin"
        response = requests.get(url, headers=headers, timeout=15)

        print(f"   HTTP Status: {response.status_code}", file=sys.stderr)

        if response.status_code == 200:
            html = response.text

            # Birden çok pattern dene
            patterns = [
                r'ons-altin.*?data-shopping="([^"]+)"',
                r'ONS ALTIN.*?<span class="value">([0-9.,]+)',
                r'ons-altin-fiyati.*?>([0-9.,]+)',
                r'data-price="([0-9.,]+)"',
                r'<td[^>]*>ONS ALTIN[^<]*</td>\s*<td[^>]*>([0-9.,]+)',
            ]

            for i, pattern in enumerate(patterns):
                matches = re.findall(pattern, html, re.IGNORECASE | re.DOTALL)
                if matches:
                    price_str = matches[0].replace('.', '').replace(',', '.')
                    # Sadece rakamları al
                    price_str = re.sub(r'[^0-9.]', '', price_str)

                    try:
                        price = float(price_str)
                        # Mantıklı aralık kontrolü (1000-3000 USD arası)
                        if 1000 < price < 3000:
                            print(f"   ✅ Pattern {i + 1} ile bulundu: {price} USD", file=sys.stderr)
                            return price
                    except ValueError:
                        continue

            print("   ❌ Fiyat pattern'lerle bulunamadı", file=sys.stderr)

    except requests.exceptions.RequestException as e:
        print(f"   canlidoviz.com bağlantı hatası: {e}", file=sys.stderr)
    except Exception as e:
        print(f"   canlidoviz.com bilinmeyen hata: {e}", file=sys.stderr)

    # YEDEK KAYNAK 1: bloomberght
    try:
        print("   📡 bloomberght.com deneniyor (yedek)...", file=sys.stderr)

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        url = "https://www.bloomberght.com/altin"
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code == 200:
            html = response.text
            # Ons altın fiyatını bul
            pattern = r'ONS ALTIN.*?([0-9]{1,3}(?:[.,][0-9]{2,3})?)'
            matches = re.findall(pattern, html, re.IGNORECASE | re.DOTALL)

            if matches:
                price_str = matches[0].replace('.', '').replace(',', '.')
                price = float(price_str)
                if 1000 < price < 3000:
                    print(f"   ✅ bloomberght: {price} USD", file=sys.stderr)
                    return price
    except:
        pass

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
                print("✅ Mesaj GÖNDERİLDİ!", file=sys.stderr)
                return True

        print(f"❌ Telegram hatası: {response.status_code}", file=sys.stderr)
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

        # Çeyrek altın (1.75 gram)
        quarter_price = gram_price * 1.75
        formatted_quarter = f"{quarter_price:,.2f}".replace(',', '.')

        # Mesajı oluştur
        message = f"""🏆 <b>ONS ALTIN FİYATI</b> 🏆

💰 <b>{formatted_price} USD</b>

📊 <b>Gram Altın:</b> {formatted_gram} USD
🪙 <b>Çeyrek Altın:</b> {formatted_quarter} USD

📅 {date_str} - ⏰ {time_str}

📡 Kaynak: Piyasa Verileri

#altın #onsaltın #gold #yatırım"""

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

        # Çok basit hata mesajı
        error_message = "⚠️ ALTIN FİYATI ALINAMADI ⚠️\n\nFiyat bilgisine ulaşılamıyor.\n\n🔄 Yarın tekrar denenek: 10:00 ve 17:00"

        send_telegram_message(error_message)
        sys.exit(1)


if __name__ == "__main__":
    main()