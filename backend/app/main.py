"""
中国AI智能短视频创作系统 - 后端主应用
Chinese AI Intelligent Short Video Creation System - Backend Main Application

基于DeepSeek和即梦大模型的智能视频创作系统
Powered by DeepSeek and 即梦大模型 for intelligent video creation
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uvicorn
from loguru import logger

from app.core.config import settings
from app.core.database import init_db
from app.core.database import init_redis
from app.api.routes import api_router
from app.core.exceptions import setup_exception_handlers


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    logger.info("🚀 启动中国AI智能短视频创作系统...")

    # 初始化数据库
    await init_db()
    logger.info("✅ 数据库连接成功")

    # 初始化Redis
    await init_redis()
    logger.info("✅ Redis连接成功")

    # 初始化中国AI服务
    logger.info("🤖 初始化中国AI服务...")
    # 这里将初始化DeepSeek和即梦大模型服务

    yield

    logger.info("🛑 关闭系统服务...")


def create_app() -> FastAPI:
    """创建FastAPI应用实例"""

    app = FastAPI(
        title="中国AI智能短视频创作系统",
        description="基于DeepSeek和即梦大模型的智能视频创作平台",
        version="1.0.0",
        lifespan=lifespan,
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
    )

    # 配置中间件
    setup_middleware(app)

    # 配置异常处理
    setup_exception_handlers(app)

    # 注册路由
    app.include_router(api_router, prefix="/api/v1")

    # 健康检查端点
    @app.get("/health")
    async def health_check():
        return {
            "status": "healthy",
            "message": "中国AI智能短视频创作系统运行正常",
            "version": "1.0.0",
            "features": {
                "deepseek_integration": True,
                "jimeng_integration": True,
                "autogen_orchestration": True,
                "chinese_optimization": True
            }
        }

    return app


def setup_middleware(app: FastAPI) -> None:
    """配置中间件"""

    # CORS配置 - 针对中国环境优化
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
        expose_headers=["X-Total-Count", "X-Page", "X-Limit"]
    )

    # Gzip压缩
    app.add_middleware(GZipMiddleware, minimum_size=1000)

    # 自定义中间件
    @app.middleware("http")
    async def add_process_time_header(request: Request, call_next):
        """添加处理时间头部"""
        import time
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        return response


# 创建应用实例
app = create_app()


if __name__ == "__main__":
    logger.info(f"🚀 启动服务器 - 端口: {settings.PORT}")
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info" if settings.DEBUG else "warning"
    )