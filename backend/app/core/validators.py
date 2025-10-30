"""
数据验证模块 - Data validation module

提供统一的数据验证功能，支持中文内容验证和平台特定规则
Provides unified data validation functionality, supporting Chinese content validation and platform-specific rules
"""

import re
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, validator, Field, ValidationError as PydanticValidationError
from datetime import datetime

from app.core.exceptions import ValidationError
from app.core.database import PlatformTarget, ProjectStatus


class BusinessInputValidator:
    """业务输入验证器 / Business input validator"""

    @staticmethod
    def validate_target_audience(audience: str) -> str:
        """验证目标受众 / Validate target audience"""
        if not audience or len(audience.strip()) < 2:
            raise ValidationError(
                "目标受众描述太短，请提供至少2个字符的中文描述",
                details={"field": "target_audience", "min_length": 2, "actual_length": len(audience) if audience else 0}
            )

        if len(audience) > 200:
            raise ValidationError(
                "目标受众描述太长，请控制在200字符以内",
                details={"field": "target_audience", "max_length": 200, "actual_length": len(audience)}
            )

        # 检查是否包含中文字符 / Check if contains Chinese characters
        if not re.search(r'[\u4e00-\u9fff]', audience):
            raise ValidationError(
                "目标受众描述应包含中文内容，以更好地适应中国社交媒体平台",
                details={"field": "target_audience", "suggestion": "请使用中文描述目标受众"}
            )

        return audience.strip()

    @staticmethod
    def validate_key_message(message: str) -> str:
        """验证核心信息 / Validate key message"""
        if not message or len(message.strip()) < 5:
            raise ValidationError(
                "核心信息描述太短，请提供至少5个字符的详细描述",
                details={"field": "key_message", "min_length": 5, "actual_length": len(message) if message else 0}
            )

        if len(message) > 500:
            raise ValidationError(
                "核心信息描述太长，请控制在500字符以内",
                details={"field": "key_message", "max_length": 500, "actual_length": len(message)}
            )

        return message.strip()

    @staticmethod
    def validate_brand_voice(voice: str) -> str:
        """验证品牌调性 / Validate brand voice"""
        if not voice or len(voice.strip()) < 2:
            raise ValidationError(
                "品牌调性描述太短，请提供至少2个字符的描述",
                details={"field": "brand_voice", "min_length": 2, "actual_length": len(voice) if voice else 0}
            )

        if len(voice) > 100:
            raise ValidationError(
                "品牌调性描述太长，请控制在100字符以内",
                details={"field": "brand_voice", "max_length": 100, "actual_length": len(voice)}
            )

        return voice.strip()

    @staticmethod
    def validate_call_to_action(cta: str) -> str:
        """验证行动号召 / Validate call to action"""
        if not cta or len(cta.strip()) < 2:
            raise ValidationError(
                "行动号召描述太短，请提供至少2个字符的描述",
                details={"field": "call_to_action", "min_length": 2, "actual_length": len(cta) if cta else 0}
            )

        if len(cta) > 200:
            raise ValidationError(
                "行动号召描述太长，请控制在200字符以内",
                details={"field": "call_to_action", "max_length": 200, "actual_length": len(cta)}
            )

        return cta.strip()

    @staticmethod
    def validate_cultural_context(context: str) -> str:
        """验证文化背景 / Validate cultural context"""
        if not context or len(context.strip()) < 5:
            raise ValidationError(
                "文化背景描述太短，请提供至少5个字符的详细描述",
                details={"field": "cultural_context", "min_length": 5, "actual_length": len(context) if context else 0}
            )

        if len(context) > 1000:
            raise ValidationError(
                "文化背景描述太长，请控制在1000字符以内",
                details={"field": "cultural_context", "max_length": 1000, "actual_length": len(context)}
            )

        # 检查是否包含中文字符 / Check if contains Chinese characters
        if not re.search(r'[\u4e00-\u9fff]', context):
            raise ValidationError(
                "文化背景描述应包含中文内容，以更好地适应中国文化背景",
                details={"field": "cultural_context", "suggestion": "请使用中文描述文化背景"}
            )

        return context.strip()


