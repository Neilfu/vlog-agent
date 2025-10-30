# Strapi CMS 集成指南

## 概述

本指南详细说明如何将Strapi CMS集成到中国AI智能短视频创作系统中，实现完整的内容管理功能。

## 集成架构

```
┌─────────────────────────────────────────────────────────────┐
│                    前端应用 (React/Next.js)                 │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│              FastAPI 后端服务 (端口: 8000)                  │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │              Strapi 集成服务层                           │ │
│  │  • 内容同步管理                                          │ │
│  │  • Webhook 处理                                          │ │
│  │  • 数据转换                                              │ │
│  │  • 错误处理                                              │ │
│  └─────────────────────────┬───────────────────────────────┘ │
│                            │                               │
│  ┌─────────────────────────▼───────────────────────────────┐ │
│  │              数据库层 (PostgreSQL)                       │ │
│  │  • 本地项目数据                                          │ │
│  │  • 用户权限管理                                          │ │
│  │  • 工作流状态                                            │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────┬───────────────────────────────┘
                              │
┌─────────────────────────────▼───────────────────────────────┐
│              Strapi CMS (端口: 1337)                       │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │              内容类型定义                                │ │
│  │  • Projects (项目)                                       │ │
│  │  • Creative Ideas (创意想法)                             │ │
│  │  • Scripts (脚本)                                        │ │
│  │  • Storyboards (故事板)                                  │ │
│  │  • Media Assets (媒体资源)                               │ │
│  │  • Final Videos (最终视频)                               │ │
│  └─────────────────────────┬───────────────────────────────┘ │
│                            │                               │
│  ┌─────────────────────────▼───────────────────────────────┐ │
│  │              PostgreSQL 数据库                           │ │
│  │  • 内容管理数据                                          │ │
│  │  • 国际化内容                                            │ │
│  │  • 媒体文件元数据                                        │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## 配置步骤

### 1. 环境配置

在 `.env` 文件中添加 Strapi 相关配置：

```env
# Strapi 连接配置
STRAPI_URL=http://localhost:1337
STRAPI_API_TOKEN=your_strapi_api_token
STRAPI_WEBHOOK_SECRET=your_webhook_secret_key

# 同步配置
STRAPI_SYNC_ENABLED=true
STRAPI_AUTO_SYNC=true
STRAPI_SYNC_INTERVAL=300
STRAPI_REQUEST_TIMEOUT=30
STRAPI_MAX_RETRIES=3
STRAPI_RETRY_DELAY=1.0

# 国际化配置
STRAPI_DEFAULT_LOCALE=zh-CN
STRAPI_SUPPORTED_LOCALES=zh-CN,en-US
```

### 2. 数据库迁移

运行数据库迁移以添加 Strapi ID 字段：

```bash
# 应用迁移
alembic upgrade head

# 检查迁移状态
alembic current
```

### 3. 启动服务

按照以下顺序启动服务：

```bash
# 1. 启动 Strapi CMS
cd strapi-cms
./deploy.sh

# 2. 启动后端服务
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 功能特性

### 内容同步

#### 双向同步
支持主系统与Strapi之间的双向内容同步：

- **主系统 → Strapi**: 创建或更新内容时自动同步
- **Strapi → 主系统**: 通过Webhook接收更新
- **双向同步**: 冲突检测和解决机制

#### 同步状态
每个实体都有同步状态跟踪：

```python
class SyncStatus(Enum):
    PENDING = "pending"          # 等待同步
    SYNCING = "syncing"          # 同步中
    SYNCED = "synced"            # 已同步
    FAILED = "failed"            # 同步失败
    CONFLICT = "conflict"        # 冲突待解决
```

### Webhook 集成

#### 支持的Webhook事件
```python
VALID_WEBHOOK_EVENTS = [
    "entry.create",      # 内容创建
    "entry.update",      # 内容更新
    "entry.delete",      # 内容删除
    "entry.publish",     # 内容发布
    "entry.unpublish",   # 内容取消发布
    "media.create",      # 媒体创建
    "media.update",      # 媒体更新
    "media.delete"       # 媒体删除
]
```

