import machine
import time

# UART2 (RX=16, TX=17)
lora_uart = machine.UART(2, baudrate=9600, rx=16, tx=17, timeout=100)

print("--- LoRa Raw Sniffer Mode ---")

while True:
    try:
        if lora_uart.any():
            # 届いたデータをそのままバイナリで表示
            raw = lora_uart.read()
            print("RAW DATA:", raw)
            try:
                print("DECODED :", raw.decode('utf-8'))
            except:
                pass
            print("---")
    except Exception as e:
        print("Error:", e)
    
    time.sleep(0.1)
