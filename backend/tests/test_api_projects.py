"""
项目API测试
Project API Tests

测试项目管理相关API端点
Tests project management related API endpoints
"""

import pytest
from fastapi import status

def test_create_project_success(client, sample_project_data):
    """测试成功创建项目"""
    response = client.post("/api/v1/projects/", json=sample_project_data)

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()

    assert data["name"] == sample_project_data["name"]
    assert data["description"] == sample_project_data["description"]
    assert data["project_type"] == sample_project_data["project_type"]
    assert data["target_platform"] == sample_project_data["target_platform"]
    assert data["status"] == "active"
    assert "id" in data
    assert "created_at" in data

def test_create_project_invalid_data(client):
    """测试创建项目时提供无效数据"""
    invalid_data = {
        "name": "",  # 空名称
        "description": "测试描述",
        "project_type": "invalid_type",  # 无效类型
        "target_platform": "invalid_platform"  # 无效平台
    }

    response = client.post("/api/v1/projects/", json=invalid_data)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

def test_get_projects_list(client, sample_project_data):
    """测试获取项目列表"""
    # 先创建一个项目
    create_response = client.post("/api/v1/projects/", json=sample_project_data)
    assert create_response.status_code == status.HTTP_201_CREATED

    # 获取项目列表
    response = client.get("/api/v1/projects/")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["name"] == sample_project_data["name"]

def test_get_project_detail(client, sample_project_data):
    """测试获取项目详情"""
    # 创建项目
    create_response = client.post("/api/v1/projects/", json=sample_project_data)
    project_id = create_response.json()["id"]

    # 获取项目详情
    response = client.get(f"/api/v1/projects/{project_id}")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert data["id"] == project_id
    assert data["name"] == sample_project_data["name"]
    assert data["description"] == sample_project_data["description"]

def test_get_nonexistent_project(client):
    """测试获取不存在的项目"""
    response = client.get("/api/v1/projects/nonexistent-id")

    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_update_project_success(client, sample_project_data):
    """测试成功更新项目"""
    # 创建项目
    create_response = client.post("/api/v1/projects/", json=sample_project_data)
    project_id = create_response.json()["id"]

    # 更新项目
    update_data = {
        "name": "更新后的项目名称",
        "description": "更新后的项目描述",
        "status": "completed"
    }

    response = client.put(f"/api/v1/projects/{project_id}", json=update_data)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert data["id"] == project_id
    assert data["name"] == update_data["name"]
    assert data["description"] == update_data["description"]
    assert data["status"] == update_data["status"]

def test_delete_project_success(client, sample_project_data):
    """测试成功删除项目"""
    # 创建项目
    create_response = client.post("/api/v1/projects/", json=sample_project_data)
    project_id = create_response.json()["id"]

    # 删除项目
    response = client.delete(f"/api/v1/projects/{project_id}")

    assert response.status_code == status.HTTP_200_OK

    # 验证项目已被删除
    get_response = client.get(f"/api/v1/projects/{project_id}")
    assert get_response.status_code == status.HTTP_404_NOT_FOUND

def test_project_search(client, sample_project_data):
    """测试项目搜索功能"""
    # 创建测试项目
    client.post("/api/v1/projects/", json=sample_project_data)

    # 搜索项目
    response = client.get("/api/v1/projects/search?q=测试")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert isinstance(data, list)
    assert len(data) >= 1
    assert "测试" in data[0]["name"]

def test_project_chinese_content(client):
    """测试项目中文内容处理"""
    chinese_data = {
        "name": "母婴品牌春季推广活动",
        "description": "为知名母婴品牌创作春季新品推广短视频，目标受众为年轻妈妈群体",
        "project_type": "advertisement",
        "target_platform": "douyin",
        "target_audience": "25-35岁年轻妈妈",
        "cultural_context": "春季育儿，关注宝宝健康成长",
        "business_input": {
            "product_name": "婴儿护肤产品",
            "key_messages": ["温和无刺激", "天然成分", "专业推荐"],
            "competitors": ["强生", "贝亲"]
        }
    }

    response = client.post("/api/v1/projects/", json=chinese_data)

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()

    assert data["name"] == chinese_data["name"]
    assert data["description"] == chinese_data["description"]
    assert data["target_audience"] == chinese_data["target_audience"]
    assert data["cultural_context"] == chinese_data["cultural_context"]

def test_project_platform_validation(client, sample_project_data):
    """测试项目平台验证"""
    # 测试有效平台
    for platform in ["douyin", "wechat", "xiaohongshu", "weibo", "bilibili"]:
        test_data = {**sample_project_data, "target_platform": platform}
        response = client.post("/api/v1/projects/", json=test_data)
        assert response.status_code == status.HTTP_201_CREATED

    # 测试无效平台
    invalid_data = {**sample_project_data, "target_platform": "invalid_platform"}
    response = client.post("/api/v1/projects/", json=invalid_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

def test_project_pagination(client, sample_project_data):
    """测试项目分页功能"""
    # 创建多个项目
    for i in range(5):
        test_data = {**sample_project_data, "name": f"测试项目 {i}"}
        client.post("/api/v1/projects/", json=test_data)

    # 测试分页
    response = client.get("/api/v1/projects/?skip=0&limit=3")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert len(data) <= 3  # 限制返回数量

def test_project_filter_by_status(client, sample_project_data):
    """测试按状态筛选项目"""
    # 创建项目
    create_response = client.post("/api/v1/projects/", json=sample_project_data)
    project_id = create_response.json()["id"]

    # 更新项目状态
    update_data = {"status": "completed"}
    client.put(f"/api/v1/projects/{project_id}", json=update_data)

    # 按状态筛选
    response = client.get("/api/v1/projects/?status=completed")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert len(data) >= 1
    assert all(project["status"] == "completed" for project in data)

def test_project_filter_by_platform(client, sample_project_data):
    """测试按平台筛选项目"""
    # 创建项目
    client.post("/api/v1/projects/", json=sample_project_data)

    # 按平台筛选
    response = client.get("/api/v1/projects/?platform=douyin")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert len(data) >= 1
    assert all(project["target_platform"] == "douyin" for project in data)

def test_project_chinese_search(client):
    """测试项目中文搜索"""
    # 创建包含中文的项目
    chinese_data = {
        "name": "人工智能技术应用",
        "description": "探索AI在各个领域的创新应用",
        "project_type": "technology",
        "target_platform": "douyin",
        "target_audience": "科技爱好者",
        "cultural_context": "中国AI技术发展"
    }

    client.post("/api/v1/projects/", json=chinese_data)

    # 中文搜索
    response = client.get("/api/v1/projects/search?q=人工智能")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert len(data) >= 1
    assert any("人工智能" in project["name"] for project in data)

def test_project_sorting(client, sample_project_data):
    """测试项目排序功能"""
    # 创建多个项目
    for i in range(3):
        test_data = {**sample_project_data, "name": f"项目 {i}"}
        client.post("/api/v1/projects/", json=test_data)

    # 按创建时间排序
    response = client.get("/api/v1/projects/?sort_by=created_at&sort_order=desc")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    # 验证排序（如果数据足够的话）
    if len(data) >= 2:
        # 检查是否按创建时间降序排列
        created_times = [project["created_at"] for project in data]
        assert created_times == sorted(created_times, reverse=True)