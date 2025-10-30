"""
认证API端点
Authentication API Endpoints

处理用户认证、JWT令牌、微信登录等
Handles user authentication, JWT tokens, WeChat login, etc.
"""

import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from pydantic import BaseModel, EmailStr, validator
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import (
    create_tokens_for_user,
    refresh_access_token,
    verify_password,
    hash_password,
    get_current_user,
    validate_token_data
)
from app.models import User
from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(tags=["认证"])
security = HTTPBearer()


# 认证相关模型 / Authentication models
class RegisterRequest(BaseModel):
    """用户注册请求模型 / User registration request model"""
    username: str
    email: EmailStr
    password: str
    phone: Optional[str] = None
    full_name: Optional[str] = None

    @validator('username')
    def validate_username(cls, v):
        if len(v) < 3 or len(v) > 30:
            raise ValueError('用户名长度必须在3-30个字符之间')
        if not v.replace('_', '').isalnum():
            raise ValueError('用户名只能包含字母、数字和下划线')
        return v

    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('密码长度必须至少为8个字符')
        if not any(char.isdigit() for char in v):
            raise ValueError('密码必须包含至少一个数字')
        if not any(char.isalpha() for char in v):
            raise ValueError('密码必须包含至少一个字母')
        return v


class LoginRequest(BaseModel):
    """用户登录请求模型 / User login request model"""
    email: Optional[str] = None
    phone: Optional[str] = None
    password: str
    remember_me: bool = False

    @validator('email', 'phone', pre=True)
    def validate_login_method(cls, v, values):
        # 确保至少提供email或phone / Ensure at least email or phone is provided
        if not values.get('email') and not values.get('phone'):
            raise ValueError('必须提供邮箱或手机号')
        return v


class TokenResponse(BaseModel):
    """令牌响应模型 / Token response model"""
    access_token: str
    refresh_token: str
    expires_in: int
    token_type: str = "Bearer"
    user: dict


class RefreshTokenRequest(BaseModel):
    """刷新令牌请求模型 / Refresh token request model"""
    refresh_token: str


class UserResponse(BaseModel):
    """用户响应模型 / User response model"""
    id: str
    username: str
    email: str
    phone: Optional[str]
    role: str
    is_active: bool
    created_at: datetime


# 认证端点 / Authentication endpoints

@router.post("/register", response_model=TokenResponse)
async def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """
    用户注册
    User registration

    Args:
        request: 注册请求数据 / Registration request data
        db: 数据库会话 / Database session

    Returns:
        包含访问令牌的响应 / Response containing access token
    """
    try:
        # 检查用户名是否已存在 / Check if username already exists
        existing_user = db.query(User).filter(User.username == request.username).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户名已存在 / Username already exists"
            )

        # 检查邮箱是否已存在 / Check if email already exists
        existing_email = db.query(User).filter(User.email == request.email).first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="邮箱已被使用 / Email already in use"
            )

        # 创建新用户 / Create new user
        hashed_password = hash_password(request.password)

        new_user = User(
            username=request.username,
            email=request.email,
            phone=request.phone,
            full_name=request.full_name,
            hashed_password=hashed_password,
            role="creator",  # 默认角色为内容创作者 / Default role is content creator
            is_active=True
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        # 创建令牌 / Create tokens
        tokens = create_tokens_for_user(new_user)

        logger.info(f"用户注册成功: {new_user.username}")

        return TokenResponse(
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            expires_in=tokens["expires_in"],
            token_type=tokens["token_type"],
            user={
                "id": str(new_user.id),
                "username": new_user.username,
                "email": new_user.email,
                "role": new_user.role
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"用户注册失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="注册失败，请稍后重试 / Registration failed, please try again later"
        )


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    用户登录 - 支持邮箱/手机号
    User login - supports email/phone number

    Args:
        request: 登录请求数据 / Login request data
        db: 数据库会话 / Database session

    Returns:
        包含访问令牌的响应 / Response containing access token
    """
    try:
        # 查找用户 / Find user
        if request.email:
            user = db.query(User).filter(User.email == request.email).first()
        elif request.phone:
            user = db.query(User).filter(User.phone == request.phone).first()
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="必须提供邮箱或手机号 / Must provide email or phone number"
            )

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户不存在 / User does not exist"
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户账户未激活 / User account is not active"
            )

        # 验证密码 / Verify password
        if not verify_password(request.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="密码错误 / Incorrect password"
            )

        # 更新最后登录时间 / Update last login time
        user.last_login = datetime.utcnow()
        db.commit()

        # 创建令牌 / Create tokens
        tokens = create_tokens_for_user(user)

        logger.info(f"用户登录成功: {user.username}")

        return TokenResponse(
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            expires_in=tokens["expires_in"],
            token_type=tokens["token_type"],
            user={
                "id": str(user.id),
                "username": user.username,
                "email": user.email,
                "role": user.role
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"用户登录失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="登录失败，请稍后重试 / Login failed, please try again later"
        )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(request: RefreshTokenRequest, db: Session = Depends(get_db)):
    """
    刷新访问令牌
    Refresh access token

    Args:
        request: 刷新令牌请求 / Refresh token request
        db: 数据库会话 / Database session

    Returns:
        新的访问令牌 / New access token
    """
    try:
        # 验证刷新令牌 / Verify refresh token
        tokens = await refresh_access_token(request.refresh_token, db)

        if tokens is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的刷新令牌 / Invalid refresh token"
            )

        logger.info("访问令牌刷新成功")

        return TokenResponse(
            access_token=tokens["access_token"],
            refresh_token=request.refresh_token,  # 返回相同的刷新令牌 / Return same refresh token
            expires_in=tokens["expires_in"],
            token_type=tokens["token_type"],
            user={}  # 刷新令牌时不返回用户信息 / Don't return user info on token refresh
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"令牌刷新失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="令牌刷新失败，请稍后重试 / Token refresh failed, please try again later"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    获取当前用户信息
    Get current user information

    Args:
        current_user: 当前用户 / Current user

    Returns:
        用户信息 / User information
    """
    return UserResponse(
        id=str(current_user.id),
        username=current_user.username,
        email=current_user.email,
        phone=current_user.phone,
        role=current_user.role,
        is_active=current_user.is_active,
        created_at=current_user.created_at
    )


@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    """
    用户登出
    User logout

    Args:
        current_user: 当前用户 / Current user

    Returns:
        登出成功消息 / Logout success message
    """
    # 在实际应用中，这里可以处理令牌黑名单等逻辑
    # In real applications, this could handle token blacklisting, etc.
    logger.info(f"用户登出: {current_user.username}")

    return {
        "message": "登出成功 / Logout successful",
        "user": current_user.username
    }


@router.get("/wechat/callback")
async def wechat_callback(code: str, state: Optional[str] = None, db: Session = Depends(get_db)):
    """
    微信登录回调
    WeChat login callback

    Args:
        code: 微信授权码 / WeChat authorization code
        state: 状态参数 / State parameter
        db: 数据库会话 / Database session

    Returns:
        登录结果 / Login result
    """
    try:
        # TODO: 实现微信OAuth2.0集成
        # TODO: Implement WeChat OAuth2.0 integration

        # 这里应该调用微信API获取用户信息
        # This should call WeChat API to get user information

        logger.info(f"微信登录回调: code={code}, state={state}")

        return {
            "message": "微信登录功能待实现 / WeChat login feature to be implemented",
            "code": code,
            "state": state
        }

    except Exception as e:
        logger.error(f"微信登录回调失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="微信登录处理失败 / WeChat login processing failed"
        )


logger.info("✅ 认证API端点配置完成 - JWT认证系统已实现")