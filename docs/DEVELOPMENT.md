# 开发指南 / Development Guide

## 🎯 概述 / Overview

本指南为开发者提供中国AI智能短视频创作系统的完整开发环境设置、代码贡献流程和最佳实践。

This guide provides developers with complete development environment setup, code contribution processes, and best practices for the Chinese AI Intelligent Short Video Creation System.

---

## 🚀 快速开始 / Quick Start

### 1. 克隆仓库 / Clone Repository

```bash
git clone https://github.com/your-repo/chinese-ai-video-system.git
cd chinese-ai-video-system
```

### 2. 运行设置脚本 / Run Setup Script

```bash
# 基本设置
./setup.sh

# 完整设置（包含依赖安装和测试）
./setup.sh --install-deps --run-tests
```

### 3. 配置环境变量 / Configure Environment Variables

```bash
# 复制环境模板
cp backend/.env.example backend/.env

# 编辑环境变量
nano backend/.env
```

### 4. 启动服务 / Start Services

```bash
# 使用Docker Compose
docker-compose up -d

# 或手动启动（见下文详细步骤）
```

---

## 🛠️ 开发环境设置 / Development Environment Setup

### 系统要求 / System Requirements

- **操作系统**: Linux/macOS/Windows
- **Python**: 3.8+
- **Node.js**: 16+
- **Docker**: 20+
- **PostgreSQL**: 13+ (可选，开发可用SQLite)
- **Redis**: 6+ (可选，开发可用内存存储)

### 后端开发环境 / Backend Development Environment

#### Python环境设置 / Python Environment Setup

```bash
# 进入后端目录
cd backend

# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate  # Windows

# 升级pip
pip install --upgrade pip

# 安装依赖
pip install -r requirements.txt

# 安装开发依赖
pip install -r requirements-dev.txt
```

#### 数据库设置 / Database Setup

```bash
# SQLite（开发用）
# 无需额外设置，会自动创建数据库文件

# PostgreSQL（推荐用于生产环境测试）
createdb chinese_ai_video_dev

# 更新环境变量
echo "DATABASE_URL=postgresql://username:password@localhost:5432/chinese_ai_video_dev" >> .env
```

#### Redis设置 / Redis Setup

```bash
# 安装Redis（macOS）
brew install redis
brew services start redis

# 安装Redis（Ubuntu/Debian）
sudo apt-get install redis-server
sudo systemctl start redis-server

# 更新环境变量
echo "REDIS_URL=redis://localhost:6379/0" >> .env
```

#### 启动后端服务 / Start Backend Service

```bash
# 开发模式（带热重载）
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 生产模式
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

# 或使用Gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### 前端开发环境 / Frontend Development Environment

#### Node.js环境设置 / Node.js Environment Setup

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 或使用Yarn
yarn install
```

#### 启动前端服务 / Start Frontend Service

```bash
# 开发模式（带热重载）
npm start

# 构建生产版本
npm run build

# 运行测试
npm test

# 运行测试（带覆盖率）
npm run test:coverage
```

---

## 🧪 测试 / Testing

### 测试策略 / Testing Strategy

#### 测试类型 / Test Types

1. **单元测试** / Unit Tests
   - 测试单个函数或组件
   - 快速执行
   - 高覆盖率要求

2. **集成测试** / Integration Tests
   - 测试多个组件的交互
   - 测试数据库操作
   - 测试API端点

3. **端到端测试** / End-to-End Tests
   - 测试完整的用户流程
   - 模拟真实用户操作
   - 验证系统整体功能

4. **AI服务测试** / AI Service Tests
   - 测试AI集成功能
   - 验证中文内容处理
   - 测试成本估算

### 后端测试 / Backend Testing

#### 运行测试 / Run Tests

```bash
# 运行所有测试
cd backend
pytest tests/ -v

# 运行特定测试文件
pytest tests/test_api_projects.py -v

# 运行测试并生成覆盖率报告
pytest tests/ --cov=app --cov-report=html --cov-report=term

# 运行测试并显示详细输出
pytest tests/ -v -s
```

#### 测试覆盖率 / Test Coverage

```bash
# 生成覆盖率报告
pytest tests/ --cov=app --cov-report=html

# 查看覆盖率报告
open htmlcov/index.html

# 覆盖率目标：80%+
```

### 前端测试 / Frontend Testing

#### 运行测试 / Run Tests

```bash
# 运行所有测试
cd frontend
npm test

# 运行测试并生成覆盖率报告
npm run test:coverage

# 运行特定测试文件
npm test -- --testPathPattern=Projects.test.tsx
```

#### 测试工具 / Testing Tools

- **Jest**: 测试框架
- **React Testing Library**: 组件测试
- **Cypress**: 端到端测试
- **MSW**: API模拟

---

