"""
项目管理API端点
Project Management API Endpoints

处理视频项目的CRUD操作和中文业务逻辑
Handles CRUD operations for video projects and Chinese business logic
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from uuid import uuid4
import re

from app.core.database import get_db, Project, ProjectStatus, PlatformTarget
from app.core.exceptions import NotFoundError, ValidationError
from loguru import logger

router = APIRouter()


def generate_slug(text: str) -> str:
    """生成URL友好的slug"""
    # 将中文转换为拼音（简化处理）
    import unicodedata
    
    # 移除特殊字符，保留中文、字母、数字和空格
    text = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9\s-]', '', text)
    
    # 将空格替换为连字符
    text = re.sub(r'\s+', '-', text.strip())
    
    # 限制长度
    if len(text) > 50:
        text = text[:50]
    
    # 确保不为空
    if not text:
        text = 'project'
    
    return text.lower()


# Pydantic模型 - 支持中文输入
class BusinessInput(BaseModel):
    """业务输入模型 - 中文优化"""
    target_audience: str = Field(..., description="目标受众 (中文)", example="年轻妈妈群体")
    key_message: str = Field(..., description="核心信息 (中文)", example="我们的母婴产品安全、温和、有效")
    brand_voice: str = Field(..., description="品牌调性 (中文)", example="温暖、专业、可信")
    call_to_action: str = Field(..., description="行动号召 (中文)", example="立即购买，给宝宝最好的呵护")
    cultural_context: str = Field(..., description="文化背景 (中文)", example="中国家庭注重宝宝健康和安全")
    platform_target: PlatformTarget = Field(..., description="目标平台")


class TechnicalSpecs(BaseModel):
    """技术规格模型"""
    target_duration: int = Field(..., ge=5, le=300, description="目标时长 (秒)")
    resolution: str = Field(default="1080p", description="分辨率")
    aspect_ratio: str = Field(default="16:9", description="宽高比")
    frame_rate: int = Field(default=24, description="帧率")
    file_format: str = Field(default="mp4", description="文件格式")


class CreateProjectRequest(BaseModel):
    """创建项目请求模型"""
    title: str = Field(..., min_length=1, max_length=200, description="项目标题 (支持中文)")
    description: Optional[str] = Field(None, max_length=2000, description="项目描述 (支持中文)")
    project_type: str = Field(default="promotional", description="项目类型")
    priority: str = Field(default="medium", description="优先级")
    deadline: Optional[datetime] = Field(None, description="截止日期")
    business_input: BusinessInput = Field(..., description="业务输入 (中文优化)")
    technical_specs: TechnicalSpecs = Field(default_factory=TechnicalSpecs, description="技术规格")
    creator_id: Optional[str] = Field(None, description="创建者ID (可选，用于关联用户)")


class ProjectResponse(BaseModel):
    """项目响应模型"""
    id: str
    title: str
    slug: str
    description: Optional[str]
    status: ProjectStatus
    project_type: str
    priority: str
    deadline: Optional[datetime]
    creator_id: Optional[str]
    business_input: BusinessInput
    technical_specs: TechnicalSpecs
    progress: dict
    created_at: datetime
    updated_at: datetime


class ProjectListResponse(BaseModel):
    """项目列表响应模型"""
    data: List[ProjectResponse]
    total: int
    page: int
    limit: int
    total_pages: int


# API端点实现

@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_data: CreateProjectRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    创建新的视频项目

    支持中文业务输入，针对中国短视频平台优化
    """
    try:
        # 验证中文业务输入
        if len(project_data.business_input.target_audience) < 2:
            raise ValidationError("目标受众描述太短，请提供更详细的中文描述")

        if len(project_data.business_input.key_message) < 5:
            raise ValidationError("核心信息描述太短，请提供更详细的中文描述")

        # 验证平台选择
        if project_data.business_input.platform_target not in [p.value for p in PlatformTarget]:
            raise ValidationError(f"不支持的目标平台: {project_data.business_input.platform_target}")

        # 创建项目
        project_id = str(uuid4())
        
        # 生成slug
        base_slug = generate_slug(project_data.title)
        slug = base_slug
        
        # 确保slug唯一性（简单处理，添加时间戳）
        import time
        slug = f"{base_slug}-{int(time.time())}"
        
        project = Project(
            id=project_id,
            title=project_data.title,
            slug=slug,
            description=project_data.description,
            status=ProjectStatus.DRAFT,
            project_type=project_data.project_type,
            priority=project_data.priority,
            deadline=project_data.deadline,
            creator_id=project_data.creator_id,
            business_input=project_data.business_input.dict(),
            technical_specs=project_data.technical_specs.dict(),
            progress={
                "current_stage": "draft",
                "overall_completion": 0.0,
                "stage_completion": {
                    "concept": 0.0,
                    "script": 0.0,
                    "storyboard": 0.0,
                    "production": 0.0,
                    "post_production": 0.0
                }
            },
            project_metadata={
                "estimated_cost": 0.0,
                "actual_cost": 0.0,
                "complexity_score": 5,
                "ai_confidence_score": 0.0,
                "human_review_required": False,
                "cultural_sensitivity": "medium"
            }
        )

        db.add(project)
        await db.commit()
        await db.refresh(project)

        logger.info(f"✅ 项目创建成功: {project.title} (ID: {project.id})")

        return ProjectResponse(
            id=project.id,
            title=project.title,
            slug=project.slug,
            description=project.description,
            status=project.status,
            project_type=project.project_type,
            priority=project.priority,
            deadline=project.deadline,
            creator_id=project.creator_id,
            business_input=BusinessInput(**project.business_input),
            technical_specs=TechnicalSpecs(**project.technical_specs),
            progress=project.progress,
            created_at=project.created_at,
            updated_at=project.updated_at
        )

    except ValidationError as e:
        logger.warning(f"❌ 项目创建验证失败: {e.message}")
        raise e
    except Exception as e:
        logger.error(f"❌ 项目创建失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="项目创建失败，请稍后重试"
        )


