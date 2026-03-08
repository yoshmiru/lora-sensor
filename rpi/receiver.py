import serial
import time

# Raspberry Pi のシリアルポート設定
# 通常、/dev/serial0 が GPIO 14 (TX), 15 (RX) に割り当てられています。
# 設定（raspi-config）で「シリアルコンソール」を無効化し、「シリアルハードウェア」を有効化しておく必要があります。
PORT = '/dev/serial0'
BAUD = 9600

def main():
    try:
        # シリアルポートの初期化
        ser = serial.Serial(PORT, BAUD, timeout=1)
        print(f"Starting LoRa Receiver on {PORT} at {BAUD}bps...")

        while True:
            # データの受信を待機
            if ser.in_waiting > 0:
                # E220 からのデータを受信
                # 透過伝送モード（Normal Mode）なので、送信側が送ったバイトがそのまま届きます。
                line = ser.readline().decode('utf-8', errors='replace').strip()
                
                if line:
                    timestamp = time.strftime("[%Y-%m-%d %H:%M:%S]")
                    print(f"{timestamp} Received: {line}")

            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\nReceiver stopped by user.")
    except Exception as e:
        print(f"\nError: {e}")
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()

if __name__ == "__main__":
    main()
