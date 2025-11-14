#!/usr/bin/env python3
"""
HTML to Markdown Web API Service
支持部署到 Cloudflare Workers，使用 Supabase 存储
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
from typing import Optional
import os
import tempfile
import hashlib
from datetime import datetime
from pathlib import Path
import uuid

from html2md import HTML2Markdown
from supabase import create_client, Client

# 环境变量配置
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_BUCKET = os.getenv("SUPABASE_BUCKET", "markdown-files")

app = FastAPI(
    title="HTML to Markdown API",
    description="将网页 URL 转换为 Markdown 格式并存储到 Supabase",
    version="1.0.0"
)

# 允许跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ConvertRequest(BaseModel):
    """转换请求"""
    url: HttpUrl
    download_media: bool = True
    callback_url: Optional[str] = None  # 可选的回调 URL（用于异步通知）


class ConvertResponse(BaseModel):
    """转换响应"""
    success: bool
    message: str
    data: Optional[dict] = None


class SupabaseStorage:
    """Supabase 存储管理类"""

    def __init__(self):
        if not SUPABASE_URL or not SUPABASE_KEY:
            raise ValueError("Missing SUPABASE_URL or SUPABASE_KEY environment variables")

        # 创建Supabase客户端（暂时使用默认配置）
        # TODO: 配置httpx使用HTTP/1.1需要更深入的Supabase客户端定制
        self.client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        self.bucket = SUPABASE_BUCKET
        self._ensure_bucket()

    def _ensure_bucket(self):
        """确保存储桶存在"""
        try:
            # 尝试获取桶信息
            self.client.storage.get_bucket(self.bucket)
        except Exception:
            # 如果不存在，创建桶（公开访问）
            try:
                self.client.storage.create_bucket(
                    self.bucket,
                    options={"public": True}
                )
            except Exception as e:
                print(f"Warning: Could not create bucket: {e}")

    def upload_file(self, local_path: str, remote_path: str) -> str:
        """
        上传文件到 Supabase Storage（带重试机制）

        Args:
            local_path: 本地文件路径
            remote_path: 远程文件路径

        Returns:
            公开访问 URL
        """
        import time

        with open(local_path, 'rb') as f:
            file_data = f.read()

        # 重试上传（应对HTTP/2 StreamReset错误）
        max_retries = 5
        for attempt in range(max_retries):
            try:
                # 上传文件
                self.client.storage.from_(self.bucket).upload(
                    remote_path,
                    file_data,
                    file_options={"content-type": "text/markdown; charset=utf-8"}
                )

                # 获取公开 URL
                public_url = self.client.storage.from_(self.bucket).get_public_url(remote_path)
                return public_url

            except Exception as e:
                error_msg = str(e)
                if 'StreamReset' in error_msg or 'stream_id' in error_msg:
                    if attempt < max_retries - 1:
                        wait_time = (attempt + 1) * 2
                        print(f"  Supabase上传失败 (尝试 {attempt + 1}/{max_retries}): {e}")
                        print(f"  等待 {wait_time} 秒后重试...")
                        time.sleep(wait_time)
                        continue
                # 非StreamReset错误或最后一次尝试失败，直接抛出
                raise

    def upload_directory(self, local_dir: str, remote_prefix: str) -> dict:
        """
        上传整个目录（包括媒体文件）

        Args:
            local_dir: 本地目录路径
            remote_prefix: 远程路径前缀

        Returns:
            文件映射字典 {本地路径: 公开URL}
        """
        uploaded_files = {}
        local_dir_path = Path(local_dir)
        file_counter = {}  # 用于计数不同类型的文件

        for file_path in local_dir_path.rglob("*"):
            if file_path.is_file():
                # 跳过Markdown文件（已单独上传）
                if file_path.suffix == '.md':
                    continue

                # 根据扩展名生成安全的文件名
                extension = file_path.suffix.lower()

                # 获取文件类型计数
                if extension not in file_counter:
                    file_counter[extension] = 0
                file_counter[extension] += 1

                # 生成安全的远程文件名：prefix/type_001.ext
                if extension in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
                    file_type = 'image'
                elif extension in ['.mp4', '.mov', '.avi']:
                    file_type = 'video'
                else:
                    file_type = 'file'

                safe_filename = f"{file_type}_{file_counter[extension]:03d}{extension}"
                remote_path = f"{remote_prefix}/{safe_filename}"

                # 上传文件
                with open(file_path, 'rb') as f:
                    file_data = f.read()

                # 确定 content-type
                content_type = self._get_content_type(extension)

                self.client.storage.from_(self.bucket).upload(
                    remote_path,
                    file_data,
                    file_options={"content-type": content_type}
                )

                public_url = self.client.storage.from_(self.bucket).get_public_url(remote_path)
                uploaded_files[str(file_path)] = public_url

        return uploaded_files

    def _get_content_type(self, extension: str) -> str:
        """根据文件扩展名获取 content-type"""
        content_types = {
            '.md': 'text/markdown; charset=utf-8',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.webp': 'image/webp',
            '.mp4': 'video/mp4',
            '.mov': 'video/quicktime',
            '.avi': 'video/x-msvideo',
        }
        return content_types.get(extension.lower(), 'application/octet-stream')

    def save_metadata(self, metadata: dict):
        """保存转换元数据到数据库"""
        try:
            self.client.table('conversions').insert(metadata).execute()
        except Exception as e:
            print(f"Warning: Could not save metadata: {e}")


# 初始化存储
try:
    storage = SupabaseStorage()
except Exception as e:
    print(f"Warning: Supabase not configured: {e}")
    storage = None


def process_conversion(url: str, download_media: bool) -> dict:
    """
    处理转换逻辑

    Args:
        url: 要转换的 URL
        download_media: 是否下载媒体资源

    Returns:
        转换结果字典
    """
    # 生成唯一的文件夹名称
    url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = f"{timestamp}_{url_hash}"

    # 创建临时目录
    with tempfile.TemporaryDirectory() as temp_dir:
        output_dir = os.path.join(temp_dir, "output")
        os.makedirs(output_dir, exist_ok=True)

        # 执行转换
        converter = HTML2Markdown(download_media=download_media)
        md_file_path = converter.convert(
            url=url,
            output_path=None,
            output_dir=output_dir
        )

        # 提取文件名（不含路径）
        md_filename = os.path.basename(md_file_path)
        base_name = os.path.splitext(md_filename)[0]

        # 上传到 Supabase
        if not storage:
            raise Exception("Supabase storage not configured")

        # 使用 URL 安全的文件名（避免中文和特殊字符）
        safe_filename = f"{unique_id}.md"

        # 上传 Markdown 文件
        md_remote_path = safe_filename
        md_public_url = storage.upload_file(md_file_path, md_remote_path)

        # 上传媒体文件（如果有）
        media_files = {}
        media_dir = os.path.join(output_dir, f"{base_name}_files")
        if download_media and os.path.exists(media_dir):
            # 使用 unique_id 作为远程路径前缀，确保路径安全
            media_files = storage.upload_directory(output_dir, f"{unique_id}_files")

        # 保存元数据
        metadata = {
            "id": str(uuid.uuid4()),
            "url": url,
            "md_file_url": md_public_url,
            "download_media": download_media,
            "created_at": datetime.utcnow().isoformat(),
            "media_count": len(media_files)
        }
        storage.save_metadata(metadata)

        return {
            "md_url": md_public_url,
            "md_filename": md_filename,
            "media_files": len(media_files),
            "unique_id": unique_id
        }


@app.get("/")
async def root():
    """API 根路径"""
    return {
        "service": "HTML to Markdown API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "convert": "/api/convert",
            "health": "/health"
        }
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    supabase_status = "connected" if storage else "not configured"

    # 检查依赖版本
    import requests
    import urllib3

    return {
        "status": "healthy",
        "supabase": supabase_status,
        "timestamp": datetime.utcnow().isoformat(),
        "dependencies": {
            "requests": requests.__version__,
            "urllib3": urllib3.__version__
        }
    }


@app.post("/api/convert", response_model=ConvertResponse)
async def convert_url(request: ConvertRequest, background_tasks: BackgroundTasks):
    """
    转换 URL 为 Markdown

    - **url**: 要转换的网页 URL
    - **download_media**: 是否下载媒体资源（默认 True）
    - **callback_url**: 可选的回调 URL（异步通知结果）
    """
    try:
        # 同步处理（小任务）
        result = process_conversion(str(request.url), request.download_media)

        return ConvertResponse(
            success=True,
            message="转换成功",
            data=result
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"转换失败: {str(e)}"
        )


@app.get("/api/convert")
async def convert_url_get(url: str, download_media: bool = True):
    """
    GET 方式转换 URL（方便测试和简单调用）

    参数:
    - url: 要转换的网页 URL
    - download_media: 是否下载媒体资源
    """
    try:
        result = process_conversion(url, download_media)

        return ConvertResponse(
            success=True,
            message="转换成功",
            data=result
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"转换失败: {str(e)}"
        )


# 用于 Cloudflare Workers 的入口
# 如果使用 Cloudflare Workers Python，需要特殊处理
if __name__ == "__main__":
    import uvicorn
    # 从环境变量获取端口，默认为8000
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
