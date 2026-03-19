import machine
import network
import urequests
import time

# --- 設定 ---
WIFI_SSID = "Buffalo-G-6278"
WIFI_PASS = "4rxkndv4fva43"
WORKER_URL = "https://lora-gateway-worker.miru.workers.dev/"

# 【安全装置】
print("System booting in 5 seconds...")
time.sleep(5)

def connect_wifi():
    wlan = network.WLAN()
    wlan.active(True)
    if not wlan.isconnected():
        print('Connecting to WiFi...', end='')
        wlan.connect(WIFI_SSID, WIFI_PASS)
        for _ in range(20):
            if wlan.isconnected(): break
            print('.', end='')
            time.sleep(1)
    
    if wlan.isconnected():
        print("\nWiFi connected:", wlan.ifconfig())
        return True
    return False

def main():
    # 起動時に接続を完了させておく (突入電流をここで済ませる)
    connect_wifi()
    wlan = network.WLAN(network.STA_IF)

    lora_uart = machine.UART(2, baudrate=9600, rx=16, tx=17, timeout=100)
    m0 = machine.Pin(4, machine.Pin.OUT, value=0)
    m1 = machine.Pin(5, machine.Pin.OUT, value=0)

    data_buffer = []
    print("--- Gateway Running (WiFi-Always-On) ---")

    while True:
        if lora_uart.any():
            try:
                line = lora_uart.readline()
                if line:
                    data = line.decode('utf-8', 'replace').strip()
                    if data.startswith("M:"):
                        data_buffer.append({"message": data})
                        print("Buffered ({}/6): {}".format(len(data_buffer), data))

                    if len(data_buffer) >= 6:
                        # 接続が切れていたら再接続
                        if not wlan.isconnected():
                            print("Reconnecting WiFi...")
                            connect_wifi()

                        if wlan.isconnected():
                            print("Sending batch...")
                            try:
                                response = urequests.post(WORKER_URL, json=data_buffer)
                                print("Response:", response.status_code)
                                response.close()
                                data_buffer = []
                            except Exception as e:
                                print("POST Error:", e)
            except Exception as e:
                print("Read Error:", e)

        time.sleep(0.1)

if __name__ == "__main__":
    main()
