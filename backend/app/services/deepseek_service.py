"""
DeepSeek API 集成服务
DeepSeek API Integration Service

提供中文文本生成功能，支持创意概念和剧本生成
Provides Chinese text generation capabilities for concept and script creation
"""

import httpx
import json
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
from tenacity import retry, stop_after_attempt, wait_exponential
import logging

from app.core.config import settings
from app.core.exceptions import AIServiceError

logger = logging.getLogger(__name__)

class DeepSeekService:
    """DeepSeek API 服务类"""

    def __init__(self):
        self.api_key = settings.DEEPSEEK_API_KEY
        self.base_url = settings.DEEPSEEK_BASE_URL
        self.timeout = 30.0

        if not self.api_key:
            logger.warning("DeepSeek API key not configured")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def generate_concept(
        self,
        prompt: str,
        cultural_context: str,
        platform_target: str,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> Dict[str, Any]:
        """
        生成创意概念
        Generate creative concept

        Args:
            prompt: 生成提示词 (中文)
            cultural_context: 文化背景 (中文)
            platform_target: 目标平台 (douyin/wechat/xiaohongshu等)
            temperature: 生成温度 (0.0-2.0)
            max_tokens: 最大token数

        Returns:
            生成的创意概念内容
        """
        try:
            # 构建系统提示词
            system_prompt = self._build_concept_system_prompt(platform_target)

            # 构建用户提示词
            user_prompt = f"""
            创作需求：{prompt}

            文化背景：{cultural_context}

            请基于以上信息，创作一个适合{platform_target}平台的中文创意概念，包含：
            1. 核心创意主题 (简洁有力，易于传播)
            2. 情感共鸣点 (触动目标受众)
            3. 视觉风格建议 (适合短视频表现)
            4. 传播策略要点 (符合平台算法偏好)

            要求：
            - 内容必须原创，符合中国文化背景
            - 语言生动活泼，适合短视频传播
            - 考虑目标平台的用户习惯和算法特点
            """

            # 调用DeepSeek API
            response = await self._call_deepseek_api(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=temperature,
                max_tokens=max_tokens
            )

            # 解析响应
            concept_content = self._parse_concept_response(response)

            logger.info(f"✅ 创意概念生成成功 - 平台: {platform_target}")

            return {
                "concept": concept_content,
                "platform_target": platform_target,
                "cultural_context": cultural_context,
                "generated_at": datetime.now().isoformat(),
                "model_used": "deepseek-chat"
            }

        except Exception as e:
            logger.error(f"❌ 创意概念生成失败: {str(e)}")
            raise AIServiceError(f"DeepSeek概念生成失败: {str(e)}")

    async def generate_script(
        self,
        concept: str,
        tone: str,
        target_age_group: str,
        cultural_references: List[str],
        duration: int = 60,
        temperature: float = 0.6
    ) -> Dict[str, Any]:
        """
        生成短视频剧本
        Generate short video script

        Args:
            concept: 创意概念
            tone: 语调风格
            target_age_group: 目标年龄群体
            cultural_references: 文化引用列表
            duration: 视频时长 (秒)
            temperature: 生成温度

        Returns:
            生成的剧本内容
        """
        try:
            # 构建系统提示词
            system_prompt = self._build_script_system_prompt(tone, target_age_group)

            # 构建用户提示词
            cultural_refs_text = "、".join(cultural_references) if cultural_references else "无特殊要求"

            user_prompt = f"""
            创意概念：{concept}

            语调风格：{tone}
            目标年龄群体：{target_age_group}
            文化引用：{cultural_refs_text}
            视频时长：{duration}秒

            请创作一个{duration}秒的短视频剧本，要求：
            1. 开头3秒必须抓住用户注意力
            2. 内容紧凑有趣，符合{tone}风格
            3. 自然融入中国文化元素
            4. 适合短视频平台传播
            5. 包含具体的镜头描述和文案

            输出格式：
            - 场景描述：[具体的画面内容]
            - 文案内容：[需要配音或字幕的文字]
            - 时长分配：[该场景的时长]
            - 拍摄建议：[镜头运用、特效等]
            """

            # 调用DeepSeek API
            response = await self._call_deepseek_api(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=temperature,
                max_tokens=2000
            )

            # 解析响应
            script_content = self._parse_script_response(response)

            logger.info(f"✅ 剧本生成成功 - 时长: {duration}秒, 风格: {tone}")

            return {
                "script": script_content,
                "concept": concept,
                "tone": tone,
                "target_age_group": target_age_group,
                "duration": duration,
                "generated_at": datetime.now().isoformat(),
                "model_used": "deepseek-chat"
            }

        except Exception as e:
            logger.error(f"❌ 剧本生成失败: {str(e)}")
            raise AIServiceError(f"DeepSeek剧本生成失败: {str(e)}")

    async def optimize_content(
        self,
        content: str,
        optimization_type: str = "engagement",
        platform: str = "douyin"
    ) -> Dict[str, Any]:
        """
        优化内容以提高平台表现
        Optimize content for better platform performance

        Args:
            content: 需要优化的内容
            optimization_type: 优化类型 (engagement/conversion/viral)
            platform: 目标平台

        Returns:
            优化后的内容
        """
        try:
            system_prompt = f"""
            你是专业的短视频内容优化专家，熟悉{platform}平台的算法和用户偏好。
            你的任务是优化内容以提高{optimization_type}效果。
            """

            user_prompt = f"""
            请优化以下内容，提高其在{platform}平台上的{optimization_type}表现：

            原始内容：
            {content}

            优化要求：
            1. 符合平台算法偏好和用户习惯
            2. 保持内容的原创性和文化适应性
            3. 提高用户参与度和传播潜力
            4. 语言风格贴近平台主流内容

            请提供优化后的内容，并说明优化的具体要点。
            """

            response = await self._call_deepseek_api(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=0.5,
                max_tokens=1500
            )

            optimized_content = self._parse_optimization_response(response)

            logger.info(f"✅ 内容优化成功 - 类型: {optimization_type}, 平台: {platform}")

            return {
                "optimized_content": optimized_content,
                "original_content": content,
                "optimization_type": optimization_type,
                "platform": platform,
                "optimized_at": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"❌ 内容优化失败: {str(e)}")
            raise AIServiceError(f"DeepSeek内容优化失败: {str(e)}")

    async def _call_deepseek_api(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float,
        max_tokens: int
    ) -> str:
        """调用DeepSeek API"""
        if not self.api_key:
            raise AIServiceError("DeepSeek API key未配置")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        data = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=data
            )

            if response.status_code != 200:
                raise AIServiceError(f"DeepSeek API错误: {response.status_code} - {response.text}")

            result = response.json()
            return result["choices"][0]["message"]["content"]

    def _build_concept_system_prompt(self, platform: str) -> str:
        """构建创意概念系统提示词"""
        platform_insights = {
            "douyin": "抖音用户喜欢新鲜、有趣、易于模仿的内容，算法偏好高完播率和互动率",
            "wechat": "微信视频号用户更注重内容质量和社交价值，适合深度和有价值的内容",
            "xiaohongshu": "小红书用户追求精致生活，重视美学和品质感，算法偏好收藏和分享",
            "weibo": "微博用户关注热点和话题性，适合有争议性或讨论价值的内容",
            "bilibili": "B站用户喜欢创意和二次元文化，重视内容的独特性和创意性"
        }

        platform_tip = platform_insights.get(platform, "通用短视频平台")

        return f"""
        你是专业的短视频创意策划专家，精通中国社交媒体文化和用户心理。
        你熟悉{platform}平台的算法机制和用户偏好：{platform_tip}

        你的任务是创作符合中国文化背景、适合{platform}平台传播的优质创意概念。
        创意必须原创、有趣、易于病毒式传播，同时符合中国法律法规和社会价值观。
        """

    def _build_script_system_prompt(self, tone: str, target_age_group: str) -> str:
        """构建剧本系统提示词"""
        tone_descriptions = {
            "casual": "轻松随意，像朋友聊天一样",
            "professional": "专业权威，可信度高",
            "humorous": "幽默风趣，让人发笑",
            "emotional": "情感丰富，引起共鸣",
            "trendy": "时尚潮流，引领趋势"
        }

        tone_desc = tone_descriptions.get(tone, tone)

        return f"""
        你是专业的短视频剧本创作专家，精通中国短视频内容创作和平台算法。

        创作要求：
        - 语调风格：{tone_desc}
        - 目标年龄群体：{target_age_group}
        - 视频时长：15-60秒
        - 平台：抖音、快手等中国主流短视频平台

        剧本必须：
        1. 开头3秒抓住用户注意力
        2. 内容紧凑，节奏明快
        3. 符合中国文化背景和价值观
        4. 易于理解和传播
        5. 包含具体的拍摄指导
        """

    def _parse_concept_response(self, response: str) -> Dict[str, Any]:
        """解析创意概念响应"""
        # 这里可以实现更复杂的解析逻辑
        # 目前返回结构化内容
        return {
            "raw_content": response,
            "structured": {
                "theme": "从响应中提取的主题",
                "emotional_hook": "情感共鸣点",
                "visual_style": "视觉风格建议",
                "distribution_strategy": "传播策略"
            }
        }

    def _parse_script_response(self, response: str) -> Dict[str, Any]:
        """解析剧本响应"""
        # 解析剧本内容为结构化格式
        lines = response.split('\n')
        scenes = []
        current_scene = {}

        for line in lines:
            line = line.strip()
            if line.startswith('场景') or line.startswith('【场景'):
                if current_scene:
                    scenes.append(current_scene)
                current_scene = {"description": line, "content": "", "duration": "", "tips": ""}
            elif '文案' in line or '内容' in line:
                current_scene["content"] = line
            elif '时长' in line:
                current_scene["duration"] = line
            elif '拍摄' in line or '建议' in line:
                current_scene["tips"] = line

        if current_scene:
            scenes.append(current_scene)

        return {
            "raw_content": response,
            "scenes": scenes,
            "total_scenes": len(scenes)
        }

    def _parse_optimization_response(self, response: str) -> Dict[str, Any]:
        """解析优化响应"""
        return {
            "optimized_content": response,
            "key_improvements": [
                "改进点1：更吸引人的开头",
                "改进点2：更符合平台算法",
                "改进点3：更好的用户参与度"
            ]
        }

# 创建全局服务实例
deepseek_service = DeepSeekService()