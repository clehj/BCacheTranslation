#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""流式布局 - 自动换行"""

from PyQt5.QtCore import Qt, QPoint, QRect, QSize
from PyQt5.QtWidgets import QLayout, QSizePolicy

from gui.constants import CARD_WIDTH, CARD_SPACING


class FlowLayout(QLayout):
    """流式布局，自动换行"""

    def __init__(self, parent=None, margin=0, spacing=CARD_SPACING):
        super().__init__(parent)
        self._items = []
        self._margin = margin
        self._spacing = spacing

    def __del__(self):
        self._clear_items()

    def _clear_items(self):
        """清空所有项目"""
        while self._items:
            item = self._items.pop()
            if item.widget():
                item.widget().deleteLater()

    def addItem(self, item):
        self._items.append(item)

    def count(self):
        return len(self._items)

    def itemAt(self, index):
        if 0 <= index < len(self._items):
            return self._items[index]
        return None

    def takeAt(self, index):
        if 0 <= index < len(self._items):
            return self._items.pop(index)
        return None

    def expandingDirections(self):
        return Qt.Orientations(Qt.Horizontal)

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        return self._do_layout(QRect(0, 0, width, 0), True)

    def setGeometry(self, rect):
        super().setGeometry(rect)
        self._do_layout(rect, False)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        size = QSize()
        for item in self._items:
            size = size.expandedTo(item.minimumSize())

        left, top, right, bottom = self.getContentsMargins()
        size += QSize(left + right, top + bottom)
        return size

    def _do_layout(self, rect, test_only):
        """执行布局计算"""
        left, top, right, bottom = self.getContentsMargins()
        effective_rect = rect.adjusted(left, top, -right, -bottom)

        if effective_rect.width() <= 0:
            return 0

        # 获取可见控件
        visible_items = [
            item for item in self._items
            if item.widget() and item.widget().isVisible()
        ]

        if not visible_items:
            return 0

        # 计算每行最大卡片数
        max_per_row = max(1, (effective_rect.width() + CARD_SPACING) // (CARD_WIDTH + CARD_SPACING))

        # 计算居中偏移
        total_width = max_per_row * (CARD_WIDTH + CARD_SPACING) - CARD_SPACING
        x_offset = max(0, (effective_rect.width() - total_width) // 2)

        x = effective_rect.x() + x_offset
        y = effective_rect.y()
        line_height = 0
        spacing = self._spacing

        for i, item in enumerate(visible_items):
            widget = item.widget()
            if not widget:
                continue

            widget_height = widget.sizeHint().height()

            # 换行
            if i > 0 and i % max_per_row == 0:
                x = effective_rect.x() + x_offset
                y = y + line_height + spacing
                line_height = 0

            if not test_only:
                item.setGeometry(QRect(QPoint(x, y), QSize(CARD_WIDTH, widget_height)))

            x += CARD_WIDTH + spacing
            line_height = max(line_height, widget_height)

        return y + line_height - rect.y() + bottom