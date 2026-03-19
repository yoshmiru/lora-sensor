import serial
import requests
import time
import json

# --- 設定 ---
# USBシリアルアダプタのポート (Windowsなら 'COM3', Linuxなら '/dev/ttyUSB0' など)
SERIAL_PORT = '/dev/ttyUSB0'
BAUD_RATE = 9600
WORKER_URL = "https://lora-gateway-worker.miru.workers.dev/"

def main():
    try:
        # シリアルポートの初期化
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        print("--- LoRa to Cloudflare Gateway (Python) ---")
        print("Listening on " + SERIAL_PORT + " at " + str(BAUD_RATE) + "bps...")

        while True:
            if ser.in_waiting > 0:
                # データの読み取り
                line = ser.readline().decode('utf-8', errors='replace').strip()
                
                if line:
                    print("Received: " + line)
                    
                    # Cloudflare Workers 側の batch 仕様 (配列) に合わせて送信
                    if line.startswith("M:"):
                        payload = [{"message": line}]
                        try:
                            # タイムアウトを設定してハングアップを防止
                            response = requests.post(WORKER_URL, json=payload, timeout=5)
                            print("Cloudflare Response: " + str(response.status_code))
                        except Exception as e:
                            print("HTTP Error: " + str(e))
                    else:
                        print("Ignored (Invalid Format)")

            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\nGateway stopped.")
    except Exception as e:
        print("\nError: " + str(e))
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()

if __name__ == "__main__":
    main()
