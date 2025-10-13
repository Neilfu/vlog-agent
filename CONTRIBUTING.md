# 贡献指南 / Contributing Guide

感谢您对**中国AI智能短视频创作系统**项目的关注！我们欢迎所有形式的贡献，包括代码、文档、测试、设计想法和问题报告。

Thank you for your interest in the **Chinese AI Intelligent Short Video Creation System** project! We welcome all forms of contributions, including code, documentation, testing, design ideas, and issue reports.

---

## 🎯 开始之前 / Before You Start

### 行为准则 / Code of Conduct

本项目遵守[行为准则](CODE_OF_CONDUCT.md)。参与本项目即表示您同意遵守其条款。

This project adheres to the [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

### 项目概述 / Project Overview

这是一个专为中文用户设计的AI视频创作平台，集成DeepSeek和即梦大模型，提供成本效益高、文化适应性强的视频内容生成服务。

This is an AI video creation platform designed specifically for Chinese users, integrating DeepSeek and Jimeng models to provide cost-effective, culturally adapted video content generation services.

---

## 🚀 如何贡献 / How to Contribute

### 1. 报告问题 / Reporting Issues

如果您发现了错误或有功能建议，请通过[GitHub Issues](https://github.com/your-repo/issues)告诉我们：

If you find bugs or have feature suggestions, please let us know through [GitHub Issues](https://github.com/your-repo/issues):

#### 错误报告 / Bug Reports
- 使用错误报告模板
- 提供清晰的复现步骤
- 包含环境信息
- 添加相关截图

#### 功能请求 / Feature Requests
- 使用功能请求模板
- 描述清楚使用场景
- 考虑替代方案
- 设定验收标准

### 2. 代码贡献 / Code Contributions

#### 设置开发环境 / Setting Up Development Environment

1. **Fork仓库** / Fork the Repository
   ```bash
   # 点击GitHub上的Fork按钮
   # Click the Fork button on GitHub
   ```

2. **克隆您的Fork** / Clone Your Fork
   ```bash
   git clone https://github.com/YOUR_USERNAME/chinese-ai-video-system.git
   cd chinese-ai-video-system
   ```

3. **添加上游仓库** / Add Upstream Remote
   ```bash
   git remote add upstream https://github.com/ORIGINAL_OWNER/chinese-ai-video-system.git
   ```

4. **创建功能分支** / Create Feature Branch
   ```bash
   git checkout -b feature/your-feature-name
   # 或 / or
   git checkout -b fix/issue-description
   ```

#### 开发环境要求 / Development Requirements

- **Python**: 3.8+
- **Node.js**: 16+
- **Docker**: 20+
- **PostgreSQL**: 13+ (或 SQLite 用于开发)
- **Redis**: 6+

#### 后端开发设置 / Backend Development Setup

```bash
# 1. 安装Python依赖
# 1. Install Python dependencies
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows
pip install -r requirements.txt
pip install -r requirements-dev.txt  # 开发依赖

# 2. 配置环境变量
# 2. Configure environment variables
cp .env.example .env
# 编辑 .env 文件 / Edit .env file

# 3. 运行数据库迁移
# 3. Run database migrations
python -m app.db.init_db

# 4. 启动开发服务器
# 4. Start development server
uvicorn app.main:app --reload
```

#### 前端开发设置 / Frontend Development Setup

```bash
# 1. 安装Node.js依赖
# 1. Install Node.js dependencies
cd frontend
npm install

# 2. 启动开发服务器
# 2. Start development server
npm start

# 3. 运行测试
# 3. Run tests
npm test

# 4. 构建生产版本
# 4. Build for production
npm run build
```

#### 代码质量标准 / Code Quality Standards

##### Python代码规范 / Python Code Standards

- 遵循[PEP 8](https://pep8.org/)风格指南
- 使用Black进行代码格式化
- 使用Flake8进行代码检查
- 使用MyPy进行类型检查
- 编写类型注解

```bash
# 代码格式化
# Code formatting
black app/

# 代码检查
# Code linting
flake8 app/

# 类型检查
# Type checking
mypy app/
```

##### JavaScript/TypeScript代码规范 / JavaScript/TypeScript Code Standards

- 使用ESLint进行代码检查
- 使用Prettier进行代码格式化
- 遵循TypeScript最佳实践
- 编写Jest测试

```bash
# 代码检查
# Code linting
npm run lint

# 代码格式化
# Code formatting
npm run format

# 运行测试
# Run tests
npm test
```

### 3. 测试 / Testing

#### 测试类型 / Test Types

- **单元测试** / Unit Tests: 测试单个函数或组件
- **集成测试** / Integration Tests: 测试多个组件的交互
- **端到端测试** / E2E Tests: 测试完整的用户流程
- **AI服务测试** / AI Service Tests: 测试AI集成功能

#### 运行测试 / Running Tests

```bash
# 后端测试
# Backend tests
cd backend
pytest tests/ -v --cov=app

# 前端测试
# Frontend tests
cd frontend
npm test -- --coverage

# 集成测试
# Integration tests
pytest tests/test_integration.py -v
```

#### 测试覆盖率 / Test Coverage

- 目标覆盖率: 80%+
- 关键模块: 90%+
- 新增代码: 必须包含测试

### 4. 文档贡献 / Documentation Contributions

#### 文档类型 / Documentation Types

- **API文档** / API Documentation
- **用户指南** / User Guides
- **开发文档** / Development Documentation
- **部署指南** / Deployment Guides
- **教程** / Tutorials

#### 文档标准 / Documentation Standards

- 双语支持（中文/英文）
- 清晰的代码示例
- 截图和图表
- 逐步说明

---

## 🔄 提交更改 / Submitting Changes

### 1. 提交信息规范 / Commit Message Standards

遵循[Conventional Commits](https://www.conventionalcommits.org/)规范：

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

类型说明 / Type Descriptions:
- `feat`: 新功能 / New feature
- `fix`: 错误修复 / Bug fix
- `docs`: 文档更新 / Documentation
- `style`: 代码格式 / Code style
- `refactor`: 代码重构 / Code refactoring
- `test`: 测试相关 / Testing
- `chore`: 构建过程 / Build process

示例 / Examples:
```bash
feat: add Chinese cultural context optimization
fix: resolve DeepSeek API connection timeout
docs: update deployment guide with Docker instructions
test: add integration tests for AI services
```

### 2. Pull Request流程 / Pull Request Process

1. **更新您的Fork** / Update Your Fork
   ```bash
   git fetch upstream
   git checkout main
   git merge upstream/main
   ```

2. **推送更改** / Push Changes
   ```bash
   git push origin feature/your-feature-name
   ```

3. **创建Pull Request** / Create Pull Request
   - 使用PR模板
   - 提供清晰的描述
   - 链接相关问题
   - 确保所有测试通过

4. **代码审查** / Code Review
   - 等待维护者审查
   - 根据反馈进行修改
   - 保持PR更新

---

## 🧪 特殊贡献领域 / Special Contribution Areas

### 1. AI模型优化 / AI Model Optimization

- 改进中文内容生成质量
- 优化文化背景理解
- 提升生成速度
- 降低成本

### 2. 中文本地化 / Chinese Localization

- 改进翻译质量
- 添加地域文化特色
- 优化平台特定内容
- 增强用户界面本地化

### 3. 性能优化 / Performance Optimization

- 数据库查询优化
- 缓存策略改进
- API响应时间优化
- 前端加载速度提升

### 4. 安全性增强 / Security Enhancement

- 输入验证和清理
- API安全加固
- 数据加密改进
- 访问控制优化

---

## 🎯 优先贡献领域 / Priority Contribution Areas

### 高优先级 / High Priority
- 错误修复和稳定性改进
- 性能优化
- 安全漏洞修复
- 文档完善

### 中优先级 / Medium Priority
- 新功能开发
- 用户体验改进
- 测试覆盖率提升
- 代码质量改进

### 低优先级 / Low Priority
n- 代码重构
- 依赖更新
- 开发工具改进
- 示例和教程

---

## 📊 贡献指标 / Contribution Metrics

### 代码贡献 / Code Contributions
- 提交频率
- 代码质量
- 测试覆盖率
- 文档完整性

### 非代码贡献 / Non-Code Contributions
- 问题报告质量
- 功能建议价值
- 文档改进
- 社区支持

---

## 🏆 贡献者认可 / Contributor Recognition

### 贡献者类型 / Contributor Types

- **代码贡献者** / Code Contributors
- **文档撰写者** / Documentation Writers
- **测试人员** / Testers
- **设计人员** / Designers
- **翻译人员** / Translators

### 认可方式 / Recognition Methods

- GitHub贡献者列表
- 发布说明中致谢
- 特殊贡献徽章
- 维护者权限（长期贡献者）

---

## 📞 获取帮助 / Getting Help

### 沟通渠道 / Communication Channels

- **GitHub Issues**: 技术问题和错误报告
- **GitHub Discussions**: 功能讨论和问答
- **Email**: 安全和隐私相关问题

### 支持资源 / Support Resources

- [项目文档](README.md)
- [部署指南](PRODUCTION_DEPLOYMENT.md)
- [实现总结](IMPLEMENTATION_SUMMARY.md)
- 系统状态检查工具

---

## ✅ 提交前检查清单 / Pre-Submission Checklist

### 代码质量 / Code Quality
- [ ] 代码遵循项目风格指南
- [ ] 已通过自我代码审查
- [ ] 已添加适当的注释
- [ ] 已更新相关文档
- [ ] 代码不会产生新的警告

### 测试 / Testing
- [ ] 已添加证明修复或功能有效的测试
- [ ] 所有测试在本地通过
- [ ] 测试覆盖率没有下降

### 文档 / Documentation
- [ ] 已更新README（如需要）
- [ ] 已更新API文档（如需要）
- [ ] 已添加代码注释（复杂部分）

### 提交信息 / Commit Messages
- [ ] 提交信息清晰且描述性强
- [ ] 遵循常规提交规范
- [ ] 包含相关的问题引用

---

**再次感谢您的贡献！** 🎉

您的每一行代码、每一个建议、每一次测试都在帮助构建更好的中国AI视频创作平台。让我们一起为中文创作者提供世界一流的AI工具！

**Thank you again for your contribution!** 🎉

Every line of code, every suggestion, and every test helps build a better Chinese AI video creation platform. Let's provide world-class AI tools for Chinese creators together!

---

*本贡献指南会根据项目发展持续更新* / *This contributing guide is continuously updated as the project evolves*