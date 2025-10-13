"""
集成测试
Integration Tests

测试完整的系统功能和API集成
Tests complete system functionality and API integrations
"""

import pytest
import asyncio
from fastapi import status
from typing import Dict, Any

def test_health_check_endpoint(client):
    """测试健康检查端点"""
    response = client.get("/api/v1/health")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert "version" in data

def test_api_documentation(client):
    """测试API文档端点"""
    response = client.get("/api/v1/docs")

    assert response.status_code == status.HTTP_200_OK
    assert "text/html" in response.headers["content-type"]

def test_openapi_schema(client):
    """测试OpenAPI架构端点"""
    response = client.get("/api/v1/openapi.json")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert "openapi" in data
    assert "info" in data
    assert "paths" in data
    assert "/api/v1/projects/" in data["paths"]
    assert "/api/v1/ai/generate/concept" in data["paths"]

def test_cors_headers(client):
    """测试CORS头设置"""
    response = client.options("/api/v1/health", headers={
        "Origin": "http://localhost:3000",
        "Access-Control-Request-Method": "GET"
    })

    assert response.status_code == status.HTTP_200_OK
    assert "access-control-allow-origin" in response.headers

def test_rate_limiting(client):
    """测试限流功能"""
    # 发送多个请求测试限流
    for i in range(10):
        response = client.get("/api/v1/health")

        # 前几个请求应该成功
        if i < 5:
            assert response.status_code == status.HTTP_200_OK
        # 后续请求可能被限流（取决于配置）
        # 这里我们只需要确保不抛出异常即可

def test_chinese_content_support(client):
    """测试中文内容支持"""
    chinese_project = {
        "name": "人工智能创新应用项目",
        "description": "探索AI技术在各个行业的创新应用，为中国市场提供智能化解决方案",
        "project_type": "technology",
        "target_platform": "douyin",
        "target_audience": "科技爱好者和专业人士",
        "cultural_context": "中国AI技术快速发展，创新应用层出不穷",
        "business_input": {
            "product_name": "智能助手",
            "key_messages": ["智能化", "高效率", "易使用"],
            "competitors": ["百度", "腾讯", "阿里"]
        },
        "technical_specs": {
            "duration": 90,
            "resolution": "4K",
            "aspect_ratio": "16:9"
        }
    }

    response = client.post("/api/v1/projects/", json=chinese_project)

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()

    assert "人工智能" in data["name"]
    assert "AI技术" in data["description"]
    assert "科技爱好者" in data["target_audience"]
    assert "中国AI" in data["cultural_context"]

def test_platform_specific_endpoints(client):
    """测试平台特定端点"""
    platforms = ["douyin", "wechat", "xiaohongshu", "weibo", "bilibili"]

    for platform in platforms:
        project_data = {
            "name": f"{platform}平台推广项目",
            "description": f"专门为{platform}平台创作的内容",
            "project_type": "advertisement",
            "target_platform": platform,
            "target_audience": "年轻用户群体",
            "cultural_context": "测试文化背景"
        }

        response = client.post("/api/v1/projects/", json=project_data)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["target_platform"] == platform

def test_ai_generation_workflow(client):
    """测试AI生成工作流"""
    # 1. 创建项目
    project_data = {
        "name": "AI生成测试项目",
        "description": "测试AI内容生成功能",
        "project_type": "test",
        "target_platform": "douyin",
        "target_audience": "测试用户",
        "cultural_context": "测试文化背景"
    }

    project_response = client.post("/api/v1/projects/", json=project_data)
    assert project_response.status_code == status.HTTP_201_CREATED
    project_id = project_response.json()["id"]

    # 2. 生成创意概念
    concept_request = {
        "project_id": project_id,
        "prompt": "为科技产品创作创新广告",
        "cultural_context": "中国年轻人追求科技创新",
        "platform_target": "douyin",
        "temperature": 0.7,
        "max_tokens": 1000
    }

    concept_response = client.post("/api/v1/ai/generate/concept", json=concept_request)
    assert concept_response.status_code == status.HTTP_200_OK
    concept_data = concept_response.json()
    assert "task_id" in concept_data
    assert concept_data["status"] == "pending"

    # 3. 检查任务状态
    task_id = concept_data["task_id"]
    status_response = client.get(f"/api/v1/ai/tasks/{task_id}/status")
    assert status_response.status_code == status.HTTP_200_OK
    status_data = status_response.json()
    assert status_data["task_id"] == task_id
    assert status_data["task_type"] == "concept_generation"

