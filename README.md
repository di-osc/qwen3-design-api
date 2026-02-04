# 音色设计API

基于Qwen3-TTS的音色设计服务，支持根据文本和语音指令生成定制音频。

## 安装依赖

```bash
# 安装Python依赖
pip install -r requirements.txt

# 安装系统依赖（Ubuntu/Debian）
sudo apt-get update && sudo apt-get install -y sox
```

## 运行服务

```bash
python server.py
```

服务将在 `http://0.0.0.0:8867` 启动（可通过 `http://localhost:8867` 访问）

### 后台运行（推荐）

```bash
# 使用screen在后台运行
screen -S voice-api
python server.py

# 按Ctrl+A+D分离screen会话
# 重新连接：screen -r voice-api
```

### 检查服务状态

```bash
curl http://localhost:8867/
```

## 测试

项目包含两个测试脚本：

### 快速测试

```bash
python quick_test.py
```

快速验证API基本功能，无需手动启动服务器。

### 完整测试

```bash
python test_api.py
```

完整测试套件，包括：
- 自动启动/停止服务器
- 多语言音频生成测试
- 音频文件验证
- 详细的测试报告

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
# 生成音频文件
curl -X POST "http://localhost:8000/generate_audio?text=你好世界&instruct=温柔的女声" \
     -o generated_audio.wav

# 使用中文文本和指令
curl -X POST "http://localhost:8000/generate_audio?text=哥哥，你回来啦&language=Chinese&instruct=体现撒娇稚嫩的萝莉女声，音调偏高且起伏明显" \
     -o cute_voice.wav

# 使用英文文本
curl -X POST "http://localhost:8000/generate_audio?text=Hello world&language=English&instruct=Speak in a cheerful and energetic tone" \
     -o english_audio.wav
```

**返回:** WAV格式的音频文件

## 语音指令示例

- "体现撒娇稚嫩的萝莉女声，音调偏高且起伏明显"
- "成熟稳重的男声，语速适中"
- "活泼开朗的少女声，充满活力"