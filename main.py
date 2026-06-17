#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""程序入口"""

import sys
import os
import traceback
from pathlib import Path
from datetime import datetime

# 设置调试模式
if '--debug' in sys.argv or os.environ.get('BILI_DEBUG') == '1':
    os.environ['BILI_DEBUG'] = '1'
    print("调试模式已启用，日志将写入 logs/ 目录")

from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QFont, QFontDatabase
from PyQt5.QtCore import Qt

from logger import debug_logger


def load_fonts():
    """加载内置字体"""
    font_dir = Path(__file__).parent / "fonts"
    if not font_dir.exists():
        return

    loaded = 0
    for ext in ["*.ttf", "*.ttc", "*.otf"]:
        for font_file in font_dir.glob(ext):
            font_id = QFontDatabase.addApplicationFont(str(font_file))
            if font_id != -1:
                loaded += 1
                debug_logger.info(f"已加载字体: {font_file.name}")

    if loaded > 0:
        debug_logger.info(f"共加载 {loaded} 个字体文件")


def get_chinese_font():
    """获取可用的中文字体"""
    # 方法1：检查内置字体（从 QFontDatabase 获取）
    try:
        font_families = []
        for i in range(QFontDatabase.applicationFontCount()):
            font_families.extend(QFontDatabase.applicationFontFamilies(i))

        for family in font_families:
            if "Noto Sans" in family or "Source Han" in family:
                return family
    except:
        pass

    # 方法2：使用系统字体（直接用 QFont 测试）
    system_fonts = [
        "Microsoft YaHei",
        "PingFang SC",
        "Noto Sans CJK SC",
        "SimHei",
        "SimSun",
        "WenQuanYi Micro Hei",
        "Arial Unicode MS",
        "Arial",
    ]

    # 逐个测试字体是否可用
    for font_name in system_fonts:
        font = QFont(font_name)
        # 如果字体存在，QFont 的 family() 会返回设置的名称
        if font.family() == font_name:
            return font_name

    return "Arial"


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

        # 加载内置字体
        load_fonts()

        # 设置中文字体
        font_family = get_chinese_font()
        font = QFont(font_family, 11)
        app.setFont(font)
        debug_logger.info(f"使用字体: {font_family}")

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