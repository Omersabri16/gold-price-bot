import requests
import os
import sys

TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")


def get_gold_price():
    try:
        # Binance PAXG/USDT (Altın endeksli varlık)
        url = "https://api.binance.com/api/v3/ticker/price?symbol=PAXGUSDT"

        # User-Agent ekleyelim (bazı API'ler ister)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        r = requests.get(url, headers=headers, timeout=10)
        r.raise_for_status()  # HTTP hatası varsa exception fırlat

        data = r.json()

        # Debug için (isterseniz yoruma alabilirsiniz)
        print(f"API Yanıtı: {data}", file=sys.stderr)

        # PAXGUSDT her zaman dict olarak gelir
        if isinstance(data, dict):
            price = data.get("price")
            if price:
                return price

        # Eğer hala price bulunamadıysa
        print(f"Beklenmeyen veri formatı: {data}", file=sys.stderr)
        return None

    except requests.exceptions.RequestException as e:
        print(f"API isteği hatası: {e}", file=sys.stderr)
        return None
    except ValueError as e:
        print(f"JSON çözümleme hatası: {e}", file=sys.stderr)
        return None


def send_message(text):
    if not TOKEN or not CHAT_ID:
        print("BOT_TOKEN veya CHAT_ID bulunamadı!", file=sys.stderr)
        return False

    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        payload = {
            "chat_id": CHAT_ID,
            "text": text,
            "parse_mode": "HTML"  # İsteğe bağlı: HTML formatı kullanabilirsiniz
        }

        response = requests.post(url, data=payload, timeout=10)
        response.raise_for_status()

        result = response.json()
        if result.get("ok"):
            print("Mesaj başarıyla gönderildi", file=sys.stderr)
            return True
        else:
            print(f"Telegram API hatası: {result}", file=sys.stderr)
            return False

    except requests.exceptions.RequestException as e:
        print(f"Mesaj gönderilemedi: {e}", file=sys.stderr)
        return False


# Ana Akış
def main():
    print("Altın fiyat botu başlatılıyor...", file=sys.stderr)

    # Token ve Chat ID kontrolü
    if not TOKEN:
        error_msg = "❌ HATA: BOT_TOKEN bulunamadı! GitHub Secrets'a eklendiğinden emin olun."
        print(error_msg, file=sys.stderr)
        # Token yoksa mesaj gönderemeyiz ama yine de çıkalım
        sys.exit(1)

    if not CHAT_ID:
        error_msg = "❌ HATA: CHAT_ID bulunamadı! GitHub Secrets'a eklendiğinden emin olun."
        print(error_msg, file=sys.stderr)
        sys.exit(1)

    try:
        print("Altın fiyatı alınıyor...", file=sys.stderr)
        price_raw = get_gold_price()

        if price_raw:
            try:
                price_float = float(price_raw)
                # Ondalık kısmı 2 hane göster
                formatted_price = f"{price_float:,.2f}".replace(',', '.')
                message = f"🌕 <b>Ons Altın Fiyatı (PAXG/USDT):</b>\n💵 <b>{formatted_price} USD</b>"
                print(f"Fiyat bulundu: {price_float} USD", file=sys.stderr)
            except ValueError as e:
                message = f"⚠️ Fiyat formatı hatalı: {price_raw}"
                print(f"Fiyat dönüştürme hatası: {e}", file=sys.stderr)
        else:
            message = "⚠️ <b>Fiyat bilgisi alınamadı.</b>\nBinance API'den veri gelmiyor olabilir."
            print("Fiyat alınamadı", file=sys.stderr)

        # Mesajı gönder
        success = send_message(message)
        if not success:
            print("Mesaj gönderilemedi!", file=sys.stderr)
            sys.exit(1)
        else:
            print("İşlem tamamlandı.", file=sys.stderr)

    except Exception as e:
        # Beklenmeyen hatalar için
        error_msg = f"❌ <b>Kritik Hata:</b>\n{type(e).__name__}: {str(e)}"
        print(f"Hata: {error_msg}", file=sys.stderr)

        # Hata mesajını göndermeyi dene (belki token hala geçerlidir)
        try:
            send_message(error_msg)
        except:
            pass  # Mesaj gönderilemezse sessizce geç

        sys.exit(1)


if __name__ == "__main__":
    main()