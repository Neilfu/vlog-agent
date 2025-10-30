# 中国AI短视频创作系统 - Strapi CMS

## 项目概述

本项目是为中国AI智能短视频创作系统提供的内容管理服务，基于Strapi CMS构建。它提供了完整的视频创作工作流内容管理功能，支持双语（中文/英文）内容管理。

## 主要功能

### 内容类型

1. **项目 (Projects)**
   - 视频创作项目的基本信息管理
   - 支持项目状态跟踪和进度管理
   - 业务输入和技术规格存储

2. **创意想法 (Creative Ideas)**
   - AI生成的创意概念管理
   - 支持创意分类和评分
   - 目标受众和平台定位

3. **脚本 (Scripts)**
   - 视频脚本内容管理
   - 场景和角色信息管理
   - 支持多语言和本地化

4. **故事板 (Storyboards)**
   - 视觉故事板管理
   - 帧序列和布局信息
   - 样式和视觉风格定义

5. **媒体资源 (Media Assets)**
   - 图片、视频、音频文件管理
   - 元数据和文件信息存储
   - 支持AI生成资源标识

6. **最终视频 (Final Videos)**
   - 渲染完成的视频管理
   - 发布状态和平台优化设置
   - 性能指标和统计数据

## 技术架构

### 核心技术栈
- **Strapi CMS**: 4.15.4
- **Node.js**: 18.x
- **PostgreSQL**: 15.x
- **Redis**: 7.x
- **Nginx**: 反向代理和负载均衡

### 插件和扩展
- **国际化插件 (i18n)**: 支持双语内容管理
- **用户权限插件**: 细粒度权限控制
- **中文本地化插件**: 优化中文内容管理

## 快速开始

### 环境要求
- Docker 20.10+
- Docker Compose 2.0+
- Node.js 18.x (本地开发)

### 使用Docker部署

1. **克隆项目**
   ```bash
   cd strapi-cms
   ```

2. **配置环境变量**
   ```bash
   cp .env.example .env
   # 编辑 .env 文件，设置必要的环境变量
   ```

3. **启动服务**
   ```bash
   docker-compose up -d
   ```

4. **访问管理界面**
   - Strapi Admin: http://localhost:1337/admin
   - API文档: http://localhost:1337/documentation

### 本地开发

1. **安装依赖**
   ```bash
   npm install
   ```

2. **配置数据库**
   ```bash
   # 创建PostgreSQL数据库
   createdb strapi_cms
   ```

3. **启动开发服务器**
   ```bash
   npm run develop
   ```

## 环境配置

### 必需环境变量

```env
# 数据库配置
DATABASE_HOST=postgres
DATABASE_PORT=5432
DATABASE_NAME=strapi_cms
DATABASE_USERNAME=strapi
DATABASE_PASSWORD=your_secure_password

# JWT密钥
JWT_SECRET=your_jwt_secret_key
ADMIN_JWT_SECRET=your_admin_jwt_secret_key
APP_KEYS=app-key-1,app-key-2,app-key-3,app-key-4
API_TOKEN_SALT=your_api_token_salt
TRANSFER_TOKEN_SALT=your_transfer_token_salt

# Webhook密钥
WEBHOOK_SECRET=your_webhook_secret

# 后端服务URL
STRAPI_BACKEND_URL=http://backend:8000
```

### 可选环境变量

```env
# 国际化配置
STRAPI_DEFAULT_LOCALE=zh-CN
STRAPI_SUPPORTED_LOCALES=zh-CN,en-US

# 性能优化
DATABASE_POOL_MIN=2
DATABASE_POOL_MAX=10

# 安全配置
DATABASE_SSL=false
IS_PROXY=false
```

## API使用

### 认证

所有API请求都需要在Header中包含认证信息：

```http
Authorization: Bearer YOUR_API_TOKEN
```

### 内容管理API

#### 创建项目
```http
POST /api/projects
Content-Type: application/json

{
  "data": {
    "title": "短视频营销项目",
    "description": "抖音平台产品推广视频",
    "status": "draft",
    "businessInput": {
      "product": "智能手表",
      "target_audience": "年轻消费者",
      "platform": "douyin"
    },
    "technicalSpecs": {
      "duration": 30,
      "resolution": "1080p",
      "aspect_ratio": "9:16"
    },
    "locale": "zh-CN"
  }
}
```

#### 获取内容列表
```http
GET /api/projects?populate=*&sort=createdAt:desc
```

