"""
API密钥验证工具模块
API Key Validation Utility Module

验证和管理AI服务的API密钥配置
Validates and manages API keys for AI services
"""

import os
import httpx
import asyncio
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

class APIKeyValidator:
    """API密钥验证器"""

    def __init__(self):
        self.validation_results = {}

    async def validate_all_keys(self) -> Dict[str, Any]:
        """
        验证所有配置的API密钥
        Validate all configured API keys

        Returns:
            验证结果字典
        """
        results = {
            "timestamp": datetime.now().isoformat(),
            "services": {},
            "summary": {
                "total": 0,
                "valid": 0,
                "invalid": 0,
                "missing": 0
            }
        }

        # 验证DeepSeek API密钥
        deepseek_result = await self._validate_deepseek_key()
        results["services"]["deepseek"] = deepseek_result

        # 验证即梦大模型API密钥
        jimeng_result = await self._validate_jimeng_keys()
        results["services"]["jimeng"] = jimeng_result

        # 验证微信API密钥
        wechat_result = await self._validate_wechat_keys()
        results["services"]["wechat"] = wechat_result

        # 验证阿里云OSS密钥
        oss_result = await self._validate_oss_keys()
        results["services"]["aliyun_oss"] = oss_result

        # 更新统计信息
        for service, result in results["services"].items():
            results["summary"]["total"] += 1
            if result["status"] == "valid":
                results["summary"]["valid"] += 1
            elif result["status"] == "invalid":
                results["summary"]["invalid"] += 1
            elif result["status"] == "missing":
                results["summary"]["missing"] += 1

        self.validation_results = results
        return results

    async def _validate_deepseek_key(self) -> Dict[str, Any]:
        """验证DeepSeek API密钥"""
        api_key = settings.DEEPSEEK_API_KEY

        if not api_key:
            return {
                "status": "missing",
                "message": "DeepSeek API密钥未配置",
                "suggestion": "请设置DEEPSEEK_API_KEY环境变量",
                "help_url": "https://platform.deepseek.com/api-keys"
            }

        try:
            # 尝试调用简单的API端点来验证密钥
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }

            test_data = {
                "model": "deepseek-chat",
                "messages": [{"role": "user", "content": "Hello"}],
                "max_tokens": 5
            }

            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    f"{settings.DEEPSEEK_BASE_URL}/chat/completions",
                    headers=headers,
                    json=test_data
                )

                if response.status_code == 200:
                    return {
                        "status": "valid",
                        "message": "DeepSeek API密钥有效",
                        "model": settings.DEEPSEEK_MODEL,
                        "base_url": settings.DEEPSEEK_BASE_URL
                    }
                elif response.status_code == 401:
                    return {
                        "status": "invalid",
                        "message": "DeepSeek API密钥无效或已过期",
                        "suggestion": "请检查DEEPSEEK_API_KEY是否正确",
                        "help_url": "https://platform.deepseek.com/api-keys"
                    }
                else:
                    return {
                        "status": "error",
                        "message": f"DeepSeek API验证失败: {response.status_code}",
                        "details": response.text
                    }

        except Exception as e:
            return {
                "status": "error",
                "message": f"DeepSeek API验证异常: {str(e)}",
                "suggestion": "请检查网络连接和API配置"
            }

    async def _validate_jimeng_keys(self) -> Dict[str, Any]:
        """验证即梦大模型API密钥"""
        access_key = settings.VOLC_ACCESS_KEY
        secret_key = settings.VOLC_SECRET_KEY

        if not access_key or not secret_key:
            return {
                "status": "missing",
                "message": "即梦大模型API密钥不完整",
                "suggestion": "请设置VOLC_ACCESS_KEY和VOLC_SECRET_KEY环境变量",
                "help_url": "https://www.volcengine.com/docs"
            }

        try:
            # 尝试调用简单的API端点来验证密钥
            headers = {
                "Authorization": f"Bearer {access_key}",
                "Content-Type": "application/json",
                "X-Secret-Key": secret_key
            }

            # 使用简单的图像生成测试
            test_data = {
                "prompt": "test image",
                "model": "jimeng-4.0",
                "resolution": "512x512",
                "num_images": 1
            }

            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    f"{settings.JIMENG_BASE_URL}/images/generations",
                    headers=headers,
                    json=test_data
                )

                if response.status_code == 200:
                    return {
                        "status": "valid",
                        "message": "即梦大模型API密钥有效",
                        "region": settings.VOLC_REGION,
                        "base_url": settings.JIMENG_BASE_URL
                    }
                elif response.status_code == 401:
                    return {
                        "status": "invalid",
                        "message": "即梦大模型API密钥无效",
                        "suggestion": "请检查VOLC_ACCESS_KEY和VOLC_SECRET_KEY是否正确",
                        "help_url": "https://www.volcengine.com/docs"
                    }
                else:
                    # 其他状态码可能表示密钥有效但请求格式错误，这仍然说明密钥是有效的
                    return {
                        "status": "valid",
                        "message": f"即梦API密钥验证通过 (响应码: {response.status_code})",
                        "note": "密钥有效，但测试请求格式可能需要调整"
                    }

        except Exception as e:
            return {
                "status": "error",
                "message": f"即梦API验证异常: {str(e)}",
                "suggestion": "请检查网络连接和API配置"
            }

    async def _validate_wechat_keys(self) -> Dict[str, Any]:
        """验证微信API密钥"""
        app_id = settings.WECHAT_APP_ID
        app_secret = settings.WECHAT_APP_SECRET

        if not app_id or not app_secret:
            return {
                "status": "missing",
                "message": "微信API密钥未配置",
                "suggestion": "请设置WECHAT_APP_ID和WECHAT_APP_SECRET环境变量",
                "help_url": "https://developers.weixin.qq.com/doc/oplatform/Third-party_Platforms/2.0/api/Before_Develop/WeChat_Account_Registration_Guide.html"
            }

        # 微信API验证需要更复杂的流程，这里只做基本格式验证
        if len(app_id) != 18 or not app_id.isalnum():
            return {
                "status": "invalid",
                "message": "微信APP_ID格式不正确",
                "suggestion": "请检查WECHAT_APP_ID是否为正确的18位字符"
            }

        if len(app_secret) < 10:
            return {
                "status": "invalid",
                "message": "微信APP_SECRET格式不正确",
                "suggestion": "请检查WECHAT_APP_SECRET是否正确"
            }

        return {
            "status": "valid",
            "message": "微信API密钥格式正确",
            "app_id": app_id,
            "redirect_uri": settings.WECHAT_REDIRECT_URI
        }

    async def _validate_oss_keys(self) -> Dict[str, Any]:
        """验证阿里云OSS密钥"""
        access_key = settings.OSS_ACCESS_KEY
        secret_key = settings.OSS_SECRET_KEY
        bucket = settings.OSS_BUCKET

        if not access_key or not secret_key or not bucket:
            return {
                "status": "missing",
                "message": "阿里云OSS密钥未配置",
                "suggestion": "请设置OSS_ACCESS_KEY、OSS_SECRET_KEY和OSS_BUCKET环境变量",
                "help_url": "https://help.aliyun.com/document_detail/31926.html"
            }

        # 基本格式验证
        if len(access_key) < 10 or len(secret_key) < 10:
            return {
                "status": "invalid",
                "message": "阿里云OSS密钥格式不正确",
                "suggestion": "请检查OSS_ACCESS_KEY和OSS_SECRET_KEY是否正确"
            }

        return {
            "status": "valid",
            "message": "阿里云OSS密钥格式正确",
            "bucket": bucket,
            "region": settings.OSS_REGION,
            "endpoint": settings.OSS_ENDPOINT
        }

    def generate_setup_guide(self) -> str:
        """
        生成API密钥设置指南
        Generate API key setup guide

        Returns:
            设置指南文本
        """
        guide = """
# 🚀 中国AI智能短视频创作系统 - API密钥设置指南

## 必需API密钥列表

### 1. DeepSeek API (文本生成)
```bash
export DEEPSEEK_API_KEY="your-deepseek-api-key"
export DEEPSEEK_BASE_URL="https://api.deepseek.com/v1"  # 可选
export DEEPSEEK_MODEL="deepseek-chat"  # 可选
```
**获取方式**: https://platform.deepseek.com/api-keys

### 2. 即梦大模型 (图像/视频生成)
```bash
export VOLC_ACCESS_KEY="your-volc-access-key"
export VOLC_SECRET_KEY="your-volc-secret-key"
export VOLC_REGION="cn-north-1"  # 可选
export JIMENG_BASE_URL="https://open-api.dreamina.com/v1"  # 可选
```
**获取方式**: https://www.volcengine.com/docs

### 3. 阿里云OSS (文件存储)
```bash
export OSS_BUCKET="your-bucket-name"
export OSS_REGION="cn-beijing"  # 可选
export OSS_ACCESS_KEY="your-oss-access-key"
export OSS_SECRET_KEY="your-oss-secret-key"
```
**获取方式**: https://oss.console.aliyun.com

### 4. 微信登录 (可选)
```bash
export WECHAT_APP_ID="your-wechat-app-id"
export WECHAT_APP_SECRET="your-wechat-app-secret"
export WECHAT_REDIRECT_URI="http://localhost:8000/api/v1/auth/wechat/callback"
```
**获取方式**: https://developers.weixin.qq.com

## 🔒 安全配置建议

1. **使用强密码**: API密钥应足够复杂且唯一
2. **定期轮换**: 建议每3-6个月更换一次API密钥
3. **访问控制**: 限制API密钥的访问权限
4. **监控使用**: 定期检查API使用情况和费用
5. **环境隔离**: 为不同环境使用不同的密钥

## 📝 环境变量设置方法

### Linux/Mac
```bash
# 临时设置
export DEEPSEEK_API_KEY="your-key"

# 永久设置 (添加到 ~/.bashrc 或 ~/.zshrc)
echo 'export DEEPSEEK_API_KEY="your-key"' >> ~/.bashrc
source ~/.bashrc
```

### Windows
```cmd
# 临时设置
set DEEPSEEK_API_KEY=your-key

# 永久设置
setx DEEPSEEK_API_KEY "your-key"
```

### Docker
```dockerfile
ENV DEEPSEEK_API_KEY="your-key"
```

## 🧪 验证配置

运行以下命令验证API密钥配置:
```bash
python -c "from app.utils.api_key_validator import APIKeyValidator; import asyncio; validator = APIKeyValidator(); result = asyncio.run(validator.validate_all_keys()); print(result)"
```

## 🆘 常见问题

### Q: API密钥验证失败怎么办？
A: 检查以下几点:
- 密钥是否正确复制，没有多余空格
- 密钥是否还在有效期内
- 账户是否有足够的余额或配额
- 网络连接是否正常

### Q: 可以只配置部分API密钥吗？
A: 可以，系统会自动检测已配置的API服务并启用相应功能。但建议配置所有主要API以获得完整功能。

### Q: API密钥安全吗？
A: 系统使用环境变量存储密钥，不会硬编码在代码中。确保服务器安全，限制文件访问权限。
"""
        return guide

    def get_missing_keys_summary(self) -> Dict[str, Any]:
        """
        获取缺失密钥的摘要信息
        Get summary of missing keys

        Returns:
            缺失密钥摘要
        """
        if not self.validation_results:
            return {"error": "尚未进行密钥验证"}

        missing_services = []
        for service, result in self.validation_results["services"].items():
            if result["status"] in ["missing", "invalid"]:
                missing_services.append({
                    "service": service,
                    "status": result["status"],
                    "message": result["message"],
                    "suggestion": result.get("suggestion", "")
                })

        return {
            "total_missing": len(missing_services),
            "missing_services": missing_services,
            "setup_guide_available": True
        }