class TechnicalSpecsValidator:
    """技术规格验证器 / Technical specs validator"""

    @staticmethod
    def validate_duration(duration: int) -> int:
        """验证视频时长 / Validate video duration"""
        if not isinstance(duration, int):
            raise ValidationError(
                "视频时长必须是整数",
                details={"field": "duration", "type": type(duration).__name__, "expected_type": "int"}
            )

        if duration < 5:
            raise ValidationError(
                "视频时长太短，最少5秒",
                details={"field": "duration", "min_value": 5, "actual_value": duration}
            )

        if duration > 300:
            raise ValidationError(
                "视频时长太长，最多300秒",
                details={"field": "duration", "max_value": 300, "actual_value": duration}
            )

        return duration

    @staticmethod
    def validate_resolution(resolution: str) -> str:
        """验证分辨率 / Validate resolution"""
        valid_resolutions = ["720p", "1080p", "1440p", "4K", "8K"]
        if resolution not in valid_resolutions:
            raise ValidationError(
                f"不支持的分辨率: {resolution}",
                details={"field": "resolution", "valid_values": valid_resolutions, "actual_value": resolution}
            )
        return resolution

    @staticmethod
    def validate_aspect_ratio(aspect_ratio: str) -> str:
        """验证宽高比 / Validate aspect ratio"""
        valid_ratios = ["16:9", "9:16", "1:1", "4:3", "21:9"]
        if aspect_ratio not in valid_ratios:
            raise ValidationError(
                f"不支持的宽高比: {aspect_ratio}",
                details={"field": "aspect_ratio", "valid_values": valid_ratios, "actual_value": aspect_ratio}
            )
        return aspect_ratio

    @staticmethod
    def validate_frame_rate(frame_rate: int) -> int:
        """验证帧率 / Validate frame rate"""
        valid_frame_rates = [24, 25, 30, 48, 50, 60]
        if frame_rate not in valid_frame_rates:
            raise ValidationError(
                f"不支持的帧率: {frame_rate}",
                details={"field": "frame_rate", "valid_values": valid_frame_rates, "actual_value": frame_rate}
            )
        return frame_rate


class PlatformTargetValidator:
    """平台目标验证器 / Platform target validator"""

    @staticmethod
    def validate_platform_target(platform: str) -> str:
        """验证目标平台 / Validate target platform"""
        valid_platforms = [p.value for p in PlatformTarget]
        if platform not in valid_platforms:
            raise ValidationError(
                f"不支持的目标平台: {platform}",
                details={"field": "platform_target", "valid_platforms": valid_platforms, "actual_value": platform}
            )
        return platform

    @staticmethod
    def validate_platform_specific_requirements(platform: str, content: Dict[str, Any]) -> Dict[str, Any]:
        """验证平台特定要求 / Validate platform-specific requirements"""
        platform_rules = {
            "douyin": {
                "max_duration": 60,
                "min_duration": 3,
                "preferred_aspect_ratios": ["9:16"],
                "max_title_length": 100,
                "max_description_length": 2000
            },
            "xiaohongshu": {
                "max_duration": 300,
                "min_duration": 5,
                "preferred_aspect_ratios": ["3:4", "9:16", "1:1"],
                "max_title_length": 50,
                "max_description_length": 1000
            },
            "wechat": {
                "max_duration": 300,
                "min_duration": 5,
                "preferred_aspect_ratios": ["16:9", "9:16"],
                "max_title_length": 64,
                "max_description_length": 1000
            },
            "weibo": {
                "max_duration": 300,
                "min_duration": 5,
                "preferred_aspect_ratios": ["16:9", "9:16"],
                "max_title_length": 140,
                "max_description_length": 2000
            },
            "bilibili": {
                "max_duration": 300,
                "min_duration": 5,
                "preferred_aspect_ratios": ["16:9"],
                "max_title_length": 80,
                "max_description_length": 2000
            },
            "youtube": {
                "max_duration": 300,
                "min_duration": 5,
                "preferred_aspect_ratios": ["16:9"],
                "max_title_length": 100,
                "max_description_length": 5000
            }
        }

        if platform in platform_rules:
            rules = platform_rules[platform]

            # 验证时长限制 / Validate duration limits
            if "duration" in content:
                duration = content["duration"]
                if duration < rules["min_duration"]:
                    raise ValidationError(
                        f"{platform}平台视频时长不能少于{rules['min_duration']}秒",
                        details={"field": "duration", "platform": platform, "min_duration": rules["min_duration"], "actual_duration": duration}
                    )
                if duration > rules["max_duration"]:
                    raise ValidationError(
                        f"{platform}平台视频时长不能多于{rules['max_duration']}秒",
                        details={"field": "duration", "platform": platform, "max_duration": rules["max_duration"], "actual_duration": duration}
                    )

        return content


