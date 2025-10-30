"""
文件存储服务模块
File Storage Service Module

集成阿里云OSS和本地文件存储
Integrates Alibaba Cloud OSS and local file storage
"""

import os
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Union
from pathlib import Path

from app.core.config import settings
from app.core.exceptions import ValidationError

try:
    import oss2
    OSS_AVAILABLE = True
except ImportError:
    OSS_AVAILABLE = False
    logging.warning("阿里云OSS SDK未安装，将使用本地存储")

try:
    from PIL import Image
    import io
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    logging.warning("PIL库未安装，缩略图功能将不可用")

logger = logging.getLogger(__name__)

class FileStorageService:
    """文件存储服务类"""

    def __init__(self):
        self.use_oss = OSS_AVAILABLE and settings.OSS_ACCESS_KEY and settings.OSS_SECRET_KEY
        self.oss_auth = None
        self.oss_bucket = None
        self.local_storage_path = Path("storage/uploads")

        if self.use_oss:
            try:
                self._init_oss_client()
                logger.info("✅ 阿里云OSS客户端初始化成功")
            except Exception as e:
                logger.error(f"阿里云OSS客户端初始化失败: {str(e)}")
                self.use_oss = False

        if not self.use_oss:
            self._init_local_storage()
            logger.info("✅ 本地文件存储初始化成功")

    def _init_oss_client(self):
        """初始化阿里云OSS客户端"""
        if not OSS_AVAILABLE:
            raise RuntimeError("阿里云OSS SDK未安装")

        # 创建认证对象
        self.oss_auth = oss2.Auth(settings.OSS_ACCESS_KEY, settings.OSS_SECRET_KEY)

        # 创建Bucket对象
        endpoint = f"https://oss-{settings.OSS_REGION}.aliyuncs.com"
        self.oss_bucket = oss2.Bucket(self.oss_auth, endpoint, settings.OSS_BUCKET)

        # 测试连接
        try:
            self.oss_bucket.get_bucket_info()
            logger.info(f"✅ 阿里云OSS连接成功 - Bucket: {settings.OSS_BUCKET}")
        except Exception as e:
            logger.error(f"阿里云OSS连接失败: {str(e)}")
            raise

    def _init_local_storage(self):
        """初始化本地存储"""
        self.local_storage_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"✅ 本地存储路径创建成功: {self.local_storage_path}")

    async def upload_file(
        self,
        file_content: bytes,
        file_path: str,
        content_type: str = "application/octet-stream",
        metadata: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        上传文件

        Args:
            file_content: 文件内容
            file_path: 文件存储路径
            content_type: 文件内容类型
            metadata: 文件元数据

        Returns:
            上传结果信息
        """
        try:
            if self.use_oss:
                return await self._upload_to_oss(file_content, file_path, content_type, metadata)
            else:
                return await self._upload_to_local(file_content, file_path, content_type)
        except Exception as e:
            logger.error(f"文件上传失败: {str(e)}")
            raise ValidationError(f"文件上传失败: {str(e)}")

    async def _upload_to_oss(
        self,
        file_content: bytes,
        file_path: str,
        content_type: str,
        metadata: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """上传到阿里云OSS"""
        try:
            # 设置文件元数据
            headers = {
                'Content-Type': content_type,
                'Cache-Control': 'max-age=31536000',  # 缓存1年
            }

            if metadata:
                for key, value in metadata.items():
                    headers[f'x-oss-meta-{key}'] = value

            # 上传文件
            result = self.oss_bucket.put_object(file_path, file_content, headers=headers)

            if result.status == 200:
                # 生成文件URL
                file_url = f"https://{settings.OSS_BUCKET}.oss-{settings.OSS_REGION}.aliyuncs.com/{file_path}"

                logger.info(f"✅ 文件上传到OSS成功: {file_path}")

                return {
                    "url": file_url,
                    "path": file_path,
                    "size": len(file_content),
                    "content_type": content_type,
                    "uploaded_at": datetime.now().isoformat(),
                    "storage_type": "oss"
                }
            else:
                raise RuntimeError(f"OSS上传失败，状态码: {result.status}")

        except Exception as e:
            logger.error(f"阿里云OSS上传失败: {str(e)}")
            raise

    async def _upload_to_local(
        self,
        file_content: bytes,
        file_path: str,
        content_type: str
    ) -> Dict[str, Any]:
        """上传到本地存储"""
        try:
            # 构建完整文件路径
            full_path = self.local_storage_path / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)

            # 写入文件
            with open(full_path, 'wb') as f:
                f.write(file_content)

            # 生成文件URL（这里需要配置Web服务器来提供文件访问）
            file_url = f"/storage/{file_path}"

            logger.info(f"✅ 文件上传到本地存储成功: {full_path}")

            return {
                "url": file_url,
                "path": str(full_path),
                "size": len(file_content),
                "content_type": content_type,
                "uploaded_at": datetime.now().isoformat(),
                "storage_type": "local"
            }

        except Exception as e:
            logger.error(f"本地文件上传失败: {str(e)}")
            raise

    async def delete_file(self, file_url: str) -> bool:
        """
        删除文件

        Args:
            file_url: 文件URL

        Returns:
            是否删除成功
        """
        try:
            if self.use_oss:
                return await self._delete_from_oss(file_url)
            else:
                return await self._delete_from_local(file_url)
        except Exception as e:
            logger.error(f"文件删除失败: {str(e)}")
            return False

    async def _delete_from_oss(self, file_url: str) -> bool:
        """从阿里云OSS删除文件"""
        try:
            # 从URL中提取文件路径
            file_path = file_url.split(f"/{settings.OSS_BUCKET}.oss-{settings.OSS_REGION}.aliyuncs.com/")[-1]

            # 删除文件
            result = self.oss_bucket.delete_object(file_path)

            if result.status == 204:
                logger.info(f"✅ 文件从OSS删除成功: {file_path}")
                return True
            else:
                logger.warning(f"文件从OSS删除失败，状态码: {result.status}")
                return False

        except Exception as e:
            logger.error(f"阿里云OSS文件删除失败: {str(e)}")
            return False

    async def _delete_from_local(self, file_url: str) -> bool:
        """从本地存储删除文件"""
        try:
            # 从URL中提取文件路径
            file_path = file_url.replace("/storage/", "")
            full_path = self.local_storage_path / file_path

            if full_path.exists():
                full_path.unlink()
                logger.info(f"✅ 文件从本地存储删除成功: {full_path}")
                return True
            else:
                logger.warning(f"文件不存在: {full_path}")
                return False

        except Exception as e:
            logger.error(f"本地文件删除失败: {str(e)}")
            return False

    async def generate_thumbnail(
        self,
        file_content: bytes,
        thumbnail_path: str,
        size: tuple = (300, 300),
        quality: int = 85
    ) -> Dict[str, Any]:
        """
        生成缩略图

        Args:
            file_content: 原始图片内容
            thumbnail_path: 缩略图存储路径
            size: 缩略图尺寸
            quality: 图片质量

        Returns:
            缩略图信息
        """
        if not PIL_AVAILABLE:
            logger.warning("PIL库未安装，无法生成缩略图")
            return {"url": None, "error": "PIL库未安装"}

        try:
            # 打开图片
            image = Image.open(io.BytesIO(file_content))

            # 转换为RGB模式（如果是RGBA等模式）
            if image.mode != 'RGB':
                image = image.convert('RGB')

            # 生成缩略图
            image.thumbnail(size, Image.Resampling.LANCZOS)

            # 保存缩略图到内存
            thumbnail_buffer = io.BytesIO()
            image.save(thumbnail_buffer, format='JPEG', quality=quality)
            thumbnail_content = thumbnail_buffer.getvalue()

            # 上传缩略图
            thumbnail_result = await self.upload_file(
                file_content=thumbnail_content,
                file_path=thumbnail_path,
                content_type="image/jpeg"
            )

            logger.info(f"✅ 缩略图生成成功: {thumbnail_path}")

            return {
                "url": thumbnail_result["url"],
                "path": thumbnail_path,
                "size": len(thumbnail_content),
                "width": image.width,
                "height": image.height,
                "generated_at": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"缩略图生成失败: {str(e)}")
            return {"url": None, "error": str(e)}

    async def get_file_info(self, file_url: str) -> Dict[str, Any]:
        """
        获取文件信息

        Args:
            file_url: 文件URL

        Returns:
            文件信息
        """
        try:
            if self.use_oss:
                return await self._get_oss_file_info(file_url)
            else:
                return await self._get_local_file_info(file_url)
        except Exception as e:
            logger.error(f"获取文件信息失败: {str(e)}")
            return {"error": str(e)}

    async def _get_oss_file_info(self, file_url: str) -> Dict[str, Any]:
        """获取阿里云OSS文件信息"""
        try:
            # 从URL中提取文件路径
            file_path = file_url.split(f"/{settings.OSS_BUCKET}.oss-{settings.OSS_REGION}.aliyuncs.com/")[-1]

            # 获取文件信息
            result = self.oss_bucket.get_object_meta(file_path)

            return {
                "url": file_url,
                "path": file_path,
                "size": int(result.headers.get('Content-Length', 0)),
                "content_type": result.headers.get('Content-Type'),
                "last_modified": result.headers.get('Last-Modified'),
                "etag": result.headers.get('ETag'),
                "storage_type": "oss"
            }

        except Exception as e:
            logger.error(f"获取阿里云OSS文件信息失败: {str(e)}")
            return {"error": str(e)}

    async def _get_local_file_info(self, file_url: str) -> Dict[str, Any]:
        """获取本地文件信息"""
        try:
            # 从URL中提取文件路径
            file_path = file_url.replace("/storage/", "")
            full_path = self.local_storage_path / file_path

            if full_path.exists():
                stat = full_path.stat()
                return {
                    "url": file_url,
                    "path": str(full_path),
                    "size": stat.st_size,
                    "content_type": None,  # 可以从文件扩展名推断
                    "last_modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    "storage_type": "local"
                }
            else:
                return {"error": "文件不存在"}

        except Exception as e:
            logger.error(f"获取本地文件信息失败: {str(e)}")
            return {"error": str(e)}

    def get_storage_info(self) -> Dict[str, Any]:
        """
        获取存储服务信息

        Returns:
            存储服务信息
        """
        return {
            "storage_type": "oss" if self.use_oss else "local",
            "oss_configured": self.use_oss,
            "bucket": settings.OSS_BUCKET if self.use_oss else None,
            "region": settings.OSS_REGION if self.use_oss else None,
            "local_path": str(self.local_storage_path) if not self.use_oss else None
        }

    async def generate_presigned_url(
        self,
        file_path: str,
        expiration: int = 3600
    ) -> Optional[str]:
        """
        生成预签名URL（用于临时访问私有文件）

        Args:
            file_path: 文件路径
            expiration: 过期时间（秒）

        Returns:
            预签名URL
        """
        if not self.use_oss:
            logger.warning("本地存储不支持预签名URL")
            return None

        try:
            # 生成预签名URL
            url = self.oss_bucket.sign_url('GET', file_path, expiration)
            return url

        except Exception as e:
            logger.error(f"生成预签名URL失败: {str(e)}")
            return None


# 创建全局文件存储服务实例
file_storage_service = FileStorageService()

async def get_file_storage_service() -> FileStorageService:
    """获取文件存储服务实例"""
    return file_storage_service