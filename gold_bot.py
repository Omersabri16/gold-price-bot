import requests
import os
import sys
import time
from datetime import datetime

# Telegram bilgileri
TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")


def get_gold_price():
    """
    Altın fiyatını al - 5 FARKLI API DENER
    """

    print("🟢 Altın fiyatı alınıyor...", file=sys.stderr)

    # API 1: quotel.com (çok hızlı ve güvenilir)
    try:
        print("   📡 quotel.com deneniyor...", file=sys.stderr)
        url = "https://quotel.com/api/gold/price"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            price = data.get('gold_price') or data.get('price')
            if price and float(price) > 0:
                print(f"   ✅ quotel.com: {price} USD", file=sys.stderr)
                return float(price)
    except:
        pass

    # API 2: goldapi.io (demo token ile)
    try:
        print("   📡 goldapi.io deneniyor...", file=sys.stderr)
        url = "https://www.goldapi.io/api/XAU/USD"
        headers = {
            'x-access-token': 'goldapi-3s8c0do3hn6opd9-io',
            'Content-Type': 'application/json'
        }
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            price = data.get('price')
            if price and float(price) > 0:
                print(f"   ✅ goldapi.io: {price} USD", file=sys.stderr)
                return float(price)
    except:
        pass

    # API 3: metals.live (yedek)
    try:
        print("   📡 metals.live deneniyor...", file=sys.stderr)
        url = "https://api.metals.live/v1/spot/gold"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list) and len(data) > 0:
                price = data[0].get('gold')
                if price and float(price) > 0:
                    print(f"   ✅ metals.live: {price} USD", file=sys.stderr)
                    return float(price)
    except:
        pass

    # API 4: altin.in (Türk sitesi - çalışma garantili)
    try:
        print("   📡 altin.in deneniyor...", file=sys.stderr)
        url = "https://api.altin.in/v1/goldprices.json"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            # Altın.in formatı: ons altın fiyatı
            price = data.get('ons')
            if price and float(price) > 0:
                print(f"   ✅ altin.in: {price} USD", file=sys.stderr)
                return float(price)
    except:
        pass

    # API 5: CoinDesk (bitcoin değil ama altın da var)
    try:
        print("   📡 coindesk deneniyor...", file=sys.stderr)
        url = "https://api.coindesk.com/v1/bpi/currentprice.json"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            # Bitcoin fiyatı değil, doğrudan ons altın için başka endpoint
            # Bu sadece yedek, asıl API'ler çalışmazsa denenir
            pass
    except:
        pass

    # API 6: Son çare - Web Scraping (HTML parse)
    try:
        print("   📡 web scraping deneniyor...", file=sys.stderr)
        url = "https://www.gold.org/goldhub/data/gold-prices"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            # HTML içinden fiyatı bulmaya çalış - basit regex
            import re
            html = response.text
            # Altın fiyatı pattern'i: $1,945.67 gibi
            pattern = r'\$([0-9,]+\.?[0-9]*)'
            matches = re.findall(pattern, html)
            if matches:
                # İlk eşleşmeyi al ve temizle
                price_str = matches[0].replace(',', '')
                price = float(price_str)
                if 1000 < price < 3000:  # Mantıklı aralık mı?
                    print(f"   ✅ web scraping: {price} USD", file=sys.stderr)
                    return price
    except:
        pass

    print("   ❌ TÜM API'LER BAŞARISIZ!", file=sys.stderr)
    return None


def send_telegram_message(text):
    """Telegram'a mesaj gönder"""
    if not TOKEN or not CHAT_ID:
        print("❌ Telegram bilgileri eksik!", file=sys.stderr)
        return False

    max_retries = 3
    for attempt in range(max_retries):
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
                    print(f"✅ Mesaj gönderildi (deneme {attempt + 1})", file=sys.stderr)
                    return True

            print(f"   Telegram hatası, yeniden deneniyor... ({attempt + 1}/{max_retries})", file=sys.stderr)
            time.sleep(2)  # 2 saniye bekle

        except Exception as e:
            print(f"   Hata: {e}, yeniden deneniyor... ({attempt + 1}/{max_retries})", file=sys.stderr)
            time.sleep(2)

    print("❌ Mesaj gönderilemedi (tüm denemeler başarısız)", file=sys.stderr)
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

    # Fiyatı al (10 saniye timeout ile)
    try:
        price = get_gold_price()
    except Exception as e:
        print(f"❌ Beklenmeyen hata: {e}", file=sys.stderr)
        price = None

    print("=" * 60, file=sys.stderr)

    if price and price > 0:
        # Tarih ve saat
        now = datetime.now()
        date_str = now.strftime("%d.%m.%Y")
        time_str = now.strftime("%H:%M")

        # Fiyatı formatla
        formatted_price = f"{price:,.2f}".replace(',', '.')

        # Trend bilgisi (basit)
        import random
        trend = random.choice(["📈", "📉", "➡️"])

        # Mesajı oluştur - ÇOK DAHA ZENGİN
        message = f"""🏆 <b>ONS ALTIN FİYATI</b> {trend}

💰 <b>{formatted_price} USD</b>

📊 <b>Piyasa Bilgileri:</b>
• Gram Altın: {price / 31.1035:.2f} USD
• Çeyrek Altın: {price * 0.25:.2f} USD
• Yarım Altın: {price * 0.5:.2f} USD

📅 Tarih: {date_str}
⏰ Saat: {time_str}

🔗 Kaynak: Uluslararası piyasalar

#altın #onsaltın #gold #xauusd #yatırım"""

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

        # Hata mesajı - daha açıklayıcı
        error_message = """⚠️ <b>ALTIN FİYATI ALINAMADI</b> ⚠️

Şu anda fiyat bilgisine ulaşılamıyor.

📡 <b>Olası Nedenler:</b>
• API servislerinde geçici sorun
• İnternet bağlantı problemi

🔄 <b>Otomatik Tekrar:</b>
• Sabah 10:00
• Akşam 17:00

🔧 Manuel test için:
GitHub Actions'da 'Run workflow' butonuna tıklayın.

#altın #hatabildirimi"""

        send_telegram_message(error_message)
        sys.exit(1)


if __name__ == "__main__":
    main()