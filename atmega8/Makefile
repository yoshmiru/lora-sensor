# 変数定義
CARGO = cargo
TARGET = avr-atmega8.json
MCU = m8
AVRDUDE = avrdude
PROGRAMMER = avrisp
PORT = /dev/ttyUSB0
BAUD = 19200

# バイナリのパス
BIN_DIR = target/avr-atmega8/release

.PHONY: build-tx build-rx flash-tx flash-rx clean

# ビルドコマンド
build-tx:
	$(CARGO) build --release --bin transmitter --target $(TARGET) -Zjson-target-spec

build-rx:
	$(CARGO) build --release --bin receiver --target $(TARGET) -Zjson-target-spec

# 書き込みコマンド
flash-tx: build-tx
	$(AVRDUDE) -c $(PROGRAMMER) -P $(PORT) -b $(BAUD) -p $(MCU) -U flash:w:$(BIN_DIR)/transmitter:e

flash-rx: build-rx
	$(AVRDUDE) -c $(PROGRAMMER) -P $(PORT) -b $(BAUD) -p $(MCU) -U flash:w:$(BIN_DIR)/receiver:e

clean:
	$(CARGO) clean
