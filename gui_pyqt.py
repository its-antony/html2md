#!/usr/bin/env python3
"""
HTML2Markdown - PyQt6 GUI版本
专业的桌面应用界面
"""

import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTextEdit, QCheckBox,
    QFileDialog, QMessageBox, QProgressBar, QGroupBox, QTabWidget
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QIcon
from html2md import HTML2Markdown, PlatformDetector
import os


class ConversionThread(QThread):
    """转换线程"""
    log_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(bool, str, str)  # success, message, output_path

    def __init__(self, url, download_media, output_dir):
        super().__init__()
        self.url = url
        self.download_media = download_media
        self.output_dir = output_dir

    def run(self):
        """执行转换"""
        try:
            # 检测平台
            platform = PlatformDetector.detect(self.url)
            platform_name = PlatformDetector.get_platform_name(platform)

            self.log_signal.emit(f"🌐 正在获取网页: {self.url}")
            self.log_signal.emit(f"🔍 检测到平台: {platform_name}")

            # 创建转换器
            converter = HTML2Markdown(download_media=self.download_media)

            # 劫持print输出
            import sys
            from io import StringIO
            old_stdout = sys.stdout
            sys.stdout = StringIO()

            try:
                output_path = converter.convert(
                    self.url,
                    output_path=None,
                    output_dir=self.output_dir
                )

                # 获取输出
                output = sys.stdout.getvalue()
                for line in output.split('\n'):
                    if line.strip():
                        self.log_signal.emit(line)

            finally:
                sys.stdout = old_stdout

            # 读取文件统计
            with open(output_path, 'r', encoding='utf-8') as f:
                content = f.read()

            lines = len(content.split('\n'))
            chars = len(content)

            success_msg = f"""
✅ 转换成功！

📄 文件: {output_path}
📊 行数: {lines}
📊 字符数: {chars}
            """

            self.log_signal.emit("\n" + "="*50)
            self.log_signal.emit(success_msg)
            self.log_signal.emit("="*50)

            self.finished_signal.emit(True, success_msg, output_path)

        except Exception as e:
            error_msg = f"❌ 转换失败：{str(e)}"
            self.log_signal.emit(f"\n{error_msg}")
            self.finished_signal.emit(False, error_msg, "")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.conversion_thread = None
        self.init_ui()

    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle("HTML转Markdown工具")
        self.setGeometry(100, 100, 1000, 700)

        # 中央widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 主布局
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        # 标题
        title_label = QLabel("🎯 HTML转Markdown工具")
        title_font = QFont()
        title_font.setPointSize(20)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)

        subtitle_label = QLabel("支持：微信公众号、知乎、掘金、CSDN等")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(subtitle_label)

        # URL输入组
        url_group = QGroupBox("📝 文章URL")
        url_layout = QVBoxLayout()
        url_group.setLayout(url_layout)

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://mp.weixin.qq.com/s/xxxxx")
        self.url_input.setFont(QFont("Arial", 11))
        url_layout.addWidget(self.url_input)

        main_layout.addWidget(url_group)

        # 选项组
        options_group = QGroupBox("⚙️ 选项")
        options_layout = QVBoxLayout()
        options_group.setLayout(options_layout)

        # 下载选项
        self.download_checkbox = QCheckBox("📥 下载图片和视频到本地")
        self.download_checkbox.setChecked(True)
        options_layout.addWidget(self.download_checkbox)

        # 输出目录
        output_dir_layout = QHBoxLayout()
        output_dir_label = QLabel("📁 输出目录:")
        self.output_dir_input = QLineEdit("output")
        browse_btn = QPushButton("浏览...")
        browse_btn.clicked.connect(self.browse_directory)

        output_dir_layout.addWidget(output_dir_label)
        output_dir_layout.addWidget(self.output_dir_input)
        output_dir_layout.addWidget(browse_btn)

        options_layout.addLayout(output_dir_layout)

        main_layout.addWidget(options_group)

        # 转换按钮
        self.convert_btn = QPushButton("🚀 开始转换")
        self.convert_btn.setMinimumHeight(40)
        self.convert_btn.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.convert_btn.clicked.connect(self.start_conversion)
        main_layout.addWidget(self.convert_btn)

        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)

        # 标签页
        tabs = QTabWidget()

        # 状态标签页
        status_widget = QWidget()
        status_layout = QVBoxLayout()
        status_widget.setLayout(status_layout)

        self.status_text = QTextEdit()
        self.status_text.setReadOnly(True)
        self.status_text.setFont(QFont("Courier", 10))
        status_layout.addWidget(self.status_text)

        tabs.addTab(status_widget, "📊 状态日志")

        # 帮助标签页
        help_widget = QWidget()
        help_layout = QVBoxLayout()
        help_widget.setLayout(help_layout)

        help_text = QTextEdit()
        help_text.setReadOnly(True)
        help_text.setMarkdown("""
### 支持的平台

- ✅ **微信公众号** (mp.weixin.qq.com) - 完美支持
- ✅ **知乎** (zhihu.com) - 基础支持
- ✅ **掘金** (juejin.cn) - 较好支持
- ✅ **CSDN** (csdn.net) - 较好支持

### 使用步骤

1. 复制文章URL
2. 粘贴到输入框
3. 选择是否下载图片
4. 点击"开始转换"
5. 等待完成，查看结果

### 注意事项

- 微信公众号建议勾选"下载图片"，避免链接失效
- 输出文件默认保存在 `output` 目录
- 部分平台可能需要登录才能访问
        """)
        help_layout.addWidget(help_text)

        tabs.addTab(help_widget, "📖 使用说明")

        main_layout.addWidget(tabs)

        # 状态栏
        self.statusBar().showMessage("就绪")

    def browse_directory(self):
        """选择输出目录"""
        directory = QFileDialog.getExistingDirectory(
            self,
            "选择输出目录",
            self.output_dir_input.text()
        )
        if directory:
            self.output_dir_input.setText(directory)

    def log(self, message):
        """添加日志"""
        self.status_text.append(message)

    def start_conversion(self):
        """开始转换"""
        url = self.url_input.text().strip()

        if not url:
            QMessageBox.warning(self, "警告", "请输入URL")
            return

        # 禁用按钮，显示进度条
        self.convert_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # 不确定进度
        self.status_text.clear()
        self.statusBar().showMessage("正在转换...")

        # 创建并启动转换线程
        self.conversion_thread = ConversionThread(
            url,
            self.download_checkbox.isChecked(),
            self.output_dir_input.text()
        )

        # 连接信号
        self.conversion_thread.log_signal.connect(self.log)
        self.conversion_thread.finished_signal.connect(self.on_conversion_finished)

        # 启动线程
        self.conversion_thread.start()

    def on_conversion_finished(self, success, message, output_path):
        """转换完成"""
        # 恢复按钮，隐藏进度条
        self.convert_btn.setEnabled(True)
        self.progress_bar.setVisible(False)

        if success:
            self.statusBar().showMessage("转换成功！")
            QMessageBox.information(
                self,
                "成功",
                f"转换完成！\n\n文件已保存到:\n{output_path}"
            )
        else:
            self.statusBar().showMessage("转换失败")
            QMessageBox.critical(
                self,
                "错误",
                message
            )


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # 使用Fusion风格，跨平台一致
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
