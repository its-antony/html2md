#!/usr/bin/env python3
"""
通用网页转Markdown工具
支持多个平台：微信公众号、知乎、小红书等
"""

import re
import sys
import argparse
import requests
from bs4 import BeautifulSoup
import html2text
from pathlib import Path
from urllib.parse import urlparse
import os


class WebToMarkdown:
    def __init__(self, download_media=False):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        }
        self.download_media = download_media
        self.media_folder = None
        self.media_map = {}

    def detect_platform(self, url):
        """检测网站平台"""
        if 'mp.weixin.qq.com' in url:
            return 'wechat'
        elif 'zhihu.com' in url:
            return 'zhihu'
        elif 'xiaohongshu.com' in url or 'xhslink.com' in url:
            return 'xiaohongshu'
        elif 'juejin.cn' in url:
            return 'juejin'
        elif 'csdn.net' in url:
            return 'csdn'
        else:
            return 'generic'

    def fetch_page(self, url):
        """获取网页HTML内容"""
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            response.encoding = response.apparent_encoding or 'utf-8'
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"错误: 无法获取网页内容 - {e}")
            return None

    def parse_wechat(self, soup):
        """解析微信公众号文章"""
        title = None
        title_tag = soup.find('h1', class_='rich_media_title')
        if title_tag:
            title = title_tag.get_text().strip()

        author = None
        author_tag = soup.find('a', class_='rich_media_meta_link')
        if author_tag:
            author = author_tag.get_text().strip()

        content = soup.find('div', id='js_content')
        if not content:
            content = soup.find('div', class_='rich_media_content')

        return {
            'title': title,
            'author': author,
            'content': content,
            'platform': '微信公众号'
        }

    def parse_zhihu(self, soup):
        """解析知乎文章"""
        title = None
        title_tag = soup.find('h1', class_='Post-Title')
        if not title_tag:
            title_tag = soup.find('h1', class_='ArticleItem-title')
        if title_tag:
            title = title_tag.get_text().strip()

        author = None
        author_tag = soup.find('meta', {'name': 'author'})
        if author_tag:
            author = author_tag.get('content')

        content = soup.find('div', class_='RichContent-inner')
        if not content:
            content = soup.find('div', class_='Post-RichTextContainer')

        return {
            'title': title,
            'author': author,
            'content': content,
            'platform': '知乎'
        }

    def parse_juejin(self, soup):
        """解析掘金文章"""
        title = None
        title_tag = soup.find('h1', class_='article-title')
        if title_tag:
            title = title_tag.get_text().strip()

        author = None
        author_tag = soup.find('span', class_='username')
        if author_tag:
            author = author_tag.get_text().strip()

        content = soup.find('article', class_='article-content')
        if not content:
            content = soup.find('div', class_='markdown-body')

        return {
            'title': title,
            'author': author,
            'content': content,
            'platform': '掘金'
        }

    def parse_csdn(self, soup):
        """解析CSDN文章"""
        title = None
        title_tag = soup.find('h1', class_='title-article')
        if title_tag:
            title = title_tag.get_text().strip()

        author = None
        author_tag = soup.find('a', class_='follow-nickName')
        if author_tag:
            author = author_tag.get_text().strip()

        content = soup.find('article', class_='baidu_pl')
        if not content:
            content = soup.find('div', id='article_content')

        return {
            'title': title,
            'author': author,
            'content': content,
            'platform': 'CSDN'
        }

    def parse_generic(self, soup):
        """通用解析方法"""
        # 尝试从常见位置提取标题
        title = None
        for selector in ['h1', 'title', 'meta[property="og:title"]']:
            if selector.startswith('meta'):
                tag = soup.find('meta', {'property': 'og:title'})
                if tag:
                    title = tag.get('content')
            else:
                tag = soup.find(selector)
                if tag:
                    title = tag.get_text().strip()
            if title:
                break

        # 尝试查找主要内容区域
        content = None
        for selector in ['article', 'main', '.post-content', '.article-content', '.content']:
            if selector.startswith('.'):
                content = soup.find(class_=selector[1:])
            else:
                content = soup.find(selector)
            if content:
                break

        # 如果都找不到，尝试找最大的div
        if not content:
            all_divs = soup.find_all('div')
            if all_divs:
                content = max(all_divs, key=lambda x: len(x.get_text()))

        return {
            'title': title,
            'author': None,
            'content': content,
            'platform': '通用网页'
        }

    def parse_page(self, html_content, platform):
        """根据平台解析页面"""
        soup = BeautifulSoup(html_content, 'html.parser')

        parse_methods = {
            'wechat': self.parse_wechat,
            'zhihu': self.parse_zhihu,
            'juejin': self.parse_juejin,
            'csdn': self.parse_csdn,
            'generic': self.parse_generic
        }

        parser = parse_methods.get(platform, self.parse_generic)
        return parser(soup)

    def extract_media(self, content_tag):
        """提取媒体资源"""
        media_list = []
        if not content_tag:
            return media_list

        # 提取图片
        for img in content_tag.find_all('img'):
            img_url = img.get('data-src') or img.get('src') or img.get('data-original')
            if img_url and img_url.startswith('http'):
                media_list.append({
                    'type': 'image',
                    'url': img_url,
                    'tag': img
                })

        return media_list

    def html_to_markdown(self, html_content, media_list):
        """将HTML转换为Markdown"""
        if not html_content:
            return ""

        # 处理图片标签
        for img in html_content.find_all('img'):
            if img.get('data-src') and not img.get('src'):
                img['src'] = img['data-src']
            elif img.get('data-original') and not img.get('src'):
                img['src'] = img['data-original']

        h = html2text.HTML2Text()
        h.ignore_links = False
        h.ignore_images = False
        h.ignore_emphasis = False
        h.body_width = 0
        h.unicode_snob = True
        h.skip_internal_links = True

        return h.handle(str(html_content))

    def clean_markdown(self, markdown_text):
        """清理Markdown文本"""
        markdown_text = re.sub(r'\n{3,}', '\n\n', markdown_text)
        markdown_text = markdown_text.strip()

        # 修复包含空格的图片链接
        def fix_image_path(match):
            alt_text = match.group(1)
            path = match.group(2)
            if ' ' in path and not path.startswith('<'):
                return f'![{alt_text}](<{path}>)'
            return match.group(0)

        markdown_text = re.sub(r'!\[(.*?)\]\(([^)]+)\)', fix_image_path, markdown_text)
        return markdown_text

    def generate_filename(self, title, url):
        """生成文件名"""
        if title:
            filename = re.sub(r'[<>:"/\\|?*]', '', title)
            filename = filename.strip()[:100]
        else:
            parsed = urlparse(url)
            filename = f"article_{parsed.path.split('/')[-1]}"
        return f"{filename}.md"

    def save_markdown(self, content, filepath):
        """保存Markdown文件"""
        try:
            Path(filepath).write_text(content, encoding='utf-8')
            print(f"✓ 文章已保存到: {filepath}")
        except Exception as e:
            print(f"错误: 保存文件失败 - {e}")
            sys.exit(1)

    def convert(self, url, output_path=None, output_dir='output'):
        """主转换流程"""
        print(f"正在获取网页: {url}")

        # 检测平台
        platform = self.detect_platform(url)
        print(f"检测到平台: {platform}")

        # 获取网页内容
        html_content = self.fetch_page(url)
        if not html_content:
            print("错误: 无法获取网页内容")
            sys.exit(1)

        # 解析页面
        article = self.parse_page(html_content, platform)

        if not article['content']:
            print(f"警告: 未能找到文章内容")
            print(f"提示: {article['platform']}的页面结构可能已更新，需要调整解析规则")
            # 保存原始HTML用于调试
            debug_file = Path(output_dir) / 'debug.html'
            debug_file.parent.mkdir(exist_ok=True)
            debug_file.write_text(html_content, encoding='utf-8')
            print(f"已保存原始HTML到: {debug_file}（可用于调试）")
            sys.exit(1)

        print(f"✓ 成功解析文章")
        if article['title']:
            print(f"  标题: {article['title']}")
        if article['author']:
            print(f"  作者: {article['author']}")

        # 提取媒体资源
        media_list = self.extract_media(article['content'])
        if media_list:
            print(f"✓ 找到 {len(media_list)} 个图片")

        # 确定输出路径
        if not output_path:
            output_dir_path = Path(output_dir)
            output_dir_path.mkdir(exist_ok=True)
            output_path = output_dir_path / self.generate_filename(article['title'], url)
            output_path = str(output_path)
        else:
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        # 构建Markdown内容
        markdown_parts = []

        if article['title']:
            markdown_parts.append(f"# {article['title']}\n")

        metadata = []
        if article['author']:
            metadata.append(f"**作者:** {article['author']}")
        if article.get('platform'):
            metadata.append(f"**来源:** {article['platform']}")
        metadata.append(f"**原文链接:** {url}")

        if metadata:
            markdown_parts.append("\n".join(metadata))
            markdown_parts.append("\n---\n")

        # 添加正文
        content_md = self.html_to_markdown(article['content'], media_list)
        content_md = self.clean_markdown(content_md)
        markdown_parts.append(content_md)

        final_markdown = "\n".join(markdown_parts)

        # 保存文件
        self.save_markdown(final_markdown, output_path)

        return output_path


def main():
    parser = argparse.ArgumentParser(
        description='通用网页转Markdown工具，支持微信公众号、知乎、掘金、CSDN等',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
支持的平台:
  - 微信公众号 (mp.weixin.qq.com)
  - 知乎 (zhihu.com)
  - 掘金 (juejin.cn)
  - CSDN (csdn.net)
  - 其他网站 (通用解析)

示例:
  # 转换微信公众号文章
  %(prog)s https://mp.weixin.qq.com/s/xxxxx

  # 转换知乎文章
  %(prog)s https://zhuanlan.zhihu.com/p/xxxxx

  # 转换掘金文章
  %(prog)s https://juejin.cn/post/xxxxx

  # 指定输出目录
  %(prog)s https://xxxx --output-dir ./articles
        """
    )

    parser.add_argument('url', help='网页URL')
    parser.add_argument('-o', '--output', help='输出文件路径（可选）')
    parser.add_argument('--output-dir', default='output', help='输出目录（默认: output）')

    args = parser.parse_args()

    converter = WebToMarkdown()
    converter.convert(args.url, args.output, args.output_dir)


if __name__ == '__main__':
    main()