@router.get("/", response_model=ProjectListResponse)
async def get_projects(
    status: Optional[ProjectStatus] = Query(None, description="项目状态过滤"),
    platform_target: Optional[PlatformTarget] = Query(None, description="目标平台过滤"),
    search: Optional[str] = Query(None, description="搜索关键词 (支持中文)"),
    page: int = Query(1, ge=1, description="页码"),
    limit: int = Query(20, ge=1, le=100, description="每页数量"),
    sort_by: str = Query("created_at", description="排序字段"),
    sort_order: str = Query("desc", description="排序方向"),
    db: AsyncSession = Depends(get_db)
):
    """
    获取项目列表

    支持中文搜索、多平台过滤、状态过滤
    """
    try:
        from sqlalchemy import select, func, or_
        from sqlalchemy.orm import selectinload

        # 基础查询
        query = select(Project).options(selectinload(Project.creator))

        # 状态过滤
        if status:
            query = query.where(Project.status == status)

        # 平台过滤 - 从business_input中提取
        if platform_target:
            query = query.where(
                Project.business_input["platform_target"].astext == platform_target.value
            )

        # 中文搜索支持
        if search:
            search_term = f"%{search}%"
            query = query.where(
                or_(
                    Project.title.ilike(search_term),
                    Project.description.ilike(search_term),
                    Project.business_input["target_audience"].astext.ilike(search_term),
                    Project.business_input["key_message"].astext.ilike(search_term),
                    Project.business_input["brand_voice"].astext.ilike(search_term)
                )
            )

        # 排序
        if sort_order == "desc":
            query = query.order_by(getattr(Project, sort_by).desc())
        else:
            query = query.order_by(getattr(Project, sort_by).asc())

        # 分页
        total_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(total_query)
        total = total_result.scalar()

        # 分页查询
        offset = (page - 1) * limit
        query = query.offset(offset).limit(limit)

        result = await db.execute(query)
        projects = result.scalars().all()

        logger.info(f"✅ 项目列表查询成功: {len(projects)} 个项目，总计 {total}")

        return ProjectListResponse(
            data=[
                ProjectResponse(
                    id=p.id,
                    title=p.title,
                    slug=p.slug,
                    description=p.description,
                    status=p.status,
                    project_type=p.project_type,
                    priority=p.priority,
                    deadline=p.deadline,
                    creator_id=p.creator_id,
                    business_input=BusinessInput(**p.business_input),
                    technical_specs=TechnicalSpecs(**p.technical_specs),
                    progress=p.progress,
                    created_at=p.created_at,
                    updated_at=p.updated_at
                )
                for p in projects
            ],
            total=total,
            page=page,
            limit=limit,
            total_pages=(total + limit - 1) // limit
        )

    except Exception as e:
        logger.error(f"❌ 项目列表查询失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="项目列表查询失败，请稍后重试"
        )


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    获取项目详情
    """
    try:
        from sqlalchemy import select
        from sqlalchemy.orm import selectinload

        query = select(Project).options(selectinload(Project.creator)).where(Project.id == project_id)
        result = await db.execute(query)
        project = result.scalar_one_or_none()

        if not project:
            raise NotFoundError("项目", project_id)

        logger.info(f"✅ 项目详情查询成功: {project.title} (ID: {project.id})")

        return ProjectResponse(
            id=project.id,
            title=project.title,
            description=project.description,
            status=project.status,
            project_type=project.project_type,
            priority=project.priority,
            deadline=project.deadline,
            creator_id=project.creator_id,
            business_input=BusinessInput(**project.business_input),
            technical_specs=TechnicalSpecs(**project.technical_specs),
            progress=project.progress,
            created_at=project.created_at,
            updated_at=project.updated_at
        )

    except NotFoundError:
        raise
    except Exception as e:
        logger.error(f"❌ 项目详情查询失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="项目详情查询失败，请稍后重试"
        )


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: str,
    project_data: CreateProjectRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    更新项目信息
    """
    try:
        from sqlalchemy import select

        query = select(Project).where(Project.id == project_id)
        result = await db.execute(query)
        project = result.scalar_one_or_none()

        if not project:
            raise NotFoundError("项目", project_id)

        # 更新字段
        project.title = project_data.title
        project.description = project_data.description
        project.project_type = project_data.project_type
        project.priority = project_data.priority
        project.deadline = project_data.deadline
        project.business_input = project_data.business_input.dict()
        project.technical_specs = project_data.technical_specs.dict()
        project.updated_at = datetime.utcnow()

        await db.commit()
        await db.refresh(project)

        logger.info(f"✅ 项目更新成功: {project.title} (ID: {project.id})")

        return ProjectResponse(
            id=project.id,
            title=project.title,
            description=project.description,
            status=project.status,
            project_type=project.project_type,
            priority=project.priority,
            deadline=project.deadline,
            creator_id=project.creator_id,
            business_input=BusinessInput(**project.business_input),
            technical_specs=TechnicalSpecs(**project.technical_specs),
            progress=project.progress,
            created_at=project.created_at,
            updated_at=project.updated_at
        )

    except NotFoundError:
        raise
    except Exception as e:
        logger.error(f"❌ 项目更新失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="项目更新失败，请稍后重试"
        )


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    删除项目（软删除）
    """
    try:
        from sqlalchemy import select

        query = select(Project).where(Project.id == project_id)
        result = await db.execute(query)
        project = result.scalar_one_or_none()

        if not project:
            raise NotFoundError("项目", project_id)

        # 软删除 - 更新状态而不是真正删除
        project.status = ProjectStatus.ARCHIVED
        await db.commit()

        logger.info(f"✅ 项目归档成功: {project.title} (ID: {project.id})")

    except NotFoundError:
        raise
    except Exception as e:
        logger.error(f"❌ 项目归档失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="项目归档失败，请稍后重试"
        )


@router.get("/{project_id}/status", response_model=dict)
async def get_project_status(
    project_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    获取项目状态
    """
    try:
        from sqlalchemy import select

        query = select(Project.status, Project.progress).where(Project.id == project_id)
        result = await db.execute(query)
        project_data = result.first()

        if not project_data:
            raise NotFoundError("项目", project_id)

        status_value, progress = project_data

        logger.info(f"✅ 项目状态查询成功: {project_id} - {status_value}")

        return {
            "project_id": project_id,
            "status": status_value,
            "progress": progress,
            "updated_at": datetime.utcnow().isoformat()
        }

    except NotFoundError:
        raise
    except Exception as e:
        logger.error(f"❌ 项目状态查询失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="项目状态查询失败，请稍后重试"
        )


logger.info("✅ 项目管理API端点配置完成 - 支持中文业务逻辑")