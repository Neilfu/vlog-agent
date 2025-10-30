# 🛡️ 角色权限系统 (Role-Based Permissions System)

## 🚀 快速开始 Quick Start

### 1. 初始化权限系统 Initialize Permission System

```bash
# 运行权限系统初始化脚本
python scripts/init_permissions.py
```

### 2. 基本权限检查 Basic Permission Check

```python
from app.core.permissions import permission_service, PermissionResource, PermissionAction

# 检查用户权限
has_permission = await permission_service.check_permission(
    db=db,
    user_id=user_id,
    resource=PermissionResource.PROJECT,
    action=PermissionAction.READ,
    resource_id=project_id
)
```

### 3. 使用权限装饰器 Use Permission Decorators

```python
from app.core.permissions import require_project_read
from fastapi import Depends

@router.get("/projects/{project_id}")
async def get_project(
    project_id: str,
    current_user = Depends(require_project_read)
):
    # 自动进行权限检查
    pass
```

## 📋 系统特性 Features

- ✅ **细粒度权限控制** - 支持资源级别和操作级别的权限控制
- ✅ **角色继承** - 子角色自动继承父角色权限
- ✅ **多角色支持** - 用户可同时拥有多个角色
- ✅ **权限过期** - 支持权限和角色的有效期设置
- ✅ **资源特定权限** - 针对特定资源的权限控制
- ✅ **审计日志** - 完整的权限操作记录
- ✅ **多语言支持** - 中英文双语支持
- ✅ **权限缓存** - 高性能权限缓存机制

## 🏗️ 系统架构 Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    API Layer (FastAPI)                      │
├─────────────────────────────────────────────────────────────┤
│                Permission Decorators                        │
├─────────────────────────────────────────────────────────────┤
│              Permission Service Layer                       │
├─────────────────────────────────────────────────────────────┤
│                  Database Models                            │
│  ┌─────────────┬──────────┬──────────────┬──────────────┐   │
│  │Permissions  │  Roles   │UserRoles     │RolePermissions│   │
│  └─────────────┴──────────┴──────────────┴──────────────┘   │
├─────────────────────────────────────────────────────────────┤
│                    Database (PostgreSQL)                    │
└─────────────────────────────────────────────────────────────┘
```

## 🔧 核心组件 Core Components

### 权限服务 (Permission Service)
- 权限检查核心逻辑
- 角色继承处理
- 权限缓存管理
- 审计日志记录

### 权限装饰器 (Permission Decorators)
- FastAPI依赖注入
- 自动权限验证
- 错误处理
- 向后兼容

### 数据库模型 (Database Models)
- 权限定义表
- 角色管理表
- 用户角色关联
- 角色权限关联
- 资源特定权限
- 审计日志

## 📖 详细文档 Detailed Documentation

- [完整权限系统文档](PERMISSIONS.md) - 包含所有API端点、使用示例、最佳实践
- [API端点参考](PERMISSIONS.md#api端点-api-endpoints) - 所有权限相关API的详细说明
- [权限装饰器指南](PERMISSIONS.md#权限装饰器-permission-decorators) - 如何使用权限装饰器
- [系统默认权限](PERMISSIONS.md#系统默认权限-system-default-permissions) - 预定义的角色和权限
- [故障排除](PERMISSIONS.md#故障排除-troubleshooting) - 常见问题解决方案

## 🧪 测试 Testing

```bash
# 运行权限系统测试
pytest tests/test_permissions.py -v

# 运行所有测试
pytest tests/ -v
```

## 🛠️ 开发 Development

### 添加新权限 Add New Permission

```python
from app.services.permissions import permission_service
from app.core.database import PermissionResource, PermissionAction

# 创建新权限
permission = await permission_service.create_permission(
    db=db,
    name="new.permission",
    description="Description of new permission",
    resource=PermissionResource.PROJECT,
    action=PermissionAction.CUSTOM,
    name_zh="新权限",
    description_zh="新权限的描述"
)
```

### 添加新角色 Add New Role

```python
from app.services.permissions import permission_service
from app.core.database import RoleType

# 创建新角色
role = await permission_service.create_role(
    db=db,
    name="new_role",
    description="Description of new role",
    name_zh="新角色",
    description_zh="新角色的描述",
    role_type=RoleType.CUSTOM
)
```

## 🔍 监控和调试 Monitoring & Debugging

### 查看权限日志 View Permission Logs

```python
# 获取权限审计日志
from app.core.database import PermissionAuditLog
from sqlalchemy import select

result = await db.execute(
    select(PermissionAuditLog).where(
        PermissionAuditLog.subject_id == user_id
    ).order_by(PermissionAuditLog.created_at.desc())
)
audit_logs = result.scalars().all()
```

### 调试权限问题 Debug Permission Issues

```python
# 获取用户所有权限
user_permissions = await permission_service.get_user_permissions(
    db=db,
    user_id=user_id
)

# 检查用户角色
user_roles = await permission_service._get_user_roles(db, user_id)

# 检查特定权限
has_permission = await permission_service.check_permission(
    db=db,
    user_id=user_id,
    resource=PermissionResource.PROJECT,
    action=PermissionAction.READ,
    resource_id=resource_id
)
```

## 📊 性能优化 Performance Optimization

### 权限缓存 Permission Caching
- 用户权限缓存：5分钟TTL
- 角色权限缓存：5分钟TTL
- 自动缓存失效机制

### 数据库优化 Database Optimization
- 适当的索引配置
- 查询优化
- 批量操作支持

## 🔐 安全考虑 Security Considerations

- 所有权限检查都经过严格验证
- 完整的审计日志记录
- 权限数据加密存储
- 敏感操作需要额外验证

## 🤝 贡献 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 许可证 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 支持 Support

如有问题，请：
1. 查看[详细文档](PERMISSIONS.md)
2. 检查[故障排除指南](PERMISSIONS.md#故障排除-troubleshooting)
3. 在GitHub Issues中报告问题

---

**文档版本**: v1.0.0
**最后更新**: 2024年1月15日
**维护团队**: AI视频创作系统开发团队