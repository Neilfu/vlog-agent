"""
验证器测试模块
Tests for validation system
"""

import pytest
from datetime import datetime, timedelta
from app.core.validators import (
    validate_project_creation_data,
    BusinessInputValidator,
    TechnicalSpecsValidator,
    ProjectValidator,
    ChineseContentValidator,
    ContentModerationValidator,
    ValidationError
)


class TestBusinessInputValidator:
    """测试业务输入验证器"""

    def test_validate_target_audience_success(self):
        """测试有效的目标受众验证"""
        result = BusinessInputValidator.validate_target_audience("年轻妈妈群体")
        assert result == "年轻妈妈群体"

    def test_validate_target_audience_too_short(self):
        """测试目标受众太短"""
        with pytest.raises(ValidationError) as exc_info:
            BusinessInputValidator.validate_target_audience("短")
        assert "目标受众描述太短" in str(exc_info.value.message)

    def test_validate_target_audience_no_chinese(self):
        """测试目标受众缺少中文"""
        with pytest.raises(ValidationError) as exc_info:
            BusinessInputValidator.validate_target_audience("young mothers")
        assert "应包含中文内容" in str(exc_info.value.message)

    def test_validate_key_message_success(self):
        """测试有效的核心信息验证"""
        result = BusinessInputValidator.validate_key_message("我们的母婴产品安全、温和、有效")
        assert result == "我们的母婴产品安全、温和、有效"

    def test_validate_key_message_too_short(self):
        """测试核心信息太短"""
        with pytest.raises(ValidationError) as exc_info:
            BusinessInputValidator.validate_key_message("短")
        assert "核心信息描述太短" in str(exc_info.value.message)


class TestTechnicalSpecsValidator:
    """测试技术规格验证器"""

    def test_validate_duration_success(self):
        """测试有效的时长验证"""
        result = TechnicalSpecsValidator.validate_duration(60)
        assert result == 60

    def test_validate_duration_too_short(self):
        """测试时长太短"""
        with pytest.raises(ValidationError) as exc_info:
            TechnicalSpecsValidator.validate_duration(3)
        assert "视频时长太短" in str(exc_info.value.message)

    def test_validate_duration_too_long(self):
        """测试时长太长"""
        with pytest.raises(ValidationError) as exc_info:
            TechnicalSpecsValidator.validate_duration(400)
        assert "视频时长太长" in str(exc_info.value.message)

    def test_validate_resolution_success(self):
        """测试有效的分辨率验证"""
        result = TechnicalSpecsValidator.validate_resolution("1080p")
        assert result == "1080p"

    def test_validate_resolution_invalid(self):
        """测试无效的分辨率"""
        with pytest.raises(ValidationError) as exc_info:
            TechnicalSpecsValidator.validate_resolution("720i")
        assert "不支持的分辨率" in str(exc_info.value.message)


class TestProjectValidator:
    """测试项目验证器"""

    def test_validate_title_success(self):
        """测试有效的项目标题验证"""
        result = ProjectValidator.validate_title("母婴产品推广视频")
        assert result == "母婴产品推广视频"

    def test_validate_title_empty(self):
        """测试空标题"""
        with pytest.raises(ValidationError) as exc_info:
            ProjectValidator.validate_title("")
        assert "项目标题不能为空" in str(exc_info.value.message)

    def test_validate_title_sensitive_word(self):
        """测试标题包含敏感词"""
        with pytest.raises(ValidationError) as exc_info:
            ProjectValidator.validate_title("暴力游戏推广视频")
        assert "包含不当词汇" in str(exc_info.value.message)

    def test_validate_project_type_invalid(self):
        """测试无效的项目类型"""
        with pytest.raises(ValidationError) as exc_info:
            ProjectValidator.validate_project_type("invalid_type")
        assert "不支持的项目类型" in str(exc_info.value.message)

    def test_validate_priority_invalid(self):
        """测试无效的优先级"""
        with pytest.raises(ValidationError) as exc_info:
            ProjectValidator.validate_priority("invalid_priority")
        assert "不支持的优先级" in str(exc_info.value.message)

    def test_validate_deadline_past(self):
        """测试过去的截止日期"""
        past_date = datetime.utcnow() - timedelta(days=1)
        with pytest.raises(ValidationError) as exc_info:
            ProjectValidator.validate_deadline(past_date)
        assert "截止日期不能早于当前时间" in str(exc_info.value.message)


