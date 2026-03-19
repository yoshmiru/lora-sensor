import serial
import requests
import time
import json

# --- 設定 ---
# 環境に合わせてポート名を変更してください (例: '/dev/serial0' or '/dev/ttyUSB0')
SERIAL_PORT = '/dev/ttyUSB0'
BAUD_RATE = 9600
WORKER_URL = "https://lora-gateway-worker.miru.workers.dev/"
BATCH_SIZE = 6

def main():
    try:
        # シリアルポートの初期化
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        print("--- LoRa to Cloudflare RPi Batch Gateway ---")
        print("Listening on " + SERIAL_PORT + " (Batch Size: " + str(BATCH_SIZE) + ")...")

        data_buffer = []

        while True:
            if ser.in_waiting > 0:
                # LoRa データの読み取り
                line = ser.readline().decode('utf-8', errors='replace').strip()
                
                if line and line.startswith("M:"):
                    # バッファに追加
                    data_buffer.append({"message": line})
                    print("Buffered ({}/{}): {}".format(len(data_buffer), BATCH_SIZE, line))

                    # 指定件数貯まったら Cloudflare へ送信
                    if len(data_buffer) >= BATCH_SIZE:
                        print("Sending batch to Cloudflare...")
                        try:
                            response = requests.post(WORKER_URL, json=data_buffer, timeout=10)
                            if response.status_code == 200:
                                print("Cloudflare Response: 200 OK")
                                data_buffer = [] # 成功時のみバッファをクリア
                            else:
                                print("Cloudflare Error: " + str(response.status_code))
                        except Exception as e:
                            print("HTTP Send Error (will retry): " + str(e))
                elif line:
                    print("Ignored invalid data: " + line)

            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\nGateway stopped by user.")
    except Exception as e:
        print("\nCritical Error: " + str(e))
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()

if __name__ == "__main__":
    main()
