#!/usr/bin/env python3
"""
微信公众号文章转Markdown工具
提取微信公众号文章内容并保存为Markdown格式
支持图片和视频资源的提取与下载
"""

import re
import sys
import argparse
import requests
from bs4 import BeautifulSoup
import html2text
from pathlib import Path
from urllib.parse import urlparse, unquote, urljoin
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed


class WechatArticleExtractor:
    def __init__(self, download_media=False):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        }
        self.download_media = download_media
        self.media_folder = None
        self.media_map = {}  # 用于存储原始URL到本地路径的映射

    def fetch_article(self, url):
        """获取文章HTML内容"""
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            response.encoding = 'utf-8'
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"错误: 无法获取网页内容 - {e}")
            sys.exit(1)

    def extract_media(self, content_tag):
        """提取文章中的图片和视频URL"""
        media_list = []

        if not content_tag:
            return media_list

        # 提取图片
        for img in content_tag.find_all('img'):
            img_url = img.get('data-src') or img.get('src')
            if img_url and img_url.startswith('http'):
                media_list.append({
                    'type': 'image',
                    'url': img_url,
                    'tag': img
                })

        # 提取视频
        for video in content_tag.find_all(['video', 'iframe']):
            video_url = video.get('data-src') or video.get('src')
            if video_url and video_url.startswith('http'):
                media_list.append({
                    'type': 'video',
                    'url': video_url,
                    'tag': video
                })

        return media_list

    def download_file(self, url, save_path):
        """下载单个文件"""
        try:
            response = requests.get(url, headers=self.headers, timeout=30, stream=True)
            response.raise_for_status()

            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            return True
        except Exception as e:
            print(f"  警告: 下载失败 {url} - {e}")
            return False

    def download_media_files(self, media_list, base_name):
        """批量下载媒体文件"""
        if not media_list:
            return

        # 创建媒体文件夹
        self.media_folder = f"{base_name}_files"
        Path(self.media_folder).mkdir(parents=True, exist_ok=True)

        # 提取文件夹的basename（用于相对路径）
        media_folder_name = os.path.basename(base_name) + "_files"

        print(f"\n开始下载媒体资源 (共 {len(media_list)} 个)...")

        downloaded = 0
        for idx, media in enumerate(media_list, 1):
            url = media['url']
            media_type = media['type']

            # 生成文件名
            ext = self.get_file_extension(url, media_type)
            filename = f"{media_type}_{idx:03d}{ext}"
            save_path = os.path.join(self.media_folder, filename)

            # 下载文件
            print(f"  [{idx}/{len(media_list)}] 下载 {media_type}: {filename}")
            if self.download_file(url, save_path):
                # 保存URL映射（使用相对路径）
                relative_path = os.path.join(media_folder_name, filename)
                self.media_map[url] = relative_path
                downloaded += 1
            else:
                # 如果下载失败，仍然使用原始URL
                self.media_map[url] = url

        print(f"✓ 下载完成: {downloaded}/{len(media_list)} 个文件")

    def get_file_extension(self, url, media_type):
        """获取文件扩展名"""
        parsed = urlparse(url)
        path = parsed.path

        # 尝试从URL中提取扩展名
        if '.' in path:
            ext = os.path.splitext(path)[1]
            if ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.mp4', '.mov', '.avi']:
                return ext

        # 根据类型返回默认扩展名
        if media_type == 'image':
            return '.jpg'
        elif media_type == 'video':
            return '.mp4'
        return ''

    def parse_article(self, html_content):
        """解析文章内容"""
        soup = BeautifulSoup(html_content, 'html.parser')

        # 提取标题
        title = None
        title_tag = soup.find('h1', class_='rich_media_title')
        if title_tag:
            title = title_tag.get_text().strip()

        # 提取作者
        author = None
        author_tag = soup.find('a', class_='rich_media_meta rich_media_meta_link rich_media_meta_nickname')
        if not author_tag:
            author_tag = soup.find('span', class_='rich_media_meta rich_media_meta_text')
        if author_tag:
            author = author_tag.get_text().strip()

        # 提取发布时间
        publish_time = None
        time_tag = soup.find('em', id='publish_time')
        if not time_tag:
            time_tag = soup.find('span', class_='rich_media_meta rich_media_meta_text')
        if time_tag:
            publish_time = time_tag.get_text().strip()

        # 提取正文内容
        content = None
        content_tag = soup.find('div', class_='rich_media_content')
        if not content_tag:
            content_tag = soup.find('div', id='js_content')

        if content_tag:
            # 移除不必要的标签
            for tag in content_tag.find_all(['script', 'style']):
                tag.decompose()

            content = content_tag

        return {
            'title': title,
            'author': author,
            'publish_time': publish_time,
            'content': content
        }

    def html_to_markdown(self, html_content, media_list):
        """将HTML转换为Markdown，并处理媒体资源"""
        if not html_content:
            return ""

        # 处理所有img标签：将data-src复制到src，以便html2text能够识别
        for img in html_content.find_all('img'):
            if img.get('data-src') and not img.get('src'):
                img['src'] = img['data-src']

        # 处理所有video/iframe标签
        for video in html_content.find_all(['video', 'iframe']):
            if video.get('data-src') and not video.get('src'):
                video['src'] = video['data-src']

        # 如果下载了媒体，替换HTML中的链接为本地路径
        if self.download_media and self.media_map:
            for media in media_list:
                url = media['url']
                tag = media['tag']
                if url in self.media_map:
                    local_path = self.media_map[url]
                    # 更新标签的src属性为本地路径
                    tag['src'] = local_path

        h = html2text.HTML2Text()
        h.ignore_links = False
        h.ignore_images = False
        h.ignore_emphasis = False
        h.body_width = 0  # 不自动换行
        h.unicode_snob = True
        h.skip_internal_links = True

        return h.handle(str(html_content))

    def clean_markdown(self, markdown_text):
        """清理Markdown文本"""
        # 移除多余的空行
        markdown_text = re.sub(r'\n{3,}', '\n\n', markdown_text)
        # 移除首尾空白
        markdown_text = markdown_text.strip()

        # 修复包含空格的图片和视频链接
        # 查找所有的 ![...](路径) 格式的链接
        def fix_image_path(match):
            alt_text = match.group(1)
            path = match.group(2)
            # 如果路径包含空格且不是以 < 开头（避免重复处理）
            if ' ' in path and not path.startswith('<'):
                return f'![{alt_text}](<{path}>)'
            return match.group(0)

        # 匹配 ![alt](path) 格式
        markdown_text = re.sub(r'!\[(.*?)\]\(([^)]+)\)', fix_image_path, markdown_text)

        return markdown_text

    def generate_filename(self, title, url):
        """生成文件名"""
        if title:
            # 移除不合法的文件名字符
            filename = re.sub(r'[<>:"/\\|?*]', '', title)
            filename = filename.strip()
            filename = filename[:100]  # 限制长度
        else:
            # 如果没有标题，使用URL生成
            parsed = urlparse(url)
            filename = f"wechat_article_{parsed.path.split('/')[-1]}"

        return f"{filename}.md"

    def save_markdown(self, content, filepath):
        """保存Markdown文件"""
        try:
            Path(filepath).write_text(content, encoding='utf-8')
            print(f"✓ 文章已保存到: {filepath}")
        except Exception as e:
            print(f"错误: 保存文件失败 - {e}")
            sys.exit(1)

    def extract(self, url, output_path=None, output_dir='output'):
        """主提取流程"""
        print(f"正在获取文章: {url}")

        # 1. 获取网页内容
        html_content = self.fetch_article(url)

        # 2. 解析文章
        article = self.parse_article(html_content)

        if not article['content']:
            print("错误: 未能找到文章内容")
            sys.exit(1)

        # 3. 提取媒体资源
        media_list = self.extract_media(article['content'])
        print(f"✓ 找到 {len(media_list)} 个媒体资源 (图片: {sum(1 for m in media_list if m['type'] == 'image')}, 视频: {sum(1 for m in media_list if m['type'] == 'video')})")

        # 4. 确定输出路径
        if not output_path:
            # 如果没有指定输出路径，使用output目录
            output_dir_path = Path(output_dir)
            output_dir_path.mkdir(exist_ok=True)
            output_path = output_dir_path / self.generate_filename(article['title'], url)
            output_path = str(output_path)
        else:
            # 如果指定了输出路径，确保目录存在
            output_path_obj = Path(output_path)
            output_path_obj.parent.mkdir(parents=True, exist_ok=True)

        # 5. 下载媒体资源（如果需要）
        if self.download_media and media_list:
            # 生成基础文件名
            base_name = os.path.splitext(output_path)[0]
            self.download_media_files(media_list, base_name)

        # 6. 构建Markdown内容
        markdown_parts = []

        # 添加标题
        if article['title']:
            markdown_parts.append(f"# {article['title']}\n")

        # 添加元信息
        metadata = []
        if article['author']:
            metadata.append(f"**作者:** {article['author']}")
        if article['publish_time']:
            metadata.append(f"**发布时间:** {article['publish_time']}")

        if metadata:
            markdown_parts.append("\n".join(metadata))
            markdown_parts.append("\n---\n")

        # 添加正文
        content_md = self.html_to_markdown(article['content'], media_list)
        content_md = self.clean_markdown(content_md)
        markdown_parts.append(content_md)

        final_markdown = "\n".join(markdown_parts)

        # 7. 保存文件
        self.save_markdown(final_markdown, output_path)

        return output_path


