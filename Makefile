# 各コンポーネントのディレクトリ
AVR_C_DIR = atmega8-c
ESP32_DIR = esp32
RPI_DIR = rpi

# コマンド
.PHONY: build-tx flash-tx esp32-check esp32-update esp32-deploy run-rpi clean

# --- ATmega8 (C言語版 - 推奨) ---
# 安定性を考慮し、送信機は C 言語版を使用します
build-tx:
	$(MAKE) -C $(AVR_C_DIR) all

flash-tx:
	$(MAKE) -C $(AVR_C_DIR) flash-tx

# --- ESP32 (MicroPython) ---
esp32-check:
	$(MAKE) -C $(ESP32_DIR) check-config

esp32-update:
	$(MAKE) -C $(ESP32_DIR) update-config

esp32-deploy:
	$(MAKE) -C $(ESP32_DIR) deploy-main

# --- Raspberry Pi ---
run-rpi:
	python3 $(RPI_DIR)/receiver.py

# --- クリーンアップ ---
clean:
	$(MAKE) -C $(AVR_C_DIR) clean
