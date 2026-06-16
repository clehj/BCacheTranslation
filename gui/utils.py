#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""GUI工具函数"""

import re
from pathlib import Path
from typing import Optional
from datetime import datetime

from gui.constants import THUMB_ASPECT_RATIO


def format_duration(seconds: int) -> str:
    """格式化时长"""
    if not seconds:
        return "00:00"
    minutes = seconds // 60
    secs = seconds % 60
    return f"{minutes}:{secs:02d}"


def format_file_size(size_bytes: int) -> str:
    """格式化文件大小"""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / 1024 / 1024:.1f} MB"
    else:
        return f"{size_bytes / 1024 / 1024 / 1024:.2f} GB"


def sanitize_filename(filename: str, max_length: int = 200) -> str:
    """清理文件名"""
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '')
    filename = filename.strip().strip('.')
    if not filename:
        filename = f"video_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    if len(filename) > max_length:
        filename = filename[:max_length]
    return filename


def extract_numbers(text: str) -> Optional[str]:
    """提取文本中的数字"""
    match = re.search(r'\d+', text)
    return match.group() if match else None


def is_bilibili_cache_dir(directory: Path) -> bool:
    """判断是否为B站缓存目录"""
    if not directory.is_dir():
        return False
    m4s_files = list(directory.glob("*.m4s"))
    if not m4s_files:
        return False
    return (directory / "videoInfo.json").exists() or (directory / ".videoInfo").exists()


def get_thumb_size(width: int) -> tuple:
    """根据宽度计算缩略图尺寸（16:9）"""
    height = int(width * THUMB_ASPECT_RATIO)
    return width, height