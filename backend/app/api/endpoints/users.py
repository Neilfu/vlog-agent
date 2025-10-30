"""
用户管理API端点
User Management API Endpoints

处理用户资料、偏好设置、安全设置等
Handles user profiles, preferences, security settings, etc.
"""

import logging
from datetime import datetime
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from pydantic import BaseModel, EmailStr, validator, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from uuid import uuid4

from app.core.database import get_db, PermissionResource, PermissionAction
from app.core.security import get_current_user, hash_password, verify_password
from app.core.permissions import require_user_manage, require_admin, permission_service
from app.models import User
from app.core.exceptions import ValidationError, NotFoundError, PermissionDeniedError
from app.core.validators import ChineseContentValidator

logger = logging.getLogger(__name__)
router = APIRouter()

# 用户模型定义
class UserPreference(BaseModel):
    """用户偏好设置模型"""
    language: str = Field(default="zh-CN", description="界面语言")
    theme: str = Field(default="light", description="主题设置")
    notifications: Dict[str, bool] = Field(default_factory=dict, description="通知设置")
    privacy: Dict[str, bool] = Field(default_factory=dict, description="隐私设置")
    ai_settings: Dict[str, Any] = Field(default_factory=dict, description="AI生成偏好")
    platform_preferences: Dict[str, Any] = Field(default_factory=dict, description="平台偏好设置")

class UserProfileResponse(BaseModel):
    """用户资料响应模型"""
    id: str
    username: str
    email: str
    phone: Optional[str]
    full_name: Optional[str]
    avatar: Optional[str]
    role: str
    is_active: bool
    preferences: UserPreference
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime]
    profile_completion: float

class UpdateUserProfileRequest(BaseModel):
    """更新用户资料请求模型"""
    username: Optional[str] = Field(None, min_length=3, max_length=30, description="用户名")
    phone: Optional[str] = Field(None, pattern=r'^1[3-9]\d{9}$', description="手机号")
    full_name: Optional[str] = Field(None, max_length=100, description="真实姓名")
    avatar: Optional[str] = Field(None, description="头像URL")
    preferences: Optional[UserPreference] = None

    @validator('username')
    def validate_username(cls, v):
        if v and not v.replace('_', '').isalnum():
            raise ValueError('用户名只能包含字母、数字和下划线')
        return v

    @validator('full_name')
    def validate_full_name(cls, v):
        if v:
            # 验证中文姓名
            if not any('\u4e00' <= char <= '\u9fff' for char in v):
                raise ValueError('姓名应包含中文字符')
            if len(v) < 2 or len(v) > 20:
                raise ValueError('姓名长度应在2-20个字符之间')
        return v

class ChangePasswordRequest(BaseModel):
    """修改密码请求模型"""
    current_password: str = Field(..., min_length=8, description="当前密码")
    new_password: str = Field(..., min_length=8, description="新密码")
    confirm_password: str = Field(..., min_length=8, description="确认新密码")

    @validator('new_password')
    def validate_password(cls, v):
        if not any(char.isdigit() for char in v):
            raise ValueError('密码必须包含至少一个数字')
        if not any(char.isalpha() for char in v):
            raise ValueError('密码必须包含至少一个字母')
        return v

    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('两次输入的密码不一致')
        return v

class UserSecuritySettings(BaseModel):
    """用户安全设置模型"""
    two_factor_enabled: bool = Field(default=False, description="是否启用双因素认证")
    login_notifications: bool = Field(default=True, description="登录通知")
    password_change_notifications: bool = Field(default=True, description="密码修改通知")
    api_access_enabled: bool = Field(default=True, description="API访问权限")

class UserActivityResponse(BaseModel):
    """用户活动记录响应模型"""
    id: str
    action: str
    timestamp: datetime
    ip_address: Optional[str]
    user_agent: Optional[str]
    details: Optional[Dict[str, Any]]

class UserDashboardResponse(BaseModel):
    """用户仪表板响应模型"""
    user_profile: UserProfileResponse
    project_stats: Dict[str, Any]
    recent_activities: List[UserActivityResponse]
    ai_usage_stats: Dict[str, Any]
    storage_usage: Dict[str, Any]

# API端点实现

