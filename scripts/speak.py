#!/usr/bin/env python3
"""Generate speech with edge-tts and print an OpenClaw MEDIA line."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
import uuid
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_VOICE = "zh-CN-XiaoxiaoNeural"
DEFAULT_OUTPUT_DIR = BASE_DIR / "media"
DEFAULT_FORMAT = "mp3"
VOICE_NOTE_FORMAT = "ogg"


def resolve_bin(name: str, local_name: str | None = None) -> str | None:
    local_name = local_name or name
    local_bin = BASE_DIR / "venv" / "bin" / local_name
    if local_bin.exists() and local_bin.is_file():
        return str(local_bin)
    return shutil.which(name)


def require_edge_tts() -> str:
    edge_tts_bin = resolve_bin("edge-tts")
    if edge_tts_bin:
        return edge_tts_bin

    print(
        "edge-tts executable not found. Run `bash scripts/install.sh` from the skill root.",
        file=sys.stderr,
    )
    sys.exit(1)


def require_ffmpeg() -> str:
    ffmpeg_bin = shutil.which("ffmpeg")
    if ffmpeg_bin:
        return ffmpeg_bin

    print(
        "ffmpeg is required for OGG/Opus output. Install ffmpeg or use `--format mp3`.",
        file=sys.stderr,
    )
    sys.exit(1)


def choose_format(raw_format: str | None, output: str | None, voice_note: bool) -> str:
    if raw_format:
        return raw_format
    if voice_note:
        return VOICE_NOTE_FORMAT
    if output:
        suffix = Path(output).suffix.lower().lstrip(".")
        if suffix in {"mp3", "ogg"}:
            return suffix
    return DEFAULT_FORMAT


def build_output_path(output: str | None, output_dir: str | None, audio_format: str) -> Path:
    if output:
        path = Path(output).expanduser()
        return path if path.is_absolute() else Path.cwd() / path

    directory = Path(output_dir).expanduser() if output_dir else DEFAULT_OUTPUT_DIR
    if not directory.is_absolute():
        directory = Path.cwd() / directory
    return directory / f"tts_{uuid.uuid4().hex[:8]}.{audio_format}"


def run_command(cmd: list[str], label: str) -> None:
    proc = subprocess.run(cmd, text=True, capture_output=True)
    if proc.returncode != 0:
        detail = (proc.stderr or proc.stdout or f"{label} failed").strip()
        print(detail, file=sys.stderr)
        sys.exit(proc.returncode)


def synthesize_mp3(edge_tts_bin: str, args: argparse.Namespace, mp3_path: Path) -> None:
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
        args.text.strip(),
        "--write-media",
        str(mp3_path),
    ]
    run_command(cmd, "edge-tts")


def convert_mp3_to_ogg(ffmpeg_bin: str, mp3_path: Path, ogg_path: Path) -> None:
    cmd = [
        ffmpeg_bin,
        "-y",
        "-hide_banner",
        "-loglevel",
        "error",
        "-i",
        str(mp3_path),
        "-vn",
        "-c:a",
        "libopus",
        "-b:a",
        "32k",
        str(ogg_path),
    ]
    run_command(cmd, "ffmpeg")


def main() -> None:
    parser = argparse.ArgumentParser(description="Edge TTS wrapper for OpenClaw")
    parser.add_argument("text", help="Text to speak")
    parser.add_argument("--voice", default=DEFAULT_VOICE, help=f"Voice id (default: {DEFAULT_VOICE})")
    parser.add_argument("--rate", default="+0%", help="Rate adjustment, e.g. +10%% or -10%%")
    parser.add_argument("--volume", default="+0%", help="Volume adjustment, e.g. +10%%")
    parser.add_argument("--pitch", default="+0Hz", help="Pitch adjustment, e.g. +5Hz or -5Hz")
    parser.add_argument("--format", choices=["mp3", "ogg"], help="Output format. Defaults to mp3; voice-note mode defaults to ogg")
    parser.add_argument("--voice-note", action="store_true", help="Telegram-style voice bubble mode; defaults to OGG/Opus")
    parser.add_argument("--output", help="Explicit output file path. Defaults to media/tts_<id>.<format>")
    parser.add_argument("--output-dir", help="Output directory when --output is not provided")
    args = parser.parse_args()

    if not args.text.strip():
        print("Text must not be empty.", file=sys.stderr)
        sys.exit(2)

    audio_format = choose_format(args.format, args.output, args.voice_note)
    output_path = build_output_path(args.output, args.output_dir, audio_format)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    edge_tts_bin = require_edge_tts()

    if audio_format == "mp3":
        synthesize_mp3(edge_tts_bin, args, output_path)
    elif audio_format == "ogg":
        ffmpeg_bin = require_ffmpeg()
        with tempfile.TemporaryDirectory(prefix="edge-tts-") as tmp_dir:
            tmp_mp3 = Path(tmp_dir) / "source.mp3"
            synthesize_mp3(edge_tts_bin, args, tmp_mp3)
            convert_mp3_to_ogg(ffmpeg_bin, tmp_mp3, output_path)
    else:  # pragma: no cover - guarded by argparse choices
        print(f"Unsupported format: {audio_format}", file=sys.stderr)
        sys.exit(2)

    print(f"MEDIA:{output_path.resolve()}")


if __name__ == "__main__":
    main()
