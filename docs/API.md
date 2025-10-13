# API文档 / API Documentation

## 🚀 概述 / Overview

中国AI智能短视频创作系统提供RESTful API接口，支持中文视频内容的创作、管理和优化。所有API端点都支持双语（中文/英文）响应。

The Chinese AI Intelligent Short Video Creation System provides RESTful API interfaces supporting Chinese video content creation, management, and optimization. All API endpoints support bilingual (Chinese/English) responses.

---

## 📋 目录 / Table of Contents

- [基础信息 / Basic Information](#基础信息--basic-information)
- [认证 / Authentication](#认证--authentication)
- [用户管理 / User Management](#用户管理--user-management)
- [项目管理 / Project Management](#项目管理--project-management)
- [AI服务 / AI Services](#ai服务--ai-services)
- [媒体资源 / Media Assets](#媒体资源--media-assets)
- [错误处理 / Error Handling](#错误处理--error-handling)
- [速率限制 / Rate Limiting](#速率限制--rate-limiting)

---

## 🔧 基础信息 / Basic Information

### 基础URL / Base URL
```
开发环境 / Development: http://localhost:8000
生产环境 / Production: https://api.chinese-ai-video.com
```

### API版本 / API Version
```
当前版本 / Current Version: v1
版本前缀 / Version Prefix: /api/v1
```

### 内容类型 / Content Type
```
请求格式 / Request Format: application/json
响应格式 / Response Format: application/json
字符编码 / Character Encoding: UTF-8
```

---

## 🔐 认证 / Authentication

### JWT令牌 / JWT Token

系统使用JWT（JSON Web Token）进行用户认证。

The system uses JWT (JSON Web Token) for user authentication.

#### 获取令牌 / Get Token
```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "username": "用户名",
  "password": "密码"
}
```

#### 响应示例 / Response Example
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 1440,
  "user": {
    "id": "user_123",
    "username": "用户名",
    "email": "user@example.com",
    "role": "creator"
  }
}
```

#### 使用令牌 / Using Token
```http
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

---

## 👥 用户管理 / User Management

### 用户注册 / User Registration
```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "username": "新用户名",
  "email": "user@example.com",
  "password": "secure_password",
  "phone": "+86-138-0013-8000",
  "preferences": {
    "language": "zh-CN",
    "timezone": "Asia/Shanghai"
  }
}
```

### 获取用户资料 / Get User Profile
```http
GET /api/v1/users/profile
Authorization: Bearer {token}
```

### 更新用户资料 / Update User Profile
```http
PUT /api/v1/users/profile
Authorization: Bearer {token}
Content-Type: application/json

{
  "username": "新用户名",
  "avatar": "https://example.com/avatar.jpg",
  "preferences": {
    "language": "zh-CN",
    "notifications": {
      "email": true,
      "sms": false
    }
  }
}
```

---

## 📁 项目管理 / Project Management

### 创建项目 / Create Project
```http
POST /api/v1/projects
Authorization: Bearer {token}
Content-Type: application/json

{
  "title": "春节家庭温馨短片",
  "description": "展现中国春节家庭团聚的温暖氛围",
  "target_platform": "douyin",
  "business_input": {
    "target_audience": "年轻家庭群体",
    "cultural_context": "中国春节传统文化和现代家庭观念",
    "key_message": "家的温暖，年的味道",
    "call_to_action": "关注账号，分享家庭故事"
  },
  "technical_specs": {
    "duration": 60,
    "resolution": "1080p",
    "aspect_ratio": "9:16"
  }
}
```

#### 响应示例 / Response Example
```json
{
  "id": "proj_123456",
  "title": "春节家庭温馨短片",
  "status": "draft",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z",
  "creator_id": "user_123",
  "business_input": {
    "target_audience": "年轻家庭群体",
    "cultural_context": "中国春节传统文化和现代家庭观念",
    "key_message": "家的温暖，年的味道"
  }
}
```

### 获取项目列表 / Get Project List
```http
GET /api/v1/projects?status=draft&page=1&limit=10
Authorization: Bearer {token}
```

### 获取项目详情 / Get Project Details
```http
GET /api/v1/projects/{project_id}
Authorization: Bearer {token}
```

### 更新项目 / Update Project
```http
PUT /api/v1/projects/{project_id}
Authorization: Bearer {token}
Content-Type: application/json

{
  "title": "更新的项目标题",
  "status": "in_progress",
  "progress": {
    "concept_generation": "completed",
    "script_writing": "in_progress",
    "completion_percentage": 45
  }
}
```

### 删除项目 / Delete Project
```http
DELETE /api/v1/projects/{project_id}
Authorization: Bearer {token}
```

---

## 🤖 AI服务 / AI Services

### 生成创意概念 / Generate Creative Concept
```http
POST /api/v1/ai/generate-concept
Authorization: Bearer {token}
Content-Type: application/json

{
  "prompt": "创建一个关于中秋节的短视频创意",
  "cultural_context": "中国传统中秋节，家人团聚赏月吃月饼",
  "platform_target": "xiaohongshu",
  "target_age_group": "25-35岁女性",
  "tone": "warm",
  "duration": 45,
  "temperature": 0.7
}
```

#### 响应示例 / Response Example
```json
{
  "concepts": [
    {
      "id": "concept_001",
      "title": "月圆人团圆",
      "description": "通过三代同堂赏月的温馨场景，展现中秋团圆主题",
      "key_elements": ["家庭聚会", "赏月", "月饼", "传统文化"],
      "visual_style": "温暖柔和的色调，突出家庭温馨氛围",
      "narrative_arc": "开场-铺垫-高潮-结尾",
      "estimated_engagement": "高",
      "cultural_relevance": "强",
      "platform_optimization": {
        "xiaohongshu": {
          "hashtags": ["#中秋节", "#家庭团聚", "#传统文化"],
          "posting_time": "晚上8-10点",
          "content_format": "图文+短视频"
        }
      }
    }
  ],
  "generation_time": 2.3,
  "model_used": "deepseek-chat",
  "cost_estimate": 0.015
}
```

### 生成剧本 / Generate Script
```http
POST /api/v1/ai/generate-script
Authorization: Bearer {token}
Content-Type: application/json

{
  "concept": "月圆人团圆",
  "cultural_context": "中秋传统文化",
  "target_platform": "xiaohongshu",
  "duration": 45,
  "tone": "warm",
  "target_audience": "25-35岁女性"
}
```

### 生成分镜图像 / Generate Storyboard Images
```http
POST /api/v1/ai/generate-storyboard
Authorization: Bearer {token}
Content-Type: application/json

{
  "scenes": [
    {
      "description": "三代同堂在庭院中摆好桌椅，准备赏月",
      "emotional_tone": "温馨期待",
      "visual_style": "温暖柔和"
    },
    {
      "description": "月亮升起，全家人抬头赏月，脸上洋溢着幸福笑容",
      "emotional_tone": "幸福满足",
      "visual_style": "温暖明亮"
    }
  ],
  "style": "现代简约",
  "resolution": "1024x1024",
  "color_palette": ["暖黄色", "淡蓝色", "米白色"]
}
```

### 生成视频 / Generate Video
```http
POST /api/v1/ai/generate-video
Authorization: Bearer {token}
Content-Type: application/json

{
  "image_urls": [
    "https://example.com/storyboard1.jpg",
    "https://example.com/storyboard2.jpg"
  ],
  "duration": 6,
  "resolution": "1080p",
  "frame_rate": 24,
  "transition_style": "smooth",
  "music_style": "traditional_chinese",
  "voiceover_text": "中秋佳节，月圆人团圆..."
}
```

### 内容优化 / Content Optimization
```http
POST /api/v1/ai/optimize-content
Authorization: Bearer {token}
Content-Type: application/json

{
  "content": "中秋佳节，月圆人团圆。在这个特别的日子里...",
  "optimization_type": "engagement",
  "platform": "douyin",
  "target_metrics": ["view_count", "engagement_rate", "share_count"]
}
```

---

## 📁 媒体资源 / Media Assets

### 上传文件 / Upload File
```http
POST /api/v1/assets/upload
Authorization: Bearer {token}
Content-Type: multipart/form-data

file: (binary file data)
name: "中秋赏月图.jpg"
type: "image"
description: "中秋赏月场景图片"
project_id: "proj_123456"
```

### 获取资源列表 / Get Asset List
```http
GET /api/v1/assets?type=image&project_id=proj_123456
Authorization: Bearer {token}
```

### 获取资源详情 / Get Asset Details
```http
GET /api/v1/assets/{asset_id}
Authorization: Bearer {token}
```

### 删除资源 / Delete Asset
```http
DELETE /api/v1/assets/{asset_id}
Authorization: Bearer {token}
```

---

## ❌ 错误处理 / Error Handling

### 错误响应格式 / Error Response Format
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "请求数据验证失败",
    "details": {
      "field": "title",
      "message": "标题不能为空"
    }
  },
  "timestamp": "2024-01-15T10:30:00Z",
  "path": "/api/v1/projects",
  "method": "POST"
}
```

### 常见错误代码 / Common Error Codes

| 代码 / Code | HTTP状态 / Status | 描述 / Description |
|-------------|-------------------|-------------------|
| `VALIDATION_ERROR` | 400 | 请求数据验证失败 / Request validation failed |
| `UNAUTHORIZED` | 401 | 未授权访问 / Unauthorized access |
| `FORBIDDEN` | 403 | 权限不足 / Insufficient permissions |
| `NOT_FOUND` | 404 | 资源不存在 / Resource not found |
| `CONFLICT` | 409 | 资源冲突 / Resource conflict |
| `RATE_LIMIT_EXCEEDED` | 429 | 速率限制超出 / Rate limit exceeded |
| `INTERNAL_ERROR` | 500 | 服务器内部错误 / Internal server error |
| `AI_SERVICE_ERROR` | 503 | AI服务不可用 / AI service unavailable |

---

## ⚡ 速率限制 / Rate Limiting

### 限制规则 / Rate Limit Rules

| 端点类型 / Endpoint Type | 限制 / Limit | 时间窗口 / Time Window |
|-------------------------|--------------|----------------------|
| 认证端点 / Auth endpoints | 10 requests | 1 minute |
| 普通API / General APIs | 100 requests | 1 minute |
| AI生成服务 / AI generation | 20 requests | 1 minute |
| 文件上传 / File uploads | 5 requests | 1 minute |

### 速率限制头信息 / Rate Limit Headers
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1642246200
X-RateLimit-Reset-After: 30
```

---

## 📊 响应格式 / Response Format

### 成功响应 / Success Response
```json
{
  "success": true,
  "data": {
    // 响应数据 / Response data
  },
  "meta": {
    "timestamp": "2024-01-15T10:30:00Z",
    "version": "v1",
    "request_id": "req_123456"
  }
}
```

### 分页响应 / Paginated Response
```json
{
  "success": true,
  "data": [
    // 数据数组 / Data array
  ],
  "meta": {
    "pagination": {
      "page": 1,
      "limit": 10,
      "total": 100,
      "pages": 10,
      "has_next": true,
      "has_prev": false
    }
  }
}
```

---

## 🔧 SDK和工具 / SDKs and Tools

### 官方SDK / Official SDKs

我们正在开发以下语言的官方SDK：

We are developing official SDKs for the following languages:

- **Python**: `pip install chinese-ai-video`
- **JavaScript/Node.js**: `npm install chinese-ai-video-sdk`
- **Go**: `go get github.com/chinese-ai-video/go-sdk`

### API测试工具 / API Testing Tools

- **Postman**: 导入我们的[Postman集合](https://github.com/your-repo/postman-collection)
- **curl**: 命令行测试
- **Swagger UI**: 交互式API文档

---

## 📞 支持和帮助 / Support and Help

### 获取帮助 / Getting Help

- **API文档**: 查看完整的[API参考](#)
- **示例代码**: 浏览[示例项目](https://github.com/your-repo/examples)
- **社区支持**: 加入我们的[Discord服务器](https://discord.gg/your-server)
- **问题报告**: 在[GitHub Issues](https://github.com/your-repo/issues)提交问题

### 联系支持 / Contact Support

- **技术支持**: tech-support@chinese-ai-video.com
- **API支持**: api-support@chinese-ai-video.com
- **商务咨询**: business@chinese-ai-video.com

---

## 🔄 版本历史 / Version History

| 版本 / Version | 日期 / Date | 主要变更 / Major Changes |
|----------------|-------------|------------------------|
| v1.0.0 | 2024-10-13 | 初始版本发布 / Initial release |
| v1.0.1 | 2024-10-14 | 修复认证错误 / Fixed auth errors |

---

## 🚀 即将推出 / Coming Soon

- **GraphQL API**: 更灵活的查询选项
- **Webhook支持**: 实时事件通知
- **批量操作**: 批量处理多个资源
- **高级分析**: 详细的API使用分析

---

**有问题？** 请查看我们的[FAQ](#)或在[GitHub Issues](https://github.com/your-repo/issues)提问。

**有问题？** 请查看我们的[FAQ](#)或在[GitHub Issues](https://github.com/your-repo/issues)提问。

---

*最后更新: 2024年10月13日* / *Last updated: October 13, 2024*