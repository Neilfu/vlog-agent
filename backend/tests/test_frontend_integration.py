"""
前端集成测试
Frontend Integration Tests

测试前端与后端的集成
Tests frontend and backend integration
"""

import pytest
import requests
import json
from typing import Dict, Any

class TestFrontendAPIIntegration:
    """前端API集成测试类"""

    @pytest.fixture
    def base_url(self):
        """基础URL"""
        return "http://localhost:8000/api/v1"

    @pytest.fixture
    def frontend_headers(self):
        """前端请求头"""
        return {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "ChineseAIVideoFrontend/1.0.0",
            "X-Requested-With": "XMLHttpRequest"
        }

    def test_frontend_project_creation(self, base_url, frontend_headers):
        """测试前端项目创建"""
        project_data = {
            "name": "前端集成测试项目",
            "description": "测试前端与后端的集成",
            "project_type": "advertisement",
            "target_platform": "douyin",
            "target_audience": "年轻用户群体",
            "cultural_context": "测试文化背景",
            "business_input": {
                "product_name": "测试产品",
                "key_messages": ["消息1", "消息2"],
                "competitors": ["竞品1"]
            },
            "technical_specs": {
                "duration": 60,
                "resolution": "1080p",
                "aspect_ratio": "16:9"
            }
        }

        response = requests.post(
            f"{base_url}/projects/",
            headers=frontend_headers,
            json=project_data
        )

        assert response.status_code == 201
        data = response.json()

        assert data["name"] == project_data["name"]
        assert data["description"] == project_data["description"]
        assert data["target_platform"] == "douyin"

        return data["id"]

    def test_frontend_ai_generation_flow(self, base_url, frontend_headers):
        """测试前端AI生成流程"""
        # 1. 创建项目
        project_response = requests.post(
            f"{base_url}/projects/",
            headers=frontend_headers,
            json={
                "name": "AI生成测试项目",
                "description": "测试AI生成功能",
                "project_type": "advertisement",
                "target_platform": "douyin",
                "target_audience": "年轻用户",
                "cultural_context": "测试文化背景"
            }
        )
        assert project_response.status_code == 201
        project_id = project_response.json()["id"]

        # 2. 生成创意概念
        concept_response = requests.post(
            f"{base_url}/ai/generate/concept",
            headers=frontend_headers,
            json={
                "project_id": project_id,
                "prompt": "为科技产品创作创新广告",
                "cultural_context": "中国年轻人追求科技创新",
                "platform_target": "douyin",
                "temperature": 0.7,
                "max_tokens": 1000
            }
        )
        assert concept_response.status_code == 200
        concept_data = concept_response.json()
        assert "task_id" in concept_data
        task_id = concept_data["task_id"]

        # 3. 轮询任务状态（模拟前端轮询）
        max_retries = 10
        for i in range(max_retries):
            status_response = requests.get(
                f"{base_url}/ai/tasks/{task_id}/status",
                headers=frontend_headers
            )
            assert status_response.status_code == 200
            status_data = status_response.json()

            if status_data["status"] in ["completed", "failed"]:
                break

            import time
            time.sleep(1)  # 等待1秒后重试

        assert status_data["status"] in ["completed", "failed"]

    def test_frontend_chinese_content(self, base_url, frontend_headers):
        """测试前端中文内容处理"""
        chinese_project = {
            "name": "母婴护肤品牌春季推广",
            "description": "为知名母婴品牌创作春季新品推广短视频，目标受众为年轻妈妈群体",
            "project_type": "advertisement",
            "target_platform": "xiaohongshu",
            "target_audience": "25-35岁年轻妈妈",
            "cultural_context": "春季育儿，关注宝宝健康成长，中国妈妈注重天然安全",
            "business_input": {
                "product_name": "婴儿天然护肤霜",
                "key_messages": ["天然成分", "温和无刺激", "妈妈放心选择"],
                "competitors": ["强生", "贝亲", "妙思乐"]
            }
        }

        response = requests.post(
            f"{base_url}/projects/",
            headers=frontend_headers,
            json=chinese_project
        )

        assert response.status_code == 201
        data = response.json()

        # 验证中文内容正确保存
        assert "母婴" in data["name"]
        assert "春季" in data["description"]
        assert "年轻妈妈" in data["target_audience"]
        assert "天然安全" in data["cultural_context"]

    def test_frontend_file_upload_simulation(self, base_url, frontend_headers):
        """测试前端文件上传模拟"""
        # 模拟前端文件上传
        files = {
            'file': ('test-image.jpg', b'fake image data', 'image/jpeg'),
            'name': (None, '测试图片'),
            'type': (None, 'image'),
            'description': (None, '测试上传的图片素材')
        }

        response = requests.post(
            f"{base_url}/assets/upload",
            files=files,
            headers={k: v for k, v in frontend_headers.items() if k != "Content-Type"}
        )

        # 注意：这个测试会返回模拟数据，因为实际上传功能需要完整实现
        assert response.status_code == 200
        data = response.json()
        assert "asset_id" in data
        assert data["filename"] == "test-image.jpg"
        assert data["upload_status"] == "completed"

    def test_frontend_error_handling(self, base_url, frontend_headers):
        """测试前端错误处理"""
        # 测试无效数据
        invalid_data = {
            "name": "",  # 空名称
            "description": "测试描述",
            "project_type": "invalid_type",
            "target_platform": "invalid_platform"
        }

        response = requests.post(
            f"{base_url}/projects/",
            headers=frontend_headers,
            json=invalid_data
        )

        assert response.status_code == 422
        error_data = response.json()
        assert "detail" in error_data

    def test_frontend_cors_support(self, base_url):
        """测试前端CORS支持"""
        # 模拟前端跨域请求
        headers = {
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Content-Type"
        }

        response = requests.options(
            f"{base_url}/projects/",
            headers=headers
        )

        assert response.status_code == 200
        assert "Access-Control-Allow-Origin" in response.headers
        assert "Access-Control-Allow-Methods" in response.headers
        assert "Access-Control-Allow-Headers" in response.headers

    def test_frontend_authentication_simulation(self, base_url):
        """测试前端认证模拟（如需要）"""
        # 这里可以添加JWT token或其他认证机制的测试
        # 目前系统可能没有实现完整的认证
        pass

    def test_frontend_real_time_updates(self, base_url, frontend_headers):
        """测试前端实时更新（WebSocket或长轮询）"""
        # 创建AI任务
        project_response = requests.post(
            f"{base_url}/projects/",
            headers=frontend_headers,
            json={
                "name": "实时更新测试项目",
                "description": "测试实时更新功能",
                "project_type": "test",
                "target_platform": "douyin",
                "target_audience": "测试用户",
                "cultural_context": "测试背景"
            }
        )
        project_id = project_response.json()["id"]

        # 创建AI生成任务
        ai_response = requests.post(
            f"{base_url}/ai/generate/concept",
            headers=frontend_headers,
            json={
                "project_id": project_id,
                "prompt": "测试实时更新",
                "cultural_context": "测试文化背景",
                "platform_target": "douyin"
            }
        )
        task_id = ai_response.json()["task_id"]

        # 模拟前端轮询获取更新
        status_changes = []
        for i in range(5):  # 最多轮询5次
            status_response = requests.get(
                f"{base_url}/ai/tasks/{task_id}/status",
                headers=frontend_headers
            )
            status_data = status_response.json()
            status_changes.append(status_data["status"])

            if status_data["status"] in ["completed", "failed"]:
                break

            import time
            time.sleep(0.5)

        # 验证状态变化
        assert len(status_changes) >= 1
        assert status_changes[0] in ["pending", "in_progress", "completed", "failed"]