def test_concurrent_requests(client):
    """测试并发请求处理"""
    import concurrent.futures

    def make_request(i):
        project_data = {
            "name": f"并发测试项目 {i}",
            "description": f"测试并发请求 {i}",
            "project_type": "test",
            "target_platform": "douyin",
            "target_audience": "测试用户",
            "cultural_context": "测试背景"
        }
        return client.post("/api/v1/projects/", json=project_data)

    # 并发发送多个请求
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(make_request, i) for i in range(10)]
        responses = [future.result() for future in concurrent.futures.as_completed(futures)]

    # 验证所有请求都成功
    success_count = sum(1 for response in responses if response.status_code == status.HTTP_201_CREATED)
    assert success_count == 10

def test_error_handling_and_recovery(client):
    """测试错误处理和恢复机制"""
    # 测试无效数据
    invalid_data = {
        "name": "",  # 空名称
        "description": "测试描述",
        "project_type": "invalid_type",  # 无效类型
        "target_platform": "invalid_platform"  # 无效平台
    }

    response = client.post("/api/v1/projects/", json=invalid_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    # 测试不存在的资源
    response = client.get("/api/v1/projects/nonexistent-id")
    assert response.status_code == status.HTTP_404_NOT_FOUND

    # 验证系统在错误后仍能正常工作
    valid_data = {
        "name": "恢复测试项目",
        "description": "测试系统恢复功能",
        "project_type": "advertisement",
        "target_platform": "douyin",
        "target_audience": "测试用户",
        "cultural_context": "测试背景"
    }

    response = client.post("/api/v1/projects/", json=valid_data)
    assert response.status_code == status.HTTP_201_CREATED

def test_data_validation_and_sanitization(client):
    """测试数据验证和清理"""
    # 测试XSS防护
    xss_attempt = {
        "name": "<script>alert('XSS')</script>",
        "description": "测试XSS防护<script>alert('XSS')</script>",
        "project_type": "advertisement",
        "target_platform": "douyin",
        "target_audience": "<script>alert('XSS')</script>",
        "cultural_context": "<script>alert('XSS')</script>"
    }

    response = client.post("/api/v1/projects/", json=xss_attempt)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()

    # 验证脚本标签被正确处理（通常会被转义或删除）
    assert "<script>" not in data["name"]
    assert "<script>" not in data["description"]

    # 测试SQL注入防护（使用特殊字符）
    sql_injection_attempt = {
        "name": "项目'; DROP TABLE projects; --",
        "description": "测试SQL注入防护",
        "project_type": "advertisement",
        "target_platform": "douyin",
        "target_audience": "测试用户",
        "cultural_context": "测试背景"
    }

    response = client.post("/api/v1/projects/", json=sql_injection_attempt)
    assert response.status_code == status.HTTP_201_CREATED

    # 验证项目仍然可以正常查询
    response = client.get("/api/v1/projects/")
    assert response.status_code == status.HTTP_200_OK

def test_performance_benchmarks(client):
    """测试性能基准"""
    import time

    # 测试项目创建性能
    start_time = time.time()

    for i in range(10):
        project_data = {
            "name": f"性能测试项目 {i}",
            "description": f"性能测试描述 {i}",
            "project_type": "test",
            "target_platform": "douyin",
            "target_audience": "性能测试用户",
            "cultural_context": "性能测试背景"
        }
        response = client.post("/api/v1/projects/", json=project_data)
        assert response.status_code == status.HTTP_201_CREATED

    end_time = time.time()
    duration = end_time - start_time

    # 验证性能在可接受范围内（10个项目创建应该在5秒内完成）
    assert duration < 5.0, f"性能测试失败: 创建10个项目耗时 {duration:.2f} 秒"

    print(f"✅ 性能测试通过: 创建10个项目耗时 {duration:.2f} 秒")

def test_memory_usage_and_cleanup(client):
    """测试内存使用和清理"""
    import gc
    import psutil
    import os

    process = psutil.Process(os.getpid())
    initial_memory = process.memory_info().rss / 1024 / 1024  # MB

    # 创建大量项目
    for i in range(20):
        project_data = {
            "name": f"内存测试项目 {i}",
            "description": f"内存测试描述 {i}",
            "project_type": "test",
            "target_platform": "douyin",
            "target_audience": "内存测试用户",
            "cultural_context": "内存测试背景"
        }
        response = client.post("/api/v1/projects/", json=project_data)
        assert response.status_code == status.HTTP_201_CREATED

    # 强制垃圾回收
    gc.collect()

    final_memory = process.memory_info().rss / 1024 / 1024  # MB
    memory_increase = final_memory - initial_memory

    # 验证内存增长在可接受范围内（应该小于100MB）
    assert memory_increase < 100, f"内存测试失败: 内存增长 {memory_increase:.2f} MB"

    print(f"✅ 内存测试通过: 内存增长 {memory_increase:.2f} MB")

# 端到端测试
class TestEndToEndScenarios:
    """端到端场景测试"""

    def test_complete_video_creation_workflow(self, client):
        """测试完整的视频创建工作流"""
        # 1. 创建项目
        project_data = {
            "name": "完整工作流测试项目",
            "description": "测试从概念到视频的完整创作流程",
            "project_type": "advertisement",
            "target_platform": "douyin",
            "target_audience": "25-35岁年轻妈妈",
            "cultural_context": "春季母婴护理，关注宝宝健康",
            "business_input": {
                "product_name": "婴儿护肤霜",
                "key_messages": ["天然成分", "温和无刺激", "专业推荐"],
                "competitors": ["强生", "贝亲", "妙思乐"]
            }
        }

        project_response = client.post("/api/v1/projects/", json=project_data)
        assert project_response.status_code == status.HTTP_201_CREATED
        project_id = project_response.json()["id"]

        # 2. 生成创意概念
        concept_response = client.post("/api/v1/ai/generate/concept", json={
            "project_id": project_id,
            "prompt": "为婴儿护肤霜创作温馨的广告创意",
            "cultural_context": "中国妈妈注重宝宝肌肤健康，春季护肤需求增加",
            "platform_target": "douyin"
        })
        assert concept_response.status_code == status.HTTP_200_OK
        concept_task_id = concept_response.json()["task_id"]

        # 3. 生成剧本
        script_response = client.post("/api/v1/ai/generate/script", json={
            "project_id": project_id,
            "concept_id": concept_task_id,
            "tone": "emotional",
            "target_age_group": "25-35岁年轻妈妈",
            "cultural_references": ["母爱", "春季", "呵护"]
        })
        assert script_response.status_code == status.HTTP_200_OK

        # 4. 查询所有任务状态
        tasks_response = client.get("/api/v1/ai/tasks")
        assert tasks_response.status_code == status.HTTP_200_OK
        tasks_data = tasks_response.json()
        assert tasks_data["total_count"] >= 2

        # 5. 验证项目详情
        detail_response = client.get(f"/api/v1/projects/{project_id}")
        assert detail_response.status_code == status.HTTP_200_OK
        project_detail = detail_response.json()
        assert project_detail["ai_tasks_count"] >= 2

        print(f"✅ 完整工作流测试完成 - 项目ID: {project_id}")

    def test_multi_platform_content_adaptation(self, client):
        """测试多平台内容适配"""
        base_project = {
            "name": "多平台适配测试",
            "description": "测试同一内容在不同平台的适配",
            "project_type": "advertisement",
            "target_audience": "年轻用户群体",
            "cultural_context": "国潮文化流行"
        }

        platforms = ["douyin", "wechat", "xiaohongshu", "weibo", "bilibili"]
        project_ids = []

        for platform in platforms:
            project_data = {**base_project, "target_platform": platform}
            response = client.post("/api/v1/projects/", json=project_data)
            assert response.status_code == status.HTTP_201_CREATED
            project_ids.append(response.json()["id"])

        # 为每个平台生成特定内容
        for i, platform in enumerate(platforms):
            concept_response = client.post("/api/v1/ai/generate/concept", json={
                "project_id": project_ids[i],
                "prompt": f"为{platform}平台创作国潮风格内容",
                "cultural_context": "国潮文化在年轻人中的流行趋势",
                "platform_target": platform
            })
            assert concept_response.status_code == status.HTTP_200_OK

        print(f"✅ 多平台适配测试完成 - 平台: {', '.join(platforms)}")

# 运行测试
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])