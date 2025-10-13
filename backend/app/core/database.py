
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
    status: Mapped[ProjectStatus] = mapped_column(SQLEnum(ProjectStatus), default=ProjectStatus.DRAFT, index=True)
    priority: Mapped[str] = mapped_column(String(20), default="medium")
    project_type: Mapped[str] = mapped_column(String(50), default="promotional")

    # 业务输入 - 中文优化
    business_input: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    technical_specs: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    progress: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    project_metadata: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)

    # 关联
    creator_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("users.id"), index=True, nullable=True)
    creator: Mapped[Optional["User"]] = relationship("User", back_populates="projects")
    organization_id: Mapped[Optional[str]] = mapped_column(String(36), index=True)
    workflow_id: Mapped[Optional[str]] = mapped_column(String(36))
    parent_project_id: Mapped[Optional[str]] = mapped_column(String(36))

    # 时间跟踪
    deadline: Mapped[Optional[datetime]] = mapped_column(DateTime)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    creative_ideas: Mapped[List["CreativeIdea"]] = relationship("CreativeIdea", back_populates="project")
    scripts: Mapped[List["Script"]] = relationship("Script", back_populates="project")
    storyboards: Mapped[List["Storyboard"]] = relationship("Storyboard", back_populates="project")
    media_assets: Mapped[List["MediaAsset"]] = relationship("MediaAsset", back_populates="project")
    final_videos: Mapped[List["FinalVideo"]] = relationship("FinalVideo", back_populates="project")


# AI模型配置
class AIModel(Base):
    """AI模型配置"""
    __tablename__ = "ai_models"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    provider: Mapped[str] = mapped_column(String(50), index=True)  # deepseek, jimeng, etc.
    model_type: Mapped[str] = mapped_column(String(50), index=True)  # text, image, video, audio
    model_id: Mapped[str] = mapped_column(String(100))
    version: Mapped[str] = mapped_column(String(50))
    endpoint: Mapped[str] = mapped_column(String(500))

    # 配置
    config: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    pricing: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    performance: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)

    # 状态和限制
    status: Mapped[str] = mapped_column(String(20), default="active")
    rate_limit: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    region: Mapped[str] = mapped_column(String(20), default="china")
    compliance: Mapped[List[str]] = mapped_column(JSON, default=list)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# 创意想法模型
class CreativeIdea(Base):
    """创意想法模型 - AI生成的创意内容"""
    __tablename__ = "creative_ideas"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id"), index=True)
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[Optional[str]] = mapped_column(Text)
    content: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    
    # AI生成信息
    ai_model: Mapped[str] = mapped_column(String(100))
    prompt: Mapped[Optional[str]] = mapped_column(Text)
    parameters: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    
    # 评分和反馈
    rating: Mapped[Optional[int]] = mapped_column(Integer)
    feedback: Mapped[Optional[str]] = mapped_column(Text)
    
    # 状态
    status: Mapped[str] = mapped_column(String(20), default="active")
    is_selected: Mapped[bool] = mapped_column(Boolean, default=False)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    project: Mapped["Project"] = relationship("Project", back_populates="creative_ideas")


# 脚本模型
class Script(Base):
    """脚本模型 - 视频脚本内容"""
    __tablename__ = "scripts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id"), index=True)
    title: Mapped[str] = mapped_column(String(200))
    content: Mapped[str] = mapped_column(Text)
    
    # 脚本元数据
    duration: Mapped[Optional[int]] = mapped_column(Integer)  # 秒
    word_count: Mapped[Optional[int]] = mapped_column(Integer)
    language: Mapped[str] = mapped_column(String(10), default="zh-CN")
    
    # 结构化内容
    scenes: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list)
    characters: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list)
    
    # 状态管理
    status: Mapped[ScriptStatus] = mapped_column(SQLEnum(ScriptStatus), default=ScriptStatus.DRAFT)
    version: Mapped[int] = mapped_column(Integer, default=1)
    
    # AI信息
    ai_model: Mapped[Optional[str]] = mapped_column(String(100))
    prompt: Mapped[Optional[str]] = mapped_column(Text)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    project: Mapped["Project"] = relationship("Project", back_populates="scripts")


# 分镜模型
class Storyboard(Base):
    """分镜模型 - 视频分镜设计"""
    __tablename__ = "storyboards"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id"), index=True)
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[Optional[str]] = mapped_column(Text)
    
    # 分镜内容
    frames: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list)
    layout: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    
    # 视觉风格
    style: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    color_palette: Mapped[List[str]] = mapped_column(JSON, default=list)
    
    # 状态管理
    status: Mapped[StoryboardStatus] = mapped_column(SQLEnum(StoryboardStatus), default=StoryboardStatus.DRAFT)
    version: Mapped[int] = mapped_column(Integer, default=1)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    project: Mapped["Project"] = relationship("Project", back_populates="storyboards")


# 媒体资源模型
class MediaAsset(Base):
    """媒体资源模型 - 图片、视频、音频等资源"""
    __tablename__ = "media_assets"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id"), index=True)
    name: Mapped[str] = mapped_column(String(200))
    type: Mapped[AssetType] = mapped_column(SQLEnum(AssetType))
    
    # 文件信息
    file_url: Mapped[str] = mapped_column(String(500))
    file_size: Mapped[Optional[int]] = mapped_column(Integer)
    mime_type: Mapped[str] = mapped_column(String(100))
    
    # 元数据
    asset_metadata: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    tags: Mapped[List[str]] = mapped_column(JSON, default=list)
    
    # 来源信息
    source: Mapped[str] = mapped_column(String(50), default="upload")  # upload, ai_generated, external
    ai_model: Mapped[Optional[str]] = mapped_column(String(100))
    
    # 状态
    status: Mapped[str] = mapped_column(String(20), default="active")
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    project: Mapped["Project"] = relationship("Project", back_populates="media_assets")


