---
name: "edge-tts"
description: "Generate Edge TTS audio and deliver reliable audio files or Telegram voice bubbles through OpenClaw."
homepage: https://github.com/longlannet/edge-tts
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
              "label": "Install edge-tts",
            },
          ],
      },
  }
---

# Edge TTS

Use this skill to generate spoken audio with Microsoft Edge online voices and deliver the resulting file through OpenClaw.

## When to use

Use this skill when the user asks to:
- speak or read text aloud
- generate audio from text
- make a short voice-note style reply
- try a specific Microsoft Edge Neural voice

Do not use it for speech-to-text transcription.

## Quick start

```bash
bash scripts/install.sh
bash scripts/check.sh
./venv/bin/python scripts/speak.py "你好，这是语音示例。" --voice zh-CN-XiaoxiaoNeural
```

## Required delivery workflow

`scripts/speak.py` prints one `MEDIA:/absolute/path` line after successful generation. Treat that line only as the location of the generated file. Tool output is not itself a channel delivery event.

1. Run `scripts/speak.py` and capture the absolute path from its `MEDIA:` line.
2. Confirm the command succeeded and the file exists.
3. Deliver the file with OpenClaw's structured `message` tool.
4. After the message tool reports success, reply with exactly `NO_REPLY` to avoid duplicate text or attachments.
5. If delivery fails, do not claim success. Retry once with the smallest valid payload after removing optional fields. If it still fails, report the exact blocker.

For message-tool calls, omit optional keys that are not needed. Do not populate them with empty strings, placeholder numbers, or guessed identifiers.

## Telegram voice bubbles

When the current surface is Telegram and the user asks for a voice message, voice note, or 语音泡泡, generate native Ogg/Opus output:

```bash
{baseDir}/venv/bin/python {baseDir}/scripts/speak.py "{{text}}" --voice "{{voice:-zh-CN-XiaoxiaoNeural}}" --voice-note
```

Then send the generated path as a structured voice attachment. Use only the fields required for the current send, for example:

```json
{
  "action": "send",
  "target": "<current Telegram chat id>",
  "message": "",
  "media": "/absolute/path/to/generated.ogg",
  "asVoice": true
}
```

Use the current trusted channel context to resolve the target. Do not guess a chat, topic, or message identifier.

### Reply and thread safety

- `replyTo` is a Telegram message ID and may be included when a valid current inbound message ID is available.
- `threadId` is a Telegram forum/topic identifier. It is not a message ID.
- In ordinary Telegram direct chats, omit `threadId` entirely.
- Set `threadId` only when trusted inbound channel metadata explicitly provides a genuine topic/thread ID.
- Never copy `replyTo` into `threadId`.

A direct-chat reply may therefore use:

```json
{
  "action": "send",
  "target": "<current Telegram chat id>",
  "message": "",
  "media": "/absolute/path/to/generated.ogg",
  "asVoice": true,
  "replyTo": "<current inbound message id>"
}
```

If a send attempt returns `message thread not found`, remove an incorrectly supplied `threadId`; do not invent another thread value.

## Regular audio files

When the user asks for a normal audio file instead of a voice bubble, generate MP3 by default:

```bash
{baseDir}/venv/bin/python {baseDir}/scripts/speak.py "{{text}}" --voice "{{voice:-zh-CN-XiaoxiaoNeural}}"
```

Send the generated path with the structured `message` tool and leave `asVoice` false or omit it.

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
- Telegram voice bubbles should use `--voice-note` and Ogg/Opus output.
- `venv/` and `media/` are runtime artifacts and should not be committed.
- If the local environment is missing or stale, rerun `scripts/install.sh`.
