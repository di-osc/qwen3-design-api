# 音色设计API

基于Qwen3-TTS的音色设计服务，支持根据文本和语音指令生成定制音频。

## 安装依赖

```bash
pip install -r requirements.txt
```

## 运行服务

```bash
python server.py
```

服务将在 http://localhost:8000 启动

## API接口

### GET /

检查服务状态

### POST /generate_audio

生成音频文件

**参数:**
- `text` (必需): 要合成的文本内容
- `language` (可选): 文本语言，默认为 "Chinese"
- `instruct` (必需): 语音指令，用于控制音色设计

**示例请求:**
```bash
curl -X POST "http://localhost:8000/generate_audio?text=你好世界&instruct=温柔的女声" \
     -o generated_audio.wav
```

**返回:** WAV格式的音频文件

## 语音指令示例

- "体现撒娇稚嫩的萝莉女声，音调偏高且起伏明显"
- "成熟稳重的男声，语速适中"
- "活泼开朗的少女声，充满活力"