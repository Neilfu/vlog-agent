"""
测试配置和夹具
Test Configuration and Fixtures

提供测试环境配置和共享测试夹具
Provides test environment configuration and shared test fixtures
"""

import pytest
import asyncio
from typing import AsyncGenerator, Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.core.database import Base, get_db
from app.core.config import settings

# 测试数据库配置
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    """覆盖数据库依赖"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

@pytest.fixture(scope="function")
def db_session():
    """创建测试数据库会话"""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db_session) -> Generator[TestClient, None, None]:
    """创建测试客户端"""
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """创建事件循环"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def sample_project_data():
    """示例项目数据"""
    return {
        "name": "测试项目",
        "description": "这是一个测试项目",
        "project_type": "advertisement",
        "target_platform": "douyin",
        "target_audience": "年轻用户群体",
        "cultural_context": "中国文化背景",
        "business_input": {
            "product_name": "测试产品",
            "key_messages": ["消息1", "消息2"],
            "competitors": ["竞品1", "竞品2"]
        },
        "technical_specs": {
            "duration": 60,
            "resolution": "1080p",
            "aspect_ratio": "16:9"
        }
    }

@pytest.fixture
def sample_concept_request():
    """示例创意概念请求数据"""
    return {
        "project_id": "test-project-123",
        "prompt": "为科技产品创作创新广告",
        "cultural_context": "中国年轻人追求科技创新",
        "platform_target": "douyin",
        "temperature": 0.7,
        "max_tokens": 1000
    }

@pytest.fixture
def sample_script_request():
    """示例剧本请求数据"""
    return {
        "project_id": "test-project-123",
        "concept_id": "test-concept-456",
        "tone": "casual",
        "target_age_group": "18-25岁年轻人",
        "cultural_references": ["科技", "创新", "未来"],
        "ai_model": "deepseek-chat"
    }

@pytest.fixture
def sample_storyboard_request():
    """示例分镜请求数据"""
    return {
        "project_id": "test-project-123",
        "script_scene_ids": ["scene-1", "scene-2", "scene-3"],
        "resolution": "1024x1024",
        "style": "现代简约风格",
        "color_palette": ["蓝色", "白色", "灰色"],
        "ai_model": "jimeng-4.0"
    }

@pytest.fixture
def sample_video_request():
    """示例视频请求数据"""
    return {
        "project_id": "test-project-123",
        "storyboard_ids": ["storyboard-1", "storyboard-2"],
        "duration": 6,
        "resolution": "1080p",
        "frame_rate": 24,
        "ai_model": "jimeng-video-3.0"
    }

@pytest.fixture
def mock_deepseek_response():
    """模拟DeepSeek API响应"""
    return {
        "choices": [{
            "message": {
                "content": """创意概念：智能科技，点亮未来

核心创意主题："科技让生活更智能"
情感共鸣点：年轻人对科技创新的渴望和追求
视觉风格建议：现代简约，科技感强，色彩鲜明
传播策略要点：利用热门科技话题，引发用户讨论和分享"""
            }
        }]
    }

@pytest.fixture
def mock_jimeng_image_response():
    """模拟即梦图像生成响应"""
    return {
        "data": [{
            "url": "https://example.com/generated-image.jpg",
            "id": "img-123456",
            "revised_prompt": "现代简约风格的科技产品展示图"
        }]
    }

@pytest.fixture
def mock_jimeng_video_response():
    """模拟即梦视频生成响应"""
    return {
        "data": {
            "url": "https://example.com/generated-video.mp4",
            "id": "video-123456",
            "thumbnail_url": "https://example.com/video-thumbnail.jpg",
            "duration": 6
        }
    }