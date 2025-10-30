# 角色权限系统文档
# Role-Based Permissions System Documentation

## 概述 Overview

本系统实现了基于角色的细粒度权限控制（RBAC），支持角色继承、资源特定权限、权限过期、审计日志等高级功能。

This system implements a fine-grained Role-Based Access Control (RBAC) with role inheritance, resource-specific permissions, permission expiration, audit logging, and other advanced features.

## 核心特性 Core Features

### 🎯 细粒度权限控制 Fine-grained Permission Control
- **资源类型 Resource Types**: 用户、项目、资源、脚本、分镜、视频、AI模型、组织、系统
- **操作类型 Action Types**: 创建、读取、更新、删除、执行、管理、审批、审核、发布、导出、分享

### 🔄 角色继承 Role Inheritance
- 支持角色层级结构，子角色自动继承父角色权限
- 可配置的继承深度和权限合并策略

### 📋 多角色支持 Multi-role Support
- 用户可同时拥有多个角色
- 权限自动合并，支持权限冲突解决

### ⏰ 权限有效期 Permission Expiration
- 支持角色和权限的过期时间设置
- 自动权限失效和续期管理

### 🔍 资源特定权限 Resource-specific Permissions
- 针对特定资源的权限控制
- 支持用户和角色级别的资源权限

### 📊 审计日志 Audit Logging
- 完整的权限操作审计跟踪
- 权限检查、授予、撤销等操作记录

## 系统架构 System Architecture

### 数据库模型 Database Models

#### 权限表 Permissions
```sql
permissions: {
  id: UUID,
  name: String,           // 权限名称（唯一）
  description: String,    // 权限描述
  resource: Enum,         // 资源类型
  action: Enum,          // 操作类型
  category: String,      // 权限分类
  is_system: Boolean,    // 是否为系统权限
  name_zh: String,       // 中文名称
  description_zh: String, // 中文描述
  created_at: DateTime,
  updated_at: DateTime
}
```

#### 角色表 Roles
```sql
roles: {
  id: UUID,
  name: String,           // 角色名称（唯一）
  description: String,    // 角色描述
  role_type: Enum,       // 角色类型（系统/自定义/组织）
  parent_role_id: UUID,  // 父角色ID（用于继承）
  level: Integer,        // 角色级别
  organization_id: UUID, // 组织ID
  is_active: Boolean,    // 是否激活
  is_system: Boolean,    // 是否为系统角色
  name_zh: String,       // 中文名称
  description_zh: String, // 中文描述
  created_at: DateTime,
  updated_at: DateTime
}
```

#### 用户角色关联 User Roles
```sql
user_roles: {
  id: UUID,
  user_id: UUID,         // 用户ID
  role_id: UUID,         // 角色ID
  assigned_by: UUID,     // 分配者ID
  assignment_reason: String, // 分配原因
  expires_at: DateTime,  // 过期时间
  is_active: Boolean,    // 是否激活
  created_at: DateTime,
  updated_at: DateTime
}
```

#### 角色权限关联 Role Permissions
```sql
role_permissions: {
  id: UUID,
  role_id: UUID,         // 角色ID
  permission_id: UUID,   // 权限ID
  scope: String,         // 权限范围（own/organization/all）
  conditions: JSON,      // 额外条件
  is_granted: Boolean,   // 是否授予（支持拒绝权限）
  expires_at: DateTime,  // 过期时间
  created_at: DateTime,
  updated_at: DateTime
}
```

#### 资源权限 Resource Permissions
```sql
resource_permissions: {
  id: UUID,
  resource_type: Enum,   // 资源类型
  resource_id: UUID,     // 特定资源ID
  permission_id: UUID,   // 权限ID
  subject_type: String,  // 主体类型（user/role）
  subject_id: UUID,      // 主体ID
  is_granted: Boolean,   // 是否授予
  expires_at: DateTime,  // 过期时间
  conditions: JSON,      // 额外条件
  created_by: UUID,      // 创建者ID
  created_at: DateTime,
  updated_at: DateTime
}
```

#### 审计日志 Audit Logs
```sql
permission_audit_logs: {
  id: UUID,
  action: String,        // 操作类型
  resource_type: Enum,   // 资源类型
  resource_id: UUID,     // 资源ID
  subject_type: String,  // 主体类型
  subject_id: UUID,      // 主体ID
  permission_id: UUID,   // 权限ID
  role_id: UUID,         // 角色ID
  performed_by: UUID,    // 执行者ID
  ip_address: String,    // IP地址
  user_agent: String,    // 用户代理
  success: Boolean,      // 是否成功
  details: JSON,         // 详细信息
  error_message: Text,   // 错误信息
  created_at: DateTime
}
```

