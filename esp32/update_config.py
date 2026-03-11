import machine
import time

# --- 設定 (接続ピンに合わせて変更してください) ---
TX_PIN = 17
RX_PIN = 16
lora_uart = machine.UART(2, baudrate=9600, rx=RX_PIN, tx=TX_PIN, timeout=2000)

# M0, M1 ピンの設定 (GPIOで制御している場合)
m0 = machine.Pin(4, machine.Pin.OUT)
m1 = machine.Pin(5, machine.Pin.OUT)

def update_to_transparent():
    # 1. 設定モードへ移行
    print("Switching to Configuration Mode...")
    m0.value(1)
    m1.value(1)
    time.sleep(0.5)

    # 2. UARTバッファ掃除
    if lora_uart.any():
        lora_uart.read()

    # 3. 設定書き込みコマンド (C0: 保存して設定, 00: 開始アドレス, 08: 長さ)
    # 以下の 8バイト を送ります:
    # 0x00, 0x00 (アドレス)
    # 0x62 (UART:9600, 125kHz, SF7)
    # 0x00 (SubPacket:200, RSSI:off, Power:13dBm)
    # 0x00 (Channel: 0)
    # 0x03 (RSSI Byte:off, Transmit:Transparent(ここが0!), WOR:2000ms)
    # 0x00, 0x00 (Encryption Key)
    
    config_data = bytes([0x00, 0x00, 0x62, 0x00, 0x00, 0x00, 0x00, 0x00])
    cmd = bytes([0xC0, 0x00, 0x08]) + config_data
    
    print("Sending Update Command...")
    lora_uart.write(cmd)
    
    time.sleep(1.0)
    
    if lora_uart.any():
        res = lora_uart.read()
        if res[0] == 0xC1: # 書き込み成功時は C1 から始まる設定値が返ってくる仕様
            print("Success! Module updated to Transparent mode.")
            print("Response:", [hex(b) for b in res])
        else:
            print("Failed. Unexpected response:", [hex(b) for b in res])
    else:
        print("No response from module.")

    # 4. 通常モードに戻す
    print("Returning to Normal Mode (M0=0, M1=0)...")
    m0.value(0)
    m1.value(0)

if __name__ == "__main__":
    update_to_transparent()
