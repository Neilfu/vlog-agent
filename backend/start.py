#!/usr/bin/env python3
"""
启动脚本 - 中国AI智能短视频创作系统
Startup Script - Chinese AI Intelligent Short Video Creation System

快速启动开发服务器的脚本，包含完整的错误处理和调试功能
Quick startup script for development server with comprehensive error handling and debugging
"""

import subprocess
import sys
import os
import time
import signal
from pathlib import Path
from typing import Optional
import traceback
import socket

# 颜色定义
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    RESET = '\033[0m'

def print_banner():
    """打印启动横幅"""
    banner = f"""
{Colors.CYAN}
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║    🎬 中国AI智能短视频创作系统 🇨🇳                                    ║
║       Chinese AI Intelligent Short Video Creation System                    ║
║                                                                              ║
║    🤖 基于DeepSeek和即梦大模型的智能视频创作平台                  ║
║       Powered by DeepSeek and 即梦大模型                              ║
║                                                                              ║
║    🚀 启动中... Starting...                                                 ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
{Colors.RESET}
"""
    print(banner)

def check_port_available(port: int) -> bool:
    """检查端口是否可用"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            result = s.connect_ex(('localhost', port))
            return result != 0
    except Exception:
        return True

def wait_for_port(port: int, timeout: int = 30) -> bool:
    """等待端口可用"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        if check_port_available(port):
            return True
        time.sleep(1)
    return False

def check_dependencies() -> bool:
    """检查依赖项"""
    print(f"{Colors.BLUE}🔍 检查系统依赖...{Colors.RESET}")

    try:
        # 检查Python版本
        if sys.version_info < (3, 8):
            print(f"{Colors.RED}❌ Python版本过低，需要3.8+{Colors.RESET}")
            return False
        print(f"{Colors.GREEN}✅ Python版本: {sys.version}{Colors.RESET}")

        # 检查必要模块
        required_modules = [
            'fastapi', 'uvicorn', 'sqlalchemy', 'aiosqlite',
            'httpx', 'pydantic', 'loguru', 'redis', 'alembic'
        ]

        missing_modules = []
        for module in required_modules:
            try:
                __import__(module)
                print(f"{Colors.GREEN}✅ {module}{Colors.RESET}")
            except ImportError:
                missing_modules.append(module)
                print(f"{Colors.RED}❌ {module}{Colors.RESET}")

        if missing_modules:
            print(f"{Colors.RED}❌ 缺少依赖模块: {', '.join(missing_modules)}{Colors.RESET}")
            print(f"{Colors.YELLOW}请运行: pip install -r requirements.txt{Colors.RESET}")
            return False

        return True

    except Exception as e:
        print(f"{Colors.RED}❌ 依赖检查失败: {e}{Colors.RESET}")
        return False

def check_environment() -> bool:
    """检查环境配置"""
    print(f"\n{Colors.BLUE}🔧 检查环境配置...{Colors.RESET}")

    try:
        # 设置Python路径
        sys.path.insert(0, str(Path(__file__).parent))

        # 导入配置
        from app.core.config import settings

        print(f"{Colors.GREEN}✅ 配置文件加载成功{Colors.RESET}")
        print(f"{Colors.CYAN}📋 配置信息:{Colors.RESET}")
        print(f"   应用名称: {settings.APP_NAME}")
        print(f"   版本: {settings.APP_VERSION}")
        print(f"   调试模式: {settings.DEBUG}")
        print(f"   主机: {settings.HOST}")
        print(f"   端口: {settings.PORT}")
        print(f"   数据库: {settings.DATABASE_URL.split(':///')[0] if '://' in settings.DATABASE_URL else 'SQLite'}")
        print(f"   Strapi: {settings.STRAPI_URL}")
        print(f"   Redis: {settings.REDIS_URL}")

        # 检查关键配置
        if not settings.JWT_SECRET_KEY or settings.JWT_SECRET_KEY == "your-secret-key-change-in-production":
            print(f"{Colors.YELLOW}⚠️  JWT_SECRET_KEY使用默认值，建议修改{Colors.RESET}")

        if not settings.DEEPSEEK_API_KEY:
            print(f"{Colors.YELLOW}⚠️  DEEPSEEK_API_KEY未配置{Colors.RESET}")

        if not settings.STRAPI_API_TOKEN:
            print(f"{Colors.YELLOW}⚠️  STRAPI_API_TOKEN未配置{Colors.RESET}")

        return True

    except Exception as e:
        print(f"{Colors.RED}❌ 环境配置检查失败: {e}{Colors.RESET}")
        print(f"{Colors.RED}错误详情: {traceback.format_exc()}{Colors.RESET}")
        return False

