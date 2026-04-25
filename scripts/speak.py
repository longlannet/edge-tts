#!/usr/bin/env python3
"""Generate speech with edge-tts and print an OpenClaw MEDIA line."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import uuid
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_VOICE = "zh-CN-XiaoxiaoNeural"
DEFAULT_OUTPUT_DIR = BASE_DIR / "media"


def resolve_edge_tts() -> str:
    """Find the edge-tts executable, preferring the skill-local venv."""
    local_bin = BASE_DIR / "venv" / "bin" / "edge-tts"
    if local_bin.exists() and local_bin.is_file():
        return str(local_bin)

    discovered = shutil.which("edge-tts")
    if discovered:
        return discovered

    print(
        "edge-tts executable not found. Run `bash scripts/install.sh` from the skill root.",
        file=sys.stderr,
    )
    sys.exit(1)


def build_output_path(output: str | None, output_dir: str | None) -> Path:
    if output:
        path = Path(output).expanduser()
        return path if path.is_absolute() else Path.cwd() / path

    directory = Path(output_dir).expanduser() if output_dir else DEFAULT_OUTPUT_DIR
    if not directory.is_absolute():
        directory = Path.cwd() / directory
    return directory / f"tts_{uuid.uuid4().hex[:8]}.mp3"


def run_edge_tts(cmd: list[str]) -> None:
    proc = subprocess.run(cmd, text=True, capture_output=True)
    if proc.returncode != 0:
        detail = (proc.stderr or proc.stdout or "edge-tts failed").strip()
        print(detail, file=sys.stderr)
        sys.exit(proc.returncode)


def main() -> None:
    parser = argparse.ArgumentParser(description="Edge TTS wrapper for OpenClaw")
    parser.add_argument("text", help="Text to speak")
    parser.add_argument("--voice", default=DEFAULT_VOICE, help=f"Voice id (default: {DEFAULT_VOICE})")
    parser.add_argument("--rate", default="+0%", help="Rate adjustment, e.g. +10%% or -10%%")
    parser.add_argument("--volume", default="+0%", help="Volume adjustment, e.g. +10%%")
    parser.add_argument("--pitch", default="+0Hz", help="Pitch adjustment, e.g. +5Hz or -5Hz")
    parser.add_argument("--output", help="Explicit output file path. Defaults to media/tts_<id>.mp3")
    parser.add_argument("--output-dir", help="Output directory when --output is not provided")
    args = parser.parse_args()

    text = args.text.strip()
    if not text:
        print("Text must not be empty.", file=sys.stderr)
        sys.exit(2)

    output_path = build_output_path(args.output, args.output_dir)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    edge_tts_bin = resolve_edge_tts()
    cmd = [
        edge_tts_bin,
        "--voice",
        args.voice,
        "--rate",
        args.rate,
        "--volume",
        args.volume,
        "--pitch",
        args.pitch,
        "--text",
        text,
        "--write-media",
        str(output_path),
    ]
    run_edge_tts(cmd)

    print(f"MEDIA:{output_path.resolve()}")


if __name__ == "__main__":
    main()
