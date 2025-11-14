# HTML2MD Web API 服务

将你的 HTML 转 Markdown 工具升级为 Web API 服务，可以部署到云平台并与飞书多维表格等工具集成。

## ✨ 新特性

- 🌐 **RESTful API** - 标准的 Web API，任何语言都能调用
- ☁️ **云端部署** - 部署到 Railway/Render/Cloudflare
- 💾 **永久存储** - 使用 Supabase 存储 Markdown 文件
- 🔗 **公开访问** - 生成可分享的文件链接
- 📊 **飞书集成** - 轻松与飞书多维表格集成
- 🚀 **全球加速** - 通过 CDN 加速访问
- 📖 **自动文档** - 内置 Swagger UI 交互式文档

## 🏗️ 架构

```
┌──────────────┐
│   客户端      │  (飞书/浏览器/脚本)
└──────┬───────┘
       │ HTTPS
       ↓
┌──────────────┐
│  Web API     │  (FastAPI + Uvicorn)
└──────┬───────┘
       │
       ├─→ HTML 抓取 & 转换
       │
       └─→ ┌────────────┐
           │  Supabase  │
           │  Storage   │  (文件存储 + 数据库)
           └────────────┘
```

## 🚀 快速开始

### 1. 配置 Supabase

1. 访问 [supabase.com](https://supabase.com) 创建项目
2. 获取项目 URL 和 API Key
3. 创建存储桶（或由脚本自动创建）

### 2. 本地运行

```bash
# 克隆项目
git clone <your-repo>
cd html2md

# 配置环境变量
cp .env.example .env
# 编辑 .env，填入 Supabase 配置

# 启动服务（自动安装依赖）
./start_api.sh

# 或手动启动
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn api_service:app --reload
```

访问 http://localhost:8000/docs 查看 API 文档

### 3. 测试 API

```bash
# 使用测试脚本
python test_api.py "https://mp.weixin.qq.com/s/your-article"

# 或使用 curl
curl "http://localhost:8000/api/convert?url=https://example.com"
```

## 📦 部署到云平台

### Railway (推荐)

```bash
# 1. 推送代码到 GitHub

# 2. 访问 railway.app

# 3. 连接 GitHub 仓库

# 4. 配置环境变量:
#    SUPABASE_URL
#    SUPABASE_KEY
#    SUPABASE_BUCKET

# 5. 自动部署完成！
```

详细部署指南: [DEPLOYMENT.md](DEPLOYMENT.md)

### Docker

```bash
# 构建
docker build -t html2md-api .

# 运行
docker run -p 8000:8000 \
  -e SUPABASE_URL=xxx \
  -e SUPABASE_KEY=xxx \
  html2md-api
```

## 🔌 API 使用

### 基本调用

```bash
# GET 方式（简单）
curl "https://your-api.com/api/convert?url=https://example.com"

# POST 方式（推荐）
curl -X POST "https://your-api.com/api/convert" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com", "download_media": true}'
```

### Python 调用

```python
import requests

response = requests.post(
    "https://your-api.com/api/convert",
    json={"url": "https://mp.weixin.qq.com/s/xxxxx"}
)

result = response.json()
md_url = result['data']['md_url']
print(f"Markdown: {md_url}")
```

### JavaScript 调用

```javascript
const response = await fetch('https://your-api.com/api/convert', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    url: 'https://mp.weixin.qq.com/s/xxxxx',
    download_media: true
  })
});

const result = await response.json();
console.log('MD文件:', result.data.md_url);
```

完整 API 文档: [API_USAGE.md](API_USAGE.md)

## 📊 飞书多维表格集成

### 方案 1: 飞书自动化（最简单）

1. 创建字段: `URL`, `状态`, `MD路径`
2. 设置自动化规则:
   - 触发: URL 字段更新
   - 动作: 调用 Webhook
   - URL: `https://your-api.com/api/convert?url={{URL}}`

### 方案 2: Webhook 服务

运行 `feishu_webhook.py` 监听飞书事件:

```bash
python feishu_webhook.py
```

### 方案 3: 定时任务

使用 Cron 定时扫描表格中的待处理记录。

## 📂 项目文件

```
html2md/
├── html2md.py              # 核心转换逻辑
├── api_service.py          # Web API 服务
├── feishu_webhook.py       # 飞书 Webhook 集成
├── requirements.txt        # Python 依赖
├── .env.example            # 环境变量示例
├── Dockerfile              # Docker 配置
├── wrangler.toml           # Cloudflare Workers 配置
├── start_api.sh            # 启动脚本
├── test_api.py             # 测试脚本
├── DEPLOYMENT.md           # 部署指南
├── API_USAGE.md            # API 使用文档
└── README_API.md           # 本文档
```

## 🌟 特性对比

| 功能 | 命令行工具 | Web API 服务 |
|------|-----------|-------------|
| 本地使用 | ✅ | ✅ |
| 远程调用 | ❌ | ✅ |
| 飞书集成 | 🔄 需要脚本 | ✅ 原生支持 |
| 文件存储 | 本地文件 | Supabase 云存储 |
| 分享链接 | ❌ | ✅ 公开 URL |
| 自动扩展 | ❌ | ✅ 云平台自动扩展 |
| 全球访问 | ❌ | ✅ CDN 加速 |

## 💡 使用场景

### 1. 个人知识库
- 将微信公众号文章保存到 Notion/Obsidian
- 通过飞书表格管理待读文章
- 自动转换并存档

### 2. 团队协作
- 团队成员共享文章链接
- 自动转换为统一格式
- 存储到共享空间

### 3. 内容分发
- 转换网页内容为 Markdown
- 通过 API 集成到 CMS
- 自动发布到多个平台

### 4. 数据采集
- 批量抓取文章列表
- 自动转换格式
- 存储到数据库

## 🔒 安全建议

- ✅ 使用 HTTPS (云平台自动配置)
- ✅ 配置 CORS 白名单
- ✅ 添加 API 密钥认证
- ✅ 实施速率限制
- ✅ 定期更新依赖

## 🐛 故障排查

### API 无法启动
- 检查 Python 版本 (需要 3.8+)
- 检查依赖是否安装完整
- 查看错误日志

### Supabase 连接失败
- 验证 URL 和 API Key
- 检查网络连接
- 确认存储桶已创建

### 转换超时
- 增加超时时间设置
- 检查目标网站是否可访问
- 考虑使用异步任务队列

## 📈 性能优化

- 使用 Redis 缓存转换结果
- 配置 CDN 加速静态资源
- 使用消息队列处理长任务
- 启用 gzip 压缩

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

---

## 下一步

1. ✅ 部署到云平台 → 查看 [DEPLOYMENT.md](DEPLOYMENT.md)
2. ✅ 集成飞书表格 → 使用 `feishu_webhook.py`
3. ✅ 查看 API 文档 → 访问 `/docs`
4. ✅ 开始使用 → 查看 [API_USAGE.md](API_USAGE.md)

**享受你的云端 Markdown 转换服务吧！** 🎉
