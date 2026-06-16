#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""用户设置管理"""

import json
from pathlib import Path
from typing import Optional


class SettingsManager:
    """用户设置管理器"""

    _instance = None
    _settings = {}
    _settings_file = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init()
        return cls._instance

    def _init(self):
        """初始化"""
        self._settings_file = Path(__file__).parent / "settings.json"
        self._load()

    def _load(self):
        """加载设置"""
        if self._settings_file.exists():
            try:
                with open(self._settings_file, 'r', encoding='utf-8') as f:
                    self._settings = json.load(f)
            except:
                self._settings = self._get_default()
        else:
            self._settings = self._get_default()

    def _get_default(self):
        """默认设置"""
        return {
            "cache_dir": "",  # 缓存目录
            "output_dir": "",  # 输出目录
            "extract_mp3": True,  # 是否提取MP3
            "first_run": True  # 是否首次运行
        }

    def save(self):
        """保存设置"""
        try:
            with open(self._settings_file, 'w', encoding='utf-8') as f:
                json.dump(self._settings, f, ensure_ascii=False, indent=2)
        except:
            pass

    def get(self, key, default=None):
        """获取设置"""
        return self._settings.get(key, default)

    def set(self, key, value):
        """设置值"""
        self._settings[key] = value
        self.save()

    def get_cache_dir(self) -> Optional[str]:
        """获取缓存目录"""
        cache_dir = self.get('cache_dir', '')
        if cache_dir and Path(cache_dir).exists():
            return cache_dir
        return None

    def get_output_dir(self) -> Optional[str]:
        """获取输出目录"""
        output_dir = self.get('output_dir', '')
        if output_dir and Path(output_dir).exists():
            return output_dir
        return None

    def get_extract_mp3(self) -> bool:
        """获取是否提取MP3"""
        return self.get('extract_mp3', True)

    def set_cache_dir(self, path: str):
        self.set('cache_dir', path)

    def set_output_dir(self, path: str):
        self.set('output_dir', path)

    def set_extract_mp3(self, value: bool):
        self.set('extract_mp3', value)

    def is_first_run(self) -> bool:
        """是否首次运行"""
        return self.get('first_run', True)

    def set_first_run_done(self):
        self.set('first_run', False)