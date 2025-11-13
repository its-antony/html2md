# HTML转Markdown工具

一个强大的Python工具，用于将网页内容转换为Markdown格式，支持图片和视频资源的提取与下载。

## ✨ 功能特点

- 🎯 **统一入口** - 一个脚本支持多个平台
- 🤖 **自动识别** - 自动检测网站类型并使用对应的解析器
- 📝 **完美转换** - 自动提取标题、作者、发布时间
- 🖼️ **媒体下载** - 支持下载图片和视频到本地
- 📁 **智能管理** - 自动创建资源文件夹，使用相对路径
- 🔧 **易于扩展** - 模块化设计，方便添加新平台支持

## 🌐 支持的平台

| 平台 | 支持程度 | 说明 |
|------|----------|------|
| 微信公众号 | ⭐⭐⭐⭐⭐ | 完美支持，强烈推荐 |
| 知乎 | ⭐⭐⭐ | 基础支持，部分需登录 |
| 掘金 | ⭐⭐⭐⭐ | 较好支持 |
| CSDN | ⭐⭐⭐⭐ | 较好支持 |
| 其他网站 | ⭐⭐ | 通用解析，效果视网站而定 |

## 📦 安装依赖

```bash
pip install -r requirements.txt
```

或者单独安装：

```bash
pip install requests beautifulsoup4 html2text lxml
```

## 🚀 快速开始

### 基本使用

```bash
# 提取微信公众号文章（保留在线链接）
python html2md.py "https://mp.weixin.qq.com/s/xxxxx"

# 下载图片和视频到本地
python html2md.py "https://mp.weixin.qq.com/s/xxxxx" --download
```

### 其他平台

```bash
# 知乎文章
python html2md.py "https://zhuanlan.zhihu.com/p/xxxxx"

# 掘金文章
python html2md.py "https://juejin.cn/post/xxxxx"

# CSDN文章
python html2md.py "https://blog.csdn.net/xxx/article/details/xxxxx"
```

## 📖 使用说明

### 命令行参数

```bash
python html2md.py <URL> [选项]
```

**参数：**
- `URL` - 网页链接（必需）
- `-d, --download` - 下载图片和视频到本地
- `-o, --output` - 指定输出文件路径
- `--output-dir` - 指定输出目录（默认：output）

### 使用示例

```bash
# 示例1: 基本提取（保留在线链接，保存到output目录）
python html2md.py "https://mp.weixin.qq.com/s/xxxxxxxxxxxx"

# 示例2: 下载图片和视频到本地
python html2md.py "https://mp.weixin.qq.com/s/xxxxxxxxxxxx" --download

# 示例3: 指定输出文件名
python html2md.py "https://mp.weixin.qq.com/s/xxxxxxxxxxxx" -o my_article.md -d

# 示例4: 使用自定义输出目录
python html2md.py "https://zhuanlan.zhihu.com/p/xxxxx" --output-dir ./articles

# 示例5: 指定完整路径
python html2md.py "https://juejin.cn/post/xxxxx" -o ./docs/article.md -d
```

### 查看帮助

```bash
python html2md.py -h
```

## 📂 输出格式

### Markdown文件

生成的Markdown文件包含：

```markdown
# 文章标题

**作者:** 作者名
**来源:** 微信公众号
**原文链接:** https://...

---

文章正文内容...

![](图片链接或本地路径)
```

### 文件结构

默认保存到 `output` 目录：

```
output/
├── 文章标题.md              # Markdown文件
└── 文章标题_files/          # 媒体资源文件夹（使用--download时）
    ├── image_001.jpg        # 图片文件
    ├── image_002.jpg
    ├── ...
    └── video_001.mp4        # 视频文件
```

**注意：**
- 默认情况下，所有文件保存到 `output` 目录，保持工作目录整洁
- 图片路径使用相对路径（如：`文章标题_files/image_001.jpg`）
- 包含空格的路径会自动用 `<>` 包裹以确保正确显示

## 🏗️ 架构设计

### 模块化设计

