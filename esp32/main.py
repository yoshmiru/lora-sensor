import machine
import network
import urequests
import time

# --- 設定 ---
WIFI_SSID = "Buffalo-G-6278"
WIFI_PASS = "4rxkndv4fva43"
WORKER_URL = "https://lora-gateway-worker.miru.workers.dev/"

# UART2 (RX=16, TX=17)
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
    print("--- Batch Gateway Mode Active ---")

    data_buffer = []

    while True:
        if lora_uart.any():
            try:
                line = lora_uart.readline()
                if line:
                    data = line.decode('utf-8', 'replace').strip()
                    if data.startswith("M:"): # 正しいデータ形式か簡易チェック
                        data_buffer.append({"message": data})
                        print("Buffered:", data)

                    # 6件貯まったら送信 (10秒おきなら約1分に1回)
                    if len(data_buffer) >= 6:
                        print("Sending batch to Cloudflare...")
                        try:
                            response = urequests.post(WORKER_URL, json=data_buffer)
                            print("Cloudflare Response:", response.status_code)
                            response.close()
                            data_buffer = [] # 成功したらバッファをクリア
                        except Exception as e:
                            print("HTTP Error, keeping buffer:", e)
                            # 送信失敗時は次回復帰を待つためバッファを保持
            except Exception as e:
                print("Read Error:", e)

        time.sleep(0.1)

if __name__ == "__main__":
    main()
