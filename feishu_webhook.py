#!/usr/bin/env python3
"""
飞书多维表格 Webhook 集成脚本
当表格中添加新 URL 时，自动调用 Web API 进行转换
"""

import requests
import time
from typing import Optional


class FeishuWebhookIntegration:
    """飞书 Webhook 集成类"""

    def __init__(self, api_base_url: str, app_id: str, app_secret: str,
                 app_token: str, table_id: str):
        """
        初始化

        Args:
            api_base_url: HTML2MD API 服务地址
            app_id: 飞书应用ID
            app_secret: 飞书应用密钥
            app_token: 多维表格 App Token
            table_id: 表格ID
        """
        self.api_base_url = api_base_url.rstrip('/')
        self.app_id = app_id
        self.app_secret = app_secret
        self.app_token = app_token
        self.table_id = table_id
        self.access_token = None
        self.token_expire_time = 0

    def get_tenant_access_token(self):
        """获取飞书 access token"""
        if self.access_token and time.time() < self.token_expire_time:
            return self.access_token

        url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
        payload = {
            "app_id": self.app_id,
            "app_secret": self.app_secret
        }

        response = requests.post(url, json=payload)
        response.raise_for_status()
        result = response.json()

        if result.get('code') != 0:
            raise Exception(f"获取token失败: {result.get('msg')}")

        self.access_token = result['tenant_access_token']
        self.token_expire_time = time.time() + result['expire'] - 300

        return self.access_token

    def update_record(self, record_id: str, fields: dict):
        """更新表格记录"""
        token = self.get_tenant_access_token()
        url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{self.app_token}/tables/{self.table_id}/records/{record_id}"

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        payload = {"fields": fields}

        response = requests.put(url, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()

        if result.get('code') != 0:
            raise Exception(f"更新记录失败: {result.get('msg')}")

    def convert_url(self, url: str, download_media: bool = True) -> dict:
        """
        调用 API 转换 URL

        Args:
            url: 要转换的 URL
            download_media: 是否下载媒体资源

        Returns:
            API 响应结果
        """
        api_url = f"{self.api_base_url}/api/convert"

        response = requests.post(
            api_url,
            json={
                "url": url,
                "download_media": download_media
            },
            timeout=300  # 5分钟超时
        )

        response.raise_for_status()
        return response.json()

    def handle_new_record(self, record_id: str, url: str):
        """
        处理新记录

        Args:
            record_id: 记录ID
            url: URL
        """
        print(f"\n处理新记录: {record_id}")
        print(f"  URL: {url}")

        try:
            # 更新状态为"处理中"
            self.update_record(record_id, {"状态": "处理中"})

            # 调用 API 转换
            result = self.convert_url(url, download_media=True)

            if result.get('success'):
                data = result.get('data', {})
                md_url = data.get('md_url', '')

                print(f"  ✓ 转换成功: {md_url}")

                # 更新记录
                self.update_record(record_id, {
                    "状态": "已完成",
                    "MD路径": md_url,
                    "错误信息": ""
                })
            else:
                error_msg = result.get('message', '未知错误')
                print(f"  ✗ 转换失败: {error_msg}")

                self.update_record(record_id, {
                    "状态": "失败",
                    "错误信息": error_msg
                })

        except Exception as e:
            error_msg = f"{type(e).__name__}: {str(e)}"
            print(f"  ✗ 处理失败: {error_msg}")

            try:
                self.update_record(record_id, {
                    "状态": "失败",
                    "错误信息": error_msg
                })
            except:
                pass


def main():
    """示例：处理飞书 Webhook 事件"""
    import os
    from flask import Flask, request, jsonify

    app = Flask(__name__)

    # 从环境变量获取配置
    API_BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:8000')
    FEISHU_APP_ID = os.getenv('FEISHU_APP_ID')
    FEISHU_APP_SECRET = os.getenv('FEISHU_APP_SECRET')
    FEISHU_APP_TOKEN = os.getenv('FEISHU_APP_TOKEN')
    FEISHU_TABLE_ID = os.getenv('FEISHU_TABLE_ID')

    integration = FeishuWebhookIntegration(
        api_base_url=API_BASE_URL,
        app_id=FEISHU_APP_ID,
        app_secret=FEISHU_APP_SECRET,
        app_token=FEISHU_APP_TOKEN,
        table_id=FEISHU_TABLE_ID
    )

    @app.route('/webhook', methods=['POST'])
    def webhook_handler():
        """处理飞书 Webhook"""
        data = request.json

        # URL 验证（首次配置时）
        if data.get('type') == 'url_verification':
            return jsonify({
                'challenge': data.get('challenge')
            })

        # 处理事件
        event = data.get('event', {})
        if event.get('type') == 'bitable.record.created':
            # 新记录创建事件
            record_id = event.get('record_id')
            # 这里需要获取记录详情来获取 URL
            # 简化示例，实际需要调用飞书 API 获取记录内容
            url = event.get('fields', {}).get('URL')

            if url:
                # 异步处理（推荐使用消息队列）
                integration.handle_new_record(record_id, url)

        return jsonify({'success': True})

    @app.route('/health', methods=['GET'])
    def health():
        return jsonify({'status': 'ok'})

    app.run(host='0.0.0.0', port=5000)


if __name__ == '__main__':
    main()
