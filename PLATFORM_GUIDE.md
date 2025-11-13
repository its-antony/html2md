# 多平台支持指南

## 原理说明

网页转Markdown的核心原理：

1. **HTTP请求** → 获取网页HTML源码
2. **HTML解析** → 使用CSS选择器定位内容
3. **内容提取** → 提取标题、作者、正文等
4. **格式转换** → 将HTML转换为Markdown

## 为什么不同网站需要不同的解析规则？

每个网站的HTML结构都不同，例如：

**微信公众号：**
```html
<h1 class="rich_media_title">标题</h1>
<div id="js_content">正文内容</div>
```

**知乎：**
```html
<h1 class="Post-Title">标题</h1>
<div class="RichContent-inner">正文内容</div>
```

**掘金：**
```html
<h1 class="article-title">标题</h1>
<article class="article-content">正文内容</article>
```

## 支持的平台

### ✅ 微信公众号 (mp.weixin.qq.com)

**支持程度：** 完美支持 ⭐⭐⭐⭐⭐

**特点：**
- 固定的HTML结构
- 无需登录
- 图片使用懒加载（data-src）

**使用示例：**
```bash
python wechat_to_md.py "https://mp.weixin.qq.com/s/xxxxx" --download
```

### ✅ 知乎 (zhihu.com)

**支持程度：** 基础支持 ⭐⭐⭐

**限制：**
- 部分内容需要登录才能查看
- 动态加载的内容可能无法获取
- 可能遇到反爬虫限制

**使用示例：**
```bash
python web_to_md.py "https://zhuanlan.zhihu.com/p/xxxxx"
```

### ⚠️ 小红书 (xiaohongshu.com)

**支持程度：** 困难 ⭐

**主要障碍：**
1. **强反爬虫机制**
   - 需要登录才能查看完整内容
   - 有滑块验证、设备指纹等

2. **动态渲染**
   - 内容通过JavaScript动态加载
   - 需要使用浏览器自动化工具（Selenium/Playwright）

3. **加密内容**
   - API返回的数据经过加密
   - 需要逆向分析解密算法

**解决方案：**
- 使用浏览器插件手动复制内容
- 或使用浏览器自动化工具（更复杂）

### ✅ 掘金 (juejin.cn)

**支持程度：** 较好支持 ⭐⭐⭐⭐

**特点：**
- Markdown内容存储
- HTML结构清晰
- 无需登录

**使用示例：**
```bash
python web_to_md.py "https://juejin.cn/post/xxxxx"
```

### ✅ CSDN (csdn.net)

**支持程度：** 较好支持 ⭐⭐⭐⭐

**特点：**
- 技术博客平台
- HTML结构清晰
- 可能有部分广告内容

**使用示例：**
```bash
python web_to_md.py "https://blog.csdn.net/xxx/article/details/xxxxx"
```

## 如何适配新的网站？

### 步骤1: 查看网页源代码

在浏览器中按 `F12` 打开开发者工具，找到：

1. **标题** 的HTML标签和class/id
2. **作者** 的HTML标签和class/id
3. **正文内容** 的HTML标签和class/id

### 步骤2: 编写解析函数

```python
def parse_新网站(self, soup):
    """解析新网站文章"""
    # 提取标题
    title = None
    title_tag = soup.find('h1', class_='网站的标题class')
    if title_tag:
        title = title_tag.get_text().strip()

    # 提取作者
    author = None
    author_tag = soup.find('span', class_='网站的作者class')
    if author_tag:
        author = author_tag.get_text().strip()

    # 提取正文
    content = soup.find('div', class_='网站的内容class')

    return {
        'title': title,
        'author': author,
        'content': content,
        'platform': '新网站名称'
    }
```

### 步骤3: 注册解析器

```python
def detect_platform(self, url):
    if '新网站.com' in url:
        return '新网站'
    # ... 其他网站

def parse_page(self, html_content, platform):
    parse_methods = {
        '新网站': self.parse_新网站,
        # ... 其他网站
    }
```

## 常见问题

### Q1: 为什么有些网站转换失败？

**可能的原因：**

1. **需要登录** - 内容被登录墙拦截
2. **反爬虫机制** - 网站检测到非浏览器访问
3. **动态加载** - 内容由JavaScript生成
4. **HTML结构变化** - 网站更新了页面结构

**解决方案：**

- 使用浏览器的"复制为Markdown"插件
- 使用浏览器自动化工具（Selenium/Playwright）
- 添加Cookie/Token进行身份验证

### Q2: 如何处理需要登录的网站？

**方法1: 手动添加Cookie**

```python
self.headers = {
    'User-Agent': '...',
    'Cookie': '你的登录Cookie'  # 从浏览器复制
}
```

**方法2: 使用浏览器自动化**

需要安装额外的库：
```bash
pip install selenium
pip install webdriver-manager
```

### Q3: 如何处理JavaScript动态加载的内容？

**简单脚本无法处理**，需要：

1. 使用 **Selenium** 或 **Playwright** 模拟浏览器
2. 等待JavaScript执行完成
3. 再获取完整的DOM

示例：
```python
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

driver = webdriver.Chrome()
driver.get(url)
# 等待内容加载
WebDriverWait(driver, 10).until(...)
html = driver.page_source
```

### Q4: 小红书为什么这么难抓取？

小红书的反爬虫策略包括：

1. **设备指纹** - 识别设备特征
2. **滑块验证** - 人机验证
3. **加密签名** - API请求需要签名
4. **动态渲染** - 内容由React/Vue生成
5. **频率限制** - IP访问频率限制

**实际建议：**
- 对于个人使用，建议手动复制内容
- 或使用浏览器插件（如MarkDownload）
- 避免大规模自动化爬取（可能违反服务条款）

## 推荐的浏览器插件

如果网站难以通过脚本抓取，可以使用这些插件：

1. **MarkDownload** - 将网页转换为Markdown
2. **Obsidian Web Clipper** - 保存网页到Obsidian
3. **Notion Web Clipper** - 保存到Notion

## 技术栈说明

- **requests** - HTTP请求
- **BeautifulSoup** - HTML解析
- **html2text** - HTML转Markdown
- **lxml** - 快速XML/HTML解析器

## 法律与道德说明

⚠️ **重要提醒：**

1. **尊重版权** - 仅用于个人学习和研究
2. **遵守robots.txt** - 尊重网站的爬虫协议
3. **控制频率** - 避免对服务器造成压力
4. **不要商用** - 未经授权不得商业使用内容
5. **遵守服务条款** - 某些网站明确禁止爬虫

## 总结

| 平台 | 难度 | 支持程度 | 限制 |
|------|------|----------|------|
| 微信公众号 | ⭐ | ✅ 完美 | 无 |
| 知乎 | ⭐⭐ | ✅ 较好 | 部分需登录 |
| 掘金 | ⭐⭐ | ✅ 较好 | 无 |
| CSDN | ⭐⭐ | ✅ 较好 | 广告内容 |
| 小红书 | ⭐⭐⭐⭐⭐ | ❌ 困难 | 强反爬虫 |
| 简书 | ⭐⭐ | ✅ 较好 | 部分需登录 |

**最佳实践：**
- 优先使用官方API（如果有）
- 其次使用本脚本
- 最后使用浏览器插件手动操作
