#!/usr/bin/env python3
"""
音色设计API测试脚本

测试功能：
1. 服务器启动测试
2. API端点访问测试
3. 音频生成功能测试
4. 音频文件验证测试
"""

import time
import requests
import subprocess
import threading
import os
import sys
from pathlib import Path


class APITester:
    def __init__(self, host="localhost", port=8867):
        self.base_url = f"http://{host}:{port}"
        self.server_process = None
        self.server_thread = None

    def start_server(self):
        """启动服务器"""
        print("🚀 启动音色设计API服务器...")

        def run_server():
            try:
                self.server_process = subprocess.Popen(
                    [sys.executable, "server.py"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )
                print("✅ 服务器进程已启动")
                self.server_process.wait()
            except Exception as e:
                print(f"❌ 服务器启动失败: {e}")

        self.server_thread = threading.Thread(target=run_server, daemon=True)
        self.server_thread.start()

        # 等待服务器启动
        print("⏳ 等待服务器启动...")
        time.sleep(15)  # 等待模型加载

    def stop_server(self):
        """停止服务器"""
        if self.server_process:
            print("🛑 停止服务器...")
            self.server_process.terminate()
            try:
                self.server_process.wait(timeout=10)
                print("✅ 服务器已停止")
            except subprocess.TimeoutExpired:
                self.server_process.kill()
                print("⚠️ 服务器强制停止")

    def test_root_endpoint(self):
        """测试根路径"""
        print("📡 测试根路径...")
        try:
            response = requests.get(f"{self.base_url}/", timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 根路径测试成功: {data}")
                return True
            else:
                print(f"❌ 根路径测试失败: HTTP {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"❌ 根路径连接失败: {e}")
            return False

    def test_audio_generation(self, text, language="Chinese", instruct="温柔的女声"):
        """测试音频生成"""
        print(f"🎵 测试音频生成: {text[:30]}...")

        params = {"text": text, "language": language, "instruct": instruct}

        try:
            response = requests.post(
                f"{self.base_url}/generate_audio",
                params=params,
                timeout=60,  # 音频生成可能需要更长时间
            )

            if response.status_code == 200:
                # 保存音频文件
                filename = f"test_audio_{int(time.time())}.wav"
                with open(filename, "wb") as f:
                    f.write(response.content)

                file_size = os.path.getsize(filename)
                print(f"✅ 音频生成成功: {filename} ({file_size} bytes)")

                # 验证音频文件
                if self.verify_audio_file(filename):
                    print("✅ 音频文件验证通过")
                    return True, filename
                else:
                    print("❌ 音频文件验证失败")
                    return False, filename
            else:
                print(f"❌ 音频生成失败: HTTP {response.status_code}")
                print(f"错误信息: {response.text}")
                return False, None

        except requests.exceptions.RequestException as e:
            print(f"❌ 音频生成连接失败: {e}")
            return False, None

    def verify_audio_file(self, filename):
        """验证音频文件"""
        try:
            import soundfile as sf

            # 尝试读取音频文件
            data, samplerate = sf.read(filename)
            if len(data) > 0 and samplerate > 0:
                print(f"   📊 音频信息: {len(data)} 采样点, {samplerate}Hz 采样率")
                return True
            else:
                return False
        except Exception as e:
            print(f"   ❌ 音频文件读取失败: {e}")
            return False

    def run_tests(self):
        """运行所有测试"""
        print("=" * 50)
        print("🎯 开始音色设计API测试")
        print("=" * 50)

        # 启动服务器
        self.start_server()

        try:
            # 测试根路径
            root_ok = self.test_root_endpoint()

            if not root_ok:
                print("❌ 服务器未正常启动，跳过后续测试")
                return False

            # 测试音频生成
            test_cases = [
                {
                    "text": "你好，欢迎使用音色设计API！",
                    "language": "Chinese",
                    "instruct": "温柔的女声，语速适中",
                },
                {
                    "text": "哥哥，你回来啦，人家等了你好久好久了，要抱抱！",
                    "language": "Chinese",
                    "instruct": "体现撒娇稚嫩的萝莉女声，音调偏高且起伏明显，营造出黏人、做作又刻意卖萌的听觉效果",
                },
                {
                    "text": "Hello world! This is a test of voice design API.",
                    "language": "English",
                    "instruct": "Clear and professional female voice",
                },
            ]

            success_count = 0
            for i, case in enumerate(test_cases, 1):
                print(f"\n--- 测试用例 {i}/{len(test_cases)} ---")
                success, filename = self.test_audio_generation(**case)
                if success:
                    success_count += 1

            print("\n" + "=" * 50)
            print(f"📊 测试结果: {success_count}/{len(test_cases)} 个用例通过")

            if success_count == len(test_cases):
                print("🎉 所有测试通过！API工作正常")
                return True
            else:
                print("⚠️ 部分测试失败，请检查服务器配置")
                return False

        finally:
            # 停止服务器
            self.stop_server()


def main():
    """主函数"""
    # 检查依赖
    import importlib.util

    missing_deps = []
    for module in ["requests", "soundfile"]:
        if importlib.util.find_spec(module) is None:
            missing_deps.append(module)

    if missing_deps:
        print(f"❌ 缺少必要依赖: {', '.join(missing_deps)}")
        print("请运行: pip install requests soundfile")
        return

    # 检查服务器文件
    if not Path("server.py").exists():
        print("❌ 找不到 server.py 文件")
        return

    # 运行测试
    tester = APITester()
    success = tester.run_tests()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