class TestFrontendComponentIntegration:
    """前端组件集成测试类"""

    def test_dashboard_data_loading(self, base_url, frontend_headers):
        """测试仪表板数据加载"""
        # 先创建一些测试数据
        for i in range(3):
            requests.post(
                f"{base_url}/projects/",
                headers=frontend_headers,
                json={
                    "name": f"仪表板测试项目 {i}",
                    "description": f"测试仪表板数据 {i}",
                    "project_type": "test",
                    "target_platform": "douyin",
                    "target_audience": "测试用户",
                    "cultural_context": "测试背景"
                }
            )

        # 获取项目列表（模拟仪表板数据加载）
        response = requests.get(
            f"{base_url}/projects/",
            headers=frontend_headers
        )

        assert response.status_code == 200
        projects = response.json()
        assert isinstance(projects, list)
        assert len(projects) >= 3

        # 验证数据结构适合前端展示
        for project in projects:
            assert "id" in project
            assert "name" in project
            assert "status" in project
            assert "created_at" in project

    def test_project_management_workflow(self, base_url, frontend_headers):
        """测试项目管理完整工作流"""
        # 1. 创建项目
        create_response = requests.post(
            f"{base_url}/projects/",
            headers=frontend_headers,
            json={
                "name": "项目管理测试",
                "description": "测试项目管理功能",
                "project_type": "advertisement",
                "target_platform": "douyin",
                "target_audience": "测试用户",
                "cultural_context": "测试背景"
            }
        )
        assert create_response.status_code == 201
        project_id = create_response.json()["id"]

        # 2. 获取项目详情
        detail_response = requests.get(
            f"{base_url}/projects/{project_id}",
            headers=frontend_headers
        )
        assert detail_response.status_code == 200

        # 3. 更新项目
        update_response = requests.put(
            f"{base_url}/projects/{project_id}",
            headers=frontend_headers,
            json={
                "name": "项目管理测试（已更新）",
                "status": "in_progress"
            }
        )
        assert update_response.status_code == 200

        # 4. 搜索项目
        search_response = requests.get(
            f"{base_url}/projects/search?q=管理测试",
            headers=frontend_headers
        )
        assert search_response.status_code == 200
        search_results = search_response.json()
        assert len(search_results) >= 1

        # 5. 删除项目
        delete_response = requests.delete(
            f"{base_url}/projects/{project_id}",
            headers=frontend_headers
        )
        assert delete_response.status_code == 200

    def test_settings_management(self, base_url, frontend_headers):
        """测试设置管理功能"""
        # 测试API密钥设置
        api_keys_data = {
            "deepseek": "test-deepseek-key",
            "jimeng_access_key": "test-jimeng-access-key",
            "jimeng_secret_key": "test-jimeng-secret-key",
            "wechat_app_id": "test-wechat-app-id",
            "wechat_app_secret": "test-wechat-app-secret"
        }

        # 注意：实际实现中可能需要专门的设置端点
        # 这里模拟设置保存和验证过程
        print(f"模拟API密钥设置: {api_keys_data}")

        # 测试通知设置
        notification_settings = {
            "email": True,
            "sms": False,
            "push": True,
            "ai_completion": True,
            "system_updates": True
        }

        print(f"模拟通知设置: {notification_settings}")

