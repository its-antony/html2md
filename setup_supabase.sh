#!/bin/bash

# Supabase 自动化配置脚本
# 使用 Supabase CLI 完成所有配置

set -e  # 遇到错误立即退出

echo "================================================"
echo "  Supabase 自动化配置工具"
echo "================================================"
echo ""

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 检查是否安装了 Supabase CLI
check_supabase_cli() {
    if ! command -v supabase &> /dev/null; then
        echo -e "${YELLOW}未检测到 Supabase CLI${NC}"
        echo ""
        echo "请选择安装方式:"
        echo "  1) macOS (Homebrew)"
        echo "  2) npm"
        echo "  3) 手动安装"
        echo ""
        read -p "选择 [1-3]: " choice

        case $choice in
            1)
                echo -e "${BLUE}使用 Homebrew 安装...${NC}"
                brew install supabase/tap/supabase
                ;;
            2)
                echo -e "${BLUE}使用 npm 安装...${NC}"
                npm install -g supabase
                ;;
            3)
                echo -e "${YELLOW}请访问: https://supabase.com/docs/guides/cli${NC}"
                exit 1
                ;;
            *)
                echo -e "${RED}无效选择${NC}"
                exit 1
                ;;
        esac
    else
        echo -e "${GREEN}✓ Supabase CLI 已安装${NC}"
    fi
}

# 登录 Supabase
login_supabase() {
    echo ""
    echo -e "${BLUE}正在登录 Supabase...${NC}"
    echo "这会在浏览器中打开登录页面"
    echo ""

    supabase login

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ 登录成功${NC}"
    else
        echo -e "${RED}✗ 登录失败${NC}"
        exit 1
    fi
}

# 选择或创建项目
setup_project() {
    echo ""
    echo "================================================"
    echo "  项目配置"
    echo "================================================"
    echo ""
    echo "请选择:"
    echo "  1) 使用现有项目"
    echo "  2) 创建新项目"
    echo ""
    read -p "选择 [1-2]: " choice

    case $choice in
        1)
            use_existing_project
            ;;
        2)
            create_new_project
            ;;
        *)
            echo -e "${RED}无效选择${NC}"
            exit 1
            ;;
    esac
}

# 使用现有项目
use_existing_project() {
    echo ""
    echo -e "${BLUE}获取项目列表...${NC}"

    # 列出所有项目
    supabase projects list

    echo ""
    read -p "请输入项目 Reference ID: " PROJECT_REF

    if [ -z "$PROJECT_REF" ]; then
        echo -e "${RED}项目 ID 不能为空${NC}"
        exit 1
    fi

    # 链接项目
    echo -e "${BLUE}链接项目...${NC}"
    supabase link --project-ref "$PROJECT_REF"

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ 项目链接成功${NC}"
    else
        echo -e "${RED}✗ 项目链接失败${NC}"
        exit 1
    fi
}

# 创建新项目
create_new_project() {
    echo ""
    echo -e "${YELLOW}注意: 通过 CLI 创建项目需要付费订阅${NC}"
    echo -e "${YELLOW}建议在网页端创建项目，然后选择'使用现有项目'${NC}"
    echo ""
    read -p "是否继续? (y/N): " -n 1 -r
    echo

    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "已取消"
        exit 1
    fi

    read -p "项目名称: " PROJECT_NAME
    read -p "数据库密码: " DB_PASSWORD
    read -p "区域 (默认: us-east-1): " REGION
    REGION=${REGION:-us-east-1}

    echo -e "${BLUE}创建项目...${NC}"
    supabase projects create "$PROJECT_NAME" --db-password "$DB_PASSWORD" --region "$REGION"
}

# 创建存储桶
create_storage_bucket() {
    echo ""
    echo "================================================"
    echo "  配置存储桶"
    echo "================================================"
    echo ""

    BUCKET_NAME="markdown-files"

    echo -e "${BLUE}创建存储桶: $BUCKET_NAME${NC}"

    # 使用 SQL 创建存储桶
    supabase db execute --sql "
        INSERT INTO storage.buckets (id, name, public)
        VALUES ('$BUCKET_NAME', '$BUCKET_NAME', true)
        ON CONFLICT (id) DO NOTHING;
    "

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ 存储桶创建成功${NC}"
    else
        echo -e "${YELLOW}⚠ 存储桶可能已存在${NC}"
    fi
}

