#!/usr/bin/env python3
"""
系统状态检查脚本 - System Status Check Script
检查中国AI视频创作系统的当前状态和配置
"""

import os
import sys
import json
import subprocess
import requests
from pathlib import Path
from typing import Dict, List, Optional

class Colors:
    """终端颜色输出"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'

class SystemChecker:
    """系统状态检查器"""

    def __init__(self):
        self.results = []
        self.project_root = Path(__file__).parent

    def log_success(self, message: str):
        """记录成功信息"""
        print(f"{Colors.GREEN}✅ {message}{Colors.RESET}")
        self.results.append({"status": "success", "message": message})

    def log_error(self, message: str):
        """记录错误信息"""
        print(f"{Colors.RED}❌ {message}{Colors.RESET}")
        self.results.append({"status": "error", "message": message})

    def log_warning(self, message: str):
        """记录警告信息"""
        print(f"{Colors.YELLOW}⚠️  {message}{Colors.RESET}")
        self.results.append({"status": "warning", "message": message})

    def log_info(self, message: str):
        """记录信息"""
        print(f"{Colors.BLUE}ℹ️  {message}{Colors.RESET}")
        self.results.append({"status": "info", "message": message})

    def check_environment_file(self) -> bool:
        """检查环境文件"""
        env_file = self.project_root / "backend" / ".env"
        env_example = self.project_root / "backend" / ".env.example"

        if not env_file.exists():
            if env_example.exists():
                self.log_warning("未找到 .env 文件，但有 .env.example 模板")
                self.log_info("请复制 .env.example 到 .env 并配置API密钥")
                return False
            else:
                self.log_error("未找到环境配置文件")
                return False

        # 检查关键配置
        with open(env_file, 'r', encoding='utf-8') as f:
            content = f.read()

        required_keys = [
            'DEEPSEEK_API_KEY',
            'VOLC_ACCESS_KEY',
            'VOLC_SECRET_KEY',
            'JWT_SECRET_KEY'
        ]

        missing_keys = []
        empty_keys = []

        for key in required_keys:
            if key not in content:
                missing_keys.append(key)
            else:
                # 检查是否为空值
                for line in content.split('\n'):
                    if line.startswith(f'{key}='):
                        value = line.split('=', 1)[1].strip()
                        if not value or value == 'your_key_here':
                            empty_keys.append(key)
                        break

        if missing_keys:
            self.log_error(f"缺失环境变量: {', '.join(missing_keys)}")
            return False

        if empty_keys:
            self.log_warning(f"空值环境变量: {', '.join(empty_keys)}")
            return False

        self.log_success("环境文件配置正确")
        return True

    def check_docker_setup(self) -> bool:
        """检查Docker配置"""
        docker_files = [
            "docker-compose.yml",
            "docker-compose.prod.yml",
            "backend/Dockerfile",
            "frontend/Dockerfile"
        ]

        missing_files = []
        for file in docker_files:
            file_path = self.project_root / file
            if not file_path.exists():
                missing_files.append(file)

        if missing_files:
            self.log_warning(f"缺失Docker文件: {', '.join(missing_files)}")
            return False

        self.log_success("Docker配置文件完整")
        return True

    def check_project_structure(self) -> bool:
        """检查项目结构"""
        required_dirs = [
            "backend/app",
            "backend/app/api",
            "backend/app/services",
            "frontend/src",
            "frontend/public",
            "tests"
        ]

        missing_dirs = []
        for dir_path in required_dirs:
            full_path = self.project_root / dir_path
            if not full_path.exists():
                missing_dirs.append(dir_path)

        if missing_dirs:
            self.log_error(f"缺失项目目录: {', '.join(missing_dirs)}")
            return False

        self.log_success("项目结构完整")
        return True

    def check_backend_dependencies(self) -> bool:
        """检查后端依赖"""
        requirements_file = self.project_root / "backend" / "requirements.txt"

        if not requirements_file.exists():
            self.log_error("未找到requirements.txt文件")
            return False

        try:
            # 检查Python环境
            result = subprocess.run([sys.executable, "--version"],
                                  capture_output=True, text=True)
            if result.returncode == 0:
                self.log_info(f"Python版本: {result.stdout.strip()}")
            else:
                self.log_error("Python环境检查失败")
                return False

            # 检查pip
            result = subprocess.run([sys.executable, "-m", "pip", "--version"],
                                  capture_output=True, text=True)
            if result.returncode == 0:
                self.log_info(f"Pip版本: {result.stdout.strip()}")
            else:
                self.log_error("Pip环境检查失败")
                return False

        except Exception as e:
            self.log_error(f"依赖检查失败: {e}")
            return False

        self.log_success("后端依赖环境就绪")
        return True

    def check_frontend_dependencies(self) -> bool:
        """检查前端依赖"""
        package_json = self.project_root / "frontend" / "package.json"

        if not package_json.exists():
            self.log_error("未找到package.json文件")
            return False

        try:
            # 检查Node.js
            result = subprocess.run(["node", "--version"],
                                  capture_output=True, text=True)
            if result.returncode == 0:
                self.log_info(f"Node.js版本: {result.stdout.strip()}")
            else:
                self.log_warning("Node.js未安装")
                return False

            # 检查npm
            result = subprocess.run(["npm", "--version"],
                                  capture_output=True, text=True)
            if result.returncode == 0:
                self.log_info(f"Npm版本: {result.stdout.strip()}")
            else:
                self.log_warning("Npm未安装")
                return False

        except Exception as e:
            self.log_warning(f"前端依赖检查失败: {e}")
            return False

        self.log_success("前端依赖环境就绪")
        return True

    def check_ai_service_configs(self) -> bool:
        """检查AI服务配置"""
        # 检查DeepSeek服务文件
        deepseek_file = self.project_root / "backend" / "app" / "services" / "deepseek_service.py"
        if not deepseek_file.exists():
            self.log_error("DeepSeek服务文件缺失")
            return False

        # 检查即梦服务文件
        jimeng_file = self.project_root / "backend" / "app" / "services" / "jimeng_service.py"
        if not jimeng_file.exists():
            self.log_error("即梦服务文件缺失")
            return False

        # 检查AutoGen编排器
        autogen_file = self.project_root / "backend" / "app" / "services" / "autogen_orchestrator.py"
        if not autogen_file.exists():
            self.log_error("AutoGen编排器文件缺失")
            return False

        self.log_success("AI服务配置完整")
        return True

    def check_database_models(self) -> bool:
        """检查数据库模型"""
        models_file = self.project_root / "backend" / "app" / "core" / "database.py"

        if not models_file.exists():
            self.log_error("数据库模型文件缺失")
            return False

        # 检查关键模型定义
        with open(models_file, 'r', encoding='utf-8') as f:
            content = f.read()

        required_models = ['User', 'Project', 'AIModel']
        missing_models = []

        for model in required_models:
            if f"class {model}" not in content:
                missing_models.append(model)

        if missing_models:
            self.log_error(f"缺失数据模型: {', '.join(missing_models)}")
            return False

        self.log_success("数据库模型完整")
        return True

    def check_api_endpoints(self) -> bool:
        """检查API端点"""
        api_dir = self.project_root / "backend" / "app" / "api" / "endpoints"

        if not api_dir.exists():
            self.log_error("API端点目录缺失")
            return False

        required_endpoints = [
            "projects.py",
            "users.py",
            "assets.py"
        ]

        missing_endpoints = []
        for endpoint in required_endpoints:
            endpoint_file = api_dir / endpoint
            if not endpoint_file.exists():
                missing_endpoints.append(endpoint)

        if missing_endpoints:
            self.log_warning(f"缺失API端点: {', '.join(missing_endpoints)}")
            return False

        self.log_success("API端点配置完整")
        return True

    def check_testing_setup(self) -> bool:
        """检查测试设置"""
        tests_dir = self.project_root / "tests"

        if not tests_dir.exists():
            self.log_warning("测试目录不存在")
            return False

        # 检查pytest配置
        pytest_ini = self.project_root / "pytest.ini"
        if not pytest_ini.exists():
            self.log_warning("pytest.ini配置文件不存在")

        # 检查测试文件
        test_files = list(tests_dir.glob("test_*.py"))
        if not test_files:
            self.log_warning("未找到测试文件")
            return False

        self.log_info(f"找到 {len(test_files)} 个测试文件")
        self.log_success("测试配置就绪")
        return True

    def check_documentation(self) -> bool:
        """检查文档"""
        doc_files = [
            "README.md",
            "IMPLEMENTATION_SUMMARY.md",
            "PRODUCTION_DEPLOYMENT.md"
        ]

        missing_docs = []
        for doc in doc_files:
            doc_path = self.project_root / doc
            if not doc_path.exists():
                missing_docs.append(doc)

        if missing_docs:
            self.log_warning(f"缺失文档文件: {', '.join(missing_docs)}")
            return False

        self.log_success("项目文档完整")
        return True

    def generate_report(self) -> Dict:
        """生成检查报告"""
        total_checks = len(self.results)
        success_count = len([r for r in self.results if r["status"] == "success"])
        error_count = len([r for r in self.results if r["status"] == "error"])
        warning_count = len([r for r in self.results if r["status"] == "warning"])

        return {
            "total_checks": total_checks,
            "success_count": success_count,
            "error_count": error_count,
            "warning_count": warning_count,
            "success_rate": (success_count / total_checks * 100) if total_checks > 0 else 0,
            "details": self.results
        }

    def run_full_check(self) -> Dict:
        """运行完整检查"""
        print(f"{Colors.BLUE}")
        print("=" * 60)
        print("中国AI智能短视频创作系统 - 状态检查")
        print("Chinese AI Video Creation System - Status Check")
        print("=" * 60)
        print(f"{Colors.RESET}")

        checks = [
            ("项目结构", self.check_project_structure),
            ("环境配置", self.check_environment_file),
            ("Docker设置", self.check_docker_setup),
            ("后端依赖", self.check_backend_dependencies),
            ("前端依赖", self.check_frontend_dependencies),
            ("AI服务配置", self.check_ai_service_configs),
            ("数据库模型", self.check_database_models),
            ("API端点", self.check_api_endpoints),
            ("测试设置", self.check_testing_setup),
            ("项目文档", self.check_documentation)
        ]

        for check_name, check_func in checks:
            print(f"\n{Colors.BLUE}--- 检查: {check_name} ---{Colors.RESET}")
            try:
                check_func()
            except Exception as e:
                self.log_error(f"检查失败: {e}")

        report = self.generate_report()

        print(f"\n{Colors.BLUE}")
        print("=" * 60)
        print("检查结果汇总")
        print("=" * 60)
        print(f"{Colors.RESET}")

        print(f"总检查项: {report['total_checks']}")
        print(f"成功: {Colors.GREEN}{report['success_count']}{Colors.RESET}")
        print(f"错误: {Colors.RED}{report['error_count']}{Colors.RESET}")
        print(f"警告: {Colors.YELLOW}{report['warning_count']}{Colors.RESET}")
        print(f"成功率: {report['success_rate']:.1f}%")

        if report['error_count'] > 0:
            print(f"\n{Colors.RED}需要修复的错误项:{Colors.RESET}")
            for result in report['details']:
                if result['status'] == 'error':
                    print(f"  - {result['message']}")

        if report['warning_count'] > 0:
            print(f"\n{Colors.YELLOW}需要注意的警告项:{Colors.RESET}")
            for result in report['details']:
                if result['status'] == 'warning':
                    print(f"  - {result['message']}")

        print(f"\n{Colors.BLUE}")
        print("=" * 60)
        print("下一步行动建议:")
        print("=" * 60)
        print(f"{Colors.RESET}")

        if report['error_count'] > 0:
            print("1. 🔧 首先修复所有错误项")
            print("2. 📝 配置缺失的环境变量和API密钥")
            print("3. 🐳 确保Docker环境就绪")
        elif report['warning_count'] > 0:
            print("1. ⚠️  处理警告项以优化系统")
            print("2. 🚀 系统基本可用，可以开始部署")
        else:
            print("1. 🎉 系统状态良好，可以立即部署！")
            print("2. 🚀 运行 docker-compose up -d 启动服务")
            print("3. ✅ 访问 http://localhost:8000/docs 查看API文档")

        return report

def main():
    """主函数"""
    checker = SystemChecker()
    report = checker.run_full_check()

    # 保存报告到文件
    report_file = Path(__file__).parent / "system_status_report.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"\n{Colors.GREEN}检查报告已保存到: {report_file}{Colors.RESET}")

if __name__ == "__main__":
    main()