## API端点 API Endpoints

### 权限管理 Permission Management

#### 获取权限列表 Get Permissions List
```http
GET /api/permissions
Authorization: Bearer {token}

Query Parameters:
- resource: 资源类型过滤
- action: 操作类型过滤
- category: 分类过滤
- is_system: 是否系统权限

Response:
{
  "permissions": [
    {
      "id": "uuid",
      "name": "permission.name",
      "description": "Permission description",
      "resource": "project",
      "action": "read",
      "category": "general",
      "is_system": false,
      "name_zh": "权限名称",
      "description_zh": "权限描述"
    }
  ]
}
```

#### 创建权限 Create Permission
```http
POST /api/permissions
Authorization: Bearer {token}
Content-Type: application/json

{
  "name": "custom.permission",
  "description": "Custom permission description",
  "resource": "project",
  "action": "read",
  "name_zh": "自定义权限",
  "description_zh": "自定义权限描述",
  "category": "custom"
}
```

#### 更新权限 Update Permission
```http
PUT /api/permissions/{permission_id}
Authorization: Bearer {token}
Content-Type: application/json

{
  "name": "updated.permission",
  "description": "Updated permission description"
}
```

#### 删除权限 Delete Permission
```http
DELETE /api/permissions/{permission_id}
Authorization: Bearer {token}
```

### 角色管理 Role Management

#### 获取角色列表 Get Roles List
```http
GET /api/permissions/roles
Authorization: Bearer {token}

Query Parameters:
- role_type: 角色类型过滤
- organization_id: 组织ID过滤
- is_active: 是否激活过滤

Response:
{
  "roles": [
    {
      "id": "uuid",
      "name": "admin",
      "description": "Administrator role",
      "role_type": "system",
      "name_zh": "管理员",
      "description_zh": "管理员角色",
      "is_system": true
    }
  ]
}
```

#### 创建角色 Create Role
```http
POST /api/permissions/roles
Authorization: Bearer {token}
Content-Type: application/json

{
  "name": "custom_role",
  "description": "Custom role description",
  "name_zh": "自定义角色",
  "description_zh": "自定义角色描述",
  "role_type": "custom",
  "parent_role_id": "parent-role-uuid"
}
```

#### 为角色分配权限 Assign Permission to Role
```http
POST /api/permissions/roles/{role_id}/permissions
Authorization: Bearer {token}
Content-Type: application/json

{
  "permission_id": "permission-uuid",
  "scope": "organization",
  "conditions": {"department": "marketing"},
  "is_granted": true,
  "expires_at": "2024-12-31T23:59:59Z"
}
```

### 用户权限管理 User Permission Management

#### 获取用户角色 Get User Roles
```http
GET /api/permissions/users/{user_id}/roles
Authorization: Bearer {token}

Response:
{
  "user_roles": [
    {
      "id": "uuid",
      "user_id": "user-uuid",
      "role_id": "role-uuid",
      "role": {
        "id": "role-uuid",
        "name": "admin",
        "name_zh": "管理员"
      },
      "assigned_by": "admin-uuid",
      "assignment_reason": "Assigned for project management",
      "expires_at": null,
      "is_active": true
    }
  ]
}
```

#### 为用户分配角色 Assign Role to User
```http
POST /api/permissions/users/{user_id}/roles
Authorization: Bearer {token}
Content-Type: application/json

{
  "role_id": "role-uuid",
  "assignment_reason": "Assigned for project management",
  "expires_at": "2024-12-31T23:59:59Z"
}
```

#### 撤销用户角色 Revoke Role from User
```http
DELETE /api/permissions/users/{user_id}/roles/{role_id}
Authorization: Bearer {token}
```

### 权限检查 Permission Checking

#### 检查用户权限 Check User Permission
```http
POST /api/permissions/check
Authorization: Bearer {token}
Content-Type: application/json

{
  "resource": "project",
  "action": "read",
  "resource_id": "project-uuid",
  "conditions": {"organization_id": "org-uuid"}
}

Response:
{
  "has_permission": true,
  "resource": "project",
  "action": "read",
  "resource_id": "project-uuid",
  "details": {
    "user_id": "user-uuid",
    "username": "john_doe",
    "checked_at": "2024-01-15T10:30:00Z"
  }
}
```

