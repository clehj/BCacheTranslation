#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""日志系统"""

import os
import sys
import logging
from pathlib import Path
from datetime import datetime


class DebugLogger:
    """调试日志管理器"""

    _instance = None
    _enabled = False
    _logger = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._setup()
        return cls._instance

    def _setup(self):
        """设置日志"""
        # 检查是否启用调试模式
        self._enabled = os.environ.get('BILI_DEBUG', '0') == '1'

        if not self._enabled:
            # 创建一个空的处理器，不输出任何东西
            self._logger = logging.getLogger('BiliTool')
            self._logger.addHandler(logging.NullHandler())
            return

        # 创建日志目录
        log_dir = Path(__file__).parent / 'logs'
        log_dir.mkdir(exist_ok=True)

        # 创建日志文件
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = log_dir / f'bili_tool_{timestamp}.log'

        # 配置日志
        self._logger = logging.getLogger('BiliTool')
        self._logger.setLevel(logging.DEBUG)

        # 文件处理器
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)

        # 控制台处理器（只显示 INFO 以上）
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # 格式
        formatter = logging.Formatter(
            '[%(asctime)s] [%(levelname)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        self._logger.addHandler(file_handler)
        self._logger.addHandler(console_handler)

        self._logger.info(f"日志文件: {log_file}")
        self._logger.info(f"调试模式已启用")

    def debug(self, msg):
        if self._enabled:
            self._logger.debug(msg)

    def info(self, msg):
        if self._enabled:
            self._logger.info(msg)

    def warning(self, msg):
        if self._enabled:
            self._logger.warning(msg)

    def error(self, msg):
        if self._enabled:
            self._logger.error(msg)

    def exception(self, msg):
        if self._enabled:
            self._logger.exception(msg)


# 全局实例
debug_logger = DebugLogger()


def log_exception(func):
    """装饰器：捕获异常并记录日志"""

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            debug_logger.exception(f"异常发生在 {func.__name__}: {str(e)}")
            raise

    return wrapper