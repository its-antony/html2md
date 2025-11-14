#!/bin/bash

# HTML2MD API 启动脚本

echo "================================================"
echo "  HTML2MD Web API 服务启动脚本"
echo "================================================"

# 检查是否安装了 Python 3
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到 Python 3，请先安装 Python 3.8+"
    exit 1
fi

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
echo "激活虚拟环境..."
source venv/bin/activate

# 安装/更新依赖
echo "安装依赖..."
pip install -r requirements.txt -q

# 检查环境变量
if [ ! -f ".env" ]; then
    echo ""
    echo "警告: 未找到 .env 文件"
    echo "请先配置 Supabase 信息："
    echo "  1. 复制 .env.example 为 .env"
    echo "  2. 填写 SUPABASE_URL 和 SUPABASE_KEY"
    echo ""
    read -p "是否继续启动？(y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# 加载环境变量
if [ -f ".env" ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# 启动服务
echo ""
echo "================================================"
echo "  启动 API 服务..."
echo "================================================"
echo "  - API 文档: http://localhost:8000/docs"
echo "  - 健康检查: http://localhost:8000/health"
echo "  - 按 Ctrl+C 停止服务"
echo "================================================"
echo ""

uvicorn api_service:app --host 0.0.0.0 --port 8000 --reload
