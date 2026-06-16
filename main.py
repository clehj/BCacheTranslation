#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""程序入口"""

import sys
import os
import traceback  # 添加这行
from pathlib import Path
from datetime import datetime

# 设置调试模式
if '--debug' in sys.argv or os.environ.get('BILI_DEBUG') == '1':
    os.environ['BILI_DEBUG'] = '1'
    print("调试模式已启用，日志将写入 logs/ 目录")

from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

from logger import debug_logger


def global_exception_handler(exc_type, exc_value, exc_tb):
    """全局异常处理"""
    error_msg = ''.join(traceback.format_exception(exc_type, exc_value, exc_tb))

    error_dir = Path(__file__).parent / "errors"
    error_dir.mkdir(exist_ok=True)
    error_file = error_dir / f"crash_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    error_file.write_text(error_msg, encoding='utf-8')

    from PyQt5.QtWidgets import QMessageBox
    QMessageBox.critical(None, "程序崩溃",
                         f"程序发生错误，已保存错误日志:\n{error_file}\n\n请报告此问题。")

    sys.exit(1)


def main():
    sys.excepthook = global_exception_handler
    debug_logger.info("程序启动")

    try:
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

        app = QApplication(sys.argv)
        app.setApplicationName("BCacheTranslation")
        app.setApplicationVersion("2.0.0")
        app.setOrganizationName("BiliTool")
        app.setStyle('Fusion')

        font = QFont()
        font.setFamily("Microsoft YaHei")
        font.setPointSize(11)
        app.setFont(font)

        debug_logger.info("导入 GUI 模块...")
        from gui import MainWindow

        debug_logger.info("创建主窗口...")
        window = MainWindow()

        debug_logger.info("显示窗口...")
        window.show()

        debug_logger.info("进入事件循环...")
        sys.exit(app.exec_())

    except Exception as e:
        debug_logger.exception(f"程序崩溃: {str(e)}")
        raise


if __name__ == "__main__":
    main()