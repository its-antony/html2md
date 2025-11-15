#!/usr/bin/env python3
"""
微信公众号文章搜索模块
使用搜狗微信搜索 (weixin.sogou.com)
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import quote, urljoin
import time
import random


class WechatArticleSearcher:
    """微信公众号文章搜索器（基于搜狗）"""

    def __init__(self, use_playwright=False):
        self.base_url = "https://weixin.sogou.com"
        self.use_playwright = use_playwright

        # 模拟浏览器请求头
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Referer': 'https://weixin.sogou.com/',
            'Upgrade-Insecure-Requests': '1',
        }

    def search_articles(self, keyword, page=1, time_range=None):
        """
        搜索文章

        Args:
            keyword: 搜索关键词
            page: 页码（从1开始）
            time_range: 时间范围 ('day', 'week', 'month', 'year', None)

        Returns:
            文章列表，每个文章包含：title, url, author, publish_time, abstract
        """
        # 构建搜索URL
        search_url = f"{self.base_url}/weixin"

        params = {
            'query': keyword,
            'type': 2,  # 2=文章, 1=公众号
            'page': page,
        }

        # 添加时间范围
        if time_range:
            time_map = {
                'day': 1,
                'week': 2,
                'month': 3,
                'year': 4
            }
            if time_range in time_map:
                params['tsn'] = time_map[time_range]

        try:
            print(f"正在搜索: {keyword} (第{page}页)...")

            if self.use_playwright:
                html = self._fetch_with_playwright(search_url, params)
            else:
                html = self._fetch_with_requests(search_url, params)

            if not html:
                print("获取搜索结果失败")
                return []

            # 解析搜索结果
            articles = self._parse_search_results(html)
            print(f"✓ 找到 {len(articles)} 篇文章")

            return articles

        except Exception as e:
            print(f"搜索失败: {e}")
            return []

    def search_by_account(self, account_name, keyword=None, page=1):
        """
        搜索指定公众号的文章

        Args:
            account_name: 公众号名称
            keyword: 文章关键词（可选）
            page: 页码

        Returns:
            文章列表
        """
        # 如果有关键词，组合搜索
        if keyword:
            search_query = f"{keyword} {account_name}"
        else:
            search_query = account_name

        return self.search_articles(search_query, page)

    def _fetch_with_requests(self, url, params):
        """使用requests获取页面"""
        try:
            # 添加随机延迟避免被封
            time.sleep(random.uniform(1, 3))

            response = requests.get(
                url,
                params=params,
                headers=self.headers,
                timeout=30,
                allow_redirects=True
            )
            response.raise_for_status()
            response.encoding = 'utf-8'

            return response.text

        except Exception as e:
            print(f"Requests获取失败: {e}")
            return None

    def _fetch_with_playwright(self, url, params):
        """使用Playwright获取页面（处理反爬虫）"""
        try:
            from playwright.sync_api import sync_playwright
            from urllib.parse import urlencode

            # 构建完整URL
            full_url = f"{url}?{urlencode(params)}"

            print("使用浏览器模式获取搜索结果...")

            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(
                    user_agent=self.headers['User-Agent'],
                    viewport={'width': 1920, 'height': 1080},
                    locale='zh-CN'
                )
                page = context.new_page()

                # 访问页面
                page.goto(full_url, wait_until='networkidle', timeout=60000)

                # 等待内容加载
                page.wait_for_timeout(2000)

                # 获取页面内容
                content = page.content()
                browser.close()

                print("✓ 浏览器模式获取成功")
                return content

        except ImportError:
            print("警告: Playwright未安装，无法使用浏览器模式")
            return None
        except Exception as e:
            print(f"Playwright获取失败: {e}")
            return None

    def _parse_search_results(self, html):
        """解析搜索结果页面"""
        soup = BeautifulSoup(html, 'html.parser')
        articles = []

        # 搜狗微信搜索结果的CSS选择器
        # 结果列表在 <ul class="news-list"> 中
        news_list = soup.find('ul', class_='news-list')

        if not news_list:
            # 尝试其他可能的结构
            news_list = soup.find('div', class_='news-box')

        if not news_list:
            print("警告: 未找到搜索结果列表")
            # 保存HTML用于调试
            with open('debug_search.html', 'w', encoding='utf-8') as f:
                f.write(html)
            print("已保存调试HTML到 debug_search.html")
            return []

        # 查找所有文章条目
        items = news_list.find_all('li')

        for item in items:
            try:
                article = self._parse_article_item(item)
                if article:
                    articles.append(article)
            except Exception as e:
                print(f"解析文章条目失败: {e}")
                continue

        return articles

    def _parse_article_item(self, item):
        """解析单个文章条目"""
        article = {}

        # 标题和链接
        title_tag = item.find('h3') or item.find('a')
        if title_tag:
            article['title'] = title_tag.get_text().strip()
            link_tag = title_tag.find('a') if title_tag.name == 'h3' else title_tag
            if link_tag:
                article['url'] = link_tag.get('href', '')
                # 处理相对链接
                if article['url'] and not article['url'].startswith('http'):
                    article['url'] = urljoin(self.base_url, article['url'])

        # 公众号名称
        account_tag = item.find('a', attrs={'uigs': 'account_name_0'})
        if not account_tag:
            account_tag = item.find('a', class_='account')
        if account_tag:
            article['author'] = account_tag.get_text().strip()

        # 发布时间
        time_tag = item.find('span', class_='s2') or item.find('span', class_='time')
        if time_tag:
            article['publish_time'] = time_tag.get_text().strip()

        # 摘要
        abstract_tag = item.find('p', class_='txt-info') or item.find('div', class_='txt-box')
        if abstract_tag:
            article['abstract'] = abstract_tag.get_text().strip()

        # 只返回包含标题和URL的文章
        if article.get('title') and article.get('url'):
            return article

        return None


def main():
    """命令行接口"""
    import argparse

    parser = argparse.ArgumentParser(
        description='搜索微信公众号文章',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 搜索关键词
  %(prog)s "Claude Code"

  # 搜索指定公众号的文章
  %(prog)s --account "腾讯科技"

  # 组合搜索：在指定公众号中搜索关键词
  %(prog)s "人工智能" --account "腾讯科技"

  # 搜索最近一周的文章
  %(prog)s "AI" --time week

  # 使用Playwright（处理反爬虫）
  %(prog)s "微信" --playwright

  # 翻页搜索
  %(prog)s "技术" --page 2
        """
    )

    parser.add_argument('keyword', nargs='?', help='搜索关键词')
    parser.add_argument('-a', '--account', help='公众号名称')
    parser.add_argument('-p', '--page', type=int, default=1, help='页码（默认1）')
    parser.add_argument('-t', '--time', choices=['day', 'week', 'month', 'year'],
                        help='时间范围')
    parser.add_argument('--playwright', action='store_true',
                        help='使用Playwright（处理反爬虫）')
    parser.add_argument('-o', '--output', help='输出JSON文件')

    args = parser.parse_args()

    # 检查参数
    if not args.keyword and not args.account:
        parser.error("必须提供关键词或公众号名称")

    # 创建搜索器
    searcher = WechatArticleSearcher(use_playwright=args.playwright)

    # 执行搜索
    if args.account and args.keyword:
        # 组合搜索
        articles = searcher.search_by_account(args.account, args.keyword, args.page)
    elif args.account:
        # 只搜索公众号
        articles = searcher.search_by_account(args.account, page=args.page)
    else:
        # 只搜索关键词
        articles = searcher.search_articles(args.keyword, args.page, args.time)

    # 显示结果
    if articles:
        print(f"\n{'='*80}")
        print(f"搜索结果: 共 {len(articles)} 篇文章")
        print(f"{'='*80}\n")

        for i, article in enumerate(articles, 1):
            print(f"{i}. {article.get('title', 'N/A')}")
            print(f"   公众号: {article.get('author', 'N/A')}")
            print(f"   时间: {article.get('publish_time', 'N/A')}")
            print(f"   链接: {article.get('url', 'N/A')}")
            if article.get('abstract'):
                print(f"   摘要: {article.get('abstract', '')[:100]}...")
            print()

        # 保存到文件
        if args.output:
            import json
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(articles, f, ensure_ascii=False, indent=2)
            print(f"✓ 结果已保存到: {args.output}")
    else:
        print("\n未找到相关文章")


if __name__ == '__main__':
    main()