#### 获取当前用户权限 Get Current User Permissions
```http
GET /api/permissions/my-permissions
Authorization: Bearer {token}

Query Parameters:
- resource: 资源类型过滤

Response:
{
  "permissions": [
    {
      "permission_id": "uuid",
      "permission_name": "project.read",
      "resource": "project",
      "action": "read",
      "role_name": "content_creator",
      "scope": "own"
    }
  ]
}
```

## 权限装饰器 Permission Decorators

### 基本权限检查 Basic Permission Checking

```python
from app.core.permissions import require_permission, PermissionResource, PermissionAction
from fastapi import Depends

@router.get("/projects/{project_id}")
async def get_project(
    project_id: str,
    current_user: User = Depends(require_permission(
        PermissionResource.PROJECT,
        PermissionAction.READ,
        resource_id_path="project_id"
    ))
):
    # 用户必须有项目读取权限才能访问
    pass
```

### 预定义权限检查器 Predefined Permission Checkers

```python
from app.core.permissions import (
    require_project_create, require_project_read,
    require_project_write, require_project_delete,
    require_user_manage, require_admin
)

@router.post("/projects")
async def create_project(
    project_data: ProjectData,
    current_user: User = Depends(require_project_create)
):
    # 需要项目创建权限
    pass

@router.get("/admin/users")
async def get_users(
    current_user: User = Depends(require_admin)
):
    # 需要管理员权限
    pass
```

### 自定义权限检查 Custom Permission Checking

```python
from app.core.permissions import PermissionChecker, PermissionResource, PermissionAction

# 创建自定义权限检查器
custom_permission = PermissionChecker(
    resource=PermissionResource.PROJECT,
    action=PermissionAction.MANAGE,
    conditions={"organization_id": "specific_org"}
)

@router.put("/projects/{project_id}")
async def update_project(
    project_id: str,
    project_data: ProjectData,
    current_user: User = Depends(custom_permission)
):
    # 自定义权限检查逻辑
    pass
```

### 权限验证器 Permission Validator

```python
from app.core.permissions import get_permission_validator

@router.get("/projects/{project_id}/edit")
async def edit_project(
    project_id: str,
    validator = Depends(get_permission_validator)
):
    # 使用权限验证器进行复杂权限检查
    if not await validator.can_edit_project(project_id):
        raise PermissionDeniedError("没有权限编辑此项目")

    # 获取用户可访问的项目列表
    accessible_projects = await validator.get_accessible_projects()

    return {"accessible_projects": accessible_projects}
```

## 系统默认权限 System Default Permissions

### 超级管理员 Super Admin
拥有所有系统权限，包括：
- 用户管理：创建、读取、更新、删除、管理
- 项目管理：创建、读取、更新、删除、管理、审批
- 资源管理：创建、读取、更新、删除
- AI模型：执行、管理
- 系统管理：管理、读取

### 管理员 Admin
拥有大部分管理权限，除用户删除外：
- 用户管理：创建、读取、更新、管理
- 项目管理：创建、读取、更新、管理、审批
- 资源管理：创建、读取、更新、删除
- AI模型：执行、管理
- 系统管理：读取

### 项目经理 Project Manager
项目管理相关权限：
- 项目：创建、读取、更新、管理
- 资源：创建、读取、更新、删除
- AI模型：执行

### 内容创作者 Content Creator
内容创作权限：
- 项目：创建、读取、更新
- 资源：创建、读取、更新
- AI模型：执行

### 审核员 Reviewer
内容审核权限：
- 项目：读取、更新、审批
- 资源：读取、更新

### 客户 Client
只读权限：
- 项目：读取
- 资源：读取

## 权限缓存 Permission Caching

系统实现了权限缓存机制以提高性能：

```python
# 权限缓存配置
_permission_cache = {}
_cache_ttl = 300  # 5分钟缓存

# 缓存键格式
permission_cache_key = f"user:{user_id}:resource:{resource}:action:{action}"
role_cache_key = f"user:{user_id}:roles"
```

缓存策略：
- 用户权限检查结果缓存5分钟
- 用户角色列表缓存5分钟
- 角色权限关系缓存5分钟
- 权限变更时自动清除相关缓存

## 安全考虑 Security Considerations

### 权限验证 Permission Validation
- 所有权限检查都经过严格的验证
- 支持权限过期时间检查
- 支持权限条件验证
- 支持资源特定权限检查

