# 変数定義
PORT = /dev/ttyUSB0
MPREMOTE = mpremote

.PHONY: repl ls check-config update-config deploy-main

# REPL（シリアルコンソール）に入る
repl:
	$(MPREMOTE) connect $(PORT) repl

# ESP32内のファイル一覧を表示
ls:
	$(MPREMOTE) connect $(PORT) ls

# 設定確認スクリプトを実行
check-config:
	$(MPREMOTE) connect $(PORT) run check_config.py

# 設定更新スクリプトを実行
update-config:
	$(MPREMOTE) connect $(PORT) run update_config.py

# main.py を ESP32 に書き込む
deploy-main:
	$(MPREMOTE) connect $(PORT) cp main.py :main.py
	$(MPREMOTE) connect $(PORT) soft-reset