# 最终视频模型
class FinalVideo(Base):
    """最终视频模型 - 生成的最终视频"""
    __tablename__ = "final_videos"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id"), index=True)
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[Optional[str]] = mapped_column(Text)
    
    # 视频信息
    video_url: Mapped[str] = mapped_column(String(500))
    thumbnail_url: Mapped[Optional[str]] = mapped_column(String(500))
    duration: Mapped[int] = mapped_column(Integer)  # 秒
    resolution: Mapped[str] = mapped_column(String(20))
    file_size: Mapped[int] = mapped_column(Integer)
    
    # 平台优化
    platform_optimizations: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    video_metadata: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    
    # 状态管理
    status: Mapped[VideoStatus] = mapped_column(SQLEnum(VideoStatus), default=VideoStatus.DRAFT)
    render_job_id: Mapped[Optional[str]] = mapped_column(String(100))
    
    # AI信息
    ai_model: Mapped[str] = mapped_column(String(100))
    parameters: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    
    # 发布信息
    published_urls: Mapped[Dict[str, str]] = mapped_column(JSON, default=dict)  # 各平台发布链接
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    project: Mapped["Project"] = relationship("Project", back_populates="final_videos")


# 数据库引擎和会话
engine = None
async_session_maker = None


async def init_db():
    """初始化数据库连接"""
    global engine, async_session_maker

    try:
        # 创建数据库引擎 - 根据数据库类型调整配置
        engine_kwargs = {
            "url": settings.DATABASE_URL,
            "echo": settings.DEBUG,
            "pool_pre_ping": True,
        }

        # PostgreSQL特有配置
        if "postgresql" in settings.DATABASE_URL:
            engine_kwargs.update({
                "pool_size": settings.DATABASE_POOL_SIZE,
                "max_overflow": settings.DATABASE_MAX_OVERFLOW,
            })

        # SQLite特有配置
        elif "sqlite" in settings.DATABASE_URL:
            # SQLite不支持连接池配置
            pass

        engine = create_async_engine(**engine_kwargs)

        # 创建会话工厂
        async_session_maker = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False
        )

        # 创建所有表
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        logger.info("✅ 数据库连接和表结构创建成功")

    except Exception as e:
        logger.error(f"❌ 数据库连接失败: {e}")
        raise


async def get_db():
    """获取数据库会话"""
    async with async_session_maker() as session:
        try:
            yield session
        except Exception as e:
            logger.error(f"数据库会话错误: {e}")
            await session.rollback()
            raise
        finally:
            await session.close()


class RedisManager:
    """Redis连接管理器"""
    
    def __init__(self):
        self._client = None
        self._initialized = False
        
    async def init(self):
        """初始化Redis连接"""
        if self._initialized and self._client is not None:
            return True
            
        try:
            import redis.asyncio as redis
            from redis.exceptions import RedisError, ConnectionError
            
            # 配置Redis连接参数
            redis_config = {
                "max_connections": settings.REDIS_POOL_SIZE,
                "decode_responses": True,
                "socket_connect_timeout": 5,
                "socket_timeout": 5,
                "retry_on_timeout": True,
                "health_check_interval": 30,
            }
            
            # 创建Redis客户端
            self._client = redis.from_url(
                settings.REDIS_URL,
                **redis_config
            )

            # 测试连接
            await self._client.ping()
            self._initialized = True
            logger.info("✅ Redis连接成功")
            return True

        except ConnectionError as e:
            logger.warning(f"⚠️ Redis连接失败 - 连接错误: {e}")
            self._client = None
            self._initialized = False
            return False
        except RedisError as e:
            logger.warning(f"⚠️ Redis连接失败 - Redis错误: {e}")
            self._client = None
            self._initialized = False
            return False
        except Exception as e:
            logger.warning(f"⚠️ Redis连接失败 - 未知错误: {e}")
            self._client = None
            self._initialized = False
            return False
    
    async def close(self):
        """关闭Redis连接"""
        if self._client is not None:
            try:
                await self._client.aclose()
            except Exception as e:
                logger.warning(f"关闭Redis连接时出错: {e}")
            finally:
                self._client = None
                self._initialized = False
    
    @property
    def is_available(self):
        """检查Redis是否可用"""
        return self._client is not None and self._initialized
    
    def get_client(self):
        """获取Redis客户端"""
        if not self.is_available:
            raise RuntimeError("Redis客户端不可用，请先调用init()方法初始化")
        return self._client
    
    async def health_check(self):
        """健康检查"""
        if not self.is_available:
            return False
        try:
            await self._client.ping()
            return True
        except Exception:
            return False


# Redis连接管理器实例
redis_manager = RedisManager()

# 向后兼容的函数
async def init_redis():
    """初始化Redis连接（向后兼容）"""
    return await redis_manager.init()

async def get_redis():
    """获取Redis客户端（向后兼容）"""
    return redis_manager.get_client()

async def check_redis_health():
    """检查Redis健康状态（向后兼容）"""
    return await redis_manager.health_check()


# 数据库工具函数
async def check_db_health():
    """检查数据库健康状态"""
    try:
        async with async_session_maker() as session:
            result = await session.execute("SELECT 1")
            return True
    except Exception as e:
        logger.error(f"数据库健康检查失败: {e}")
        return False


async def check_redis_health():
    """检查Redis健康状态"""
    try:
        if redis_client:
            await redis_client.ping()
            return True
        return False
    except Exception as e:
        logger.error(f"Redis健康检查失败: {e}")
        return False


logger.info("✅ 数据库模块加载完成 - 支持中文内容存储")
