#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
样式管理器 - 从 JSON 配置文件加载样式
"""

import json
from pathlib import Path
from PyQt5.QtGui import QFont


class StyleManager:
    """样式管理器"""

    _instance = None
    _config = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_config()
        return cls._instance

    def _load_config(self):
        """加载配置文件"""
        config_path = Path(__file__).parent / "style_config.json"

        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    self._config = json.load(f)
            except:
                self._config = self._get_default_config()
        else:
            self._config = self._get_default_config()

    def _get_default_config(self):
        """获取默认配置"""
        return {
            "window": {
                "title": "BCacheTranslation",
                "min_width": 1100,
                "min_height": 800,
                "margins": [15, 15, 15, 15],
                "spacing": 10
            },
            "fonts": {
                "family": "Microsoft YaHei",
                "sizes": {
                    "global": 10,
                    "title": 22,
                    "button": 13,
                    "card_title": 16,
                    "card_detail": 12,
                    "card_status": 12,
                    "log": 12,
                    "label": 13,
                    "checkbox": 13
                }
            },
            "colors": {
                "primary": "#4299e1",
                "success": "#48bb78",
                "danger": "#f56565",
                "warning": "#ed8936",
                "info": "#718096",
                "dark": "#2d3748",
                "light": "#f7fafc",
                "border": "#cbd5e0",
                "background": "#ffffff",
                "log_bg": "#1a202c",
                "log_text": "#e2e8f0"
            },
            "sizes": {
                "drop_area_height": 120,
                "drop_area_padding": 25,
                "thumb_width": 160,
                "thumb_height": 90,
                "log_height": 150,
                "card_margin": 10,
                "card_padding": 10
            },
            "buttons": {
                "select_all": {"text": "✓ 全选", "color": "#48bb78"},
                "deselect_all": {"text": "✗ 取消全选", "color": "#ed8936"},
                "output_dir": {"text": "📂 输出目录", "color": "#4299e1"},
                "reset_output": {"text": "🔄 重置默认", "color": "#718096"},
                "start": {"text": "▶ 处理选中的视频", "color": "#48bb78"},
                "stop": {"text": "⏹ 停止", "color": "#f56565"}
            },
            "status_colors": {
                "PENDING": "#718096",
                "PROCESSING": "#4299e1",
                "SUCCESS": "#48bb78",
                "FAILED": "#f56565",
                "SKIPPED": "#a0aec0"
            }
        }

    def get(self, key, default=None):
        """获取配置值"""
        keys = key.split('.')
        value = self._config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
        return value if value is not None else default

    # 窗口相关
    def get_window_title(self):
        return self.get('window.title', 'BCacheTranslation')

    def get_window_min_width(self):
        return self.get('window.min_width', 1100)

    def get_window_min_height(self):
        return self.get('window.min_height', 800)

    def get_window_margins(self):
        return self.get('window.margins', [15, 15, 15, 15])

    def get_window_spacing(self):
        return self.get('window.spacing', 10)

    def apply_window_properties(self, window):
        """应用窗口属性"""
        window.setMinimumSize(self.get_window_min_width(), self.get_window_min_height())

    # 字体相关
    def get_font_size(self, name):
        """获取字体大小"""
        return self.get(f'fonts.sizes.{name}', 12)

    def get_global_font(self):
        """获取全局字体"""
        font = QFont()
        family = self.get('fonts.family', 'Microsoft YaHei')
        font.setFamily(family)
        return font

    # 颜色相关
    def get_color(self, name):
        """获取颜色"""
        return self.get(f'colors.{name}', '#000000')

    def get_status_color(self, status):
        """获取状态颜色"""
        return self.get(f'status_colors.{status}', '#718096')

    # 尺寸相关
    def get_drop_area_height(self):
        return self.get('sizes.drop_area_height', 120)

    def get_thumb_size(self):
        return self.get('sizes.thumb_width', 160), self.get('sizes.thumb_height', 90)

    def get_log_height(self):
        return self.get('sizes.log_height', 150)

    # 按钮相关
    def get_button_text(self, button_name):
        """获取按钮文字"""
        return self.get(f'buttons.{button_name}.text', button_name)

    def get_button_color(self, button_name):
        """获取按钮颜色"""
        return self.get(f'buttons.{button_name}.color', '#4299e1')

    def get_button_style(self, button_name):
        """获取按钮样式"""
        btn_config = self.get(f'buttons.{button_name}')
        if not btn_config:
            return ""

        color = btn_config.get('color', '#4299e1')
        font_size = self.get_font_size('button')

        # 颜色变暗
        hover_color = self._darken_color(color)

        return f"""
            QPushButton {{
                background-color: {color};
                color: white;
                font-size: {font_size}px;
                font-weight: bold;
                padding: 8px 16px;
                border-radius: 6px;
                border: none;
            }}
            QPushButton:hover {{
                background-color: {hover_color};
            }}
            QPushButton:disabled {{
                background-color: #a0aec0;
            }}
            QPushButton:pressed {{
                background-color: {self._darken_color(hover_color)};
            }}
        """

    def _darken_color(self, color):
        """颜色变暗（简单处理）"""
        dark_map = {
            "#48bb78": "#38a169",
            "#f56565": "#e53e3e",
            "#4299e1": "#3182ce",
            "#ed8936": "#dd6b20",
            "#718096": "#4a5568"
        }
        return dark_map.get(color, color)

    # 样式字符串
    def get_drop_area_style(self):
        """获取拖拽区域样式"""
        border_color = self.get_color('border')
        bg_color = self.get_color('light')
        text_color = self.get_color('info')
        primary_color = self.get_color('primary')
        padding = self.get('sizes.drop_area_padding', 25)

        return f"""
            QLabel {{
                border: 2px dashed {border_color};
                border-radius: 10px;
                background-color: {bg_color};
                color: {text_color};
                font-size: 14px;
                padding: {padding}px;
            }}
        """

    def get_drop_area_hover_style(self):
        """获取拖拽区域悬停样式"""
        primary_color = self.get_color('primary')
        bg_color = self.get_color('card_hover')

        return f"""
            QLabel {{
                border: 2px solid {primary_color};
                border-radius: 10px;
                background-color: {bg_color};
                color: {primary_color};
                font-size: 14px;
                padding: 25px;
            }}
        """

    def get_log_style(self):
        """获取日志区域样式"""
        log_bg = self.get_color('log_bg')
        log_text = self.get_color('log_text')
        border_color = self.get_color('border')
        font_size = self.get_font_size('log')

        return f"""
            QTextEdit {{
                font-family: Consolas, monospace;
                font-size: {font_size}px;
                background-color: {log_bg};
                color: {log_text};
                border: 1px solid {border_color};
                border-radius: 6px;
            }}
        """

    def get_card_style(self):
        """获取卡片样式"""
        radius = self.get('sizes.card_radius', 12)
        margin = self.get('sizes.card_margin', 12)
        bg_color = self.get('colors.card_bg', '#313244')
        hover_color = self.get('colors.card_hover', '#45475a')
        border_color = self.get('colors.border', '#45475a')

        return f"""
            VideoCardWidget {{
                background-color: {bg_color};
                border: 1px solid {border_color};
                border-radius: {radius}px;
                margin: {margin}px;
            }}
            VideoCardWidget:hover {{
                background-color: {hover_color};
                border-color: #6366f1;
            }}
        """

    def get_drop_area_style(self):
        """获取拖拽区域样式"""
        border_color = self.get_color('border')
        bg_color = self.get_color('light')
        text_color = self.get_color('info')
        primary_color = self.get_color('primary')
        padding = self.get('sizes.drop_area_padding', 25)

        return f"""
            QLabel {{
                border: 2px dashed {border_color};
                border-radius: 10px;
                background-color: {bg_color};
                color: {text_color};
                font-size: 14px;
                padding: {padding}px;
            }}
        """

    def get_drop_area_hover_style(self):
        """获取拖拽区域悬停样式"""
        primary_color = self.get_color('primary')
        bg_color = self.get_color('card_hover')

        return f"""
            QLabel {{
                border: 2px solid {primary_color};
                border-radius: 10px;
                background-color: {bg_color};
                color: {primary_color};
                font-size: 14px;
                padding: 25px;
            }}
        """

    def get_log_style(self):
        """获取日志区域样式"""
        log_bg = self.get_color('log_bg')
        log_text = self.get_color('log_text')
        border_color = self.get_color('border')
        font_size = self.get_font_size('log')

        return f"""
            QTextEdit {{
                font-family: Consolas, monospace;
                font-size: {font_size}px;
                background-color: {log_bg};
                color: {log_text};
                border: 1px solid {border_color};
                border-radius: 6px;
            }}
        """

    def get_card_style(self):
        """获取卡片样式"""
        radius = self.get('sizes.card_radius', 12)
        margin = self.get('sizes.card_margin', 12)
        bg_color = self.get('colors.card_bg', '#313244')
        hover_color = self.get('colors.card_hover', '#45475a')
        border_color = self.get('colors.border', '#45475a')

        return f"""
            VideoCardWidget {{
                background-color: {bg_color};
                border: 1px solid {border_color};
                border-radius: {radius}px;
                margin: {margin}px;
            }}
            VideoCardWidget:hover {{
                background-color: {hover_color};
                border-color: #6366f1;
            }}
        """

    def get_scroll_area_style(self):
        """获取滚动区域样式"""
        border_color = self.get_color('border')

        return f"""
            QScrollArea {{
                border: none;
                background: transparent;
            }}
            QScrollBar:vertical {{
                background: {border_color};
                width: 8px;
                border-radius: 4px;
            }}
            QScrollBar::handle:vertical {{
                background: #6c7086;
                border-radius: 4px;
                min-height: 30px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: #89b4fa;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0;
            }}
        """


# 全局单例
style_manager = StyleManager()