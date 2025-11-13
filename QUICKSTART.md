# 快速开始指南

## 🚀 30秒上手

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 运行脚本

```bash
# 提取微信公众号文章
python html2md.py "https://mp.weixin.qq.com/s/xxxxx" --download
```

就这么简单！✨

---

## 📚 常用命令

### 微信公众号

```bash
# 只提取文本（保留在线图片链接）
python html2md.py "微信文章URL"

# 下载所有图片和视频到本地
python html2md.py "微信文章URL" --download
```

### 知乎文章

```bash
python html2md.py "https://zhuanlan.zhihu.com/p/xxxxx"
```

### 掘金文章

```bash
python html2md.py "https://juejin.cn/post/xxxxx"
```

### 自定义输出

```bash
# 指定文件名
python html2md.py "URL" -o my_article.md -d

# 指定输出目录
python html2md.py "URL" --output-dir ./articles -d
```

---

## 📂 输出位置

默认保存到 `output/` 目录：

```
output/
├── 文章标题.md
└── 文章标题_files/    # 使用 --download 时
    ├── image_001.jpg
    ├── image_002.jpg
    └── ...
```

---

## 💡 推荐用法

**微信公众号文章归档：**

```bash
python html2md.py "文章URL" --download
```

**原因：**
- ✅ 图片永久保存，不担心链接失效
- ✅ 可以离线阅读
- ✅ 完整保留文章内容

---

## ❓ 遇到问题？

查看完整文档：
- [README.md](README.md) - 完整使用说明
- [PLATFORM_GUIDE.md](PLATFORM_GUIDE.md) - 各平台支持详情
- [CHANGELOG.md](CHANGELOG.md) - 更新日志

或运行：

```bash
python html2md.py -h
```

---

## 📝 批量处理

创建 `urls.txt` 文件，每行一个URL：

```
https://mp.weixin.qq.com/s/xxxxx1
https://mp.weixin.qq.com/s/xxxxx2
https://mp.weixin.qq.com/s/xxxxx3
```

然后运行：

```bash
while IFS= read -r url; do
    python html2md.py "$url" --download
done < urls.txt
```

---

**享受使用吧！🎉**
