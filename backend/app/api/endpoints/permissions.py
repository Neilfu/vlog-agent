"""
权限管理API端点
Permission Management API Endpoints

处理角色管理、权限分配、权限检查等
Handles role management, permission assignment, permission checking, etc.
"""

import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from pydantic import BaseModel, Field, validator
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func

from app.core.database import get_db, Permission, Role, UserRole, RolePermission, ResourcePermission
from app.core.security import get_current_user
from app.core.permissions import (
    require_admin, require_permission, PermissionChecker,
    require_user_manage, require_role_manage
)
from app.models import User
from app.core.exceptions import ValidationError, NotFoundError
from app.services.permissions import permission_service, PermissionService

logger = logging.getLogger(__name__)
router = APIRouter()

# 权限模型定义
class PermissionResponse(BaseModel):
    """权限响应模型"""
    id: str
    name: str
    description: str
    resource: str
    action: str
    category: str
    is_system: bool
    name_zh: str
    description_zh: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PermissionCreateRequest(BaseModel):
    """权限创建请求模型"""
    name: str = Field(..., min_length=3, max_length=100, description="权限名称（英文）")
    description: str = Field(..., max_length=500, description="权限描述（英文）")
    resource: str = Field(..., description="资源类型")
    action: str = Field(..., description="操作类型")
    name_zh: str = Field(..., min_length=1, max_length=100, description="权限名称（中文）")
    description_zh: str = Field(..., max_length=500, description="权限描述（中文）")
    category: str = Field(default="general", description="权限分类")

    @validator('resource')
    def validate_resource(cls, v):
        from app.core.database import PermissionResource
        valid_resources = [r.value for r in PermissionResource]
        if v not in valid_resources:
            raise ValueError(f'无效的资源类型: {v}. 有效类型: {valid_resources}')
        return v

    @validator('action')
    def validate_action(cls, v):
        from app.core.database import PermissionAction
        valid_actions = [a.value for a in PermissionAction]
        if v not in valid_actions:
            raise ValueError(f'无效的操作类型: {v}. 有效类型: {valid_actions}')
        return v


class RoleResponse(BaseModel):
    """角色响应模型"""
    id: str
    name: str
    description: str
    role_type: str
    parent_role_id: Optional[str]
    level: int
    organization_id: Optional[str]
    is_active: bool
    is_system: bool
    name_zh: str
    description_zh: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class RoleCreateRequest(BaseModel):
    """角色创建请求模型"""
    name: str = Field(..., min_length=3, max_length=100, description="角色名称（英文）")
    description: str = Field(..., max_length=500, description="角色描述（英文）")
    name_zh: str = Field(..., min_length=1, max_length=100, description="角色名称（中文）")
    description_zh: str = Field(..., max_length=500, description="角色描述（中文）")
    role_type: str = Field(default="custom", description="角色类型")
    parent_role_id: Optional[str] = Field(None, description="父角色ID")
    organization_id: Optional[str] = Field(None, description="组织ID")

    @validator('role_type')
    def validate_role_type(cls, v):
        from app.core.database import RoleType
        valid_types = [t.value for t in RoleType]
        if v not in valid_types:
            raise ValueError(f'无效的角色类型: {v}. 有效类型: {valid_types}')
        return v


class RolePermissionResponse(BaseModel):
    """角色权限响应模型"""
    id: str
    role_id: str
    permission_id: str
    permission: PermissionResponse
    scope: Optional[str]
    conditions: Dict[str, Any]
    is_granted: bool
    expires_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class RolePermissionAssignRequest(BaseModel):
    """角色权限分配请求模型"""
    permission_id: str = Field(..., description="权限ID")
    scope: Optional[str] = Field(None, description="权限范围")
    conditions: Dict[str, Any] = Field(default_factory=dict, description="额外条件")
    is_granted: bool = Field(default=True, description="是否授予权限")
    expires_at: Optional[datetime] = Field(None, description="过期时间")


class UserRoleResponse(BaseModel):
    """用户角色响应模型"""
    id: str
    user_id: str
    role_id: str
    role: RoleResponse
    assigned_by: Optional[str]
    assignment_reason: Optional[str]
    expires_at: Optional[datetime]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserRoleAssignRequest(BaseModel):
    """用户角色分配请求模型"""
    role_id: str = Field(..., description="角色ID")
    assignment_reason: Optional[str] = Field(None, max_length=500, description="分配原因")
    expires_at: Optional[datetime] = Field(None, description="过期时间")


