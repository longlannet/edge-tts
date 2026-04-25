#!/usr/bin/env bash
set -euo pipefail

BASE_DIR="$(cd "$(dirname "$0")/.." && pwd)"
VENV_DIR="$BASE_DIR/venv"
BIN_DIR="$VENV_DIR/bin"
RUN_SMOKE="${RUN_SMOKE:-1}"

log() { printf '[edge-tts] %s\n' "$*"; }
fail() { printf '[edge-tts] ERROR: %s\n' "$*" >&2; exit 1; }

log "base dir: $BASE_DIR"
[ -x "$BIN_DIR/python" ] || fail "venv python missing: $BIN_DIR/python (run scripts/install.sh)"
[ -x "$BIN_DIR/edge-tts" ] || fail "edge-tts binary missing: $BIN_DIR/edge-tts (run scripts/install.sh)"
[ -f "$BASE_DIR/scripts/speak.py" ] || fail "speak.py missing"

log "import check"
"$BIN_DIR/python" - <<'PY'
import edge_tts
print('edge_tts_import=OK')
PY

log "help check"
"$BIN_DIR/python" "$BASE_DIR/scripts/speak.py" --help >/tmp/edge-tts-skill-help.txt

if [ "$RUN_SMOKE" = "1" ]; then
  log "running smoke test"
  OUT_FILE="/tmp/edge-tts-skill-check.mp3"
  OUT_LOG="/tmp/edge-tts-skill-check.out"
  rm -f "$OUT_FILE" "$OUT_LOG"
  "$BIN_DIR/python" "$BASE_DIR/scripts/speak.py" "测试" --output "$OUT_FILE" >"$OUT_LOG"
  grep -q '^MEDIA:' "$OUT_LOG" || fail "smoke test did not return MEDIA output"
  [ -s "$OUT_FILE" ] || fail "smoke output file missing or empty"
  log "smoke test: OK"
fi

log "check complete"
