# LoRa E220 IoT System (ATmega8 to Cloudflare)

ATmega8 を送信機とし、ESP32 をゲートウェイにして Cloudflare Workers へデータを転送する IoT システムのサンプルコードです。

## 特徴
- **送信機 (ATmega8)**: C言語による軽量・安定実装。1MHz内蔵クロックで動作。
- **ゲートウェイ (ESP32)**: MicroPython 実装。LoRa 受信データを Wi-Fi 経由でクラウドへ転送。
- **クラウド (Cloudflare Workers)**: 受信データの処理とログ保存。

## ディレクトリ構成
- `atmega8-c/`: 送信機ソースコード (C言語)。
- `esp32/`: ゲートウェイソースコード (MicroPython)。
- `cloudflare/`: クラウド側ロジック (TypeScript / Wrangler)。
- `rpi/`: ローカル受信用スクリプト (Python)。

## クイックスタート

### 1. 送信機の書き込み (ATmega8)
```bash
# ビルドと書き込みを実行
make flash-tx
```
※ PB0 ピンに接続された LED が 5秒おきに点滅し、LoRa 送信が行われます。

### 2. ゲートウェイの準備 (ESP32)
1. `esp32/main.py` の `WIFI_SSID`, `WIFI_PASS`, `WORKER_URL` を編集します。
2. ファイルを ESP32 に書き込みます。
   ```bash
   make esp32-deploy
   ```

### 3. モジュールの設定確認 (オプション)
E220 モジュールが「透過伝送モード」になっていない場合は、ESP32 を使って設定を変更できます。
```bash
make esp32-check   # 設定確認
make esp32-update  # 透過モードへ更新
```

## 接続図 (ATmega8 <-> E220)

| E220 側 | ATmega8 側 | 備考 |
| :--- | :--- | :--- |
| **RXD** | **PD1 (3番ピン)** | UART 送信ライン |
| **M0/M1** | **GND** | 通常モード固定 |
| **VCC** | **3.3V** | パスコン(10uF〜)推奨 |
| **GND** | **GND** | 共通GNDを確実に接続 |

## 免責事項
- このコードは学習・実験用です。日本国内での運用は電波法を遵守してください。
