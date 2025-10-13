"""
AI内容生成API端点
AI Content Generation API Endpoints

集成DeepSeek和即梦大模型进行内容创作
Integrates DeepSeek and 即梦大模型 for content creation
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import uuid4

from app.services.deepseek_service import deepseek_service
from app.services.jimeng_service import jimeng_service
from app.services.autogen_orchestrator import (
    autogen_orchestrator, TaskType, TaskStatus
)

logger = logging.getLogger(__name__)
router = APIRouter()

# AI生成请求模型
class GenerateConceptRequest(BaseModel):
    project_id: str
    prompt: str = Field(..., description="生成提示词 (中文)", example="为母婴护肤品牌创作温馨的广告创意")
    cultural_context: str = Field(..., description="文化背景 (中文)", example="中国年轻妈妈注重宝宝健康和安全")
    platform_target: str = Field(..., description="目标平台", example="douyin")
    ai_model: str = Field(default="deepseek-chat", description="AI模型选择")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="生成温度")
    max_tokens: int = Field(default=1000, ge=100, le=4000, description="最大token数")

class GenerateScriptRequest(BaseModel):
    project_id: str
    concept_id: str
    tone: str = Field(default="casual", description="语调风格")
    target_age_group: str = Field(..., description="目标年龄群体 (中文)", example="25-35岁年轻妈妈")
    cultural_references: List[str] = Field(default_factory=list, description="文化引用 (中文)")
    ai_model: str = Field(default="deepseek-chat", description="AI模型选择")

class GenerateStoryboardRequest(BaseModel):
    project_id: str
    script_scene_ids: List[str] = Field(..., description="关联的剧本场景ID列表")
    resolution: str = Field(default="1024x1024", description="图像分辨率")
    style: str = Field(..., description="视觉风格 (中文)", example="现代简约，温馨家庭风格")
    color_palette: List[str] = Field(default_factory=list, description="色彩调色板")
    ai_model: str = Field(default="jimeng-4.0", description="即梦大模型版本")

class GenerateVideoRequest(BaseModel):
    project_id: str
    storyboard_ids: List[str] = Field(..., description="关联的分镜ID列表")
    duration: int = Field(default=6, ge=5, le=30, description="视频时长 (秒)")
    resolution: str = Field(default="1080p", description="视频分辨率")
    frame_rate: int = Field(default=24, description="帧率")
    ai_model: str = Field(default="jimeng-video-3.0", description="即梦视频模型")

@router.post("/generate/concept")
async def generate_concept(request: GenerateConceptRequest):
    """生成创意概念 - 使用DeepSeek"""
    try:
        # 使用AutoGen编排器创建任务
        task_id = await autogen_orchestrator.create_task(
            task_type=TaskType.CONCEPT_GENERATION,
            project_id=request.project_id,
            parameters={
                "prompt": request.prompt,
                "cultural_context": request.cultural_context,
                "platform_target": request.platform_target,
                "temperature": request.temperature,
                "max_tokens": request.max_tokens
            }
        )

        logger.info(f"🚀 创意概念生成任务已创建 - TaskID: {task_id}")

        return {
            "message": "创意概念生成任务已启动",
            "task_id": task_id,
            "status": "pending",
            "project_id": request.project_id
        }

    except Exception as e:
        logger.error(f"❌ 创意概念生成任务创建失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创意概念生成任务创建失败: {str(e)}"
        )

@router.post("/generate/script")
async def generate_script(request: GenerateScriptRequest):
    """生成剧本 - 使用DeepSeek"""
    try:
        # 使用AutoGen编排器创建任务
        task_id = await autogen_orchestrator.create_task(
            task_type=TaskType.SCRIPT_WRITING,
            project_id=request.project_id,
            parameters={
                "concept": request.concept_id,  # 这里应该获取实际的创意概念内容
                "tone": request.tone,
                "target_age_group": request.target_age_group,
                "cultural_references": request.cultural_references,
                "ai_model": request.ai_model
            }
        )

        logger.info(f"🚀 剧本生成任务已创建 - TaskID: {task_id}")

        return {
            "message": "剧本生成任务已启动",
            "task_id": task_id,
            "status": "pending",
            "project_id": request.project_id
        }

    except Exception as e:
        logger.error(f"❌ 剧本生成任务创建失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"剧本生成任务创建失败: {str(e)}"
        )

@router.post("/generate/storyboard")
async def generate_storyboard(request: GenerateStoryboardRequest):
    """生成分镜图像 - 使用即梦大模型"""
    try:
        # 使用AutoGen编排器创建任务
        task_id = await autogen_orchestrator.create_task(
            task_type=TaskType.STORYBOARD_CREATION,
            project_id=request.project_id,
            parameters={
                "script_scene_ids": request.script_scene_ids,
                "resolution": request.resolution,
                "style": request.style,
                "color_palette": request.color_palette,
                "ai_model": request.ai_model
            }
        )

        logger.info(f"🚀 分镜图像生成任务已创建 - TaskID: {task_id}")

        return {
            "message": "分镜图像生成任务已启动",
            "task_id": task_id,
            "status": "pending",
            "project_id": request.project_id
        }

    except Exception as e:
        logger.error(f"❌ 分镜图像生成任务创建失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"分镜图像生成任务创建失败: {str(e)}"
        )

@router.post("/generate/video")
async def generate_video(request: GenerateVideoRequest):
    """生成视频 - 使用即梦大模型"""
    try:
        # 使用AutoGen编排器创建任务
        task_id = await autogen_orchestrator.create_task(
            task_type=TaskType.VIDEO_GENERATION,
            project_id=request.project_id,
            parameters={
                "storyboard_ids": request.storyboard_ids,
                "duration": request.duration,
                "resolution": request.resolution,
                "frame_rate": request.frame_rate,
                "ai_model": request.ai_model
            }
        )

        logger.info(f"🚀 视频生成任务已创建 - TaskID: {task_id}")

        return {
            "message": "视频生成任务已启动",
            "task_id": task_id,
            "status": "pending",
            "project_id": request.project_id
        }

    except Exception as e:
        logger.error(f"❌ 视频生成任务创建失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"视频生成任务创建失败: {str(e)}"
        )

@router.get("/tasks/{task_id}/status")
async def get_generation_status(task_id: str):
    """获取AI生成任务状态"""
    try:
        # 从AutoGen编排器获取任务状态
        task_status = autogen_orchestrator.get_task_status(task_id)

        if not task_status:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"未找到任务: {task_id}"
            )

        return task_status

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 获取任务状态失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取任务状态失败: {str(e)}"
        )

@router.get("/tasks")
async def get_all_tasks():
    """获取所有AI生成任务"""
    try:
        # 获取所有活跃任务
        tasks = autogen_orchestrator.get_active_tasks()

        return {
            "tasks": tasks,
            "total_count": len(tasks)
        }

    except Exception as e:
        logger.error(f"❌ 获取任务列表失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取任务列表失败: {str(e)}"
        )

@router.delete("/tasks/{task_id}")
async def cancel_task(task_id: str):
    """取消AI生成任务"""
    try:
        # 尝试取消任务
        success = await autogen_orchestrator.cancel_task(task_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"无法取消任务: {task_id}"
            )

        return {
            "message": "任务已取消",
            "task_id": task_id,
            "status": "cancelled"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 取消任务失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"取消任务失败: {str(e)}"
        )

logger.info("✅ AI内容生成API端点配置完成 - 集成DeepSeek和即梦大模型")