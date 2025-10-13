#!/usr/bin/env python3
"""
启动脚本 - 中国AI智能短视频创作系统
Startup Script - Chinese AI Intelligent Short Video Creation System

快速启动开发服务器的脚本
Quick startup script for development server
"""

import subprocess
import sys
import os
from pathlib import Path

def main():
    """主函数"""
    print("🚀 启动中国AI智能短视频创作系统...")
    print("🎯 基于DeepSeek和即梦大模型的智能视频创作平台")
    print("=" * 60)

    # 检查环境文件
    env_file = Path(".env")
    if not env_file.exists():
        print("⚠️  未找到.env文件，将使用默认配置")
        print("   请复制.env.example为.env并配置您的API密钥")
        print()

    # 设置Python路径
    sys.path.insert(0, str(Path(__file__).parent))

    # 启动Uvicorn服务器
    print("🔥 启动Uvicorn开发服务器...")
    print("📍 API文档: http://localhost:8000/docs")
    print("📊 监控面板: http://localhost:8000/metrics")
    print("🩺 健康检查: http://localhost:8000/health")
    print()

    try:
        subprocess.run([
            sys.executable, "-m", "uvicorn",
            "app.main:app",
            "--host", "0.0.0.0",
            "--port", "8000",
            "--reload",
            "--log-level", "info"
        ], check=True)
    except KeyboardInterrupt:
        print("\n🛑 服务器已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()