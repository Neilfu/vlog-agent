"""
权限系统测试
Permission System Tests

测试权限系统的各项功能，包括权限检查、角色管理、用户权限等
Test all aspects of the permission system including permission checking, role management, user permissions, etc.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from uuid import uuid4
from typing import List, Dict, Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.core.database import (
    User, Role, Permission, UserRole, RolePermission, ResourcePermission,
    PermissionResource, PermissionAction, RoleType, get_db, init_db
)
from app.services.permissions import (
    permission_service, PermissionService, init_permissions_system
)
from app.core.exceptions import ValidationError, NotFoundError, PermissionDeniedError


class TestPermissionSystem:
    """权限系统测试类"""

    @pytest.fixture(autouse=True)
    async def setup(self):
        """测试设置"""
        # 初始化数据库
        await init_db()

        # 获取数据库会话
        self.db = None
        async for db in get_db():
            self.db = db
            break

        # 创建测试用户
        self.test_user = await self._create_test_user("test_user", "test@example.com")
        self.admin_user = await self._create_test_user("admin_user", "admin@example.com")

        yield

        # 清理
        if self.db:
            await self.db.close()

    async def _create_test_user(self, username: str, email: str) -> User:
        """创建测试用户"""
        user = User(
            id=str(uuid4()),
            username=username,
            email=email,
            hashed_password="test_password_hash",
            is_active=True
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def _create_test_role(self, name: str, description: str, name_zh: str, description_zh: str) -> Role:
        """创建测试角色"""
        role = Role(
            id=str(uuid4()),
            name=name,
            description=description,
            name_zh=name_zh,
            description_zh=description_zh,
            role_type=RoleType.CUSTOM,
            is_system=False
        )
        self.db.add(role)
        await self.db.commit()
        await self.db.refresh(role)
        return role

    async def _create_test_permission(self, name: str, description: str, resource: PermissionResource,
                                   action: PermissionAction, name_zh: str, description_zh: str) -> Permission:
        """创建测试权限"""
        permission = Permission(
            id=str(uuid4()),
            name=name,
            description=description,
            resource=resource,
            action=action,
            name_zh=name_zh,
            description_zh=description_zh,
            category="test",
            is_system=False
        )
        self.db.add(permission)
        await self.db.commit()
        await self.db.refresh(permission)
        return permission

    async def test_create_permission(self):
        """测试创建权限"""
        permission = await permission_service.create_permission(
            db=self.db,
            name="test.permission",
            description="Test permission",
            resource=PermissionResource.PROJECT,
            action=PermissionAction.READ,
            name_zh="测试权限",
            description_zh="测试权限描述",
            category="test"
        )

        assert permission.name == "test.permission"
        assert permission.resource == PermissionResource.PROJECT
        assert permission.action == PermissionAction.READ
        assert permission.name_zh == "测试权限"

    async def test_create_role(self):
        """测试创建角色"""
        role = await permission_service.create_role(
            db=self.db,
            name="test_role",
            description="Test role",
            name_zh="测试角色",
            description_zh="测试角色描述"
        )

        assert role.name == "test_role"
        assert role.name_zh == "测试角色"
        assert role.role_type == RoleType.CUSTOM

    async def test_assign_permission_to_role(self):
        """测试为角色分配权限"""
        # 创建权限
        permission = await self._create_test_permission(
            "test.assign.permission", "Test assign permission",
            PermissionResource.PROJECT, PermissionAction.READ,
            "测试分配权限", "测试分配权限描述"
        )

        # 创建角色
        role = await self._create_test_role(
            "test_assign_role", "Test assign role",
            "测试分配角色", "测试分配角色描述"
        )

        # 分配权限
        role_permission = await permission_service.assign_permission_to_role(
            db=self.db,
            role_id=role.id,
            permission_id=permission.id
        )

        assert role_permission.role_id == role.id
        assert role_permission.permission_id == permission.id
        assert role_permission.is_granted == True

    async def test_assign_role_to_user(self):
        """测试为用户分配角色"""
        # 创建角色
        role = await self._create_test_role(
            "test_user_role", "Test user role",
            "测试用户角色", "测试用户角色描述"
        )

        # 分配角色
        user_role = await permission_service.assign_role_to_user(
            db=self.db,
            user_id=self.test_user.id,
            role_id=role.id,
            assigned_by=self.admin_user.id,
            assignment_reason="Test assignment"
        )

        assert user_role.user_id == self.test_user.id
        assert user_role.role_id == role.id
        assert user_role.assigned_by == self.admin_user.id
        assert user_role.assignment_reason == "Test assignment"

    async def test_check_permission_basic(self):
        """测试基本权限检查"""
        # 创建权限
        permission = await self._create_test_permission(
            "test.basic.permission", "Test basic permission",
            PermissionResource.PROJECT, PermissionAction.READ,
            "测试基本权限", "测试基本权限描述"
        )

        # 创建角色
        role = await self._create_test_role(
            "test_basic_role", "Test basic role",
            "测试基本角色", "测试基本角色描述"
        )

        # 分配权限给角色
        await permission_service.assign_permission_to_role(
            db=self.db,
            role_id=role.id,
            permission_id=permission.id
        )

        # 分配角色给用户
        await permission_service.assign_role_to_user(
            db=self.db,
            user_id=self.test_user.id,
            role_id=role.id
        )

        # 检查权限
        has_permission = await permission_service.check_permission(
            db=self.db,
            user_id=self.test_user.id,
            resource=PermissionResource.PROJECT,
            action=PermissionAction.READ
        )

        assert has_permission == True

    async def test_check_permission_denied(self):
        """测试权限拒绝"""
        # 检查不存在的权限
        has_permission = await permission_service.check_permission(
            db=self.db,
            user_id=self.test_user.id,
            resource=PermissionResource.USER,
            action=PermissionAction.DELETE
        )

        assert has_permission == False

    async def test_check_resource_permission(self):
        """测试特定资源权限检查"""
        # 创建权限
        permission = await self._create_test_permission(
            "test.resource.permission", "Test resource permission",
            PermissionResource.PROJECT, PermissionAction.READ,
            "测试资源权限", "测试资源权限描述"
        )

        # 创建资源权限
        resource_permission = ResourcePermission(
            id=str(uuid4()),
            resource_type=PermissionResource.PROJECT,
            resource_id="test_project_id",
            permission_id=permission.id,
            subject_type="user",
            subject_id=self.test_user.id,
            is_granted=True,
            created_by=self.admin_user.id
        )
        self.db.add(resource_permission)
        await self.db.commit()

        # 检查特定资源权限
        has_permission = await permission_service.check_permission(
            db=self.db,
            user_id=self.test_user.id,
            resource=PermissionResource.PROJECT,
            action=PermissionAction.READ,
            resource_id="test_project_id"
        )

        assert has_permission == True

    async def test_role_inheritance(self):
        """测试角色继承"""
        # 创建父角色
        parent_role = await self._create_test_role(
            "parent_role", "Parent role",
            "父角色", "父角色描述"
        )

        # 创建子角色
        child_role = await self._create_test_role(
            "child_role", "Child role",
            "子角色", "子角色描述"
        )
        child_role.parent_role_id = parent_role.id
        await self.db.commit()

        # 创建权限并分配给父角色
        permission = await self._create_test_permission(
            "test.inherit.permission", "Test inherit permission",
            PermissionResource.PROJECT, PermissionAction.READ,
            "测试继承权限", "测试继承权限描述"
        )

        await permission_service.assign_permission_to_role(
            db=self.db,
            role_id=parent_role.id,
            permission_id=permission.id
        )

        # 分配子角色给用户
        await permission_service.assign_role_to_user(
            db=self.db,
            user_id=self.test_user.id,
            role_id=child_role.id
        )

        # 检查权限 - 应该通过继承获得父角色的权限
        has_permission = await permission_service.check_permission(
            db=self.db,
            user_id=self.test_user.id,
            resource=PermissionResource.PROJECT,
            action=PermissionAction.READ
        )

        assert has_permission == True

    async def test_permission_expiration(self):
        """测试权限过期"""
        # 创建权限
        permission = await self._create_test_permission(
            "test.expire.permission", "Test expire permission",
            PermissionResource.PROJECT, PermissionAction.READ,
            "测试过期权限", "测试过期权限描述"
        )

        # 创建角色
        role = await self._create_test_role(
            "test_expire_role", "Test expire role",
            "测试过期角色", "测试过期角色描述"
        )

        # 分配权限（设置过期时间）
        expired_time = datetime.utcnow() - timedelta(hours=1)  # 已过期
        role_permission = await permission_service.assign_permission_to_role(
            db=self.db,
            role_id=role.id,
            permission_id=permission.id
        )
        role_permission.expires_at = expired_time
        await self.db.commit()

        # 分配角色给用户
        await permission_service.assign_role_to_user(
            db=self.db,
            user_id=self.test_user.id,
            role_id=role.id
        )

        # 检查权限 - 应该被拒绝（已过期）
        has_permission = await permission_service.check_permission(
            db=self.db,
            user_id=self.test_user.id,
            resource=PermissionResource.PROJECT,
            action=PermissionAction.READ
        )

        assert has_permission == False

    async def test_get_user_permissions(self):
        """测试获取用户权限"""
        # 创建多个权限
        permissions = []
        for i in range(3):
            permission = await self._create_test_permission(
                f"test.user.permission.{i}", f"Test user permission {i}",
                PermissionResource.PROJECT, PermissionAction.READ,
                f"测试用户权限{i}", f"测试用户权限描述{i}"
            )
            permissions.append(permission)

        # 创建角色
        role = await self._create_test_role(
            "test_user_permissions_role", "Test user permissions role",
            "测试用户权限角色", "测试用户权限角色描述"
        )

        # 分配所有权限给角色
        for permission in permissions:
            await permission_service.assign_permission_to_role(
                db=self.db,
                role_id=role.id,
                permission_id=permission.id
            )

        # 分配角色给用户
        await permission_service.assign_role_to_user(
            db=self.db,
            user_id=self.test_user.id,
            role_id=role.id
        )

        # 获取用户权限
        user_permissions = await permission_service.get_user_permissions(
            db=self.db,
            user_id=self.test_user.id
        )

        assert len(user_permissions) == 3
        assert all(p["resource"] == "project" for p in user_permissions)
        assert all(p["action"] == "read" for p in user_permissions)

    async def test_get_user_permissions_with_filter(self):
        """测试带过滤的用户权限获取"""
        # 创建不同类型的权限
        project_permission = await self._create_test_permission(
            "test.filter.project", "Test filter project",
            PermissionResource.PROJECT, PermissionAction.READ,
            "测试过滤项目", "测试过滤项目描述"
        )

        user_permission = await self._create_test_permission(
            "test.filter.user", "Test filter user",
            PermissionResource.USER, PermissionAction.READ,
            "测试过滤用户", "测试过滤用户描述"
        )

        # 创建角色
        role = await self._create_test_role(
            "test_filter_role", "Test filter role",
            "测试过滤角色", "测试过滤角色描述"
        )

        # 分配权限给角色
        await permission_service.assign_permission_to_role(
            db=self.db,
            role_id=role.id,
            permission_id=project_permission.id
        )
        await permission_service.assign_permission_to_role(
            db=self.db,
            role_id=role.id,
            permission_id=user_permission.id
        )

        # 分配角色给用户
        await permission_service.assign_role_to_user(
            db=self.db,
            user_id=self.test_user.id,
            role_id=role.id
        )

        # 获取用户权限（过滤为项目权限）
        user_permissions = await permission_service.get_user_permissions(
            db=self.db,
            user_id=self.test_user.id,
            resource=PermissionResource.PROJECT
        )

        assert len(user_permissions) == 1
        assert user_permissions[0]["resource"] == "project"

    async def test_system_permissions_creation(self):
        """测试系统权限创建"""
        # 初始化系统权限
        await permission_service.create_system_permissions(self.db)

        # 检查是否创建了系统权限
        result = await self.db.execute(
            select(Permission).where(Permission.is_system == True)
        )
        system_permissions = result.scalars().all()

        assert len(system_permissions) > 0
        assert any(p.name == "project.create" for p in system_permissions)
        assert any(p.name == "user.manage" for p in system_permissions)

    async def test_system_roles_creation(self):
        """测试系统角色创建"""
        # 初始化系统角色
        await permission_service.create_system_roles(self.db)

        # 检查是否创建了系统角色
        result = await self.db.execute(
            select(Role).where(Role.is_system == True)
        )
        system_roles = result.scalars().all()

        assert len(system_roles) > 0
        assert any(r.name == "super_admin" for r in system_roles)
        assert any(r.name == "admin" for r in system_roles)
        assert any(r.name == "content_creator" for r in system_roles)

    async def test_permission_conditions(self):
        """测试权限条件"""
        # 创建权限
        permission = await self._create_test_permission(
            "test.conditions.permission", "Test conditions permission",
            PermissionResource.PROJECT, PermissionAction.READ,
            "测试条件权限", "测试条件权限描述"
        )

        # 创建角色
        role = await self._create_test_role(
            "test_conditions_role", "Test conditions role",
            "测试条件角色", "测试条件角色描述"
        )

        # 分配权限（带条件）
        await permission_service.assign_permission_to_role(
            db=self.db,
            role_id=role.id,
            permission_id=permission.id,
            conditions={"organization_id": "test_org_123"}
        )

        # 分配角色给用户
        await permission_service.assign_role_to_user(
            db=self.db,
            user_id=self.test_user.id,
            role_id=role.id
        )

        # 检查权限（满足条件）
        has_permission = await permission_service.check_permission(
            db=self.db,
            user_id=self.test_user.id,
            resource=PermissionResource.PROJECT,
            action=PermissionAction.READ,
            conditions={"organization_id": "test_org_123"}
        )

        assert has_permission == True

        # 检查权限（不满足条件）
        has_permission = await permission_service.check_permission(
            db=self.db,
            user_id=self.test_user.id,
            resource=PermissionResource.PROJECT,
            action=PermissionAction.READ,
            conditions={"organization_id": "different_org"}
        )

        assert has_permission == False

    async def test_permission_audit_logging(self):
        """测试权限审计日志"""
        # 创建权限
        permission = await self._create_test_permission(
            "test.audit.permission", "Test audit permission",
            PermissionResource.PROJECT, PermissionAction.READ,
            "测试审计权限", "测试审计权限描述"
        )

        # 创建角色
        role = await self._create_test_role(
            "test_audit_role", "Test audit role",
            "测试审计角色", "测试审计角色描述"
        )

        # 分配权限给角色
        await permission_service.assign_permission_to_role(
            db=self.db,
            role_id=role.id,
            permission_id=permission.id
        )

        # 分配角色给用户
        await permission_service.assign_role_to_user(
            db=self.db,
            user_id=self.test_user.id,
            role_id=role.id
        )

        # 检查权限（会记录审计日志）
        has_permission = await permission_service.check_permission(
            db=self.db,
            user_id=self.test_user.id,
            resource=PermissionResource.PROJECT,
            action=PermissionAction.READ
        )

        # 检查审计日志
        from app.core.database import PermissionAuditLog
        result = await self.db.execute(
            select(PermissionAuditLog).where(
                and_(
                    PermissionAuditLog.action == "check",
                    PermissionAuditLog.subject_id == self.test_user.id,
                    PermissionAuditLog.resource_type == PermissionResource.PROJECT
                )
            )
        )
        audit_logs = result.scalars().all()

        assert len(audit_logs) > 0
        assert any(log.success == True for log in audit_logs)


@pytest.mark.asyncio
async def test_permission_system():
    """运行所有权限系统测试"""
    test_instance = TestPermissionSystem()
    await test_instance.setup()

    # 运行所有测试方法
    await test_instance.test_create_permission()
    await test_instance.test_create_role()
    await test_instance.test_assign_permission_to_role()
    await test_instance.test_assign_role_to_user()
    await test_instance.test_check_permission_basic()
    await test_instance.test_check_permission_denied()
    await test_instance.test_check_resource_permission()
    await test_instance.test_role_inheritance()
    await test_instance.test_permission_expiration()
    await test_instance.test_get_user_permissions()
    await test_instance.test_get_user_permissions_with_filter()
    await test_instance.test_system_permissions_creation()
    await test_instance.test_system_roles_creation()
    await test_instance.test_permission_conditions()
    await test_instance.test_permission_audit_logging()

    print("✅ 所有权限系统测试通过！")


if __name__ == "__main__":
    asyncio.run(test_permission_system())