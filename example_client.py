#!/usr/bin/env python3
"""
音色设计API客户端使用示例

展示如何使用VoiceDesignClient进行音频生成
"""

import logging
from client import VoiceDesignClient, quick_generate


def basic_example():
    """基础使用示例"""
    print("🎵 基础使用示例")
    print("-" * 40)

    # 创建客户端
    client = VoiceDesignClient(host="localhost", port=8867)

    try:
        # 检查服务器状态
        status = client.check_server_status()
        print(f"服务器状态: {status}")

        # 生成单个音频
        audio_file = client.generate_audio(
            text="你好，欢迎使用音色设计API！",
            language="Chinese",
            instruct="温柔的女声，语速适中",
            output_file="example_basic.wav",
        )
        print(f"生成音频: {audio_file}")

    except Exception as e:
        print(f"错误: {e}")


def advanced_example():
    """高级使用示例"""
    print("\n🎵 高级使用示例")
    print("-" * 40)

    client = VoiceDesignClient()

    # 批量生成音频
    batch_tasks = [
        {
            "text": "哥哥，你回来啦，人家等了你好久好久了，要抱抱！",
            "language": "Chinese",
            "instruct": "体现撒娇稚嫩的萝莉女声，音调偏高且起伏明显，营造出黏人、做作又刻意卖萌的听觉效果",
            "filename": "cute_girl.wav",
        },
        {
            "text": "我是专业的AI助手，可以帮助你生成各种音色的语音。",
            "language": "Chinese",
            "instruct": "成熟稳重的女声，语速适中，专业可信",
            "filename": "professional_female.wav",
        },
        {
            "text": "Hello! This is an English voice synthesis example.",
            "language": "English",
            "instruct": "Clear and professional male voice",
            "filename": "english_male.wav",
        },
        {
            "text": "哇，这里好漂亮啊！我们去那边看看吧！",
            "language": "Chinese",
            "instruct": "活泼开朗的少女声，充满活力和好奇心",
            "filename": "cheerful_girl.wav",
        },
    ]

    try:
        results = client.batch_generate(
            texts_and_settings=batch_tasks,
            output_dir="examples_output",
            delay=0.5,  # 每次请求间隔0.5秒
        )

        print("批量生成结果:")
        for text_preview, result in results.items():
            if result.startswith("ERROR:"):
                print(f"❌ {text_preview}: {result}")
            else:
                print(f"✅ {text_preview}: {result}")

    except Exception as e:
        print(f"批量生成错误: {e}")


def quick_example():
    """快速生成示例"""
    print("\n🎵 快速生成示例")
    print("-" * 40)

    try:
        # 使用便捷函数
        audio_file = quick_generate(
            text="这是一个快速生成的音频示例。",
            instruct="清脆悦耳的女声",
            output_file="quick_example.wav",
        )
        print(f"快速生成成功: {audio_file}")

    except Exception as e:
        print(f"快速生成错误: {e}")


def command_line_example():
    """命令行使用示例"""
    print("\n🎵 命令行使用示例")
    print("-" * 40)
    print("运行以下命令:")
    print()
    print("# 生成基础音频")
    print('python client.py "你好世界" -o hello.wav')
    print()
    print("# 指定音色指令")
    print('python client.py "今天天气真好" -i "活泼开朗的女声" -o weather.wav')
    print()
    print("# 英文音频")
    print(
        'python client.py "Hello world" -l English -i "Professional male voice" -o english.wav'
    )
    print()
    print("# 列出音频文件")
    print("python client.py --list-audio .")
    print()


def error_handling_example():
    """错误处理示例"""
    print("\n🎵 错误处理示例")
    print("-" * 40)

    # 测试连接失败的情况
    try:
        client = VoiceDesignClient(host="nonexistent-server", port=9999, timeout=5)
        client.generate_audio("测试文本")
    except Exception as e:
        print(f"预期的连接错误: {type(e).__name__}: {e}")

    # 测试服务器错误的情况
    try:
        client = VoiceDesignClient()
        client.generate_audio("")  # 空文本
    except ValueError as e:
        print(f"预期的参数错误: {e}")


def main():
    """主函数"""
    # 设置日志
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    print("🎤 音色设计API客户端使用示例")
    print("=" * 50)

    # 检查服务器是否运行
    try:
        client = VoiceDesignClient()
        client.check_server_status()
        print("✅ 服务器运行正常，开始示例...")
    except Exception as e:
        print(f"⚠️ 服务器未运行，请先启动服务器: {e}")
        print("运行: python server.py")
        return

    # 运行各种示例
    basic_example()
    advanced_example()
    quick_example()
    command_line_example()
    error_handling_example()

    print("\n🎉 所有示例完成！")
    print("生成的文件保存在当前目录和 examples_output/ 目录中")


if __name__ == "__main__":
    main()