#### 更新内容
```http
PUT /api/projects/1
Content-Type: application/json

{
  "data": {
    "status": "published"
  }
}
```

### Webhook集成

Strapi支持webhook功能，可以在内容变更时通知外部系统：

#### 注册Webhook
```http
POST /api/webhooks
Content-Type: application/json

{
  "data": {
    "name": "AI Video System Webhook",
    "url": "https://your-backend.com/api/v1/strapi/webhooks",
    "events": ["entry.create", "entry.update", "entry.delete"],
    "headers": {
      "X-Webhook-Secret": "your-webhook-secret"
    }
  }
}
```

#### Webhook载荷格式
```json
{
  "event": "entry.create",
  "model": "project",
  "entry": {
    "id": 1,
    "title": "短视频营销项目",
    "status": "published"
  },
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

## 内容同步

### 与主系统同步

主系统（后端API）提供了完整的Strapi集成服务：

#### 同步项目到Strapi
```http
POST /api/v1/strapi/projects/sync
Content-Type: application/json

{
  "content_type": "project",
  "direction": "to_strapi",
  "entity_id": "project_123"
}
```

#### 从Strapi同步内容
```http
POST /api/v1/strapi/sync/bidirectional
Content-Type: application/json

{
  "content_type": "project",
  "direction": "from_strapi",
  "entity_id": "1"
}
```

## 数据库结构

### 核心表结构

- **projects**: 项目基本信息
- **creative_ideas**: 创意想法内容
- **scripts**: 脚本内容
- **storyboards**: 故事板内容
- **media_assets**: 媒体资源信息
- **final_videos**: 最终视频信息

### 关系设计

```
projects (1) ←→ (N) creative_ideas
projects (1) ←→ (N) scripts
projects (1) ←→ (N) storyboards
projects (1) ←→ (N) media_assets
projects (1) ←→ (N) final_videos
```

## 性能优化

### 数据库优化
- 使用PostgreSQL 15.x版本
- 配置适当的连接池大小
- 定期执行VACUUM和ANALYZE

### 缓存策略
- Redis缓存热点数据
- CDN缓存静态资源
- 浏览器缓存控制

### 查询优化
- 使用populate参数控制关联数据加载
- 合理使用分页和过滤
- 避免N+1查询问题

## 安全配置

### 认证和授权
- JWT Token认证
- 细粒度权限控制
- API速率限制

### 数据安全
- 数据库连接加密
- 敏感数据加密存储
- 定期备份策略

### 网络安全
- Nginx反向代理
- SSL/TLS加密
- 安全头部设置

## 监控和日志

### 健康检查
```bash
curl http://localhost:1337/_health
```

### 日志管理
- 应用日志: `/app/logs`
- 访问日志: Nginx访问日志
- 错误日志: 详细的错误信息记录

## 故障排除

### 常见问题

1. **数据库连接失败**
   - 检查数据库配置
   - 确认网络连通性
   - 验证用户权限

2. **媒体上传失败**
   - 检查文件大小限制
   - 验证存储权限
   - 确认文件类型支持

3. **API请求超时**
   - 检查网络连接
   - 优化查询性能
   - 调整超时设置

### 调试模式

开发模式下启用详细日志：
```bash
npm run develop
```

## 升级和维护

### 版本升级
1. 备份数据库和上传文件
2. 更新package.json依赖版本
3. 执行数据库迁移
4. 测试功能完整性

### 定期维护
- 数据库清理和优化
- 日志文件轮转
- 安全补丁更新

## 支持和文档

### 官方文档
- [Strapi官方文档](https://docs.strapi.io/)
- [Strapi API文档](http://localhost:1337/documentation)

### 开发资源
- [Strapi插件开发](https://docs.strapi.io/developer-docs/latest/development/plugins-development.html)
- [内容类型构建器](https://docs.strapi.io/user-docs/latest/content-type-builder/introduction-to-content-type-builder.html)

## 许可证

本项目采用MIT许可证 - 详见 [LICENSE](../LICENSE) 文件。

## 贡献指南

欢迎提交Issue和Pull Request来改进项目。请遵循以下规范：

1. 提交前运行测试
2. 遵循代码风格指南
3. 更新相关文档
4. 添加适当的注释

## 联系方式

如有问题或建议，请联系开发团队。

---

**注意**: 本README文档会随项目更新而更新，建议定期查看最新版本。