"""
API端点模块
API Endpoints Module

包含所有API端点的路由定义
Contains all API endpoint route definitions
"""

from .auth import router as auth_router
from .projects import router as projects_router
from .ai import router as ai_router
from .assets import router as assets_router
from .users import router as users_router
from .services import router as services_router
from .permissions import router as permissions_router
from .strapi_integration import router as strapi_integration_router

__all__ = [
    "auth_router",
    "projects_router",
    "ai_router",
    "assets_router",
    "users_router",
    "services_router",
    "permissions_router",
    "strapi_integration_router"
]