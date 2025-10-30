# Redis连接问题解决方案

## 问题描述
系统启动时出现Redis连接失败错误：
```
app.core.database:init_redis:443 - ⚠️ Redis连接失败: Error 111 connecting to localhost:6379. 111.
```

## 解决方案

### 1. 启动Redis服务
```bash
# 使用Docker启动Redis
docker run -d --name chinese-ai-redis -p 6379:6379 redis:7-alpine

# 验证Redis运行状态
docker ps | grep redis
docker exec chinese-ai-redis redis-cli ping
```

### 2. 环境配置
确保环境变量正确设置：
```bash
# 在.env文件中设置
REDIS_URL=redis://localhost:6379/0
REDIS_POOL_SIZE=10
```

### 3. 代码改进
已增强Redis连接管理：
- 添加了更健壮的连接管理器 `RedisManager`
- 改进了错误处理和重连机制
- 添加了健康检查功能
- 提供了向后兼容的API

### 4. 测试连接
使用提供的测试脚本验证连接：
```bash
python test_redis_connection.py
```

## 故障排除

### 常见问题
1. **连接被拒绝 (Error 111)**
   - 确保Redis服务正在运行
   - 检查端口6379是否被占用
   - 验证防火墙设置

2. **认证失败**
   - 检查Redis是否需要密码
   - 验证REDIS_URL格式

3. **连接超时**
   - 检查网络连接
   - 增加连接超时时间

### 监控Redis状态
```bash
# 查看Redis日志
docker logs chinese-ai-redis

# 使用Redis CLI
docker exec -it chinese-ai-redis redis-cli
```

## 生产环境建议
1. 使用Docker Compose管理Redis服务
2. 配置Redis持久化
3. 设置内存限制
4. 配置监控和告警
5. 使用Redis集群提高可用性