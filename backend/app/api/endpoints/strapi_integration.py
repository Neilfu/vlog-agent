"""
Strapi集成API端点
Strapi Integration API Endpoints

处理与Strapi CMS的集成功能，包括内容同步、webhook处理等
Handles integration functionality with Strapi CMS, including content sync, webhook handling, etc.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status, Query, Path, Header
from pydantic import BaseModel, Field, validator
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db, Project, User
from app.core.security import get_current_user
from app.core.exceptions import ValidationError, NotFoundError, ExternalServiceError
from app.core.config import settings
from app.models import User as UserModel
from app.services.strapi_service import strapi_service, StrapiService, get_strapi_service
from app.core.strapi_config import get_strapi_config, validate_strapi_connection

logger = logging.getLogger(__name__)
router = APIRouter()

# 请求模型定义
class StrapiProjectCreateRequest(BaseModel):
    """Strapi项目创建请求模型"""
    title: str = Field(..., min_length=1, max_length=200, description="项目标题")
    description: Optional[str] = Field(None, max_length=2000, description="项目描述")
    project_type: str = Field(default="promotional", description="项目类型")
    priority: str = Field(default="medium", description="优先级")
    deadline: Optional[datetime] = Field(None, description="截止日期")
    business_input: Dict[str, Any] = Field(..., description="业务输入数据")
    technical_specs: Dict[str, Any] = Field(default_factory=dict, description="技术规格")
    creator_id: str = Field(..., description="创建者ID")
    organization_id: Optional[str] = Field(None, description="组织ID")

    @validator('project_type')
    def validate_project_type(cls, v):
        valid_types = ["promotional", "educational", "entertainment", "corporate", "social_media", "advertisement"]
        if v not in valid_types:
            raise ValueError(f'项目类型必须是以下之一: {", ".join(valid_types)}')
        return v

    @validator('priority')
    def validate_priority(cls, v):
        valid_priorities = ["low", "medium", "high", "urgent"]
        if v not in valid_priorities:
            raise ValueError(f'优先级必须是以下之一: {", ".join(valid_priorities)}')
        return v


class StrapiProjectUpdateRequest(BaseModel):
    """Strapi项目更新请求模型"""
    title: Optional[str] = Field(None, min_length=1, max_length=200, description="项目标题")
    description: Optional[str] = Field(None, max_length=2000, description="项目描述")
    status: Optional[str] = Field(None, description="项目状态")
    project_type: Optional[str] = Field(None, description="项目类型")
    priority: Optional[str] = Field(None, description="优先级")
    deadline: Optional[datetime] = Field(None, description="截止日期")
    business_input: Optional[Dict[str, Any]] = Field(None, description="业务输入数据")
    technical_specs: Optional[Dict[str, Any]] = Field(None, description="技术规格")
    progress: Optional[Dict[str, Any]] = Field(None, description="进度信息")
    project_metadata: Optional[Dict[str, Any]] = Field(None, description="项目元数据")

    @validator('status')
    def validate_status(cls, v):
        if v is None:
            return v
        valid_statuses = ["draft", "concept", "scripting", "storyboard", "production", "post_production", "review", "published", "archived"]
        if v not in valid_statuses:
            raise ValueError(f'项目状态必须是以下之一: {", ".join(valid_statuses)}')
        return v


class StrapiCreativeIdeaRequest(BaseModel):
    """Strapi创意想法请求模型"""
    title: str = Field(..., min_length=1, max_length=200, description="创意标题")
    description: Optional[str] = Field(None, description="创意描述")
    content: Dict[str, Any] = Field(..., description="创意内容")
    prompt: Optional[str] = Field(None, description="AI生成提示词")
    ai_model: str = Field(..., description="使用的AI模型")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="AI参数")
    rating: Optional[int] = Field(None, ge=1, le=5, description="评分")
    feedback: Optional[str] = Field(None, description="反馈")
    category: str = Field(default="concept", description="创意分类")
    project_id: str = Field(..., description="关联项目ID")

    @validator('category')
    def validate_category(cls, v):
        valid_categories = ["concept", "storyline", "creative_angle", "marketing_approach", "cultural_element"]
        if v not in valid_categories:
            raise ValueError(f'创意分类必须是以下之一: {", ".join(valid_categories)}')
        return v


class StrapiScriptRequest(BaseModel):
    """Strapi脚本请求模型"""
    title: str = Field(..., min_length=1, max_length=200, description="脚本标题")
    content: str = Field(..., description="脚本内容")
    duration: Optional[int] = Field(None, ge=5, le=300, description="预计时长(秒)")
    word_count: Optional[int] = Field(None, ge=10, description="字数")
    language: str = Field(default="zh-CN", description="语言")
    scenes: List[Dict[str, Any]] = Field(default_factory=list, description="场景列表")
    characters: List[Dict[str, Any]] = Field(default_factory=list, description="角色列表")
    target_audience: Optional[str] = Field(None, description="目标受众")
    key_message: Optional[str] = Field(None, description="核心信息")
    call_to_action: Optional[str] = Field(None, description="行动号召")
    ai_model: Optional[str] = Field(None, description="使用的AI模型")
    prompt: Optional[str] = Field(None, description="AI生成提示词")
    project_id: str = Field(..., description="关联项目ID")

    @validator('language')
    def validate_language(cls, v):
        valid_languages = ["zh-CN", "en-US", "zh-TW"]
        if v not in valid_languages:
            raise ValueError(f'语言必须是以下之一: {", ".join(valid_languages)}')
        return v


class StrapiWebhookPayload(BaseModel):
    """Strapi webhook载荷模型"""
    event: str = Field(..., description="事件类型")
    model: str = Field(..., description="内容模型")
    entry: Dict[str, Any] = Field(..., description="内容条目")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="时间戳")


class StrapiSyncRequest(BaseModel):
    """Strapi同步请求模型"""
    content_type: str = Field(..., description="内容类型")
    direction: str = Field(default="to_strapi", description="同步方向")
    entity_id: Optional[str] = Field(None, description="实体ID")
    force_sync: bool = Field(default=False, description="强制同步")

    @validator('content_type')
    def validate_content_type(cls, v):
        valid_types = ["project", "creative-idea", "script", "storyboard", "media-asset", "final-video"]
        if v not in valid_types:
            raise ValueError(f'内容类型必须是以下之一: {", ".join(valid_types)}')
        return v

    @validator('direction')
    def validate_direction(cls, v):
        valid_directions = ["to_strapi", "from_strapi", "bidirectional"]
        if v not in valid_directions:
            raise ValueError(f'同步方向必须是以下之一: {", ".join(valid_directions)}')
        return v


# API端点实现

@router.get("/health")
async def check_strapi_health(
    current_user: User = Depends(get_current_user),
    strapi_service: StrapiService = Depends(get_strapi_service)
):
    """
    检查Strapi服务健康状态
    """
    try:
        health_status = await strapi_service.health_check()

        logger.info(f"✅ Strapi健康检查完成 - 用户: {current_user.username}")
        return health_status

    except Exception as e:
        logger.error(f"❌ Strapi健康检查失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Strapi服务连接失败"
        )


@router.post("/projects/sync")
async def sync_project_to_strapi(
    sync_request: StrapiSyncRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    strapi_service: StrapiService = Depends(get_strapi_service)
):
    """
    同步项目到Strapi
    """
    try:
        if not sync_request.entity_id:
            raise ValidationError("需要指定实体ID")

        # 获取项目数据
        from sqlalchemy import select
        result = await db.execute(
            select(Project).where(Project.id == sync_request.entity_id)
        )
        project = result.scalar_one_or_none()

        if not project:
            raise NotFoundError("项目", sync_request.entity_id)

        # 检查权限
        if project.creator_id != current_user.id and current_user.role != "admin":
            raise PermissionDeniedError("您没有权限同步此项目")

        # 转换数据格式
        project_data = {
            "title": project.title,
            "slug": project.slug,
            "description": project.description,
            "status": project.status.value if hasattr(project.status, 'value') else str(project.status),
            "projectType": project.project_type,
            "priority": project.priority,
            "deadline": project.deadline.isoformat() if project.deadline else None,
            "businessInput": project.business_input,
            "technicalSpecs": project.technical_specs,
            "progress": project.progress,
            "projectMetadata": project.project_metadata,
            "creatorId": project.creator_id,
            "organizationId": project.organization_id,
            "workflowId": project.workflow_id
        }

        # 同步到Strapi
        strapi_id = await strapi_service.sync_project_to_strapi(project_data)

        # 更新项目的Strapi ID
        project.strapi_id = strapi_id
        project.updated_at = datetime.utcnow()
        await db.commit()

        logger.info(f"✅ 项目同步到Strapi成功: {project.title} -> {strapi_id} - 用户: {current_user.username}")

        return {
            "message": "项目同步到Strapi成功",
            "project_id": project.id,
            "strapi_id": strapi_id,
            "synced_at": datetime.utcnow().isoformat()
        }

    except (NotFoundError, ValidationError, PermissionDeniedError):
        raise
    except Exception as e:
        logger.error(f"❌ 项目同步到Strapi失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="项目同步到Strapi失败"
        )


@router.get("/projects/{project_id}")
async def get_project_from_strapi(
    project_id: str = Path(..., description="Strapi项目ID"),
    populate: Optional[str] = Query(None, description="关联数据"),
    current_user: User = Depends(get_current_user),
    strapi_service: StrapiService = Depends(get_strapi_service)
):
    """
    从Strapi获取项目详情
    """
    try:
        # 添加查询参数
        params = {}
        if populate:
            params["populate"] = populate

        project_data = await strapi_service.get_project(project_id)

        logger.info(f"✅ 从Strapi获取项目成功: {project_id} - 用户: {current_user.username}")

        return project_data

    except Exception as e:
        logger.error(f"❌ 从Strapi获取项目失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="从Strapi获取项目失败"
        )


@router.put("/projects/{project_id}")
async def update_project_in_strapi(
    project_id: str,
    update_data: StrapiProjectUpdateRequest,
    current_user: User = Depends(get_current_user),
    strapi_service: StrapiService = Depends(get_strapi_service)
):
    """
    在Strapi中更新项目
    """
    try:
        # 转换数据格式
        strapi_update_data = update_data.dict(exclude_unset=True)

        # 更新Strapi中的项目
        updated_project = await strapi_service.update_project(project_id, strapi_update_data)

        logger.info(f"✅ Strapi项目更新成功: {project_id} - 用户: {current_user.username}")

        return updated_project

    except Exception as e:
        logger.error(f"❌ Strapi项目更新失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Strapi项目更新失败"
        )


@router.post("/creative-ideas")
async def create_creative_idea_in_strapi(
    idea_data: StrapiCreativeIdeaRequest,
    current_user: User = Depends(get_current_user),
    strapi_service: StrapiService = Depends(get_strapi_service)
):
    """
    在Strapi中创建创意想法
    """
    try:
        # 转换数据格式
        strapi_data = {
            "title": idea_data.title,
            "description": idea_data.description,
            "content": idea_data.content,
            "prompt": idea_data.prompt,
            "aiModel": idea_data.ai_model,
            "parameters": idea_data.parameters,
            "rating": idea_data.rating,
            "feedback": idea_data.feedback,
            "category": idea_data.category,
            "status": "active",
            "isSelected": False,
            "project": idea_data.project_id,
            "locale": "zh-CN"
        }

        # 创建创意想法
        creative_idea = await strapi_service.create_creative_idea(strapi_data)

        logger.info(f"✅ Strapi创意想法创建成功: {idea_data.title} - 用户: {current_user.username}")

        return creative_idea

    except Exception as e:
        logger.error(f"❌ Strapi创意想法创建失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Strapi创意想法创建失败"
        )


@router.get("/creative-ideas/project/{project_id}")
async def get_creative_ideas_by_project(
    project_id: str,
    current_user: User = Depends(get_current_user),
    strapi_service: StrapiService = Depends(get_strapi_service)
):
    """
    获取项目的创意想法列表
    """
    try:
        creative_ideas = await strapi_service.get_creative_ideas_by_project(project_id)

        logger.info(f"✅ 获取项目创意想法成功: {len(creative_ideas)} 个想法 - 用户: {current_user.username}")

        return {
            "creative_ideas": creative_ideas,
            "total": len(creative_ideas),
            "project_id": project_id
        }

    except Exception as e:
        logger.error(f"❌ 获取项目创意想法失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取项目创意想法失败"
        )


@router.post("/scripts")
async def create_script_in_strapi(
    script_data: StrapiScriptRequest,
    current_user: User = Depends(get_current_user),
    strapi_service: StrapiService = Depends(get_strapi_service)
):
    """
    在Strapi中创建脚本
    """
    try:
        # 转换数据格式
        strapi_data = {
            "title": script_data.title,
            "content": script_data.content,
            "duration": script_data.duration,
            "wordCount": script_data.word_count,
            "language": script_data.language,
            "scenes": script_data.scenes,
            "characters": script_data.characters,
            "targetAudience": script_data.target_audience,
            "keyMessage": script_data.key_message,
            "callToAction": script_data.call_to_action,
            "aiModel": script_data.ai_model,
            "prompt": script_data.prompt,
            "status": "draft",
            "version": 1,
            "project": script_data.project_id,
            "locale": "zh-CN"
        }

        # 创建脚本
        script = await strapi_service.create_script(strapi_data)

        logger.info(f"✅ Strapi脚本创建成功: {script_data.title} - 用户: {current_user.username}")

        return script

    except Exception as e:
        logger.error(f"❌ Strapi脚本创建失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Strapi脚本创建失败"
        )


@router.post("/webhooks/strapi")
async def handle_strapi_webhook(
    webhook_payload: StrapiWebhookPayload,
    x_strapi_event: Optional[str] = Header(None),
    x_strapi_signature: Optional[str] = Header(None),
    strapi_service: StrapiService = Depends(get_strapi_service)
):
    """
    处理来自Strapi的webhook
    """
    try:
        # 验证webhook签名（如果有配置）
        if settings.STRAPI_WEBHOOK_SECRET and x_strapi_signature:
            # 这里应该实现签名验证逻辑
            pass

        # 处理webhook
        success = await strapi_service.handle_webhook(webhook_payload.dict())

        if success:
            logger.info(f"✅ Strapi webhook处理成功: {webhook_payload.event} - {webhook_payload.model}")
            return {
                "status": "success",
                "message": "Webhook处理成功",
                "event": webhook_payload.event,
                "model": webhook_payload.model
            }
        else:
            logger.warning(f"⚠️ Strapi webhook处理失败: {webhook_payload.event} - {webhook_payload.model}")
            return {
                "status": "error",
                "message": "Webhook处理失败"
            }

    except Exception as e:
        logger.error(f"❌ Strapi webhook处理异常: {str(e)}")
        return {
            "status": "error",
            "message": f"Webhook处理异常: {str(e)}"
        }


@router.post("/sync/bidirectional")
async def bidirectional_sync(
    sync_request: StrapiSyncRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    strapi_service: StrapiService = Depends(get_strapi_service)
):
    """
    双向同步内容
    """
    try:
        if sync_request.direction == "to_strapi":
            # 同步到Strapi
            if sync_request.content_type == "project":
                # 这里可以实现具体的同步逻辑
                pass
            else:
                raise ValidationError(f"不支持的内容类型同步: {sync_request.content_type}")

        elif sync_request.direction == "from_strapi":
            # 从Strapi同步
            if sync_request.entity_id:
                content_data = await strapi_service.sync_content_from_strapi(
                    sync_request.content_type, sync_request.entity_id
                )
                return {
                    "message": "从Strapi同步成功",
                    "content_type": sync_request.content_type,
                    "entity_id": sync_request.entity_id,
                    "data": content_data
                }
            else:
                raise ValidationError("从Strapi同步需要指定entity_id")

        elif sync_request.direction == "bidirectional":
            # 双向同步（复杂逻辑）
            # 这里可以实现冲突检测和解决逻辑
            pass

        logger.info(f"✅ 双向同步完成: {sync_request.content_type} - {sync_request.direction} - 用户: {current_user.username}")

        return {
            "message": "同步完成",
            "content_type": sync_request.content_type,
            "direction": sync_request.direction,
            "synced_at": datetime.utcnow().isoformat()
        }

    except ValidationError:
        raise
    except Exception as e:
        logger.error(f"❌ 双向同步失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="双向同步失败"
        )


@router.get("/content/{content_type}")
async def get_content_from_strapi(
    content_type: str = Path(..., description="内容类型"),
    populate: Optional[str] = Query(None, description="关联数据"),
    filters: Optional[str] = Query(None, description="过滤条件"),
    sort: Optional[str] = Query("createdAt:desc", description="排序"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    current_user: User = Depends(get_current_user),
    strapi_service: StrapiService = Depends(get_strapi_service)
):
    """
    从Strapi获取内容列表
    """
    try:
        # 验证内容类型
        valid_content_types = ["projects", "creative-ideas", "scripts", "storyboards", "media-assets", "final-videos"]
        if content_type not in valid_content_types:
            raise ValidationError(f"无效的内容类型: {content_type}")

        # 构建查询参数
        params = {
            "pagination[page]": page,
            "pagination[pageSize]": page_size,
            "sort": sort
        }

        if populate:
            params["populate"] = populate

        if filters:
            # 解析过滤条件（简单的实现）
            # 格式: field:value,field2:value2
            filter_pairs = filters.split(",")
            for pair in filter_pairs:
                if ":" in pair:
                    field, value = pair.split(":", 1)
                    params[f"filters[{field}][$eq]"] = value

        # 获取内容
        content_data = await strapi_service._make_request("GET", content_type, params=params)

        logger.info(f"✅ 从Strapi获取内容成功: {content_type} - 用户: {current_user.username}")

        return content_data

    except ValidationError:
        raise
    except Exception as e:
        logger.error(f"❌ 从Strapi获取内容失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="从Strapi获取内容失败"
        )


@router.post("/register-webhook")
async def register_strapi_webhook(
    webhook_url: str = Query(..., description="Webhook URL"),
    events: List[str] = Query(..., description="监听事件列表"),
    current_user: User = Depends(get_current_user),
    strapi_service: StrapiService = Depends(get_strapi_service)
):
    """
    注册Strapi webhook
    """
    try:
        # 验证事件类型
        valid_events = [
            "entry.create", "entry.update", "entry.delete",
            "entry.publish", "entry.unpublish",
            "media.create", "media.update", "media.delete"
        ]

        for event in events:
            if event not in valid_events:
                raise ValidationError(f"无效的事件类型: {event}")

        # 注册webhook
        webhook_response = await strapi_service.register_webhook(webhook_url, events)

        logger.info(f"✅ Strapi webhook注册成功: {webhook_url} - 事件: {events} - 用户: {current_user.username}")

        return {
            "message": "Webhook注册成功",
            "webhook_url": webhook_url,
            "events": events,
            "webhook_id": webhook_response["data"]["id"],
            "registered_at": datetime.utcnow().isoformat()
        }

    except ValidationError:
        raise
    except Exception as e:
        logger.error(f"❌ Strapi webhook注册失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Strapi webhook注册失败"
        )


logger.info("✅ Strapi集成API端点配置完成 - 支持内容管理和同步功能")