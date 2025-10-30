# Strapi Content Management Data Models
# Strapi内容管理数据模型

## 🎯 Overview / 概述

This document defines the data models for integrating Strapi as a headless CMS with the Chinese AI Video Creation System. The models are designed to support bilingual content management (Chinese/English) and optimize for Chinese social media platform requirements.

本文档定义了将Strapi作为无头CMS与中国AI视频创作系统集成的数据模型。这些模型专为支持双语内容管理（中文/英文）并针对中国社交媒体平台需求进行优化而设计。

## 📊 Content Types / 内容类型

### 1. Video Content / 视频内容
**Purpose**: Store video metadata, descriptions, and platform-specific optimizations
**目的**: 存储视频元数据、描述和平台特定优化

```json
{
  "kind": "collectionType",
  "collectionName": "video_contents",
  "info": {
    "singularName": "video-content",
    "pluralName": "video-contents",
    "displayName": "Video Content"
  },
  "options": {
    "draftAndPublish": true,
    "comment": "AI generated video content with platform optimizations"
  },
  "attributes": {
    "title": {
      "type": "string",
      "required": true,
      "maxLength": 100,
      "pluginOptions": {
        "i18n": {
          "localized": true
        }
      }
    },
    "description": {
      "type": "text",
      "required": true,
      "maxLength": 500,
      "pluginOptions": {
        "i18n": {
          "localized": true
        }
      }
    },
    "slug": {
      "type": "uid",
      "targetField": "title"
    },
    "videoFile": {
      "type": "media",
      "multiple": false,
      "required": true,
      "allowedTypes": ["videos"]
    },
    "thumbnail": {
      "type": "media",
      "multiple": false,
      "required": false,
      "allowedTypes": ["images"]
    },
    "duration": {
      "type": "integer",
      "required": true,
      "min": 1,
      "max": 300
    },
    "resolution": {
      "type": "enumeration",
      "enum": ["720p", "1080p", "1440p", "4K"],
      "default": "1080p"
    },
    "aspectRatio": {
      "type": "enumeration",
      "enum": ["16:9", "9:16", "1:1", "4:3"],
      "default": "16:9"
    },
    "platforms": {
      "type": "enumeration",
      "enum": ["douyin", "wechat", "xiaohongshu", "weibo", "bilibili", "youtube"],
      "multiple": true,
      "required": true
    },
    "tags": {
      "type": "component",
      "repeatable": true,
      "component": "content.tags"
    },
    "aiMetadata": {
      "type": "component",
      "component": "content.ai-metadata"
    },
    "platformOptimizations": {
      "type": "component",
      "repeatable": true,
      "component": "content.platform-optimization"
    },
    "engagementMetrics": {
      "type": "component",
      "component": "content.engagement-metrics"
    },
    "publishStatus": {
      "type": "enumeration",
      "enum": ["draft", "review", "scheduled", "published", "archived"],
      "default": "draft"
    },
    "scheduledPublishAt": {
      "type": "datetime"
    },
    "publishedAt": {
      "type": "datetime"
    },
    "locale": {
      "type": "string",
      "private": true
    },
    "localizations": {
      "type": "relation",
      "relation": "oneToMany",
      "target": "api::video-content.video-content"
    }
  }
}
```

### 2. AI Generated Content / AI生成内容
**Purpose**: Store AI-generated scripts, concepts, and metadata
**目的**: 存储AI生成的脚本、概念和元数据

```json
{
  "kind": "collectionType",
  "collectionName": "ai_generated_contents",
  "info": {
    "singularName": "ai-generated-content",
    "pluralName": "ai-generated-contents",
    "displayName": "AI Generated Content"
  },
  "options": {
    "draftAndPublish": false,
    "comment": "AI generated concepts, scripts, and metadata"
  },
  "attributes": {
    "contentType": {
      "type": "enumeration",
      "enum": ["concept", "script", "storyboard", "video", "optimization"],
      "required": true
    },
    "aiModel": {
      "type": "string",
      "required": true
    },
    "prompt": {
      "type": "text",
      "required": true,
      "private": true
    },
    "generatedContent": {
      "type": "json",
      "required": true
    },
    "qualityScore": {
      "type": "decimal",
      "min": 0,
      "max": 100
    },
    "processingTime": {
      "type": "integer"
    },
    "cost": {
      "type": "decimal",
      "min": 0
    },
    "videoContent": {
      "type": "relation",
      "relation": "manyToOne",
      "target": "api::video-content.video-content"
    }
  }
}
```

