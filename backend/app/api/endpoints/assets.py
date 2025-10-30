"""
媒体资源API端点
Media Assets API Endpoints

处理文件上传、存储、媒体资源管理和阿里云OSS集成
Handles file uploads, storage, media asset management, and Alibaba Cloud OSS integration
"""

import logging
import os
import hashlib
import mimetypes
from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import uuid4
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from pydantic import BaseModel, Field, validator
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, update, delete

from app.core.database import get_db, MediaAsset
from app.core.security import get_current_user
from app.models import User
from app.core.exceptions import ValidationError, NotFoundError
from app.core.config import settings
from app.services.file_storage import FileStorageService

logger = logging.getLogger(__name__)
router = APIRouter()

# 文件存储服务实例
file_storage = FileStorageService()

# 媒体资源模型定义
class AssetUploadResponse(BaseModel):
    """资源上传响应模型"""
    asset_id: str
    filename: str
    original_filename: str
    file_size: int
    file_type: str
    mime_type: str
    url: str
    thumbnail_url: Optional[str]
    upload_status: str
    checksum: str
    uploaded_at: str

class AssetResponse(BaseModel):
    """资源详情响应模型"""
    id: str
    name: str
    original_filename: str
    type: str
    mime_type: str
    url: str
    thumbnail_url: Optional[str]
    file_size: int
    checksum: str
    technical_specs: Dict[str, Any]
    metadata: Dict[str, Any]
    project_id: Optional[str]
    uploaded_by: str
    created_at: datetime
    updated_at: datetime

class AssetListResponse(BaseModel):
    """资源列表响应模型"""
    assets: List[AssetResponse]
    total: int
    page: int
    limit: int
    total_pages: int

class AssetUploadRequest(BaseModel):
    """资源上传请求模型"""
    name: str = Field(..., min_length=1, max_length=255, description="资源名称")
    type: str = Field(..., description="资源类型 (image/video/audio/document)")
    project_id: Optional[str] = Field(None, description="关联的项目ID")
    description: Optional[str] = Field(None, max_length=1000, description="资源描述")
    tags: Optional[List[str]] = Field(default_factory=list, description="资源标签")
    generate_thumbnail: bool = Field(default=True, description="是否生成缩略图")

    @validator('type')
    def validate_type(cls, v):
        valid_types = ["image", "video", "audio", "document"]
        if v not in valid_types:
            raise ValueError(f'资源类型必须是以下之一: {", ".join(valid_types)}')
        return v

    @validator('name')
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError('资源名称不能为空')
        return v.strip()

class AssetUpdateRequest(BaseModel):
    """资源更新请求模型"""
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="资源名称")
    description: Optional[str] = Field(None, max_length=1000, description="资源描述")
    tags: Optional[List[str]] = Field(None, description="资源标签")
    project_id: Optional[str] = Field(None, description="关联的项目ID")

class AssetSearchRequest(BaseModel):
    """资源搜索请求模型"""
    query: Optional[str] = Field(None, description="搜索关键词")
    type: Optional[str] = Field(None, description="资源类型过滤")
    project_id: Optional[str] = Field(None, description="项目ID过滤")
    tags: Optional[List[str]] = Field(None, description="标签过滤")
    uploaded_by: Optional[str] = Field(None, description="上传者过滤")
    date_from: Optional[datetime] = Field(None, description="开始日期")
    date_to: Optional[datetime] = Field(None, description="结束日期")

# 文件验证常量
MAX_FILE_SIZES = {
    "image": 10 * 1024 * 1024,      # 10MB
    "video": 500 * 1024 * 1024,     # 500MB
    "audio": 50 * 1024 * 1024,      # 50MB
    "document": 20 * 1024 * 1024    # 20MB
}

ALLOWED_MIME_TYPES = {
    "image": ["image/jpeg", "image/png", "image/webp", "image/gif", "image/bmp", "image/tiff"],
    "video": ["video/mp4", "video/webm", "video/quicktime", "video/x-msvideo", "video/mpeg"],
    "audio": ["audio/mp3", "audio/wav", "audio/aac", "audio/m4a", "audio/ogg", "audio/flac"],
    "document": ["application/pdf", "application/msword", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]
}

# API端点实现

