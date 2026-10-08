#!/bin/bash
# Ping-Hash daemon: jalankan ping_hash.py dengan delay acak 1-8 menit di antara tiap eksekusi.
# Loop ini jalan terus (via systemd atau screen/nohup), BUKAN cron tetap.

while true; do
  /usr/bin/python3 "$HOME/ping-hash/ping_hash.py" >> "$HOME/ping-hash/cron.log" 2>&1
  # delay acak 60-480 detik (1-8 menit)
  SLEEP=$((60 + RANDOM % 421))
  echo "[daemon] sleep ${SLEEP}s" >> "$HOME/ping-hash/cron.log"
  sleep "$SLEEP"
done
