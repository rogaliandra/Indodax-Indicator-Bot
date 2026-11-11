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
import sdl2
import sdl2.ext

# ================= KONFIGURASI =================
API_KEY = "FILL API KEY HERE"
SECRET_KEY = "FILL SECRET KEY HERE"
BASE_URL = "https://indodax.com/api"
INTERVAL = 60  # detik — update tiap 15 detik
CHART_PAIR = "btcidr"  # Pasangan yang ditampilkan di grafik
MAX_DATA_POINTS = 60   # Maksimal titik di grafik

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

# Data untuk grafik
price_history = []
time_history = []

# SDL2 Constants
WIDTH, HEIGHT = 900, 550
MARGIN_LEFT, MARGIN_RIGHT = 80, 40
MARGIN_TOP, MARGIN_BOTTOM = 50, 60
CHART_W = WIDTH - MARGIN_LEFT - MARGIN_RIGHT
CHART_H = HEIGHT - MARGIN_TOP - MARGIN_BOTTOM

def ambil_harga(pair):
    try:
        res = requests.get(f"{BASE_URL}/ticker/{pair}", timeout=10)
        return float(res.json()["ticker"]["last"])
    except Exception as e:
        print(f"❌ {pair}: {e}")
        return None

def format_harga(angka):
    if angka >= 1000000:
        return f"Rp{angka:,.0f}"
    elif angka >= 1000:
        return f"Rp{angka:,.0f}"
    return f"Rp{angka:.2f}"

def waktu_sekarang():
    return datetime.now().strftime("%H:%M:%S")

def cek_sinyal(harga, beli, jual):
    if harga < beli:
        return "🔵 BELI"
    elif harga > jual:
        return "🔴 JUAL"
    return "⏸️ TAHAN"

# ============== SDL2 CHART FUNCTIONS ==============

def init_sdl2():
    sdl2.ext.init()
    window = sdl2.ext.Window(
        f"📈 Indodax Bot — {PAIRS[CHART_PAIR]['nama']} Live Chart",
        size=(WIDTH, HEIGHT)
    )
    renderer = sdl2.ext.Renderer(window, logical_size=(WIDTH, HEIGHT))
    window.show()
    return window, renderer

def draw_grid(renderer, min_p, max_p):
    sdl2.SDL_SetRenderDrawColor(renderer.sdlrenderer, 50, 55, 65, 255)
    for i in range(5):
        y = MARGIN_TOP + int(i * CHART_H / 4)
        sdl2.SDL_RenderDrawLine(renderer.sdlrenderer,
            MARGIN_LEFT, y, WIDTH - MARGIN_RIGHT, y)
    for i in range(6):
        x = MARGIN_LEFT + int(i * CHART_W / 5)
        sdl2.SDL_RenderDrawLine(renderer.sdlrenderer,
            x, MARGIN_TOP, x, HEIGHT - MARGIN_BOTTOM)

def price_to_y(price, min_p, max_p):
    if max_p == min_p: return MARGIN_TOP + CHART_H // 2
    ratio = (max_p - price) / (max_p - min_p)
    return MARGIN_TOP + int(ratio * CHART_H)

def update_chart(renderer, harga, beli, jual):
    global price_history, time_history
    
    price_history.append(harga)
    time_history.append(waktu_sekarang())
    
    price_history = price_history[-MAX_DATA_POINTS:]
    time_history = time_history[-MAX_DATA_POINTS:]
    
    if len(price_history) < 2:
        min_p = min(harga * 0.999, beli * 0.999)
        max_p = max(harga * 1.001, jual * 1.001)
    else:
        min_p = min(min(price_history), beli) * 0.9995
        max_p = max(max(price_history), jual) * 1.0005
    
    sdl2.SDL_SetRenderDrawColor(renderer.sdlrenderer, 20, 22, 30, 255)
    sdl2.SDL_RenderClear(renderer.sdlrenderer)
    
    draw_grid(renderer, min_p, max_p)
    
    y_beli = price_to_y(beli, min_p, max_p)
    sdl2.SDL_SetRenderDrawColor(renderer.sdlrenderer, 30, 144, 255, 180)
    for x in range(MARGIN_LEFT, WIDTH - MARGIN_RIGHT, 8):
        sdl2.SDL_RenderDrawPoint(renderer.sdlrenderer, x, y_beli)
    
    y_jual = price_to_y(jual, min_p, max_p)
    sdl2.SDL_SetRenderDrawColor(renderer.sdlrenderer, 220, 50, 50, 180)
    for x in range(MARGIN_LEFT, WIDTH - MARGIN_RIGHT, 8):
        sdl2.SDL_RenderDrawPoint(renderer.sdlrenderer, x, y_jual)
    
    if len(price_history) > 1:
        sdl2.SDL_SetRenderDrawColor(renderer.sdlrenderer, 0, 255, 136, 255)
        points = []
        for i, p in enumerate(price_history):
            x = MARGIN_LEFT + int(i * CHART_W / max(len(price_history)-1, 1))
            y = price_to_y(p, min_p, max_p)
            points.append((x, y))
        for i in range(len(points)-1):
            sdl2.SDL_RenderDrawLine(
                renderer.sdlrenderer,
                points[i][0], points[i][1],
                points[i+1][0], points[i+1][1]
            )
    
    sinyal = cek_sinyal(harga, beli, jual)
    info_text = f"{PAIRS[CHART_PAIR]['nama']} | Terbaru: {format_harga(harga)} | {sinyal}"
    print(f"\n📊 {info_text}")
    
    renderer.present()

# =================== MAIN LOOP ===================

def main():
    print("=" * 65)
    print("🤖 INDOdAX BOT + SDL2 LIVE CHART")
    print(f"📊 Memantau {len(PAIRS)} pasangan — Update tiap {INTERVAL} detik")
    print(f"📈 Grafik: {PAIRS[CHART_PAIR]['nama']}")
    print("=" * 65)
    
    window, renderer = init_sdl2()
    running = True
    last_update = 0
    
    try:
        while running:
            events = sdl2.ext.get_events()
            for event in events:
                if event.type == sdl2.SDL_QUIT:
                    running = False
                    break
            
            now = time.time()
            if now - last_update >= INTERVAL:
                last_update = now
                print(f"\n🕒 {waktu_sekarang()}")
                print(f"{'Pasangan':<12} {'Harga':>18} {'Sinyal':<10}")
                print("-" * 45)
                
                chart_price = None
                chart_cfg = PAIRS[CHART_PAIR]
                
                for pair, cfg in PAIRS.items():
                    harga = ambil_harga(pair)
                    if harga:
                        sinyal = cek_sinyal(harga, cfg["beli"], cfg["jual"])
                        print(f"{cfg['nama']:<12} {format_harga(harga):>18} {sinyal:<10}")
                        if pair == CHART_PAIR:
                            chart_price = harga
                
                if chart_price:
                    update_chart(renderer, chart_price, chart_cfg["beli"], chart_cfg["jual"])
            
            time.sleep(0.5)
            
    except KeyboardInterrupt:
        print("\n\n✅ Bot dihentikan oleh pengguna")
    finally:
        sdl2.ext.quit()
        print("👋 SDL2 window closed")

if __name__ == "__main__":
    main()