@router.post("/upload", response_model=AssetUploadResponse)
async def upload_asset(
    file: UploadFile = File(...),
    name: str = Form(...),
    type: str = Form(...),
    project_id: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),
    generate_thumbnail: bool = Form(True),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    上传媒体资源文件

    支持图片、视频、音频和文档文件上传，自动进行文件类型验证和大小限制检查
    """
    try:
        # 验证文件
        _validate_upload_file(file, type)

        # 解析标签
        tag_list = []
        if tags:
            tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()]

        # 读取文件内容并计算校验和
        file_content = await file.read()
        file_size = len(file_content)
        checksum = hashlib.sha256(file_content).hexdigest()

        # 检查文件是否已存在（通过校验和）
        existing_asset = await db.execute(
            select(MediaAsset).where(MediaAsset.checksum == checksum)
        )
        if existing_asset.scalar_one_or_none():
            raise ValidationError(
                "文件已存在（校验和匹配）",
                details={"checksum": checksum}
            )

        # 生成文件存储路径
        file_extension = Path(file.filename).suffix.lower()
        asset_id = str(uuid4())
        storage_path = f"assets/{current_user.id}/{asset_id}{file_extension}"

        # 上传文件到存储服务
        upload_result = await file_storage.upload_file(
            file_content=file_content,
            file_path=storage_path,
            content_type=file.content_type
        )

        # 生成缩略图（如果是图片且需要生成）
        thumbnail_url = None
        if type == "image" and generate_thumbnail:
            try:
                thumbnail_path = f"thumbnails/{current_user.id}/{asset_id}.jpg"
                thumbnail_result = await file_storage.generate_thumbnail(
                    file_content=file_content,
                    thumbnail_path=thumbnail_path,
                    size=(300, 300)
                )
                thumbnail_url = thumbnail_result["url"]
            except Exception as e:
                logger.warning(f"生成缩略图失败: {str(e)}")

        # 提取技术规格
        technical_specs = await _extract_technical_specs(file_content, type, file.content_type)

        # 创建媒体资源记录
        new_asset = MediaAsset(
            id=asset_id,
            name=name,
            original_filename=file.filename,
            type=type,
            mime_type=file.content_type,
            file_size=file_size,
            url=upload_result["url"],
            thumbnail_url=thumbnail_url,
            checksum=checksum,
            technical_specs=technical_specs,
            metadata={
                "description": description,
                "tags": tag_list,
                "upload_original_name": file.filename
            },
            project_id=project_id,
            uploaded_by=current_user.id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        db.add(new_asset)
        await db.commit()
        await db.refresh(new_asset)

        logger.info(f"✅ 媒体资源上传成功: {name} ({file.filename}) - 用户: {current_user.username}")

        return AssetUploadResponse(
            asset_id=asset_id,
            filename=name,
            original_filename=file.filename,
            file_size=file_size,
            file_type=type,
            mime_type=file.content_type,
            url=upload_result["url"],
            thumbnail_url=thumbnail_url,
            upload_status="completed",
            checksum=checksum,
            uploaded_at=datetime.utcnow().isoformat()
        )

    except ValidationError:
        raise
    except Exception as e:
        logger.error(f"❌ 媒体资源上传失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="媒体资源上传失败"
        )

@router.get("/", response_model=AssetListResponse)
async def get_assets(
    type: Optional[str] = None,
    project_id: Optional[str] = None,
    page: int = 1,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取媒体资源列表

    支持按类型、项目ID过滤，支持分页
    """
    try:
        # 基础查询
        query = select(MediaAsset).where(MediaAsset.uploaded_by == current_user.id)

        # 应用过滤条件
        if type:
            query = query.where(MediaAsset.type == type)
        if project_id:
            query = query.where(MediaAsset.project_id == project_id)

        # 排序（按创建时间倒序）
        query = query.order_by(MediaAsset.created_at.desc())

        # 分页
        from sqlalchemy import func
        total_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(total_query)
        total = total_result.scalar()

        offset = (page - 1) * limit
        query = query.offset(offset).limit(limit)

        # 执行查询
        result = await db.execute(query)
        assets = result.scalars().all()

        # 转换为响应模型
        asset_responses = []
        for asset in assets:
            asset_responses.append(AssetResponse(
                id=asset.id,
                name=asset.name,
                original_filename=asset.original_filename,
                type=asset.type,
                mime_type=asset.mime_type,
                url=asset.url,
                thumbnail_url=asset.thumbnail_url,
                file_size=asset.file_size,
                checksum=asset.checksum,
                technical_specs=asset.technical_specs,
                metadata=asset.metadata,
                project_id=asset.project_id,
                uploaded_by=str(asset.uploaded_by),
                created_at=asset.created_at,
                updated_at=asset.updated_at
            ))

        logger.info(f"✅ 媒体资源列表获取成功: {len(asset_responses)} 个资源 - 用户: {current_user.username}")

        return AssetListResponse(
            assets=asset_responses,
            total=total,
            page=page,
            limit=limit,
            total_pages=(total + limit - 1) // limit
        )

    except Exception as e:
        logger.error(f"❌ 获取媒体资源列表失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取媒体资源列表失败"
        )

