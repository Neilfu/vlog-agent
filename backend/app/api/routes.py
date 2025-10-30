"""
API路由配置
API Routes Configuration

定义所有API端点的路由配置
Defines all API endpoint route configurations
"""

from fastapi import APIRouter
from loguru import logger
from app.api.endpoints import (
    auth_router, projects_router, ai_router,
    assets_router, users_router, services_router, permissions_router,
    strapi_integration_router
)

# 创建主API路由器
api_router = APIRouter()

# 认证相关路由
api_router.include_router(
    auth_router,
    prefix="/auth",
    tags=["认证"]
)

# 项目管理相关路由
api_router.include_router(
    projects_router,
    prefix="/projects",
    tags=["项目管理"]
)

# AI内容生成相关路由
api_router.include_router(
    ai_router,
    prefix="/ai",
    tags=["AI内容生成"]
)

# 媒体资源相关路由
api_router.include_router(
    assets_router,
    prefix="/assets",
    tags=["媒体资源"]
)

# 用户管理相关路由
api_router.include_router(
    users_router,
    prefix="/users",
    tags=["用户管理"]
)

# AI服务管理相关路由
api_router.include_router(
    services_router,
    prefix="/services",
    tags=["AI服务管理"]
)

# 权限管理相关路由
api_router.include_router(
    permissions_router,
    prefix="/permissions",
    tags=["权限管理"]
)

# Strapi集成相关路由
api_router.include_router(
    strapi_integration_router,
    prefix="/strapi",
    tags=["Strapi集成"]
)

logger.info("✅ API路由配置完成 - 包含认证、项目管理、AI生成、媒体资源、用户管理、AI服务管理、权限管理、Strapi集成")