## 📝 代码质量 / Code Quality

### 代码规范 / Code Standards

#### Python代码规范 / Python Code Standards

- **PEP 8**: 官方Python风格指南
- **Black**: 代码格式化
- **Flake8**: 代码检查
- **MyPy**: 类型检查

```bash
# 代码格式化
black app/

# 代码检查
flake8 app/

# 类型检查
mypy app/

# 运行所有检查
pre-commit run --all-files
```

#### JavaScript/TypeScript代码规范 / JavaScript/TypeScript Code Standards

- **ESLint**: 代码检查
- **Prettier**: 代码格式化
- **TypeScript**: 类型检查

```bash
# 代码检查
npm run lint

# 代码格式化
npm run format

# 类型检查
npm run type-check
```

### 预提交钩子 / Pre-commit Hooks

```bash
# 安装预提交钩子
pip install pre-commit
pre-commit install

# 手动运行预提交检查
pre-commit run --all-files
```

---

## 🔧 开发工具 / Development Tools

### API开发工具 / API Development Tools

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Postman**: 导入API集合

### 数据库工具 / Database Tools

- **pgAdmin**: PostgreSQL管理
- **Redis Commander**: Redis管理
- **DBeaver**: 通用数据库工具

### 监控工具 / Monitoring Tools

- **Prometheus**: 指标收集
- **Grafana**: 仪表板
- **Jaeger**: 分布式追踪

---

## 🐳 Docker开发 / Docker Development

### 开发容器 / Development Containers

```bash
# 启动开发环境
docker-compose up -d

# 查看日志
docker-compose logs -f

# 重建容器
docker-compose up --build

# 进入容器
docker-compose exec backend bash
docker-compose exec frontend bash
```

### 调试容器 / Debugging Containers

```bash
# 查看容器状态
docker-compose ps

# 查看容器日志
docker-compose logs backend
docker-compose logs frontend

# 进入容器调试
docker-compose exec backend python -m pdb app/main.py
```

---

## 🔄 开发工作流 / Development Workflow

### 分支策略 / Branch Strategy

- **main**: 生产分支
- **develop**: 开发分支
- **feature/***: 功能分支
- **bugfix/***: 错误修复分支
- **hotfix/***: 紧急修复分支

### 提交规范 / Commit Convention

遵循[Conventional Commits](https://www.conventionalcommits.org/)规范：

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

类型说明：
- `feat`: 新功能
- `fix`: 错误修复
- `docs`: 文档更新
- `style`: 代码格式
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建过程

### Pull Request流程 / Pull Request Process

1. **创建功能分支**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **开发和测试**
   ```bash
   # 开发代码
   # 运行测试
   pytest tests/
   npm test
   ```

3. **提交更改**
   ```bash
   git add .
   git commit -m "feat: add new feature"
   ```

4. **推送分支**
   ```bash
   git push origin feature/your-feature-name
   ```

5. **创建Pull Request**
   - 使用PR模板
   - 提供清晰的描述
   - 确保所有测试通过

---

## 📊 性能优化 / Performance Optimization

### 后端优化 / Backend Optimization

#### 数据库优化
```python
# 使用连接池
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=30

# 添加索引
CREATE INDEX idx_projects_status ON projects(status);
CREATE INDEX idx_projects_creator_id ON projects(creator_id);
```

#### 缓存策略
```python
# Redis缓存
from app.core.cache import cache

@cache.cached(timeout=300)
def get_project(project_id: str):
    return db.query(Project).filter(Project.id == project_id).first()
```

#### 异步处理
```python
# 使用Celery进行异步处理
from celery import Celery

@app.task
def generate_video_async(project_id: str):
    # 异步视频生成逻辑
    pass
```

### 前端优化 / Frontend Optimization

#### 代码分割
```typescript
// 路由级别的代码分割
const Projects = lazy(() => import('./pages/Projects'));
const Dashboard = lazy(() => import('./pages/Dashboard'));
```

#### 图片优化
```typescript
// 使用WebP格式
import { Picture } from 'react-optimized-image';

<Picture src="image.jpg" webp />
```

#### 状态管理优化
```typescript
// 使用React Query进行数据缓存
const { data, isLoading, error } = useQuery(
  ['projects', page],
  () => fetchProjects(page),
  {
    staleTime: 5 * 60 * 1000, // 5分钟
    cacheTime: 10 * 60 * 1000, // 10分钟
  }
);
```

---

## 🔍 调试技巧 / Debugging Tips

### 后端调试 / Backend Debugging

#### 日志记录
```python
import logging
from loguru import logger

# 使用结构化的日志记录
logger.info("Processing project", project_id=project_id, user_id=user_id)

# 调试日志
logger.debug(f"AI response: {ai_response}")
```

#### 调试器使用
```python
# 使用pdb进行调试
import pdb; pdb.set_trace()

# 使用ipdb（更好的调试器）
import ipdb; ipdb.set_trace()
```

#### API调试
```bash
# 使用curl调试API
curl -X POST http://localhost:8000/api/v1/ai/generate-concept \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"prompt": "测试提示"}'
```

### 前端调试 / Frontend Debugging

#### React DevTools
```bash
# 安装React DevTools
npm install -g react-devtools

# 启动DevTools
react-devtools
```

#### Chrome DevTools
- 使用React Developer Tools扩展
- 使用Redux DevTools（如果使用Redux）
- Network面板查看API调用
- Console面板查看错误信息

#### React Query DevTools
```typescript
import { ReactQueryDevtools } from 'react-query/devtools'

function App() {
  return (
    <>
      {/* Your app */}
      <ReactQueryDevtools initialIsOpen={false} />
    </>
  )
}
```

---

## 🚨 故障排除 / Troubleshooting

### 常见问题 / Common Issues

#### 数据库连接失败
```bash
# 检查PostgreSQL状态
sudo systemctl status postgresql

