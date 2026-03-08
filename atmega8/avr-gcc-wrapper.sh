#!/usr/bin/env bash
# 引数から --eh-frame-hdr を削除して本物の avr-gcc を呼び出す
ARGS=()
for arg in "$@"; do
  if [ "$arg" != "-Wl,--eh-frame-hdr" ] && [ "$arg" != "--eh-frame-hdr" ]; then
    ARGS+=("$arg")
  fi
done

exec /nix/store/mpsrz88mifqxxz2v7x1lwzq2l36x2v1c-avr-gcc-15.2.0/bin/avr-gcc "${ARGS[@]}"
