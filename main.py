HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
    "Referer": "https://shopee.co.id/",
    "X-Shopee-Language": "id",
    "Cookie": "SPC_EC=-; shopee_webUnique_id=;"
}

def ambil_data_shopee(item_id, shop_id):
    url = f"https://shopee.co.id/api/v4/item/get?itemid={item_id}&shopid={shop_id}"
    try:
        session = requests.Session()
        res = session.get(url, headers=HEADERS, timeout=10)
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