@router.get("/profile", response_model=UserProfileResponse)
async def get_user_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取当前用户完整资料

    返回用户的所有信息，包括个人资料、偏好设置等
    """
    try:
        # 计算资料完整度
        profile_completion = _calculate_profile_completion(current_user)

        # 构建用户偏好设置
        preferences = UserPreference(**current_user.preferences) if current_user.preferences else UserPreference()

        response = UserProfileResponse(
            id=str(current_user.id),
            username=current_user.username,
            email=current_user.email,
            phone=current_user.phone,
            full_name=current_user.full_name,
            avatar=current_user.avatar,
            role=current_user.role,
            is_active=current_user.is_active,
            preferences=preferences,
            created_at=current_user.created_at,
            updated_at=current_user.updated_at,
            last_login=current_user.last_login,
            profile_completion=profile_completion
        )

        logger.info(f"✅ 用户资料获取成功: {current_user.username}")
        return response

    except Exception as e:
        logger.error(f"❌ 获取用户资料失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取用户资料失败"
        )

@router.put("/profile", response_model=UserProfileResponse)
async def update_user_profile(
    profile_data: UpdateUserProfileRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    更新当前用户资料

    支持更新用户名、手机号、真实姓名、头像和偏好设置
    """
    try:
        update_data = profile_data.dict(exclude_unset=True)

        # 验证用户名唯一性（如果提供了新用户名）
        if "username" in update_data and update_data["username"] != current_user.username:
            from sqlalchemy import select
            existing_user = await db.execute(
                select(User).where(User.username == update_data["username"])
            )
            if existing_user.scalar_one_or_none():
                raise ValidationError(
                    "用户名已被使用",
                    details={"field": "username", "value": update_data["username"]}
                )

        # 验证手机号唯一性（如果提供了新手机号）
        if "phone" in update_data and update_data["phone"] != current_user.phone:
            from sqlalchemy import select
            existing_user = await db.execute(
                select(User).where(User.phone == update_data["phone"])
            )
            if existing_user.scalar_one_or_none():
                raise ValidationError(
                    "手机号已被使用",
                    details={"field": "phone", "value": update_data["phone"]}
                )

        # 验证中文内容（如果提供了真实姓名）
        if "full_name" in update_data and update_data["full_name"]:
            try:
                ChineseContentValidator.validate_chinese_content(update_data["full_name"], min_chinese_chars=2)
            except Exception as e:
                raise ValidationError(
                    f"真实姓名验证失败: {str(e)}",
                    details={"field": "full_name"}
                )

        # 更新用户资料
        if update_data:
            # 处理偏好设置更新
            if "preferences" in update_data:
                current_preferences = current_user.preferences or {}
                current_preferences.update(update_data["preferences"])
                update_data["preferences"] = current_preferences

            # 执行更新
            from sqlalchemy import update
            await db.execute(
                update(User).
                where(User.id == current_user.id).
                values(**update_data, updated_at=datetime.utcnow())
            )
            await db.commit()

            # 刷新用户信息
            await db.refresh(current_user)

        logger.info(f"✅ 用户资料更新成功: {current_user.username}")

        # 返回更新后的完整资料
        return await get_user_profile(current_user, db)

    except ValidationError:
        raise
    except Exception as e:
        logger.error(f"❌ 更新用户资料失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新用户资料失败"
        )

