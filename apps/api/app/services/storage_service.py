from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile

from apps.api.app.core.config import get_settings


ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}


def save_upload_file(file: UploadFile) -> tuple[str, str, int]:
    """保存用户上传的图片到本地目录。

    返回值：
    - object_key：文件在存储系统中的相对路径
    - public_url：前端可以访问的图片地址
    - file_size：文件大小，单位字节

    现在先实现本地存储。后续如果切阿里云 OSS，只需要保留这个函数的调用方式，
    内部改成上传到 OSS，并返回 OSS 的 object_key/public_url。
    """

    settings = get_settings()
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise ValueError("只支持 JPG、PNG、WEBP 图片")

    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)

    suffix = Path(file.filename or "image").suffix.lower()
    if suffix not in {".jpg", ".jpeg", ".png", ".webp"}:
        suffix = ".jpg"

    stored_filename = f"{uuid4().hex}{suffix}"
    target = upload_dir / stored_filename

    content = file.file.read()
    target.write_bytes(content)

    object_key = stored_filename
    public_url = f"{settings.public_upload_base_url.rstrip('/')}/{stored_filename}"
    return object_key, public_url, len(content)
