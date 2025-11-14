#!/bin/bash
# Railway 部署指南脚本
# 此脚本会引导你完成 Railway 部署

echo "🚀 HTML2MD Railway 部署指南"
echo "================================"
echo ""

# 检查 Railway CLI
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI 未安装"
    echo "请运行: brew install railway"
    exit 1
fi

echo "✅ Railway CLI 已安装"
echo ""

# 步骤 1: 登录
echo "步骤 1: 登录 Railway"
echo "-------------------"
echo "请在新打开的浏览器窗口中登录 Railway (使用 GitHub 账号)"
echo ""
read -p "按回车键继续..."

railway login

if [ $? -ne 0 ]; then
    echo "❌ 登录失败"
    exit 1
fi

echo "✅ 登录成功"
echo ""

# 步骤 2: 初始化项目
echo "步骤 2: 初始化 Railway 项目"
echo "-------------------------"
railway init

if [ $? -ne 0 ]; then
    echo "❌ 初始化失败"
    exit 1
fi

echo "✅ 项目初始化成功"
echo ""

# 步骤 3: 配置环境变量
echo "步骤 3: 配置环境变量"
echo "------------------"

# 从 .env 文件读取变量
if [ -f .env ]; then
    source .env

    echo "正在设置 SUPABASE_URL..."
    railway variables set SUPABASE_URL="$SUPABASE_URL"

    echo "正在设置 SUPABASE_KEY..."
    railway variables set SUPABASE_KEY="$SUPABASE_KEY"

    echo "正在设置 SUPABASE_BUCKET..."
    railway variables set SUPABASE_BUCKET="$SUPABASE_BUCKET"

    echo "✅ 环境变量配置完成"
else
    echo "⚠️  未找到 .env 文件，需要手动配置环境变量"
    echo "请运行以下命令："
    echo "  railway variables set SUPABASE_URL=your_url"
    echo "  railway variables set SUPABASE_KEY=your_key"
    echo "  railway variables set SUPABASE_BUCKET=markdown-files"
fi

echo ""

# 步骤 4: 部署
echo "步骤 4: 部署应用"
echo "--------------"
echo "正在部署到 Railway..."
echo ""

railway up

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ 部署成功！"
    echo ""
    echo "查看部署状态:"
    echo "  railway status"
    echo ""
    echo "查看日志:"
    echo "  railway logs"
    echo ""
    echo "获取公开 URL:"
    echo "  railway domain"
    echo ""
else
    echo "❌ 部署失败"
    echo "请检查日志: railway logs"
    exit 1
fi