class TestChineseContentValidator:
    """测试中文内容验证器"""

    def test_validate_chinese_content_success(self):
        """测试有效的中文内容验证"""
        result = ChineseContentValidator.validate_chinese_content("这是一个很好的中文内容")
        assert result == "这是一个很好的中文内容"

    def test_validate_chinese_content_insufficient_chars(self):
        """测试中文字符不足"""
        with pytest.raises(ValidationError) as exc_info:
            ChineseContentValidator.validate_chinese_content("ab")
        assert "中文字符数量不足" in str(exc_info.value.message)

    def test_validate_chinese_text_quality_invalid_chars(self):
        """测试包含无效字符"""
        with pytest.raises(ValidationError) as exc_info:
            ChineseContentValidator.validate_chinese_text_quality("内容\x00包含控制字符")
        assert "内容包含无效字符" in str(exc_info.value.message)

    def test_validate_chinese_text_quality_excessive_repetition(self):
        """测试过多重复字符"""
        with pytest.raises(ValidationError) as exc_info:
            ChineseContentValidator.validate_chinese_text_quality("aaaaaaaaaa")
        assert "内容包含过多重复字符" in str(exc_info.value.message)


class TestContentModerationValidator:
    """测试内容审核验证器"""

    def test_validate_content_compliance_sensitive_words(self):
        """测试内容包含敏感词"""
        with pytest.raises(ValidationError) as exc_info:
            ContentModerationValidator.validate_content_compliance("这个产品涉及政治和政策问题")
        assert "内容包含敏感词汇" in str(exc_info.value.message)

    def test_validate_content_compliance_success(self):
        """测试合规内容"""
        result = ContentModerationValidator.validate_content_compliance("这是一个很好的产品推荐")
        assert result == "这是一个很好的产品推荐"

    def test_validate_platform_compliance_banned_words(self):
        """测试平台特定禁用词"""
        with pytest.raises(ValidationError) as exc_info:
            ContentModerationValidator.validate_platform_compliance("抖音是最好的平台", "douyin")
        assert "平台内容包含禁用词汇" in str(exc_info.value.message)


class TestComprehensiveValidation:
    """测试综合验证功能"""

    def test_validate_project_creation_data_success(self):
        """测试有效的项目创建数据验证"""
        data = {
            "title": "母婴产品推广视频",
            "description": "为年轻妈妈群体制作的产品介绍视频",
            "project_type": "promotional",
            "priority": "medium",
            "business_input": {
                "target_audience": "年轻妈妈群体",
                "key_message": "我们的母婴产品安全、温和、有效",
                "brand_voice": "温暖、专业、可信",
                "call_to_action": "立即购买，给宝宝最好的呵护",
                "cultural_context": "中国家庭注重宝宝健康和安全",
                "platform_target": "douyin"
            },
            "technical_specs": {
                "target_duration": 60,
                "resolution": "1080p",
                "aspect_ratio": "16:9",
                "frame_rate": 24
            }
        }

        result = validate_project_creation_data(data)
        assert result["title"] == "母婴产品推广视频"
        assert result["business_input"]["target_audience"] == "年轻妈妈群体"

    def test_validate_project_creation_data_invalid_title(self):
        """测试项目创建数据包含无效标题"""
        data = {
            "title": "暴力游戏推广视频",
            "business_input": {
                "target_audience": "年轻妈妈群体",
                "key_message": "我们的母婴产品安全、温和、有效",
                "brand_voice": "温暖、专业、可信",
                "call_to_action": "立即购买，给宝宝最好的呵护",
                "cultural_context": "中国家庭注重宝宝健康和安全",
                "platform_target": "douyin"
            },
            "technical_specs": {
                "target_duration": 60,
                "resolution": "1080p",
                "aspect_ratio": "16:9",
                "frame_rate": 24
            }
        }

        with pytest.raises(ValidationError) as exc_info:
            validate_project_creation_data(data)
        assert "包含不当词汇" in str(exc_info.value.message)

    def test_validate_project_creation_data_invalid_platform_duration(self):
        """测试项目创建数据包含无效平台时长"""
        data = {
            "title": "母婴产品推广视频",
            "business_input": {
                "target_audience": "年轻妈妈群体",
                "key_message": "我们的母婴产品安全、温和、有效",
                "brand_voice": "温暖、专业、可信",
                "call_to_action": "立即购买，给宝宝最好的呵护",
                "cultural_context": "中国家庭注重宝宝健康和安全",
                "platform_target": "douyin"
            },
            "technical_specs": {
                "target_duration": 120,  # 抖音平台最长60秒
                "resolution": "1080p",
                "aspect_ratio": "16:9",
                "frame_rate": 24
            }
        }

        with pytest.raises(ValidationError) as exc_info:
            validate_project_creation_data(data)
        assert "不能多于60秒" in str(exc_info.value.message)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])