#### Webhook载荷格式
```json
{
  "event": "entry.create",
  "model": "project",
  "entry": {
    "id": 1,
    "attributes": {
      "title": "短视频营销项目",
      "description": "抖音平台产品推广",
      "status": "published",
      "createdAt": "2024-01-15T10:30:00.000Z",
      "updatedAt": "2024-01-15T10:30:00.000Z"
    }
  },
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

### 内容类型映射

#### 项目 (Project) 映射
```python
# 主系统 → Strapi 字段映射
PROJECT_FIELD_MAPPING = {
    "title": "title",
    "description": "description",
    "status": "status",
    "business_input": "businessInput",
    "technical_specs": "technicalSpecs",
    "priority": "priority",
    "deadline": "deadline",
    "budget": "budget",
    "tags": "tags",
    "metadata": "metadata"
}
```

#### 创意想法 (Creative Idea) 映射
```python
CREATIVE_IDEA_MAPPING = {
    "title": "title",
    "description": "description",
    "content": "content",
    "concept": "concept",
    "target_audience": "targetAudience",
    "platform": "platform",
    "tone": "tone",
    "style": "style",
    "duration": "duration"
}
```

## API 端点

### 健康检查
```http
GET /api/v1/strapi/health
```

**响应示例：**
```json
{
  "status": "healthy",
  "service": "strapi",
  "url": "http://localhost:1337",
  "checked_at": "2024-01-15T10:30:00.000Z"
}
```

### 项目同步

#### 同步项目到Strapi
```http
POST /api/v1/strapi/projects/sync
Content-Type: application/json

{
  "content_type": "project",
  "direction": "to_strapi",
  "entity_id": "123e4567-e89b-12d3-a456-426614174000"
}
```

#### 从Strapi获取项目
```http
GET /api/v1/strapi/projects/{strapi_project_id}?populate=*
```

#### 更新Strapi项目
```http
PUT /api/v1/strapi/projects/{strapi_project_id}
Content-Type: application/json

{
  "title": "更新后的项目标题",
  "status": "published"
}
```

### 内容管理

#### 获取内容列表
```http
GET /api/v1/strapi/content/projects?populate=*&page=1&page_size=20
```

#### 创建创意想法
```http
POST /api/v1/strapi/creative-ideas
Content-Type: application/json

{
  "title": "创意标题",
  "content": {
    "concept": "创新概念描述",
    "visual_style": "现代简约"
  },
  "ai_model": "deepseek-chat",
  "project_id": "1"
}
```

#### 创建脚本
```http
POST /api/v1/strapi/scripts
Content-Type: application/json

{
  "title": "产品推广脚本",
  "content": "欢迎来到我们的频道...",
  "duration": 60,
  "scenes": [
    {
      "scene_number": 1,
      "title": "开场介绍",
      "duration": 10,
      "description": "产品展示和介绍"
    }
  ],
  "project_id": "1"
}
```

### Webhook 管理

#### 注册Webhook
```http
POST /api/v1/strapi/register-webhook?webhook_url=https://your-backend.com/webhook&events=entry.create,entry.update
```

#### 处理Webhook
```http
POST /api/v1/strapi/webhooks/strapi
Content-Type: application/json
X-Strapi-Event: entry.create
X-Strapi-Signature: sha256=signature