```
html2md.py
├── PlatformDetector    - 平台检测器
├── BaseParser          - 解析器基类
├── WechatParser        - 微信公众号解析器
├── ZhihuParser         - 知乎解析器
├── JuejinParser        - 掘金解析器
├── CSDNParser          - CSDN解析器
├── GenericParser       - 通用解析器
└── HTML2Markdown       - 主转换类
```

### 工作流程

1. **平台检测** → 自动识别URL所属平台
2. **内容获取** → 发送HTTP请求获取HTML
3. **内容解析** → 使用对应的解析器提取内容
4. **媒体处理** → 提取图片/视频，可选下载
5. **格式转换** → HTML转Markdown
6. **文件保存** → 保存到指定位置

## 🔧 扩展支持新平台

如果需要支持新的网站，只需：

1. **创建新的解析器类**

```python
class NewSiteParser(BaseParser):
    def __init__(self):
        super().__init__()
        self.platform_name = '新网站'

    def parse(self, soup):
        # 实现解析逻辑
        title = soup.find('h1', class_='title').get_text()
        content = soup.find('div', class_='content')

        return {
            'title': title,
            'author': None,
            'content': content
        }
```

2. **注册解析器**

在 `PlatformDetector.detect()` 和 `HTML2Markdown.__init__()` 中添加：

```python
# 检测
if 'newsite.com' in url:
    return 'newsite'

# 注册
self.parsers = {
    ...
    'newsite': NewSiteParser()
}
```

## ⚠️ 注意事项

1. **网络连接** - 请确保网络连接正常
2. **访问限制** - 某些文章可能因为访问限制无法获取
3. **磁盘空间** - 使用 `--download` 时确保有足够的磁盘空间
4. **下载时间** - 图片和视频下载可能需要一些时间
5. **链接时效** - 微信公众号的在线图片链接可能有时效性，建议使用 `--download`
6. **法律法规** - 请遵守相关法律法规，仅用于个人学习和研究

## 📚 依赖项

- Python 3.6+
- requests - HTTP请求库
- beautifulsoup4 - HTML解析库
- html2text - HTML转Markdown库
- lxml - XML和HTML解析器

## ❓ 常见问题

### Q: 为什么有些文章无法提取？

A: 可能的原因：
- 文章已被删除
- 需要关注公众号才能查看
- 网络连接问题
- 微信公众号平台的访问限制

### Q: 图片无法显示？

A: 微信公众号的图片链接可能有时效性或访问限制。**建议使用 `--download` 参数将图片下载到本地**，这样可以确保图片永久可用。

```bash
python html2md.py "https://mp.weixin.qq.com/s/xxxxx" --download
```

### Q: 脚本能检测到媒体资源但没有下载？

A: 默认情况下，脚本只提取在线链接而不下载。需要添加 `--download` 或 `-d` 参数才会下载资源到本地。

### Q: 下载的图片和视频保存在哪里？

A: 资源会保存在与Markdown文件同名的文件夹中。例如，如果Markdown文件名为 `article.md`，资源会保存在 `article_files/` 文件夹中。

### Q: 如何批量下载多篇文章？

A: 可以创建一个包含多个URL的文本文件，然后使用shell脚本批量处理：

```bash
#!/bin/bash
while IFS= read -r url; do
    python html2md.py "$url" --download
done < urls.txt
```

### Q: 为什么知乎/小红书等平台提取效果不好？

A: 不同平台的HTML结构差异很大，某些平台还有以下限制：
- **需要登录** - 内容被登录墙拦截
- **反爬虫机制** - 检测到非浏览器访问
- **动态加载** - 内容由JavaScript生成
- **HTML结构变化** - 网站更新了页面结构

对于这些平台，建议使用浏览器插件（如MarkDownload）手动操作。

## 📜 更新日志

查看 [CHANGELOG.md](CHANGELOG.md) 了解详细的更新历史。

## 📄 许可证

MIT License

## 🙏 致谢

感谢所有开源项目的贡献者！

---

**推荐使用场景：**
- ✅ 微信公众号文章归档
- ✅ 技术博客内容保存
- ✅ 学习资料整理
- ✅ 离线阅读准备
