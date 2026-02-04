import io
import logging

import torch
import soundfile as sf
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from qwen_tts import Qwen3TTSModel

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 全局模型变量
model = None


def init_model():
    """初始化Qwen3-TTS模型"""
    global model
    try:
        logger.info("正在加载Qwen3-TTS模型...")
        model = Qwen3TTSModel.from_pretrained(
            "/root/autodl-tmp/Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign",
            device_map="cuda:0",
            dtype=torch.bfloat16,
            attn_implementation="flash_attention_2",
        )
        logger.info("模型加载完成")
    except Exception as e:
        logger.error(f"模型加载失败: {e}")
        raise


# 创建FastAPI应用
app = FastAPI(
    title="音色设计API", description="基于Qwen3-TTS的音色设计服务", version="1.0.0"
)

# 启动时初始化模型
@app.on_event("startup")
async def startup_event():
    init_model()

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """根路径"""
    return {"message": "音色设计API服务运行中", "version": "1.0.0"}


@app.post("/generate_audio")
async def generate_audio(
    text: str = Query(..., description="要合成的文本内容"),
    language: str = Query("Chinese", description="文本语言，默认为Chinese"),
    instruct: str = Query(..., description="语音指令，用于控制音色设计"),
):
    """
    根据文本和指令生成音频

    - **text**: 要合成的文本
    - **language**: 文本语言 (Chinese, English等)
    - **instruct**: 语音指令描述音色特点
    """
    try:
        if model is None:
            raise HTTPException(status_code=500, detail="模型未加载")

        logger.info(f"开始生成音频 - 文本: {text[:50]}..., 语言: {language}")

        # 调用模型生成音频
        wavs, sr = model.generate_voice_design(
            text=text,
            language=language,
            instruct=instruct,
        )

        # 将音频数据转换为WAV格式的字节流
        audio_buffer = io.BytesIO()
        sf.write(audio_buffer, wavs[0], sr, format="WAV")
        audio_buffer.seek(0)

        logger.info("音频生成完成")

        # 返回音频流
        return StreamingResponse(
            audio_buffer,
            media_type="audio/wav",
            headers={"Content-Disposition": "attachment; filename=generated_audio.wav"},
        )

    except Exception as e:
        logger.error(f"音频生成失败: {e}")
        raise HTTPException(status_code=500, detail=f"音频生成失败: {str(e)}")
