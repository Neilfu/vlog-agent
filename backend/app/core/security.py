"""
安全工具模块 - Security utilities module

处理JWT令牌、密码哈希、用户认证等安全相关功能
Handles JWT tokens, password hashing, user authentication and other security functions
"""

import jwt
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models import User

# 密码上下文配置 / Password context configuration
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# HTTP认证方案 / HTTP authentication scheme
security = HTTPBearer()


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    创建访问令牌
    Create access token

    Args:
        data: 要编码到令牌中的数据 / Data to encode in the token
        expires_delta: 过期时间增量 / Expiration time delta

    Returns:
        JWT访问令牌 / JWT access token
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.JWT_EXPIRATION_MINUTES)

    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access"
    })

    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: Dict[str, Any]) -> str:
    """
    创建刷新令牌
    Create refresh token

    Args:
        data: 要编码到令牌中的数据 / Data to encode in the token

    Returns:
        JWT刷新令牌 / JWT refresh token
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.JWT_REFRESH_EXPIRATION_DAYS)

    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh"
    })

    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def verify_token(token: str, token_type: str = "access") -> Optional[Dict[str, Any]]:
    """
    验证JWT令牌
    Verify JWT token

    Args:
        token: JWT令牌 / JWT token
        token_type: 令牌类型 (access/refresh) / Token type

    Returns:
        解码后的令牌数据，如果验证失败返回None / Decoded token data, None if verification fails
    """
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])

        # 验证令牌类型 / Verify token type
        if payload.get("type") != token_type:
            return None

        # 检查过期时间 / Check expiration
        exp = payload.get("exp")
        if exp is None or datetime.utcnow() > datetime.fromtimestamp(exp):
            return None

        return payload

    except jwt.ExpiredSignatureError:
        return None
    except jwt.JWTError:
        return None


def hash_password(password: str) -> str:
    """
    哈希密码
    Hash password

    Args:
        password: 明文密码 / Plain text password

    Returns:
        哈希后的密码 / Hashed password
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    验证密码
    Verify password

    Args:
        plain_password: 明文密码 / Plain text password
        hashed_password: 哈希密码 / Hashed password

    Returns:
        密码是否匹配 / Whether password matches
    """
    return pwd_context.verify(plain_password, hashed_password)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    获取当前用户
    Get current user

    Args:
        credentials: HTTP认证凭据 / HTTP authorization credentials
        db: 数据库会话 / Database session

    Returns:
        当前用户对象 / Current user object

    Raises:
        HTTPException: 如果认证失败 / If authentication fails
    """
    token = credentials.credentials
    payload = verify_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证凭据 / Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的用户ID / Invalid user ID",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 查询用户 / Query user
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在 / User not found"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户账户未激活 / User account is not active"
        )

    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """
    获取当前活跃用户
    Get current active user

    Args:
        current_user: 当前用户 / Current user

    Returns:
        当前活跃用户对象 / Current active user object
    """
    return current_user


class RoleChecker:
    """角色检查器 / Role checker"""

    def __init__(self, allowed_roles: list):
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: User = Depends(get_current_user)) -> User:
        """
        检查用户角色
        Check user role

        Args:
            current_user: 当前用户 / Current user

        Returns:
            当前用户对象 / Current user object

        Raises:
            HTTPException: 如果用户角色不允许 / If user role is not allowed
        """
        if current_user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="权限不足 / Insufficient permissions"
            )
        return current_user


# 角色检查依赖项 / Role check dependencies
require_admin = RoleChecker(["admin"])
require_creator = RoleChecker(["admin", "creator"])
require_reviewer = RoleChecker(["admin", "creator", "reviewer"])
require_client = RoleChecker(["admin", "creator", "reviewer", "client"])


def create_tokens_for_user(user: User) -> Dict[str, str]:
    """
    为用户创建访问和刷新令牌
    Create access and refresh tokens for user

    Args:
        user: 用户对象 / User object

    Returns:
        包含访问和刷新令牌的字典 / Dictionary containing access and refresh tokens
    """
    token_data = {
        "sub": str(user.id),
        "username": user.username,
        "email": user.email,
        "role": user.role
    }

    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "Bearer",
        "expires_in": settings.JWT_EXPIRATION_MINUTES * 60
    }


async def refresh_access_token(refresh_token: str, db: Session) -> Optional[Dict[str, str]]:
    """
    使用刷新令牌获取新的访问令牌
    Get new access token using refresh token

    Args:
        refresh_token: 刷新令牌 / Refresh token
        db: 数据库会话 / Database session

    Returns:
        新的访问令牌数据，如果验证失败返回None / New access token data, None if verification fails
    """
    payload = verify_token(refresh_token, token_type="refresh")

    if payload is None:
        return None

    user_id = payload.get("sub")
    if user_id is None:
        return None

    # 验证用户仍然存在 / Verify user still exists
    user = db.query(User).filter(User.id == user_id).first()
    if user is None or not user.is_active:
        return None

    # 创建新的访问令牌 / Create new access token
    access_token = create_access_token(payload)

    return {
        "access_token": access_token,
        "token_type": "Bearer",
        "expires_in": settings.JWT_EXPIRATION_MINUTES * 60
    }


def validate_token_data(token_data: Dict[str, Any]) -> bool:
    """
    验证令牌数据的有效性
    Validate token data validity

    Args:
        token_data: 令牌数据 / Token data

    Returns:
        数据是否有效 / Whether data is valid
    """
    required_fields = ["sub", "username", "email"]

    for field in required_fields:
        if field not in token_data or not token_data[field]:
            return False

    return True


# 日志配置 / Logging configuration
logger = logging.getLogger(__name__)
logger.info("✅ 安全模块加载完成 - JWT认证和密码哈希已就绪")