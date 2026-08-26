import requests
import time
import re

# ================= KONFIGURASI =================
TOKEN_BOT = "8992344332:AAG-1KfsuscEpASmgUOGI1rXsAhOyeHQE0g"
CHAT_ID = "6737964389"
URL_PRODUK = "https://id.shp.ee/W9y3Vdex"
INTERVAL_CEK = 300
# ===============================================

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
    "Referer": "https://shopee.co.id/",
    "X-Requested-With": "XMLHttpRequest"
}

def kirim_notifikasi_telegram(pesan):
    url = f"https://api.telegram.org/bot{TOKEN_BOT}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": pesan, "parse_mode": "Markdown"}
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print(f"Gagal kirim Telegram: {e}")

def dapatkan_id_dari_url(url):
    try:
        res = requests.get(url, headers=HEADERS, allow_redirects=True, timeout=10)
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
    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
        if res.status_code == 200:
            data = res.json()
            item = data.get("data")
            if item:
                return {
                    "nama": item.get("name", "Produk Shopee"),
                    "stok": item.get("stock", 0),
                    "harga": item.get("price", 0) / 100000
                }
            else:
                print(f"Response API Shopee kosong/dibatasi: {data}")
        else:
            print(f"HTTP Status Error: {res.status_code}")
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
            print(f"[{time.strftime('%H:%M:%S')}] Cek Berhasil - Stok: {stok} | Harga: Rp {harga:,.0f}")
        else:
            print(f"[{time.strftime('%H:%M:%S')}] Gagal mengambil data.")

        time.sleep(INTERVAL_CEK)

if __name__ == "__main__":
    jalankan_bot()
