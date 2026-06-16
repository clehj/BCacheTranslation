#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BCacheTranslation - 核心处理模块
"""

import os
import sys
import json
import subprocess
import tempfile
import shutil
import atexit
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass
from enum import Enum


def _get_app_dir() -> Path:
    """获取应用根目录（兼容 PyInstaller 打包和源码运行）"""
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).parent
    return Path(__file__).parent


def _find_ffmpeg() -> str:
    """自动查找 ffmpeg 路径

    查找顺序：
    1. PyInstaller 打包目录中的 ffmpeg/
    2. 应用目录下的 ffmpeg/
    3. 系统 PATH
    """
    app_dir = _get_app_dir()
    ffmpeg_exe = "ffmpeg.exe" if os.name == 'nt' else "ffmpeg"

    # 1. 打包内置目录
    bundled_dir = app_dir / "ffmpeg" / ffmpeg_exe
    if bundled_dir.exists():
        return str(bundled_dir)

    # 2. 如果是 PyInstaller 打包，检查 _MEIPASS 中的资源
    if getattr(sys, 'frozen', False):
        meipass_dir = Path(sys._MEIPASS) / "ffmpeg" / ffmpeg_exe
        if meipass_dir.exists():
            return str(meipass_dir)

    # 3. 回退到系统 PATH
    return "ffmpeg"


class ProcessStatus(Enum):
    PENDING = "等待"
    PROCESSING = "处理中"
    SUCCESS = "成功"
    FAILED = "失败"
    SKIPPED = "跳过"


@dataclass
class VideoInfo:
    title: str
    cache_dir: Path
    video_file: Optional[Path] = None
    audio_file: Optional[Path] = None
    size_mb: float = 0.0
    status: ProcessStatus = ProcessStatus.PENDING
    error_msg: str = ""
    duration: int = 0


class BilibiliRestorer:
    def __init__(self, ffmpeg_path: Optional[str] = None):
        self.ffmpeg_path = ffmpeg_path or _find_ffmpeg()
        self._ffmpeg_available = None
        self.temp_files = []
        self.temp_dir = Path(__file__).parent / "temp"
        self.temp_dir.mkdir(exist_ok=True)
        atexit.register(self.cleanup_temp_files)

    def check_ffmpeg(self) -> bool:
        if self._ffmpeg_available is not None:
            return self._ffmpeg_available
        try:
            creation_flags = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            result = subprocess.run(
                [self.ffmpeg_path, '-version'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=creation_flags if os.name == 'nt' else 0
            )
            self._ffmpeg_available = result.returncode == 0
        except (subprocess.SubprocessError, FileNotFoundError):
            self._ffmpeg_available = False
        return self._ffmpeg_available

    def cleanup_temp_files(self):
        """清理所有临时文件"""
        for temp_file in self.temp_files:
            if temp_file and temp_file.exists():
                try:
                    temp_file.unlink()
                except:
                    pass
        self.temp_files.clear()

        if self.temp_dir.exists():
            for f in self.temp_dir.iterdir():
                try:
                    if f.is_file():
                        f.unlink()
                except:
                    pass

    def _add_temp_file(self, file_path: Path):
        if file_path not in self.temp_files:
            self.temp_files.append(file_path)

    def get_default_bilibili_cache_dir(self) -> Optional[Path]:
        """获取B站客户端默认缓存目录"""
        possible_paths = [
            Path.home() / "Videos" / "bilibili",
            Path.home() / "Downloads" / "bilibili",
            Path("D:/System/Videos/bilibili"),
        ]
        for path in possible_paths:
            if path.exists():
                return path
        return None

    def scan_cache_dirs(self, root_path: str) -> List[Path]:
        """扫描缓存目录（只扫描一级子目录）"""
        cache_dirs = []
        root = Path(root_path)
        try:
            for item in root.iterdir():
                if item.is_dir() and list(item.glob("*.m4s")):
                    cache_dirs.append(item)
        except Exception as e:
            print(f"扫描出错: {e}")
        return cache_dirs

    def parse_video_info(self, cache_dir: Path, log_callback=None) -> Optional[VideoInfo]:
        """只读取元数据，不处理视频文件"""
        info = VideoInfo(
            title=cache_dir.name,
            cache_dir=cache_dir
        )

        m4s_files = [f for f in cache_dir.glob("*.m4s") if not f.name.startswith('_')]
        if not m4s_files:
            return None

        m4s_files.sort(key=lambda x: x.stat().st_size, reverse=True)
        info.video_file = m4s_files[0]
        info.audio_file = m4s_files[1] if len(m4s_files) >= 2 else None

        info_file = cache_dir / "videoInfo.json"
        if info_file.exists():
            try:
                with open(info_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    info.title = data.get('title', '') or data.get('tabName', '') or info.title
                    info.duration = data.get('duration', 0)
            except:
                pass

        total_size = info.video_file.stat().st_size
        if info.audio_file:
            total_size += info.audio_file.stat().st_size
        info.size_mb = total_size / 1024 / 1024

        return info

    def remove_leading_zeros(self, file_path: Path, log_callback=None) -> Path:
        """删除文件开头的所有 '0' 字符（用于预览）"""
        try:
            if file_path.parent == self.temp_dir:
                return file_path

            with open(file_path, 'rb') as f:
                first_chunk = f.read(65536)

            zero_count = 0
            for byte in first_chunk:
                if byte == 0x30:
                    zero_count += 1
                else:
                    break

            if zero_count == 0:
                return file_path

            temp_file = self.temp_dir / f"preview_{file_path.stem}{file_path.suffix}"
            with open(file_path, 'rb') as f_in:
                f_in.seek(zero_count)
                with open(temp_file, 'wb') as f_out:
                    while True:
                        chunk = f_in.read(1024 * 1024)
                        if not chunk:
                            break
                        f_out.write(chunk)

            self._add_temp_file(temp_file)
            return temp_file
        except Exception as e:
            if log_callback:
                log_callback(f"清理失败: {e}")
            return file_path

    def _clean_file(self, file_path: Path) -> Path:
        """清理单个文件的前导0，返回临时文件路径（用于处理）"""
        with open(file_path, 'rb') as f:
            first_chunk = f.read(65536)

        zero_count = 0
        for byte in first_chunk:
            if byte == 0x30:
                zero_count += 1
            else:
                break

        if zero_count == 0:
            return file_path

        temp_file = self.temp_dir / f"{file_path.stem}_cleaned{file_path.suffix}"
        with open(file_path, 'rb') as f_in:
            f_in.seek(zero_count)
            with open(temp_file, 'wb') as f_out:
                while True:
                    chunk = f_in.read(1024 * 1024)
                    if not chunk:
                        break
                    f_out.write(chunk)

        self._add_temp_file(temp_file)
        return temp_file

    def remux_to_standard(self, input_file: Path, output_file: Path,
                          is_audio: bool = False) -> bool:
        """重新编码为标准格式"""
        temp_output = self.temp_dir / f"temp_{output_file.name}"

        if is_audio:
            cmd = [self.ffmpeg_path, '-y', '-i', str(input_file),
                   '-c:a', 'libmp3lame', '-b:a', '192k',
                   '-ar', '44100', '-ac', '2', str(temp_output)]
        else:
            cmd = [self.ffmpeg_path, '-y', '-i', str(input_file),
                   '-c:v', 'libx264', '-preset', 'fast', '-crf', '18',
                   '-c:a', 'aac', '-b:a', '192k', '-ar', '44100', '-ac', '2',
                   '-movflags', '+faststart', str(temp_output)]

        try:
            creation_flags = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                    creationflags=creation_flags, timeout=600)

            if result.returncode == 0 and temp_output.exists():
                shutil.copy2(temp_output, output_file)
                temp_output.unlink()
                return True
            return False
        except:
            return False

    def convert_to_mp4(self, video_file: Path, audio_file: Optional[Path],
                       output_path: Path, log_callback=None) -> bool:
        """转换视频"""
        cleaned_video = self._clean_file(video_file)
        temp_video = self.temp_dir / f"temp_video_{output_path.stem}.mp4"

        if not self.remux_to_standard(cleaned_video, temp_video, is_audio=False):
            return False

        temp_audio = None
        if audio_file:
            cleaned_audio = self._clean_file(audio_file)
            temp_audio = self.temp_dir / f"temp_audio_{output_path.stem}.mp3"
            if not self.remux_to_standard(cleaned_audio, temp_audio, is_audio=True):
                temp_audio = None

        if temp_audio and temp_audio.exists():
            cmd = [self.ffmpeg_path, '-y', '-i', str(temp_video), '-i', str(temp_audio),
                   '-c', 'copy', '-map', '0:v:0', '-map', '1:a:0', str(output_path)]
        else:
            cmd = [self.ffmpeg_path, '-y', '-i', str(temp_video), '-c', 'copy', str(output_path)]

        try:
            creation_flags = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                    creationflags=creation_flags, timeout=120)

            if result.returncode == 0 and output_path.exists():
                if temp_video.exists():
                    temp_video.unlink()
                if temp_audio and temp_audio.exists():
                    temp_audio.unlink()
                return True
            return False
        except:
            return False

    def extract_to_mp3(self, audio_file: Path, output_path: Path, log_callback=None) -> bool:
        """提取MP3"""
        if not audio_file or not audio_file.exists():
            return False
        cleaned_audio = self._clean_file(audio_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        return self.remux_to_standard(cleaned_audio, output_path, is_audio=True)

    def sanitize_filename(self, filename: str, max_length: int = 200) -> str:
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '')
        filename = filename.strip().strip('.')
        if not filename:
            filename = f"video_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        if len(filename) > max_length:
            filename = filename[:max_length]
        return filename

    def process_video(self, cache_dir: Path, output_dir: str,
                      extract_mp3: bool = True, log_callback=None) -> VideoInfo:
        info = self.parse_video_info(cache_dir)
        if not info:
            return VideoInfo(
                title=cache_dir.name,
                cache_dir=cache_dir,
                status=ProcessStatus.SKIPPED,
                error_msg="未找到有效视频文件"
            )

        info.status = ProcessStatus.PROCESSING

        try:
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
            safe_title = self.sanitize_filename(info.title)
            mp4_path = output_dir / f"{safe_title}.mp4"

            if self.convert_to_mp4(info.video_file, info.audio_file, mp4_path, log_callback):
                info.status = ProcessStatus.SUCCESS
                info.error_msg = f"MP4: {mp4_path.stat().st_size / 1024 / 1024:.1f}MB"

                if extract_mp3 and info.audio_file:
                    mp3_path = output_dir / f"{safe_title}.mp3"
                    if self.extract_to_mp3(info.audio_file, mp3_path, log_callback):
                        info.error_msg += f", MP3: {mp3_path.stat().st_size / 1024 / 1024:.1f}MB"
            else:
                info.status = ProcessStatus.FAILED
                info.error_msg = "转换失败"
        except Exception as e:
            info.status = ProcessStatus.FAILED
            info.error_msg = str(e)

        return info


class BatchProcessor:
    def __init__(self, restorer: BilibiliRestorer):
        self.restorer = restorer
        self._stop_flag = False

    def stop(self):
        self._stop_flag = True

    def process_batch(self, cache_dirs: List[Path], output_dir: str,
                      extract_mp3: bool = True, fix: bool = True,
                      log_callback=None) -> List[VideoInfo]:
        self._stop_flag = False
        results = []
        total = len(cache_dirs)

        for i, cache_dir in enumerate(cache_dirs, 1):
            if self._stop_flag:
                if log_callback:
                    log_callback("⚠ 用户中止处理")
                break

            if log_callback:
                log_callback(f"\n[{i}/{total}] 📁 {cache_dir.name}")

            result = self.restorer.process_video(cache_dir, output_dir, extract_mp3, fix, log_callback)
            results.append(result)

            if log_callback:
                if result.status == ProcessStatus.SUCCESS:
                    log_callback(f"  ✅ {result.error_msg}")
                elif result.status == ProcessStatus.FAILED:
                    log_callback(f"  ❌ {result.error_msg}")
                elif result.status == ProcessStatus.SKIPPED:
                    log_callback(f"  ⏭ {result.error_msg}")

        self.restorer.cleanup_temp_files()
        return results