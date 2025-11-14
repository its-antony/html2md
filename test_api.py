#!/usr/bin/env python3
"""
API 测试脚本
用于测试 HTML2MD Web API 是否正常工作
"""

import requests
import sys
from pprint import pprint


def test_health(base_url):
    """测试健康检查端点"""
    print("\n" + "="*60)
    print("测试 1: 健康检查")
    print("="*60)

    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        response.raise_for_status()

        print("✓ 服务正常运行")
        print("响应:")
        pprint(response.json())
        return True

    except Exception as e:
        print(f"✗ 健康检查失败: {e}")
        return False


def test_convert_get(base_url, test_url):
    """测试 GET 方式转换"""
    print("\n" + "="*60)
    print("测试 2: GET 方式转换")
    print("="*60)
    print(f"URL: {test_url}")

    try:
        response = requests.get(
            f"{base_url}/api/convert",
            params={
                "url": test_url,
                "download_media": False  # 测试时不下载媒体
            },
            timeout=120
        )
        response.raise_for_status()
        result = response.json()

        if result.get('success'):
            print("✓ 转换成功")
            print("响应:")
            pprint(result)
            return True
        else:
            print(f"✗ 转换失败: {result.get('message')}")
            return False

    except Exception as e:
        print(f"✗ 请求失败: {e}")
        return False


def test_convert_post(base_url, test_url):
    """测试 POST 方式转换"""
    print("\n" + "="*60)
    print("测试 3: POST 方式转换（下载媒体）")
    print("="*60)
    print(f"URL: {test_url}")

    try:
        response = requests.post(
            f"{base_url}/api/convert",
            json={
                "url": test_url,
                "download_media": True
            },
            timeout=300  # 5分钟超时
        )
        response.raise_for_status()
        result = response.json()

        if result.get('success'):
            print("✓ 转换成功")
            print("响应:")
            pprint(result)

            data = result.get('data', {})
            print(f"\n📄 Markdown 文件: {data.get('md_url')}")
            print(f"📁 文件名: {data.get('md_filename')}")
            print(f"🖼️  媒体文件数: {data.get('media_files')}")

            return True
        else:
            print(f"✗ 转换失败: {result.get('message')}")
            return False

    except Exception as e:
        print(f"✗ 请求失败: {e}")
        return False


def main():
    """主函数"""
    # 配置
    BASE_URL = "http://localhost:8000"  # 修改为你的 API 地址
    TEST_URL = "https://mp.weixin.qq.com/s/example"  # 修改为真实的测试 URL

    print("="*60)
    print("  HTML2MD API 测试")
    print("="*60)
    print(f"API 地址: {BASE_URL}")
    print(f"测试 URL: {TEST_URL}")

    # 检查是否提供了自定义测试 URL
    if len(sys.argv) > 1:
        TEST_URL = sys.argv[1]
        print(f"使用自定义 URL: {TEST_URL}")

    # 检查是否提供了自定义 API 地址
    if len(sys.argv) > 2:
        BASE_URL = sys.argv[2]
        print(f"使用自定义 API 地址: {BASE_URL}")

    # 运行测试
    results = []

    # 测试 1: 健康检查
    results.append(("健康检查", test_health(BASE_URL)))

    # 测试 2: GET 转换
    results.append(("GET 转换", test_convert_get(BASE_URL, TEST_URL)))

    # 测试 3: POST 转换
    results.append(("POST 转换", test_convert_post(BASE_URL, TEST_URL)))

    # 输出总结
    print("\n" + "="*60)
    print("测试总结")
    print("="*60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{name}: {status}")

    print("="*60)
    print(f"通过: {passed}/{total}")

    if passed == total:
        print("✓ 所有测试通过！")
        sys.exit(0)
    else:
        print("✗ 部分测试失败")
        sys.exit(1)


if __name__ == "__main__":
    main()
