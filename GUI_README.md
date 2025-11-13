# 图形界面版本使用指南

我们提供了**3种图形界面版本**，你可以根据需求选择：

## 🚀 快速开始

### 方式1: 自动安装（推荐）

```bash
chmod +x install_gui.sh
./install_gui.sh
```

然后选择要安装的GUI库。

### 方式2: 手动安装

```bash
# 激活虚拟环境
source venv/bin/activate

# 选择一个安装（或全部安装）
pip install gradio      # Gradio版本
pip install PyQt6       # PyQt6版本
# Tkinter无需安装（Python自带）
```

---

## 📱 三种界面对比

### 1. Gradio版本 ⭐⭐⭐⭐⭐ (推荐先试这个)

**特点：**
- ✅ 最简单、最快
- ✅ 界面现代美观
- ✅ 在浏览器中运行
- ✅ 自动生成UI

**运行：**
```bash
python gui_gradio.py
```

**效果：**
- 自动打开浏览器
- 地址：http://127.0.0.1:7860
- 支持实时预览

**截图：**
```
┌─────────────────────────────────────────┐
│  🎯 HTML转Markdown工具                  │
│  支持：微信公众号、知乎、掘金、CSDN等     │
├─────────────────────────────────────────┤
│  📝 文章URL                             │
│  ┌──────────────────────────────────┐  │
│  │ https://mp.weixin.qq.com/s/...  │  │
│  └──────────────────────────────────┘  │
│                                         │
│  ☑ 📥 下载图片和视频到本地              │
│  📁 输出目录: output                    │
│                                         │
│  ┌────────────────┐                    │
│  │ 🚀 开始转换     │                    │
│  └────────────────┘                    │
│                                         │
│  📊 转换状态    │  📄 Markdown预览      │
│  ✅ 转换成功！   │  # 文章标题...        │
│  文件：output... │                       │
└─────────────────────────────────────────┘
```

---

### 2. Tkinter版本 ⭐⭐⭐ (无需安装)

**特点：**
- ✅ 无需额外依赖
- ✅ Python标准库自带
- ✅ 真正的桌面应用
- ⚠️ 界面较简单

**运行：**
```bash
python gui_tkinter.py
```

**效果：**
- 独立的桌面窗口
- 原生macOS外观
- 适合简单使用

---

### 3. PyQt6版本 ⭐⭐⭐⭐⭐ (最专业)

**特点：**
- ✅ 最专业的界面
- ✅ 功能最完整
- ✅ 支持多标签页
- ✅ 真正的桌面应用
- ✅ 可以打包成.app

**运行：**
```bash
python gui_pyqt.py
```

**效果：**
- 专业的桌面应用
- 原生macOS风格
- 多标签页设计
- 支持拖拽等高级功能

---

## 🎨 界面功能

所有版本都包含：

### 基础功能
- ✅ URL输入框
- ✅ 下载图片选项
- ✅ 输出目录选择
- ✅ 开始转换按钮
- ✅ 状态显示
- ✅ 进度提示

### 高级功能（部分版本）
- 📊 实时日志显示
- 📄 Markdown预览（Gradio）
- 📖 帮助文档（PyQt6）
- 📁 文件浏览器
- 🔄 后台处理（不卡界面）

---

## 💻 使用演示

### 步骤1: 启动应用

```bash
# 选择一个版本运行
python gui_gradio.py    # Gradio
python gui_tkinter.py   # Tkinter
python gui_pyqt.py      # PyQt6
```

### 步骤2: 输入URL

复制微信公众号文章链接，粘贴到输入框

### 步骤3: 选择选项

- ☑ 勾选"下载图片"（推荐）
- 📁 确认输出目录

### 步骤4: 开始转换

点击"开始转换"按钮，等待完成

### 步骤5: 查看结果

- 转换完成后会显示成功消息
- 文件保存在output目录
- 可以直接打开查看

---

## 🎯 推荐选择

### 快速体验 → Gradio

```bash
pip install gradio
python gui_gradio.py
```

- 1分钟安装
- 界面最美观
- 最容易上手

### 无需安装 → Tkinter

```bash
python gui_tkinter.py
```

- 0安装成本
- 立即可用
- 适合临时使用

### 专业使用 → PyQt6

```bash
pip install PyQt6
python gui_pyqt.py
```

- 最专业
- 功能最全
- 可打包分发

---

## 📦 打包成.app文件

如果你想打包成独立的macOS应用：

### 使用PyQt6打包

```bash
# 1. 安装打包工具
pip install pyinstaller

# 2. 打包
pyinstaller --windowed \
  --name "HTML2Markdown" \
  --icon icon.icns \
  gui_pyqt.py

# 3. 输出
# dist/HTML2Markdown.app
```

打包后可以：
- 双击运行
- 分享给他人
- 放到应用程序文件夹

---

## ❓ 常见问题

### Q: 哪个版本最好？

A:
- **快速体验** → Gradio（最简单）
- **日常使用** → PyQt6（最专业）
- **零成本** → Tkinter（无需安装）

### Q: Gradio为什么在浏览器中？

A: Gradio使用Web技术，通过浏览器访问。虽然不是传统桌面应用，但界面更美观，开发更简单。

### Q: 可以打包成.app吗？

A: 可以！PyQt6版本可以用PyInstaller打包成独立的.app文件。

### Q: 需要学什么知识？

A:
- **使用**：不需要任何编程知识
- **修改**：基础Python（修改功能）
- **打包**：了解PyInstaller（创建.app）

---

## 🎉 快速测试

想快速体验？运行这个：

```bash
# 安装Gradio（最简单）
pip install gradio

# 运行
python gui_gradio.py

# 浏览器会自动打开
```

试试这个链接：
```
https://mp.weixin.qq.com/s/zbsqwm98QLK4uKH3A186ZQ
```

---

## 📚 更多文档

- [GUI_GUIDE.md](GUI_GUIDE.md) - 详细技术指南
- [README.md](README.md) - 完整使用说明
- [QUICKSTART.md](QUICKSTART.md) - 快速开始

---

**选择一个开始吧！** 🚀
