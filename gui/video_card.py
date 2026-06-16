#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""视频卡片组件"""

import os
from pathlib import Path

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from core import VideoInfo
from style_manager import style_manager
from gui.constants import CARD_WIDTH, THUMB_WIDTH, THUMB_HEIGHT


class VideoCardWidget(QWidget):
    """视频卡片组件"""
    video_selected = pyqtSignal(object, bool)

    def __init__(self, video_info: VideoInfo, parent=None):
        super().__init__(parent)
        self.video_info = video_info
        self.is_selected = False
        self.init_ui()
        self.setup_events()

    def setup_events(self):
        self.mousePressEvent = self.on_mouse_press
        self.mouseDoubleClickEvent = self.on_mouse_double_click

    def on_mouse_press(self, event):
        if event.button() == Qt.LeftButton:
            self.is_selected = not self.is_selected
            self.video_selected.emit(self.video_info, self.is_selected)
            self.update_selected_style()
        super().mousePressEvent(event)

    def on_mouse_double_click(self, event):
        if event.button() == Qt.LeftButton:
            self.show_details()
        super().mouseDoubleClickEvent(event)

    def update_selected_style(self):
        """更新选中样式"""
        if self.is_selected:
            self.setStyleSheet("""
                VideoCardWidget {
                    background-color: #45475a;
                    border: 2px solid #6366f1;
                    border-radius: 12px;
                }
                VideoCardWidget:hover {
                    background-color: #585b70;
                    border-color: #8187dc;
                }
            """)
        else:
            self.setStyleSheet("""
                VideoCardWidget {
                    background-color: #313244;
                    border: 1px solid #45475a;
                    border-radius: 12px;
                }
                VideoCardWidget:hover {
                    background-color: #45475a;
                    border-color: #6366f1;
                }
            """)

        self.style().unpolish(self)
        self.style().polish(self)
        self.update()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        self.setFixedWidth(CARD_WIDTH)
        self.setMinimumHeight(200)
        self.setStyleSheet("""
            VideoCardWidget {
                background-color: #313244;
                border: 1px solid #45475a;
                border-radius: 12px;
            }
            VideoCardWidget:hover {
                background-color: #45475a;
                border-color: #6366f1;
            }
        """)

        # 缩略图容器
        self.thumb_container = QFrame()
        self.thumb_container.setFixedSize(THUMB_WIDTH, THUMB_HEIGHT)
        self.thumb_container.setStyleSheet("""
            QFrame {
                background-color: #1e1e2e;
                border-radius: 8px;
                border: none;
            }
        """)

        self.thumb_label = QLabel(self.thumb_container)
        self.thumb_label.setGeometry(0, 0, THUMB_WIDTH, THUMB_HEIGHT)
        self.thumb_label.setAlignment(Qt.AlignCenter)
        self.thumb_label.setText("🎬")
        self.thumb_label.setFont(QFont("Segoe UI", 32))
        self.thumb_label.setStyleSheet("""
            QLabel {
                background-color: transparent;
                border-radius: 8px;
                color: #a6adc8;
            }
        """)

        layout.addWidget(self.thumb_container, alignment=Qt.AlignCenter)

        # 标题
        self.title_label = QLabel(self.video_info.title)
        self.title_label.setStyleSheet(f"""
            font-weight: 600;
            font-size: {style_manager.get_font_size('card_title')}px;
            color: #cdd6f4;
            line-height: 1.3;
            padding: 0 4px;
        """)
        self.title_label.setWordWrap(True)
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setFixedHeight(42)
        self.title_label.setToolTip(self.video_info.title)
        layout.addWidget(self.title_label)

        # 详细信息
        details = []
        if self.video_info.duration:
            minutes = self.video_info.duration // 60
            seconds = self.video_info.duration % 60
            details.append(f"⏱ {minutes}:{seconds:02d}")

        if self.video_info.size_mb > 0:
            details.append(f"💾 {self.video_info.size_mb:.1f} MB")

        self.detail_label = QLabel(" | ".join(details))
        self.detail_label.setStyleSheet(
            f"color: #a6adc8; font-size: {style_manager.get_font_size('card_detail')}px; padding: 0 4px;"
        )
        self.detail_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.detail_label)

        self.setLayout(layout)

    def update_thumbnail(self):
        """更新缩略图"""
        possible_names = ["image.jpg", "cover.jpg", "thumb.jpg", "thumbnail.jpg", "cover.png"]

        thumb_path = None
        for name in possible_names:
            test_path = self.video_info.cache_dir / name
            if test_path.exists():
                thumb_path = test_path
                break

        if thumb_path and thumb_path.exists():
            pixmap = QPixmap(str(thumb_path))
            if not pixmap.isNull():
                scaled = pixmap.scaled(THUMB_WIDTH, THUMB_HEIGHT,
                                       Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.thumb_label.setPixmap(scaled)
                self.thumb_label.setText("")
                return

        self.thumb_label.setText("🎬")

    def show_details(self):
        """显示详细信息"""
        try:
            video_size = "未知"
            audio_size = "未知"

            if self.video_info.video_file and self.video_info.video_file.exists():
                video_size = f"{self.video_info.video_file.stat().st_size / 1024 / 1024:.2f} MB"

            if self.video_info.audio_file and self.video_info.audio_file.exists():
                audio_size = f"{self.video_info.audio_file.stat().st_size / 1024 / 1024:.2f} MB"

            details = f"""
            标题: {self.video_info.title}
            目录: {self.video_info.cache_dir}
            状态: {self.video_info.status.value}
            总大小: {self.video_info.size_mb:.2f} MB

            视频文件: {self.video_info.video_file.name if self.video_info.video_file else '无'}
            视频大小: {video_size}

            音频文件: {self.video_info.audio_file.name if self.video_info.audio_file else '无'}
            音频大小: {audio_size}
            """
            QMessageBox.information(self, "视频详情", details)
        except Exception as e:
            QMessageBox.warning(self, "错误", f"获取详情失败: {e}")