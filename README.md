# HTML to Markdown Web API Service

将网页 URL 转换为 Markdown 格式的 Web API 服务，支持多个平台（微信公众号、知乎、小红书、掘金、CSDN等），使用 Supabase 存储，可部署到 Cloudflare Workers。

## 功能特性

- RESTful API 接口，方便客户端调用
- 支持多平台网页转换（微信公众号、知乎、小红书、掘金、CSDN、通用网页）
- 自动下载并存储媒体资源（图片、视频）
- 使用 Supabase 进行文件存储和元数据管理
- 支持部署到 Cloudflare Workers
- 完整的健康检查和错误处理

## 支持的平台

- 微信公众号 (mp.weixin.qq.com)
- 知乎 (zhihu.com)
- 小红书 (xiaohongshu.com)
- 掘金 (juejin.cn)
- CSDN (csdn.net)
- 通用网页

## 快速开始

### 1. 环境准备

```bash
# 克隆项目
git clone <your-repo-url>
cd html2md

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置环境变量

创建 `.env` 文件：

```bash
# Supabase 配置
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key
SUPABASE_BUCKET=markdown-files

# 服务端口（可选，默认8000）
PORT=8000
```

### 3. 初始化 Supabase 数据库

在 Supabase 控制台执行 `supabase_init.sql` 中的 SQL 语句创建必要的表和存储桶。

### 4. 启动服务

```bash
# 本地开发
python api_service.py

# 或使用 uvicorn
uvicorn api_service:app --host 0.0.0.0 --port 8000 --reload
```

服务启动后访问：
- API 文档：http://localhost:8000/docs
- 健康检查：http://localhost:8000/health

## API 使用

### POST 转换请求

```bash
curl -X POST "http://localhost:8000/api/convert" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://mp.weixin.qq.com/s/xxxxx",
    "download_media": true
  }'
```

### GET 转换请求（简化版）

```bash
curl "http://localhost:8000/api/convert?url=https://mp.weixin.qq.com/s/xxxxx&download_media=true"
```

### 响应示例

```json
{
  "success": true,
  "message": "转换成功",
  "data": {
    "md_url": "https://your-supabase-url/storage/v1/object/public/markdown-files/...",
    "md_filename": "article_title.md",
    "media_files": 5,
    "unique_id": "20231114_abc123"
  }
}
```

## Cloudflare Workers 部署

### 方案一：使用 Cloudflare Workers（推荐免费方案）

Cloudflare Workers 现在支持 Python，可以直接部署 FastAPI 应用。

#### 1. 安装 Wrangler CLI

```bash
npm install -g wrangler
# 或
brew install wrangler
```

#### 2. 登录 Cloudflare

```bash
wrangler login
```

#### 3. 配置环境变量

在 Cloudflare Dashboard 中设置以下环境变量：
- `SUPABASE_URL`
- `SUPABASE_KEY`
- `SUPABASE_BUCKET`

或使用命令行：

```bash
wrangler secret put SUPABASE_URL
wrangler secret put SUPABASE_KEY
wrangler secret put SUPABASE_BUCKET
```

#### 4. 部署

```bash
wrangler deploy
```

### 方案二：使用 Cloudflare Pages Functions

如果 Workers 不支持某些依赖，可以使用 Cloudflare Pages + Functions 方案。

```bash
# 创建 pages 目录结构
mkdir -p functions
# 将 API 逻辑放入 functions 目录
# 使用 wrangler pages 命令部署
```

## 部署到其他平台

### Railway

```bash
railway up
```

确保在 Railway 中设置环境变量：
- `SUPABASE_URL`
- `SUPABASE_KEY`
- `SUPABASE_BUCKET`

### Vercel

```bash
vercel deploy
```

### 传统服务器

使用 systemd 或 supervisor 管理服务：

```bash
uvicorn api_service:app --host 0.0.0.0 --port 8000 --workers 4
```

## Supabase 配置

### 1. 创建项目

在 [Supabase](https://supabase.com) 创建新项目。

### 2. 执行初始化 SQL

在 SQL Editor 中执行 `supabase_init.sql` 内容。

### 3. 创建存储桶

在 Storage 中创建名为 `markdown-files` 的公开存储桶（或在环境变量中指定其他名称）。

### 4. 获取凭证

从 Project Settings > API 获取：
- Project URL (SUPABASE_URL)
- anon/public key (SUPABASE_KEY)

## 项目结构

```
html2md/
├── api_service.py          # FastAPI Web 服务
├── html2md.py              # 核心转换逻辑
├── requirements.txt        # Python 依赖
├── runtime.txt            # Python 版本
├── Procfile               # 进程配置
├── Dockerfile             # Docker 配置
├── wrangler.toml          # Cloudflare Workers 配置
├── supabase_init.sql      # Supabase 初始化脚本
├── setup_cloudflare.sh    # Cloudflare 部署脚本
├── setup_supabase.sh      # Supabase 配置脚本
├── start_api.sh           # 启动脚本
└── .env.example           # 环境变量示例
```

## 核心依赖

- **FastAPI**: 现代、快速的 Web 框架
- **Uvicorn**: ASGI 服务器
- **Supabase**: 后端即服务（存储 + 数据库）
- **BeautifulSoup4**: HTML 解析
- **html2text**: HTML 转 Markdown
- **Requests**: HTTP 客户端

## 注意事项

### 1. URL3 版本限制

项目使用 `urllib3<2.0` 以避免 HTTP/2 相关问题。如遇到网络错误，确保：

```bash
pip install 'urllib3<2.0'
```

### 2. Supabase 存储限制

免费版 Supabase 有存储限制（1GB），注意监控使用量。

### 3. Cloudflare Workers 限制

- CPU 时间限制（免费版 10ms，付费版 50ms）
- 内存限制（128MB）
- 请求大小限制（100MB）

如果遇到限制，考虑：
- 使用 Cloudflare Pages Functions（更宽松的限制）
- 部署到 Railway、Vercel 或传统服务器

### 4. 媒体文件下载

下载大量媒体文件可能较慢，可以：
- 设置 `download_media=false` 只转换文本
- 使用异步处理（通过 `callback_url` 参数）

## 开发

### 本地测试

```bash
# 启动服务
python api_service.py

# 测试 API
curl http://localhost:8000/health
curl "http://localhost:8000/api/convert?url=https://mp.weixin.qq.com/s/xxxxx"
```

### Docker

```bash
# 构建镜像
docker build -t html2md-api .

# 运行容器
docker run -p 8000:8000 \
  -e SUPABASE_URL=xxx \
  -e SUPABASE_KEY=xxx \
  -e SUPABASE_BUCKET=markdown-files \
  html2md-api
```

## License

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！
