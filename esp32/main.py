import machine
import network
import urequests
import time

# --- 設定 ---
WIFI_SSID = "Buffalo-G-6278"
WIFI_PASS = "4rxkndv4fva43"
# wrangler deploy で取得した URL をここに貼ってください
WORKER_URL = "https://lora-gateway-worker.miru.workers.dev/"

# UART2 (RX=16, TX=17) の初期化
lora_uart = machine.UART(2, baudrate=9600, rx=16, tx=17, timeout=100)

# M0, M1 ピンの設定 (Normal Mode 固定)
m0 = machine.Pin(4, machine.Pin.OUT)
m1 = machine.Pin(5, machine.Pin.OUT)
m0.value(0)
m1.value(0)

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('Connecting to WiFi...')
        wlan.connect(WIFI_SSID, WIFI_PASS)
        while not wlan.isconnected():
            time.sleep(1)
    print("WiFi connected:", wlan.ifconfig())

def main():
    connect_wifi()
    print("--- LoRa to Cloudflare Gateway Active ---")

    while True:
        if lora_uart.any():
            try:
                # 1行読み取り
                line = lora_uart.readline()
                if line:
                    data = line.decode('utf-8', 'replace').strip()
                    print("Forwarding:", data)
                    
                    # Cloudflare Workers へ転送
                    payload = {"message": data, "timestamp": time.time()}
                    response = urequests.post(WORKER_URL, json=payload)
                    print("Cloudflare Response:", response.status_code)
                    response.close()
            except Exception as e:
                print("Gateway Error:", e)
        
        time.sleep(0.1)

if __name__ == "__main__":
    main()
