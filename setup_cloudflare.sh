#!/bin/bash

# Cloudflare Workers 自动化部署脚本
# 使用 Wrangler CLI 完成部署

set -e  # 遇到错误立即退出

echo "================================================"
echo "  Cloudflare Workers 自动化部署工具"
echo "================================================"
echo ""

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 检查是否安装了 Node.js
check_nodejs() {
    if ! command -v node &> /dev/null; then
        echo -e "${RED}未检测到 Node.js${NC}"
        echo "请先安装 Node.js: https://nodejs.org"
        exit 1
    fi
    echo -e "${GREEN}✓ Node.js 已安装: $(node --version)${NC}"
}

# 检查是否安装了 Wrangler
check_wrangler() {
    if ! command -v wrangler &> /dev/null; then
        echo -e "${YELLOW}未检测到 Wrangler CLI${NC}"
        echo ""
        read -p "是否安装 Wrangler? (y/N): " -n 1 -r
        echo

        if [[ $REPLY =~ ^[Yy]$ ]]; then
            echo -e "${BLUE}安装 Wrangler...${NC}"
            npm install -g wrangler

            if [ $? -eq 0 ]; then
                echo -e "${GREEN}✓ Wrangler 安装成功${NC}"
            else
                echo -e "${RED}✗ Wrangler 安装失败${NC}"
                exit 1
            fi
        else
            echo "已取消"
            exit 1
        fi
    else
        echo -e "${GREEN}✓ Wrangler 已安装: $(wrangler --version)${NC}"
    fi
}

# 登录 Cloudflare
login_cloudflare() {
    echo ""
    echo "================================================"
    echo "  登录 Cloudflare"
    echo "================================================"
    echo ""

    echo -e "${BLUE}检查登录状态...${NC}"

    if wrangler whoami &> /dev/null; then
        echo -e "${GREEN}✓ 已登录 Cloudflare${NC}"
        wrangler whoami
    else
        echo -e "${YELLOW}未登录，开始登录流程...${NC}"
        echo "这会在浏览器中打开授权页面"
        echo ""

        wrangler login

        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✓ 登录成功${NC}"
        else
            echo -e "${RED}✗ 登录失败${NC}"
            exit 1
        fi
    fi
}

# 配置 wrangler.toml
configure_wrangler() {
    echo ""
    echo "================================================"
    echo "  配置 Wrangler"
    echo "================================================"
    echo ""

    # 读取配置
    read -p "Worker 名称 (默认: html2md-api): " WORKER_NAME
    WORKER_NAME=${WORKER_NAME:-html2md-api}

    read -p "是否配置自定义域名? (y/N): " -n 1 -r
    echo

    CUSTOM_DOMAIN=""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        read -p "域名 (例如: api.yourdomain.com): " CUSTOM_DOMAIN
    fi

    # 生成 wrangler.toml
    echo -e "${BLUE}生成 wrangler.toml...${NC}"

    cat > wrangler.toml << EOF
# Cloudflare Workers 配置文件
name = "${WORKER_NAME}"
main = "api_service.py"
compatibility_date = "2024-01-01"

# Python Workers (需要 Workers Paid Plan)
# 注意: Cloudflare Workers 的 Python 支持目前处于 Beta 阶段

[build]
command = ""

# 环境变量（非敏感信息）
[vars]
SUPABASE_BUCKET = "markdown-files"

EOF

    if [ -n "$CUSTOM_DOMAIN" ]; then
        cat >> wrangler.toml << EOF
# 自定义域名
routes = [
  { pattern = "${CUSTOM_DOMAIN}/*" }
]

EOF
    fi

    echo -e "${GREEN}✓ wrangler.toml 已生成${NC}"
}