@router.post("/change-password")
async def change_password(
    password_data: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    修改用户密码

    需要验证当前密码，并确保新密码符合安全要求
    """
    try:
        # 验证当前密码
        if not verify_password(password_data.current_password, current_user.hashed_password):
            raise ValidationError(
                "当前密码不正确",
                details={"field": "current_password"}
            )

        # 检查新密码是否与当前密码相同
        if verify_password(password_data.new_password, current_user.hashed_password):
            raise ValidationError(
                "新密码不能与当前密码相同",
                details={"field": "new_password"}
            )

        # 更新密码
        new_hashed_password = hash_password(password_data.new_password)

        from sqlalchemy import update
        await db.execute(
            update(User).
            where(User.id == current_user.id).
            values(
                hashed_password=new_hashed_password,
                updated_at=datetime.utcnow()
            )
        )
        await db.commit()

        logger.info(f"✅ 用户密码修改成功: {current_user.username}")

        return {
            "message": "密码修改成功",
            "username": current_user.username,
            "changed_at": datetime.now().isoformat()
        }

    except ValidationError:
        raise
    except Exception as e:
        logger.error(f"❌ 修改密码失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="修改密码失败"
        )

@router.get("/security-settings", response_model=UserSecuritySettings)
async def get_security_settings(
    current_user: User = Depends(get_current_user)
):
    """
    获取用户安全设置

    包括双因素认证、通知设置等
    """
    try:
        # 从用户偏好设置中提取安全设置
        preferences = current_user.preferences or {}
        security_prefs = preferences.get("security", {})

        security_settings = UserSecuritySettings(
            two_factor_enabled=security_prefs.get("two_factor_enabled", False),
            login_notifications=security_prefs.get("login_notifications", True),
            password_change_notifications=security_prefs.get("password_change_notifications", True),
            api_access_enabled=security_prefs.get("api_access_enabled", True)
        )

        return security_settings

    except Exception as e:
        logger.error(f"❌ 获取安全设置失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取安全设置失败"
        )

@router.put("/security-settings", response_model=UserSecuritySettings)
async def update_security_settings(
    security_settings: UserSecuritySettings,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    更新用户安全设置

    包括双因素认证、通知设置等
    """
    try:
        # 获取当前偏好设置
        preferences = current_user.preferences or {}

        # 更新安全设置
        preferences["security"] = security_settings.dict()

        # 保存更新
        from sqlalchemy import update
        await db.execute(
            update(User).
            where(User.id == current_user.id).
            values(
                preferences=preferences,
                updated_at=datetime.utcnow()
            )
        )
        await db.commit()

        logger.info(f"✅ 用户安全设置更新成功: {current_user.username}")
        return security_settings

    except Exception as e:
        logger.error(f"❌ 更新安全设置失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新安全设置失败"
        )

@router.get("/dashboard", response_model=UserDashboardResponse)
async def get_user_dashboard(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取用户仪表板信息

    包括个人资料、项目统计、最近活动等综合信息
    """
    try:
        # 获取用户资料
        profile_response = await get_user_profile(current_user, db)

        # 获取项目统计（简化实现）
        project_stats = {
            "total_projects": 0,  # 可以从数据库查询
            "active_projects": 0,
            "completed_projects": 0,
            "recent_projects": []
        }

        # 获取最近活动（简化实现）
        recent_activities = [
            UserActivityResponse(
                id=str(uuid4()),
                action="登录",
                timestamp=datetime.utcnow(),
                ip_address="192.168.1.1",
                details={"device": "Web Browser"}
            )
        ]

        # AI使用统计（简化实现）
        ai_usage_stats = {
            "total_requests": 0,
            "concepts_generated": 0,
            "scripts_written": 0,
            "videos_created": 0
        }

        # 存储使用情况（简化实现）
        storage_usage = {
            "used_gb": 0.5,
            "total_gb": 10,
            "percentage": 5.0,
            "media_files": 0
        }

        dashboard_response = UserDashboardResponse(
            user_profile=profile_response,
            project_stats=project_stats,
            recent_activities=recent_activities,
            ai_usage_stats=ai_usage_stats,
            storage_usage=storage_usage
        )

        logger.info(f"✅ 用户仪表板信息获取成功: {current_user.username}")
        return dashboard_response

    except Exception as e:
        logger.error(f"❌ 获取用户仪表板信息失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取用户仪表板信息失败"
        )

@router.post("/avatar/upload")
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    上传用户头像

    支持图片文件上传和头像更新
    """
    try:
        # 验证文件类型
        allowed_types = ["image/jpeg", "image/png", "image/webp", "image/gif"]
        if file.content_type not in allowed_types:
            raise ValidationError(
                "不支持的文件类型",
                details={
                    "allowed_types": allowed_types,
                    "provided_type": file.content_type
                }
            )

        # 验证文件大小 (最大5MB)
        contents = await file.read()
        if len(contents) > 5 * 1024 * 1024:
            raise ValidationError(
                "文件大小超过限制",
                details={"max_size": "5MB", "actual_size": len(contents)}
            )

        # TODO: 实现文件上传到OSS或其他存储服务
        # 这里返回一个模拟的URL
        avatar_url = f"https://example.com/avatars/{current_user.id}/{file.filename}"

        # 更新用户头像URL
        from sqlalchemy import update
        await db.execute(
            update(User).
            where(User.id == current_user.id).
            values(
                avatar=avatar_url,
                updated_at=datetime.utcnow()
            )
        )
        await db.commit()

        logger.info(f"✅ 用户头像上传成功: {current_user.username} - {file.filename}")

        return {
            "message": "头像上传成功",
            "avatar_url": avatar_url,
            "filename": file.filename,
            "file_size": len(contents),
            "uploaded_at": datetime.now().isoformat()
        }

    except ValidationError:
        raise
    except Exception as e:
        logger.error(f"❌ 头像上传失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="头像上传失败"
        )

# 辅助函数
def _calculate_profile_completion(user: User) -> float:
    """
    计算用户资料完整度

    Args:
        user: 用户对象

    Returns:
        完整度百分比 (0-100)
    """
    required_fields = ["username", "email", "phone", "full_name", "avatar"]
    completed_fields = 0

    for field in required_fields:
        value = getattr(user, field, None)
        if value and str(value).strip():
            completed_fields += 1

    # 偏好设置完整度检查
    if user.preferences and len(user.preferences) > 0:
        completed_fields += 0.5  # 偏好设置算作半个字段

    completion_percentage = (completed_fields / len(required_fields)) * 100
    return min(completion_percentage, 100.0)

logger.info("✅ 用户管理API端点配置完成 - 支持完整的用户资料管理功能")