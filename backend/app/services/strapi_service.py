"""
Strapi CMS服务集成模块
Strapi CMS Service Integration Module

处理与Strapi内容管理系统的集成，包括内容同步、webhook处理等
Handles integration with Strapi content management system, including content sync, webhook handling, etc.
"""

import logging
import httpx
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime
from uuid import uuid4
from pathlib import Path

from app.core.config import settings
from app.core.exceptions import ValidationError, NotFoundError, ExternalServiceError

logger = logging.getLogger(__name__)


class StrapiService:
    """Strapi服务类 - 处理与Strapi CMS的集成"""

    def __init__(self):
        self.base_url = settings.STRAPI_URL or "http://localhost:1337"
        self.api_token = settings.STRAPI_API_TOKEN
        self.timeout = 30.0
        self.max_retries = 3
        self.retry_delay = 1.0

        # 内容类型映射
        self.content_types = {
            "project": "projects",
            "creative_idea": "creative-ideas",
            "script": "scripts",
            "storyboard": "storyboards",
            "media_asset": "media-assets",
            "final_video": "final-videos"
        }

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        发送HTTP请求到Strapi API

        Args:
            method: HTTP方法 (GET, POST, PUT, DELETE)
            endpoint: API端点
            data: 请求数据
            files: 文件数据
            params: 查询参数

        Returns:
            API响应数据

        Raises:
            ExternalServiceError: 当请求失败时
        """
        url = f"{self.base_url}/api/{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }

        for attempt in range(self.max_retries):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    if method.upper() == "GET":
                        response = await client.get(url, headers=headers, params=params)
                    elif method.upper() == "POST":
                        if files:
                            # 文件上传需要multipart/form-data
                            headers.pop("Content-Type", None)
                            response = await client.post(url, headers=headers, data=data, files=files)
                        else:
                            response = await client.post(url, headers=headers, json=data)
                    elif method.upper() == "PUT":
                        response = await client.put(url, headers=headers, json=data)
                    elif method.upper() == "DELETE":
                        response = await client.delete(url, headers=headers)
                    else:
                        raise ValueError(f"不支持的HTTP方法: {method}")

                    response.raise_for_status()
                    return response.json()

            except (httpx.HTTPError, httpx.TimeoutException) as e:
                logger.warning(f"Strapi请求失败 (尝试 {attempt + 1}/{self.max_retries}): {str(e)}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay * (attempt + 1))
                else:
                    raise ExternalServiceError(f"Strapi服务请求失败: {str(e)}")

    # 项目相关操作
    async def create_project(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """创建项目"""
        try:
            endpoint = self.content_types["project"]
            response = await self._make_request("POST", endpoint, data={"data": project_data})
            logger.info(f"✅ Strapi项目创建成功: {project_data.get('title', 'Unknown')}")
            return response
        except Exception as e:
            logger.error(f"❌ Strapi项目创建失败: {str(e)}")
            raise

    async def get_project(self, project_id: str) -> Dict[str, Any]:
        """获取项目详情"""
        try:
            endpoint = f"{self.content_types['project']}/{project_id}"
            response = await self._make_request("GET", endpoint)
            return response
        except Exception as e:
            logger.error(f"❌ Strapi项目获取失败: {str(e)}")
            raise

    async def update_project(self, project_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """更新项目"""
        try:
            endpoint = f"{self.content_types['project']}/{project_id}"
            response = await self._make_request("PUT", endpoint, data={"data": update_data})
            logger.info(f"✅ Strapi项目更新成功: {project_id}")
            return response
        except Exception as e:
            logger.error(f"❌ Strapi项目更新失败: {str(e)}")
            raise

    async def delete_project(self, project_id: str) -> Dict[str, Any]:
        """删除项目"""
        try:
            endpoint = f"{self.content_types['project']}/{project_id}"
            response = await self._make_request("DELETE", endpoint)
            logger.info(f"✅ Strapi项目删除成功: {project_id}")
            return response
        except Exception as e:
            logger.error(f"❌ Strapi项目删除失败: {str(e)}")
            raise

    async def list_projects(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """获取项目列表"""
        try:
            endpoint = self.content_types["project"]
            params = {}
            if filters:
                # 构建Strapi过滤参数
                for key, value in filters.items():
                    params[f"filters[{key}][$eq]"] = value

            response = await self._make_request("GET", endpoint, params=params)
            return response.get("data", [])
        except Exception as e:
            logger.error(f"❌ Strapi项目列表获取失败: {str(e)}")
            raise

    # 创意想法相关操作
    async def create_creative_idea(self, idea_data: Dict[str, Any]) -> Dict[str, Any]:
        """创建创意想法"""
        try:
            endpoint = self.content_types["creative_idea"]
            response = await self._make_request("POST", endpoint, data={"data": idea_data})
            logger.info(f"✅ Strapi创意想法创建成功: {idea_data.get('title', 'Unknown')}")
            return response
        except Exception as e:
            logger.error(f"❌ Strapi创意想法创建失败: {str(e)}")
            raise

    async def get_creative_ideas_by_project(self, project_id: str) -> List[Dict[str, Any]]:
        """获取项目的创意想法"""
        try:
            endpoint = self.content_types["creative_idea"]
            params = {
                "filters[project][id][$eq]": project_id,
                "populate": "project"
            }
            response = await self._make_request("GET", endpoint, params=params)
            return response.get("data", [])
        except Exception as e:
            logger.error(f"❌ Strapi项目创意想法获取失败: {str(e)}")
            raise

    # 脚本相关操作
    async def create_script(self, script_data: Dict[str, Any]) -> Dict[str, Any]:
        """创建脚本"""
        try:
            endpoint = self.content_types["script"]
            response = await self._make_request("POST", endpoint, data={"data": script_data})
            logger.info(f"✅ Strapi脚本创建成功: {script_data.get('title', 'Unknown')}")
            return response
        except Exception as e:
            logger.error(f"❌ Strapi脚本创建失败: {str(e)}")
            raise

    async def update_script(self, script_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """更新脚本"""
        try:
            endpoint = f"{self.content_types['script']}/{script_id}"
            response = await self._make_request("PUT", endpoint, data={"data": update_data})
            logger.info(f"✅ Strapi脚本更新成功: {script_id}")
            return response
        except Exception as e:
            logger.error(f"❌ Strapi脚本更新失败: {str(e)}")
            raise

    # 分镜相关操作
    async def create_storyboard(self, storyboard_data: Dict[str, Any]) -> Dict[str, Any]:
        """创建分镜"""
        try:
            endpoint = self.content_types["storyboard"]
            response = await self._make_request("POST", endpoint, data={"data": storyboard_data})
            logger.info(f"✅ Strapi分镜创建成功: {storyboard_data.get('title', 'Unknown')}")
            return response
        except Exception as e:
            logger.error(f"❌ Strapi分镜创建失败: {str(e)}")
            raise

    # 媒体资源相关操作
    async def upload_media_asset(self, file_path: str, asset_data: Dict[str, Any]) -> Dict[str, Any]:
        """上传媒体资源"""
        try:
            endpoint = self.content_types["media_asset"]

            # 读取文件
            file_path_obj = Path(file_path)
            if not file_path_obj.exists():
                raise FileNotFoundError(f"文件不存在: {file_path}")

            with open(file_path, 'rb') as f:
                files = {
                    "files.file": (file_path_obj.name, f, asset_data.get('mimeType', 'application/octet-stream'))
                }

                # 准备数据
                data = {"data": asset_data}

                response = await self._make_request("POST", endpoint, data=data, files=files)
                logger.info(f"✅ Strapi媒体资源上传成功: {file_path_obj.name}")
                return response

        except Exception as e:
            logger.error(f"❌ Strapi媒体资源上传失败: {str(e)}")
            raise

    async def get_media_assets_by_project(self, project_id: str) -> List[Dict[str, Any]]:
        """获取项目的媒体资源"""
        try:
            endpoint = self.content_types["media_asset"]
            params = {
                "filters[project][id][$eq]": project_id,
                "populate": "project,file,thumbnail"
            }
            response = await self._make_request("GET", endpoint, params=params)
            return response.get("data", [])
        except Exception as e:
            logger.error(f"❌ Strapi项目媒体资源获取失败: {str(e)}")
            raise

    # 最终视频相关操作
    async def create_final_video(self, video_data: Dict[str, Any]) -> Dict[str, Any]:
        """创建最终视频"""
        try:
            endpoint = self.content_types["final_video"]
            response = await self._make_request("POST", endpoint, data={"data": video_data})
            logger.info(f"✅ Strapi最终视频创建成功: {video_data.get('title', 'Unknown')}")
            return response
        except Exception as e:
            logger.error(f"❌ Strapi最终视频创建失败: {str(e)}")
            raise

    async def update_final_video(self, video_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """更新最终视频"""
        try:
            endpoint = f"{self.content_types['final_video']}/{video_id}"
            response = await self._make_request("PUT", endpoint, data={"data": update_data})
            logger.info(f"✅ Strapi最终视频更新成功: {video_id}")
            return response
        except Exception as e:
            logger.error(f"❌ Strapi最终视频更新失败: {str(e)}")
            raise

    # Webhook处理
    async def register_webhook(self, webhook_url: str, events: List[str]) -> Dict[str, Any]:
        """注册webhook"""
        try:
            webhook_data = {
                "name": f"AI Video System Webhook {uuid4()}",
                "url": webhook_url,
                "events": events,
                "headers": {
                    "X-Webhook-Secret": settings.STRAPI_WEBHOOK_SECRET or "default-secret"
                }
            }
            response = await self._make_request("POST", "webhooks", data={"data": webhook_data})
            logger.info(f"✅ Strapi webhook注册成功: {webhook_url}")
            return response
        except Exception as e:
            logger.error(f"❌ Strapi webhook注册失败: {str(e)}")
            raise

    async def handle_webhook(self, webhook_data: Dict[str, Any]) -> bool:
        """处理来自Strapi的webhook"""
        try:
            event = webhook_data.get("event")
            model = webhook_data.get("model")
            entry = webhook_data.get("entry", {})

            logger.info(f"📨 收到Strapi webhook: {event} for {model}")

            # 根据事件类型处理
            if event.startswith("entry.create"):
                await self._handle_content_created(model, entry)
            elif event.startswith("entry.update"):
                await self._handle_content_updated(model, entry)
            elif event.startswith("entry.delete"):
                await self._handle_content_deleted(model, entry)
            elif event.startswith("entry.publish"):
                await self._handle_content_published(model, entry)
            elif event.startswith("entry.unpublish"):
                await self._handle_content_unpublished(model, entry)

            return True

        except Exception as e:
            logger.error(f"❌ Strapi webhook处理失败: {str(e)}")
            return False

    async def _handle_content_created(self, model: str, entry: Dict[str, Any]):
        """处理内容创建事件"""
        logger.info(f"📝 Strapi内容创建: {model} - {entry.get('id')}")
        # 这里可以添加同步到主系统的逻辑

    async def _handle_content_updated(self, model: str, entry: Dict[str, Any]):
        """处理内容更新事件"""
        logger.info(f"✏️ Strapi内容更新: {model} - {entry.get('id')}")
        # 这里可以添加同步到主系统的逻辑

    async def _handle_content_deleted(self, model: str, entry: Dict[str, Any]):
        """处理内容删除事件"""
        logger.info(f"🗑️ Strapi内容删除: {model} - {entry.get('id')}")
        # 这里可以添加同步到主系统的逻辑

    async def _handle_content_published(self, model: str, entry: Dict[str, Any]):
        """处理内容发布事件"""
        logger.info(f"📢 Strapi内容发布: {model} - {entry.get('id')}")
        # 这里可以添加同步到主系统的逻辑

    async def _handle_content_unpublished(self, model: str, entry: Dict[str, Any]):
        """处理内容取消发布事件"""
        logger.info(f"📪 Strapi内容取消发布: {model} - {entry.get('id')}")
        # 这里可以添加同步到主系统的逻辑

    # 同步功能
    async def sync_project_to_strapi(self, project_data: Dict[str, Any]) -> str:
        """同步项目到Strapi"""
        try:
            # 转换数据格式
            strapi_data = {
                "title": project_data.get("title"),
                "slug": project_data.get("slug"),
                "description": project_data.get("description"),
                "status": project_data.get("status", "draft"),
                "projectType": project_data.get("project_type", "promotional"),
                "priority": project_data.get("priority", "medium"),
                "deadline": project_data.get("deadline"),
                "businessInput": project_data.get("business_input", {}),
                "technicalSpecs": project_data.get("technical_specs", {}),
                "progress": project_data.get("progress", {}),
                "projectMetadata": project_data.get("project_metadata", {}),
                "creatorId": project_data.get("creator_id"),
                "organizationId": project_data.get("organization_id"),
                "workflowId": project_data.get("workflow_id"),
                "locale": "zh-CN"
            }

            response = await self.create_project(strapi_data)
            strapi_id = response["data"]["id"]

            logger.info(f"✅ 项目同步到Strapi成功: {project_data.get('title')} -> {strapi_id}")
            return strapi_id

        except Exception as e:
            logger.error(f"❌ 项目同步到Strapi失败: {str(e)}")
            raise

    async def sync_content_from_strapi(self, content_type: str, strapi_id: str) -> Dict[str, Any]:
        """从Strapi同步内容"""
        try:
            endpoint = f"{self.content_types.get(content_type, content_type)}/{strapi_id}"
            response = await self._make_request("GET", endpoint)

            logger.info(f"✅ 从Strapi同步内容成功: {content_type} - {strapi_id}")
            return response.get("data", {})

        except Exception as e:
            logger.error(f"❌ 从Strapi同步内容失败: {str(e)}")
            raise

    # 健康检查
    async def health_check(self) -> Dict[str, Any]:
        """检查Strapi服务健康状态"""
        try:
            # 尝试获取基础信息
            response = await self._make_request("GET", "")

            return {
                "status": "healthy",
                "service": "strapi",
                "url": self.base_url,
                "response": response,
                "checked_at": datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"❌ Strapi健康检查失败: {str(e)}")
            return {
                "status": "unhealthy",
                "service": "strapi",
                "url": self.base_url,
                "error": str(e),
                "checked_at": datetime.utcnow().isoformat()
            }


# 创建全局Strapi服务实例
strapi_service = StrapiService()


async def get_strapi_service() -> StrapiService:
    """获取Strapi服务实例"""
    return strapi_service


logger.info("✅ Strapi服务模块加载完成 - 支持内容管理和同步")