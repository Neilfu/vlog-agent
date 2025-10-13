"""
API路由配置
API Routes Configuration

定义所有API端点的路由配置
Defines all API endpoint route configurations
"""

from fastapi import APIRouter
from loguru import logger
from app.api.endpoints import auth, projects, ai, assets, users

# 创建主API路由器
api_router = APIRouter()

# 认证相关路由
api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["认证"]
)

# 项目管理相关路由
api_router.include_router(
    projects.router,
    prefix="/projects",
    tags=["项目管理"]
)

# AI内容生成相关路由
api_router.include_router(
    ai.router,
    prefix="/ai",
    tags=["AI内容生成"]
)

# 媒体资源相关路由
api_router.include_router(
    assets.router,
    prefix="/assets",
    tags=["媒体资源"]
)

# 用户管理相关路由
api_router.include_router(
    users.router,
    prefix="/users",
    tags=["用户管理"]
)

logger.info("✅ API路由配置完成 - 包含认证、项目管理、AI生成、媒体资源、用户管理")