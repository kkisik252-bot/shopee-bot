import requests
import time
import re

# ================= KONFIGURASI =================
TOKEN_BOT = "8992344332:AAG-1KfsuscEpASmgUOGI1rXsAhOyeHQE0g"
CHAT_ID = "6737964389"
URL_PRODUK = "https://shopee.co.id/product/1727535752/49866663031?d_id=121c5&uls_trackid=56ft3oeo003l&utm_content=2Wtj1M2JeuXi8qXK5xJvfknUqgGF"
INTERVAL_CEK = 300
# ===============================================

def kirim_notifikasi_telegram(pesan):
    url = f"https://api.telegram.org/bot{TOKEN_BOT}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": pesan, "parse_mode": "Markdown"}
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print(f"Gagal kirim Telegram: {e}")

def dapatkan_id_dari_url(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    try:
        res = requests.get(url, headers=headers, allow_redirects=True, timeout=10)
        final_url = res.url

        match1 = re.search(r"-i\.(\d+)\.(\d+)", final_url)
        if match1:
            return match1.group(2), match1.group(1)

        match2 = re.search(r"/product/(\d+)/(\d+)", final_url)
        if match2:
            return match2.group(2), match2.group(1)

    except Exception as e:
        print(f"Gagal ekstrak URL: {e}")
    return None, None

def ambil_data_shopee(item_id, shop_id):
    url = f"https://shopee.co.id/api/v4/item/get?itemid={item_id}&shopid={shop_id}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    try:
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code == 200:
            item = res.json().get("data", {})
            return {
                "nama": item.get("name", "Produk Shopee"),
                "stok": item.get("stock", 0),
                "harga": item.get("price", 0) / 100000
            }
    except Exception as e:
        print(f"Error API: {e}")
    return None

def jalankan_bot():
    print("Memproses URL produk...")
    item_id, shop_id = dapatkan_id_dari_url(URL_PRODUK)
    
    if not item_id or not shop_id:
        print("Format URL Shopee tidak valid!")
        return

    print(f"Berhasil! Item ID: {item_id} | Shop ID: {shop_id}")
    kirim_notifikasi_telegram("🤖 *Bot Pemantau Shopee Aktif!*")
    
    stok_terakhir = None
    harga_terakhir = None

    while True:
        data = ambil_data_shopee(item_id, shop_id)
        if data:
            nama, stok, harga = data["nama"], data["stok"], data["harga"]
            if stok_terakhir is not None:
                if stok > 0 and stok_terakhir == 0:
                    kirim_notifikasi_telegram(f"🚨 *STOK TERSEDIA!*\n\n{nama}\nHarga: Rp {harga:,.0f}\n[Beli]({URL_PRODUK})")
                elif harga < harga_terakhir:
                    kirim_notifikasi_telegram(f"📉 *HARGA TURUN!*\n\n{nama}\nHarga Baru: Rp {harga:,.0f}\n[Beli]({URL_PRODUK})")
            
            stok_terakhir = stok
            harga_terakhir = harga
            print(f"[{time.strftime('%H:%M:%S')}] Stok: {stok} | Harga: Rp {harga:,.0f}")
        else:
            print(f"[{time.strftime('%H:%M:%S')}] Gagal mengambil data.")

        time.sleep(INTERVAL_CEK)

if __name__ == "__main__":
    jalankan_bot()
