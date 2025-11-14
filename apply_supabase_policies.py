#!/usr/bin/env python3
"""
应用 Supabase RLS 策略脚本
直接执行 SQL 语句来设置权限
"""

import os
from supabase import create_client, Client
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("错误：缺少 SUPABASE_URL 或 SUPABASE_KEY 环境变量")
    exit(1)

# 创建客户端（需要使用service_role key才能执行管理操作）
print(f"连接到 Supabase: {SUPABASE_URL}")
print("注意：此脚本需要 service_role key 才能设置 RLS 策略")
print("当前使用的是 anon key，只能设置基本权限")

client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# SQL 语句列表
policies_sql = [
    # Storage policies
    """
    CREATE POLICY IF NOT EXISTS "Allow Upload"
    ON storage.objects FOR INSERT
    WITH CHECK ( bucket_id = 'markdown-files' );
    """,
    """
    CREATE POLICY IF NOT EXISTS "Allow Update"
    ON storage.objects FOR UPDATE
    USING ( bucket_id = 'markdown-files' );
    """,
    # Conversions table policies
    """
    ALTER TABLE conversions ENABLE ROW LEVEL SECURITY;
    """,
    """
    CREATE POLICY IF NOT EXISTS "Allow Insert"
    ON conversions FOR INSERT
    WITH CHECK (true);
    """,
    """
    CREATE POLICY IF NOT EXISTS "Allow Select"
    ON conversions FOR SELECT
    USING (true);
    """,
]

print("\n正在应用 RLS 策略...")
print("=" * 50)

for i, sql in enumerate(policies_sql, 1):
    try:
        print(f"\n[{i}/{len(policies_sql)}] 执行 SQL...")
        print(sql.strip()[:100] + "...")
        # 注意：supabase-py 不支持直接执行SQL，需要使用postgrest API
        print("❌ 无法通过 Python API 直接执行 SQL")
        print("   请手动在 Supabase SQL Editor 中执行 supabase_init.sql")
        break
    except Exception as e:
        print(f"❌ 失败: {e}")

print("\n" + "=" * 50)
print("\n📋 手动操作步骤:")
print("1. 访问 Supabase Dashboard")
print("2. 进入 SQL Editor")
print("3. 复制并执行 supabase_init.sql 文件中的所有 SQL 语句")
print("4. 确认所有策略都已创建成功")
print("\n或者使用 service_role key 而不是 anon key")
