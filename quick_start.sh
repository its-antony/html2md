#!/bin/bash

# HTML2MD 快速启动脚本
# 一键完成所有配置和部署

set -e

echo "================================================"
echo "  HTML2MD Web API 快速启动向导"
echo "================================================"
echo ""

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# 显示菜单
show_menu() {
    echo ""
    echo "请选择操作:"
    echo ""
    echo "  1) 🚀 完整部署流程（Supabase + Railway）- 推荐"
    echo "  2) 🔧 仅配置 Supabase"
    echo "  3) ☁️  仅部署到 Railway"
    echo "  4) 🌐 部署到 Cloudflare Workers"
    echo "  5) 💻 本地开发运行"
    echo "  6) 🧪 测试 API"
    echo "  7) 📚 查看文档"
    echo "  0) 退出"
    echo ""
}

# 完整部署流程
full_deployment() {
    echo ""
    echo -e "${BLUE}开始完整部署流程...${NC}"
    echo ""

    echo "步骤 1/3: 配置 Supabase"
    echo "----------------------------------------"
    ./setup_supabase.sh

    echo ""
    echo "步骤 2/3: 部署到 Railway"
    echo "----------------------------------------"
    ./deploy_railway.sh

    echo ""
    echo "步骤 3/3: 测试 API"
    echo "----------------------------------------"
    read -p "是否运行测试? (y/N): " -n 1 -r
    echo

    if [[ $REPLY =~ ^[Yy]$ ]]; then
        # 获取 Railway URL
        RAILWAY_URL=$(railway domain 2>/dev/null || echo "")

        if [ -n "$RAILWAY_URL" ]; then
            echo "测试 URL: https://$RAILWAY_URL"

            # 测试健康检查
            echo -e "${BLUE}测试健康检查...${NC}"
            curl -s "https://$RAILWAY_URL/health" | python3 -m json.tool

            echo ""
            echo -e "${GREEN}✓ 部署完成！${NC}"
            echo ""
            echo "访问链接:"
            echo "  - API 文档: https://$RAILWAY_URL/docs"
            echo "  - 健康检查: https://$RAILWAY_URL/health"
        else
            echo -e "${YELLOW}无法获取 Railway URL，请手动测试${NC}"
        fi
    fi
}

# 本地运行
local_run() {
    echo ""
    echo -e "${BLUE}本地运行模式${NC}"
    echo ""

    # 检查 .env 文件
    if [ ! -f ".env" ]; then
        echo -e "${YELLOW}.env 文件不存在${NC}"
        echo ""
        read -p "是否运行 Supabase 配置向导? (y/N): " -n 1 -r
        echo

        if [[ $REPLY =~ ^[Yy]$ ]]; then
            ./setup_supabase.sh
        else
            echo "请先创建 .env 文件"
            echo "参考: .env.example"
            return
        fi
    fi

    # 启动服务
    echo -e "${BLUE}启动 API 服务...${NC}"
    ./start_api.sh
}

# 测试 API
test_api() {
    echo ""
    echo -e "${BLUE}测试 API${NC}"
    echo ""

    echo "请选择测试目标:"
    echo "  1) 本地 (localhost:8000)"
    echo "  2) Railway"
    echo "  3) 自定义 URL"
    echo ""
    read -p "选择 [1-3]: " choice

    case $choice in
        1)
            TEST_URL="http://localhost:8000"
            ;;
        2)
            RAILWAY_URL=$(railway domain 2>/dev/null || echo "")
            if [ -n "$RAILWAY_URL" ]; then
                TEST_URL="https://$RAILWAY_URL"
            else
                echo -e "${RED}无法获取 Railway URL${NC}"
                return
            fi
            ;;
        3)
            read -p "请输入 API URL: " TEST_URL
            ;;
        *)
            echo -e "${RED}无效选择${NC}"
            return
            ;;
    esac

    echo ""
    echo -e "${BLUE}测试目标: $TEST_URL${NC}"
    echo ""

    # 运行测试脚本
    if [ -f "test_api.py" ]; then
        python3 test_api.py "$TEST_URL"
    else
        # 简单的 curl 测试
        echo "健康检查:"
        curl -s "$TEST_URL/health" | python3 -m json.tool || echo "测试失败"
    fi
}

# 查看文档
show_docs() {
    echo ""
    echo "文档列表:"
    echo ""
    echo "  1) README.md - 项目概述"
    echo "  2) README_API.md - API 服务说明"
    echo "  3) DEPLOYMENT.md - 部署指南"
    echo "  4) API_USAGE.md - API 使用文档"
    echo "  5) CLI_GUIDE.md - CLI 工具指南"
    echo ""
    read -p "选择文档 [1-5]: " choice

    case $choice in
        1) doc="README.md" ;;
        2) doc="README_API.md" ;;
        3) doc="DEPLOYMENT.md" ;;
        4) doc="API_USAGE.md" ;;
        5) doc="CLI_GUIDE.md" ;;
        *)
            echo -e "${RED}无效选择${NC}"
            return
            ;;
    esac

    if [ -f "$doc" ]; then
        # 尝试使用更好的查看器
        if command -v bat &> /dev/null; then
            bat "$doc"
        elif command -v less &> /dev/null; then
            less "$doc"
        else
            cat "$doc"
        fi
    else
        echo -e "${RED}文档不存在: $doc${NC}"
    fi
}

# 主循环
main() {
    while true; do
        show_menu
        read -p "请选择 [0-7]: " choice

        case $choice in
            1)
                full_deployment
                ;;
            2)
                ./setup_supabase.sh
                ;;
            3)
                ./deploy_railway.sh
                ;;
            4)
                ./setup_cloudflare.sh
                ;;
            5)
                local_run
                ;;
            6)
                test_api
                ;;
            7)
                show_docs
                ;;
            0)
                echo ""
                echo "再见！"
                exit 0
                ;;
            *)
                echo -e "${RED}无效选择，请重试${NC}"
                ;;
        esac

        echo ""
        read -p "按 Enter 继续..."
    done
}

# 启动
echo "欢迎使用 HTML2MD Web API 快速启动向导"
echo ""
echo "这个向导会帮助你:"
echo "  ✓ 配置 Supabase 存储"
echo "  ✓ 部署到云平台"
echo "  ✓ 测试 API 服务"
echo ""

main
