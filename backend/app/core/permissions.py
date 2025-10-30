"""
权限检查和装饰器模块
Permission Checking and Decorator Module

提供权限检查装饰器、中间件和依赖项
Provides permission checking decorators, middleware, and dependencies
"""

import logging
import functools
from typing import Optional, Dict, Any, List, Callable
from datetime import datetime

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db, PermissionResource, PermissionAction
from app.core.security import get_current_user
from app.core.exceptions import PermissionDeniedError
from app.models import User
from app.services.permissions import permission_service, PermissionService

logger = logging.getLogger(__name__)


class PermissionChecker:
    """权限检查器 - 核心权限验证逻辑"""

    def __init__(
        self,
        resource: PermissionResource,
        action: PermissionAction,
        resource_id_param: Optional[str] = None,
        resource_id_path: Optional[str] = None,
        conditions: Optional[Dict[str, Any]] = None
    ):
        """
        初始化权限检查器

        Args:
            resource: 资源类型
            action: 操作类型
            resource_id_param: 从请求参数获取资源ID的字段名
            resource_id_path: 从路径参数获取资源ID的字段名
            conditions: 额外条件
        """
        self.resource = resource
        self.action = action
        self.resource_id_param = resource_id_param
        self.resource_id_path = resource_id_path
        self.conditions = conditions or {}

    async def __call__(
        self,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
    ) -> User:
        """
        执行权限检查

        Args:
            current_user: 当前用户
            db: 数据库会话

        Returns:
            用户对象（如果检查通过）

        Raises:
            PermissionDeniedError: 如果没有权限
        """
        try:
            # 获取资源ID
            resource_id = None
            if self.resource_id_path:
                # 这里需要从请求路径中获取，实际实现中可能需要调整
                resource_id = self.resource_id_path

            # 检查权限
            has_permission = await permission_service.check_permission(
                db=db,
                user_id=current_user.id,
                resource=self.resource,
                action=self.action,
                resource_id=resource_id,
                conditions=self.conditions
            )

            if not has_permission:
                logger.warning(
                    f"权限检查失败 - 用户: {current_user.username}, "
                    f"资源: {self.resource.value}, 操作: {self.action.value}"
                )
                raise PermissionDeniedError(
                    f"您没有权限执行此操作: {self.action.value} {self.resource.value}",
                    details={
                        "resource": self.resource.value,
                        "action": self.action.value,
                        "user_id": current_user.id
                    }
                )

            logger.info(
                f"权限检查通过 - 用户: {current_user.username}, "
                f"资源: {self.resource.value}, 操作: {self.action.value}"
            )
            return current_user

        except PermissionDeniedError:
            raise
        except Exception as e:
            logger.error(f"权限检查异常: {str(e)}")
            raise PermissionDeniedError(f"权限检查失败: {str(e)}")


def require_permission(
    resource: PermissionResource,
    action: PermissionAction,
    resource_id_param: Optional[str] = None,
    resource_id_path: Optional[str] = None,
    conditions: Optional[Dict[str, Any]] = None
):
    """
    权限检查装饰器 - 用于FastAPI依赖注入

    Args:
        resource: 资源类型
        action: 操作类型
        resource_id_param: 从请求参数获取资源ID的字段名
        resource_id_path: 从路径参数获取资源ID的字段名
        conditions: 额外条件

    Returns:
        权限检查依赖项

    Example:
        @router.get("/projects/{project_id}")
        async def get_project(
            project_id: str,
            current_user: User = Depends(require_permission(
                PermissionResource.PROJECT,
                PermissionAction.READ,
                resource_id_path="project_id"
            ))
        ):
            pass
    """
    return PermissionChecker(
        resource=resource,
        action=action,
        resource_id_param=resource_id_param,
        resource_id_path=resource_id_path,
        conditions=conditions
    )


