#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""拖拽区域组件"""

import os
from pathlib import Path

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from style_manager import style_manager


class DropArea(QLabel):
    files_dropped = pyqtSignal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setText("📁 拖拽缓存文件夹到任意位置")
        self.setMinimumHeight(60)
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("""
            QLabel {
                border: 1px dashed #45475a;
                border-radius: 8px;
                background-color: #313244;
                color: #a6adc8;
                font-size: 12px;
                padding: 15px;
            }
            QLabel:hover {
                border-color: #6366f1;
                background-color: #45475a;
                color: #89b4fa;
            }
        """)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
            self.setStyleSheet("""
                QLabel {
                    border: 2px solid #6366f1;
                    border-radius: 8px;
                    background-color: #45475a;
                    color: #89b4fa;
                    font-size: 12px;
                    padding: 15px;
                }
            """)
        else:
            event.ignore()

    def dragLeaveEvent(self, event):
        self.setStyleSheet("""
            QLabel {
                border: 1px dashed #45475a;
                border-radius: 8px;
                background-color: #313244;
                color: #a6adc8;
                font-size: 12px;
                padding: 15px;
            }
        """)

    def dropEvent(self, event):
        self.dragLeaveEvent(event)
        urls = []
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            if os.path.exists(path):
                urls.append(path)
        if urls:
            self.files_dropped.emit(urls)