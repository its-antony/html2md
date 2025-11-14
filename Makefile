.PHONY: help install setup deploy test clean dev logs

# 默认目标
.DEFAULT_GOAL := help

# 颜色定义
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[1;33m
NC := \033[0m

help: ## 显示帮助信息
	@echo "$(BLUE)HTML2MD Web API - Makefile 命令$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-15s$(NC) %s\n", $$1, $$2}'
	@echo ""

install: ## 安装依赖
	@echo "$(BLUE)安装 Python 依赖...$(NC)"
	pip install -r requirements.txt

setup-supabase: ## 配置 Supabase
	@echo "$(BLUE)配置 Supabase...$(NC)"
	./setup_supabase.sh

setup-railway: ## 配置 Railway
	@echo "$(BLUE)配置 Railway...$(NC)"
	./deploy_railway.sh

setup: setup-supabase setup-railway ## 完整配置（Supabase + Railway）

deploy: ## 部署到 Railway
	@echo "$(BLUE)部署到 Railway...$(NC)"
	railway up

deploy-cloudflare: ## 部署到 Cloudflare Workers
	@echo "$(BLUE)部署到 Cloudflare...$(NC)"
	wrangler deploy

dev: ## 本地开发运行
	@echo "$(BLUE)启动开发服务器...$(NC)"
	uvicorn api_service:app --reload --host 0.0.0.0 --port 8000

start: ## 启动服务（使用脚本）
	./start_api.sh

test: ## 运行测试
	@echo "$(BLUE)运行 API 测试...$(NC)"
	python test_api.py

test-local: ## 测试本地服务
	@echo "$(BLUE)测试本地服务...$(NC)"
	curl -s http://localhost:8000/health | python -m json.tool

test-railway: ## 测试 Railway 部署
	@echo "$(BLUE)测试 Railway 部署...$(NC)"
	@RAILWAY_URL=$$(railway domain 2>/dev/null); \
	if [ -n "$$RAILWAY_URL" ]; then \
		curl -s "https://$$RAILWAY_URL/health" | python -m json.tool; \
	else \
		echo "$(YELLOW)无法获取 Railway URL$(NC)"; \
	fi

logs: ## 查看 Railway 日志
	railway logs --follow

logs-recent: ## 查看最近的日志
	railway logs --lines 100

open: ## 打开 Railway Dashboard
	railway open

clean: ## 清理临时文件
	@echo "$(BLUE)清理临时文件...$(NC)"
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf venv/ 2>/dev/null || true
	@echo "$(GREEN)清理完成$(NC)"

venv: ## 创建虚拟环境
	@echo "$(BLUE)创建虚拟环境...$(NC)"
	python3 -m venv venv
	@echo "$(GREEN)虚拟环境已创建$(NC)"
	@echo "运行: source venv/bin/activate"

init: venv install ## 初始化项目（创建虚拟环境 + 安装依赖）
	@echo "$(GREEN)项目初始化完成！$(NC)"
	@echo ""
	@echo "下一步:"
	@echo "  1. source venv/bin/activate"
	@echo "  2. cp .env.example .env"
	@echo "  3. 编辑 .env 填入 Supabase 配置"
	@echo "  4. make dev"

status: ## 查看项目状态
	@echo "$(BLUE)项目状态:$(NC)"
	@echo ""
	@echo "Python 版本:"
	@python3 --version
	@echo ""
	@echo "依赖状态:"
	@pip list | grep -E "fastapi|uvicorn|supabase|requests" || echo "未安装依赖"
	@echo ""
	@if [ -f ".env" ]; then \
		echo "$(GREEN)✓ .env 文件存在$(NC)"; \
	else \
		echo "$(YELLOW)✗ .env 文件不存在$(NC)"; \
	fi
	@echo ""
	@if command -v railway &> /dev/null; then \
		echo "$(GREEN)✓ Railway CLI 已安装$(NC)"; \
		railway whoami 2>/dev/null || echo "$(YELLOW)  未登录$(NC)"; \
	else \
		echo "$(YELLOW)✗ Railway CLI 未安装$(NC)"; \
	fi
	@echo ""
	@if command -v supabase &> /dev/null; then \
		echo "$(GREEN)✓ Supabase CLI 已安装$(NC)"; \
	else \
		echo "$(YELLOW)✗ Supabase CLI 未安装$(NC)"; \
	fi

docs: ## 打开 API 文档（本地）
	@echo "$(BLUE)打开 API 文档...$(NC)"
	@if command -v open &> /dev/null; then \
		open http://localhost:8000/docs; \
	elif command -v xdg-open &> /dev/null; then \
		xdg-open http://localhost:8000/docs; \
	else \
		echo "访问: http://localhost:8000/docs"; \
	fi

quick: ## 快速启动向导
	./quick_start.sh

# 开发辅助命令
format: ## 格式化代码（需要 black）
	@if command -v black &> /dev/null; then \
		black *.py; \
	else \
		echo "$(YELLOW)未安装 black，跳过格式化$(NC)"; \
	fi

lint: ## 代码检查（需要 flake8）
	@if command -v flake8 &> /dev/null; then \
		flake8 *.py; \
	else \
		echo "$(YELLOW)未安装 flake8，跳过检查$(NC)"; \
	fi

requirements: ## 更新 requirements.txt
	@echo "$(BLUE)更新 requirements.txt...$(NC)"
	pip freeze > requirements.txt
	@echo "$(GREEN)完成$(NC)"

# Railway 相关命令
railway-status: ## Railway 项目状态
	railway status

railway-vars: ## 查看 Railway 环境变量
	railway variables

railway-domain: ## 配置 Railway 域名
	railway domain

railway-rollback: ## 回滚 Railway 部署
	railway rollback

# Supabase 相关命令
supabase-login: ## 登录 Supabase
	supabase login

supabase-status: ## Supabase 项目状态
	supabase status

supabase-db: ## 执行 SQL（示例）
	@echo "$(BLUE)查询最近的转换记录...$(NC)"
	supabase db execute --sql "SELECT * FROM conversions ORDER BY created_at DESC LIMIT 10;"

# 一键命令
all: init setup deploy ## 完整流程（初始化 + 配置 + 部署）
	@echo "$(GREEN)所有步骤完成！$(NC)"
