import machine
import time

# --- 設定 (接続ピンに合わせて変更してください) ---
TX_PIN = 17
RX_PIN = 16
# UARTの初期化 (timeoutを長めにして確実に待つ)
lora_uart = machine.UART(2, baudrate=9600, rx=RX_PIN, tx=TX_PIN, timeout=2000)

# M0, M1 ピンの設定
m0 = machine.Pin(4, machine.Pin.OUT)
m1 = machine.Pin(5, machine.Pin.OUT)

def read_config():
    # 1. 設定モードへ移行
    print("Switching to Configuration Mode (M0=1, M1=1)...")
    m0.value(1)
    m1.value(1)
    time.sleep(0.5) # モードが安定するまで少し長めに待つ

    # 2. UARTバッファを空にする (掃除)
    if lora_uart.any():
        lora_uart.read()
        print("Cleared old data from buffer.")

    # 3. 設定読み出しコマンド送付
    cmd = bytes([0xC1, 0x00, 0x08])
    print("Sending: 0xC1 0x00 0x08")
    lora_uart.write(cmd)

    # 4. 返信を待つ
    time.sleep(1.0)
    
    if lora_uart.any():
        res = lora_uart.read()
        raw_hex = [hex(b) for b in res]
        print("Response (Raw):", raw_hex)
        
        if len(res) >= 11 and res[0] == 0xC1:
            addr = (res[3] << 8) + res[4]
            chan = res[7]
            mode_bit = (res[8] & 0b01000000) >> 6
            
            print("\n--- E220 Current Settings ---")
            print("Address: 0x{:04X}".format(addr))
            print("Channel: {}".format(chan))
            print("Transmission Mode: {}".format("Transparent" if mode_bit == 0 else "Fixed"))
            print("-----------------------------\n")
        else:
            print("Error: Invalid or incomplete response.")
            if len(res) > 0 and res[0] != 0xC1:
                print("Hint: First byte should be 0xC1, but got {}. Check M0/M1 pins.".format(hex(res[0])))
    else:
        print("Error: No response from module. Is E220 powered and M0/M1 High?")

    # 通常モードに戻す
    m0.value(0)
    m1.value(0)

if __name__ == "__main__":
    read_config()