class ProjectValidator:
    """项目验证器 / Project validator"""

    @staticmethod
    def validate_title(title: str) -> str:
        """验证项目标题 / Validate project title"""
        if not title or len(title.strip()) < 1:
            raise ValidationError(
                "项目标题不能为空",
                details={"field": "title", "error": "empty_title"}
            )

        if len(title) > 200:
            raise ValidationError(
                "项目标题太长，请控制在200字符以内",
                details={"field": "title", "max_length": 200, "actual_length": len(title)}
            )

        # 检查是否包含敏感词 / Check for sensitive words
        sensitive_words = ["暴力", "色情", "政治", "反动", "违法", "犯罪"]
        for word in sensitive_words:
            if word in title:
                raise ValidationError(
                    f"项目标题包含不当词汇: {word}",
                    details={"field": "title", "sensitive_word": word}
                )

        return title.strip()

    @staticmethod
    def validate_description(description: Optional[str]) -> Optional[str]:
        """验证项目描述 / Validate project description"""
        if description is None:
            return None

        if len(description) > 2000:
            raise ValidationError(
                "项目描述太长，请控制在2000字符以内",
                details={"field": "description", "max_length": 2000, "actual_length": len(description)}
            )

        # 检查是否包含敏感词 / Check for sensitive words
        sensitive_words = ["暴力", "色情", "政治", "反动", "违法", "犯罪"]
        for word in sensitive_words:
            if word in description:
                raise ValidationError(
                    f"项目描述包含不当词汇: {word}",
                    details={"field": "description", "sensitive_word": word}
                )

        return description.strip() if description else None

    @staticmethod
    def validate_project_type(project_type: str) -> str:
        """验证项目类型 / Validate project type"""
        valid_types = ["promotional", "educational", "entertainment", "news", "tutorial", "review"]
        if project_type not in valid_types:
            raise ValidationError(
                f"不支持的项目类型: {project_type}",
                details={"field": "project_type", "valid_types": valid_types, "actual_value": project_type}
            )
        return project_type

    @staticmethod
    def validate_priority(priority: str) -> str:
        """验证优先级 / Validate priority"""
        valid_priorities = ["low", "medium", "high", "urgent"]
        if priority not in valid_priorities:
            raise ValidationError(
                f"不支持的优先级: {priority}",
                details={"field": "priority", "valid_priorities": valid_priorities, "actual_value": priority}
            )
        return priority

    @staticmethod
    def validate_deadline(deadline: Optional[datetime]) -> Optional[datetime]:
        """验证截止日期 / Validate deadline"""
        if deadline is None:
            return None

        if deadline < datetime.utcnow():
            raise ValidationError(
                "截止日期不能早于当前时间",
                details={"field": "deadline", "error": "past_deadline", "current_time": datetime.utcnow().isoformat()}
            )

        # 检查是否超过合理范围（比如1年后）/ Check if beyond reasonable range (e.g., 1 year)
        max_future_date = datetime.utcnow().replace(year=datetime.utcnow().year + 1)
        if deadline > max_future_date:
            raise ValidationError(
                "截止日期不能超过1年后",
                details={"field": "deadline", "max_future_date": max_future_date.isoformat()}
            )

        return deadline