{
  "event": "entry.create",
  "model": "project",
  "entry": {...},
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

## 错误处理

### 错误类型
```python
class StrapiIntegrationError(Exception):
    """Strapi集成基础错误"""
    pass

class SyncError(StrapiIntegrationError):
    """同步错误"""
    pass

class WebhookError(StrapiIntegrationError):
    """Webhook处理错误"""
    pass

class AuthenticationError(StrapiIntegrationError):
    """认证错误"""
    pass

class RateLimitError(StrapiIntegrationError):
    """API限流错误"""
    pass
```

### 错误响应格式
```json
{
  "error": {
    "code": "STRAPI_SYNC_FAILED",
    "message": "项目同步到Strapi失败",
    "details": {
      "entity_id": "123",
      "strapi_id": null,
      "error": "Connection timeout"
    },
    "timestamp": "2024-01-15T10:30:00.000Z"
  }
}
```

## 性能优化

### 批量同步
支持批量同步多个实体：

```python
async def batch_sync_to_strapi(entities: List[Dict], batch_size: int = 10):
    """批量同步到Strapi"""
    for i in range(0, len(entities), batch_size):
        batch = entities[i:i + batch_size]
        await asyncio.gather(*[
            sync_entity_to_strapi(entity)
            for entity in batch
        ])
```

### 缓存策略
```python
# Redis缓存配置
CACHE_TTL = {
    'strapi_content': 300,      # 5分钟
    'strapi_projects': 600,     # 10分钟
    'strapi_assets': 1800,      # 30分钟
}

# 缓存键命名规范
CACHE_KEY_PREFIX = 'strapi:'
CACHE_KEY_TEMPLATE = 'strapi:{content_type}:{entity_id}:{locale}'
```

### 限流控制
```python
# API限流配置
RATE_LIMIT = {
    'requests_per_second': 10,
    'burst_size': 20,
    'retry_after': 60  # 秒
}
```

## 监控和日志

### 监控指标
```python
# 关键监控指标
METRICS = {
    'strapi_requests_total': 'Total Strapi API requests',
    'strapi_requests_success': 'Successful Strapi API requests',
    'strapi_requests_error': 'Failed Strapi API requests',
    'strapi_sync_duration': 'Content sync duration',
    'strapi_webhook_processed': 'Webhooks processed count'
}
```

### 日志格式
```python
# 结构化日志格式
log_data = {
    "timestamp": datetime.utcnow().isoformat(),
    "level": "INFO",
    "service": "strapi_integration",
    "action": "sync_project",
    "entity_id": project_id,
    "strapi_id": strapi_id,
    "duration_ms": duration,
    "status": "success",
    "error": None
}
```

## 测试

### 单元测试
```python
# 测试Strapi服务
async def test_strapi_service():
    service = StrapiService()

    # 测试健康检查
    health = await service.health_check()
    assert health["status"] == "healthy"

    # 测试内容创建
    project_data = {"title": "Test Project"}
    result = await service.create_project(project_data)
    assert result["data"]["id"] is not None
```

### 集成测试
```python
# 测试端到端同步
async def test_sync_integration():
    # 创建测试项目
    project = await create_test_project()

    # 同步到Strapi
    strapi_id = await sync_project_to_strapi(project)
    assert strapi_id is not None

    # 验证同步结果
    strapi_project = await get_project_from_strapi(strapi_id)
    assert strapi_project["title"] == project.title
```

## 部署

### Docker 配置
```yaml
# docker-compose.yml
version: '3.8'
services:
  strapi:
    image: strapi/strapi
    environment:
      - DATABASE_CLIENT=postgres
      - DATABASE_HOST=postgres
      - DATABASE_PORT=5432
      - DATABASE_NAME=strapi_cms
    depends_on:
      - postgres
      - redis
    ports:
      - "1337:1337"

  postgres:
    image: postgres:15
    environment:
      - POSTGRES_DB=strapi_cms
      - POSTGRES_USER=strapi
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

### 环境变量
```bash
# 生产环境配置
STRAPI_URL=https://cms.yourdomain.com
STRAPI_API_TOKEN=your_production_token
STRAPI_WEBHOOK_SECRET=your_production_secret
STRAPI_SYNC_ENABLED=true
```

## 故障排除

### 常见问题

#### 1. 同步失败
```bash
# 检查Strapi服务状态
curl http://localhost:1337/_health

# 检查API Token
echo $STRAPI_API_TOKEN

# 查看错误日志
docker-compose logs strapi
```

#### 2. Webhook 未触发
```bash
# 检查Webhook配置
curl http://localhost:1337/api/webhooks

# 验证Webhook URL
curl -X POST https://your-webhook-url.com/test
```

#### 3. 数据库连接问题
```bash
# 检查数据库连接
docker-compose exec strapi npm run strapi console

# 查看数据库状态
docker-compose exec postgres pg_isready
```

### 性能问题

#### 高延迟
- 检查网络连接质量
- 优化查询参数和populate设置
- 启用Redis缓存

#### 内存使用过高
- 监控内存使用情况
- 优化Docker资源限制
- 调整数据库连接池大小

## 最佳实践

### 1. 数据一致性
- 使用事务确保数据一致性
- 实现幂等性操作
- 定期验证同步状态

### 2. 安全性
- 使用HTTPS进行所有通信
- 定期轮换API密钥
- 实施适当的访问控制

### 3. 可维护性
- 编写清晰的文档
- 实施适当的错误处理
- 使用结构化日志

### 4. 性能优化
- 实施适当的缓存策略
- 使用批量操作减少API调用
- 监控和优化查询性能

## 升级和维护

### 版本升级
1. 备份现有数据
2. 测试新版本兼容性
3. 逐步迁移生产环境
4. 验证功能完整性

### 定期维护
- 清理过期缓存
- 优化数据库性能
- 更新安全补丁
- 监控资源使用情况

## 支持和文档

### 相关资源
- [Strapi官方文档](https://docs.strapi.io/)
- [FastAPI文档](https://fastapi.tiangolo.com/)
- [项目GitHub仓库](https://github.com/your-repo)

### 获取帮助
- 提交GitHub Issue
- 查看项目Wiki
- 联系开发团队

---

**注意**: 本集成指南会随项目更新而更新，建议定期查看最新版本。"}