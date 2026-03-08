# LoRa E220-900T22S(JP)-EV1 with ATmega8 (Rust)

このプロジェクトは、ATmega8/16PUを使用して LoRa モジュール **E220-900T22S(JP)-EV1** でデータを送受信するための Rust サンプルコードです。

## 特徴
- **透過伝送モード (Normal Mode)** を使用したシンプルなシリアル通信。
- 送信側 (Transmitter) と受信側 (Receiver) の両方のコードを含みます。
- `atmega-hal` を使用した Rust による組み込み実装。

## ディレクトリ構成
- `atmega8/`: ATmega8 用の Rust プロジェクト。
  - `src/transmitter.rs`: 送信側プログラム。5秒ごとにメッセージを送信。
  - `src/receiver.rs`: 受信側プログラム。データ受信時に LED (PB0) をトグル。

## 接続 (ATmega8 <-> E220-900T22S(JP))

| E220 側 | ATmega8 側 | 備考 |
| :--- | :--- | :--- |
| **RXD** | **PD1 (TX)** | |
| **TXD** | **PD0 (RX)** | |
| **M0** | **PD2** | 送受信時は Low (GND) に固定 |
| **M1** | **PD3** | 送受信時は Low (GND) に固定 |
| **AUX** | **PD4** | 送信側で使用（ビジー確認用） |
| **VCC** | **3.3V** | **注意: 5V は不可** |
| **GND** | **GND** | |

※ LED は ATmega8 の **PB0** ピンに接続してください。

## ビルド方法

Nix 環境（`nix develop`）または Rust AVR ツールチェーンがセットアップされた環境で実行してください。

```bash
cd atmega8
cargo build --release -Zjson-target-spec
```

生成された ELF ファイル:
- `atmega8/target/avr-atmega8/release/transmitter`
- `atmega8/target/avr-atmega8/release/receiver`

## 受信側 (Raspberry Pi / Python)

Raspberry Pi を受信機として使用する場合、`rpi/receiver.py` を使用します。

### 接続 (Raspberry Pi <-> E220-900T22S(JP))

| E220 側 | Raspberry Pi 側 | 備考 |
| :--- | :--- | :--- |
| **RXD** | **GPIO 14 (TXD)** | 物理番号 8 番 |
| **TXD** | **GPIO 15 (RXD)** | 物理番号 10 番 |
| **M0/M1** | **GND** | 送受信モード (Low) |
| **VCC** | **3.3V** | 物理番号 1 番 |
| **GND** | **GND** | 物理番号 6 番など |

### 実行方法 (Raspberry Pi)

1. `pyserial` をインストールします。
   ```bash
   pip install pyserial
   ```
2. シリアルポート (`/dev/serial0`) を有効化します。
   - `sudo raspi-config` -> `Interface Options` -> `Serial Port`
   - **Serial Login Shell**: NO
   - **Serial Port Hardware**: YES
3. 受信スクリプトを実行します。
   ```bash
   python rpi/receiver.py
   ```

## 注意事項
- E220 モジュールのデフォルト設定（9600bps, 透過伝送）を想定しています。
- 日本国内で使用する場合は、電波法に適合した（技適マーク付きの）モジュールを使用し、適切なチャンネル設定を行ってください。
- E220-900T22S(JP) は 3.3V 駆動です。ATmega8 を 5V で動作させる場合は、信号線のレベルシフト（分圧抵抗など）が必要です。
