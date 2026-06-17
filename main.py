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
        print(f"[字体] 已加载 {loaded} 个内置字体")
    else:
        print("[字体] 未找到内置字体文件")


def get_chinese_font():
    """获取可用的中文字体"""
    # 方法1：检查内置字体
    try:
        font_families = []
        for i in range(QFontDatabase.applicationFontCount()):
            font_families.extend(QFontDatabase.applicationFontFamilies(i))

        print(f"[字体] 可用字体列表: {font_families[:5]}...")  # 只显示前5个

        for family in font_families:
            if "Noto Sans" in family or "Noto Serif" in family or "Source Han" in family:
                print(f"[字体] 找到内置字体: {family}")
                return family
    except Exception as e:
        print(f"[字体] 检查内置字体时出错: {e}")

    # 方法2：使用系统字体
    system_fonts = [
        "Microsoft YaHei",
        "PingFang SC",
        "Noto Sans CJK SC",
        "Noto Serif CJK SC",
        "SimHei",
        "SimSun",
        "WenQuanYi Micro Hei",
        "Arial Unicode MS",
        "Arial",
    ]

    for font_name in system_fonts:
        font = QFont(font_name)
        if font.family() == font_name:
            print(f"[字体] 使用系统字体: {font_name}")
            return font_name

    print("[字体] 未找到任何中文字体，使用默认字体")
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

        # ========== 字体加载信息（调试） ==========
        print("\n" + "=" * 50)
        print("字体加载信息:")
        print(f"  选择的字体: {font_family}")
        print(f"  QFont 实际字体: {app.font().family()}")

        # 检查内置字体文件
        font_dir = Path(__file__).parent / "fonts"
        if font_dir.exists():
            font_files = list(font_dir.glob("*.otf")) + list(font_dir.glob("*.ttf")) + list(font_dir.glob("*.ttc"))
            if font_files:
                print(f"  内置字体文件: {[f.name for f in font_files]}")
            else:
                print("  内置字体目录存在，但无字体文件")
        else:
            print("  fonts/ 目录不存在")

        # 检查系统可用字体
        try:
            available = [QFontDatabase.applicationFontFamilies(i)[0]
                         for i in range(QFontDatabase.applicationFontCount())]
            print(f"  已注册字体数: {len(available)}")
        except:
            print("  无法获取已注册字体数")

        # 显示正在使用的字体路径
        print(f"  使用的字体族: {app.font().family()}")
        print("=" * 50 + "\n")
        # ========== 调试输出结束 ==========

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