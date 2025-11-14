#!/bin/bash

# Railway 自动化部署脚本
# 使用 Railway CLI 快速部署

set -e

echo "================================================"
echo "  Railway 自动化部署工具"
echo "================================================"
echo ""

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# 检查 Railway CLI
check_railway_cli() {
    if ! command -v railway &> /dev/null; then
        echo -e "${YELLOW}未检测到 Railway CLI${NC}"
        echo ""
        echo "安装 Railway CLI:"
        echo ""

        if [[ "$OSTYPE" == "darwin"* ]]; then
            # macOS
            echo "  brew install railway"
        else
            # Linux/Other
            echo "  bash <(curl -fsSL cli.new)"
        fi

        echo ""
        read -p "是否现在安装? (y/N): " -n 1 -r
        echo

        if [[ $REPLY =~ ^[Yy]$ ]]; then
            if [[ "$OSTYPE" == "darwin"* ]]; then
                brew install railway
            else
                bash <(curl -fsSL cli.new)
            fi
        else
            echo "已取消"
            exit 1
        fi
    else
        echo -e "${GREEN}✓ Railway CLI 已安装${NC}"
    fi
}

# 登录 Railway
login_railway() {
    echo ""
    echo -e "${BLUE}登录 Railway...${NC}"
    echo "这会在浏览器中打开授权页面"
    echo ""

    railway login

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ 登录成功${NC}"
    else
        echo -e "${RED}✗ 登录失败${NC}"
        exit 1
    fi
}

# 初始化项目
init_project() {
    echo ""
    echo "================================================"
    echo "  初始化项目"
    echo "================================================"
    echo ""

    echo "请选择:"
    echo "  1) 创建新项目"
    echo "  2) 链接到现有项目"
    echo ""
    read -p "选择 [1-2]: " choice

    case $choice in
        1)
            echo -e "${BLUE}创建新项目...${NC}"
            railway init

            if [ $? -eq 0 ]; then
                echo -e "${GREEN}✓ 项目创建成功${NC}"
            else
                echo -e "${RED}✗ 项目创建失败${NC}"
                exit 1
            fi
            ;;
        2)
            echo -e "${BLUE}链接到现有项目...${NC}"
            railway link

            if [ $? -eq 0 ]; then
                echo -e "${GREEN}✓ 项目链接成功${NC}"
            else
                echo -e "${RED}✗ 项目链接失败${NC}"
                exit 1
            fi
            ;;
        *)
            echo -e "${RED}无效选择${NC}"
            exit 1
            ;;
    esac
}

# 配置环境变量
configure_env_vars() {
    echo ""
    echo "================================================"
    echo "  配置环境变量"
    echo "================================================"
    echo ""

    # 检查是否有 .env 文件
    if [ -f ".env" ]; then
        echo "检测到 .env 文件"
        echo ""
        cat .env
        echo ""
        read -p "是否使用此配置? (y/N): " -n 1 -r
        echo

        if [[ $REPLY =~ ^[Yy]$ ]]; then
            echo -e "${BLUE}上传环境变量到 Railway...${NC}"

            # 读取 .env 并设置到 Railway
            while IFS='=' read -r key value; do
                # 跳过注释和空行
                if [[ ! $key =~ ^# && -n $key ]]; then
                    # 移除值两端的引号
                    value=$(echo "$value" | sed 's/^"\(.*\)"$/\1/' | sed "s/^'\(.*\)'$/\1/")

                    echo "  设置: $key"
                    railway variables set "$key=$value"
                fi
            done < .env

            echo -e "${GREEN}✓ 环境变量配置完成${NC}"
        fi
    else
        echo -e "${YELLOW}未找到 .env 文件${NC}"
        echo ""
        echo "请手动配置环境变量:"
        echo ""

        read -p "SUPABASE_URL: " SUPABASE_URL
        read -p "SUPABASE_KEY: " SUPABASE_KEY

        railway variables set "SUPABASE_URL=$SUPABASE_URL"
        railway variables set "SUPABASE_KEY=$SUPABASE_KEY"
        railway variables set "SUPABASE_BUCKET=markdown-files"

        echo -e "${GREEN}✓ 环境变量配置完成${NC}"
    fi
}

# 创建 Procfile（如果不存在）
create_procfile() {
    if [ ! -f "Procfile" ]; then
        echo ""
        echo -e "${BLUE}创建 Procfile...${NC}"

        cat > Procfile << 'EOF'
web: uvicorn api_service:app --host 0.0.0.0 --port $PORT
EOF

        echo -e "${GREEN}✓ Procfile 已创建${NC}"
    fi
}

# 创建 runtime.txt（指定 Python 版本）
create_runtime() {
    if [ ! -f "runtime.txt" ]; then
        echo ""
        echo -e "${BLUE}创建 runtime.txt...${NC}"

        cat > runtime.txt << 'EOF'
python-3.11
EOF

        echo -e "${GREEN}✓ runtime.txt 已创建${NC}"
    fi
}

# 部署
deploy_to_railway() {
    echo ""
    echo "================================================"
    echo "  部署到 Railway"
    echo "================================================"
    echo ""

    echo -e "${BLUE}开始部署...${NC}"
    echo "这可能需要几分钟时间..."
    echo ""

    railway up

    if [ $? -eq 0 ]; then
        echo ""
        echo -e "${GREEN}✓ 部署成功！${NC}"
    else
        echo -e "${RED}✗ 部署失败${NC}"
        echo ""
        echo "查看日志: railway logs"
        exit 1
    fi
}

# 获取部署信息
get_deployment_info() {
    echo ""
    echo "================================================"
    echo "  部署信息"
    echo "================================================"
    echo ""

    # 获取域名
    DOMAIN=$(railway domain 2>/dev/null || echo "未配置域名")

    echo "项目状态:"
    railway status

    echo ""
    echo "访问链接:"
    if [ "$DOMAIN" != "未配置域名" ]; then
        echo "  - API 服务: https://$DOMAIN"
        echo "  - API 文档: https://$DOMAIN/docs"
        echo "  - 健康检查: https://$DOMAIN/health"
    else
        echo "  ${YELLOW}尚未配置域名${NC}"
        echo "  运行: railway domain 来配置域名"
    fi

    echo ""
    echo "常用命令:"
    echo "  - 查看日志: railway logs"
    echo "  - 打开控制台: railway open"
    echo "  - 查看环境变量: railway variables"
    echo "  - 重新部署: railway up"
    echo ""
}

# 配置域名
configure_domain() {
    echo ""
    read -p "是否配置自定义域名? (y/N): " -n 1 -r
    echo

    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${BLUE}生成 Railway 域名...${NC}"
        railway domain

        echo ""
        echo "如需配置自定义域名，请访问 Railway Dashboard"
        echo "运行: railway open"
    fi
}

# 主流程
main() {
    echo "开始 Railway 部署流程..."
    echo ""

    # 1. 检查 CLI
    check_railway_cli

    # 2. 登录
    login_railway

    # 3. 初始化项目
    init_project

    # 4. 创建配置文件
    create_procfile
    create_runtime

    # 5. 配置环境变量
    configure_env_vars

    # 6. 部署
    deploy_to_railway

    # 7. 配置域名
    configure_domain

    # 8. 显示部署信息
    get_deployment_info

    echo ""
    echo "================================================"
    echo -e "${GREEN}✓ Railway 部署完成！${NC}"
    echo "================================================"
    echo ""
    echo "下一步:"
    echo "  1. 访问 API 文档测试接口"
    echo "  2. 集成到飞书多维表格"
    echo "  3. 查看日志: railway logs"
    echo ""
}

# 运行主流程
main
