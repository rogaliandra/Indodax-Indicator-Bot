# Copyright 2026 Reando Jr. Liandra
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import requests
import time
import hmac
import hashlib
import json
from datetime import datetime

# ================= KONFIGURASI =================
API_KEY = "FILL API KEY HERE"
SECRET_KEY = "FILL SECRET KEY HERE"
BASE_URL = "https://indodax.com/api"

PAIR = "btcidr"
INTERVAL = 10  # Cek setiap 5 menit
BELI_DI_BAWAH = 95000000
JUAL_DI_ATAS = 105000000
# ===============================================

def buat_tanda(data):
    post_data = json.dumps(data)
    return hmac.new(
        bytes(SECRET_KEY, encoding='utf-8'),
        bytes(post_data, encoding='utf-8'),
        hashlib.sha512
    ).hexdigest()

def ambil_harga(pair):
    try:
        res = requests.get(f"{BASE_URL}/ticker/{pair}", timeout=30)
        return float(res.json()['ticker']['last'])
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def waktu_sekarang():
    return datetime.now().strftime("%d-%m-%Y %H:%M:%S")

def main():
    print("="*50)
    print("🤖 BOT INDOdAX — VERSI SEDERHANA")
    print("⚠️  HANYA UNTUK SIMULASI — TIDAK EKSEKUSI OTOMATIS")
    print(f"📈 Pasangan: {PAIR.upper()}")
    print(f"💰 Beli di bawah: Rp{BELI_DI_BAWAH:,}")
    print(f"💰 Jual di atas: Rp{JUAL_DI_ATAS:,}")
    print("="*50)

    while True:
        harga = ambil_harga(PAIR)
        if harga:
            print(f"[{waktu_sekarang()}] Harga: Rp{harga:,}")
            
            if harga < BELI_DI_BAWAH:
                print("🔵 SINYAL BELI — Harga rendah")
            elif harga > JUAL_DI_ATAS:
                print("🔴 SINYAL JUAL — Harga tinggi")
            else:
                print("⏸️  Menunggu...")
        print(f"⏳ Cek lagi dalam {INTERVAL/60} menit\n")
        time.sleep(INTERVAL)

if __name__ == "__main__":
    main()