class ChineseContentValidator:
    """中文内容验证器 / Chinese content validator"""

    @staticmethod
    def validate_chinese_content(text: str, min_chinese_chars: int = 2) -> str:
        """验证中文内容 / Validate Chinese content"""
        if not text or len(text.strip()) < min_chinese_chars:
            raise ValidationError(
                f"中文内容太短，请提供至少{min_chinese_chars}个字符的中文内容",
                details={"field": "text", "min_length": min_chinese_chars, "actual_length": len(text) if text else 0}
            )

        # 检查是否包含中文字符 / Check if contains Chinese characters
        chinese_chars = re.findall(r'[\u4e00-\u9fff]', text)
        if len(chinese_chars) < min_chinese_chars:
            raise ValidationError(
                f"内容中中文字符数量不足，需要至少{min_chinese_chars}个中文字符",
                details={"field": "text", "min_chinese_chars": min_chinese_chars, "actual_chinese_chars": len(chinese_chars)}
            )

        return text.strip()

    @staticmethod
    def validate_chinese_text_quality(text: str) -> str:
        """验证中文文本质量 / Validate Chinese text quality"""
        # 检查是否包含乱码或特殊字符 / Check for garbled text or special characters
        invalid_patterns = [
            r'[\u0000-\u001f]',  # 控制字符 / Control characters
            r'[\u0080-\u009f]',  # 控制字符 / Control characters
            r'[\ufffe-\uffff]',  # Unicode特殊字符 / Unicode special characters
        ]

        for pattern in invalid_patterns:
            if re.search(pattern, text):
                raise ValidationError(
                    "内容包含无效字符",
                    details={"field": "text", "error": "invalid_characters", "pattern": pattern}
                )

        # 检查是否包含过多重复字符 / Check for too many repeated characters
        for char in set(text):
            if text.count(char) > len(text) * 0.3:  # 单个字符出现超过30% / Single character appears more than 30%
                raise ValidationError(
                    "内容包含过多重复字符",
                    details={"field": "text", "error": "excessive_repetition", "character": char}
                )

        return text.strip()


class ContentModerationValidator:
    """内容审核验证器 / Content moderation validator"""

    @staticmethod
    def validate_content_compliance(text: str) -> str:
        """验证内容合规性 / Validate content compliance"""
        # 敏感词列表 / Sensitive words list
        sensitive_words = [
            # 政治敏感 / Political sensitivity
            "国家领导人", "政府", "政策", "政治", "政权", "体制",
            # 暴力血腥 / Violence and gore
            "暴力", "血腥", "杀戮", "战争", "武器", "枪支",
            # 色情低俗 / Pornographic and vulgar
            "色情", "性", "裸体", "低俗", "淫秽", "挑逗",
            # 违法犯罪 / Illegal and criminal
            "毒品", "赌博", "诈骗", "盗窃", "抢劫", "杀人",
            # 其他敏感 / Other sensitive
            "邪教", "迷信", "谣言", "虚假", "欺骗", "误导"
        ]

        found_sensitive_words = []
        for word in sensitive_words:
            if word in text:
                found_sensitive_words.append(word)

        if found_sensitive_words:
            raise ValidationError(
                f"内容包含敏感词汇: {', '.join(found_sensitive_words)}",
                details={"field": "text", "sensitive_words": found_sensitive_words}
            )

        return text.strip()

    @staticmethod
    def validate_platform_compliance(text: str, platform: str) -> str:
        """验证平台特定合规性 / Validate platform-specific compliance"""
        platform_restrictions = {
            "douyin": {
                "banned_words": ["抖音", "tiktok", "竞争对手"],
                "max_caps_ratio": 0.3,  # 大写字母比例上限 / Uppercase letter ratio limit
            },
            "xiaohongshu": {
                "banned_words": ["小红书", "广告", "推销"],
                "max_hashtags": 30,
            },
            "wechat": {
                "banned_words": ["微信", "wechat", "腾讯"],
                "max_external_links": 0,  # 不允许外部链接 / No external links allowed
            },
            "weibo": {
                "banned_words": ["微博", "新浪"],
                "max_mentions": 50,
            },
            "bilibili": {
                "banned_words": ["哔哩哔哩", "bilibili", "B站"],
                "min_video_quality": "720p",
            }
        }

        if platform in platform_restrictions:
            restrictions = platform_restrictions[platform]

            # 检查禁用词汇 / Check banned words
            banned_words = restrictions.get("banned_words", [])
            found_banned_words = [word for word in banned_words if word in text]

            if found_banned_words:
                raise ValidationError(
                    f"{platform}平台内容包含禁用词汇: {', '.join(found_banned_words)}",
                    details={"field": "text", "platform": platform, "banned_words": found_banned_words}
                )

        return text.strip()


