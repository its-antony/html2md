# Railway 网页部署指南

代码已推送到GitHub，现在可以通过Railway网页快速部署。

## 🚀 5分钟部署步骤

### 1. 访问 Railway

打开浏览器，访问：https://railway.app

点击右上角 **"Login"**，使用 **GitHub** 账号登录。

### 2. 创建新项目

登录后，点击 **"New Project"**

选择 **"Deploy from GitHub repo"**

### 3. 选择仓库

在仓库列表中找到：**`its-antony/html2md`**

> 如果看不到仓库，点击 "Configure GitHub App" 授权访问。

选择 **`web-service`** 分支

### 4. 配置环境变量

Railway会自动检测到Python项目。点击项目后，进入 **"Variables"** 标签页，添加以下环境变量：

| 变量名 | 值 |
|--------|-----|
| `SUPABASE_URL` | `https://fryabprsfurgcraytocu.supabase.co` |
| `SUPABASE_KEY` | `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZyeWFicHJzZnVyZ2NyYXl0b2N1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjMxMDA0MzcsImV4cCI6MjA3ODY3NjQzN30.joOfBmxaWMRhVGCE6RvGPpnWxpZlSJY4x2nB_gEUkWU` |
| `SUPABASE_BUCKET` | `markdown-files` |

### 5. 添加公开域名

点击 **"Settings"** 标签页

找到 **"Networking"** 部分

点击 **"Generate Domain"** 生成一个公开URL

格式类似：`html2md-api-production.up.railway.app`

### 6. 等待部署

Railway会自动：
- 安装依赖 (`pip install -r requirements.txt`)
- 启动服务 (`python api_service.py`)
- 分配公开URL

部署需要 2-3 分钟。

### 7. 测试部署

部署完成后，访问以下URL测试：

**健康检查**：
```
https://your-app.up.railway.app/health
```

**API 文档**：
```
https://your-app.up.railway.app/docs
```

**转换测试**：
```
https://your-app.up.railway.app/api/convert?url=https://mp.weixin.qq.com/s/7B0ow_nCapf1Rhd5kiOPbA&download_media=false
```

## 📊 监控和管理

### 查看日志
在Railway项目页面，点击 **"Deployments"** 标签，选择最新部署，可以看到实时日志。

### 查看指标
点击 **"Metrics"** 查看CPU、内存、网络使用情况。

### 重新部署
每次推送新代码到GitHub的 `web-service` 分支，Railway会自动重新部署。

## 💰 费用说明

Railway提供：
- **$5/月 免费额度**（足够个人使用）
- 超出部分按使用量计费
- 可以设置预算上限防止超支

## 🔧 故障排查

### 部署失败
1. 检查日志中的错误信息
2. 确认环境变量是否正确设置
3. 确认分支是 `web-service`

### 服务无法访问
1. 确认已生成公开域名
2. 检查部署状态是否为 "Active"
3. 查看日志确认服务是否正常启动

### 转换失败
1. 检查Supabase环境变量是否正确
2. 访问 `/health` 端点检查Supabase连接状态
3. 查看日志获取详细错误信息

## ✅ 完成！

部署成功后，你就拥有了一个公开可访问的HTML转Markdown API服务！

**GitHub仓库**: https://github.com/its-antony/html2md
**分支**: web-service
