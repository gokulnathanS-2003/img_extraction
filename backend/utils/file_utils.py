"""
File handling utilities
"""
import os
import uuid
from pathlib import Path
from typing import Optional
import aiofiles

from config import UPLOAD_DIR, IMAGES_DIR, ALLOWED_EXTENSIONS


def generate_unique_filename(original_filename: str) -> str:
    """Generate a unique filename preserving the extension"""
    ext = Path(original_filename).suffix
    return f"{uuid.uuid4().hex}{ext}"


def is_allowed_file(filename: str) -> bool:
    """Check if file extension is allowed"""
    ext = Path(filename).suffix.lower()
    return ext in ALLOWED_EXTENSIONS


async def save_upload_file(file_content: bytes, filename: str) -> Path:
    """Save uploaded file to disk"""
    unique_name = generate_unique_filename(filename)
    file_path = UPLOAD_DIR / unique_name
    
    async with aiofiles.open(file_path, 'wb') as f:
        await f.write(file_content)
    
    return file_path


def save_image(image_bytes: bytes, image_id: str, extension: str = "png") -> Path:
    """Save extracted image to disk"""
    image_path = IMAGES_DIR / f"{image_id}.{extension}"
    with open(image_path, 'wb') as f:
        f.write(image_bytes)
    return image_path


def cleanup_file(file_path: Path) -> bool:
    """Remove a file if it exists"""
    try:
        if file_path.exists():
            os.remove(file_path)
            return True
    except Exception:
        pass
    return False