class RolePermissionChecker:
    """基于角色的权限检查器 - 向后兼容"""

    def __init__(self, allowed_roles: List[str]):
        """
        初始化角色权限检查器

        Args:
            allowed_roles: 允许的角色列表
        """
        self.allowed_roles = allowed_roles

    async def __call__(
        self,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
    ) -> User:
        """
        执行角色检查

        Args:
            current_user: 当前用户
            db: 数据库会话

        Returns:
            用户对象（如果检查通过）

        Raises:
            PermissionDeniedError: 如果角色不允许
        """
        # 这里使用向后兼容的方式，检查用户角色
        if current_user.role not in self.allowed_roles:
            raise PermissionDeniedError(
                f"权限不足 - 需要角色: {', '.join(self.allowed_roles)}, "
                f"当前角色: {current_user.role}",
                details={
                    "required_roles": self.allowed_roles,
                    "current_role": current_user.role
                }
            )

        return current_user


def require_role(allowed_roles: List[str]):
    """
    基于角色的权限检查装饰器 - 向后兼容

    Args:
        allowed_roles: 允许的角色列表

    Returns:
        角色检查依赖项

    Example:
        @router.get("/admin/users")
        async def get_users(
            current_user: User = Depends(require_role(["admin", "super_admin"]))
        ):
            pass
    """
    return RolePermissionChecker(allowed_roles=allowed_roles)


# 预定义的权限检查器 - 常用权限组合
require_admin = require_role(["admin", "super_admin"])
require_creator = require_role(["admin", "creator", "super_admin"])
require_reviewer = require_role(["admin", "reviewer", "creator", "super_admin"])
require_client = require_role(["admin", "client", "reviewer", "creator", "super_admin"])

# 用户和角色管理权限检查器
require_user_manage = require_permission(PermissionResource.USER, PermissionAction.MANAGE)
require_role_manage = require_permission(PermissionResource.SYSTEM, PermissionAction.MANAGE)

# 细粒度权限检查器
require_project_read = require_permission(PermissionResource.PROJECT, PermissionAction.READ)
require_project_write = require_permission(PermissionResource.PROJECT, PermissionAction.UPDATE)
require_project_create = require_permission(PermissionResource.PROJECT, PermissionAction.CREATE)
require_project_delete = require_permission(PermissionResource.PROJECT, PermissionAction.DELETE)
require_project_manage = require_permission(PermissionResource.PROJECT, PermissionAction.MANAGE)

require_user_read = require_permission(PermissionResource.USER, PermissionAction.READ)
require_user_write = require_permission(PermissionResource.USER, PermissionAction.UPDATE)
require_user_create = require_permission(PermissionResource.USER, PermissionAction.CREATE)
require_user_delete = require_permission(PermissionResource.USER, PermissionAction.DELETE)
require_user_manage = require_permission(PermissionResource.USER, PermissionAction.MANAGE)

require_asset_read = require_permission(PermissionResource.ASSET, PermissionAction.READ)
require_asset_write = require_permission(PermissionResource.ASSET, PermissionAction.UPDATE)
require_asset_create = require_permission(PermissionResource.ASSET, PermissionAction.CREATE)
require_asset_delete = require_permission(PermissionResource.ASSET, PermissionAction.DELETE)

require_ai_execute = require_permission(PermissionResource.AI_MODEL, PermissionAction.EXECUTE)
require_ai_manage = require_permission(PermissionResource.AI_MODEL, PermissionAction.MANAGE)

require_system_read = require_permission(PermissionResource.SYSTEM, PermissionAction.READ)
require_system_manage = require_permission(PermissionResource.SYSTEM, PermissionAction.MANAGE)


class PermissionMiddleware:
    """权限中间件 - 用于全局权限检查"""

    def __init__(self, app):
        """
        初始化权限中间件

        Args:
            app: FastAPI应用实例
        """
        self.app = app

    async def __call__(self, scope, receive, send):
        """
        执行权限检查

        Args:
            scope: ASGI作用域
            receive: 接收函数
            send: 发送函数
        """
        # 这里可以实现全局权限检查逻辑
        # 例如基于路径模式的权限检查
        await self.app(scope, receive, send)


