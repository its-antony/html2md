# CLI 自动化部署指南

使用命令行工具快速配置 Supabase 和部署到云平台。

---

## 目录

- [Supabase CLI](#supabase-cli)
- [Railway CLI](#railway-cli-推荐)
- [Cloudflare CLI](#cloudflare-cli)
- [常见问题](#常见问题)

---

## Supabase CLI

### 一键配置

```bash
# 自动安装 CLI、登录、配置项目
./setup_supabase.sh
```

### 手动操作

#### 1. 安装 Supabase CLI

**macOS:**
```bash
brew install supabase/tap/supabase
```

**npm:**
```bash
npm install -g supabase
```

**其他平台:**
```bash
# 查看官方文档
# https://supabase.com/docs/guides/cli
```

#### 2. 登录

```bash
supabase login
```

浏览器会自动打开授权页面。

#### 3. 链接项目

**方式 1: 链接现有项目（推荐）**

```bash
# 查看所有项目
supabase projects list

# 链接项目（替换 your-project-ref）
supabase link --project-ref your-project-ref
```

**方式 2: 创建新项目**

```bash
supabase projects create my-project \
  --db-password your-password \
  --region us-east-1
```

> ⚠️ 注意：创建项目需要付费订阅

#### 4. 创建存储桶

```bash
# 执行 SQL
supabase db execute --sql "
  INSERT INTO storage.buckets (id, name, public)
  VALUES ('markdown-files', 'markdown-files', true)
  ON CONFLICT (id) DO NOTHING;
"
```

#### 5. 初始化数据库

```bash
# 执行 SQL 文件
supabase db execute --file supabase_init.sql
```

#### 6. 获取配置信息

```bash
# 查看项目状态
supabase status

# API URL 会显示在输出中
# 然后去 Dashboard 获取 API Key
```

访问: https://app.supabase.com
- 选择项目
- Settings → API
- 复制 "anon" "public" key

#### 7. 保存配置

创建 `.env` 文件:

```bash
cat > .env << EOF
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_BUCKET=markdown-files
EOF
```

### 常用命令

```bash
# 查看项目列表
supabase projects list

# 查看项目状态
supabase status

# 执行 SQL
supabase db execute --sql "SELECT * FROM conversions LIMIT 10;"

# 执行 SQL 文件
supabase db execute --file migration.sql

# 查看存储桶
supabase storage ls

# 重置本地数据库（开发环境）
supabase db reset

# 查看日志
supabase functions logs

# 断开项目链接
supabase unlink
```

---

## Railway CLI (推荐)

Railway 是最适合 Python 项目的部署平台：
- ✅ 免费额度充足
- ✅ 自动检测 Python 项目
- ✅ 简单易用
- ✅ 支持环境变量管理

### 一键部署

```bash
# 自动安装 CLI、登录、部署
./deploy_railway.sh
```

### 手动操作

#### 1. 安装 Railway CLI

**macOS:**
```bash
brew install railway
```

**Linux/其他:**
```bash
bash <(curl -fsSL cli.new)
```

**npm:**
```bash
npm install -g @railway/cli
```

#### 2. 登录

```bash
railway login
```

#### 3. 初始化项目

**创建新项目:**
```bash
railway init
```

**链接现有项目:**
```bash
railway link
```

#### 4. 配置环境变量

**方式 1: 从 .env 文件导入**

```bash
# 批量设置（手动逐行）
while IFS='=' read -r key value; do
  railway variables set "$key=$value"
done < .env
```

**方式 2: 手动设置**

```bash
railway variables set SUPABASE_URL=https://xxx.supabase.co
railway variables set SUPABASE_KEY=your-key
railway variables set SUPABASE_BUCKET=markdown-files
```

**方式 3: 使用 Web 界面**

```bash
# 打开 Railway Dashboard
railway open
```

在 Variables 选项卡中添加环境变量。

#### 5. 创建配置文件

**Procfile:**
```bash
cat > Procfile << 'EOF'
web: uvicorn api_service:app --host 0.0.0.0 --port $PORT
EOF
```

**runtime.txt (可选):**
```bash
echo "python-3.11" > runtime.txt
```

#### 6. 部署

```bash
railway up
```

部署完成后会自动分配一个域名。

#### 7. 配置域名

**生成 Railway 域名:**
```bash
railway domain
```

**绑定自定义域名:**

在 Railway Dashboard 中配置（运行 `railway open`）。

### 常用命令

```bash
# 查看项目状态
railway status

# 查看日志（实时）
railway logs

# 查看日志（最近 100 行）
railway logs --lines 100

# 打开 Dashboard
railway open

# 查看环境变量
railway variables

# 删除环境变量
railway variables delete KEY_NAME

# 重新部署
railway up

# 查看部署历史
railway deployments

# 回滚到之前的部署
railway rollback

# 连接到数据库（如果有）
railway connect

# 删除项目
railway delete
```

### 监控和调试

```bash
# 实时查看日志
railway logs --follow

# 查看特定服务的日志
railway logs --service api

# 查看构建日志
railway logs --build

# SSH 连接（如果支持）
railway shell
```

---

## Cloudflare CLI

> ⚠️ **重要提示**:
> - Cloudflare Workers 的 Python 支持处于 Beta 阶段
> - 需要付费计划（约 $5/月）
> - CPU 时间有限制（可能导致超时）
> - **推荐使用 Railway 代替**

### 一键配置

```bash
# 自动安装 CLI、登录、部署
./setup_cloudflare.sh
```

### 手动操作

#### 1. 安装 Wrangler

```bash
npm install -g wrangler
```

#### 2. 登录

```bash
wrangler login
```

#### 3. 配置 wrangler.toml

```toml
name = "html2md-api"
main = "api_service.py"
compatibility_date = "2024-01-01"

[vars]
SUPABASE_BUCKET = "markdown-files"
```

#### 4. 配置 Secrets

```bash
# 配置敏感信息
echo "https://xxx.supabase.co" | wrangler secret put SUPABASE_URL
echo "your-key" | wrangler secret put SUPABASE_KEY
```

#### 5. 部署

```bash
wrangler deploy
```

### 常用命令

```bash
# 查看登录状态
wrangler whoami

# 本地开发
wrangler dev

# 查看日志
wrangler tail

# 查看部署历史
wrangler deployments list

# 删除 Worker
wrangler delete

# 查看 Secrets
wrangler secret list

# 删除 Secret
wrangler secret delete KEY_NAME

# 查看配置
wrangler config
```

---

## 完整部署流程（推荐）

### 步骤 1: 配置 Supabase

```bash
# 一键配置
./setup_supabase.sh

# 或手动操作
supabase login
supabase link --project-ref your-ref
supabase db execute --file supabase_init.sql
```

### 步骤 2: 部署到 Railway

```bash
# 一键部署
./deploy_railway.sh

# 或手动操作
railway login
railway init
railway variables set SUPABASE_URL=xxx
railway variables set SUPABASE_KEY=xxx
railway up
```

### 步骤 3: 测试 API

```bash
# 获取部署的 URL
RAILWAY_URL=$(railway domain)

# 测试健康检查
curl https://$RAILWAY_URL/health

# 测试转换 API
curl "https://$RAILWAY_URL/api/convert?url=https://example.com"
```

### 步骤 4: 集成飞书

在飞书多维表格中配置 Webhook:
```
URL: https://your-railway-url.railway.app/api/convert
Method: GET
参数: url={{URL字段}}
```

---

## 常见问题

### Q: Supabase CLI 登录失败？

**解决方案:**
```bash
# 清除缓存
rm -rf ~/.supabase

# 重新登录
supabase login
```

### Q: Railway 部署失败？

**检查步骤:**

1. 查看日志
```bash
railway logs
```

2. 验证环境变量
```bash
railway variables
```

3. 确认 requirements.txt 正确
```bash
cat requirements.txt
```

4. 重新部署
```bash
railway up --force
```

### Q: 如何更新已部署的服务？

**Railway:**
```bash
# 修改代码后
git add .
git commit -m "update"
railway up
```

**Cloudflare:**
```bash
wrangler deploy
```

### Q: 如何查看生产环境日志？

**Railway:**
```bash
# 实时日志
railway logs --follow

# 最近 500 行
railway logs --lines 500
```

**Cloudflare:**
```bash
# 实时日志
wrangler tail

# 查看错误
wrangler tail --status error
```

### Q: 环境变量更新后需要重新部署吗？

**Railway:** 是的，需要重新部署
```bash
railway variables set KEY=value
railway up
```

**Cloudflare Secrets:** 不需要，自动生效
```bash
echo "new-value" | wrangler secret put KEY
```

### Q: 如何回滚到之前的版本？

**Railway:**
```bash
# 查看部署历史
railway deployments

# 回滚
railway rollback <deployment-id>
```

**Cloudflare:**
```bash
# 查看部署历史
wrangler deployments list

# 部署特定版本
wrangler rollback <deployment-id>
```

---

## 最佳实践

### 1. 使用 .env 文件管理配置

```bash
# .env.example (提交到 git)
SUPABASE_URL=https://example.supabase.co
SUPABASE_KEY=your-key-here

# .env (不提交到 git)
SUPABASE_URL=https://real-project.supabase.co
SUPABASE_KEY=real-key-here
```

### 2. 自动化脚本

创建 `Makefile`:

```makefile
.PHONY: setup deploy logs

setup:
	./setup_supabase.sh
	./deploy_railway.sh

deploy:
	railway up

logs:
	railway logs --follow

test:
	python test_api.py
```

使用:
```bash
make setup   # 初始化
make deploy  # 部署
make logs    # 查看日志
make test    # 测试
```

### 3. 多环境管理

```bash
# 开发环境
railway link --environment development
railway variables set SUPABASE_URL=dev-url

# 生产环境
railway link --environment production
railway variables set SUPABASE_URL=prod-url

# 切换环境
railway environment production
railway up
```

### 4. 监控和告警

```bash
# Railway Dashboard 配置告警
railway open

# 在 Settings → Notifications 中配置
# - 部署失败通知
# - 服务离线通知
# - 资源使用告警
```

---

## 总结

| 工具 | 推荐度 | 使用场景 |
|------|--------|----------|
| **Railway** | ⭐⭐⭐⭐⭐ | Python 应用部署（推荐） |
| **Supabase CLI** | ⭐⭐⭐⭐⭐ | 数据库和存储管理（必需） |
| Cloudflare Workers | ⭐⭐ | 边缘计算（有限制，不推荐） |

**快速开始:**

```bash
# 1. 配置 Supabase
./setup_supabase.sh

# 2. 部署到 Railway
./deploy_railway.sh

# 3. 测试
python test_api.py
```

完成！🎉