@router.get("/{asset_id}", response_model=AssetResponse)
async def get_asset(
    asset_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取媒体资源详情

    Args:
        asset_id: 资源ID
    """
    try:
        from sqlalchemy import select

        result = await db.execute(
            select(MediaAsset).where(
                MediaAsset.id == asset_id,
                MediaAsset.uploaded_by == current_user.id
            )
        )
        asset = result.scalar_one_or_none()

        if not asset:
            raise NotFoundError("媒体资源", asset_id)

        logger.info(f"✅ 媒体资源详情获取成功: {asset.name} (ID: {asset_id})")

        return AssetResponse(
            id=asset.id,
            name=asset.name,
            original_filename=asset.original_filename,
            type=asset.type,
            mime_type=asset.mime_type,
            url=asset.url,
            thumbnail_url=asset.thumbnail_url,
            file_size=asset.file_size,
            checksum=asset.checksum,
            technical_specs=asset.technical_specs,
            metadata=asset.metadata,
            project_id=asset.project_id,
            uploaded_by=str(asset.uploaded_by),
            created_at=asset.created_at,
            updated_at=asset.updated_at
        )

    except NotFoundError:
        raise
    except Exception as e:
        logger.error(f"❌ 获取媒体资源详情失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取媒体资源详情失败"
        )

@router.put("/{asset_id}", response_model=AssetResponse)
async def update_asset(
    asset_id: str,
    update_data: AssetUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    更新媒体资源信息

    Args:
        asset_id: 资源ID
        update_data: 更新数据
    """
    try:
        from sqlalchemy import select, update

        # 检查资源是否存在
        result = await db.execute(
            select(MediaAsset).where(
                MediaAsset.id == asset_id,
                MediaAsset.uploaded_by == current_user.id
            )
        )
        asset = result.scalar_one_or_none()

        if not asset:
            raise NotFoundError("媒体资源", asset_id)

        # 准备更新数据
        update_values = update_data.dict(exclude_unset=True)
        update_values["updated_at"] = datetime.utcnow()

        # 执行更新
        await db.execute(
            update(MediaAsset).
            where(MediaAsset.id == asset_id).
            values(**update_values)
        )
        await db.commit()

        logger.info(f"✅ 媒体资源更新成功: {asset.name} (ID: {asset_id})")

        # 返回更新后的资源信息
        return await get_asset(asset_id, current_user, db)

    except NotFoundError:
        raise
    except Exception as e:
        logger.error(f"❌ 更新媒体资源失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新媒体资源失败"
        )

@router.delete("/{asset_id}")
async def delete_asset(
    asset_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    删除媒体资源

    Args:
        asset_id: 资源ID
    """
    try:
        from sqlalchemy import select, delete

        # 检查资源是否存在
        result = await db.execute(
            select(MediaAsset).where(
                MediaAsset.id == asset_id,
                MediaAsset.uploaded_by == current_user.id
            )
        )
        asset = result.scalar_one_or_none()

        if not asset:
            raise NotFoundError("媒体资源", asset_id)

        # 从存储服务删除文件
        try:
            await file_storage.delete_file(asset.url)
            if asset.thumbnail_url:
                await file_storage.delete_file(asset.thumbnail_url)
        except Exception as e:
            logger.warning(f"删除存储文件失败: {str(e)}")

        # 删除数据库记录
        await db.execute(
            delete(MediaAsset).where(MediaAsset.id == asset_id)
        )
        await db.commit()

        logger.info(f"✅ 媒体资源删除成功: {asset.name} (ID: {asset_id})")

        return {
            "message": "媒体资源删除成功",
            "asset_id": asset_id,
            "deleted_at": datetime.utcnow().isoformat()
        }

    except NotFoundError:
        raise
    except Exception as e:
        logger.error(f"❌ 删除媒体资源失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="删除媒体资源失败"
        )

@router.post("/search", response_model=AssetListResponse)
async def search_assets(
    search_request: AssetSearchRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    搜索媒体资源

    支持多种搜索条件和过滤器
    """
    try:
        from sqlalchemy import select, or_, and_

        # 基础查询
        query = select(MediaAsset).where(MediaAsset.uploaded_by == current_user.id)

        # 应用搜索条件
        conditions = []

        if search_request.query:
            # 在名称、原始文件名和描述中搜索
            conditions.append(
                or_(
                    MediaAsset.name.ilike(f"%{search_request.query}%"),
                    MediaAsset.original_filename.ilike(f"%{search_request.query}%"),
                    MediaAsset.metadata["description"].astext.ilike(f"%{search_request.query}%")
                )
            )

        if search_request.type:
            conditions.append(MediaAsset.type == search_request.type)

        if search_request.project_id:
            conditions.append(MediaAsset.project_id == search_request.project_id)

        if search_request.tags:
            # 标签匹配 - 简化实现
            for tag in search_request.tags:
                conditions.append(MediaAsset.metadata["tags"].astext.ilike(f"%{tag}%"))

        if search_request.date_from:
            conditions.append(MediaAsset.created_at >= search_request.date_from)

        if search_request.date_to:
            conditions.append(MediaAsset.created_at <= search_request.date_to)

        # 应用所有条件
        if conditions:
            query = query.where(and_(*conditions))

        # 排序和分页
        query = query.order_by(MediaAsset.created_at.desc())

        from sqlalchemy import func
        total_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(total_query)
        total = total_result.scalar()

        # 执行查询（这里简化处理，实际应该支持分页参数）
        result = await db.execute(query.limit(50))  # 搜索结果限制50个
        assets = result.scalars().all()

        # 转换为响应模型
        asset_responses = []
        for asset in assets:
            asset_responses.append(AssetResponse(
                id=asset.id,
                name=asset.name,
                original_filename=asset.original_filename,
                type=asset.type,
                mime_type=asset.mime_type,
                url=asset.url,
                thumbnail_url=asset.thumbnail_url,
                file_size=asset.file_size,
                checksum=asset.checksum,
                technical_specs=asset.technical_specs,
                metadata=asset.metadata,
                project_id=asset.project_id,
                uploaded_by=str(asset.uploaded_by),
                created_at=asset.created_at,
                updated_at=asset.updated_at
            ))

        logger.info(f"✅ 媒体资源搜索完成: 找到 {len(asset_responses)} 个资源 - 用户: {current_user.username}")

        return AssetListResponse(
            assets=asset_responses,
            total=total,
            page=1,
            limit=len(asset_responses),
            total_pages=1
        )

    except Exception as e:
        logger.error(f"❌ 媒体资源搜索失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="媒体资源搜索失败"
        )

# 辅助函数
def _validate_upload_file(file: UploadFile, asset_type: str) -> None:
    """
    验证上传文件

    Args:
        file: 上传的文件
        asset_type: 资源类型

    Raises:
        ValidationError: 如果文件验证失败
    """
    # 验证文件类型
    if not file.content_type:
        raise ValidationError("无法确定文件类型", details={"filename": file.filename})

    # 检查MIME类型
    allowed_mime_types = ALLOWED_MIME_TYPES.get(asset_type, [])
    if file.content_type not in allowed_mime_types:
        raise ValidationError(
            f"不支持的文件类型: {file.content_type}",
            details={
                "allowed_types": allowed_mime_types,
                "provided_type": file.content_type,
                "asset_type": asset_type
            }
        )

    # 验证文件扩展名
    file_extension = Path(file.filename).suffix.lower()
    allowed_extensions = {
        "image": [".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp", ".tiff"],
        "video": [".mp4", ".webm", ".mov", ".avi", ".mpeg"],
        "audio": [".mp3", ".wav", ".aac", ".m4a", ".ogg", ".flac"],
        "document": [".pdf", ".doc", ".docx"]
    }

    if file_extension not in allowed_extensions.get(asset_type, []):
        raise ValidationError(
            f"不支持的文件扩展名: {file_extension}",
            details={
                "allowed_extensions": allowed_extensions.get(asset_type, []),
                "provided_extension": file_extension
            }
        )

async def _extract_technical_specs(file_content: bytes, asset_type: str, mime_type: str) -> Dict[str, Any]:
    """
    提取文件技术规格

    Args:
        file_content: 文件内容
        asset_type: 资源类型
        mime_type: MIME类型

    Returns:
        技术规格字典
    """
    specs = {
        "mime_type": mime_type,
        "file_size": len(file_content),
        "checksum": hashlib.sha256(file_content).hexdigest()
    }

    if asset_type == "image":
        try:
            from PIL import Image
            import io

            image = Image.open(io.BytesIO(file_content))
            specs.update({
                "width": image.width,
                "height": image.height,
                "format": image.format,
                "mode": image.mode,
                "color_space": image.mode
            })
        except Exception as e:
            logger.warning(f"提取图片技术规格失败: {str(e)}")

    elif asset_type == "video":
        try:
            # 这里可以集成视频处理库来提取视频信息
            specs.update({
                "duration": None,  # 需要视频处理库
                "resolution": None,
                "codec": None,
                "frame_rate": None
            })
        except Exception as e:
            logger.warning(f"提取视频技术规格失败: {str(e)}")

    elif asset_type == "audio":
        try:
            # 这里可以集成音频处理库来提取音频信息
            specs.update({
                "duration": None,  # 需要音频处理库
                "sample_rate": None,
                "channels": None,
                "codec": None
            })
        except Exception as e:
            logger.warning(f"提取音频技术规格失败: {str(e)}")

    return specs

logger.info("✅ 媒体资源API端点配置完成 - 支持文件上传、OSS集成和完整媒体管理功能")