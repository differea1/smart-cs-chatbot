#!/bin/bash
# ============================================
# 极米智能售后助手 - 云服务器一键部署脚本
# ============================================
# 适用: Ubuntu 22.04+ / Debian 12+
# 用法: chmod +x setup.sh && sudo ./setup.sh
# ============================================

set -e

APP_DIR="/opt/xgimi-cs-chatbot"
DOMAIN="${1:-localhost}"
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}"
echo "==========================================="
echo "  极米智能售后助手 - 部署脚本"
echo "==========================================="
echo -e "${NC}"

# 检查是否为 root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}请使用 root 权限运行: sudo ./setup.sh${NC}"
    exit 1
fi

# ---- 1. 安装 Docker ----
echo -e "${YELLOW}[1/6] 安装 Docker...${NC}"
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com | bash
    systemctl enable docker
    systemctl start docker
else
    echo "Docker 已安装，跳过。"
fi

# ---- 2. 安装 Docker Compose ----
echo -e "${YELLOW}[2/6] 安装 Docker Compose...${NC}"
if ! docker compose version &> /dev/null 2>&1; then
    apt-get update -qq && apt-get install -y -qq docker-compose-plugin
fi
echo "Docker Compose 版本: $(docker compose version)"

# ---- 3. 创建应用目录 ----
echo -e "${YELLOW}[3/6] 创建应用目录...${NC}"
mkdir -p "$APP_DIR"
mkdir -p "$APP_DIR/ssl"
mkdir -p "$APP_DIR/certbot/www"

# 如果当前目录有项目文件，复制过去
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

if [ -f "$PROJECT_ROOT/docker-compose.yml" ]; then
    echo "从 $PROJECT_ROOT 复制项目文件..."
    cp -r "$PROJECT_ROOT"/* "$APP_DIR/"
fi

# ---- 4. 配置环境变量 ----
echo -e "${YELLOW}[4/6] 配置环境变量...${NC}"

# 生成 JWT 密钥
if [ ! -f "$APP_DIR/backend/.env.prod" ] || grep -q "change-me" "$APP_DIR/backend/.env.prod" 2>/dev/null; then
    JWT_SECRET=$(python3 -c "import secrets; print(secrets.token_hex(32))" 2>/dev/null || openssl rand -hex 32)
    echo "生成 JWT_SECRET: ${JWT_SECRET:0:16}..."

    if [ -f "$APP_DIR/backend/.env.prod" ]; then
        # 仅替换 JWT_SECRET
        sed -i "s/^JWT_SECRET=.*/JWT_SECRET=$JWT_SECRET/" "$APP_DIR/backend/.env.prod"
    fi
fi

echo "⚠ 请确认已正确配置 backend/.env.prod 中的:"
echo "  - DEEPSEEK_API_KEY (DeepSeek API 密钥)"
echo "  - JWT_SECRET (已自动生成)"
echo "  - CORS_ORIGINS (替换为你的域名)"

# ---- 5. 构建并启动 ----
echo -e "${YELLOW}[5/6] 构建并启动服务...${NC}"
cd "$APP_DIR"

# 先构建前端
if [ -f "$APP_DIR/frontend/package.json" ]; then
    echo "构建前端..."
    cd "$APP_DIR/frontend"
    if command -v npm &> /dev/null; then
        npm install --silent
        npm run build
    else
        echo -e "${RED}未安装 Node.js，跳过前端构建。请手动构建后重试。${NC}"
        echo "安装 Node.js: curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && apt-get install -y nodejs"
    fi
    cd "$APP_DIR"
fi

# 构建并启动容器
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build

# ---- 6. 初始化知识库 ----
echo -e "${YELLOW}[6/6] 初始化知识库数据...${NC}"
sleep 5  # 等待服务启动
docker compose -f docker-compose.yml -f docker-compose.prod.yml exec -T backend python scripts/seed_knowledge.py 2>/dev/null || echo "知识库可能已初始化，跳过。"

# ---- 完成 ----
echo -e "${GREEN}"
echo "==========================================="
echo "  部署完成！"
echo "==========================================="
echo "  访问地址: http://${DOMAIN}"
echo "  管理后台: http://${DOMAIN}/login"
echo "  默认账号: admin / admin123"
echo "  API 文档: http://${DOMAIN}/api/docs"
echo ""
echo "  ⚠ 请立即修改默认管理员密码！"
echo ""
echo "  后续步骤："
echo "  1. 配置 SSL 证书: 将证书放入 $APP_DIR/ssl/"
echo "     - fullchain.pem (证书文件)"
echo "     - privkey.pem (私钥文件)"
echo "  2. 修改 nginx/prod.conf 中的 server_name"
echo "  3. 重新加载: docker compose exec nginx nginx -s reload"
echo ""
echo "  查看日志: cd $APP_DIR && docker compose logs -f"
echo "==========================================="
echo -e "${NC}"
