
"""
数据库连接和模型定义
Database Connection and Model Definitions

基于SQLAlchemy的数据库操作，支持中文内容存储
SQLAlchemy-based database operations with Chinese content support
"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, DateTime, Text, Boolean, ForeignKey, JSON, Enum as SQLEnum
from datetime import datetime
from typing import Optional, List, Dict, Any
import enum
from app.core.config import settings
from loguru import logger


class Base(DeclarativeBase):
    """数据库基类"""
    pass


# 枚举定义
class ProjectStatus(str, enum.Enum):
    """项目状态枚举"""
    DRAFT = "draft"
    CONCEPT = "concept"
    SCRIPTING = "scripting"
    STORYBOARD = "storyboard"
    PRODUCTION = "production"
    POST_PRODUCTION = "post_production"
    REVIEW = "review"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class UserRole(str, enum.Enum):
    """用户角色枚举"""
    ADMIN = "admin"
    CREATOR = "creator"
    REVIEWER = "reviewer"
    CLIENT = "client"


class PlatformTarget(str, enum.Enum):
    """目标平台枚举"""
    DOUYIN = "douyin"
    WECHAT = "wechat"
    WEIBO = "weibo"
    XIAOHONGSHU = "xiaohongshu"
    BILIBILI = "bilibili"
    YOUTUBE = "youtube"


class AssetType(str, enum.Enum):
    """资源类型枚举"""
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    TEXT = "text"
    DOCUMENT = "document"


class ScriptStatus(str, enum.Enum):
    """脚本状态枚举"""
    DRAFT = "draft"
    REVIEW = "review"
    APPROVED = "approved"
    REJECTED = "rejected"


class StoryboardStatus(str, enum.Enum):
    """分镜状态枚举"""
    DRAFT = "draft"
    REVIEW = "review"
    APPROVED = "approved"
    REJECTED = "rejected"


class VideoStatus(str, enum.Enum):
    """视频状态枚举"""
    DRAFT = "draft"
    RENDERING = "rendering"
    COMPLETED = "completed"
    FAILED = "failed"


# 用户模型
class User(Base):
    """用户模型 - 支持中国用户"""
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    phone: Mapped[Optional[str]] = mapped_column(String(20), unique=True, index=True)
    avatar: Mapped[Optional[str]] = mapped_column(String(500))
    role: Mapped[UserRole] = mapped_column(SQLEnum(UserRole), default=UserRole.CREATOR)
    organization_id: Mapped[Optional[str]] = mapped_column(String(36), index=True)
    subscription_id: Mapped[Optional[str]] = mapped_column(String(36))

    # 中文优化配置
    preferences: Mapped[Dict[str, Any]] = mapped_column(JSON, default=lambda: {
        "language": "zh-CN",
        "timezone": "Asia/Shanghai",
        "notifications": {
            "email": True,
            "sms": False,
            "wechat": False
        }
    })

    user_metadata: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    projects: Mapped[List["Project"]] = relationship("Project", back_populates="creator")


# 项目模型
class Project(Base):
    """视频项目模型 - 中文业务优化"""
    __tablename__ = "projects"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    title: Mapped[str] = mapped_column(String(200), index=True)
    slug: Mapped[str] = mapped_column(String(200), unique=True, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[ProjectStatus] = mapped