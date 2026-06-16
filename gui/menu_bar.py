#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""菜单栏"""

from PyQt5.QtWidgets import QAction


class MenuBarBuilder:
    """菜单栏构建器"""

    MENU_BAR_STYLE = """
        QMenuBar {
            background-color: #1e1e2e;
            border-bottom: 1px solid #313244;
            padding: 4px;
            color: #cdd6f4;
        }
        QMenuBar::item {
            padding: 6px 12px;
            border-radius: 6px;
        }
        QMenuBar::item:selected {
            background-color: #313244;
        }
        QMenu {
            background-color: #1e1e2e;
            border: 1px solid #313244;
            border-radius: 8px;
            padding: 8px;
            color: #cdd6f4;
        }
        QMenu::item {
            padding: 6px 24px;
            border-radius: 4px;
        }
        QMenu::item:selected {
            background-color: #313244;
        }
    """

    def __init__(self, parent):
        self.parent = parent
        self.menubar = parent.menuBar()
        self.menubar.setStyleSheet(self.MENU_BAR_STYLE)

    def build(self):
        self._build_file_menu()
        self._build_edit_menu()
        self._build_help_menu()

    def _build_file_menu(self):
        file_menu = self.menubar.addMenu("文件")

        rescan_action = QAction("重新扫描", self.parent)
        rescan_action.triggered.connect(self.parent.rescan_cache)
        file_menu.addAction(rescan_action)

        file_menu.addSeparator()

        output_action = QAction("选择输出目录", self.parent)
        output_action.triggered.connect(self.parent.select_output)
        file_menu.addAction(output_action)

        reset_output_action = QAction("重置输出目录", self.parent)
        reset_output_action.triggered.connect(self.parent.reset_default_output)
        file_menu.addAction(reset_output_action)

        file_menu.addSeparator()

        exit_action = QAction("退出", self.parent)
        exit_action.triggered.connect(self.parent.close)
        file_menu.addAction(exit_action)

    def _build_edit_menu(self):
        edit_menu = self.menubar.addMenu("编辑")

        select_all_action = QAction("全选", self.parent)
        select_all_action.triggered.connect(self.parent.select_all)
        edit_menu.addAction(select_all_action)

        deselect_all_action = QAction("取消全选", self.parent)
        deselect_all_action.triggered.connect(self.parent.deselect_all)
        edit_menu.addAction(deselect_all_action)

        edit_menu.addSeparator()

        clear_action = QAction("清空列表", self.parent)
        clear_action.triggered.connect(self.parent.clear_video_list)
        edit_menu.addAction(clear_action)

    def _build_help_menu(self):
        help_menu = self.menubar.addMenu("帮助")

        about_action = QAction("关于", self.parent)
        about_action.triggered.connect(self.parent.show_about)
        help_menu.addAction(about_action)