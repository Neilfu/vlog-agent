#!/bin/bash

# 中国AI智能短视频创作系统 - 项目设置脚本
# Chinese AI Intelligent Short Video Creation System - Project Setup Script

set -e  # Exit on any error

# 颜色定义 / Color definitions
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印函数 / Print functions
print_header() {
    echo -e "${BLUE}================================================${NC}"
    echo -e "${BLUE}  中国AI智能短视频创作系统 - 项目设置${NC}"
    echo -e "${BLUE}  Chinese AI Video Creation System - Setup${NC}"
    echo -e "${BLUE}================================================${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# 检查依赖 / Check dependencies
check_dependencies() {
    print_info "检查系统依赖..."

    # 检查Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker未安装，请先安装Docker"
        exit 1
    fi

    # 检查Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose未安装，请先安装Docker Compose"
        exit 1
    fi

    # 检查Node.js
    if ! command -v node &> /dev/null; then
        print_warning "Node.js未安装，某些功能可能无法使用"
    fi

    # 检查Python
    if ! command -v python3 &> /dev/null; then
        print_warning "Python3未安装，某些功能可能无法使用"
    fi

    print_success "系统依赖检查完成"
}

# 创建必要目录 / Create necessary directories
create_directories() {
    print_info "创建项目目录..."

    directories=(
        "logs/backend"
        "logs/frontend"
        "logs/nginx"
        "uploads"
        "temp"
        "data/postgres"
        "data/redis"
        "data/prometheus"
        "data/grafana"
    )

    for dir in "${directories[@]}"; do
        mkdir -p "$dir"
        print_success "创建目录: $dir"
    done
}

# 设置文件权限 / Set file permissions
set_permissions() {
    print_info "设置文件权限..."

    # 设置脚本执行权限
    chmod +x scripts/*.sh 2>/dev/null || true
    chmod +x check_status.py

    # 设置日志目录权限
    chmod 755 logs/ 2>/dev/null || true
    chmod 755 uploads/ 2>/dev/null || true
    chmod 755 temp/ 2>/dev/null || true

    print_success "文件权限设置完成"
}

# 配置环境变量 / Configure environment variables
configure_environment() {
    print_info "配置环境变量..."

    # 检查是否存在.env文件
    if [ ! -f "backend/.env" ]; then
        if [ -f "backend/.env.example" ]; then
            cp backend/.env.example backend/.env
            print_warning "已创建backend/.env文件，请配置API密钥"
            print_info "需要配置的API密钥:"
            print_info "  - DEEPSEEK_API_KEY: 从deepseek.com获取"
            print_info "  - VOLC_ACCESS_KEY: 从火山引擎获取"
            print_info "  - VOLC_SECRET_KEY: 从火山引擎获取"
        else
            print_error "未找到backend/.env.example文件"
        fi
    else
        print_success "backend/.env文件已存在"
    fi
}

# 安装前端依赖 / Install frontend dependencies
install_frontend_deps() {
    print_info "安装前端依赖..."

    if [ -d "frontend" ]; then
        cd frontend
        if [ -f "package.json" ]; then
            if command -v npm &> /dev/null; then
                npm install
                print_success "前端依赖安装完成"
            else
                print_warning "npm未安装，跳过前端依赖安装"
            fi
        else
            print_warning "未找到frontend/package.json文件"
        fi
        cd ..
    else
        print_warning "未找到frontend目录"
    fi
}

# 安装后端依赖 / Install backend dependencies
install_backend_deps() {
    print_info "安装后端依赖..."

    if [ -d "backend" ]; then
        cd backend
        if [ -f "requirements.txt" ]; then
            if command -v python3 &> /dev/null; then
                # 创建虚拟环境（如果尚未创建）
                if [ ! -d "venv" ]; then
                    python3 -m venv venv
                    print_success "创建Python虚拟环境"
                fi

                # 激活虚拟环境并安装依赖
                source venv/bin/activate
                pip install --upgrade pip
                pip install -r requirements.txt
                print_success "后端依赖安装完成"
                deactivate
            else
                print_warning "python3未安装，跳过后端依赖安装"
            fi
        else
            print_warning "未找到backend/requirements.txt文件"
        fi
        cd ..
    else
        print_warning "未找到backend目录"
    fi
}

# 初始化数据库 / Initialize database
init_database() {
    print_info "初始化数据库..."

    # 这里可以添加数据库初始化脚本
    # 目前使用Docker容器时会自动处理
    print_success "数据库初始化配置完成"
}

# 运行测试 / Run tests
run_tests() {
    print_info "运行测试..."

    # 后端测试
    if [ -d "backend" ] && [ -f "backend/requirements.txt" ]; then
        if command -v python3 &> /dev/null; then
            cd backend
            if [ -d "venv" ]; then
                source venv/bin/activate
                if command -v pytest &> /dev/null; then
                    pytest tests/ -v || print_warning "部分后端测试失败"
                else
                    print_warning "pytest未安装，跳过后端测试"
                fi
                deactivate
            fi
            cd ..
        fi
    fi

    # 前端测试
    if [ -d "frontend" ] && [ -f "frontend/package.json" ]; then
        cd frontend
        if command -v npm &> /dev/null; then
            if npm list jest &> /dev/null; then
                npm test -- --watchAll=false --passWithNoTests || print_warning "部分前端测试失败"
            else
                print_warning "Jest未安装，跳过后端测试"
            fi
        fi
        cd ..
    fi

    print_success "测试运行完成"
}

# 检查系统状态 / Check system status
check_system_status() {
    print_info "检查系统状态..."

    if command -v python3 &> /dev/null; then
        python3 check_status.py
    else
        print_warning "无法运行状态检查脚本（python3未安装）"
    fi
}

# 显示后续步骤 / Show next steps
show_next_steps() {
    print_info "设置完成！请按照以下步骤继续："
    echo ""
    echo "1. 🔑 配置API密钥："
    echo "   - 编辑 backend/.env 文件"
    echo "   - 添加 DEEPSEEK_API_KEY（从deepseek.com获取）"
    echo "   - 添加 VOLC_ACCESS_KEY 和 VOLC_SECRET_KEY（从火山引擎获取）"
    echo ""
    echo "2. 🐳 启动服务（使用Docker）："
    echo "   docker-compose up -d"
    echo ""
    echo "3. 🧪 验证服务："
    echo "   - 前端: http://localhost:3000"
    echo "   - 后端API: http://localhost:8000/docs"
    echo "   - 健康检查: http://localhost:8000/health"
    echo ""
    echo "4. 📚 查看文档："
    echo "   - README.md: 项目概览"
    echo "   - PRODUCTION_DEPLOYMENT.md: 生产部署指南"
    echo "   - IMPLEMENTATION_SUMMARY.md: 实现总结"
    echo ""
    echo "5. 🔍 故障排除："
    echo "   - 运行: python3 check_status.py"
    echo "   - 查看日志: docker-compose logs -f"
    echo "   - 检查GitHub Issues获取帮助"
    echo ""
    echo "🎉 享受使用中国AI智能短视频创作系统！"
    echo "Enjoy using the Chinese AI Video Creation System!"
}

# 主函数 / Main function
main() {
    print_header

    # 检查依赖
    check_dependencies

    # 创建目录
    create_directories

    # 设置权限
    set_permissions

    # 配置环境
    configure_environment

    # 安装依赖（可选）
    if [ "$1" == "--install-deps" ] || [ "$1" == "-d" ]; then
        install_frontend_deps
        install_backend_deps
    fi

    # 初始化数据库
    init_database

    # 运行测试（可选）
    if [ "$1" == "--run-tests" ] || [ "$1" == "-t" ]; then
        run_tests
    fi

    # 检查系统状态
    check_system_status

    # 显示后续步骤
    show_next_steps
}

# 显示帮助信息 / Show help
show_help() {
    echo "使用方法 / Usage:"
    echo "  $0 [选项]"
    echo ""
    echo "选项 / Options:"
    echo "  --install-deps, -d    安装项目依赖 / Install project dependencies"
    echo "  --run-tests, -t       运行测试套件 / Run test suite"
    echo "  --help, -h           显示帮助信息 / Show help information"
    echo ""
    echo "示例 / Examples:"
    echo "  $0                   # 基本设置"
    echo "  $0 --install-deps    # 安装依赖并设置"
    echo "  $0 --run-tests       # 运行测试"
}

# 处理命令行参数 / Handle command line arguments
case "$1" in
    --help|-h)
        show_help
        exit 0
        ;;
    --install-deps|-d|--run-tests|-t|"")
        main "$@"
        ;;
    *)
        print_error "未知选项: $1"
        show_help
        exit 1
        ;;
esac

exit 0