# 检查连接字符串
grep DATABASE_URL backend/.env

# 测试连接
psql $DATABASE_URL -c "SELECT 1"
```

#### Redis连接失败
```bash
# 检查Redis状态
redis-cli ping

# 检查Redis日志
sudo tail -f /var/log/redis/redis-server.log
```

#### 前端构建失败
```bash
# 清除缓存
rm -rf node_modules package-lock.json
npm install

# 检查TypeScript错误
npm run type-check

# 检查ESLint错误
npm run lint
```

#### API调用失败
```bash
# 检查后端服务状态
curl http://localhost:8000/health

# 检查环境变量
printenv | grep API

# 检查日志
tail -f backend/logs/app.log
```

### 性能问题 / Performance Issues

#### 慢查询分析
```python
# 启用SQL查询日志
import logging
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

# 使用EXPLAIN ANALYZE
EXPLAIN ANALYZE SELECT * FROM projects WHERE status = 'draft';
```

#### 内存泄漏检测
```python
# 使用tracemalloc
import tracemalloc
tracemalloc.start()

# Your code here

current, peak = tracemalloc.get_traced_memory()
print(f"Current memory usage: {current / 1024 / 1024:.1f} MB")
print(f"Peak memory usage: {peak / 1024 / 1024:.1f} MB")
```

---

## 📚 学习资源 / Learning Resources

### 推荐教程 / Recommended Tutorials

- [FastAPI官方文档](https://fastapi.tiangolo.com/)
- [React官方文档](https://reactjs.org/)
- [TypeScript官方文档](https://www.typescriptlang.org/)
- [Docker官方文档](https://docs.docker.com/)

### 相关技术 / Related Technologies

- [SQLAlchemy文档](https://docs.sqlalchemy.org/)
- [React Query文档](https://react-query.tanstack.com/)
- [Tailwind CSS文档](https://tailwindcss.com/docs)
- [Pydantic文档](https://pydantic-docs.helpmanual.io/)

### AI/ML资源 / AI/ML Resources

- [DeepSeek API文档](https://platform.deepseek.com/docs)
- [火山引擎文档](https://www.volcengine.com/docs)
- [AutoGen文档](https://microsoft.github.io/autogen/)

---

## 🤝 贡献指南 / Contribution Guidelines

### 代码风格 / Code Style

- 遵循PEP 8（Python）
- 遵循TypeScript/React最佳实践
- 编写清晰的注释
- 使用有意义的变量名

### 提交规范 / Commit Standards

- 使用常规提交格式
- 编写清晰的提交信息
- 关联相关问题
- 保持提交原子性

### 文档标准 / Documentation Standards

- 双语支持（中文/英文）
- 提供代码示例
- 包含截图和图表
- 保持文档更新

---

## 📞 获取帮助 / Getting Help

### 社区资源 / Community Resources

- [GitHub Issues](https://github.com/your-repo/issues) - 报告问题和功能请求
- [GitHub Discussions](https://github.com/your-repo/discussions) - 讨论和问答
- [Discord Server](https://discord.gg/your-server) - 实时聊天和支持

### 联系信息 / Contact Information

- **技术支持**: tech-support@chinese-ai-video.com
- **开发讨论**: dev@chinese-ai-video.com
- **安全问题**: security@chinese-ai-video.com

---

## 🔄 持续更新 / Continuous Updates

本开发指南会根据项目发展持续更新。建议定期查看最新版本。

This development guide is continuously updated as the project evolves. Please check regularly for the latest version.

---

**祝您开发愉快！** 🎉

**Happy coding!** 🎉

---

*最后更新: 2024年10月13日* / *Last updated: October 13, 2024*