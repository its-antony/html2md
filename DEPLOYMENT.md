# Web API 部署指南

本文档介绍如何将 HTML2MD 服务部署到云平台。

## 部署方案对比

| 方案 | 优点 | 缺点 | 成本 |
|------|------|------|------|
| **Cloudflare Workers** | 全球 CDN，自动扩展 | Python 支持有限，需付费计划 | 有付费要求 |
| **Railway/Render** | 简单易用，支持 Python | 免费额度有限 | 免费/付费 |
| **Docker 部署** | 灵活，可部署到任意平台 | 需要自己管理服务器 | 取决于服务器 |
| **本地运行** | 开发测试方便 | 不适合生产环境 | 免费 |

## 推荐方案：Railway + Supabase

Railway 对 Python 支持好，部署简单，免费额度足够个人使用。

---

## 1. Supabase 配置（必需）

### 1.1 创建 Supabase 项目

1. 访问 [https://supabase.com](https://supabase.com)
2. 注册并创建新项目
3. 等待项目初始化完成

### 1.2 获取配置信息

在项目设置中找到：

```
Project URL: https://xxxxx.supabase.co
Project API Key (anon, public): eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### 1.3 创建存储桶

```sql
-- 在 SQL Editor 中执行
-- 创建存储桶（如果不存在）
INSERT INTO storage.buckets (id, name, public)
VALUES ('markdown-files', 'markdown-files', true)
ON CONFLICT (id) DO NOTHING;
```

### 1.4 创建数据表（可选，用于记录转换历史）

```sql
-- 创建转换记录表
CREATE TABLE IF NOT EXISTS conversions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    url TEXT NOT NULL,
    md_file_url TEXT,
    download_media BOOLEAN DEFAULT false,
    media_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 创建索引
CREATE INDEX idx_conversions_created_at ON conversions(created_at DESC);
```

---

## 2. 本地开发运行

### 2.1 安装依赖

```bash
# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 2.2 配置环境变量

```bash
# 复制示例文件
cp .env.example .env

# 编辑 .env 文件，填入 Supabase 配置
# SUPABASE_URL=https://xxxxx.supabase.co
# SUPABASE_KEY=your-anon-key
# SUPABASE_BUCKET=markdown-files
```

### 2.3 启动服务

```bash
# 开发模式（自动重载）
uvicorn api_service:app --reload --host 0.0.0.0 --port 8000

# 生产模式
uvicorn api_service:app --host 0.0.0.0 --port 8000 --workers 4
```

访问：
- API 文档: http://localhost:8000/docs
- 健康检查: http://localhost:8000/health

---

## 3. 部署到 Railway（推荐）

### 3.1 准备工作

1. 注册 [Railway](https://railway.app) 账号
2. 安装 Railway CLI（可选）

```bash
npm install -g @railway/cli
railway login
```

### 3.2 方式一：通过 GitHub 部署（推荐）

1. 将代码推送到 GitHub
2. 在 Railway 中点击 "New Project"
3. 选择 "Deploy from GitHub repo"
4. 选择你的仓库
5. Railway 会自动检测 Python 项目并部署

### 3.3 方式二：通过 CLI 部署

```bash
# 初始化项目
railway init

# 部署
railway up
```

### 3.4 配置环境变量

在 Railway 项目设置中添加：

```
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_BUCKET=markdown-files
```

### 3.5 配置启动命令

Railway 通常会自动检测，如果需要手动配置：

**Procfile** 或在 Railway 设置中配置：
```
web: uvicorn api_service:app --host 0.0.0.0 --port $PORT
```

---

## 4. 部署到 Render

### 4.1 创建 Web Service

1. 访问 [Render](https://render.com)
2. 连接 GitHub 仓库
3. 选择 "Web Service"
4. 配置：
   - Environment: Python 3
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn api_service:app --host 0.0.0.0 --port $PORT`

### 4.2 配置环境变量

在 Render 项目设置中添加环境变量（同上）。

---

## 5. Docker 部署

### 5.1 构建镜像

```bash
docker build -t html2md-api .
```

### 5.2 运行容器

```bash
docker run -d \
  -p 8000:8000 \
  -e SUPABASE_URL=https://xxxxx.supabase.co \
  -e SUPABASE_KEY=your-anon-key \
  -e SUPABASE_BUCKET=markdown-files \
  --name html2md-api \
  html2md-api
```

### 5.3 使用 Docker Compose

创建 `docker-compose.yml`:

```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_KEY=${SUPABASE_KEY}
      - SUPABASE_BUCKET=markdown-files
    restart: unless-stopped
```

运行：
```bash
docker-compose up -d
```

---

## 6. Cloudflare Workers 部署（高级）

⚠️ **注意**: Cloudflare Workers 的 Python 支持目前处于 Beta 阶段，且需要付费计划。

### 6.1 安装 Wrangler

```bash
npm install -g wrangler
wrangler login
```

### 6.2 配置 Secrets

```bash
wrangler secret put SUPABASE_URL
wrangler secret put SUPABASE_KEY
```

### 6.3 部署

```bash
wrangler deploy
```

### 6.4 限制说明

- CPU 时间限制（免费版 10ms，付费版 50ms）
- 对于复杂的 HTML 转换可能超时
- 建议使用异步处理或队列

---

## 7. 飞书多维表格集成

### 7.1 方式一：使用 Webhook（推荐）

1. 部署 `feishu_webhook.py` 到服务器
2. 在飞书多维表格中配置 Webhook
3. 当新增记录时自动触发转换

### 7.2 方式二：使用飞书机器人

创建一个飞书机器人，使用斜杠命令调用 API：

```
/convert https://example.com/article
```

### 7.3 方式三：定时任务

使用 Cron 定时扫描表格中的待处理记录。

---

## 8. API 使用示例

### 8.1 基本使用

```bash
# POST 请求
curl -X POST "https://your-api.com/api/convert" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://mp.weixin.qq.com/s/xxxxx",
    "download_media": true
  }'

# GET 请求（简化版）
curl "https://your-api.com/api/convert?url=https://example.com&download_media=true"
```

### 8.2 Python 调用

```python
import requests

response = requests.post(
    "https://your-api.com/api/convert",
    json={
        "url": "https://mp.weixin.qq.com/s/xxxxx",
        "download_media": True
    }
)

result = response.json()
if result['success']:
    md_url = result['data']['md_url']
    print(f"Markdown 文件: {md_url}")
```

### 8.3 JavaScript 调用

```javascript
async function convertUrl(url) {
  const response = await fetch('https://your-api.com/api/convert', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      url: url,
      download_media: true
    })
  });

  const result = await response.json();
  return result.data.md_url;
}
```

---

## 9. 监控和维护

### 9.1 健康检查

```bash
curl https://your-api.com/health
```

### 9.2 日志查看

**Railway:**
```bash
railway logs
```

**Docker:**
```bash
docker logs html2md-api -f
```

### 9.3 性能优化

1. 启用缓存（Redis）
2. 使用消息队列处理长时间任务
3. 限流保护
4. CDN 加速静态资源

---

## 10. 故障排查

### 问题：转换超时

**解决方案:**
- 增加超时时间
- 使用异步任务队列
- 优化 HTML 解析逻辑

### 问题：Supabase 上传失败

**解决方案:**
- 检查存储桶权限
- 验证 API Key 是否正确
- 确认存储桶已创建

### 问题：内存不足

**解决方案:**
- 增加服务器内存
- 优化文件处理流程
- 使用流式上传

---

## 11. 安全建议

1. ✅ 使用 HTTPS
2. ✅ 配置 CORS 白名单
3. ✅ 添加 API 速率限制
4. ✅ 使用环境变量存储敏感信息
5. ✅ 定期更新依赖包
6. ✅ 添加请求验证和日志

---

## 支持

如有问题，请提交 Issue 或查看文档。