# 初始化数据库表
init_database() {
    echo ""
    echo "================================================"
    echo "  初始化数据库"
    echo "================================================"
    echo ""

    echo -e "${BLUE}执行初始化 SQL...${NC}"

    if [ -f "supabase_init.sql" ]; then
        supabase db execute --file supabase_init.sql

        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✓ 数据库初始化成功${NC}"
        else
            echo -e "${RED}✗ 数据库初始化失败${NC}"
            exit 1
        fi
    else
        echo -e "${YELLOW}未找到 supabase_init.sql，跳过数据库初始化${NC}"
    fi
}

# 获取配置信息
get_project_info() {
    echo ""
    echo "================================================"
    echo "  获取项目配置信息"
    echo "================================================"
    echo ""

    # 获取项目信息
    PROJECT_URL=$(supabase status | grep "API URL" | awk '{print $3}')

    echo -e "${BLUE}获取 API Keys...${NC}"
    echo ""
    echo "请在 Supabase Dashboard 中获取 API Key:"
    echo "  1. 访问: https://app.supabase.com"
    echo "  2. 选择你的项目"
    echo "  3. 点击左侧 Settings → API"
    echo "  4. 复制 'anon' 'public' key"
    echo ""

    read -p "请粘贴 ANON_KEY: " ANON_KEY

    # 保存到 .env 文件
    echo ""
    echo -e "${BLUE}保存配置到 .env 文件...${NC}"

    if [ -f ".env" ]; then
        read -p ".env 文件已存在，是否覆盖? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo "已取消"
            return
        fi
    fi

    cat > .env << EOF
# Supabase 配置
SUPABASE_URL=${PROJECT_URL}
SUPABASE_KEY=${ANON_KEY}
SUPABASE_BUCKET=markdown-files

# API 配置
API_HOST=0.0.0.0
API_PORT=8000
EOF

    echo -e "${GREEN}✓ 配置已保存到 .env${NC}"

    # 显示配置信息
    echo ""
    echo "================================================"
    echo "  配置信息"
    echo "================================================"
    echo "SUPABASE_URL: ${PROJECT_URL}"
    echo "SUPABASE_KEY: ${ANON_KEY:0:20}..."
    echo "SUPABASE_BUCKET: markdown-files"
    echo "================================================"
}

# 测试连接
test_connection() {
    echo ""
    echo "================================================"
    echo "  测试连接"
    echo "================================================"
    echo ""

    read -p "是否测试 API 连接? (y/N): " -n 1 -r
    echo

    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${BLUE}启动测试...${NC}"

        # 加载环境变量
        export $(cat .env | grep -v '^#' | xargs)

        # 创建简单的测试脚本
        python3 - << 'PYTHON_EOF'
import os
from supabase import create_client

try:
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_KEY')

    if not url or not key:
        print("❌ 环境变量未设置")
        exit(1)

    client = create_client(url, key)

    # 测试存储桶
    buckets = client.storage.list_buckets()
    print(f"✓ 连接成功")
    print(f"✓ 找到 {len(buckets)} 个存储桶")

    # 检查 markdown-files 桶
    bucket_names = [b['name'] for b in buckets]
    if 'markdown-files' in bucket_names:
        print("✓ markdown-files 存储桶已存在")
    else:
        print("⚠ markdown-files 存储桶未找到")

except Exception as e:
    print(f"❌ 连接失败: {e}")
    exit(1)
PYTHON_EOF

        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✓ 测试通过${NC}"
        else
            echo -e "${RED}✗ 测试失败${NC}"
        fi
    fi
}

# 主流程
main() {
    echo "开始配置..."
    echo ""

    # 1. 检查 CLI
    check_supabase_cli

    # 2. 登录
    login_supabase

    # 3. 设置项目
    setup_project

    # 4. 创建存储桶
    create_storage_bucket

    # 5. 初始化数据库
    init_database

    # 6. 获取配置信息
    get_project_info

    # 7. 测试连接
    test_connection

    echo ""
    echo "================================================"
    echo -e "${GREEN}✓ Supabase 配置完成！${NC}"
    echo "================================================"
    echo ""
    echo "下一步:"
    echo "  1. 检查 .env 文件中的配置"
    echo "  2. 运行 ./start_api.sh 启动 API 服务"
    echo "  3. 访问 http://localhost:8000/docs 查看文档"
    echo ""
}

# 运行主流程
main