### 3. Content Templates / 内容模板
**Purpose**: Reusable templates for different content types and platforms
**目的**: 不同类型和平台的内容复用模板

```json
{
  "kind": "collectionType",
  "collectionName": "content_templates",
  "info": {
    "singularName": "content-template",
    "pluralName": "content-templates",
    "displayName": "Content Template"
  },
  "options": {
    "draftAndPublish": true,
    "comment": "Reusable templates for content creation"
  },
  "attributes": {
    "name": {
      "type": "string",
      "required": true,
      "unique": true
    },
    "description": {
      "type": "text"
    },
    "templateType": {
      "type": "enumeration",
      "enum": ["video", "script", "storyboard", "thumbnail"],
      "required": true
    },
    "platforms": {
      "type": "enumeration",
      "enum": ["douyin", "wechat", "xiaohongshu", "weibo", "bilibili", "universal"],
      "multiple": true
    },
    "templateData": {
      "type": "json",
      "required": true
    },
    "variables": {
      "type": "component",
      "repeatable": true,
      "component": "content.template-variable"
    },
    "isActive": {
      "type": "boolean",
      "default": true
    },
    "usageCount": {
      "type": "integer",
      "default": 0
    }
  }
}
```

## 🔧 Component Definitions / 组件定义

### Content Tags / 内容标签
```json
{
  "collectionName": "components_content_tags",
  "info": {
    "displayName": "Content Tag",
    "icon": "tag"
  },
  "options": {},
  "attributes": {
    "tag": {
      "type": "string",
      "required": true,
      "maxLength": 50
    },
    "category": {
      "type": "enumeration",
      "enum": ["topic", "style", "emotion", "industry", "trend"]
    },
    "weight": {
      "type": "integer",
      "min": 1,
      "max": 10,
      "default": 5
    }
  }
}
```

### AI Metadata / AI元数据
```json
{
  "collectionName": "components_content_ai_metadata",
  "info": {
    "displayName": "AI Metadata",
    "icon": "robot"
  },
  "options": {},
  "attributes": {
    "modelUsed": {
      "type": "string",
      "required": true
    },
    "promptVersion": {
      "type": "string"
    },
    "processingParams": {
      "type": "json"
    },
    "confidenceScore": {
      "type": "decimal",
      "min": 0,
      "max": 1
    },
    "culturalRelevance": {
      "type": "decimal",
      "min": 0,
      "max": 1
    },
    "languageQuality": {
      "type": "decimal",
      "min": 0,
      "max": 1
    }
  }
}
```

### Platform Optimization / 平台优化
```json
{
  "collectionName": "components_content_platform_optimizations",
  "info": {
    "displayName": "Platform Optimization",
    "icon": "cog"
  },
  "options": {},
  "attributes": {
    "platform": {
      "type": "enumeration",
      "enum": ["douyin", "wechat", "xiaohongshu", "weibo", "bilibili", "youtube"],
      "required": true
    },
    "hashtags": {
      "type": "component",
      "repeatable": true,
      "component": "content.hashtag"
    },
    "optimalPostingTime": {
      "type": "time"
    },
    "contentFormat": {
      "type": "enumeration",
      "enum": ["video", "image", "carousel", "story", "live"]
    },
    "recommendedLength": {
      "type": "integer"
    },
    "engagementTips": {
      "type": "text"
    },
    "algorithmScore": {
      "type": "decimal",
      "min": 0,
      "max": 100
    }
  }
}
```

### Engagement Metrics / 参与度指标
```json
{
  "collectionName": "components_content_engagement_metrics",
  "info": {
    "displayName": "Engagement Metrics",
    "icon": "chart-line"
  },
  "options": {},
  "attributes": {
    "predictedViews": {
      "type": "integer"
    },
    "predictedLikes": {
      "type": "integer"
    },
    "predictedShares": {
      "type": "integer"
    },
    "predictedComments": {
      "type": "integer"
    },
    "engagementRate": {
      "type": "decimal",
      "min": 0,
      "max": 100
    },
    "viralityScore": {
      "type": "decimal",
      "min": 0,
      "max": 100
    }
  }
}
```

### Template Variable / 模板变量
```json
{
  "collectionName": "components_content_template_variables",
  "info": {
    "displayName": "Template Variable",
    "icon": "variable"
  },
  "options": {},
  "attributes": {
    "name": {
      "type": "string",
      "required": true
    },
    "type": {
      "type": "enumeration",
      "enum": ["text", "number", "boolean", "date", "media"],
      "required": true
    },
    "defaultValue": {
      "type": "string"
    },
    "isRequired": {
      "type": "boolean",
      "default": false
    },
    "validation": {
      "type": "json"
    }
  }
}
```