# 统一的验证函数 / Unified validation functions
def validate_project_creation_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """验证项目创建数据 / Validate project creation data"""
    try:
        # 验证基本信息 / Validate basic information
        if "title" in data:
            data["title"] = ProjectValidator.validate_title(data["title"])

        if "description" in data:
            data["description"] = ProjectValidator.validate_description(data.get("description"))

        if "project_type" in data:
            data["project_type"] = ProjectValidator.validate_project_type(data["project_type"])

        if "priority" in data:
            data["priority"] = ProjectValidator.validate_priority(data["priority"])

        if "deadline" in data:
            data["deadline"] = ProjectValidator.validate_deadline(data.get("deadline"))

        # 验证业务输入 / Validate business input
        if "business_input" in data:
            business_input = data["business_input"]

            if "target_audience" in business_input:
                business_input["target_audience"] = BusinessInputValidator.validate_target_audience(
                    business_input["target_audience"]
                )

            if "key_message" in business_input:
                business_input["key_message"] = BusinessInputValidator.validate_key_message(
                    business_input["key_message"]
                )

            if "brand_voice" in business_input:
                business_input["brand_voice"] = BusinessInputValidator.validate_brand_voice(
                    business_input["brand_voice"]
                )

            if "call_to_action" in business_input:
                business_input["call_to_action"] = BusinessInputValidator.validate_call_to_action(
                    business_input["call_to_action"]
                )

            if "cultural_context" in business_input:
                business_input["cultural_context"] = BusinessInputValidator.validate_cultural_context(
                    business_input["cultural_context"]
                )

            if "platform_target" in business_input:
                business_input["platform_target"] = PlatformTargetValidator.validate_platform_target(
                    business_input["platform_target"]
                )

        # 验证技术规格 / Validate technical specs
        if "technical_specs" in data:
            tech_specs = data["technical_specs"]

            if "target_duration" in tech_specs:
                tech_specs["target_duration"] = TechnicalSpecsValidator.validate_duration(
                    tech_specs["target_duration"]
                )

            if "resolution" in tech_specs:
                tech_specs["resolution"] = TechnicalSpecsValidator.validate_resolution(
                    tech_specs["resolution"]
                )

            if "aspect_ratio" in tech_specs:
                tech_specs["aspect_ratio"] = TechnicalSpecsValidator.validate_aspect_ratio(
                    tech_specs["aspect_ratio"]
                )

            if "frame_rate" in tech_specs:
                tech_specs["frame_rate"] = TechnicalSpecsValidator.validate_frame_rate(
                    tech_specs["frame_rate"]
                )

        return data

    except ValidationError:
        raise
    except Exception as e:
        raise ValidationError(
            f"数据验证失败: {str(e)}",
            details={"error": str(e), "data_type": type(data).__name__}
        )


def validate_chinese_content(text: str, field_name: str = "content") -> str:
    """验证中文内容 / Validate Chinese content"""
    try:
        # 基本文本验证 / Basic text validation
        text = ChineseContentValidator.validate_chinese_content(text)

        # 文本质量验证 / Text quality validation
        text = ChineseContentValidator.validate_chinese_text_quality(text)

        # 内容合规性验证 / Content compliance validation
        text = ContentModerationValidator.validate_content_compliance(text)

        return text

    except ValidationError:
        raise
    except Exception as e:
        raise ValidationError(
            f"中文内容验证失败: {str(e)}",
            details={"field": field_name, "error": str(e)}
        )


# 错误消息映射 / Error message mapping
ERROR_MESSAGES = {
    "zh-CN": {
        "VALIDATION_ERROR": "数据验证失败",
        "MISSING_FIELD": "缺少必需字段",
        "INVALID_FORMAT": "格式无效",
        "LENGTH_TOO_SHORT": "内容太短",
        "LENGTH_TOO_LONG": "内容太长",
        "INVALID_VALUE": "值无效",
        "PLATFORM_NOT_SUPPORTED": "不支持的平台",
        "SENSITIVE_CONTENT": "内容包含敏感信息",
        "CULTURAL_INAPPROPRIATE": "文化背景不合适",
    },
    "en-US": {
        "VALIDATION_ERROR": "Data validation failed",
        "MISSING_FIELD": "Missing required field",
        "INVALID_FORMAT": "Invalid format",
        "LENGTH_TOO_SHORT": "Content too short",
        "LENGTH_TOO_LONG": "Content too long",
        "INVALID_VALUE": "Invalid value",
        "PLATFORM_NOT_SUPPORTED": "Platform not supported",
        "SENSITIVE_CONTENT": "Content contains sensitive information",
        "CULTURAL_INAPPROPRIATE": "Cultural background inappropriate",
    }
}

def get_error_message(error_code: str, locale: str = "zh-CN") -> str:
    """获取本地化的错误消息 / Get localized error message"""
    return ERROR_MESSAGES.get(locale, ERROR_MESSAGES["zh-CN"]).get(error_code, "未知错误")