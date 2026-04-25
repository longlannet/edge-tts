---
name: edge-tts
description: Free, high-quality Text-to-Speech using Microsoft Edge's online API. Use when the user asks to speak, read aloud, generate audio, make a voice note, or say something aloud.
homepage: https://github.com/rany2/edge-tts
metadata:
  {
    "openclaw":
      {
        "emoji": "🗣️",
        "os": ["linux", "darwin"],
        "requires":
          {
            "bins": ["python3", "ffmpeg"],
            "scripts": ["scripts/install.sh", "scripts/check.sh"]
          },
        "install":
          [
            {
              "id": "pip-edge-tts",
              "kind": "python",
              "package": "edge-tts",
              "bins": ["python3"],
              "label": "Install edge-tts (python)",
            },
          ],
      },
  }
---

# Edge TTS

Use this skill to generate spoken audio from text with Microsoft Edge online voices.

## When to use

Use this skill when the user asks to:
- speak / read text aloud
- generate audio from text
- make a short voice-note style reply
- try a specific Microsoft Edge Neural voice

Do not use it for speech-to-text transcription.

## Quick start

```bash
bash scripts/install.sh
bash scripts/check.sh
./venv/bin/python scripts/speak.py "你好，我是小珍。" --voice zh-CN-XiaoxiaoNeural
```

## OpenClaw delivery rule

`scripts/speak.py` prints a `MEDIA:/absolute/path` line. After a successful run, reply with `NO_REPLY` so OpenClaw can deliver the generated audio without duplicating it as text.

Do not use the `message` tool to send the generated audio separately.

### Telegram voice bubble rule

If the current surface is Telegram and the user asks for a voice message / 语音泡泡 / voice note, default to Telegram voice mode:

```bash
{baseDir}/venv/bin/python {baseDir}/scripts/speak.py "{{text}}" --voice-note
```

This generates `.ogg` audio encoded with Opus, which is Telegram's most reliable native voice-bubble format. Use MP3 only when the user asks for a regular audio file instead of a Telegram voice bubble.

## Main command

```bash
{baseDir}/venv/bin/python {baseDir}/scripts/speak.py "{{text}}" --voice "{{voice:-zh-CN-XiaoxiaoNeural}}"
```

Useful options:
- `--voice`: voice id, default `zh-CN-XiaoxiaoNeural`
- `--rate`: speech rate, e.g. `+10%` or `-10%`
- `--volume`: volume adjustment, e.g. `+10%`
- `--pitch`: pitch adjustment, e.g. `+5Hz`
- `--format`: `mp3` or `ogg`; default is `mp3`
- `--voice-note`: Telegram-style voice-bubble mode; defaults format to `ogg`
- `--output`: explicit output file path
- `--output-dir`: output directory when `--output` is not provided

## Common voices

- `zh-CN-XiaoxiaoNeural` — Chinese female, default
- `zh-CN-YunxiNeural` — Chinese male
- `zh-CN-XiaoyiNeural` — Chinese female
- `en-US-AriaNeural` — English female
- `en-US-GuyNeural` — English male

List all available voices:

```bash
./venv/bin/edge-tts --list-voices
```

## Notes

- Requires network access to Microsoft's Edge TTS service.
- Generated files are written to `media/` by default.
- Telegram voice bubbles should use `--voice-note` / `.ogg` Opus output.
- `venv/` and `media/` are runtime artifacts and should not be committed.
- If the local environment is missing or stale, rerun `scripts/install.sh`.
