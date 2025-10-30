# Strapi CMS 快速开始指南

## 🚀 5分钟快速部署

### 步骤1: 启动Strapi服务
```bash
cd strapi-cms
./deploy.sh
```

### 步骤2: 访问管理界面
- 打开浏览器访问: `https://localhost:8443/admin`
- 创建管理员账户

### 步骤3: 验证API
```bash
# 测试健康检查
curl http://localhost:1337/_health

# 获取API Token
curl -X POST http://localhost:1337/api/auth/local \
  -H "Content-Type: application/json" \
  -d '{
    "identifier": "your-admin-email",
    "password": "your-admin-password"
  }'
```

## 📋 基本操作

### 1. 创建项目
```bash
curl -X POST http://localhost:1337/api/projects \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "data": {
      "title": "我的第一个项目",
      "description": "抖音短视频营销项目",
      "status": "draft",
      "businessInput": {
        "product": "智能手表",
        "target_audience": "18-35岁年轻人",
        "platform": "douyin"
      },
      "technicalSpecs": {
        "duration": 30,
        "resolution": "1080p",
        "aspect_ratio": "9:16"
      }
    }
  }'
```

### 2. 查看项目列表
```bash
curl http://localhost:1337/api/projects?populate=* \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 3. 上传媒体文件
```bash
curl -X POST http://localhost:1337/api/upload \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "files=@/path/to/your/image.jpg" \
  -F "fileInfo={\"name\":\"product-image\",\"alternativeText\":\"产品图片\"}"
```

## 🔧 开发环境

### 本地开发模式
```bash
# 安装依赖
npm install

# 启动开发服务器
npm run develop

# 访问开发环境
# Admin: http://localhost:1337/admin
# API: http://localhost:1337/api
```

### 数据模型修改
```bash
# 修改内容类型后，重启服务
npm run develop

# 或者使用CLI工具
npm run strapi content-type:list
npm run strapi content-type:generate
```

## 🧪 测试集成

### 测试与主系统集成
```bash
# 1. 确保后端服务已启动
# 2. 测试Strapi集成

# 健康检查
curl http://localhost:8000/api/v1/strapi/health

# 同步测试项目
curl -X POST http://localhost:8000/api/v1/strapi/projects/sync \
  -H "Authorization: Bearer YOUR_BACKEND_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content_type": "project",
    "direction": "to_strapi",
    "entity_id": "test-project-id"
  }'
```

### Webhook测试
```bash
# 使用ngrok暴露本地服务
grok http 8000

# 注册webhook
curl -X POST "http://localhost:8000/api/v1/strapi/register-webhook?webhook_url=https://your-ngrok-url.ngrok.io/api/v1/strapi/webhooks/strapi&events=entry.create,entry.update"
```

## 📊 监控和调试

### 查看日志
```bash
# Strapi日志
docker-compose logs -f strapi

# PostgreSQL日志
docker-compose logs -f postgres

# 所有服务日志
docker-compose logs -f
```

### 性能监控
```bash
# 检查服务状态
docker-compose ps

# 查看资源使用
docker stats

# 数据库连接检查
docker-compose exec postgres pg_isready -U strapi
```

## 🛠️ 常见问题

### Q: 服务启动失败？
**A:** 检查端口占用和Docker状态：
```bash
# 检查端口占用
netstat -tulpn | grep -E ':(1337|5433|6380|8080|8443)'

# 重启Docker服务
sudo systemctl restart docker
```

### Q: 数据库连接失败？
**A:** 检查数据库容器状态：
```bash
# 查看数据库日志
docker-compose logs postgres

# 手动连接测试
docker-compose exec postgres psql -U strapi -d strapi_cms
```

### Q: API认证失败？
**A:** 检查API Token配置：
```bash
# 在Strapi管理界面生成新的API Token
# Settings → API Tokens → Create new API Token
```

### Q: 媒体上传失败？
**A:** 检查文件权限和大小限制：
```bash
# 检查上传目录权限
docker-compose exec strapi ls -la /app/public/uploads

# 查看文件大小限制
cat config/middlewares.js | grep size
```

## 🎯 下一步

### 1. 配置生产环境
- 修改 `.env` 文件中的配置
- 设置有效的SSL证书
- 配置域名和CDN

### 2. 自定义内容类型
- 根据业务需求调整内容模型
- 添加自定义字段和验证规则
- 配置权限和角色

### 3. 集成前端应用
- 配置前端API调用
- 实现内容编辑器
- 添加媒体管理功能

### 4. 高级功能
- 设置定时备份
- 配置监控告警
- 实现内容工作流

## 📚 相关资源

- [Strapi官方文档](https://docs.strapi.io/)
- [API参考](http://localhost:1337/documentation)
- [项目README](./README.md)
- [集成指南](../backend/docs/STRAPI_INTEGRATION.md)

## 🤝 获取帮助

遇到问题？

1. 查看日志文件
2. 检查配置项
3. 搜索已知问题
4. 提交GitHub Issue

---

**享受使用Strapi CMS！** 🎉