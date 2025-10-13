"""
AutoGen 多智能体编排系统
AutoGen Multi-Agent Orchestration System

协调多个AI代理进行复杂的视频创作任务
Orchestrates multiple AI agents for complex video creation tasks
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
from uuid import uuid4
from dataclasses import dataclass, asdict
from enum import Enum

from autogen import AssistantAgent, UserProxyAgent, GroupChat, GroupChatManager
from autogen.agentchat.contrib.math_user_proxy_agent import MathUserProxyAgent

from app.core.config import settings
from app.core.exceptions import AIServiceError
from app.services.deepseek_service import deepseek_service
from app.services.jimeng_service import jimeng_service

logger = logging.getLogger(__name__)

class TaskType(Enum):
    """任务类型"""
    CONCEPT_GENERATION = "concept_generation"
    SCRIPT_WRITING = "script_writing"
    STORYBOARD_CREATION = "storyboard_creation"
    VIDEO_GENERATION = "video_generation"
    CONTENT_OPTIMIZATION = "content_optimization"
    QUALITY_REVIEW = "quality_review"

class TaskStatus(Enum):
    """任务状态"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class Task:
    """任务数据结构"""
    task_id: str
    task_type: TaskType
    project_id: str
    parameters: Dict[str, Any]
    status: TaskStatus
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    created_at: datetime = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

class ChineseContentCreatorAgent(AssistantAgent):
    """中文内容创作智能体"""

    def __init__(self):
        super().__init__(
            name="ChineseContentCreator",
            system_message="""你是专业的中文短视频内容创作专家。

            专业技能：
            - 精通中国社交媒体文化和用户心理
            - 熟悉抖音、微信、小红书等主流平台算法
            - 擅长创作符合中国文化背景的内容
            - 了解短视频病毒式传播机制

            创作原则：
            1. 内容必须原创且符合中国法律法规
            2. 充分考虑目标受众的文化背景和偏好
            3. 遵循平台算法偏好，提高传播效果
            4. 语言生动活泼，适合短视频传播

            输出格式：
            - 提供结构化的创意概念
            - 包含具体的执行建议
            - 说明预期的传播效果""",
            llm_config={
                "config_list": [{
                    "model": "deepseek-chat",
                    "api_key": settings.DEEPSEEK_API_KEY,
                    "base_url": settings.DEEPSEEK_BASE_URL
                }]
            }
        )

class VisualDesignerAgent(AssistantAgent):
    """视觉设计智能体"""

    def __init__(self):
        super().__init__(
            name="VisualDesigner",
            system_message="""你是专业的视觉设计和分镜创作专家。

            专业技能：
            - 精通短视频视觉语言和构图技巧
            - 熟悉中国用户的美学偏好
            - 擅长将文字概念转化为视觉方案
            - 了解不同平台的视觉规范

            设计原则：
            1. 确保视觉风格与内容主题一致
            2. 考虑中国用户的色彩偏好和文化象征
            3. 优化移动端观看体验
            4. 保持品牌一致性

            输出格式：
            - 详细的视觉风格描述
            - 具体的色彩搭配方案
            - 构图和镜头运用建议
            - 技术参数要求""",
            llm_config={
                "config_list": [{
                    "model": "deepseek-chat",
                    "api_key": settings.DEEPSEEK_API_KEY,
                    "base_url": settings.DEEPSEEK_BASE_URL
                }]
            }
        )

class VideoProducerAgent(AssistantAgent):
    """视频制作智能体"""

    def __init__(self):
        super().__init__(
            name="VideoProducer",
            system_message="""你是专业的短视频制作和技术实现专家。

            专业技能：
            - 精通视频制作流程和技术标准
            - 熟悉AI视频生成工具和方法
            - 了解中国短视频平台的技术要求
            - 擅长优化视频质量和加载速度

            制作原则：
            1. 确保视频质量符合平台标准
            2. 优化文件大小和加载速度
            3. 适配不同设备和网络环境
            4. 保持内容连贯性和观赏性

            输出格式：
            - 详细的制作流程
            - 技术参数设置
            - 质量控制标准
            - 后期处理建议""",
            llm_config={
                "config_list": [{
                    "model": "deepseek-chat",
                    "api_key": settings.DEEPSEEK_API_KEY,
                    "base_url": settings.DEEPSEEK_BASE_URL
                }]
            }
        )