class TestFrontendPerformance:
    """前端性能测试类"""

    def test_api_response_times(self, base_url, frontend_headers):
        """测试API响应时间"""
        import time

        # 测试项目列表响应时间
        start_time = time.time()
        response = requests.get(f"{base_url}/projects/", headers=frontend_headers)
        list_duration = time.time() - start_time

        assert response.status_code == 200
        assert list_duration < 1.0, f"项目列表响应时间过长: {list_duration:.2f}秒"

        # 测试健康检查响应时间
        start_time = time.time()
        response = requests.get(f"{base_url}/health", headers=frontend_headers)
        health_duration = time.time() - start_time

        assert response.status_code == 200
        assert health_duration < 0.5, f"健康检查响应时间过长: {health_duration:.2f}秒"

        print(f"✅ API响应时间测试通过 - 项目列表: {list_duration:.2f}s, 健康检查: {health_duration:.2f}s")

    def test_concurrent_frontend_requests(self, base_url, frontend_headers):
        """测试前端并发请求"""
        import concurrent.futures
        import time

        def make_request(i):
            start_time = time.time()
            response = requests.get(f"{base_url}/health", headers=frontend_headers)
            duration = time.time() - start_time
            return response.status_code, duration

        # 并发发送多个请求
        start_time = time.time()
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request, i) for i in range(20)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]

        total_duration = time.time() - start_time

        # 验证所有请求都成功
        success_count = sum(1 for status_code, _ in results if status_code == 200)
        assert success_count == 20

        # 验证响应时间在可接受范围内
        avg_duration = sum(duration for _, duration in results) / len(results)
        assert avg_duration < 0.5, f"平均响应时间过长: {avg_duration:.2f}秒"

        print(f"✅ 并发请求测试通过 - 20个请求，平均响应时间: {avg_duration:.2f}s，总耗时: {total_duration:.2f}s")

# 运行测试
if __name__ == "__main__":
    pytest.main([__file__, "-v"])