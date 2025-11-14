# API 使用指南

## API 概述

HTML2MD Web API 提供简单的 RESTful 接口，将网页 URL 转换为 Markdown 格式并存储到 Supabase。

**Base URL**: `https://your-api-domain.com`

---

## 认证

目前 API 为公开访问。如需添加认证，请参考部署文档中的安全建议。

---

## API 端点

### 1. 健康检查

检查服务状态。

```http
GET /health
```

**响应示例:**

```json
{
  "status": "healthy",
  "supabase": "connected",
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

---

### 2. 转换 URL (POST)

将网页 URL 转换为 Markdown 格式。

```http
POST /api/convert
Content-Type: application/json
```

**请求体:**

```json
{
  "url": "https://mp.weixin.qq.com/s/xxxxx",
  "download_media": true,
  "callback_url": "https://your-callback.com/webhook" // 可选
}
```

**参数说明:**

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| url | string | 是 | 要转换的网页 URL |
| download_media | boolean | 否 | 是否下载媒体资源，默认 true |
| callback_url | string | 否 | 转换完成后的回调 URL（暂未实现） |

**成功响应 (200):**

```json
{
  "success": true,
  "message": "转换成功",
  "data": {
    "md_url": "https://xxxxx.supabase.co/storage/v1/object/public/markdown-files/20240115_abc123/article.md",
    "md_filename": "文章标题.md",
    "media_files": 5,
    "unique_id": "20240115_123456_abc123"
  }
}
```

**错误响应 (500):**

```json
{
  "detail": "转换失败: 无法获取网页内容"
}
```

---

### 3. 转换 URL (GET)

简化版的 GET 请求，方便测试。

```http
GET /api/convert?url=https://example.com&download_media=true
```

**查询参数:**

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| url | string | 是 | 要转换的网页 URL |
| download_media | boolean | 否 | 是否下载媒体资源 |

**响应格式:** 与 POST 方法相同

---

## 使用示例

### cURL

```bash
# POST 请求
curl -X POST "https://your-api.com/api/convert" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://mp.weixin.qq.com/s/xxxxx",
    "download_media": true
  }'

# GET 请求
curl "https://your-api.com/api/convert?url=https://mp.weixin.qq.com/s/xxxxx&download_media=true"
```

### Python

```python
import requests

# 使用 requests 库
def convert_to_markdown(url, download_media=True):
    api_url = "https://your-api.com/api/convert"

    response = requests.post(
        api_url,
        json={
            "url": url,
            "download_media": download_media
        },
        timeout=300  # 5分钟超时
    )

    response.raise_for_status()
    result = response.json()

    if result['success']:
        return result['data']['md_url']
    else:
        raise Exception(result['message'])

# 使用示例
try:
    md_url = convert_to_markdown("https://mp.weixin.qq.com/s/xxxxx")
    print(f"转换成功！MD 文件: {md_url}")
except Exception as e:
    print(f"转换失败: {e}")
```

### JavaScript / TypeScript

```javascript
async function convertToMarkdown(url, downloadMedia = true) {
  const apiUrl = 'https://your-api.com/api/convert';

  try {
    const response = await fetch(apiUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        url: url,
        download_media: downloadMedia
      })
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const result = await response.json();

    if (result.success) {
      return result.data.md_url;
    } else {
      throw new Error(result.message);
    }
  } catch (error) {
    console.error('转换失败:', error);
    throw error;
  }
}

// 使用示例
convertToMarkdown('https://mp.weixin.qq.com/s/xxxxx')
  .then(mdUrl => console.log('转换成功！MD 文件:', mdUrl))
  .catch(error => console.error('转换失败:', error));
```

### PHP

```php
<?php
function convertToMarkdown($url, $downloadMedia = true) {
    $apiUrl = 'https://your-api.com/api/convert';

    $data = [
        'url' => $url,
        'download_media' => $downloadMedia
    ];

    $options = [
        'http' => [
            'method' => 'POST',
            'header' => 'Content-Type: application/json',
            'content' => json_encode($data),
            'timeout' => 300
        ]
    ];

    $context = stream_context_create($options);
    $response = file_get_contents($apiUrl, false, $context);

    if ($response === false) {
        throw new Exception('请求失败');
    }

    $result = json_decode($response, true);

    if ($result['success']) {
        return $result['data']['md_url'];
    } else {
        throw new Exception($result['message']);
    }
}

// 使用示例
try {
    $mdUrl = convertToMarkdown('https://mp.weixin.qq.com/s/xxxxx');
    echo "转换成功！MD 文件: $mdUrl\n";
} catch (Exception $e) {
    echo "转换失败: " . $e->getMessage() . "\n";
}
?>
```

---

## 飞书多维表格集成

### 方案一：使用飞书自动化（推荐）

1. 在飞书多维表格中创建字段：
   - `URL` (文本)
   - `状态` (单选: 待处理/处理中/已完成/失败)
   - `MD路径` (URL)
   - `错误信息` (文本)

2. 创建自动化规则：
   - 触发条件：当 URL 字段不为空且状态为"待处理"
   - 动作：调用 Webhook

3. Webhook 配置：
   ```
   URL: https://your-api.com/api/convert
   Method: GET
   参数: url={{URL字段}}
   ```

### 方案二：使用飞书机器人

创建飞书机器人命令：

```
/convert [URL]
```

机器人调用 API 并回复结果。

### 方案三：定时脚本

使用提供的 `feishu_webhook.py` 脚本定时扫描表格：

```bash
python feishu_webhook.py
```

---

## 响应字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| success | boolean | 是否成功 |
| message | string | 响应消息 |
| data.md_url | string | Markdown 文件的公开访问 URL |
| data.md_filename | string | Markdown 文件名 |
| data.media_files | integer | 下载的媒体文件数量 |
| data.unique_id | string | 本次转换的唯一标识 |

---

## 支持的平台

| 平台 | 支持程度 | 说明 |
|------|----------|------|
| 微信公众号 | ⭐⭐⭐⭐⭐ | 完美支持 |
| 知乎 | ⭐⭐⭐ | 基础支持 |
| 掘金 | ⭐⭐⭐⭐ | 较好支持 |
| CSDN | ⭐⭐⭐⭐ | 较好支持 |
| 其他网站 | ⭐⭐ | 通用解析 |

---

## 速率限制

目前未实施速率限制。建议在生产环境中添加：

- 每 IP 每分钟最多 10 个请求
- 每 API Key 每天最多 1000 个请求

---

## 错误代码

| HTTP 状态码 | 说明 |
|------------|------|
| 200 | 成功 |
| 400 | 请求参数错误 |
| 422 | 数据验证失败 |
| 500 | 服务器内部错误 |
| 503 | 服务不可用 |

---

## 最佳实践

1. **设置合理的超时时间**: 建议至少 60 秒，复杂页面可能需要更长时间
2. **错误处理**: 始终检查响应的 `success` 字段
3. **下载媒体**: 对于微信公众号文章，建议开启 `download_media`
4. **缓存结果**: 对于同一 URL，可以缓存转换结果
5. **异步处理**: 对于批量转换，建议使用队列异步处理

---

## 交互式 API 文档

部署后访问 `/docs` 查看 Swagger UI 交互式文档：

```
https://your-api.com/docs
```

---

## 示例项目

查看 GitHub 仓库中的 `examples/` 目录获取更多示例代码。

---

## 技术支持

- GitHub Issues: [项目地址]
- 邮箱: support@example.com