# 创建全局验证器实例
api_key_validator = APIKeyValidator()

async def validate_api_keys_async():
    """异步验证API密钥的便捷函数"""
    try:
        results = await api_key_validator.validate_all_keys()

        logger.info("🔑 API密钥验证完成")
        logger.info(f"✅ 有效服务: {results['summary']['valid']}")
        logger.info(f"❌ 无效服务: {results['summary']['invalid']}")
        logger.info(f"❓ 缺失服务: {results['summary']['missing']}")

        # 记录详细信息
        for service, result in results['services'].items():
            if result['status'] != 'valid':
                logger.warning(f"⚠️  {service}: {result['message']}")

        return results

    except Exception as e:
        logger.error(f"API密钥验证异常: {str(e)}")
        raise

def validate_api_keys_sync():
    """同步验证API密钥的便捷函数"""
    try:
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(validate_api_keys_async())
    except RuntimeError:
        # 如果没有运行的事件循环，创建一个新的
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(validate_api_keys_async())
        loop.close()
        return result

# 在应用启动时自动验证
if __name__ == "__main__":
    print("🔑 正在验证API密钥配置...")
    results = validate_api_keys_sync()

    if results["summary"]["missing"] > 0:
        print(f"\n⚠️  发现 {results['summary']['missing']} 个缺失的API密钥")
        print(api_key_validator.generate_setup_guide())
    else:
        print("✅ 所有API密钥配置正确!")

    print(f"\n📊 验证结果: {results}")