def check_database() -> bool:
    """检查数据库连接"""
    print(f"\n{Colors.BLUE}🗄️  检查数据库连接...{Colors.RESET}")

    try:
        # 导入数据库模块
        from app.core.database import init_db, check_db_health
        import asyncio

        async def test_connection():
            try:
                # 初始化数据库
                await init_db()
                # 测试连接
                return await check_db_health()
            except Exception as e:
                print(f"数据库测试失败: {e}")
                return False

        result = asyncio.run(test_connection())

        if result:
            print(f"{Colors.GREEN}✅ 数据库连接成功{Colors.RESET}")
            return True
        else:
            print(f"{Colors.RED}❌ 数据库连接测试失败{Colors.RESET}")
            return False

    except Exception as e:
        print(f"{Colors.RED}❌ 数据库连接失败: {e}{Colors.RESET}")
        print(f"{Colors.YELLOW}提示: 确保数据库已启动且配置正确{Colors.RESET}")
        return False

def check_redis() -> bool:
    """检查Redis连接"""
    print(f"\n{Colors.BLUE}🔄 检查Redis连接...{Colors.RESET}")

    try:
        from app.core.database import init_redis
        import asyncio

        async def test_redis():
            redis_client = await init_redis()
            if redis_client:
                # 测试Redis连接
                await redis_client.ping()
                return True
            return False

        result = asyncio.run(test_redis())

        if result:
            print(f"{Colors.GREEN}✅ Redis连接成功{Colors.RESET}")
            return True
        else:
            print(f"{Colors.YELLOW}⚠️  Redis连接失败，将使用内存缓存{Colors.RESET}")
            return True  # Redis是可选的，不阻止启动

    except Exception as e:
        print(f"{Colors.YELLOW}⚠️  Redis连接失败: {e}{Colors.RESET}")
        print(f"{Colors.YELLOW}将使用内存缓存{Colors.RESET}")
        return True  # Redis是可选的

def check_strapi_connection() -> bool:
    """检查Strapi连接"""
    print(f"\n{Colors.BLUE}🌐 检查Strapi连接...{Colors.RESET}")

    try:
        from app.services.strapi_service import strapi_service
        from app.core.config import settings
        import asyncio

        async def test_strapi():
            try:
                health = await strapi_service.health_check()
                return health.get("status") == "healthy"
            except Exception:
                return False

        result = asyncio.run(test_strapi())

        if result:
            print(f"{Colors.GREEN}✅ Strapi连接成功{Colors.RESET}")
            return True
        else:
            print(f"{Colors.YELLOW}⚠️  Strapi连接失败，CMS功能将不可用{Colors.RESET}")
            print(f"{Colors.YELLOW}确保Strapi服务在 {settings.STRAPI_URL} 运行{Colors.RESET}")
            return True  # Strapi是可选的，不阻止主服务启动

    except Exception as e:
        print(f"{Colors.YELLOW}⚠️  Strapi连接检查失败: {e}{Colors.RESET}")
        return True  # Strapi是可选的

