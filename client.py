#!/usr/bin/env python3
"""
音色设计API客户端

提供简单易用的Python客户端，用于调用音色设计API服务。
"""

import requests
import time
from pathlib import Path
from typing import Optional, Dict, Any
import logging


class VoiceDesignClient:
    """音色设计API客户端"""

    def __init__(
        self,
        host: str = "localhost",
        port: int = 8867,
        timeout: int = 60,
        verify_ssl: bool = True,
    ):
        """
        初始化客户端

        Args:
            host: 服务器主机地址
            port: 服务器端口
            timeout: 请求超时时间（秒）
            verify_ssl: 是否验证SSL证书
        """
        self.base_url = f"http://{host}:{port}"
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        self.logger = logging.getLogger(__name__)

        # 设置日志
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    def check_server_status(self) -> Dict[str, Any]:
        """
        检查服务器状态

        Returns:
            服务器状态信息

        Raises:
            requests.RequestException: 网络请求错误
            ValueError: 服务器响应格式错误
        """
        try:
            self.logger.info("检查服务器状态...")
            response = requests.get(
                f"{self.base_url}/", timeout=10, verify=self.verify_ssl
            )
            response.raise_for_status()

            data = response.json()
            self.logger.info("✅ 服务器运行正常")
            return data

        except requests.RequestException as e:
            self.logger.error(f"服务器连接失败: {e}")
            raise
        except ValueError as e:
            self.logger.error(f"服务器响应格式错误: {e}")
            raise

    def generate_audio(
        self,
        text: str,
        language: str = "Chinese",
        instruct: str = "温柔的女声",
        output_file: Optional[str] = None,
        auto_timestamp: bool = True,
    ) -> str:
        """
        生成音频

        Args:
            text: 要合成的文本
            language: 文本语言 (Chinese, English等)
            instruct: 语音指令，描述音色特点
            output_file: 输出文件名，如果为None则自动生成
            auto_timestamp: 是否在文件名中添加时间戳

        Returns:
            保存的音频文件路径

        Raises:
            requests.RequestException: 网络请求错误
            ValueError: 参数错误或服务器响应错误
            IOError: 文件保存错误
        """
        # 参数验证
        if not text.strip():
            raise ValueError("文本内容不能为空")

        if not instruct.strip():
            raise ValueError("语音指令不能为空")

        # 生成输出文件名
        if output_file is None:
            timestamp = int(time.time()) if auto_timestamp else ""
            safe_text = "".join(
                c for c in text[:20] if c.isalnum() or c in " _-"
            ).strip()
            if safe_text:
                output_file = f"voice_{timestamp}_{safe_text}.wav"
            else:
                output_file = f"voice_{timestamp}.wav"

        # 确保输出目录存在
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # 准备请求参数
        params = {"text": text, "language": language, "instruct": instruct}

        self.logger.info(f"开始生成音频: {text[:50]}...")
        self.logger.info(f"语言: {language}, 指令: {instruct}")
        self.logger.info(f"输出文件: {output_file}")

        start_time = time.time()

        try:
            # 发送请求
            response = requests.post(
                f"{self.base_url}/generate_audio",
                params=params,
                timeout=self.timeout,
                verify=self.verify_ssl,
                stream=True,
            )
            response.raise_for_status()

            # 保存音频文件
            with open(output_file, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

            # 验证文件
            file_size = output_path.stat().st_size
            elapsed_time = time.time() - start_time

            self.logger.info("✅ 音频生成成功")
            self.logger.info(".1f")
            self.logger.info(f"   文件大小: {file_size} bytes")
            self.logger.info(f"   生成用时: {elapsed_time:.1f}秒")

            if file_size < 1000:
                self.logger.warning("⚠️ 生成的文件可能不完整，请检查内容")

            return str(output_file)

        except requests.Timeout:
            self.logger.error(f"请求超时 ({self.timeout}s)")
            raise
        except requests.HTTPError as e:
            if e.response.status_code == 500:
                error_msg = e.response.text
                self.logger.error(f"服务器错误: {error_msg}")
                raise ValueError(f"音频生成失败: {error_msg}") from e
            else:
                self.logger.error(f"HTTP错误: {e}")
                raise
        except requests.RequestException as e:
            self.logger.error(f"网络请求错误: {e}")
            raise
        except IOError as e:
            self.logger.error(f"文件保存错误: {e}")
            raise

    def batch_generate(
        self,
        texts_and_settings: list,
        output_dir: str = "batch_output",
        delay: float = 1.0,
    ) -> Dict[str, str]:
        """
        批量生成音频

        Args:
            texts_and_settings: 文本和设置的列表
                格式: [{"text": "文本", "language": "Chinese", "instruct": "指令"}, ...]
            output_dir: 输出目录
            delay: 每次请求间的延迟（秒）

        Returns:
            文件名到文件路径的映射字典
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        results = {}

        self.logger.info(f"开始批量生成，共 {len(texts_and_settings)} 个任务")
        self.logger.info(f"输出目录: {output_dir}")

        for i, item in enumerate(texts_and_settings, 1):
            self.logger.info(f"处理任务 {i}/{len(texts_and_settings)}")

            # 提取参数
            text = item.get("text", "")
            language = item.get("language", "Chinese")
            instruct = item.get("instruct", "温柔的女声")
            custom_filename = item.get("filename")

            try:
                # 生成音频
                output_file = str(output_path / custom_filename) if custom_filename else None
                file_path = self.generate_audio(
                    text=text,
                    language=language,
                    instruct=instruct,
                    output_file=output_file,
                    auto_timestamp=True,
                )

                results[text[:30] + "..."] = file_path
                self.logger.info(f"✅ 任务 {i} 完成")

            except Exception as e:
                self.logger.error(f"❌ 任务 {i} 失败: {e}")
                results[text[:30] + "..."] = f"ERROR: {e}"

            # 请求间延迟
            if i < len(texts_and_settings) and delay > 0:
                self.logger.info(".1f")
                time.sleep(delay)

        success_count = sum(
            1 for v in results.values() if not str(v).startswith("ERROR:")
        )
        self.logger.info(
            f"批量生成完成: {success_count}/{len(texts_and_settings)} 成功"
        )

        return results

    def list_audio_files(self, directory: str = ".") -> list:
        """
        列出目录中的音频文件

        Args:
            directory: 要扫描的目录

        Returns:
            音频文件列表
        """
        audio_extensions = {".wav", ".mp3", ".flac", ".ogg", ".m4a"}
        audio_files = []

        for file_path in Path(directory).glob("*"):
            if file_path.is_file() and file_path.suffix.lower() in audio_extensions:
                audio_files.append(str(file_path))

        return sorted(audio_files)


# 便捷函数
def quick_generate(
    text: str,
    instruct: str = "温柔的女声",
    output_file: Optional[str] = None,
    host: str = "localhost",
    port: int = 8867,
) -> str:
    """
    快速生成音频的便捷函数

    Args:
        text: 要合成的文本
        instruct: 语音指令
        output_file: 输出文件路径
        host: 服务器地址
        port: 服务器端口

    Returns:
        生成的音频文件路径
    """
    client = VoiceDesignClient(host=host, port=port)
    return client.generate_audio(text, instruct=instruct, output_file=output_file)


def main():
    """主函数 - 示例用法"""
    import argparse

    parser = argparse.ArgumentParser(description="音色设计API客户端")
    parser.add_argument("text", help="要合成的文本")
    parser.add_argument(
        "-i", "--instruct", default="温柔的女声", help="语音指令 (默认: 温柔的女声)"
    )
    parser.add_argument(
        "-l", "--language", default="Chinese", help="语言 (默认: Chinese)"
    )
    parser.add_argument("-o", "--output", help="输出文件路径")
    parser.add_argument("--host", default="localhost", help="服务器地址")
    parser.add_argument("--port", type=int, default=8867, help="服务器端口")
    parser.add_argument("--list-audio", metavar="DIR", help="列出目录中的音频文件")

    args = parser.parse_args()

    # 设置日志
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    client = VoiceDesignClient(host=args.host, port=args.port)

    try:
        if args.list_audio:
            # 列出音频文件
            audio_files = client.list_audio_files(args.list_audio)
            print(f"📁 {args.list_audio} 中的音频文件:")
            for audio_file in audio_files:
                print(f"  🎵 {audio_file}")
        else:
            # 生成音频
            output_file = client.generate_audio(
                text=args.text,
                language=args.language,
                instruct=args.instruct,
                output_file=args.output,
            )
            print(f"✅ 音频生成成功: {output_file}")

    except Exception as e:
        print(f"❌ 错误: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
