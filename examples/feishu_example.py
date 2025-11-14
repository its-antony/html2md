#!/usr/bin/env python3
"""
飞书多维表格集成示例
演示如何从飞书表格读取 URL 并调用 API 转换
"""

import requests
import time
import os


class FeishuAPIClient:
    """飞书 API 客户端"""

    def __init__(self, app_id, app_secret):
        self.app_id = app_id
        self.app_secret = app_secret
        self.access_token = None
        self.token_expire_time = 0

    def get_access_token(self):
        """获取访问令牌"""
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
            raise Exception(f"获取 token 失败: {result.get('msg')}")

        self.access_token = result['tenant_access_token']
        self.token_expire_time = time.time() + result['expire'] - 300

        return self.access_token

    def get_records(self, app_token, table_id):
        """获取表格记录"""
        token = self.get_access_token()
        url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records"

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        response = requests.get(url, headers=headers)
        response.raise_for_status()
        result = response.json()

        if result.get('code') != 0:
            raise Exception(f"获取记录失败: {result.get('msg')}")

        return result['data']['items']

    def update_record(self, app_token, table_id, record_id, fields):
        """更新记录"""
        token = self.get_access_token()
        url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records/{record_id}"

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


def convert_url_via_api(api_base_url, url):
    """调用 HTML2MD API 转换 URL"""
    response = requests.post(
        f"{api_base_url}/api/convert",
        json={
            "url": url,
            "download_media": True
        },
        timeout=300
    )

    response.raise_for_status()
    result = response.json()

    if result['success']:
        return result['data']['md_url']
    else:
        raise Exception(result['message'])


def main():
    """主函数"""
    print("="*60)
    print("  飞书多维表格 → HTML2MD API 集成示例")
    print("="*60)

    # 配置（从环境变量读取）
    FEISHU_APP_ID = os.getenv("FEISHU_APP_ID", "your-app-id")
    FEISHU_APP_SECRET = os.getenv("FEISHU_APP_SECRET", "your-app-secret")
    FEISHU_APP_TOKEN = os.getenv("FEISHU_APP_TOKEN", "your-app-token")
    FEISHU_TABLE_ID = os.getenv("FEISHU_TABLE_ID", "your-table-id")
    HTML2MD_API_URL = os.getenv("HTML2MD_API_URL", "http://localhost:8000")

    # 字段名配置
    URL_FIELD = "URL"           # URL 字段名
    STATUS_FIELD = "状态"        # 状态字段名
    MD_PATH_FIELD = "MD路径"     # MD 路径字段名
    ERROR_FIELD = "错误信息"      # 错误信息字段名

    # 初始化飞书客户端
    feishu = FeishuAPIClient(FEISHU_APP_ID, FEISHU_APP_SECRET)

    print(f"\n连接到飞书多维表格...")
    print(f"  App Token: {FEISHU_APP_TOKEN}")
    print(f"  Table ID: {FEISHU_TABLE_ID}")

    # 获取所有记录
    print(f"\n正在获取记录...")
    records = feishu.get_records(FEISHU_APP_TOKEN, FEISHU_TABLE_ID)
    print(f"  找到 {len(records)} 条记录")

    # 处理待转换的记录
    pending_records = []
    for record in records:
        fields = record.get('fields', {})
        url = fields.get(URL_FIELD)
        status = fields.get(STATUS_FIELD, '')

        # 只处理有 URL 且状态为空或"待处理"的记录
        if url and (not status or status == '待处理'):
            pending_records.append({
                'record_id': record['record_id'],
                'url': url
            })

    print(f"  其中 {len(pending_records)} 条待处理")

    # 逐条处理
    for i, record in enumerate(pending_records, 1):
        record_id = record['record_id']
        url = record['url']

        print(f"\n[{i}/{len(pending_records)}] 处理记录: {record_id}")
        print(f"  URL: {url}")

        try:
            # 更新状态为"处理中"
            feishu.update_record(
                FEISHU_APP_TOKEN,
                FEISHU_TABLE_ID,
                record_id,
                {STATUS_FIELD: "处理中"}
            )

            # 调用 API 转换
            print(f"  正在转换...")
            md_url = convert_url_via_api(HTML2MD_API_URL, url)

            # 更新为"已完成"
            print(f"  ✓ 转换成功: {md_url}")
            feishu.update_record(
                FEISHU_APP_TOKEN,
                FEISHU_TABLE_ID,
                record_id,
                {
                    STATUS_FIELD: "已完成",
                    MD_PATH_FIELD: md_url,
                    ERROR_FIELD: ""
                }
            )

        except Exception as e:
            error_msg = str(e)
            print(f"  ✗ 转换失败: {error_msg}")

            # 更新为"失败"
            try:
                feishu.update_record(
                    FEISHU_APP_TOKEN,
                    FEISHU_TABLE_ID,
                    record_id,
                    {
                        STATUS_FIELD: "失败",
                        ERROR_FIELD: error_msg
                    }
                )
            except:
                pass

    print("\n" + "="*60)
    print("处理完成！")
    print("="*60)


if __name__ == "__main__":
    # 使用示例:
    # 1. 设置环境变量
    # export FEISHU_APP_ID=xxx
    # export FEISHU_APP_SECRET=xxx
    # export FEISHU_APP_TOKEN=xxx
    # export FEISHU_TABLE_ID=xxx
    # export HTML2MD_API_URL=http://localhost:8000
    #
    # 2. 运行脚本
    # python feishu_example.py

    main()
