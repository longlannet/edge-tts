#!/usr/bin/env bash
set -euo pipefail

BASE_DIR="$(cd "$(dirname "$0")/.." && pwd)"
VENV_DIR="$BASE_DIR/venv"
BIN_DIR="$VENV_DIR/bin"
REQ_FILE="$BASE_DIR/requirements.txt"
RUN_SMOKE="${RUN_SMOKE:-1}"

log() { printf '[edge-tts] %s\n' "$*"; }
fail() { printf '[edge-tts] ERROR: %s\n' "$*" >&2; exit 1; }

log "base dir: $BASE_DIR"
command -v python3 >/dev/null 2>&1 || fail "python3 not found"

if [ ! -d "$VENV_DIR" ]; then
  log "creating venv: $VENV_DIR"
  python3 -m venv "$VENV_DIR"
else
  log "venv already exists: $VENV_DIR"
fi

log "upgrading pip"
"$BIN_DIR/pip" install --upgrade pip >/dev/null

log "installing requirements"
"$BIN_DIR/pip" install -r "$REQ_FILE"

[ -x "$BIN_DIR/edge-tts" ] || fail "edge-tts binary missing after install: $BIN_DIR/edge-tts"

if [ "$RUN_SMOKE" = "1" ]; then
  log "running smoke test"
  "$BIN_DIR/python" "$BASE_DIR/scripts/speak.py" "测试" --output "/tmp/edge-tts-skill-smoke.mp3" >/tmp/edge-tts-skill-smoke.out
  grep -q '^MEDIA:' /tmp/edge-tts-skill-smoke.out || fail "smoke test did not return MEDIA output"
  [ -s /tmp/edge-tts-skill-smoke.mp3 ] || fail "smoke output file missing or empty"
  log "smoke test: OK"
fi

log "install complete"
