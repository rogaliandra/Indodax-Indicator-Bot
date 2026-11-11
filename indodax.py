# Copyright 2026 rogaliandra
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# ⚠️ DISCLAIMER: This software is for educational purposes only.
# It does NOT constitute financial advice. Trading cryptocurrencies
# carries significant risk. Use at your own risk. Always DYOR.

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
INTERVAL = 60  # detik — cek setiap 1 menit

# Daftar semua pasangan yang dipantau
PAIRS = {
    "btcidr":   {"nama": "BTC/IDR",  "beli": 95000000, "jual": 105000000},
    "xrpidr":   {"nama": "XRP/IDR",  "beli": 6000,     "jual": 7500},
    "nearidr":  {"nama": "NEAR/IDR", "beli": 3500,     "jual": 5000},
    "usdtidr":  {"nama": "USDT/IDR", "beli": 16000,    "jual": 16500},
    "usdcidr":  {"nama": "USDC/IDR", "beli": 16000,    "jual": 16500},
    "ethidr":   {"nama": "ETH/IDR",  "beli": 4500000, "jual": 5500000},
    "solidr":   {"nama": "SOL/IDR",  "beli": 80000,   "jual": 110000},
}
# ===============================================

def ambil_harga(pair):
    """Ambil harga terakhir dari Indodax"""
    try:
        res = requests.get(f"{BASE_URL}/ticker/{pair}", timeout=10)
        return float(res.json()["ticker"]["last"])
    except Exception as e:
        print(f"❌ {pair}: Gagal ambil harga — {e}")
        return None

def format_harga(angka):
    """Format angka jadi mudah dibaca"""
    if angka >= 1000000:
        return f"Rp{angka:,.0f}"
    elif angka >= 1000:
        return f"Rp{angka:,.0f}"
    else:
        return f"Rp{angka:,.2f}"

def waktu_sekarang():
    return datetime.now().strftime("%d-%m-%Y %H:%M:%S")

def cek_sinyal(harga, beli, jual):
    """Tentukan sinyal berdasarkan harga target"""
    if harga < beli:
        return "🔵 BELI"
    elif harga > jual:
        return "🔴 JUAL"
    return "⏸️ TAHAN"

def main():
    print("=" * 65)
    print("🤖 INDOdAX MULTI-PAIR BOT — Indodax-Indicator-Bot")
    print(f"📊 Memantau {len(PAIRS)} pasangan — Update tiap {INTERVAL} detik")
    print("=" * 65)

    while True:
        print(f"\n🕒 {waktu_sekarang()}")
        print(f"{'Pasangan':<12} {'Harga':>18} {'Sinyal':<10} {'Target Beli':>15} {'Target Jual':>15}")
        print("-" * 65)

        for pair, cfg in PAIRS.items():
            harga = ambil_harga(pair)
            if harga:
                sinyal = cek_sinyal(harga, cfg["beli"], cfg["jual"])
                print(
                    f"{cfg['nama']:<12} "
                    f"{format_harga(harga):>18} "
                    f"{sinyal:<10} "
                    f"{format_harga(cfg['beli']):>15} "
                    f"{format_harga(cfg['jual']):>15}"
                )
        print("-" * 65)
        time.sleep(INTERVAL)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n✅ Bot berhenti")

