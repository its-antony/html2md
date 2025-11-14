#!/usr/bin/env python3
"""
简单使用示例
演示如何调用 HTML2MD Web API
"""

import requests
import json


def example_1_simple_convert():
    """示例 1: 最简单的转换"""
    print("\n" + "="*60)
    print("示例 1: 简单转换（不下载媒体）")
    print("="*60)

    api_url = "http://localhost:8000/api/convert"
    test_url = "https://mp.weixin.qq.com/s/xxxxx"  # 替换为真实 URL

    # GET 方式
    response = requests.get(
        api_url,
        params={"url": test_url, "download_media": False}
    )

    result = response.json()
    if result['success']:
        print(f"✓ 转换成功！")
        print(f"  MD文件: {result['data']['md_url']}")
    else:
        print(f"✗ 转换失败: {result['message']}")


def example_2_download_media():
    """示例 2: 下载媒体资源"""
    print("\n" + "="*60)
    print("示例 2: 转换并下载媒体资源")
    print("="*60)

    api_url = "http://localhost:8000/api/convert"
    test_url = "https://mp.weixin.qq.com/s/xxxxx"  # 替换为真实 URL

    # POST 方式
    response = requests.post(
        api_url,
        json={
            "url": test_url,
            "download_media": True
        },
        timeout=300
    )

    result = response.json()
    if result['success']:
        data = result['data']
        print(f"✓ 转换成功！")
        print(f"  MD文件: {data['md_url']}")
        print(f"  文件名: {data['md_filename']}")
        print(f"  媒体文件: {data['media_files']} 个")
    else:
        print(f"✗ 转换失败: {result['message']}")


def example_3_batch_convert():
    """示例 3: 批量转换"""
    print("\n" + "="*60)
    print("示例 3: 批量转换多个 URL")
    print("="*60)

    api_url = "http://localhost:8000/api/convert"

    urls = [
        "https://mp.weixin.qq.com/s/xxxxx1",
        "https://mp.weixin.qq.com/s/xxxxx2",
        "https://zhuanlan.zhihu.com/p/xxxxx",
    ]

    results = []
    for i, url in enumerate(urls, 1):
        print(f"\n[{i}/{len(urls)}] 处理: {url}")

        try:
            response = requests.post(
                api_url,
                json={"url": url, "download_media": True},
                timeout=300
            )

            result = response.json()
            if result['success']:
                print(f"  ✓ 成功: {result['data']['md_url']}")
                results.append({
                    'url': url,
                    'success': True,
                    'md_url': result['data']['md_url']
                })
            else:
                print(f"  ✗ 失败: {result['message']}")
                results.append({
                    'url': url,
                    'success': False,
                    'error': result['message']
                })

        except Exception as e:
            print(f"  ✗ 异常: {e}")
            results.append({
                'url': url,
                'success': False,
                'error': str(e)
            })

    # 输出总结
    print("\n" + "="*60)
    print("批量转换总结")
    print("="*60)
    success_count = sum(1 for r in results if r['success'])
    print(f"成功: {success_count}/{len(results)}")

    return results


def example_4_save_to_file():
    """示例 4: 下载 MD 文件到本地"""
    print("\n" + "="*60)
    print("示例 4: 下载 Markdown 文件到本地")
    print("="*60)

    api_url = "http://localhost:8000/api/convert"
    test_url = "https://mp.weixin.qq.com/s/xxxxx"  # 替换为真实 URL

    # 1. 转换
    response = requests.post(
        api_url,
        json={"url": test_url, "download_media": True}
    )

    result = response.json()
    if not result['success']:
        print(f"✗ 转换失败: {result['message']}")
        return

    # 2. 获取 MD 文件 URL
    md_url = result['data']['md_url']
    md_filename = result['data']['md_filename']

    print(f"✓ 转换成功，正在下载...")

    # 3. 下载 MD 文件
    md_response = requests.get(md_url)
    md_response.raise_for_status()

    # 4. 保存到本地
    local_path = f"downloaded_{md_filename}"
    with open(local_path, 'w', encoding='utf-8') as f:
        f.write(md_response.text)

    print(f"✓ 已保存到: {local_path}")


def example_5_error_handling():
    """示例 5: 错误处理"""
    print("\n" + "="*60)
    print("示例 5: 完整的错误处理")
    print("="*60)

    api_url = "http://localhost:8000/api/convert"
    test_url = "https://mp.weixin.qq.com/s/xxxxx"  # 替换为真实 URL

    try:
        response = requests.post(
            api_url,
            json={"url": test_url, "download_media": True},
            timeout=300
        )

        # 检查 HTTP 状态
        response.raise_for_status()

        # 解析响应
        result = response.json()

        # 检查业务状态
        if result['success']:
            data = result['data']
            print(f"✓ 转换成功")
            print(f"  文件: {data['md_url']}")
            return data

        else:
            print(f"✗ 业务错误: {result['message']}")
            return None

    except requests.exceptions.Timeout:
        print("✗ 请求超时")
        return None

    except requests.exceptions.ConnectionError:
        print("✗ 连接失败，请检查 API 服务是否运行")
        return None

    except requests.exceptions.HTTPError as e:
        print(f"✗ HTTP 错误: {e.response.status_code}")
        print(f"  详情: {e.response.text}")
        return None

    except json.JSONDecodeError:
        print("✗ 响应格式错误")
        return None

    except Exception as e:
        print(f"✗ 未知错误: {e}")
        return None


def main():
    """运行所有示例"""
    print("="*60)
    print("  HTML2MD API 使用示例")
    print("="*60)
    print("\n请确保 API 服务正在运行: http://localhost:8000")
    print("并将示例中的 URL 替换为真实的测试 URL\n")

    # 运行示例
    # example_1_simple_convert()
    # example_2_download_media()
    # example_3_batch_convert()
    # example_4_save_to_file()
    example_5_error_handling()

    print("\n" + "="*60)
    print("示例运行完成！")
    print("="*60)


if __name__ == "__main__":
    main()
