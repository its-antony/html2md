#!/usr/bin/env python3
"""
HTML2Markdown - Gradio GUI版本
最简单的图形界面实现
"""

import gradio as gr
from html2md import HTML2Markdown, PlatformDetector
import os
from pathlib import Path


def convert_url(url, download_media, output_dir):
    """转换URL为Markdown"""
    if not url or not url.strip():
        return "❌ 请输入URL", "", [], "", ""

    try:
        # 检测平台
        platform = PlatformDetector.detect(url)
        platform_name = PlatformDetector.get_platform_name(platform)

        # 创建转换器
        converter = HTML2Markdown(download_media=download_media)

        # 转换
        output_path = converter.convert(url, output_path=None, output_dir=output_dir)

        # 读取生成的Markdown
        with open(output_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 统计信息
        lines = len(content.split('\n'))
        chars = len(content)

        # 收集下载的图片
        image_files = []
        if download_media:
            # 查找与输出文件同名的_files目录
            base_name = output_path.replace('.md', '')
            media_folder = f"{base_name}_files"
            if os.path.exists(media_folder):
                # 查找所有图片文件
                for file in Path(media_folder).glob('*'):
                    if file.suffix.lower() in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
                        image_files.append(str(file))

        success_msg = f"""
✅ 转换成功！

📊 统计信息：
- 平台：{platform_name}
- 文件：{output_path}
- 行数：{lines}
- 字符数：{chars}
- 图片数：{len(image_files)}

💡 提示：点击右侧标签页查看不同内容
        """

        return success_msg, output_path, image_files, content, content

    except Exception as e:
        error_msg = f"❌ 转换失败：{str(e)}"
        return error_msg, "", [], "", ""


# 创建Gradio界面
with gr.Blocks(title="HTML转Markdown工具", theme=gr.themes.Soft()) as app:
    gr.Markdown("""
    # 🎯 HTML转Markdown工具

    支持：微信公众号、知乎、掘金、CSDN等平台
    """)

    with gr.Row():
        with gr.Column(scale=1):
            url_input = gr.Textbox(
                label="📝 文章URL",
                placeholder="https://mp.weixin.qq.com/s/xxxxx",
                lines=2
            )

            with gr.Row():
                download_checkbox = gr.Checkbox(
                    label="📥 下载图片",
                    value=True
                )
                output_dir_input = gr.Textbox(
                    label="📁 输出目录",
                    value="output",
                    scale=2
                )

            convert_btn = gr.Button("🚀 开始转换", variant="primary", size="lg")

            status_output = gr.Textbox(
                label="📊 转换状态",
                lines=12,
                max_lines=15,
                interactive=False
            )

        with gr.Column(scale=2):
            file_path_output = gr.Textbox(
                label="💾 保存路径",
                interactive=False
            )

            # 使用标签页组织内容
            with gr.Tabs() as tabs:
                with gr.Tab("📄 Markdown预览"):
                    with gr.Column():
                        markdown_output = gr.Markdown(
                            value="转换完成后将在此显示Markdown内容",
                            height=500
                        )

                with gr.Tab("🖼️ 图片预览"):
                    with gr.Column():
                        image_gallery = gr.Gallery(
                            columns=3,
                            height=500,
                            object_fit="contain"
                        )

                with gr.Tab("📝 原始文本"):
                    with gr.Column():
                        raw_text_output = gr.Textbox(
                            lines=25,
                            max_lines=25,
                            interactive=False,
                            show_copy_button=True,
                            container=True
                        )

    # 示例
    gr.Examples(
        examples=[
            ["https://mp.weixin.qq.com/s/zbsqwm98QLK4uKH3A186ZQ", True, "output"],
            ["https://mp.weixin.qq.com/s/7B0ow_nCapf1Rhd5kiOPbA", True, "output"],
        ],
        inputs=[url_input, download_checkbox, output_dir_input],
    )

    # 使用说明
    with gr.Accordion("📖 使用说明", open=False):
        gr.Markdown("""
        ### 支持的平台
        - ✅ 微信公众号 (mp.weixin.qq.com) - 完美支持
        - ✅ 知乎 (zhihu.com) - 基础支持
        - ✅ 掘金 (juejin.cn) - 较好支持
        - ✅ CSDN (csdn.net) - 较好支持

        ### 使用步骤
        1. 复制文章URL
        2. 粘贴到输入框
        3. 选择是否下载图片
        4. 点击"开始转换"
        5. 等待完成，查看结果

        ### 注意事项
        - 微信公众号建议勾选"下载图片"，避免链接失效
        - 输出文件默认保存在 `output` 目录
        - **图片预览**：勾选"下载图片"后，下载的图片会显示在底部画廊中
        - **完整渲染**：Markdown文件需要用本地编辑器（如Typora、Obsidian）查看完整效果
        - 部分平台可能需要登录才能访问
        """)

    # 绑定事件
    convert_btn.click(
        fn=convert_url,
        inputs=[url_input, download_checkbox, output_dir_input],
        outputs=[status_output, file_path_output, image_gallery, markdown_output, raw_text_output]
    )

if __name__ == "__main__":
    print("🚀 启动HTML转Markdown工具...")
    print("📱 浏览器将自动打开")
    print("⏹️  按 Ctrl+C 退出")
    app.launch(
        server_name="127.0.0.1",
        server_port=7860,
        share=False,
        inbrowser=True
    )
