#!/usr/bin/env python3
"""
HTML2Markdown - Tkinter GUI版本
使用Python标准库，无需额外依赖
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
from html2md import HTML2Markdown, PlatformDetector


class HTML2MarkdownGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("HTML转Markdown工具")
        self.root.geometry("900x700")

        # 创建界面
        self.create_widgets()

    def create_widgets(self):
        # 标题
        title_frame = ttk.Frame(self.root, padding="10")
        title_frame.pack(fill=tk.X)

        title_label = ttk.Label(
            title_frame,
            text="🎯 HTML转Markdown工具",
            font=("Arial", 18, "bold")
        )
        title_label.pack()

        subtitle_label = ttk.Label(
            title_frame,
            text="支持：微信公众号、知乎、掘金、CSDN等",
            font=("Arial", 10)
        )
        subtitle_label.pack()

        # 主内容区
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # URL输入
        url_frame = ttk.LabelFrame(main_frame, text="📝 文章URL", padding="10")
        url_frame.pack(fill=tk.X, pady=(0, 10))

        self.url_entry = ttk.Entry(url_frame, font=("Arial", 11))
        self.url_entry.pack(fill=tk.X, pady=5)
        self.url_entry.insert(0, "https://mp.weixin.qq.com/s/xxxxx")

        # 选项
        options_frame = ttk.LabelFrame(main_frame, text="⚙️ 选项", padding="10")
        options_frame.pack(fill=tk.X, pady=(0, 10))

        # 下载选项
        self.download_var = tk.BooleanVar(value=True)
        download_check = ttk.Checkbutton(
            options_frame,
            text="📥 下载图片和视频到本地",
            variable=self.download_var
        )
        download_check.pack(anchor=tk.W, pady=2)

        # 输出目录
        output_frame = ttk.Frame(options_frame)
        output_frame.pack(fill=tk.X, pady=5)

        ttk.Label(output_frame, text="📁 输出目录:").pack(side=tk.LEFT, padx=(0, 5))

        self.output_dir_entry = ttk.Entry(output_frame, width=30)
        self.output_dir_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.output_dir_entry.insert(0, "output")

        ttk.Button(
            output_frame,
            text="浏览...",
            command=self.browse_directory,
            width=8
        ).pack(side=tk.LEFT)

        # 转换按钮
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))

        self.convert_btn = ttk.Button(
            button_frame,
            text="🚀 开始转换",
            command=self.start_conversion
        )
        self.convert_btn.pack(fill=tk.X)

        # 状态显示
        status_frame = ttk.LabelFrame(main_frame, text="📊 状态", padding="10")
        status_frame.pack(fill=tk.BOTH, expand=True)

        self.status_text = scrolledtext.ScrolledText(
            status_frame,
            height=15,
            font=("Courier", 10),
            wrap=tk.WORD
        )
        self.status_text.pack(fill=tk.BOTH, expand=True)

        # 进度条
        self.progress = ttk.Progressbar(
            main_frame,
            mode='indeterminate'
        )
        self.progress.pack(fill=tk.X, pady=(5, 0))

    def browse_directory(self):
        """选择输出目录"""
        directory = filedialog.askdirectory(
            title="选择输出目录",
            initialdir=self.output_dir_entry.get()
        )
        if directory:
            self.output_dir_entry.delete(0, tk.END)
            self.output_dir_entry.insert(0, directory)

    def log(self, message):
        """添加日志"""
        self.status_text.insert(tk.END, message + "\n")
        self.status_text.see(tk.END)
        self.root.update()

    def start_conversion(self):
        """开始转换（在新线程中）"""
        url = self.url_entry.get().strip()

        if not url:
            messagebox.showwarning("警告", "请输入URL")
            return

        # 禁用按钮
        self.convert_btn.config(state=tk.DISABLED)
        self.progress.start()

        # 清空日志
        self.status_text.delete(1.0, tk.END)

        # 在新线程中执行转换
        thread = threading.Thread(
            target=self.convert_url,
            args=(url,),
            daemon=True
        )
        thread.start()

    def convert_url(self, url):
        """执行转换"""
        try:
            # 获取选项
            download_media = self.download_var.get()
            output_dir = self.output_dir_entry.get()

            # 检测平台
            platform = PlatformDetector.detect(url)
            platform_name = PlatformDetector.get_platform_name(platform)

            self.log(f"🌐 正在获取网页: {url}")
            self.log(f"🔍 检测到平台: {platform_name}")

            # 创建转换器（劫持print输出）
            import sys
            from io import StringIO

            # 重定向stdout
            old_stdout = sys.stdout
            sys.stdout = StringIO()

            try:
                converter = HTML2Markdown(download_media=download_media)
                output_path = converter.convert(url, output_path=None, output_dir=output_dir)

                # 获取输出
                output = sys.stdout.getvalue()
                for line in output.split('\n'):
                    if line.strip():
                        self.log(line)

            finally:
                sys.stdout = old_stdout

            # 读取生成的文件
            with open(output_path, 'r', encoding='utf-8') as f:
                content = f.read()

            lines = len(content.split('\n'))
            chars = len(content)

            self.log("\n" + "="*50)
            self.log("✅ 转换成功！")
            self.log(f"📄 文件: {output_path}")
            self.log(f"📊 行数: {lines}")
            self.log(f"📊 字符数: {chars}")
            self.log("="*50)

            # 显示成功消息
            self.root.after(0, lambda: messagebox.showinfo(
                "成功",
                f"转换完成！\n\n文件已保存到:\n{output_path}"
            ))

        except Exception as e:
            self.log(f"\n❌ 错误: {str(e)}")
            self.root.after(0, lambda: messagebox.showerror(
                "错误",
                f"转换失败：\n{str(e)}"
            ))

        finally:
            # 恢复按钮和停止进度条
            self.root.after(0, lambda: self.convert_btn.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.progress.stop())


def main():
    root = tk.Tk()
    app = HTML2MarkdownGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
