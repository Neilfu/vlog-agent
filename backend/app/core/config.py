"""
配置管理模块
Configuration Management Module

管理中国AI智能短视频创作系统的所有配置
Manages all configurations for the Chinese AI Intelligent Short Video Creation System
"""

from pydantic_settings import BaseSettings
from typing import List, Optional
import os
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """应用配置类"""

    # 基础配置
    APP_NAME: str = "中国AI智能短视频创作系统"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() in ["true", "1", "yes", "on"]
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))

    # 数据库配置
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://user:password@localhost:5432/video_creator"
    )
    DATABASE_POOL_SIZE: int = int(os.getenv("DATABASE_POOL_SIZE", "20"))
    DATABASE_MAX_OVERFLOW: int = int(os.getenv("DATABASE_MAX_OVERFLOW", "30"))

    # Redis配置
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    REDIS_POOL_SIZE: int = int(os.getenv("REDIS_POOL_SIZE", "10"))

    # JWT配置
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_EXPIRATION_MINUTES: int = int(os.getenv("JWT_EXPIRATION_MINUTES", "1440"))
    JWT_REFRESH_EXPIRATION_DAYS: int = int(os.getenv("JWT_REFRESH_EXPIRATION_DAYS", "7"))

    # CORS配置 - 针对中国环境优化
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "https://your-domain.com",
        "https://www.your-domain.com",
        # 中国常用域名
        "https://*.aliyuncs.com",
        "https://*.volcengine.com",
    ]

    # AI服务配置 - 中国AI模型
    ## DeepSeek配置
    DEEPSEEK_API_KEY: str = os.getenv("DEEPSEEK_API_KEY", "")
    DEEPSEEK_BASE_URL: str = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
    DEEPSEEK_MODEL: str = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
    DEEPSEEK_MAX_TOKENS: int = int(os.getenv("DEEPSEEK_MAX_TOKENS", "4000"))
    DEEPSEEK_TEMPERATURE: float = float(os.getenv("DEEPSEEK_TEMPERATURE", "0.7"))

    ## 即梦大模型配置 (火山引擎)
    VOLC_ACCESS_KEY: str = os.getenv("VOLC_ACCESS_KEY", "")
    VOLC_SECRET_KEY: str = os.getenv("VOLC_SECRET_KEY", "")
    VOLC_REGION: str = os.getenv("VOLC_REGION", "cn-north-1")
    JIMENG_BASE_URL: str = os.getenv("JIMENG_BASE_URL", "https://open-api.dreamina.com/v1")

    ## AutoGen配置
    AUTOGEN_MODEL: str = os.getenv("AUTOGEN_MODEL", "gpt-4")
    AUTOGEN_TEMPERATURE: float = float(os.getenv("AUTOGEN_TEMPERATURE", "0.7"))

    # 文件存储配置 (阿里云OSS推荐)
    OSS_BUCKET: str = os.getenv("OSS_BUCKET", "your-bucket")
    OSS_REGION: str = os.getenv("OSS_REGION", "cn-beijing")
    OSS_ACCESS_KEY: str = os.getenv("OSS_ACCESS_KEY", "")
    OSS_SECRET_KEY: str = os.getenv("OSS_SECRET_KEY", "")
    OSS_ENDPOINT: str = os.getenv("OSS_ENDPOINT", f"https://{OSS_BUCKET}.oss-{OSS_REGION}.aliyuncs.com")

    # 微信配置
    WECHAT_APP_ID: str = os.getenv("WECHAT_APP_ID", "")
    WECHAT_APP_SECRET: str = os.getenv("WECHAT_APP_SECRET", "")
    WECHAT_REDIRECT_URI: str = os.getenv("WECHAT_REDIRECT_URI", "http://localhost:8000/api/v1/auth/wechat/callback")

    # 监控配置
    PROMETHEUS_ENABLED: bool = os.getenv("PROMETHEUS_ENABLED", "true").lower() == "true"
    PROMETHEUS_PORT: int = int(os.getenv("PROMETHEUS_PORT", "8001"))

    # 日志配置
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = os.getenv("LOG_FORMAT", "json")

    # 业务配置
    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", "524288000"))  # 500MB (500 * 1024 * 1024)
    ALLOWED_FILE_TYPES: List[str] = [
        "image/jpeg", "image/png", "image/webp", "image/gif",
        "video/mp4", "video/webm", "video/quicktime",
        "audio/mp3", "audio/wav", "audio/aac", "audio/m4a"
    ]

    # 缓存配置
    CACHE_TTL: int = int(os.getenv("CACHE_TTL", "3600"))  # 1小时
    SESSION_TTL: int = int(os.getenv("SESSION_TTL", "86400"))  # 24小时

    # 中国特定配置
    CHINA_CDN_ENABLED: bool = os.getenv("CHINA_CDN_ENABLED", "true").lower() == "true"
    CHINA_REGION_OPTIMIZATION: bool = os.getenv("CHINA_REGION_OPTIMIZATION", "true").lower() == "true"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# 创建全局配置实例
settings = Settings()

# 验证关键配置
def validate_settings():
    """验证关键配置项"""
    required_vars = [
        "JWT_SECRET_KEY",
        "DEEPSEEK_API_KEY",
        "VOLC_ACCESS_KEY",
        "VOLC_SECRET_KEY",
    ]

    missing_vars = []
    for var in required_vars:
        if not getattr(settings, var):
            missing_vars.append(var)

    if missing_vars:
        raise ValueError(f"缺少必需的环境变量: {', '.join(missing_vars)}")


# 在应用启动时验证配置
try:
    validate_settings()
except ValueError as e:
    import warnings
    warnings.warn(f"配置验证警告: {e}")

logger.info("✅ 配置加载完成 - 中国AI智能短视频创作系统")