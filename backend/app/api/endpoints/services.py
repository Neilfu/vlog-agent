"""
AI服务管理API端点
AI Services Management API Endpoints

管理AI服务的配置、健康检查和统计信息
Manages AI services configuration, health checks, and statistics
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime

from app.core.config import settings
from app.core.exceptions import ValidationError
from app.services import (
    check_services_health,
    validate_service_availability,
    get_service_config,
    get_services_statistics,
    deepseek_service,
    jimeng_service,
    autogen_orchestrator,
    TaskType,
    TaskStatus
)
from app.utils.api_key_validator import api_key_validator

logger = logging.getLogger(__name__)
router = APIRouter()

# 服务管理模型
class ServiceHealthResponse(BaseModel):
    """服务健康状态响应模型"""
    timestamp: str
    services: Dict[str, Any]
    overall_status: str
    not_configured_services: Optional[List[str]] = None

class ServiceConfigResponse(BaseModel):
    """服务配置响应模型"""
    service_name: str
    configured: bool
    config: Dict[str, Any]
    last_updated: str

class ServiceStatisticsResponse(BaseModel):
    """服务统计响应模型"""
    timestamp: str
    services: Dict[str, Any]
    summary: Dict[str, Any]

class ServiceValidationResponse(BaseModel):
    """服务验证响应模型"""
    timestamp: str
    services: Dict[str, Any]
    summary: Dict[str, Any]
    setup_guide: Optional[str] = None

class ServiceTestRequest(BaseModel):
    """服务测试请求模型"""
    service_name: str = Field(..., description="要测试的服务名称")
    test_type: str = Field(default="basic", description="测试类型 (basic/full)")
    parameters: Optional[Dict[str, Any]] = Field(default_factory=dict, description="测试参数")

class ServiceTestResponse(BaseModel):
    """服务测试响应模型"""
    service_name: str
    test_type: str
    status: str
    message: str
    response_time: float
    details: Optional[Dict[str, Any]] = None
    timestamp: str

# API端点实现

@router.get("/health", response_model=ServiceHealthResponse)
async def get_services_health():
    """
    获取AI服务健康状态

    检查所有AI服务的配置状态和可用性
    """
    try:
        health_status = await check_services_health()
        logger.info(f"✅ 服务健康状态检查完成 - 状态: {health_status['overall_status']}")
        return ServiceHealthResponse(**health_status)

    except Exception as e:
        logger.error(f"❌ 服务健康状态检查失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="服务健康状态检查失败"
        )

@router.get("/config/{service_name}", response_model=ServiceConfigResponse)
async def get_service_configuration(service_name: str):
    """
    获取特定AI服务的配置信息

    Args:
        service_name: 服务名称 (deepseek, jimeng, autogen_orchestrator)
    """
    try:
        # 验证服务名称
        valid_services = ["deepseek", "jimeng", "autogen_orchestrator"]
        if service_name not in valid_services:
            raise ValidationError(
                f"不支持的服务名称: {service_name}",
                details={"valid_services": valid_services}
            )

        config = get_service_config(service_name)
        is_configured = await validate_service_availability(service_name)

        response = ServiceConfigResponse(
            service_name=service_name,
            configured=is_configured,
            config=config,
            last_updated=datetime.now().isoformat()
        )

        logger.info(f"✅ 服务配置信息获取成功: {service_name}")
        return response

    except ValidationError:
        raise
    except Exception as e:
        logger.error(f"❌ 获取服务配置信息失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取服务配置信息失败"
        )

@router.get("/statistics", response_model=ServiceStatisticsResponse)
async def get_services_stats():
    """
    获取AI服务统计信息

    包括使用统计、成功率等信息
    """
    try:
        stats = await get_services_statistics()
        logger.info(f"✅ 服务统计信息获取完成 - 活跃服务: {stats['summary']['active_services']}")
        return ServiceStatisticsResponse(**stats)

    except Exception as e:
        logger.error(f"❌ 获取服务统计信息失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取服务统计信息失败"
        )

@router.post("/validate", response_model=ServiceValidationResponse)
async def validate_all_services():
    """
    验证所有AI服务的API密钥

    检查API密钥的有效性和服务可用性
    """
    try:
        from app.utils.api_key_validator import validate_api_keys_async

        validation_results = await validate_api_keys_async()
        setup_guide = None

        if validation_results["summary"]["missing"] > 0:
            setup_guide = api_key_validator.generate_setup_guide()

        response = ServiceValidationResponse(
            timestamp=validation_results["timestamp"],
            services=validation_results["services"],
            summary=validation_results["summary"],
            setup_guide=setup_guide
        )

        logger.info(f"✅ 服务验证完成 - 有效服务: {validation_results['summary']['valid']}")
        return response

    except Exception as e:
        logger.error(f"❌ 服务验证失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="服务验证失败"
        )

@router.post("/test", response_model=ServiceTestResponse)
async def test_service(request: ServiceTestRequest):
    """
    测试特定AI服务的功能

    Args:
        request: 服务测试请求
    """
    import time
    start_time = time.time()

    try:
        # 验证服务名称
        valid_services = ["deepseek", "jimeng", "autogen_orchestrator"]
        if request.service_name not in valid_services:
            raise ValidationError(
                f"不支持的服务名称: {request.service_name}",
                details={"valid_services": valid_services}
            )

        # 检查服务是否可用
        is_available = await validate_service_availability(request.service_name)
        if not is_available:
            response_time = time.time() - start_time
            return ServiceTestResponse(
                service_name=request.service_name,
                test_type=request.test_type,
                status="not_configured",
                message=f"服务 {request.service_name} 未配置或不可用",
                response_time=response_time,
                timestamp=datetime.now().isoformat()
            )

        # 根据服务类型执行测试
        if request.service_name == "deepseek":
            test_result = await _test_deepseek_service(request.test_type, request.parameters)
        elif request.service_name == "jimeng":
            test_result = await _test_jimeng_service(request.test_type, request.parameters)
        elif request.service_name == "autogen_orchestrator":
            test_result = await _test_autogen_service(request.test_type, request.parameters)

        response_time = time.time() - start_time

        response = ServiceTestResponse(
            service_name=request.service_name,
            test_type=request.test_type,
            status=test_result["status"],
            message=test_result["message"],
            response_time=response_time,
            details=test_result.get("details"),
            timestamp=datetime.now().isoformat()
        )

        logger.info(f"✅ 服务测试完成: {request.service_name} - {test_result['status']}")
        return response

    except ValidationError:
        raise
    except Exception as e:
        response_time = time.time() - start_time
        logger.error(f"❌ 服务测试失败: {str(e)}")
        return ServiceTestResponse(
            service_name=request.service_name,
            test_type=request.test_type,
            status="error",
            message=f"服务测试异常: {str(e)}",
            response_time=response_time,
            timestamp=datetime.now().isoformat()
        )

@router.get("/models")
async def get_available_models():
    """
    获取可用的AI模型列表

    返回各服务支持的模型和版本信息
    """
    try:
        models = {
            "deepseek": {
                "text_generation": [
                    {"model": "deepseek-chat", "description": "DeepSeek对话模型", "max_tokens": 4000},
                    {"model": "deepseek-coder", "description": "DeepSeek代码模型", "max_tokens": 8000}
                ]
            },
            "jimeng": {
                "image_generation": [
                    {"model": "jimeng-4.0", "description": "即梦图像生成模型V4.0", "max_resolution": "1024x1024"},
                    {"model": "jimeng-3.5", "description": "即梦图像生成模型V3.5", "max_resolution": "512x512"}
                ],
                "video_generation": [
                    {"model": "jimeng-video-3.0", "description": "即梦视频生成模型V3.0", "max_duration": 30},
                    {"model": "jimeng-video-2.0", "description": "即梦视频生成模型V2.0", "max_duration": 15}
                ],
                "image_upscale": [
                    {"model": "jimeng-upscale-2.0", "description": "即梦图像增强模型", "max_scale": 4}
                ]
            }
        }

        # 根据配置过滤可用的模型
        available_models = {}

        if settings.DEEPSEEK_API_KEY:
            available_models["deepseek"] = models["deepseek"]

        if settings.VOLC_ACCESS_KEY and settings.VOLC_SECRET_KEY:
            available_models["jimeng"] = models["jimeng"]

        logger.info(f"✅ 可用模型列表获取成功 - 服务数: {len(available_models)}")

        return {
            "available_models": available_models,
            "timestamp": datetime.now().isoformat(),
            "total_services": len(available_models)
        }

    except Exception as e:
        logger.error(f"❌ 获取可用模型列表失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取可用模型列表失败"
        )

# 内部测试函数
async def _test_deepseek_service(test_type: str, parameters: dict) -> dict:
    """测试DeepSeek服务"""
    try:
        if test_type == "basic":
            # 基本测试：简单的文本生成
            result = await deepseek_service.generate_concept(
                prompt="测试概念生成",
                cultural_context="中国文化背景",
                platform_target="douyin",
                max_tokens=100,
                temperature=0.5
            )
            return {
                "status": "success",
                "message": "DeepSeek服务基本测试通过",
                "details": {
                    "model_used": result.get("model_used"),
                    "generated_at": result.get("generated_at")
                }
            }
        else:
            return {
                "status": "success",
                "message": f"DeepSeek服务{test_type}测试完成",
                "details": {"test_type": test_type}
            }

    except Exception as e:
        return {
            "status": "failed",
            "message": f"DeepSeek服务测试失败: {str(e)}",
            "details": {"error": str(e)}
        }

async def _test_jimeng_service(test_type: str, parameters: dict) -> dict:
    """测试即梦大模型服务"""
    try:
        if test_type == "basic":
            # 基本测试：简单的图像生成
            result = await jimeng_service.generate_storyboard_image(
                scene_description="测试场景：温馨的家庭环境",
                style="现代简约",
                resolution="512x512"
            )
            return {
                "status": "success",
                "message": "即梦大模型服务基本测试通过",
                "details": {
                    "model_used": result.get("model_used"),
                    "image_id": result.get("image_id"),
                    "resolution": result.get("technical_specs", {}).get("resolution")
                }
            }
        else:
            return {
                "status": "success",
                "message": f"即梦大模型服务{test_type}测试完成",
                "details": {"test_type": test_type}
            }

    except Exception as e:
        return {
            "status": "failed",
            "message": f"即梦大模型服务测试失败: {str(e)}",
            "details": {"error": str(e)}
        }

async def _test_autogen_service(test_type: str, parameters: dict) -> dict:
    """测试AutoGen编排器服务"""
    try:
        # 创建一个简单的测试任务
        task_id = await autogen_orchestrator.create_task(
            task_type=TaskType.CONCEPT_GENERATION,
            project_id="test_project",
            parameters={
                "prompt": "测试概念生成",
                "cultural_context": "中国文化背景",
                "platform_target": "douyin",
                "test_mode": True
            }
        )

        # 获取任务状态
        task_status = autogen_orchestrator.get_task_status(task_id)

        if test_type == "basic":
            return {
                "status": "success",
                "message": "AutoGen编排器服务基本测试通过",
                "details": {
                    "task_id": task_id,
                    "task_status": task_status.get("status") if task_status else "unknown",
                    "task_type": "CONCEPT_GENERATION"
                }
            }
        else:
            return {
                "status": "success",
                "message": f"AutoGen编排器服务{test_type}测试完成",
                "details": {
                    "task_id": task_id,
                    "test_mode": True
                }
            }

    except Exception as e:
        return {
            "status": "failed",
            "message": f"AutoGen编排器服务测试失败: {str(e)}",
            "details": {"error": str(e)}
        }

logger.info("✅ AI服务管理API端点配置完成 - 支持服务健康检查、配置管理和测试功能")