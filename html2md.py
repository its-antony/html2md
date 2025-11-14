#!/usr/bin/env python3
"""
HTML转Markdown统一工具
支持微信公众号、知乎、掘金、CSDN等多个平台
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


class PlatformDetector:
    """平台检测器"""

    @staticmethod
    def detect(url):
        """检测URL所属平台"""
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

    @staticmethod
    def get_platform_name(platform):
        """获取平台中文名称"""
        names = {
            'wechat': '微信公众号',
            'zhihu': '知乎',
            'xiaohongshu': '小红书',
            'juejin': '掘金',
            'csdn': 'CSDN',
            'generic': '通用网页'
        }
        return names.get(platform, '未知平台')


class BaseParser:
    """解析器基类"""

    def __init__(self):
        self.platform_name = '未知'

    def parse(self, soup):
        """解析页面，返回标题、作者、内容"""
        raise NotImplementedError

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


class WechatParser(BaseParser):
    """微信公众号解析器"""

    def __init__(self):
        super().__init__()
        self.platform_name = '微信公众号'

    def parse(self, soup):
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
        if time_tag:
            publish_time = time_tag.get_text().strip()

        # 提取正文内容
        content = soup.find('div', id='js_content')
        if not content:
            content = soup.find('div', class_='rich_media_content')

        if content:
            # 移除不必要的标签
            for tag in content.find_all(['script', 'style']):
                tag.decompose()

        return {
            'title': title,
            'author': author,
            'publish_time': publish_time,
            'content': content
        }


class ZhihuParser(BaseParser):
    """知乎解析器"""

    def __init__(self):
        super().__init__()
        self.platform_name = '知乎'

    def parse(self, soup):
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
            'publish_time': None,
            'content': content
        }


class JuejinParser(BaseParser):
    """掘金解析器"""

    def __init__(self):
        super().__init__()
        self.platform_name = '掘金'

    def parse(self, soup):
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
            'publish_time': None,
            'content': content
        }


class CSDNParser(BaseParser):
    """CSDN解析器"""

    def __init__(self):
        super().__init__()
        self.platform_name = 'CSDN'

    def parse(self, soup):
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
            'publish_time': None,
            'content': content
        }


class GenericParser(BaseParser):
    """通用解析器"""

    def __init__(self):
        super().__init__()
        self.platform_name = '通用网页'

    def parse(self, soup):
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
            'publish_time': None,
            'content': content
        }


class HTML2Markdown:
    """HTML转Markdown主类"""

    def __init__(self, download_media=False):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Connection': 'close',  # 强制关闭keep-alive，避免HTTP/2问题
        }
        self.download_media = download_media
        self.media_folder = None
        self.media_map = {}

        # 创建Session并强制使用HTTP/1.1（避免HTTP/2 StreamReset错误）
        self.session = requests.Session()

        # 配置HTTPAdapter并禁用连接池（强制每次请求新建连接）
        from requests.adapters import HTTPAdapter
        from urllib3.util.retry import Retry

        # 配置重试策略
        retry_strategy = Retry(
            total=5,
            backoff_factor=2,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"]
        )

        # 创建adapter，禁用连接池
        adapter = HTTPAdapter(
            max_retries=retry_strategy,
            pool_connections=1,
            pool_maxsize=1,
            pool_block=False
        )

        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)

        # 注册所有解析器
        self.parsers = {
            'wechat': WechatParser(),
            'zhihu': ZhihuParser(),
            'juejin': JuejinParser(),
            'csdn': CSDNParser(),
            'generic': GenericParser()
        }

    def fetch_page(self, url):
        """获取网页内容"""
        max_retries = 5  # 增加重试次数
        import time

        for attempt in range(max_retries):
            try:
                # 使用更兼容的配置
                response = self.session.get(
                    url,
                    headers=self.headers,
                    timeout=30,
                    verify=True,
                    allow_redirects=True
                )
                response.raise_for_status()
                response.encoding = response.apparent_encoding or 'utf-8'
                return response.text
            except Exception as e:
                error_msg = str(e)
                # 特殊处理HTTP/2 StreamReset错误
                if 'StreamReset' in error_msg or 'stream_id' in error_msg:
                    wait_time = (attempt + 1) * 2  # 指数退避：2s, 4s, 6s, 8s, 10s
                    print(f"警告: HTTP/2连接错误 (尝试 {attempt + 1}/{max_retries}): {e}")
                    if attempt < max_retries - 1:
                        print(f"  等待 {wait_time} 秒后重试...")
                        time.sleep(wait_time)
                        # 重新创建session，强制使用HTTP/1.1
                        if attempt >= 2:  # 从第3次尝试开始禁用HTTP/2
                            import requests
                            from requests.adapters import HTTPAdapter
                            from urllib3.util.retry import Retry

                            self.session = requests.Session()
                            # 配置重试策略
                            retry_strategy = Retry(
                                total=3,
                                backoff_factor=1,
                                status_forcelist=[429, 500, 502, 503, 504],
                            )
                            adapter = HTTPAdapter(max_retries=retry_strategy)
                            self.session.mount("http://", adapter)
                            self.session.mount("https://", adapter)
                            print("  已切换到 HTTP/1.1")
                        continue
                    else:
                        raise  # 最后一次尝试仍失败
                elif 'ConnectionError' in error_msg or 'timeout' in error_msg.lower():
                    wait_time = (attempt + 1) * 2
                    print(f"警告: 网络错误 (尝试 {attempt + 1}/{max_retries}): {e}")
                    if attempt < max_retries - 1:
                        print(f"  等待 {wait_time} 秒后重试...")
                        time.sleep(wait_time)
                        continue
                    else:
                        raise
                else:
                    # 其他错误直接抛出
                    print(f"错误: 无法获取网页内容 - {e}")
                    raise

        return None

    def download_file(self, url, save_path):
        """下载单个文件"""
        try:
            response = self.session.get(url, headers=self.headers, timeout=30, stream=True)
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
            ext = os.path.splitext(path)[1].split('?')[0]  # 移除查询参数
            if ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.mp4', '.mov', '.avi']:
                return ext

        # 根据类型返回默认扩展名
        if media_type == 'image':
            return '.jpg'
        elif media_type == 'video':
            return '.mp4'
        return ''

    def html_to_markdown(self, html_content, media_list):
        """将HTML转换为Markdown"""
        if not html_content:
            return ""

        # 处理所有img标签：将data-src复制到src
        for img in html_content.find_all('img'):
            if img.get('data-src') and not img.get('src'):
                img['src'] = img['data-src']
            elif img.get('data-original') and not img.get('src'):
                img['src'] = img['data-original']

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
        h.body_width = 0
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
        platform = PlatformDetector.detect(url)
        platform_name = PlatformDetector.get_platform_name(platform)
        print(f"检测到平台: {platform_name}")

        # 获取网页内容
        html_content = self.fetch_page(url)
        if not html_content:
            print("错误: 无法获取网页内容")
            sys.exit(1)

        # 解析页面
        soup = BeautifulSoup(html_content, 'html.parser')
        parser = self.parsers.get(platform, self.parsers['generic'])
        article = parser.parse(soup)

        if not article['content']:
            print(f"警告: 未能找到文章内容")
            print(f"提示: {platform_name}的页面结构可能已更新，需要调整解析规则")
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
        media_list = parser.extract_media(article['content'])
        if media_list:
            image_count = sum(1 for m in media_list if m['type'] == 'image')
            video_count = sum(1 for m in media_list if m['type'] == 'video')
            print(f"✓ 找到 {len(media_list)} 个媒体资源 (图片: {image_count}, 视频: {video_count})")

        # 确定输出路径
        if not output_path:
            output_dir_path = Path(output_dir)
            output_dir_path.mkdir(exist_ok=True)
            output_path = output_dir_path / self.generate_filename(article['title'], url)
            output_path = str(output_path)
        else:
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        # 下载媒体资源（如果需要）
        if self.download_media and media_list:
            base_name = os.path.splitext(output_path)[0]
            self.download_media_files(media_list, base_name)

        # 构建Markdown内容
        markdown_parts = []

        if article['title']:
            markdown_parts.append(f"# {article['title']}\n")

        metadata = []
        if article['author']:
            metadata.append(f"**作者:** {article['author']}")
        if article.get('publish_time'):
            metadata.append(f"**发布时间:** {article['publish_time']}")
        metadata.append(f"**来源:** {platform_name}")
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
        description='HTML转Markdown统一工具 - 支持微信公众号、知乎、掘金、CSDN等多个平台',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
支持的平台:
  ✅ 微信公众号 (mp.weixin.qq.com)     - 完美支持
  ✅ 知乎 (zhihu.com)                  - 基础支持
  ✅ 掘金 (juejin.cn)                  - 基础支持
  ✅ CSDN (csdn.net)                   - 基础支持
  ⚠️  其他网站                          - 通用解析

使用示例:
  # 微信公众号文章（推荐使用 --download 下载图片）
  %(prog)s https://mp.weixin.qq.com/s/xxxxx --download

  # 知乎文章
  %(prog)s https://zhuanlan.zhihu.com/p/xxxxx

  # 掘金文章
  %(prog)s https://juejin.cn/post/xxxxx

  # 指定输出目录
  %(prog)s https://xxxx --output-dir ./articles

  # 指定输出文件
  %(prog)s https://xxxx -o my_article.md -d
        """
    )

    parser.add_argument('url', help='网页URL')
    parser.add_argument('-o', '--output', help='输出文件路径（可选，默认保存到output目录）')
    parser.add_argument('-d', '--download', action='store_true',
                        help='下载图片和视频到本地（默认只保留在线链接）')
    parser.add_argument('--output-dir', default='output',
                        help='输出目录（默认: output）')

    args = parser.parse_args()

    converter = HTML2Markdown(download_media=args.download)
    converter.convert(args.url, args.output, args.output_dir)


if __name__ == '__main__':
    main()