def check_port_and_start_server() -> bool:
    """检查端口并启动服务器"""
    print(f"\n{Colors.BLUE}🚀 准备启动服务器...{Colors.RESET}")

    try:
        from app.core.config import settings

        # 检查端口可用性
        if not check_port_available(settings.PORT):
            print(f"{Colors.RED}❌ 端口 {settings.PORT} 已被占用{Colors.RESET}")
            print(f"{Colors.YELLOW}请检查是否有其他服务在运行，或修改PORT环境变量{Colors.RESET}")
            return False

        print(f"{Colors.GREEN}✅ 端口 {settings.PORT} 可用{Colors.RESET}")

        # 启动服务器
        print(f"\n{Colors.GREEN}🚀 启动Uvicorn服务器...{Colors.RESET}")
        print(f"{Colors.CYAN}📍 API文档: http://localhost:{settings.PORT}/docs{Colors.RESET}")
        print(f"{Colors.CYAN}📊 监控面板: http://localhost:{settings.PORT}/metrics{Colors.RESET}")
        print(f"{Colors.CYAN}🩺 健康检查: http://localhost:{settings.PORT}/health{Colors.RESET}")
        print(f"{Colors.CYAN}🔌 Strapi集成: http://localhost:{settings.PORT}/api/v1/strapi/health{Colors.RESET}")
        print()

        # 构建Uvicorn命令
        cmd = [
            sys.executable, "-m", "uvicorn",
            "app.main:app",
            "--host", str(settings.HOST),
            "--port", str(settings.PORT),
            "--log-level", "info" if settings.DEBUG else "warning"
        ]

        # 开发模式添加重载
        if settings.DEBUG:
            cmd.append("--reload")

        # 设置环境变量
        env = os.environ.copy()
        env["PYTHONPATH"] = str(Path(__file__).parent)

        # 启动服务器
        process = subprocess.Popen(cmd, env=env)

        # 等待服务器启动
        print(f"{Colors.BLUE}⏳ 等待服务器启动...{Colors.RESET}")
        time.sleep(3)

        # 检查进程是否还在运行
        if process.poll() is None:
            print(f"{Colors.GREEN}✅ 服务器启动成功！{Colors.RESET}")
            print(f"\n{Colors.MAGENTA}🎉 中国AI智能短视频创作系统已启动！{Colors.RESET}")
            print(f"{Colors.CYAN}按 Ctrl+C 停止服务器{Colors.RESET}")

            # 等待进程结束
            try:
                process.wait()
            except KeyboardInterrupt:
                print(f"\n{Colors.YELLOW}🛑 收到停止信号，正在关闭服务器...{Colors.RESET}")
                process.terminate()
                process.wait()
                print(f"{Colors.GREEN}✅ 服务器已停止{Colors.RESET}")

            return True
        else:
            print(f"{Colors.RED}❌ 服务器启动失败{Colors.RESET}")
            return False

    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}🛑 用户中断启动{Colors.RESET}")
        return False
    except Exception as e:
        print(f"{Colors.RED}❌ 服务器启动失败: {e}{Colors.RESET}")
        print(f"{Colors.RED}错误详情: {traceback.format_exc()}{Colors.RESET}")
        return False

def main():
    """主函数"""
    print_banner()

    try:
        # 系统检查
        if not check_dependencies():
            print(f"\n{Colors.RED}❌ 依赖检查失败，无法启动服务器{Colors.RESET}")
            sys.exit(1)

        if not check_environment():
            print(f"\n{Colors.RED}❌ 环境配置检查失败，无法启动服务器{Colors.RESET}")
            sys.exit(1)

        if not check_database():
            print(f"\n{Colors.RED}❌ 数据库检查失败，无法启动服务器{Colors.RESET}")
            sys.exit(1)

        # 可选服务检查（不阻止启动）
        check_redis()
        check_strapi_connection()

        # 启动服务器
        if not check_port_and_start_server():
            print(f"\n{Colors.RED}❌ 服务器启动失败{Colors.RESET}")
            sys.exit(1)

    except SystemExit:
        raise
    except Exception as e:
        print(f"\n{Colors.RED}❌ 意外错误: {e}{Colors.RESET}")
        print(f"{Colors.RED}错误详情: {traceback.format_exc()}{Colors.RESET}")
        sys.exit(1)

if __name__ == "__main__":
    main()