#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""工作线程"""

from typing import List
from pathlib import Path

from PyQt5.QtCore import QThread, pyqtSignal

from core import BatchProcessor, VideoInfo
from logger import debug_logger


class ProcessingThread(QThread):
    log = pyqtSignal(str)
    finished = pyqtSignal(list)

    def __init__(self, processor: BatchProcessor, videos: List[VideoInfo],
                 output_dir: str, extract_mp3: bool):
        super().__init__()
        self.processor = processor
        self.videos = videos
        self.output_dir = output_dir
        self.extract_mp3 = extract_mp3

    def run(self):
        debug_logger.info(f"ProcessingThread 启动，视频数: {len(self.videos)}")

        try:
            cache_dirs = [v.cache_dir for v in self.videos]
            debug_logger.debug(f"缓存目录: {cache_dirs}")

            # 直接使用 self.log.emit 作为回调
            results = self.processor.process_batch(
                cache_dirs, self.output_dir, self.extract_mp3,
                fix=True,
                log_callback=self.log.emit  # 直接使用 log.emit
            )

            debug_logger.info(f"处理完成，结果数: {len(results)}")
            self.finished.emit(results)

        except Exception as e:
            debug_logger.exception(f"ProcessingThread 异常: {str(e)}")
            self.log.emit(f"线程异常: {str(e)}")

    def stop(self):
        debug_logger.info("ProcessingThread 收到停止信号")
        self.processor.stop()


class ScanThread(QThread):
    progress = pyqtSignal(str)
    batch_found = pyqtSignal(list)
    finished = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, restorer, directory, max_videos=50):
        super().__init__()
        self.restorer = restorer
        self.directory = directory
        self.max_videos = max_videos
        self._stop_flag = False

    def stop(self):
        self._stop_flag = True

    def run(self):
        try:
            cache_dirs = self.restorer.scan_cache_dirs(self.directory)
            if not cache_dirs:
                self.error.emit("未找到任何缓存视频文件")
                return

            total = len(cache_dirs)
            if total > self.max_videos:
                self.progress.emit(f"找到 {total} 个缓存，只显示前 {self.max_videos} 个")
                cache_dirs = cache_dirs[:self.max_videos]
            else:
                self.progress.emit(f"找到 {total} 个缓存视频")

            # 收集所有视频信息
            videos = []
            for i, cache_dir in enumerate(cache_dirs):
                if self._stop_flag:
                    self.progress.emit("扫描已取消")
                    break

                if i % 5 == 0:
                    self.progress.emit(f"解析中... {i + 1}/{len(cache_dirs)}")

                info = self.restorer.parse_video_info(cache_dir)
                if info:
                    videos.append(info)

                self.msleep(10)

            # 一次性发送所有视频
            if videos:
                self.batch_found.emit(videos)

            self.finished.emit()
        except Exception as e:
            self.error.emit(f"扫描出错: {str(e)}")