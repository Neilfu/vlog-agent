"""
AI服务模块初始化
AI Services Module Initialization

集成DeepSeek和即梦大模型服务
Integrates DeepSeek and Jimeng large model services
"""

from datetime import datetime
from typing import Dict, Any

from .deepseek_service import deepseek_service, DeepSeekService
from .jimeng_service import jimeng_service, JimengService
from .autogen_orchestrator import autogen_orchestrator, TaskType, TaskStatus
from .file_storage import FileStorageService, file_storage_service, get_file_storage_service
from .permissions import permission_service, PermissionService, get_permission_service, init_permissions_system
from .strapi_service import strapi_service, StrapiService, get_strapi_service

__all__ = [
    # DeepSeek服务
    "deepseek_service",
    "DeepSeekService",
    # 即梦大模型服务
    "jimeng_service",
    "JimengService",
    # AutoGen编排器
    "autogen_orchestrator",
    "TaskType",
    "TaskStatus",
    # 文件存储服务
    "file_storage_service",
    "FileStorageService",
    "get_file_storage_service",
    # 权限服务
    "permission_service",
    "PermissionService",
    "get_permission_service",
    "init_permissions_system",
    # Strapi服务
    "strapi_service",
    "StrapiService",
    "get_strapi_service"
]

# 服务健康检查
async def check_services_health() -> Dict[str, Any]:
    """
    检查所有AI服务的健康状态
    Check health status of all AI services

    Returns:
        Dict containing health status of all services
    """
    from app.core.config import settings

    health_status = {
        "timestamp": datetime.now().isoformat(),
        "services": {
            "deepseek": {
                "status": "healthy" if settings.DEEPSEEK_API_KEY else "not_configured",
                "model": settings.DEEPSEEK_MODEL,
                "base_url": settings.DEEPSEEK_BASE_URL
            },
            "jimeng": {
                "status": "healthy" if (settings.VOLC_ACCESS_KEY and settings.VOLC_SECRET_KEY) else "not_configured",
                "region": settings.VOLC_REGION,
                "base_url": settings.JIMENG_BASE_URL
            },
            "autogen_orchestrator": {
                "status": "healthy",
                "description": "AI任务编排服务"
            }
        },
        "overall_status": "healthy"
    }

    # 检查是否有任何服务未配置
    not_configured = [
        service for service, info in health_status["services"].items()
        if info["status"] == "not_configured"
    ]

    if not_configured:
        health_status["overall_status"] = "partial"
        health_status["not_configured_services"] = not_configured

    return health_status

# 服务可用性检查
async def validate_service_availability(service_name: str) -> bool:
    """
    验证特定AI服务是否可用
    Validate if a specific AI service is available

    Args:
        service_name: 服务名称 (deepseek, jimeng, autogen_orchestrator)

    Returns:
        True if service is available, False otherwise
    """
    from app.core.config import settings

    availability_checks = {
        "deepseek": lambda: bool(settings.DEEPSEEK_API_KEY),
        "jimeng": lambda: bool(settings.VOLC_ACCESS_KEY and settings.VOLC_SECRET_KEY),
        "autogen_orchestrator": lambda: True  # 总是可用，因为它不依赖外部API
    }

    check_func = availability_checks.get(service_name)
    if check_func:
        return check_func()

    return False

# 获取服务配置信息
def get_service_config(service_name: str) -> dict:
    """
    获取AI服务的配置信息
    Get configuration information for an AI service

    Args:
        service_name: 服务名称

    Returns:
        服务配置信息字典
    """
    from app.core.config import settings

    configs = {
        "deepseek": {
            "api_key_configured": bool(settings.DEEPSEEK_API_KEY),
            "model": settings.DEEPSEEK_MODEL,
            "base_url": settings.DEEPSEEK_BASE_URL,
            "max_tokens": settings.DEEPSEEK_MAX_TOKENS,
            "temperature": settings.DEEPSEEK_TEMPERATURE
        },
        "jimeng": {
            "api_keys_configured": bool(settings.VOLC_ACCESS_KEY and settings.VOLC_SECRET_KEY),
            "region": settings.VOLC_REGION,
            "base_url": settings.JIMENG_BASE_URL,
            "access_key": "已配置" if settings.VOLC_ACCESS_KEY else "未配置",
            "secret_key": "已配置" if settings.VOLC_SECRET_KEY else "未配置"
        },
        "autogen_orchestrator": {
            "model": settings.AUTOGEN_MODEL,
            "temperature": settings.AUTOGEN_TEMPERATURE,
            "status": "active"
        }
    }

    return configs.get(service_name, {})

# 服务统计信息
async def get_services_statistics() -> Dict[str, Any]:
    """
    获取AI服务使用统计
    Get AI services usage statistics

    Returns:
        服务统计信息字典
    """
    from datetime import datetime

    stats = {
        "timestamp": datetime.now().isoformat(),
        "services": {
            "deepseek": {
                "total_requests": 0,  # 可以从数据库或缓存获取实际数据
                "successful_requests": 0,
                "failed_requests": 0,
                "average_response_time": 0.0,
                "last_used": None
            },
            "jimeng": {
                "total_requests": 0,
                "successful_requests": 0,
                "failed_requests": 0,
                "average_response_time": 0.0,
                "last_used": None
            },
            "autogen_orchestrator": {
                "total_tasks": 0,
                "completed_tasks": 0,
                "failed_tasks": 0,
                "pending_tasks": 0,
                "last_task": None
            }
        },
        "summary": {
            "total_services": 3,
            "active_services": 0,
            "total_requests": 0,
            "overall_success_rate": 0.0
        }
    }

    # 计算活跃服务数
    from app.core.config import settings
    if settings.DEEPSEEK_API_KEY:
        stats["summary"]["active_services"] += 1
        stats["services"]["deepseek"]["status"] = "active"
    else:
        stats["services"]["deepseek"]["status"] = "inactive"

    if settings.VOLC_ACCESS_KEY and settings.VOLC_SECRET_KEY:
        stats["summary"]["active_services"] += 1
        stats["services"]["jimeng"]["status"] = "active"
    else:
        stats["services"]["jimeng"]["status"] = "inactive"

    stats["services"]["autogen_orchestrator"]["status"] = "active"
    stats["summary"]["active_services"] += 1

    return stats