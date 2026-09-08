#!/usr/bin/env bash
# NAS / Linux 무인 실행 래퍼.
# 예약 작업(cron)에 이 파일을 걸어두면 새 DEM이 들어올 때마다 도면이 나온다.
#
#   crontab 예)  */10 * * * * /volume1/drone/scripts/run_watch.sh
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# 아래 세 줄만 현장에 맞게 고치세요.
IN_DIR="${IN_DIR:-$HERE/입력}"
OUT_DIR="${OUT_DIR:-$HERE/출력}"
ARCHIVE_DIR="${ARCHIVE_DIR:-$HERE/처리완료}"

export PYTHONPATH="$HERE:${PYTHONPATH:-}"
export PYTHONIOENCODING=utf-8

# --once: 한 번만 훑고 끝낸다. cron이 주기를 맡으므로 상주할 필요가 없다.
exec python3 -m terrain2dxf watch "$IN_DIR" "$OUT_DIR" \
    --archive "$ARCHIVE_DIR" \
    --once \
    --ground-filter \
    --flatten-z \
    --scale 1/1000 \
    --log "$OUT_DIR/자동처리.log"
