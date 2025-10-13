"""
即梦大模型 API 集成服务
Jimeng (即梦) Large Model API Integration Service

提供中文图像和视频生成功能
Provides Chinese image and video generation capabilities
"""

import httpx
import json
import asyncio
import base64
from typing import Dict, List, Optional, Any
from datetime import datetime
from tenacity import retry, stop_after_attempt, wait_exponential
import logging

from app.core.config import settings
from app.core.exceptions import AIServiceError

logger = logging.getLogger(__name__)

class JimengService:
    """即梦大模型 API 服务类"""

    def __init__(self):
        self.access_key = settings.VOLC_ACCESS_KEY
        self.secret_key = settings.VOLC_SECRET_KEY
        self.base_url = settings.JIMENG_BASE_URL
        self.timeout = 60.0

        if not self.access_key or not self.secret_key:
            logger.warning("即梦大模型 API credentials not configured")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=2, min=5, max=15)
    )
    async def generate_storyboard_image(
        self,
        scene_description: str,
        style: str,
        resolution: str = "1024x1024",
        color_palette: List[str] = None,
        aspect_ratio: str = "16:9"
    ) -> Dict[str, Any]:
        """
        生成分镜图像
        Generate storyboard image

        Args:
            scene_description: 场景描述 (中文)
            style: 视觉风格 (中文)
            resolution: 图像分辨率
            color_palette: 色彩调色板
            aspect_ratio: 宽高比

        Returns:
            生成的图像信息和URL
        """
        try:
            # 构建优化的提示词
            enhanced_prompt = self._build_storyboard_prompt(
                scene_description, style, color_palette
            )

            # 准备生成参数
            generation_params = {
                "prompt": enhanced_prompt,
                "model": "jimeng-4.0",
                "resolution": resolution,
                "aspect_ratio": aspect_ratio,
                "style": style,
                "quality": "high",
                "num_images": 1
            }

            # 调用即梦图像生成API
            result = await self._call_jimeng_api(
                endpoint="/images/generations",
                data=generation_params
            )

            # 处理响应
            image_data = self._parse_image_response(result)

            logger.info(f"✅ 分镜图像生成成功 - 风格: {style}, 分辨率: {resolution}")

            return {
                "image_url": image_data.get("url"),
                "image_id": image_data.get("id"),
                "prompt": enhanced_prompt,
                "technical_specs": {
                    "resolution": resolution,
                    "aspect_ratio": aspect_ratio,
                    "style": style,
                    "color_palette": color_palette or []
                },
                "generated_at": datetime.now().isoformat(),
                "model_used": "jimeng-4.0"
            }

        except Exception as e:
            logger.error(f"❌ 分镜图像生成失败: {str(e)}")
            raise AIServiceError(f"即梦图像生成失败: {str(e)}")

    @retry(
        stop=stop_after_attempt(2),
        wait=wait_exponential(multiplier=3, min=10, max=30)
    )
    async def generate_video(
        self,
        image_urls: List[str],
        duration: int = 6,
        resolution: str = "1080p",
        frame_rate: int = 24,
        transition_style: str = "smooth",
        music_style: str = "upbeat"
    ) -> Dict[str, Any]:
        """
        生成短视频
        Generate short video

        Args:
            image_urls: 输入图像URL列表
            duration: 视频时长 (秒)
            resolution: 视频分辨率
            frame_rate: 帧率
            transition_style: 转场风格
            music_style: 音乐风格

        Returns:
            生成的视频信息
        """
        try:
            # 验证输入
            if not image_urls:
                raise ValueError("至少需要一张图像来生成视频")

            if duration < 3 or duration > 30:
                raise ValueError("视频时长必须在3-30秒之间")

            # 准备视频生成参数
            video_params = {
                "model": "jimeng-video-3.0",
                "image_urls": image_urls,
                "duration": duration,
                "resolution": resolution,
                "frame_rate": frame_rate,
                "transition_style": transition_style,
                "music_style": music_style,
                "quality": "high"
            }

            # 调用即梦视频生成API
            result = await self._call_jimeng_api(
                endpoint="/videos/generations",
                data=video_params,
                timeout=120.0  # 视频生成需要更长时间
            )

            # 处理响应
            video_data = self._parse_video_response(result)

            logger.info(f"✅ 视频生成成功 - 时长: {duration}秒, 分辨率: {resolution}")

            return {
                "video_url": video_data.get("url"),
                "video_id": video_data.get("id"),
                "thumbnail_url": video_data.get("thumbnail_url"),
                "duration": duration,
                "technical_specs": {
                    "resolution": resolution,
                    "frame_rate": frame_rate,
                    "transition_style": transition_style,
                    "music_style": music_style,
                    "input_images": len(image_urls)
                },
                "generated_at": datetime.now().isoformat(),
                "model_used": "jimeng-video-3.0"
            }

        except Exception as e:
            logger.error(f"❌ 视频生成失败: {str(e)}")
            raise AIServiceError(f"即梦视频生成失败: {str(e)}")

    async def generate_character_consistency_images(
        self,
        character_description: str,
        scenes: List[str],
        style: str = "realistic"
    ) -> Dict[str, Any]:
        """
        生成角色一致性图像
        Generate character consistency images

        Args:
            character_description: 角色描述 (中文)
            scenes: 场景列表
            style: 图像风格

        Returns:
            角色在不同场景中的图像
        """
        try:
            character_images = []

            for i, scene in enumerate(scenes):
                # 为每个场景生成保持角色一致性的图像
                scene_prompt = f"{character_description}，在{scene}场景中，保持角色特征一致性"

                image_result = await self.generate_storyboard_image(
                    scene_description=scene_prompt,
                    style=style,
                    resolution="1024x1024"
                )

                character_images.append({
                    "scene_index": i,
                    "scene_description": scene,
                    "image_url": image_result["image_url"],
                    "image_id": image_result["image_id"]
                })

            logger.info(f"✅ 角色一致性图像生成成功 - 场景数: {len(scenes)}")

            return {
                "character_description": character_description,
                "images": character_images,
                "style": style,
                "total_scenes": len(scenes),
                "generated_at": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"❌ 角色一致性图像生成失败: {str(e)}")
            raise AIServiceError(f"即梦角色一致性生成失败: {str(e)}")

    async def upscale_image(
        self,
        image_url: str,
        scale_factor: int = 2,
        enhancement_type: str = "general"
    ) -> Dict[str, Any]:
        """
        图像超分辨率增强
        Upscale and enhance image

        Args:
            image_url: 原始图像URL
            scale_factor: 放大倍数
            enhancement_type: 增强类型

        Returns:
            增强后的图像信息
        """
        try:
            upscale_params = {
                "image_url": image_url,
                "model": "jimeng-upscale-2.0",
                "scale_factor": scale_factor,
                "enhancement_type": enhancement_type,
                "quality": "ultra"
            }

            result = await self._call_jimeng_api(
                endpoint="/images/upscale",
                data=upscale_params
            )

            upscale_data = self._parse_upscale_response(result)

            logger.info(f"✅ 图像增强成功 - 放大倍数: {scale_factor}x")

            return {
                "original_url": image_url,
                "upscaled_url": upscale_data.get("url"),
                "scale_factor": scale_factor,
                "enhancement_type": enhancement_type,
                "enhanced_at": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"❌ 图像增强失败: {str(e)}")
            raise AIServiceError(f"即梦图像增强失败: {str(e)}")

    async def _call_jimeng_api(
        self,
        endpoint: str,
        data: Dict[str, Any],
        timeout: float = None
    ) -> Dict[str, Any]:
        """调用即梦API"""
        if not self.access_key or not self.secret_key:
            raise AIServiceError("即梦API credentials未配置")

        headers = {
            "Authorization": f"Bearer {self.access_key}",
            "Content-Type": "application/json",
            "X-Secret-Key": self.secret_key
        }

        timeout = timeout or self.timeout

        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(
                f"{self.base_url}{endpoint}",
                headers=headers,
                json=data
            )

            if response.status_code != 200:
                raise AIServiceError(f"即梦API错误: {response.status_code} - {response.text}")

            return response.json()

    def _build_storyboard_prompt(
        self,
        scene_description: str,
        style: str,
        color_palette: List[str] = None
    ) -> str:
        """构建分镜图像提示词"""
        # 风格关键词映射
        style_keywords = {
            "现代简约": "modern minimalist, clean lines, contemporary",
            "温馨家庭": "warm family style, cozy atmosphere, soft lighting",
            "时尚潮流": "fashionable, trendy, stylish, modern",
            "传统文化": "traditional chinese culture, classical elements",
            "科技感": "technological, futuristic, digital",
            "自然清新": "natural, fresh, organic, outdoor",
            "商务专业": "business professional, corporate, formal"
        }

        # 获取风格关键词
        style_enhancement = style_keywords.get(style, style)

        # 构建完整提示词
        prompt_parts = [
            f"场景描述：{scene_description}",
            f"视觉风格：{style_enhancement}",
            "高质量，专业摄影，构图精美，光线适宜"
        ]

        if color_palette:
            colors = "、".join(color_palette)
            prompt_parts.append(f"色彩方案：{colors}")

        # 添加质量提升关键词
        quality_enhancers = [
            "high quality",
            "professional photography",
            "well composed",
            "proper lighting",
            "sharp focus",
            "vivid colors"
        ]

        prompt_parts.extend(quality_enhancers)

        return ", ".join(prompt_parts)

    def _parse_image_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """解析图像生成响应"""
        if "data" in response and len(response["data"]) > 0:
            image_data = response["data"][0]
            return {
                "url": image_data.get("url"),
                "id": image_data.get("id"),
                "revised_prompt": image_data.get("revised_prompt")
            }
        else:
            raise AIServiceError("图像生成响应格式错误")

    def _parse_video_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """解析视频生成响应"""
        if "data" in response:
            video_data = response["data"]
            return {
                "url": video_data.get("url"),
                "id": video_data.get("id"),
                "thumbnail_url": video_data.get("thumbnail_url"),
                "duration": video_data.get("duration")
            }
        else:
            raise AIServiceError("视频生成响应格式错误")

    def _parse_upscale_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """解析图像增强响应"""
        if "data" in response:
            upscale_data = response["data"]
            return {
                "url": upscale_data.get("url"),
                "original_dimensions": upscale_data.get("original_dimensions"),
                "upscaled_dimensions": upscale_data.get("upscaled_dimensions")
            }
        else:
            raise AIServiceError("图像增强响应格式错误")

# 创建全局服务实例
jimeng_service = JimengService()