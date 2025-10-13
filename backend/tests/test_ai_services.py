"""
AI服务测试
AI Services Tests

测试DeepSeek和即梦大模型集成
Tests DeepSeek and Jimeng model integrations
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.services.deepseek_service import deepseek_service
from app.services.jimeng_service import jimeng_service
from app.services.autogen_orchestrator import autogen_orchestrator, TaskType
from app.core.exceptions import AIServiceError

class TestDeepSeekService:
    """DeepSeek服务测试类"""

    @pytest.mark.asyncio
    async def test_generate_concept_success(self, mock_deepseek_response):
        """测试成功生成创意概念"""
        with patch('httpx.AsyncClient.post') as mock_post:
            mock_post.return_value = AsyncMock(
                status_code=200,
                json=lambda: mock_deepseek_response
            )

            result = await deepseek_service.generate_concept(
                prompt="为科技产品创作创新广告",
                cultural_context="中国年轻人追求科技创新",
                platform_target="douyin",
                temperature=0.7,
                max_tokens=1000
            )

            assert "concept" in result
            assert "platform_target" in result
            assert result["platform_target"] == "douyin"
            assert "generated_at" in result
            assert "model_used" in result

            # 验证API调用
            mock_post.assert_called_once()
            call_args = mock_post.call_args
            assert "chat/completions" in str(call_args[0][0])

    @pytest.mark.asyncio
    async def test_generate_script_success(self, mock_deepseek_response):
        """测试成功生成剧本"""
        with patch('httpx.AsyncClient.post') as mock_post:
            mock_post.return_value = AsyncMock(
                status_code=200,
                json=lambda: mock_deepseek_response
            )

            result = await deepseek_service.generate_script(
                concept="科技让生活更智能",
                tone="casual",
                target_age_group="18-25岁年轻人",
                cultural_references=["科技", "创新"],
                duration=60,
                temperature=0.6
            )

            assert "script" in result
            assert result["concept"] == "科技让生活更智能"
            assert result["tone"] == "casual"
            assert result["duration"] == 60
            assert "generated_at" in result

    @pytest.mark.asyncio
    async def test_optimize_content_success(self, mock_deepseek_response):
        """测试成功优化内容"""
        with patch('httpx.AsyncClient.post') as mock_post:
            mock_post.return_value = AsyncMock(
                status_code=200,
                json=lambda: mock_deepseek_response
            )

            result = await deepseek_service.optimize_content(
                content="原始内容",
                optimization_type="engagement",
                platform="douyin"
            )

            assert "optimized_content" in result
            assert result["original_content"] == "原始内容"
            assert result["optimization_type"] == "engagement"
            assert result["platform"] == "douyin"

    @pytest.mark.asyncio
    async def test_deepseek_api_error(self):
        """测试DeepSeek API错误处理"""
        with patch('httpx.AsyncClient.post') as mock_post:
            mock_post.return_value = AsyncMock(
                status_code=500,
                text="Internal Server Error"
            )

            with pytest.raises(AIServiceError) as exc_info:
                await deepseek_service.generate_concept(
                    prompt="测试内容",
                    cultural_context="测试背景",
                    platform_target="douyin"
                )

            assert "DeepSeek API错误" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_deepseek_missing_api_key(self):
        """测试缺少API密钥的情况"""
        with patch.object(deepseek_service, 'api_key', None):
            with pytest.raises(AIServiceError) as exc_info:
                await deepseek_service.generate_concept(
                    prompt="测试内容",
                    cultural_context="测试背景",
                    platform_target="douyin"
                )

            assert "API key未配置" in str(exc_info.value)

class TestJimengService:
    """即梦服务测试类"""

    @pytest.mark.asyncio
    async def test_generate_storyboard_image_success(self, mock_jimeng_image_response):
        """测试成功生成分镜图像"""
        with patch('httpx.AsyncClient.post') as mock_post:
            mock_post.return_value = AsyncMock(
                status_code=200,
                json=lambda: mock_jimeng_image_response
            )

            result = await jimeng_service.generate_storyboard_image(
                scene_description="温馨家庭场景",
                style="现代简约风格",
                resolution="1024x1024",
                color_palette=["蓝色", "白色"],
                aspect_ratio="16:9"
            )

            assert "image_url" in result
            assert "image_id" in result
            assert "technical_specs" in result
            assert result["technical_specs"]["resolution"] == "1024x1024"
            assert result["model_used"] == "jimeng-4.0"

    @pytest.mark.asyncio
    async def test_generate_video_success(self, mock_jimeng_video_response):
        """测试成功生成视频"""
        with patch('httpx.AsyncClient.post') as mock_post:
            mock_post.return_value = AsyncMock(
                status_code=200,
                json=lambda: mock_jimeng_video_response
            )

            result = await jimeng_service.generate_video(
                image_urls=["https://example.com/image1.jpg", "https://example.com/image2.jpg"],
                duration=6,
                resolution="1080p",
                frame_rate=24,
                transition_style="smooth",
                music_style="upbeat"
            )

            assert "video_url" in result
            assert "video_id" in result
            assert "thumbnail_url" in result
            assert result["duration"] == 6
            assert result["technical_specs"]["resolution"] == "1080p"

    @pytest.mark.asyncio
    async def test_generate_character_consistency_images(self, mock_jimeng_image_response):
        """测试生成角色一致性图像"""
        with patch('httpx.AsyncClient.post') as mock_post:
            mock_post.return_value = AsyncMock(
                status_code=200,
                json=lambda: mock_jimeng_image_response
            )

            result = await jimeng_service.generate_character_consistency_images(
                character_description="可爱的卡通角色",
                scenes=["家庭生活场景", "工作场景", "休闲场景"],
                style="cartoon"
            )

            assert "character_description" in result
            assert "images" in result
            assert len(result["images"]) == 3
            assert result["total_scenes"] == 3

    @pytest.mark.asyncio
    async def test_upscale_image_success(self, mock_jimeng_image_response):
        """测试图像超分辨率增强"""
        with patch('httpx.AsyncClient.post') as mock_post:
            mock_post.return_value = AsyncMock(
                status_code=200,
                json=lambda: mock_jimeng_image_response
            )

            result = await jimeng_service.upscale_image(
                image_url="https://example.com/original-image.jpg",
                scale_factor=2,
                enhancement_type="general"
            )

            assert "original_url" in result
            assert "upscaled_url" in result
            assert result["scale_factor"] == 2
            assert result["enhancement_type"] == "general"

    @pytest.mark.asyncio
    async def test_jimeng_api_error(self):
        """测试即梦API错误处理"""
        with patch('httpx.AsyncClient.post') as mock_post:
            mock_post.return_value = AsyncMock(
                status_code=500,
                text="服务内部错误"
            )

            with pytest.raises(AIServiceError) as exc_info:
                await jimeng_service.generate_storyboard_image(
                    scene_description="测试场景",
                    style="测试风格"
                )

            assert "即梦API错误" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_jimeng_invalid_input(self):
        """测试即梦服务输入验证"""
        # 测试无效的视频时长
        with pytest.raises(ValueError) as exc_info:
            await jimeng_service.generate_video(
                image_urls=["https://example.com/image.jpg"],
                duration=2,  # 小于最小值3
                resolution="1080p"
            )

        assert "必须在3-30秒之间" in str(exc_info.value)

        # 测试空的图像URL列表
        with pytest.raises(ValueError) as exc_info:
            await jimeng_service.generate_video(
                image_urls=[],
                duration=6,
                resolution="1080p"
            )

        assert "至少需要一张图像" in str(exc_info.value)

class TestAutoGenOrchestrator:
    """AutoGen编排器测试类"""

    @pytest.fixture
    def orchestrator(self):
        """创建编排器实例"""
        return autogen_orchestrator

    @pytest.mark.asyncio
    async def test_create_concept_generation_task(self, orchestrator, sample_concept_request):
        """测试创建创意概念生成任务"""
        with patch.object(orchestrator, '_execute_concept_generation') as mock_execute:
            mock_execute.return_value = {
                "concept": "测试创意",
                "platform_target": "douyin",
                "cultural_context": "测试背景"
            }

            task_id = await orchestrator.create_task(
                task_type=TaskType.CONCEPT_GENERATION,
                project_id="test-project",
                parameters=sample_concept_request
            )

            assert task_id is not None
            assert len(task_id) > 0

            # 验证任务状态
            status = orchestrator.get_task_status(task_id)
            assert status is not None
            assert status["task_type"] == "concept_generation"

    @pytest.mark.asyncio
    async def test_create_script_writing_task(self, orchestrator, sample_script_request):
        """测试创建剧本创作任务"""
        with patch.object(orchestrator, '_execute_script_writing') as mock_execute:
            mock_execute.return_value = {
                "script": "测试剧本内容",
                "concept": "测试概念",
                "tone": "casual"
            }

            task_id = await orchestrator.create_task(
                task_type=TaskType.SCRIPT_WRITING,
                project_id="test-project",
                parameters=sample_script_request
            )

            assert task_id is not None

            # 等待任务完成
            await asyncio.sleep(0.1)

            status = orchestrator.get_task_status(task_id)
            assert status["status"] == "completed"

    @pytest.mark.asyncio
    async def test_create_storyboard_creation_task(self, orchestrator, sample_storyboard_request):
        """测试创建分镜创作任务"""
        with patch.object(orchestrator, '_execute_storyboard_creation') as mock_execute:
            mock_execute.return_value = {
                "storyboard_images": [],
                "total_scenes": 3,
                "style": "现代简约"
            }

            task_id = await orchestrator.create_task(
                task_type=TaskType.STORYBOARD_CREATION,
                project_id="test-project",
                parameters=sample_storyboard_request
            )

            assert task_id is not None

    @pytest.mark.asyncio
    async def test_create_video_generation_task(self, orchestrator, sample_video_request):
        """测试创建视频生成任务"""
        with patch.object(orchestrator, '_execute_video_generation') as mock_execute:
            mock_execute.return_value = {
                "video_url": "https://example.com/video.mp4",
                "video_id": "video-123",
                "duration": 6
            }

            task_id = await orchestrator.create_task(
                task_type=TaskType.VIDEO_GENERATION,
                project_id="test-project",
                parameters=sample_video_request
            )

            assert task_id is not None

    @pytest.mark.asyncio
    async def test_task_status_tracking(self, orchestrator):
        """测试任务状态跟踪"""
        with patch.object(orchestrator, '_execute_concept_generation') as mock_execute:
            mock_execute.return_value = {"test": "result"}

            task_id = await orchestrator.create_task(
                task_type=TaskType.CONCEPT_GENERATION,
                project_id="test-project",
                parameters={"test": "data"}
            )

            # 检查初始状态
            status = orchestrator.get_task_status(task_id)
            assert status["status"] in ["pending", "in_progress"]

            # 等待任务完成
            await asyncio.sleep(0.2)

            # 检查完成状态
            status = orchestrator.get_task_status(task_id)
            assert status["status"] == "completed"
            assert status["result"] is not None

    @pytest.mark.asyncio
    async def test_cancel_task(self, orchestrator):
        """测试取消任务"""
        # 创建一个长时间运行的任务
        with patch.object(orchestrator, '_execute_concept_generation') as mock_execute:
            async def slow_execution(task):
                await asyncio.sleep(1)  # 模拟长时间运行
                return {"result": "completed"}

            mock_execute.side_effect = slow_execution

            task_id = await orchestrator.create_task(
                task_type=TaskType.CONCEPT_GENERATION,
                project_id="test-project",
                parameters={"test": "data"}
            )

            # 等待任务开始
            await asyncio.sleep(0.1)

            # 取消任务
            success = await orchestrator.cancel_task(task_id)
            assert success is True

            # 验证任务状态
            status = orchestrator.get_task_status(task_id)
            assert status["status"] == "cancelled"

    @pytest.mark.asyncio
    async def test_get_active_tasks(self, orchestrator):
        """测试获取活跃任务列表"""
        with patch.object(orchestrator, '_execute_concept_generation') as mock_execute:
            mock_execute.return_value = {"test": "result"}

            # 创建多个任务
            task_ids = []
            for i in range(3):
                task_id = await orchestrator.create_task(
                    task_type=TaskType.CONCEPT_GENERATION,
                    project_id=f"test-project-{i}",
                    parameters={"test": f"data-{i}"}
                )
                task_ids.append(task_id)

            # 获取活跃任务
            active_tasks = orchestrator.get_active_tasks()

            assert len(active_tasks) >= 3
            assert all(task["task_id"] in task_ids for task in active_tasks)

    @pytest.mark.asyncio
    async def test_task_error_handling(self, orchestrator):
        """测试任务错误处理"""
        with patch.object(orchestrator, '_execute_concept_generation') as mock_execute:
            mock_execute.side_effect = Exception("测试错误")

            task_id = await orchestrator.create_task(
                task_type=TaskType.CONCEPT_GENERATION,
                project_id="test-project",
                parameters={"test": "data"}
            )

            # 等待任务执行
            await asyncio.sleep(0.2)

            # 检查错误状态
            status = orchestrator.get_task_status(task_id)
            assert status["status"] == "failed"
            assert status["error"] is not None
            assert "测试错误" in status["error"]

    @pytest.mark.asyncio
    async def test_invalid_task_type(self, orchestrator):
        """测试无效的任务类型"""
        with pytest.raises(ValueError) as exc_info:
            await orchestrator.create_task(
                task_type="invalid_type",  # 无效的任务类型
                project_id="test-project",
                parameters={"test": "data"}
            )

        assert "不支持的任务类型" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_task_callback_function(self, orchestrator):
        """测试任务回调函数"""
        callback_called = False
        callback_data = None

        async def test_callback(task):
            nonlocal callback_called, callback_data
            callback_called = True
            callback_data = task

        with patch.object(orchestrator, '_execute_concept_generation') as mock_execute:
            mock_execute.return_value = {"test": "result"}

            task_id = await orchestrator.create_task(
                task_type=TaskType.CONCEPT_GENERATION,
                project_id="test-project",
                parameters={"test": "data"},
                callback=test_callback
            )

            # 等待任务完成
            await asyncio.sleep(0.2)

            # 验证回调被调用
            assert callback_called is True
            assert callback_data is not None
            assert callback_data.task_id == task_id
            assert callback_data.status.value == "completed"  # 使用枚举值的字符串表示

class TestAIIntegration:
    """AI集成测试类"""

    @pytest.mark.asyncio
    async def test_end_to_end_content_creation_workflow(self, orchestrator):
        """测试端到端内容创作工作流"""
        project_id = "test-e2e-project"

        # 1. 创建创意概念生成任务
        with patch.object(orchestrator, '_execute_concept_generation') as mock_concept:
            mock_concept.return_value = {"concept": "智能家居概念", "theme": "科技改变生活"}

            concept_task_id = await orchestrator.create_task(
                task_type=TaskType.CONCEPT_GENERATION,
                project_id=project_id,
                parameters={
                    "prompt": "智能家居产品推广",
                    "cultural_context": "中国家庭对智能生活的向往",
                    "platform_target": "douyin"
                }
            )

        # 2. 等待概念生成完成
        await asyncio.sleep(0.2)
        concept_status = orchestrator.get_task_status(concept_task_id)
        assert concept_status["status"] == "completed"

        # 3. 创建剧本生成任务
        with patch.object(orchestrator, '_execute_script_writing') as mock_script:
            mock_script.return_value = {"script": "剧本内容", "scenes": 5}

            script_task_id = await orchestrator.create_task(
                task_type=TaskType.SCRIPT_WRITING,
                project_id=project_id,
                parameters={
                    "concept": concept_status["result"]["concept"],
                    "tone": "casual",
                    "target_age_group": "25-35岁家庭主妇",
                    "duration": 60
                }
            )

        # 4. 等待剧本生成完成
        await asyncio.sleep(0.2)
        script_status = orchestrator.get_task_status(script_task_id)
        assert script_status["status"] == "completed"

        print(f"✅ 端到端工作流测试完成 - 项目: {project_id}")
        print(f"   概念任务: {concept_task_id}")
        print(f"   剧本任务: {script_task_id}")

    @pytest.mark.asyncio
    async def test_chinese_content_handling(self, orchestrator):
        """测试中文内容处理"""
        with patch.object(orchestrator, '_execute_concept_generation') as mock_concept:
            mock_concept.return_value = {
                "concept": "春季母婴护肤新理念",
                "emotional_hook": "母爱如春，温柔呵护",
                "visual_style": "温馨家庭风格，柔和色调",
                "distribution_strategy": "利用春季育儿话题热度"
            }

            task_id = await orchestrator.create_task(
                task_type=TaskType.CONCEPT_GENERATION,
                project_id="test-chinese-project",
                parameters={
                    "prompt": "为母婴护肤品牌创作春季推广创意",
                    "cultural_context": "中国妈妈注重宝宝肌肤健康，春季护肤需求增加",
                    "platform_target": "xiaohongshu"
                }
            )

            await asyncio.sleep(0.2)
            status = orchestrator.get_task_status(task_id)

            assert status["status"] == "completed"
            result = status["result"]

            # 验证中文内容正确处理
            assert "春季" in result["concept"]
            assert "母婴" in result["concept"]
            assert "母爱" in result["emotional_hook"]
            assert "家庭" in result["visual_style"]

            print("✅ 中文内容处理测试完成")

    @pytest.mark.asyncio
    async def test_platform_specific_optimization(self, orchestrator):
        """测试平台特定优化"""
        platforms = ["douyin", "wechat", "xiaohongshu", "weibo", "bilibili"]

        for platform in platforms:
            with patch.object(orchestrator, '_execute_concept_generation') as mock_concept:
                mock_concept.return_value = {
                    "concept": f"适合{platform}的创意",
                    "platform_specific_notes": f"针对{platform}平台的特殊优化"
                }

                task_id = await orchestrator.create_task(
                    task_type=TaskType.CONCEPT_GENERATION,
                    project_id=f"test-{platform}-project",
                    parameters={
                        "prompt": f"为{platform}平台创作内容",
                        "cultural_context": "测试文化背景",
                        "platform_target": platform
                    }
                )

                await asyncio.sleep(0.1)
                status = orchestrator.get_task_status(task_id)

                assert status["status"] == "completed"
                result = status["result"]
                assert platform in result["concept"]

        print("✅ 平台特定优化测试完成 - 覆盖平台:", ", ".join(platforms))

if __name__ == "__main__":
    pytest.main([__file__, "-v"])