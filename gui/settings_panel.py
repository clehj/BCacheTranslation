#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""设置面板"""

from PyQt5.QtWidgets import QHBoxLayout, QCheckBox, QLabel
from PyQt5.QtCore import Qt

from style_manager import style_manager


class SettingsPanel:
    """设置面板"""

    def __init__(self, parent, settings):
        self.parent = parent
        self.settings = settings
        self.extract_mp3_cb = None
        self.selected_count_label = None

    def create(self, layout):
        """创建设置面板"""
        options_layout = QHBoxLayout()
        options_layout.setContentsMargins(0, 0, 0, 0)

        self.extract_mp3_cb = QCheckBox("同时提取MP3音频")
        self.extract_mp3_cb.setStyleSheet(f"""
            QCheckBox {{
                font-size: {style_manager.get_font_size('checkbox')}px;
                color: #cdd6f4;
            }}
            QCheckBox::indicator {{
                width: 16px;
                height: 16px;
            }}
        """)
        self.extract_mp3_cb.setChecked(self.settings.get_extract_mp3())
        self.extract_mp3_cb.stateChanged.connect(self.parent.on_extract_mp3_changed)
        options_layout.addWidget(self.extract_mp3_cb)

        options_layout.addStretch()

        self.selected_count_label = QLabel("已选择: 0 个视频")
        self.selected_count_label.setStyleSheet(
            f"font-size: {style_manager.get_font_size('label')}px; color: #a6adc8;"
        )
        options_layout.addWidget(self.selected_count_label)

        layout.addLayout(options_layout)

    def update_selected_count(self, count, total):
        if self.selected_count_label:
            self.selected_count_label.setText(f"已选择: {count}/{total} 个视频")

    def get_extract_mp3(self):
        return self.extract_mp3_cb.isChecked() if self.extract_mp3_cb else True