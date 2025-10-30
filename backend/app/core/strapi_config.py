"""
Strapi配置模块
Strapi Configuration Module

处理Strapi集成的配置设置
Handles configuration settings for Strapi integration
"""

import os
from typing import Optional
try:
    from pydantic.v1 import BaseSettings, validator
except ImportError:
    from pydantic_settings import BaseSettings
    from pydantic import validator

import logging

logger = logging.getLogger(__name__)


class StrapiConfig(BaseSettings):
    """Strapi配置类"""

    # Strapi服务器配置
    STRAPI_URL: str = os.getenv("STRAPI_URL", "http://localhost:1337")
    STRAPI_API_TOKEN: str = os.getenv("STRAPI_API_TOKEN", "")
    STRAPI_WEBHOOK_SECRET: str = os.getenv("STRAPI_WEBHOOK_SECRET", "")

    # 内容同步配置
    STRAPI_SYNC_ENABLED: bool = os.getenv("STRAPI_SYNC_ENABLED", "true").lower() == "true"
    STRAPI_AUTO_SYNC: bool = os.getenv("STRAPI_AUTO_SYNC", "true").lower() == "true"
    STRAPI_SYNC_INTERVAL: int = int(os.getenv("STRAPI_SYNC_INTERVAL", "300"))  # 5分钟

    # 内容类型映射
    STRAPI_CONTENT_TYPES: dict = {
        "project": "projects",
        "creative_idea": "creative-ideas",
        "script": "scripts",
        "storyboard": "storyboards",
        "media_asset": "media-assets",
        "final_video": "final-videos"
    }

    # 缓存配置
    STRAPI_CACHE_ENABLED: bool = os.getenv("STRAPI_CACHE_ENABLED", "true").lower() == "true"
    STRAPI_CACHE_TTL: int = int(os.getenv("STRAPI_CACHE_TTL", "300"))  # 5分钟

    # 超时和重试配置
    STRAPI_REQUEST_TIMEOUT: int = int(os.getenv("STRAPI_REQUEST_TIMEOUT", "30"))
    STRAPI_MAX_RETRIES: int = int(os.getenv("STRAPI_MAX_RETRIES", "3"))
    STRAPI_RETRY_DELAY: float = float(os.getenv("STRAPI_RETRY_DELAY", "1.0"))

    # Webhook配置
    STRAPI_WEBHOOK_REGISTER: bool = os.getenv("STRAPI_WEBHOOK_REGISTER", "true").lower() == "true"
    STRAPI_WEBHOOK_URL: str = os.getenv("STRAPI_WEBHOOK_URL", "http://localhost:8000/api/webhooks/strapi")

    # 本地化配置
    STRAPI_DEFAULT_LOCALE: str = os.getenv("STRAPI_DEFAULT_LOCALE", "zh-CN")
    STRAPI_SUPPORTED_LOCALES: list = os.getenv("STRAPI_SUPPORTED_LOCALES", "zh-CN,en-US").split(",")

    # 内容验证配置
    STRAPI_CONTENT_VALIDATION: bool = os.getenv("STRAPI_CONTENT_VALIDATION", "true").lower() == "true"
    STRAPI_MAX_CONTENT_LENGTH: int = int(os.getenv("STRAPI_MAX_CONTENT_LENGTH", "50000"))

    # 文件上传配置
    STRAPI_MAX_FILE_SIZE: int = int(os.getenv("STRAPI_MAX_FILE_SIZE", "104857600"))  # 100MB
    STRAPI_ALLOWED_FILE_TYPES: list = os.getenv("STRAPI_ALLOWED_FILE_TYPES",
        "jpg,jpeg,png,gif,webp,mp4,mov,avi,mp3,wav,pdf,doc,docx").split(",")

    @validator("STRAPI_URL")
    def validate_strapi_url(cls, v):
        """验证Strapi URL格式"""
        if not v.startswith(("http://", "https://")):
            raise ValueError("STRAPI_URL必须以http://或https://开头")
        return v.rstrip("/")

    @validator("STRAPI_API_TOKEN")
    def validate_api_token(cls, v, values):
        """验证API令牌"""
        sync_enabled = values.get('STRAPI_SYNC_ENABLED', False)
        if not v and sync_enabled:
            raise ValueError("启用Strapi同步时必须提供STRAPI_API_TOKEN")
        return v

    @validator("STRAPI_SUPPORTED_LOCALES")
    def validate_locales(cls, v):
        """验证本地化设置"""
        valid_locales = ["zh-CN", "zh-TW", "en-US", "en-GB", "ja-JP", "ko-KR"]
        for locale in v:
            if locale not in valid_locales:
                raise ValueError(f"不支持的本地化设置: {locale}")
        return v

    def get_content_type_endpoint(self, content_type: str) -> str:
        """获取内容类型的API端点"""
        return self.STRAPI_CONTENT_TYPES.get(content_type, content_type)

    def is_sync_enabled_for_type(self, content_type: str) -> bool:
        """检查内容类型是否启用同步"""
        # 可以在这里添加更复杂的逻辑
        return self.STRAPI_SYNC_ENABLED and self.STRAPI_AUTO_SYNC

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# 创建全局配置实例
strapi_config = StrapiConfig()


def get_strapi_config() -> StrapiConfig:
    """获取Strapi配置"""
    return strapi_config


def validate_strapi_connection() -> bool:
    """验证Strapi连接配置"""
    try:
        config = get_strapi_config()

        # 检查必需配置
        if not config.STRAPI_URL:
            raise ValueError("STRAPI_URL未配置")

        if config.STRAPI_SYNC_ENABLED and not config.STRAPI_API_TOKEN:
            raise ValueError("启用Strapi同步时STRAPI_API_TOKEN为必需")

        # 检查URL格式
        if not config.STRAPI_URL.startswith(("http://", "https://")):
            raise ValueError("STRAPI_URL格式无效")

        logger.info("✅ Strapi配置验证通过")
        return True

    except Exception as e:
        logger.error(f"❌ Strapi配置验证失败: {str(e)}")
        return False


# 配置验证器
async def validate_strapi_setup():
    """异步验证Strapi设置"""
    try:
        from app.services.strapi_service import get_strapi_service

        strapi_service = await get_strapi_service()
        health_status = await strapi_service.health_check()

        if health_status["status"] == "healthy":
            logger.info("✅ Strapi服务连接正常")
            return True
        else:
            logger.warning(f"⚠️ Strapi服务连接异常: {health_status.get('error', 'Unknown error')}")
            return False

    except Exception as e:
        logger.error(f"❌ Strapi服务验证失败: {str(e)}")
        return False


logger.info("✅ Strapi配置模块加载完成")