class PermissionCheckRequest(BaseModel):
    """权限检查请求模型"""
    resource: str = Field(..., description="资源类型")
    action: str = Field(..., description="操作类型")
    resource_id: Optional[str] = Field(None, description="特定资源ID")
    conditions: Dict[str, Any] = Field(default_factory=dict, description="额外条件")

    @validator('resource')
    def validate_resource(cls, v):
        from app.core.database import PermissionResource
        valid_resources = [r.value for r in PermissionResource]
        if v not in valid_resources:
            raise ValueError(f'无效的资源类型: {v}. 有效类型: {valid_resources}')
        return v

    @validator('action')
    def validate_action(cls, v):
        from app.core.database import PermissionAction
        valid_actions = [a.value for a in PermissionAction]
        if v not in valid_actions:
            raise ValueError(f'无效的操作类型: {v}. 有效类型: {valid_actions}')
        return v


class PermissionCheckResponse(BaseModel):
    """权限检查响应模型"""
    has_permission: bool
    resource: str
    action: str
    resource_id: Optional[str]
    details: Dict[str, Any]


# API端点实现

@router.get("/permissions", response_model=List[PermissionResponse])
async def get_permissions(
    resource: Optional[str] = Query(None, description="资源类型过滤"),
    action: Optional[str] = Query(None, description="操作类型过滤"),
    category: Optional[str] = Query(None, description="分类过滤"),
    is_system: Optional[bool] = Query(None, description="是否系统权限"),
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    获取权限列表

    支持多种过滤条件和分页
    """
    try:
        query = select(Permission)

        # 应用过滤条件
        if resource:
            query = query.where(Permission.resource == resource)
        if action:
            query = query.where(Permission.action == action)
        if category:
            query = query.where(Permission.category == category)
        if is_system is not None:
            query = query.where(Permission.is_system == is_system)

        query = query.order_by(Permission.category, Permission.name)

        result = await db.execute(query)
        permissions = result.scalars().all()

        logger.info(f"✅ 权限列表获取成功: {len(permissions)} 个权限 - 用户: {current_user.username}")
        return permissions

    except Exception as e:
        logger.error(f"❌ 获取权限列表失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取权限列表失败"
        )


@router.post("/permissions", response_model=PermissionResponse)
async def create_permission(
    permission_data: PermissionCreateRequest,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    创建新权限

    只有管理员可以创建权限
    """
    try:
        from app.core.database import PermissionResource, PermissionAction

        permission = await permission_service.create_permission(
            db=db,
            name=permission_data.name,
            description=permission_data.description,
            resource=PermissionResource(permission_data.resource),
            action=PermissionAction(permission_data.action),
            name_zh=permission_data.name_zh,
            description_zh=permission_data.description_zh,
            category=permission_data.category,
            is_system=False
        )

        return permission

    except ValidationError:
        raise
    except Exception as e:
        logger.error(f"❌ 创建权限失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="创建权限失败"
        )


@router.get("/permissions/{permission_id}", response_model=PermissionResponse)
async def get_permission(
    permission_id: str = Path(..., description="权限ID"),
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    获取权限详情

    Args:
        permission_id: 权限ID
    """
    try:
        permission = await db.get(Permission, permission_id)
        if not permission:
            raise NotFoundError("权限", permission_id)

        logger.info(f"✅ 权限详情获取成功: {permission.name} (ID: {permission_id})")
        return permission

    except NotFoundError:
        raise
    except Exception as e:
        logger.error(f"❌ 获取权限详情失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取权限详情失败"
        )


@router.put("/permissions/{permission_id}", response_model=PermissionResponse)
async def update_permission(
    permission_id: str,
    permission_data: PermissionCreateRequest,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    更新权限信息

    Args:
        permission_id: 权限ID
        permission_data: 更新的权限数据
    """
    try:
        permission = await db.get(Permission, permission_id)
        if not permission:
            raise NotFoundError("权限", permission_id)

        # 系统权限不允许修改
        if permission.is_system:
            raise ValidationError("系统权限不允许修改")

        # 更新权限信息
        update_data = permission_data.dict()
        for field, value in update_data.items():
            setattr(permission, field, value)

        permission.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(permission)

        logger.info(f"✅ 权限更新成功: {permission.name} (ID: {permission_id})")
        return permission

    except (NotFoundError, ValidationError):
        raise
    except Exception as e:
        logger.error(f"❌ 更新权限失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新权限失败"
        )


@router.delete("/permissions/{permission_id}")
async def delete_permission(
    permission_id: str,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    删除权限

    Args:
        permission_id: 权限ID
    """
    try:
        permission = await db.get(Permission, permission_id)
        if not permission:
            raise NotFoundError("权限", permission_id)

        # 系统权限不允许删除
        if permission.is_system:
            raise ValidationError("系统权限不允许删除")

        # 检查是否有角色正在使用此权限
        role_perms = await db.execute(
            select(RolePermission).where(RolePermission.permission_id == permission_id)
        )
        if role_perms.scalar_one_or_none():
            raise ValidationError("此权限正在被角色使用，无法删除")

        await db.delete(permission)
        await db.commit()

        logger.info(f"✅ 权限删除成功: {permission.name} (ID: {permission_id})")
        return {
            "message": "权限删除成功",
            "permission_id": permission_id,
            "deleted_at": datetime.utcnow().isoformat()
        }

    except (NotFoundError, ValidationError):
        raise
    except Exception as e:
        logger.error(f"❌ 删除权限失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="删除权限失败"
        )


@router.get("/roles", response_model=List[RoleResponse])
async def get_roles(
    role_type: Optional[str] = Query(None, description="角色类型过滤"),
    organization_id: Optional[str] = Query(None, description="组织ID过滤"),
    is_active: Optional[bool] = Query(None, description="是否激活"),
    is_system: Optional[bool] = Query(None, description="是否系统角色"),
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    获取角色列表

    支持多种过滤条件和分页
    """
    try:
        query = select(Role)

        # 应用过滤条件
        if role_type:
            query = query.where(Role.role_type == role_type)
        if organization_id:
            query = query.where(Role.organization_id == organization_id)
        if is_active is not None:
            query = query.where(Role.is_active == is_active)
        if is_system is not None:
            query = query.where(Role.is_system == is_system)

        query = query.order_by(Role.level, Role.name)

        result = await db.execute(query)
        roles = result.scalars().all()

        logger.info(f"✅ 角色列表获取成功: {len(roles)} 个角色 - 用户: {current_user.username}")
        return roles

    except Exception as e:
        logger.error(f"❌ 获取角色列表失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取角色列表失败"
        )


@router.post("/roles", response_model=RoleResponse)
async def create_role(
    role_data: RoleCreateRequest,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    创建新角色

    只有管理员可以创建角色
    """
    try:
        from app.core.database import RoleType

        role = await permission_service.create_role(
            db=db,
            name=role_data.name,
            description=role_data.description,
            name_zh=role_data.name_zh,
            description_zh=role_data.description_zh,
            role_type=RoleType(role_data.role_type),
            parent_role_id=role_data.parent_role_id,
            organization_id=role_data.organization_id,
            is_system=False
        )

        return role

    except ValidationError:
        raise
    except Exception as e:
        logger.error(f"❌ 创建角色失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="创建角色失败"
        )


@router.get("/roles/{role_id}", response_model=RoleResponse)
async def get_role(
    role_id: str = Path(..., description="角色ID"),
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    获取角色详情

    Args:
        role_id: 角色ID
    """
    try:
        role = await db.get(Role, role_id)
        if not role:
            raise NotFoundError("角色", role_id)

        logger.info(f"✅ 角色详情获取成功: {role.name} (ID: {role_id})")
        return role

    except NotFoundError:
        raise
    except Exception as e:
        logger.error(f"❌ 获取角色详情失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取角色详情失败"
        )


@router.put("/roles/{role_id}", response_model=RoleResponse)
async def update_role(
    role_id: str,
    role_data: RoleCreateRequest,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    更新角色信息

    Args:
        role_id: 角色ID
        role_data: 更新的角色数据
    """
    try:
        role = await db.get(Role, role_id)
        if not role:
            raise NotFoundError("角色", role_id)

        # 系统角色不允许修改
        if role.is_system:
            raise ValidationError("系统角色不允许修改")

        # 更新角色信息
        update_data = role_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(role, field, value)

        role.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(role)

        logger.info(f"✅ 角色更新成功: {role.name} (ID: {role_id})")
        return role

    except (NotFoundError, ValidationError):
        raise
    except Exception as e:
        logger.error(f"❌ 更新角色失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新角色失败"
        )


@router.delete("/roles/{role_id}")
async def delete_role(
    role_id: str,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    删除角色

    Args:
        role_id: 角色ID
    """
    try:
        role = await db.get(Role, role_id)
        if not role:
            raise NotFoundError("角色", role_id)

        # 系统角色不允许删除
        if role.is_system:
            raise ValidationError("系统角色不允许删除")

        # 检查是否有用户正在使用此角色
        user_roles = await db.execute(
            select(UserRole).where(UserRole.role_id == role_id)
        )
        if user_roles.scalar_one_or_none():
            raise ValidationError("此角色正在被用户使用，无法删除")

        await db.delete(role)
        await db.commit()

        logger.info(f"✅ 角色删除成功: {role.name} (ID: {role_id})")
        return {
            "message": "角色删除成功",
            "role_id": role_id,
            "deleted_at": datetime.utcnow().isoformat()
        }

    except (NotFoundError, ValidationError):
        raise
    except Exception as e:
        logger.error(f"❌ 删除角色失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="删除角色失败"
        )


@router.get("/roles/{role_id}/permissions", response_model=List[RolePermissionResponse])
async def get_role_permissions(
    role_id: str = Path(..., description="角色ID"),
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    获取角色的权限列表

    Args:
        role_id: 角色ID
    """
    try:
        role = await db.get(Role, role_id)
        if not role:
            raise NotFoundError("角色", role_id)

        result = await db.execute(
            select(RolePermission)
            .options(selectinload(RolePermission.permission))
            .where(RolePermission.role_id == role_id)
            .order_by(RolePermission.created_at.desc())
        )
        role_permissions = result.scalars().all()

        logger.info(f"✅ 角色权限列表获取成功: {role.name} - {len(role_permissions)} 个权限")
        return role_permissions

    except NotFoundError:
        raise
    except Exception as e:
        logger.error(f"❌ 获取角色权限列表失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取角色权限列表失败"
        )


@router.post("/roles/{role_id}/permissions", response_model=RolePermissionResponse)
async def assign_permission_to_role(
    role_id: str,
    assignment_data: RolePermissionAssignRequest,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    为角色分配权限

    Args:
        role_id: 角色ID
        assignment_data: 权限分配数据
    """
    try:
        role_permission = await permission_service.assign_permission_to_role(
            db=db,
            role_id=role_id,
            permission_id=assignment_data.permission_id,
            scope=assignment_data.scope,
            conditions=assignment_data.conditions,
            is_granted=assignment_data.is_granted,
            expires_at=assignment_data.expires_at
        )

        # 加载权限信息
        await db.refresh(role_permission, attribute_names=['permission'])

        return role_permission

    except (NotFoundError, ValidationError):
        raise
    except Exception as e:
        logger.error(f"❌ 分配角色权限失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="分配角色权限失败"
        )


@router.delete("/roles/{role_id}/permissions/{permission_id}")
async def revoke_permission_from_role(
    role_id: str,
    permission_id: str,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    从角色撤销权限

    Args:
        role_id: 角色ID
        permission_id: 权限ID
    """
    try:
        # 查找角色权限关联
        result = await db.execute(
            select(RolePermission).where(
                and_(
                    RolePermission.role_id == role_id,
                    RolePermission.permission_id == permission_id
                )
            )
        )
        role_permission = result.scalar_one_or_none()

        if not role_permission:
            raise NotFoundError("角色权限关联")

        await db.delete(role_permission)
        await db.commit()

        logger.info(f"✅ 角色权限撤销成功: 角色 {role_id} -> 权限 {permission_id}")
        return {
            "message": "权限撤销成功",
            "role_id": role_id,
            "permission_id": permission_id,
            "revoked_at": datetime.utcnow().isoformat()
        }

    except NotFoundError:
        raise
    except Exception as e:
        logger.error(f"❌ 撤销角色权限失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="撤销角色权限失败"
        )


@router.get("/users/{user_id}/roles", response_model=List[UserRoleResponse])
async def get_user_roles(
    user_id: str = Path(..., description="用户ID"),
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    获取用户的角色列表

    Args:
        user_id: 用户ID
    """
    try:
        # 检查用户是否存在
        user = await db.get(User, user_id)
        if not user:
            raise NotFoundError("用户", user_id)

        result = await db.execute(
            select(UserRole)
            .options(selectinload(UserRole.role))
            .where(
                and_(
                    UserRole.user_id == user_id,
                    UserRole.is_active == True
                )
            )
            .order_by(UserRole.created_at.desc())
        )
        user_roles = result.scalars().all()

        logger.info(f"✅ 用户角色列表获取成功: {user.username} - {len(user_roles)} 个角色")
        return user_roles

    except NotFoundError:
        raise
    except Exception as e:
        logger.error(f"❌ 获取用户角色列表失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取用户角色列表失败"
        )


@router.post("/users/{user_id}/roles", response_model=UserRoleResponse)
async def assign_role_to_user(
    user_id: str,
    assignment_data: UserRoleAssignRequest,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    为用户分配角色

    Args:
        user_id: 用户ID
        assignment_data: 角色分配数据
    """
    try:
        user_role = await permission_service.assign_role_to_user(
            db=db,
            user_id=user_id,
            role_id=assignment_data.role_id,
            assigned_by=current_user.id,
            assignment_reason=assignment_data.assignment_reason,
            expires_at=assignment_data.expires_at
        )

        # 加载角色信息
        await db.refresh(user_role, attribute_names=['role'])

        return user_role

    except (NotFoundError, ValidationError):
        raise
    except Exception as e:
        logger.error(f"❌ 分配用户角色失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="分配用户角色失败"
        )


@router.delete("/users/{user_id}/roles/{role_id}")
async def revoke_role_from_user(
    user_id: str,
    role_id: str,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    从用户撤销角色

    Args:
        user_id: 用户ID
        role_id: 角色ID
    """
    try:
        # 查找用户角色关联
        result = await db.execute(
            select(UserRole).where(
                and_(
                    UserRole.user_id == user_id,
                    UserRole.role_id == role_id,
                    UserRole.is_active == True
                )
            )
        )
        user_role = result.scalar_one_or_none()

        if not user_role:
            raise NotFoundError("用户角色关联")

        # 软删除（设置为非激活状态）
        user_role.is_active = False
        user_role.updated_at = datetime.utcnow()
        await db.commit()

        logger.info(f"✅ 用户角色撤销成功: 用户 {user_id} -> 角色 {role_id}")
        return {
            "message": "角色撤销成功",
            "user_id": user_id,
            "role_id": role_id,
            "revoked_at": datetime.utcnow().isoformat()
        }

    except NotFoundError:
        raise
    except Exception as e:
        logger.error(f"❌ 撤销用户角色失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="撤销用户角色失败"
        )


@router.post("/check", response_model=PermissionCheckResponse)
async def check_permission(
    check_request: PermissionCheckRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    检查用户权限

    用于前端或其他服务检查用户是否有特定权限
    """
    try:
        from app.core.database import PermissionResource, PermissionAction

        has_permission = await permission_service.check_permission(
            db=db,
            user_id=current_user.id,
            resource=PermissionResource(check_request.resource),
            action=PermissionAction(check_request.action),
            resource_id=check_request.resource_id,
            conditions=check_request.conditions
        )

        logger.info(
            f"权限检查 - 用户: {current_user.username}, "
            f"资源: {check_request.resource}, 操作: {check_request.action}, "
            f"结果: {has_permission}"
        )

        return PermissionCheckResponse(
            has_permission=has_permission,
            resource=check_request.resource,
            action=check_request.action,
            resource_id=check_request.resource_id,
            details={
                "user_id": current_user.id,
                "username": current_user.username,
                "checked_at": datetime.utcnow().isoformat()
            }
        )

    except Exception as e:
        logger.error(f"❌ 权限检查失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="权限检查失败"
        )


@router.get("/my-permissions", response_model=List[Dict[str, Any]])
async def get_my_permissions(
    resource: Optional[str] = Query(None, description="资源类型过滤"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取当前用户的权限列表

    用户可以查看自己拥有的所有权限
    """
    try:
        from app.core.database import PermissionResource

        resource_filter = None
        if resource:
            resource_filter = PermissionResource(resource)

        permissions = await permission_service.get_user_permissions(
            db=db,
            user_id=current_user.id,
            resource=resource_filter
        )

        logger.info(f"✅ 用户权限列表获取成功: {current_user.username} - {len(permissions)} 个权限")
        return permissions

    except Exception as e:
        logger.error(f"❌ 获取用户权限列表失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取用户权限列表失败"
        )


logger.info("✅ 权限管理API端点配置完成 - 支持完整的权限管理功能")