# 各コンポーネントのディレクトリ
AVR_C_DIR = atmega8-c
ESP32_DIR = esp32
RPI_DIR = rpi

# コマンド
.PHONY: build-tx flash-tx esp32-check esp32-update esp32-deploy run-gateway clean

# --- ATmega8 (C言語版) ---
build-tx:
	$(MAKE) -C $(AVR_C_DIR) all

flash-tx:
	$(MAKE) -C $(AVR_C_DIR) flash-tx

# --- PC / Raspberry Pi Gateway ---
# ESP32 の Wi-Fi が不安定な場合、こちらをメインに使用します
run-gateway:
	python3 $(RPI_DIR)/receiver.py

# --- ESP32 (MicroPython) ---
esp32-check:
	$(MAKE) -C $(ESP32_DIR) check-config

esp32-update:
	$(MAKE) -C $(ESP32_DIR) update-config

esp32-deploy:
	$(MAKE) -C $(ESP32_DIR) deploy-main

# --- クリーンアップ ---
clean:
	$(MAKE) -C $(AVR_C_DIR) clean