### 审计跟踪 Audit Trail
- 所有权限相关操作都有完整的审计日志
- 记录操作者、时间、IP地址、结果等信息
- 支持权限使用分析和异常检测

### 数据保护 Data Protection
- 权限数据加密存储
- 敏感权限操作需要额外验证
- 支持权限数据的备份和恢复

## 最佳实践 Best Practices

### 权限设计 Permission Design
1. **最小权限原则**：只授予用户完成工作所需的最小权限
2. **权限分组**：按功能和业务逻辑对权限进行分组
3. **角色设计**：创建清晰的角色层次结构
4. **定期审查**：定期审查和更新权限设置

### 性能优化 Performance Optimization
1. **缓存使用**：合理使用权限缓存减少数据库查询
2. **批量操作**：批量处理权限相关操作
3. **索引优化**：确保权限相关字段有适当的索引
4. **异步处理**：使用异步处理权限检查操作

### 错误处理 Error Handling
1. **清晰的错误信息**：提供清晰的权限拒绝原因
2. **异常处理**：正确处理权限相关的异常情况
3. **日志记录**：记录所有权限相关操作的日志
4. **用户反馈**：向用户提供友好的权限相关反馈

## 故障排除 Troubleshooting

### 常见问题 Common Issues

#### 权限检查失败 Permission Check Failed
```python
# 检查用户是否有权限
has_permission = await permission_service.check_permission(
    db=db,
    user_id=user_id,
    resource=PermissionResource.PROJECT,
    action=PermissionAction.READ,
    resource_id=project_id
)

# 检查用户角色
user_roles = await permission_service.get_user_roles(db, user_id)

# 检查角色权限
role_permissions = await permission_service.get_role_permissions(db, role_id)
```

#### 权限缓存问题 Permission Cache Issues
```python
# 清除权限缓存
from app.core.permissions import permission_service
permission_service.clear_permission_cache(user_id)

# 重新检查权限
has_permission = await permission_service.check_permission(...)
```

#### 角色继承问题 Role Inheritance Issues
```python
# 检查角色层级
role_hierarchy = await permission_service.get_role_hierarchy(db, role_ids)

# 检查继承的权限
inherited_permissions = await permission_service.get_inherited_permissions(db, role_id)
```

## 扩展开发 Extension Development

### 自定义权限 Custom Permissions

```python
from app.services.permissions import permission_service
from app.core.database import PermissionResource, PermissionAction

# 创建自定义权限
permission = await permission_service.create_permission(
    db=db,
    name="custom.permission",
    description="Custom permission for specific functionality",
    resource=PermissionResource.CUSTOM,
    action=PermissionAction.CUSTOM,
    name_zh="自定义权限",
    description_zh="特定功能的自定义权限",
    category="custom",
    is_system=False
)
```

### 自定义角色 Custom Roles

```python
# 创建自定义角色
role = await permission_service.create_role(
    db=db,
    name="custom_role",
    description="Custom role for specific user group",
    name_zh="自定义角色",
    description_zh="特定用户组的自定义角色",
    role_type=RoleType.CUSTOM,
    parent_role_id="parent-role-id"  # 可选的父角色
)
```

### 权限中间件 Permission Middleware

```python
from app.core.permissions import PermissionMiddleware

# 创建自定义权限中间件
class CustomPermissionMiddleware(PermissionMiddleware):
    async def __call__(self, scope, receive, send):
        # 自定义权限检查逻辑
        if await self.check_custom_permissions(scope):
            await self.app(scope, receive, send)
        else:
            await self.send_permission_denied_response(send)

    async def check_custom_permissions(self, scope):
        # 实现自定义权限检查
        pass
```

## 更新日志 Change Log

### v1.0.0 (当前版本)
- ✅ 基础RBAC权限系统
- ✅ 角色继承功能
- ✅ 资源特定权限
- ✅ 权限过期机制
- ✅ 审计日志系统
- ✅ 多语言支持（中英文）
- ✅ 权限缓存机制
- ✅ 完整的API端点
- ✅ 全面的测试覆盖

### 计划功能 Planned Features
- 🔲 动态权限创建和管理UI
- 🔲 权限使用分析和报告
- 🔲 权限推荐系统
- 🔲 高级权限冲突检测
- 🔲 组织级别的权限管理
- 🔲 API速率限制权限
- 🔲 时间基于的权限
- 🔲 地理位置权限限制

---

**文档更新日期**: 2024年1月15日
**系统版本**: v1.0.0
**维护团队**: AI视频创作系统开发团队

如有问题或建议，请联系开发团队。