def main():
    parser = argparse.ArgumentParser(
        description='提取微信公众号文章并转换为Markdown格式，支持图片和视频资源下载',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 基本使用（保留在线链接，保存到output目录）
  %(prog)s https://mp.weixin.qq.com/s/xxxxx

  # 下载图片和视频到本地（保存到output目录）
  %(prog)s https://mp.weixin.qq.com/s/xxxxx --download

  # 指定输出文件路径
  %(prog)s https://mp.weixin.qq.com/s/xxxxx -o my_article.md --download

  # 指定输出目录
  %(prog)s https://mp.weixin.qq.com/s/xxxxx --output-dir ./articles -d
        """
    )

    parser.add_argument('url', help='微信公众号文章URL')
    parser.add_argument('-o', '--output', help='输出文件路径（可选，默认保存到output目录）')
    parser.add_argument('-d', '--download', action='store_true',
                        help='下载图片和视频到本地（默认只保留在线链接）')
    parser.add_argument('--output-dir', default='output',
                        help='输出目录（默认: output）')

    args = parser.parse_args()

    # 验证URL
    if 'mp.weixin.qq.com' not in args.url:
        print("警告: 这似乎不是一个微信公众号文章链接")

    extractor = WechatArticleExtractor(download_media=args.download)
    extractor.extract(args.url, args.output, args.output_dir)


if __name__ == '__main__':
    main()
