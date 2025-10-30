#!/bin/bash

# 中国AI短视频创作系统 - Strapi CMS 部署脚本
# Chinese AI Video Creation System - Strapi CMS Deployment Script

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查Docker环境
check_docker() {
    log_info "检查Docker环境..."

    if ! command -v docker &> /dev/null; then
        log_error "Docker未安装，请先安装Docker"
        exit 1
    fi

    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose未安装，请先安装Docker Compose"
        exit 1
    fi

    # 检查Docker服务状态
    if ! docker info &> /dev/null; then
        log_error "Docker服务未运行，请先启动Docker服务"
        exit 1
    fi

    log_success "Docker环境检查通过"
}

# 检查环境变量
check_env() {
    log_info "检查环境变量配置..."

    if [ ! -f ".env" ]; then
        log_warning "未找到.env文件，将使用默认配置"

        # 创建默认的.env文件
        cat > .env << EOF
# 数据库配置
DATABASE_PASSWORD=strapi_secure_password_123

# JWT密钥 - 请更改为安全的随机字符串
JWT_SECRET=your-secure-jwt-secret-key-change-this-in-production
ADMIN_JWT_SECRET=your-secure-admin-jwt-secret-key-change-this-in-production

# 应用密钥
APP_KEYS=app-key-1,app-key-2,app-key-3,app-key-4

# API Token盐值
API_TOKEN_SALT=your-api-token-salt-change-this-in-production
TRANSFER_TOKEN_SALT=your-transfer-token-salt-change-this-in-production

# Webhook密钥
WEBHOOK_SECRET=your-webhook-secret-change-this-in-production

# 后端服务URL
STRAPI_BACKEND_URL=http://backend:8000

# 环境模式
NODE_ENV=production

# 国际化配置
STRAPI_DEFAULT_LOCALE=zh-CN
STRAPI_SUPPORTED_LOCALES=zh-CN,en-US
EOF
        log_info "已创建默认的.env文件，请根据实际需求修改配置"
    fi

    log_success "环境变量检查完成"
}

# 创建必要的目录
create_directories() {
    log_info "创建必要的目录结构..."

    # 创建SSL证书目录（如果不存在）
    mkdir -p ssl
    mkdir -p logs
    mkdir -p backups
    mkdir -p uploads

    log_success "目录创建完成"
}

# 生成SSL证书（开发环境）
generate_ssl_cert() {
    log_info "检查SSL证书..."

    if [ ! -f "ssl/cert.pem" ] || [ ! -f "ssl/key.pem" ]; then
        log_warning "SSL证书不存在，生成自签名证书（仅用于开发环境）"

        openssl req -x509 -newkey rsa:4096 -keyout ssl/key.pem -out ssl/cert.pem -days 365 -nodes \
            -subj "/C=CN/ST=Beijing/L=Beijing/O=Chinese AI Video System/CN=localhost" 2>/dev/null || {
            log_warning "OpenSSL未安装，跳过SSL证书生成（将使用HTTP）"
            return 0
        }

        log_success "SSL证书生成完成"
    else
        log_success "SSL证书已存在"
    fi
}

# 构建Docker镜像
build_images() {
    log_info "构建Docker镜像..."

    docker-compose build --no-cache

    log_success "Docker镜像构建完成"
}

# 启动服务
start_services() {
    log_info "启动Strapi服务..."

    # 停止现有服务
    docker-compose down || true

    # 启动服务
    docker-compose up -d

    log_success "服务启动命令已发送"
}

# 等待服务就绪
wait_for_services() {
    log_info "等待服务就绪..."

    # 等待PostgreSQL
    log_info "等待PostgreSQL数据库就绪..."
    timeout=60
    while ! docker-compose exec -T postgres pg_isready -U strapi -d strapi_cms &>/dev/null; do
        sleep 2
        timeout=$((timeout - 2))
        if [ $timeout -le 0 ]; then
            log_error "PostgreSQL服务启动超时"
            exit 1
        fi
    done
    log_success "PostgreSQL数据库已就绪"

    # 等待Strapi
    log_info "等待Strapi服务就绪..."
    timeout=120
    while ! curl -f http://localhost:1337/_health &>/dev/null; do
        sleep 5
        timeout=$((timeout - 5))
        if [ $timeout -le 0 ]; then
            log_error "Strapi服务启动超时"
            exit 1
        fi
    done
    log_success "Strapi服务已就绪"
}

# 创建管理员用户
create_admin_user() {
    log_info "创建管理员用户..."

    # 检查是否已存在管理员用户
    if docker-compose exec -T strapi npm run strapi admin:find-user &>/dev/null; then
        log_info "管理员用户已存在，跳过创建"
    else
        log_info "请设置管理员用户信息："
        read -p "管理员邮箱: " admin_email
        read -p "管理员用户名: " admin_username
        read -sp "管理员密码: " admin_password
        echo

        docker-compose exec -T strapi npm run strapi admin:create-user -- \
            --email="$admin_email" \
            --username="$admin_username" \
            --password="$admin_password" \
            --firstname="Admin" \
            --lastname="User"

        log_success "管理员用户创建完成"
    fi
}

# 显示服务状态
show_status() {
    log_info "服务状态信息："
    echo
    echo "========================================="
    echo "🚀 Strapi CMS 服务已启动"
    echo "========================================="
    echo
    echo "📊 服务访问地址："
    echo "  • Strapi 管理后台: https://localhost:8443/admin"
    echo "  • Strapi API 文档: https://localhost:8443/documentation"
    echo "  • PostgreSQL 数据库: localhost:5433"
    echo "  • Redis 缓存: localhost:6380"
    echo
    echo "📁 数据存储位置："
    echo "  • 上传文件: ./uploads"
    echo "  • 数据库数据: postgres_data (Docker卷)"
    echo "  • 缓存数据: redis_data (Docker卷)"
    echo
    echo "📋 管理命令："
    echo "  • 查看日志: docker-compose logs -f"
    echo "  • 停止服务: docker-compose down"
    echo "  • 重启服务: docker-compose restart"
    echo "  • 备份数据: ./backup.sh"
    echo
    echo "🔒 安全提示："
    echo "  • 请及时修改默认密码"
    echo "  • 生产环境请使用有效的SSL证书"
    echo "  • 定期备份数据库和上传文件"
    echo
    echo "========================================="
}

# 主部署流程
main() {
    log_info "开始部署Strapi CMS服务..."
    echo

    # 检查前提条件
    check_docker
    check_env
    create_directories
    generate_ssl_cert

    # 构建和启动
    build_images
    start_services
    wait_for_services
    create_admin_user

    # 显示结果
    show_status

    log_success "Strapi CMS部署完成！"
}

# 错误处理
trap 'log_error "部署过程中发生错误"; exit 1' ERR

# 运行主函数
main "$@" || {
    log_error "部署失败，请检查错误信息"
    exit 1
}

# 备份函数（可选）
backup_data() {
    log_info "创建数据备份..."

    backup_dir="backups/$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$backup_dir"

    # 备份数据库
    docker-compose exec -T postgres pg_dump -U strapi strapi_cms > "$backup_dir/database.sql"

    # 备份上传文件
    cp -r uploads "$backup_dir/" 2>/dev/null || true

    # 备份配置文件
    cp -r config "$backup_dir/" 2>/dev/null || true

    log_success "数据备份完成: $backup_dir"
}

# 如果脚本带--backup参数，执行备份
if [[ "$1" == "--backup" ]]; then
    backup_data
    exit 0
fi