### Hashtag / 话题标签
```json
{
  "collectionName": "components_content_hashtags",
  "info": {
    "displayName": "Hashtag",
    "icon": "hashtag"
  },
  "options": {},
  "attributes": {
    "tag": {
      "type": "string",
      "required": true,
      "regex": "^#[\\w\\u4e00-\\u9fff]+$"
    },
    "popularity": {
      "type": "integer",
      "min": 1,
      "max": 100
    },
    "relevance": {
      "type": "decimal",
      "min": 0,
      "max": 1
    }
  }
}
```

## 🌍 Internationalization / 国际化

### Locale Configuration / 本地化配置
```javascript
// config/plugins.js
module.exports = {
  i18n: {
    enabled: true,
    config: {
      defaultLocale: 'zh-CN',
      locales: [
        {
          code: 'zh-CN',
          name: '简体中文',
          file: 'zh-CN.json'
        },
        {
          code: 'zh-TW',
          name: '繁體中文',
          file: 'zh-TW.json'
        },
        {
          code: 'en-US',
          name: 'English',
          file: 'en-US.json'
        }
      ],
      fallbackLanguage: 'zh-CN'
    }
  }
}
```

### Content Translation Workflow / 内容翻译工作流
1. **Primary Content**: Created in Chinese (zh-CN)
2. **AI Translation**: Automatic translation to other locales
3. **Human Review**: Manual review and adjustment
4. **Cultural Adaptation**: Platform-specific cultural adjustments
5. **Publication**: Locale-specific publishing

## 🔒 Security & Permissions / 安全与权限

### Role-Based Access Control / 基于角色的访问控制
```json
{
  "roles": [
    {
      "name": "Content Creator",
      "permissions": ["create:video", "update:own-video", "read:template"]
    },
    {
      "name": "Content Reviewer",
      "permissions": ["read:video", "update:video-status", "create:review"]
    },
    {
      "name": "Content Manager",
      "permissions": ["create:*", "read:*", "update:*", "delete:*"]
    },
    {
      "name": "AI Service",
      "permissions": ["read:video", "create:ai-content", "update:ai-metadata"]
    }
  ]
}
```

### API Security / API安全
- **JWT Authentication**: Token-based authentication
- **Rate Limiting**: 100 requests/minute per API key
- **CORS Configuration**: Strict domain restrictions
- **Content Validation**: Input sanitization and validation
- **Audit Logging**: All content changes logged

## 📊 Performance Optimization / 性能优化

### Caching Strategy / 缓存策略
```javascript
// Redis caching for content
const cacheKey = `content:${locale}:${contentId}`;
const cachedContent = await redis.get(cacheKey);

if (cachedContent) {
  return JSON.parse(cachedContent);
}

const content = await strapi.entityService.findOne(...);
await redis.setex(cacheKey, 3600, JSON.stringify(content)); // 1 hour TTL
```

### Database Optimization / 数据库优化
- **Indexing**: Optimized indexes for frequent queries
- **Query Optimization**: Efficient database queries
- **Connection Pooling**: Database connection management
- **Read Replicas**: Scaling read operations

## 🚀 Integration Endpoints / 集成端点

### Content Sync API / 内容同步API
```http
GET /api/content/sync?locale=zh-CN&updatedAfter=2024-01-01
Authorization: Bearer {strapi-api-token}
```

### Webhook Events / Webhook事件
```json
{
  "event": "entry.create",
  "model": "video-content",
  "entry": {
    "id": 1,
    "title": "新视频内容",
    "locale": "zh-CN"
  }
}
```

## 📋 Validation Rules / 验证规则

### Content Validation / 内容验证
- **Title Length**: 1-100 characters
- **Description Length**: 1-500 characters
- **Video Duration**: 1-300 seconds
- **File Formats**: MP4, WebM, QuickTime
- **Image Formats**: JPEG, PNG, WebP
- **Chinese Content**: Unicode validation for CJK characters

### Business Rules / 业务规则
- **Publishing Schedule**: Cannot be in the past
- **Platform Requirements**: Must meet platform-specific constraints
- **Content Moderation**: Automatic content filtering
- **Copyright Check**: Media asset validation

This data model provides a comprehensive foundation for content management in the Chinese AI video creation system, supporting bilingual content, platform-specific optimizations, and AI-generated content workflows.