class QualityReviewerAgent(AssistantAgent):
    """质量审核智能体"""

    def __init__(self):
        super().__init__(
            name="QualityReviewer",
            system_message="""你是专业的内容质量审核和优化专家。

            专业技能：
            - 精通内容质量评估标准
            - 熟悉中国网络内容审核规范
            - 擅长识别潜在的法律和道德风险
            - 了解平台算法偏好和用户行为

            审核标准：
            1. 内容原创性和独特性
            2. 法律合规性和社会适宜性
            3. 平台算法友好度
            4. 用户参与度和传播潜力
            5. 文化适应性和目标受众匹配度

            输出格式：
            - 详细的质量评估报告
            - 具体的改进建议
            - 风险预警和合规建议
            - 优化方向和策略""",
            llm_config={
                "config_list": [{
                    "model": "deepseek-chat",
                    "api_key": settings.DEEPSEEK_API_KEY,
                    "base_url": settings.DEEPSEEK_BASE_URL
                }]
            }
        )

class TaskOrchestratorAgent(UserProxyAgent):
    """任务编排智能体"""

    def __init__(self):
        super().__init__(
            name="TaskOrchestrator",
            human_input_mode="NEVER",
            max_consecutive_auto_reply=10,
            code_execution_config=False
        )

class AutoGenOrchestrator:
    """AutoGen 编排器主类"""

    def __init__(self):
        self.agents = {}
        self.active_tasks: Dict[str, Task] = {}
        self.task_callbacks: Dict[str, Callable] = {}
        self._initialize_agents()

    def _initialize_agents(self):
        """初始化所有智能体"""
        try:
            # 创建专业智能体
            self.agents = {
                "content_creator": ChineseContentCreatorAgent(),
                "visual_designer": VisualDesignerAgent(),
                "video_producer": VideoProducerAgent(),
                "quality_reviewer": QualityReviewerAgent(),
                "orchestrator": TaskOrchestratorAgent()
            }

            logger.info("✅ AutoGen智能体初始化成功")

        except Exception as e:
            logger.error(f"❌ 智能体初始化失败: {str(e)}")
            logger.warning("AutoGen智能体初始化失败，将使用备用模式运行")
            # 不抛出异常，让系统继续运行

    async def create_task(
        self,
        task_type: TaskType,
        project_id: str,
        parameters: Dict[str, Any],
        callback: Optional[Callable] = None
    ) -> str:
        """
        创建新的创作任务

        Args:
            task_type: 任务类型
            project_id: 项目ID
            parameters: 任务参数
            callback: 完成回调函数

        Returns:
            任务ID
        """
        task_id = str(uuid4())

        task = Task(
            task_id=task_id,
            task_type=task_type,
            project_id=project_id,
            parameters=parameters,
            status=TaskStatus.PENDING,
            created_at=datetime.now()
        )

        self.active_tasks[task_id] = task

        if callback:
            self.task_callbacks[task_id] = callback

        logger.info(f"📝 创建任务成功 - ID: {task_id}, 类型: {task_type.value}")

        # 立即开始执行任务
        asyncio.create_task(self._execute_task(task_id))

        return task_id

    async def _execute_task(self, task_id: str):
        """执行具体任务"""
        task = self.active_tasks.get(task_id)
        if not task:
            return

        try:
            task.status = TaskStatus.IN_PROGRESS
            task.started_at = datetime.now()

            logger.info(f"🚀 开始执行任务 - ID: {task_id}")

            # 根据任务类型执行不同的工作流程
            if task.task_type == TaskType.CONCEPT_GENERATION:
                result = await self._execute_concept_generation(task)
            elif task.task_type == TaskType.SCRIPT_WRITING:
                result = await self._execute_script_writing(task)
            elif task.task_type == TaskType.STORYBOARD_CREATION:
                result = await self._execute_storyboard_creation(task)
            elif task.task_type == TaskType.VIDEO_GENERATION:
                result = await self._execute_video_generation(task)
            elif task.task_type == TaskType.CONTENT_OPTIMIZATION:
                result = await self._execute_content_optimization(task)
            else:
                raise ValueError(f"不支持的任务类型: {task.task_type}")

            # 如果有配置好的AutoGen智能体，可以在这里添加额外的处理
            if self.agents:
                logger.info(f"使用AutoGen智能体增强处理 - 任务: {task_id}")
                # 这里可以添加AutoGen智能体的额外逻辑

            # 更新任务状态
            task.status = TaskStatus.COMPLETED
            task.result = result
            task.completed_at = datetime.now()

            logger.info(f"✅ 任务执行成功 - ID: {task_id}")

            # 调用回调函数
            callback = self.task_callbacks.get(task_id)
            if callback:
                await callback(task)

        except Exception as e:
            logger.error(f"❌ 任务执行失败 - ID: {task_id}: {str(e)}")
            task.status = TaskStatus.FAILED
            task.error = str(e)
            task.completed_at = datetime.now()

    async def _execute_concept_generation(self, task: Task) -> Dict[str, Any]:
        """执行创意概念生成任务"""
        params = task.parameters

        # 使用DeepSeek直接生成概念
        concept_result = await deepseek_service.generate_concept(
            prompt=params["prompt"],
            cultural_context=params["cultural_context"],
            platform_target=params["platform_target"],
            temperature=params.get("temperature", 0.7),
            max_tokens=params.get("max_tokens", 1000)
        )

        return concept_result

    async def _execute_script_writing(self, task: Task) -> Dict[str, Any]:
        """执行剧本创作任务"""
        params = task.parameters

        # 使用DeepSeek生成剧本
        script_result = await deepseek_service.generate_script(
            concept=params["concept"],
            tone=params.get("tone", "casual"),
            target_age_group=params["target_age_group"],
            cultural_references=params.get("cultural_references", []),
            duration=params.get("duration", 60),
            temperature=params.get("temperature", 0.6)
        )

        return script_result

    async def _execute_storyboard_creation(self, task: Task) -> Dict[str, Any]:
        """执行分镜创作任务"""
        params = task.parameters

        # 解析剧本场景
        scenes = params.get("scenes", [])
        if not scenes:
            raise ValueError("缺少剧本场景数据")

        # 为每个场景生成图像
        storyboard_images = []
        for i, scene in enumerate(scenes):
            image_result = await jimeng_service.generate_storyboard_image(
                scene_description=scene.get("description", ""),
                style=params.get("style", "现代简约"),
                resolution=params.get("resolution", "1024x1024"),
                color_palette=params.get("color_palette", [])
            )

            storyboard_images.append({
                "scene_index": i,
                "scene_data": scene,
                "image_data": image_result
            })

        return {
            "storyboard_images": storyboard_images,
            "total_scenes": len(scenes),
            "style": params.get("style", "现代简约")
        }

    async def _execute_video_generation(self, task: Task) -> Dict[str, Any]:
        """执行视频生成任务"""
        params = task.parameters

        # 获取分镜图像URL
        image_urls = params.get("image_urls", [])
        if not image_urls:
            raise ValueError("缺少分镜图像数据")

        # 使用即梦生成视频
        video_result = await jimeng_service.generate_video(
            image_urls=image_urls,
            duration=params.get("duration", 6),
            resolution=params.get("resolution", "1080p"),
            frame_rate=params.get("frame_rate", 24),
            transition_style=params.get("transition_style", "smooth"),
            music_style=params.get("music_style", "upbeat")
        )

        return video_result

    async def _execute_content_optimization(self, task: Task) -> Dict[str, Any]:
        """执行内容优化任务"""
        params = task.parameters

        # 使用DeepSeek进行内容优化
        optimization_result = await deepseek_service.optimize_content(
            content=params["content"],
            optimization_type=params.get("optimization_type", "engagement"),
            platform=params.get("platform", "douyin")
        )

        return optimization_result

    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """获取任务状态"""
        task = self.active_tasks.get(task_id)
        if not task:
            return None

        return {
            "task_id": task.task_id,
            "task_type": task.task_type.value,
            "status": task.status.value,
            "project_id": task.project_id,
            "created_at": task.created_at.isoformat() if task.created_at else None,
            "started_at": task.started_at.isoformat() if task.started_at else None,
            "completed_at": task.completed_at.isoformat() if task.completed_at else None,
            "result": task.result,
            "error": task.error
        }

    def get_active_tasks(self) -> List[Dict[str, Any]]:
        """获取所有活跃任务"""
        return [
            self.get_task_status(task_id)
            for task_id in self.active_tasks.keys()
        ]

    async def cancel_task(self, task_id: str) -> bool:
        """取消任务"""
        task = self.active_tasks.get(task_id)
        if not task:
            return False

        if task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]:
            return False

        task.status = TaskStatus.CANCELLED
        task.completed_at = datetime.now()

        logger.info(f"🛑 任务已取消 - ID: {task_id}")
        return True

# 创建全局编排器实例
autogen_orchestrator = AutoGenOrchestrator()