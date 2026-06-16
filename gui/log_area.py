#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""日志区域"""

from datetime import datetime

from PyQt5.QtWidgets import QTextEdit, QLabel, QApplication
from PyQt5.QtCore import Qt

from style_manager import style_manager


class LogArea:
    """日志区域"""

    def __init__(self, parent):
        self.parent = parent
        self.log_text = None

    def create(self, layout):
        log_label = QLabel("处理日志")
        log_label.setStyleSheet(
            f"font-size: {style_manager.get_font_size('label')}px; font-weight: 500; color: #cdd6f4;"
        )
        layout.addWidget(log_label)

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(style_manager.get_log_height())
        self.log_text.setStyleSheet(style_manager.get_log_style())
        layout.addWidget(self.log_text)

    def add(self, message: str):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
        QApplication.processEvents()