# 配置环境变量（Secrets）
configure_secrets() {
    echo ""
    echo "================================================"
    echo "  配置环境变量 (Secrets)"
    echo "================================================"
    echo ""

    echo -e "${YELLOW}重要: 敏感信息应该使用 secrets 而不是环境变量${NC}"
    echo ""

    if [ -f ".env" ]; then
        echo "检测到 .env 文件，是否从中读取配置?"
        read -p "使用 .env 配置? (y/N): " -n 1 -r
        echo

        if [[ $REPLY =~ ^[Yy]$ ]]; then
            # 从 .env 读取
            export $(cat .env | grep -v '^#' | xargs)
        fi
    fi

    # 配置 SUPABASE_URL
    if [ -n "$SUPABASE_URL" ]; then
        echo -e "${BLUE}配置 SUPABASE_URL...${NC}"
        echo "$SUPABASE_URL" | wrangler secret put SUPABASE_URL
    else
        read -p "请输入 SUPABASE_URL: " SUPABASE_URL
        echo "$SUPABASE_URL" | wrangler secret put SUPABASE_URL
    fi

    # 配置 SUPABASE_KEY
    if [ -n "$SUPABASE_KEY" ]; then
        echo -e "${BLUE}配置 SUPABASE_KEY...${NC}"
        echo "$SUPABASE_KEY" | wrangler secret put SUPABASE_KEY
    else
        read -p "请输入 SUPABASE_KEY: " SUPABASE_KEY
        echo "$SUPABASE_KEY" | wrangler secret put SUPABASE_KEY
    fi

    echo -e "${GREEN}✓ Secrets 配置完成${NC}"
}

# 部署警告
deployment_warning() {
    echo ""
    echo "================================================"
    echo -e "${YELLOW}⚠  重要提醒${NC}"
    echo "================================================"
    echo ""
    echo "Cloudflare Workers 的 Python 支持注意事项:"
    echo ""
    echo "1. ${YELLOW}需要付费计划${NC}"
    echo "   - Python Workers 需要 Workers Paid Plan"
    echo "   - 每月约 \$5 起"
    echo ""
    echo "2. ${YELLOW}CPU 时间限制${NC}"
    echo "   - 免费版: 10ms"
    echo "   - 付费版: 50ms"
    echo "   - HTML 转换可能超时"
    echo ""
    echo "3. ${YELLOW}替代方案${NC}"
    echo "   - Railway (推荐): 免费额度，完整 Python 支持"
    echo "   - Render: 免费额度，简单部署"
    echo "   - Vercel: Serverless Functions"
    echo ""
    read -p "是否继续部署到 Cloudflare? (y/N): " -n 1 -r
    echo

    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo ""
        echo -e "${BLUE}建议使用 Railway 部署${NC}"
        echo "运行: cat DEPLOYMENT.md | grep -A 20 'Railway'"
        exit 0
    fi
}

# 部署到 Cloudflare Workers
deploy_worker() {
    echo ""
    echo "================================================"
    echo "  部署 Worker"
    echo "================================================"
    echo ""

    echo -e "${BLUE}开始部署...${NC}"
    echo ""

    wrangler deploy

    if [ $? -eq 0 ]; then
        echo ""
        echo -e "${GREEN}✓ 部署成功！${NC}"
        echo ""
        echo "Worker URL:"
        wrangler deployments list | head -5
    else
        echo -e "${RED}✗ 部署失败${NC}"
        echo ""
        echo "可能的原因:"
        echo "  1. Python Workers 需要付费计划"
        echo "  2. 配置文件错误"
        echo "  3. 网络问题"
        echo ""
        echo "建议: 使用 Railway 部署（免费且支持完整 Python）"
        exit 1
    fi
}

# 显示部署信息
show_deployment_info() {
    echo ""
    echo "================================================"
    echo "  部署信息"
    echo "================================================"
    echo ""

    # 获取 Worker URL
    WORKER_URL=$(wrangler deployments list --json 2>/dev/null | grep -o '"url":"[^"]*"' | head -1 | cut -d'"' -f4)

    if [ -n "$WORKER_URL" ]; then
        echo "Worker URL: ${WORKER_URL}"
        echo "API 文档: ${WORKER_URL}/docs"
        echo "健康检查: ${WORKER_URL}/health"
    fi

    echo ""
    echo "管理命令:"
    echo "  查看日志: wrangler tail"
    echo "  查看部署: wrangler deployments list"
    echo "  删除 Worker: wrangler delete"
    echo "  更新 Secret: wrangler secret put <KEY>"
    echo ""
}

# 主流程
main() {
    echo "开始配置 Cloudflare Workers..."
    echo ""

    # 1. 检查依赖
    check_nodejs
    check_wrangler

    # 2. 登录
    login_cloudflare

    # 3. 配置
    configure_wrangler

    # 4. 显示警告
    deployment_warning

    # 5. 配置 Secrets
    configure_secrets

    # 6. 部署
    deploy_worker

    # 7. 显示信息
    show_deployment_info

    echo ""
    echo "================================================"
    echo -e "${GREEN}✓ Cloudflare Workers 配置完成！${NC}"
    echo "================================================"
    echo ""
}

# 运行主流程
main
