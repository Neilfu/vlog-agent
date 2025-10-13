"""
异常处理模块
Exception Handling Module

统一异常处理和错误响应
Unified exception handling and error responses
"""

from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any, Union
from loguru import logger
from datetime import datetime


class ErrorResponse(BaseModel):
    """统一错误响应模型"""
    error: Dict[str, Any]
    message: str
    timestamp: str
    path: str
    request_id: Optional[str] = None


class ChineseAIVideoException(HTTPException):
    """自定义应用异常基类"""

    def __init__(
        self,
        status_code: int,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ):
        self.message = message
        self.error_code = error_code
        self.details = details or {}

        # 中文错误消息支持
        if not error_code:
            error_code = self._get_error_code(status_code)

        super().__init__(
            status_code=status_code,
            detail={
                "code": error_code,
                "message": message,
                "details": self.details
            },
            headers=headers
        )

    def _get_error_code(self, status_code: int) -> str:
        """根据状态码获取错误代码"""
        error_codes = {
            400: "BAD_REQUEST",
            401: "UNAUTHORIZED",
            403: "FORBIDDEN",
            404: "NOT_FOUND",
            409: "CONFLICT",
            422: "VALIDATION_ERROR",
            429: "RATE_LIMIT_EXCEEDED",
            500: "INTERNAL_SERVER_ERROR",
            502: "BAD_GATEWAY",
            503: "SERVICE_UNAVAILABLE",
        }
        return error_codes.get(status_code, "UNKNOWN_ERROR")


# 具体异常类
class ValidationError(ChineseAIVideoException):
    """数据验证异常"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            message=message,
            error_code="VALIDATION_ERROR",
            details=details
        )


class AuthenticationError(ChineseAIVideoException):
    """认证异常"""
    def __init__(self, message: str = "认证失败", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            message=message,
            error_code="AUTHENTICATION_ERROR",
            details=details
        )


class AuthorizationError(ChineseAIVideoException):
    """授权异常"""
    def __init__(self, message: str = "权限不足", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            message=message,
            error_code="AUTHORIZATION_ERROR",
            details=details
        )


class NotFoundError(ChineseAIVideoException):
    """资源未找到异常"""
    def __init__(self, resource: str, resource_id: Optional[str] = None):
        message = f"{resource}未找到"
        if resource_id:
            message = f"{resource} (ID: {resource_id}) 未找到"

        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            message=message,
            error_code="NOT_FOUND",
            details={"resource": resource, "resource_id": resource_id}
        )


class ConflictError(ChineseAIVideoException):
    """资源冲突异常"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            message=message,
            error_code="CONFLICT",
            details=details
        )


class RateLimitError(ChineseAIVideoException):
    """速率限制异常"""
    def __init__(self, message: str = "请求过于频繁", retry_after: Optional[int] = None):
        headers = {}
        if retry_after:
            headers["Retry-After"] = str(retry_after)

        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            message=message,
            error_code="RATE_LIMIT_EXCEEDED",
            details={"retry_after": retry_after},
            headers=headers
        )


class AIServiceError(ChineseAIVideoException):
    """AI服务异常"""
    def __init__(self, service: str, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            status_code=status.HTTP_502_BAD_GATEWAY,
            message=f"{service}服务异常: {message}",
            error_code="AI_SERVICE_ERROR",
            details={"service": service, **(details or {})}
        )


class DeepSeekError(AIServiceError):
    """DeepSeek服务异常"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__("DeepSeek", message, details)


class JimengError(AIServiceError):
    """即梦大模型服务异常"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__("即梦大模型", message, details)


# 异常处理函数
def setup_exception_handlers(app):
    """设置全局异常处理"""

    @app.exception_handler(ChineseAIVideoException)
    async def chinese_ai_video_exception_handler(request: Request, exc: ChineseAIVideoException):
        """处理自定义应用异常"""
        logger.error(f"应用异常: {exc.message} - 路径: {request.url} - 详情: {exc.details}")

        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": exc.error_code,
                    "message": exc.message,
                    "details": exc.details,
                    "timestamp": datetime.now().isoformat(),
                    "path": str(request.url),
                    "request_id": request.headers.get("X-Request-ID")
                }
            },
            headers=exc.headers
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        """处理HTTP异常"""
        logger.warning(f"HTTP异常: {exc.status_code} - {exc.detail} - 路径: {request.url}")

        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": f"HTTP_{exc.status_code}",
                    "message": str(exc.detail) if exc.detail else "未知错误",
                    "details": {},
                    "timestamp": datetime.now().isoformat(),
                    "path": str(request.url),
                    "request_id": request.headers.get("X-Request-ID")
                }
            },
            headers=exc.headers
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """处理未捕获的异常"""
        logger.error(f"未捕获异常: {type(exc).__name__}: {str(exc)} - 路径: {request.url}")
        logger.exception(exc)

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": "服务器内部错误，请稍后重试",
                    "details": {},
                    "timestamp": datetime.now().isoformat(),
                    "path": str(request.url),
                    "request_id": request.headers.get("X-Request-ID")
                }
            }
        )

    logger.info("✅ 异常处理配置完成 - 支持中文错误消息")


# 工具函数
def log_error(error_code: str, message: str, details: Optional[Dict[str, Any]] = None):
    """记录错误日志"""
    logger.error(f"[{error_code}] {message} - 详情: {details}")


def log_warning(error_code: str, message: str, details: Optional[Dict[str, Any]] = None):
    """记录警告日志"""
    logger.warning(f"[{error_code}] {message} - 详情: {details}")


# 验证函数
def validate_request_data(data: Dict[str, Any], required_fields: list[str]) -> None:
    """验证请求数据"""
    missing_fields = []
    for field in required_fields:
        if field not in data or data[field] is None:
            missing_fields.append(field)

    if missing_fields:
        raise ValidationError(
            f"缺少必需字段: {', '.join(missing_fields)}",
            details={"missing_fields": missing_fields}
        )