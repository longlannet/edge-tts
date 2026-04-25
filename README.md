# edge-tts

面向 OpenClaw 的文字转语音 skill，使用 Microsoft Edge 在线语音服务生成音频。

## 它能做什么

- 把文字生成语音文件
- 默认使用中文女声 `zh-CN-XiaoxiaoNeural`
- 支持指定 Edge Neural voice
- 输出 `MEDIA:/path/to/file.mp3`，方便 OpenClaw 自动发送音频

## 安装

```bash
bash scripts/install.sh
```

## 校验

```bash
bash scripts/check.sh
```

## 常用命令

```bash
./venv/bin/python scripts/speak.py "你好，我是小珍。"
./venv/bin/python scripts/speak.py "Hello from OpenClaw." --voice en-US-AriaNeural
./venv/bin/python scripts/speak.py "语速快一点。" --rate +10%
./venv/bin/edge-tts --list-voices
```

## 输出规则

`scripts/speak.py` 成功后会打印：

```text
MEDIA:/absolute/path/to/audio.mp3
```

在 OpenClaw 对话里，生成成功后直接回复 `NO_REPLY`，让系统自动发送音频；不要再额外调用消息工具发送同一个文件。

## 说明

- 需要联网访问 Microsoft Edge TTS 服务。
- `venv/` 是本地虚拟环境，`media/` 是生成音频目录，二者不会提交到仓库。
- 如果环境异常，重新运行 `scripts/install.sh`。
