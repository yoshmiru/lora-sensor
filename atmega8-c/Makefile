# C-blink Makefile
MCU = atmega8
F_CPU = 1000000UL
CC = avr-gcc
OBJCOPY = avr-objcopy

# float を sprintf で使うためのフラグ
# ATmega8 のメモリ(8KB)をかなり消費するので注意
CFLAGS = -mmcu=$(MCU) -Os -DF_CPU=$(F_CPU)
LDFLAGS = -Wl,-u,vfprintf -lprintf_flt -lm

# 書き込み設定
AVRDUDE = avrdude
PROGRAMMER = avrisp
PORT = /dev/ttyUSB0
BAUD = 19200

.PHONY: all flash flash-tx clean

all: blink.hex lora_tx.hex

# 診断用Lチカ
blink.elf: blink.c
	$(CC) $(CFLAGS) blink.c -o blink.elf

blink.hex: blink.elf
	$(OBJCOPY) -j .text -j .data -O ihex blink.elf blink.hex

flash: blink.hex
	$(AVRDUDE) -c $(PROGRAMMER) -P $(PORT) -b $(BAUD) -p m8 -U flash:w:blink.hex:i

# LoRa送信テスト用 (float対応)
lora_tx.elf: lora_tx.c
	$(CC) $(CFLAGS) lora_tx.c -o lora_tx.elf $(LDFLAGS)

lora_tx.hex: lora_tx.elf
	$(OBJCOPY) -j .text -j .data -O ihex lora_tx.elf lora_tx.hex

flash-tx: lora_tx.hex
	$(AVRDUDE) -c $(PROGRAMMER) -P $(PORT) -b $(BAUD) -p m8 -U flash:w:lora_tx.hex:i

clean:
	rm -f *.elf *.hex
