import os
import shutil
import subprocess
from pathlib import Path

# 配置
APP_NAME = "BCacheTranslation"
VERSION = "2.0.0"
OUTPUT_DIR = "dist"


def clean():
    """清理构建目录"""
    for dir_name in ["build", OUTPUT_DIR, "__pycache__"]:
        shutil.rmtree(dir_name, ignore_errors=True)

    for pycache in Path(".").rglob("__pycache__"):
        shutil.rmtree(pycache, ignore_errors=True)


def build():
    cmd = [
        "pyinstaller",
        "--name", f"{APP_NAME}_v{VERSION}",
        "--windowed",
        "--icon", "icon.ico",
        "--add-data", f"style_config.json;.",
        "--add-data", f"version.py;.",
        "--add-data", f"ffmpeg;ffmpeg",
        "--hidden-import", "PyQt5.sip",
        "--hidden-import", "PyQt5.QtCore",
        "--hidden-import", "PyQt5.QtWidgets",
        "--hidden-import", "PyQt5.QtGui",
        "--collect-all", "PyQt5",  # 自动收集所有 PyQt5 依赖
        "--noconfirm",
        "main.py"
    ]
    subprocess.run(cmd, check=True)

if __name__ == "__main__":
    clean()
    build()