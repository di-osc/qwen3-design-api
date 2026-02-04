#!/usr/bin/env python3
"""
快速API测试脚本

简单的功能测试，不启动完整服务器
"""

import requests
import time


def test_api_quick(base_url="http://localhost:8867"):
    """快速测试API功能"""
    print("🚀 快速API测试")
    print(f"目标URL: {base_url}")

    # 测试1: 根路径
    print("\n1️⃣ 测试根路径...")
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            print("✅ 根路径正常")
            print(f"   响应: {response.json()}")
        else:
            print(f"❌ 根路径异常: HTTP {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ 连接失败: {e}")
        print("请确保服务器已启动: python server.py")
        return False

    # 测试2: 音频生成
    print("\n2️⃣ 测试音频生成...")
    test_text = "你好，这是一个测试音频。"
    test_instruct = "温柔的女声"

    params = {"text": test_text, "language": "Chinese", "instruct": test_instruct}

    try:
        print(f"   发送请求: {test_text[:20]}...")

        response = requests.post(
            f"{base_url}/generate_audio", params=params, timeout=30
        )

        if response.status_code == 200:
            # 保存文件
            filename = f"quick_test_{int(time.time())}.wav"
            with open(filename, "wb") as f:
                f.write(response.content)

            file_size = len(response.content)
            print(".1f")
            print(f"   保存文件: {filename}")

            # 简单验证
            if file_size > 1000:  # WAV文件最小应该有1KB以上
                print("✅ 音频文件生成成功")
                return True
            else:
                print(f"❌ 音频文件过小: {file_size} bytes")
                return False
        else:
            print(f"❌ 音频生成失败: HTTP {response.status_code}")
            print(f"   错误: {response.text}")
            return False

    except requests.exceptions.Timeout:
        print("❌ 请求超时（可能模型正在加载，请稍后重试）")
        return False
    except requests.exceptions.RequestException as e:
        print(f"❌ 请求失败: {e}")
        return False


def main():
    """主函数"""
    import importlib.util

    # 检查requests依赖
    if importlib.util.find_spec("requests") is None:
        print("❌ 缺少requests依赖，请运行: pip install requests")
        return

    # 运行测试
    success = test_api_quick()

    if success:
        print("\n🎉 快速测试通过！API工作正常")
    else:
        print("\n⚠️ 测试失败，请检查服务器状态")


if __name__ == "__main__":
    main()
