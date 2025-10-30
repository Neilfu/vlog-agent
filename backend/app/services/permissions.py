"""
权限服务模块
Permission Service Module

处理细粒度权限管理、角色继承、资源权限控制等
Handles fine-grained permission management, role inheritance, resource permission control
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Set, Union
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from sqlalchemy.orm import selectinload

from app.core.database import (
    User, Role, Permission, UserRole, RolePermission,
    ResourcePermission, PermissionAuditLog,
    PermissionResource, PermissionAction, RoleType
)
from app.core.exceptions import ValidationError, NotFoundError, PermissionDeniedError

logger = logging.getLogger(__name__)


class PermissionService:
    """权限服务类 - 核心权限管理逻辑"""

    def __init__(self):
        self._permission_cache = {}
        self._role_cache = {}
        self._cache_ttl = 300  # 5分钟缓存

    async def create_permission(
        self,
        db: AsyncSession,
        name: str,
        description: str,
        resource: PermissionResource,
        action: PermissionAction,
        name_zh: str,
        description_zh: str,
        category: str = "general",
        is_system: bool = False
    ) -> Permission:
        """
        创建权限

        Args:
            db: 数据库会话
            name: 权限名称（英文）
            description: 权限描述（英文）
            resource: 资源类型
            action: 操作类型
            name_zh: 权限名称（中文）
            description_zh: 权限描述（中文）
            category: 权限分类
            is_system: 是否为系统权限

        Returns:
            创建的权限对象
        """
        try:
            permission = Permission(
                id=str(uuid4()),
                name=name,
                description=description,
                resource=resource,
                action=action,
                name_zh=name_zh,
                description_zh=description_zh,
                category=category,
                is_system=is_system
            )

            db.add(permission)
            await db.commit()
            await db.refresh(permission)

            logger.info(f"✅ 权限创建成功: {name} ({name_zh})")
            return permission

        except Exception as e:
            await db.rollback()
            logger.error(f"❌ 权限创建失败: {str(e)}")
            raise ValidationError(f"权限创建失败: {str(e)}")

    async def create_role(
        self,
        db: AsyncSession,
        name: str,
        description: str,
        name_zh: str,
        description_zh: str,
        role_type: RoleType = RoleType.CUSTOM,
        parent_role_id: Optional[str] = None,
        organization_id: Optional[str] = None,
        is_system: bool = False
    ) -> Role:
        """
        创建角色

        Args:
            db: 数据库会话
            name: 角色名称（英文）
            description: 角色描述（英文）
            name_zh: 角色名称（中文）
            description_zh: 角色描述（中文）
            role_type: 角色类型
            parent_role_id: 父角色ID（用于继承）
            organization_id: 组织ID
            is_system: 是否为系统角色

        Returns:
            创建的角色对象
        """
        try:
            # 计算角色级别
            level = 0
            if parent_role_id:
                parent_role = await db.get(Role, parent_role_id)
                if parent_role:
                    level = parent_role.level + 1

            role = Role(
                id=str(uuid4()),
                name=name,
                description=description,
                name_zh=name_zh,
                description_zh=description_zh,
                role_type=role_type,
                parent_role_id=parent_role_id,
                level=level,
                organization_id=organization_id,
                is_system=is_system
            )

            db.add(role)
            await db.commit()
            await db.refresh(role)

            logger.info(f"✅ 角色创建成功: {name} ({name_zh})")
            return role

        except Exception as e:
            await db.rollback()
            logger.error(f"❌ 角色创建失败: {str(e)}")
            raise ValidationError(f"角色创建失败: {str(e)}")

    async def assign_permission_to_role(
        self,
        db: AsyncSession,
        role_id: str,
        permission_id: str,
        scope: Optional[str] = None,
        conditions: Optional[Dict[str, Any]] = None,
        is_granted: bool = True,
        expires_at: Optional[datetime] = None
    ) -> RolePermission:
        """
        为角色分配权限

        Args:
            db: 数据库会话
            role_id: 角色ID
            permission_id: 权限ID
            scope: 权限范围
            conditions: 额外条件
            is_granted: 是否授予权限
            expires_at: 过期时间

        Returns:
            角色权限关联对象
        """
        try:
            # 检查角色和权限是否存在
            role = await db.get(Role, role_id)
            permission = await db.get(Permission, permission_id)

            if not role:
                raise NotFoundError("角色", role_id)
            if not permission:
                raise NotFoundError("权限", permission_id)

            # 检查是否已存在
            existing = await db.execute(
                select(RolePermission).where(
                    and_(
                        RolePermission.role_id == role_id,
                        RolePermission.permission_id == permission_id
                    )
                )
            )
            if existing.scalar_one_or_none():
                raise ValidationError("该角色已拥有此权限")

            role_permission = RolePermission(
                id=str(uuid4()),
                role_id=role_id,
                permission_id=permission_id,
                scope=scope,
                conditions=conditions or {},
                is_granted=is_granted,
                expires_at=expires_at
            )

            db.add(role_permission)
            await db.commit()
            await db.refresh(role_permission)

            logger.info(f"✅ 权限分配成功: 角色 {role.name} -> 权限 {permission.name}")
            return role_permission

        except Exception as e:
            await db.rollback()
            logger.error(f"❌ 权限分配失败: {str(e)}")
            raise ValidationError(f"权限分配失败: {str(e)}")

    async def assign_role_to_user(
        self,
        db: AsyncSession,
        user_id: str,
        role_id: str,
        assigned_by: Optional[str] = None,
        assignment_reason: Optional[str] = None,
        expires_at: Optional[datetime] = None
    ) -> UserRole:
        """
        为用户分配角色

        Args:
            db: 数据库会话
            user_id: 用户ID
            role_id: 角色ID
            assigned_by: 分配者ID
            assignment_reason: 分配原因
            expires_at: 过期时间

        Returns:
            用户角色关联对象
        """
        try:
            # 检查用户和角色是否存在
            user = await db.get(User, user_id)
            role = await db.get(Role, role_id)

            if not user:
                raise NotFoundError("用户", user_id)
            if not role:
                raise NotFoundError("角色", role_id)

            # 检查是否已存在
            existing = await db.execute(
                select(UserRole).where(
                    and_(
                        UserRole.user_id == user_id,
                        UserRole.role_id == role_id,
                        UserRole.is_active == True
                    )
                )
            )
            if existing.scalar_one_or_none():
                raise ValidationError("该用户已拥有此角色")

            user_role = UserRole(
                id=str(uuid4()),
                user_id=user_id,
                role_id=role_id,
                assigned_by=assigned_by,
                assignment_reason=assignment_reason,
                expires_at=expires_at
            )

            db.add(user_role)
            await db.commit()
            await db.refresh(user_role)

            logger.info(f"✅ 角色分配成功: 用户 {user.username} -> 角色 {role.name}")
            return user_role

        except Exception as e:
            await db.rollback()
            logger.error(f"❌ 角色分配失败: {str(e)}")
            raise ValidationError(f"角色分配失败: {str(e)}")

    async def check_permission(
        self,
        db: AsyncSession,
        user_id: str,
        resource: PermissionResource,
        action: PermissionAction,
        resource_id: Optional[str] = None,
        conditions: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        检查用户权限（核心方法）

        Args:
            db: 数据库会话
            user_id: 用户ID
            resource: 资源类型
            action: 操作类型
            resource_id: 特定资源ID（可选）
            conditions: 额外条件

        Returns:
            是否有权限
        """
        try:
            # 获取用户所有角色
            user_roles = await self._get_user_roles(db, user_id)
            if not user_roles:
                return False

            role_ids = [ur.role_id for ur in user_roles]

            # 检查资源特定权限
            if resource_id:
                has_resource_perm = await self._check_resource_permission(
                    db, user_id, resource, resource_id, action, role_ids
                )
                if has_resource_perm is not None:
                    return has_resource_perm

            # 检查角色权限
            has_role_perm = await self._check_role_permission(
                db, role_ids, resource, action, conditions
            )

            # 记录审计日志
            await self._log_permission_check(
                db, user_id, resource, resource_id, action, has_role_perm
            )

            return has_role_perm

        except Exception as e:
            logger.error(f"❌ 权限检查失败: {str(e)}")
            return False

    async def _get_user_roles(self, db: AsyncSession, user_id: str) -> List[UserRole]:
        """获取用户所有有效角色"""
        result = await db.execute(
            select(UserRole)
            .options(selectinload(UserRole.role))
            .where(
                and_(
                    UserRole.user_id == user_id,
                    UserRole.is_active == True,
                    or_(
                        UserRole.expires_at.is_(None),
                        UserRole.expires_at > datetime.utcnow()
                    )
                )
            )
        )
        return result.scalars().all()

    async def _check_role_permission(
        self,
        db: AsyncSession,
        role_ids: List[str],
        resource: PermissionResource,
        action: PermissionAction,
        conditions: Optional[Dict[str, Any]]
    ) -> bool:
        """检查角色权限"""
        # 获取所有相关权限（包括继承的父角色权限）
        all_role_ids = await self._get_role_hierarchy(db, role_ids)

        result = await db.execute(
            select(RolePermission)
            .options(selectinload(RolePermission.permission))
            .where(
                and_(
                    RolePermission.role_id.in_(all_role_ids),
                    RolePermission.is_granted == True,
                    or_(
                        RolePermission.expires_at.is_(None),
                        RolePermission.expires_at > datetime.utcnow()
                    )
                )
            )
        )

        role_permissions = result.scalars().all()

        # 检查是否有匹配的权限
        for rp in role_permissions:
            permission = rp.permission
            if (permission.resource == resource and
                permission.action == action):

                # 检查额外条件
                if conditions and rp.conditions:
                    if not self._check_conditions(conditions, rp.conditions):
                        continue

                return True

        return False

    async def _check_resource_permission(
        self,
        db: AsyncSession,
        user_id: str,
        resource: PermissionResource,
        resource_id: str,
        action: PermissionAction,
        role_ids: List[str]
    ) -> Optional[bool]:
        """检查特定资源权限"""
        # 检查直接的用户资源权限
        result = await db.execute(
            select(ResourcePermission)
            .where(
                and_(
                    ResourcePermission.resource_type == resource,
                    ResourcePermission.resource_id == resource_id,
                    ResourcePermission.subject_type == "user",
                    ResourcePermission.subject_id == user_id,
                    ResourcePermission.is_granted == True,
                    or_(
                        ResourcePermission.expires_at.is_(None),
                        ResourcePermission.expires_at > datetime.utcnow()
                    )
                )
            )
        )

        user_resource_perms = result.scalars().all()
        for urp in user_resource_perms:
            # 检查权限是否匹配
            if urp.permission.action == action:
                return True

        # 检查角色的资源权限
        result = await db.execute(
            select(ResourcePermission)
            .where(
                and_(
                    ResourcePermission.resource_type == resource,
                    ResourcePermission.resource_id == resource_id,
                    ResourcePermission.subject_type == "role",
                    ResourcePermission.subject_id.in_(role_ids),
                    ResourcePermission.is_granted == True,
                    or_(
                        ResourcePermission.expires_at.is_(None),
                        ResourcePermission.expires_at > datetime.utcnow()
                    )
                )
            )
        )

        role_resource_perms = result.scalars().all()
        for rrp in role_resource_perms:
            if rrp.permission.action == action:
                return True

        return None

    async def _get_role_hierarchy(self, db: AsyncSession, role_ids: List[str]) -> List[str]:
        """获取角色层级结构（包括所有父角色）"""
        all_role_ids = set(role_ids)

        for role_id in role_ids:
            current_id = role_id
            while current_id:
                role = await db.get(Role, current_id)
                if role and role.parent_role_id:
                    all_role_ids.add(role.parent_role_id)
                    current_id = role.parent_role_id
                else:
                    break

        return list(all_role_ids)

    def _check_conditions(self, user_conditions: Dict[str, Any], permission_conditions: Dict[str, Any]) -> bool:
        """检查条件是否匹配"""
        for key, required_value in permission_conditions.items():
            user_value = user_conditions.get(key)
            if user_value != required_value:
                return False
        return True

    async def _log_permission_check(
        self,
        db: AsyncSession,
        user_id: str,
        resource: PermissionResource,
        resource_id: Optional[str],
        action: PermissionAction,
        success: bool
    ):
        """记录权限检查日志"""
        try:
            log_entry = PermissionAuditLog(
                id=str(uuid4()),
                action="check",
                resource_type=resource,
                resource_id=resource_id,
                subject_type="user",
                subject_id=user_id,
                performed_by=user_id,
                success=success,
                details={
                    "action": action.value,
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
            db.add(log_entry)
            await db.commit()
        except Exception as e:
            logger.warning(f"记录权限审计日志失败: {str(e)}")

    async def get_user_permissions(
        self,
        db: AsyncSession,
        user_id: str,
        resource: Optional[PermissionResource] = None
    ) -> List[Dict[str, Any]]:
        """
        获取用户的所有权限

        Args:
            db: 数据库会话
            user_id: 用户ID
            resource: 资源类型过滤（可选）

        Returns:
            权限列表
        """
        try:
            # 获取用户角色
            user_roles = await self._get_user_roles(db, user_id)
            if not user_roles:
                return []

            role_ids = [ur.role_id for ur in user_roles]
            all_role_ids = await self._get_role_hierarchy(db, role_ids)

            # 查询权限
            query = select(RolePermission).options(
                selectinload(RolePermission.permission),
                selectinload(RolePermission.role)
            ).where(
                and_(
                    RolePermission.role_id.in_(all_role_ids),
                    RolePermission.is_granted == True,
                    or_(
                        RolePermission.expires_at.is_(None),
                        RolePermission.expires_at > datetime.utcnow()
                    )
                )
            )

            if resource:
                query = query.join(Permission).where(Permission.resource == resource)

            result = await db.execute(query)
            role_permissions = result.scalars().all()

            # 转换为标准格式
            permissions = []
            for rp in role_permissions:
                permissions.append({
                    "permission_id": rp.permission_id,
                    "permission_name": rp.permission.name,
                    "permission_name_zh": rp.permission.name_zh,
                    "resource": rp.permission.resource.value,
                    "action": rp.permission.action.value,
                    "role_id": rp.role_id,
                    "role_name": rp.role.name,
                    "scope": rp.scope,
                    "conditions": rp.conditions,
                    "expires_at": rp.expires_at.isoformat() if rp.expires_at else None
                })

            return permissions

        except Exception as e:
            logger.error(f"❌ 获取用户权限失败: {str(e)}")
            return []

    async def create_system_permissions(self, db: AsyncSession):
        """创建系统默认权限"""
        system_permissions = [
            # 用户管理权限
            ("user.create", "Create users", PermissionResource.USER, PermissionAction.CREATE, "创建用户", "创建新用户账户"),
            ("user.read", "Read users", PermissionResource.USER, PermissionAction.READ, "查看用户", "查看用户信息和列表"),
            ("user.update", "Update users", PermissionResource.USER, PermissionAction.UPDATE, "更新用户", "更新用户信息"),
            ("user.delete", "Delete users", PermissionResource.USER, PermissionAction.DELETE, "删除用户", "删除用户账户"),
            ("user.manage", "Manage users", PermissionResource.USER, PermissionAction.MANAGE, "管理用户", "全面管理用户账户"),

            # 项目管理权限
            ("project.create", "Create projects", PermissionResource.PROJECT, PermissionAction.CREATE, "创建项目", "创建新项目"),
            ("project.read", "Read projects", PermissionResource.PROJECT, PermissionAction.READ, "查看项目", "查看项目信息和列表"),
            ("project.update", "Update projects", PermissionResource.PROJECT, PermissionAction.UPDATE, "更新项目", "更新项目信息"),
            ("project.delete", "Delete projects", PermissionResource.PROJECT, PermissionAction.DELETE, "删除项目", "删除项目"),
            ("project.manage", "Manage projects", PermissionResource.PROJECT, PermissionAction.MANAGE, "管理项目", "全面管理项目"),
            ("project.approve", "Approve projects", PermissionResource.PROJECT, PermissionAction.APPROVE, "审批项目", "审批项目内容"),

            # 资源管理权限
            ("asset.create", "Create assets", PermissionResource.ASSET, PermissionAction.CREATE, "创建资源", "上传和创建媒体资源"),
            ("asset.read", "Read assets", PermissionResource.ASSET, PermissionAction.READ, "查看资源", "查看媒体资源"),
            ("asset.update", "Update assets", PermissionResource.ASSET, PermissionAction.UPDATE, "更新资源", "更新媒体资源信息"),
            ("asset.delete", "Delete assets", PermissionResource.ASSET, PermissionAction.DELETE, "删除资源", "删除媒体资源"),

            # AI模型权限
            ("ai_model.execute", "Execute AI models", PermissionResource.AI_MODEL, PermissionAction.EXECUTE, "执行AI模型", "使用AI模型生成内容"),
            ("ai_model.manage", "Manage AI models", PermissionResource.AI_MODEL, PermissionAction.MANAGE, "管理AI模型", "管理AI模型配置"),

            # 系统管理权限
            ("system.manage", "Manage system", PermissionResource.SYSTEM, PermissionAction.MANAGE, "管理系统", "系统级管理权限"),
            ("system.read", "Read system info", PermissionResource.SYSTEM, PermissionAction.READ, "查看系统信息", "查看系统信息和状态"),
        ]

        try:
            for name, description, resource, action, name_zh, description_zh in system_permissions:
                # 检查是否已存在
                existing = await db.execute(
                    select(Permission).where(Permission.name == name)
                )
                if not existing.scalar_one_or_none():
                    await self.create_permission(
                        db, name, description, resource, action,
                        name_zh, description_zh, category="system", is_system=True
                    )

            logger.info("✅ 系统默认权限创建完成")
        except Exception as e:
            logger.error(f"❌ 创建系统权限失败: {str(e)}")

    async def create_system_roles(self, db: AsyncSession):
        """创建系统默认角色"""
        system_roles = [
            ("super_admin", "Super Administrator", "超级管理员", "系统超级管理员，拥有所有权限", RoleType.SYSTEM),
            ("admin", "Administrator", "管理员", "系统管理员，拥有大部分管理权限", RoleType.SYSTEM),
            ("project_manager", "Project Manager", "项目经理", "项目管理角色，负责项目创建和管理", RoleType.SYSTEM),
            ("content_creator", "Content Creator", "内容创作者", "内容创作角色，可以创建和编辑内容", RoleType.SYSTEM),
            ("reviewer", "Content Reviewer", "内容审核员", "内容审核角色，负责审核内容质量", RoleType.SYSTEM),
            ("client", "Client", "客户", "客户角色，可以查看和评论内容", RoleType.SYSTEM),
        ]

        try:
            for name, description, name_zh, description_zh, role_type in system_roles:
                # 检查是否已存在
                existing = await db.execute(
                    select(Role).where(Role.name == name)
                )
                if not existing.scalar_one_or_none():
                    await self.create_role(
                        db, name, description, name_zh, description_zh, role_type, is_system=True
                    )

            logger.info("✅ 系统默认角色创建完成")
        except Exception as e:
            logger.error(f"❌ 创建系统角色失败: {str(e)}")

    async def assign_role_permissions(self, db: AsyncSession):
        """为系统角色分配默认权限"""
        role_permission_mappings = {
            "super_admin": [  # 超级管理员拥有所有权限
                "user.create", "user.read", "user.update", "user.delete", "user.manage",
                "project.create", "project.read", "project.update", "project.delete", "project.manage", "project.approve",
                "asset.create", "asset.read", "asset.update", "asset.delete",
                "ai_model.execute", "ai_model.manage",
                "system.manage", "system.read"
            ],
            "admin": [  # 管理员拥有大部分权限
                "user.create", "user.read", "user.update", "user.manage",
                "project.create", "project.read", "project.update", "project.manage", "project.approve",
                "asset.create", "asset.read", "asset.update", "asset.delete",
                "ai_model.execute", "ai_model.manage",
                "system.read"
            ],
            "project_manager": [  # 项目经理
                "project.create", "project.read", "project.update", "project.manage",
                "asset.create", "asset.read", "asset.update", "asset.delete",
                "ai_model.execute"
            ],
            "content_creator": [  # 内容创作者
                "project.create", "project.read", "project.update",
                "asset.create", "asset.read", "asset.update",
                "ai_model.execute"
            ],
            "reviewer": [  # 审核员
                "project.read", "project.update", "project.approve",
                "asset.read", "asset.update"
            ],
            "client": [  # 客户
                "project.read",
                "asset.read"
            ]
        }

        try:
            for role_name, permission_names in role_permission_mappings.items():
                # 获取角色
                role_result = await db.execute(select(Role).where(Role.name == role_name))
                role = role_result.scalar_one_or_none()
                if not role:
                    continue

                for permission_name in permission_names:
                    # 获取权限
                    perm_result = await db.execute(select(Permission).where(Permission.name == permission_name))
                    permission = perm_result.scalar_one_or_none()
                    if not permission:
                        continue

                    # 分配权限
                    try:
                        await self.assign_permission_to_role(db, role.id, permission.id)
                    except ValidationError:
                        # 权限已存在，跳过
                        continue

            logger.info("✅ 系统角色权限分配完成")
        except Exception as e:
            logger.error(f"❌ 分配角色权限失败: {str(e)}")


# 创建全局权限服务实例
permission_service = PermissionService()


async def get_permission_service() -> PermissionService:
    """获取权限服务实例"""
    return permission_service


async def init_permissions_system(db: AsyncSession):
    """初始化权限系统 - 创建默认权限和角色"""
    try:
        logger.info("开始初始化权限系统...")

        # 创建系统权限
        await permission_service.create_system_permissions(db)

        # 创建系统角色
        await permission_service.create_system_roles(db)

        # 分配角色权限
        await permission_service.assign_role_permissions(db)

        logger.info("✅ 权限系统初始化完成")

    except Exception as e:
        logger.error(f"❌ 权限系统初始化失败: {str(e)}")
        raise


logger.info("✅ 权限服务模块加载完成 - 支持细粒度权限管理")