def create_resource_permission_checker(
    resource_type: PermissionResource,
    actions: List[PermissionAction],
    allow_multiple: bool = False
):
    """
    创建资源权限检查器

    Args:
        resource_type: 资源类型
        actions: 允许的操作列表
        allow_multiple: 是否允许多个操作中的任意一个

    Returns:
        权限检查函数
    """
    async def check_resource_permissions(
        resource_id: str,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
    ) -> bool:
        """检查资源权限"""
        for action in actions:
            has_permission = await permission_service.check_permission(
                db=db,
                user_id=current_user.id,
                resource=resource_type,
                action=action,
                resource_id=resource_id
            )

            if allow_multiple and has_permission:
                return True
            elif not allow_multiple and not has_permission:
                return False

        return not allow_multiple

    return check_resource_permissions


class PermissionValidator:
    """权限验证器 - 用于复杂权限场景"""

    def __init__(self, user: User, db: AsyncSession, permission_service: PermissionService):
        """
        初始化权限验证器

        Args:
            user: 用户对象
            db: 数据库会话
            permission_service: 权限服务
        """
        self.user = user
        self.db = db
        self.permission_service = permission_service

    async def can_access_project(self, project_id: str) -> bool:
        """检查是否可以访问项目"""
        return await self.permission_service.check_permission(
            db=self.db,
            user_id=self.user.id,
            resource=PermissionResource.PROJECT,
            action=PermissionAction.READ,
            resource_id=project_id
        )

    async def can_edit_project(self, project_id: str) -> bool:
        """检查是否可以编辑项目"""
        return await self.permission_service.check_permission(
            db=self.db,
            user_id=self.user.id,
            resource=PermissionResource.PROJECT,
            action=PermissionAction.UPDATE,
            resource_id=project_id
        )

    async def can_delete_project(self, project_id: str) -> bool:
        """检查是否可以删除项目"""
        return await self.permission_service.check_permission(
            db=self.db,
            user_id=self.user.id,
            resource=PermissionResource.PROJECT,
            action=PermissionAction.DELETE,
            resource_id=project_id
        )

    async def can_manage_users(self) -> bool:
        """检查是否可以管理用户"""
        return await self.permission_service.check_permission(
            db=self.db,
            user_id=self.user.id,
            resource=PermissionResource.USER,
            action=PermissionAction.MANAGE
        )

    async def can_use_ai_models(self) -> bool:
        """检查是否可以使用AI模型"""
        return await self.permission_service.check_permission(
            db=self.db,
            user_id=self.user.id,
            resource=PermissionResource.AI_MODEL,
            action=PermissionAction.EXECUTE
        )

    async def get_accessible_projects(self) -> List[str]:
        """获取用户可访问的项目列表"""
        # 这里可以实现更复杂的逻辑来获取用户有权限访问的项目ID列表
        # 目前返回空列表，需要根据实际情况实现
        return []

    async def get_manageable_users(self) -> List[str]:
        """获取用户可以管理的用户列表"""
        # 这里可以实现更复杂的逻辑来获取用户可以管理的用户ID列表
        # 目前返回空列表，需要根据实际情况实现
        return []


def get_permission_validator(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> PermissionValidator:
    """
    获取权限验证器

    Args:
        current_user: 当前用户
        db: 数据库会话

    Returns:
        权限验证器实例
    """
    return PermissionValidator(current_user, db, permission_service)


# 工具函数
def merge_conditions(base_conditions: Dict[str, Any], *additional_conditions: Dict[str, Any]) -> Dict[str, Any]:
    """
    合并多个条件字典

    Args:
        base_conditions: 基础条件
        *additional_conditions: 额外条件

    Returns:
        合并后的条件
    """
    merged = base_conditions.copy()
    for conditions in additional_conditions:
        if conditions:
            merged.update(conditions)
    return merged


def create_condition_filter(**kwargs) -> Dict[str, Any]:
    """
    创建条件过滤器

    Args:
        **kwargs: 条件键值对

    Returns:
        条件字典
    """
    return {k: v for k, v in kwargs.items() if v is not None}


logger.info("✅ 权限检查模块加载完成 - 支持细粒度权限控制")