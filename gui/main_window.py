#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""主窗口"""

from pathlib import Path
from typing import List

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from core import BilibiliRestorer, BatchProcessor, VideoInfo, ProcessStatus
from gui.constants import CARD_WIDTH, AUTO_SCAN_DELAY, MAX_CARDS_PER_BATCH
from gui.drop_area import DropArea
from gui.flow_layout import FlowLayout
from gui.log_area import LogArea
from gui.menu_bar import MenuBarBuilder
from gui.settings_panel import SettingsPanel
from gui.video_card import VideoCardWidget
from gui.workers import ProcessingThread, ScanThread
from settings_manager import SettingsManager
from style_manager import style_manager


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.restorer = BilibiliRestorer()
        self.processor = BatchProcessor(self.restorer)
        self.settings = SettingsManager()

        self.processing_thread = None
        self.scan_thread = None
        self.is_scanning = False
        self.watcher = None
        self.last_check_time = 0
        self.is_checking = False

        self.video_cards = []
        self.selected_videos = []
        self.output_dir = None

        self.log_area = LogArea(self)
        self.settings_panel = SettingsPanel(self, self.settings)

        self._init_ui()
        self._check_ffmpeg()
        self._load_settings()

        QTimer.singleShot(AUTO_SCAN_DELAY, self.auto_scan_cache)

    def _init_ui(self):
        style_manager.apply_window_properties(self)
        self.setWindowTitle(style_manager.get_window_title())
        self.setAcceptDrops(True)

        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e2e;
            }
            QLabel {
                color: #cdd6f4;
            }
            QGroupBox {
                color: #cdd6f4;
                border: 1px solid #313244;
                border-radius: 6px;
                margin-top: 8px;
            }
            QGroupBox::title {
                color: #cdd6f4;
            }
            QCheckBox {
                color: #cdd6f4;
            }
            QProgressBar {
                background-color: #313244;
                border: none;
                border-radius: 4px;
                text-align: center;
                color: #cdd6f4;
            }
            QProgressBar::chunk {
                background-color: #6366f1;
                border-radius: 4px;
            }
        """)

        MenuBarBuilder(self).build()

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        margins = style_manager.get_window_margins()
        main_layout.setContentsMargins(*margins)
        main_layout.setSpacing(12)

        self.drop_area = DropArea()
        self.drop_area.setMinimumHeight(60)
        self.drop_area.files_dropped.connect(self.on_files_dropped)
        main_layout.addWidget(self.drop_area)

        list_label = QLabel("📺 缓存视频列表")
        list_label.setStyleSheet(
            f"font-size: {style_manager.get_font_size('label')}px; font-weight: 500; color: #cdd6f4;"
        )
        main_layout.addWidget(list_label)

        self.video_container = QWidget()
        self.video_container.setStyleSheet("background-color: transparent;")
        self.video_layout = FlowLayout(self.video_container, margin=20, spacing=20)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                background: #313244;
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: #6c7086;
                border-radius: 4px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover {
                background: #89b4fa;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0;
            }
        """)
        scroll_area.setWidget(self.video_container)
        main_layout.addWidget(scroll_area)

        self.settings_panel.create(main_layout)

        self.status_label = QLabel("就绪")
        self.status_label.setStyleSheet("color: #a6adc8; padding: 4px 5px; font-size: 11px;")
        main_layout.addWidget(self.status_label)

        self.log_area.create(main_layout)

        self._create_control_buttons(main_layout)

        self.output_label = QLabel("📂 输出目录: 未选择")
        self.output_label.setStyleSheet("color: #a6adc8; font-size: 10px; padding: 4px;")
        main_layout.addWidget(self.output_label)

    def _create_control_buttons(self, layout):
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)

        self.start_btn = QPushButton(style_manager.get_button_text('start'))
        self.start_btn.clicked.connect(self.start_processing)
        self.start_btn.setStyleSheet(style_manager.get_button_style('start'))
        btn_layout.addWidget(self.start_btn)

        self.stop_btn = QPushButton(style_manager.get_button_text('stop'))
        self.stop_btn.clicked.connect(self.stop_processing)
        self.stop_btn.setEnabled(False)
        self.stop_btn.setStyleSheet(style_manager.get_button_style('stop'))
        btn_layout.addWidget(self.stop_btn)

        btn_layout.addStretch()
        layout.addLayout(btn_layout)

    def _check_ffmpeg(self):
        if not self.restorer.check_ffmpeg():
            QMessageBox.critical(
                self, "缺少 ffmpeg",
                "未找到 ffmpeg！\n\n"
                "解决方法：\n"
                "1. 将 ffmpeg.exe 放入程序目录下的 ffmpeg 文件夹\n"
                "2. 或将 ffmpeg 添加到系统 PATH 环境变量\n\n"
                f"当前检测路径：\n{self.restorer.ffmpeg_path}"
            )

    def _load_settings(self):
        output_dir = self.settings.get_output_dir()
        if output_dir:
            self.output_dir = output_dir
            self.output_label.setText(f"📂 输出目录: {output_dir}")
        else:
            self._set_default_output_dir()

    def _set_default_output_dir(self):
        current_dir = Path(__file__).parent.parent
        default_output = current_dir / "output"
        default_output.mkdir(exist_ok=True)
        self.output_dir = str(default_output)
        self.output_label.setText(f"📂 输出目录: {self.output_dir}")
        self.add_log(f"默认输出目录: {self.output_dir}")

    def add_log(self, message: str):
        self.log_area.add(message)

    def add_video_card(self, video_info: VideoInfo):
        card = VideoCardWidget(video_info)
        card.video_selected.connect(self._on_video_selected)
        card.setFixedWidth(CARD_WIDTH)
        self.video_layout.addWidget(card)
        self.video_cards.append(card)
        card.update_thumbnail()
        self.video_layout.update()
        QApplication.processEvents()

    def _on_video_selected(self, video_info: VideoInfo, is_selected: bool):
        if is_selected:
            if video_info not in self.selected_videos:
                self.selected_videos.append(video_info)
        else:
            if video_info in self.selected_videos:
                self.selected_videos.remove(video_info)
        self._update_selected_count()

    def _update_selected_count(self):
        count = len(self.selected_videos)
        total = len(self.video_cards)
        self.settings_panel.update_selected_count(count, total)
        self.start_btn.setEnabled(count > 0)

    def select_all(self):
        for card in self.video_cards:
            if not card.is_selected:
                card.is_selected = True
                card.video_selected.emit(card.video_info, True)
        self._update_selected_count()

    def deselect_all(self):
        for card in self.video_cards:
            if card.is_selected:
                card.is_selected = False
                card.video_selected.emit(card.video_info, False)
        self._update_selected_count()

    def clear_video_list(self):
        if self.scan_thread and self.scan_thread.isRunning():
            self.scan_thread.stop()
            self.scan_thread.wait()
            self.is_scanning = False

        while self.video_layout.count():
            item = self.video_layout.takeAt(0)
            if item and item.widget():
                item.widget().deleteLater()

        self.video_cards.clear()
        self.selected_videos.clear()
        self._update_selected_count()
        self.add_log("🗑 已清空列表")

    def select_output(self):
        start_dir = self.output_dir or str(Path.cwd())
        directory = QFileDialog.getExistingDirectory(self, "选择输出目录", start_dir)
        if directory:
            self.output_dir = directory
            self.output_label.setText(f"📂 输出目录: {directory}")
            self.settings.set_output_dir(directory)
            self.add_log(f"输出目录已更改: {directory}")

    def reset_default_output(self):
        self._set_default_output_dir()
        self.settings.set_output_dir(self.output_dir)
        self.add_log(f"已重置为默认输出目录: {self.output_dir}")

    def on_extract_mp3_changed(self, state):
        self.settings.set_extract_mp3(state == Qt.Checked)

    def show_about(self):
        """关于对话框"""
        dialog = QDialog(self)
        dialog.setWindowTitle("关于")
        dialog.setWindowFlags(dialog.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        dialog.setFixedSize(400, 350)
        dialog.setStyleSheet("""
            QDialog {
                background-color: #1e1e2e;
            }
            QLabel {
                color: #cdd6f4;
            }
        """)

        layout = QVBoxLayout(dialog)
        layout.setAlignment(Qt.AlignCenter)

        # 标题
        title = QLabel("BCacheTranslation")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #89b4fa;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # 作者
        author = QLabel("软件作者: clehj")
        author.setAlignment(Qt.AlignCenter)
        layout.addWidget(author)

        # 版本
        version = QLabel("版本 1.0.0")
        version.setAlignment(Qt.AlignCenter)
        layout.addWidget(version)

        # 描述
        desc = QLabel("一个用于提取B站客户端缓存视频的工具")
        desc.setAlignment(Qt.AlignCenter)
        desc.setStyleSheet("color: #a6adc8;")
        layout.addWidget(desc)

        layout.addSpacing(20)

        # 功能特点
        features = QLabel("功能特点：")
        features.setStyleSheet("font-weight: bold; color: #89b4fa;")
        features.setAlignment(Qt.AlignCenter)
        layout.addWidget(features)

        for text in ["• 自动识别音视频文件", "• 批量转换MP4/MP3", "• 实时监控新缓存"]:
            label = QLabel(text)
            label.setAlignment(Qt.AlignCenter)
            layout.addWidget(label)

        layout.addSpacing(20)

        # 版权
        copyright_label = QLabel("© 2026 BiliTool")
        copyright_label.setAlignment(Qt.AlignCenter)
        copyright_label.setStyleSheet("color: #a6adc8;")
        layout.addWidget(copyright_label)

        layout.addSpacing(20)

        # 关闭按钮
        close_btn = QPushButton("关闭")
        close_btn.setFixedSize(100, 32)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #313244;
                color: #cdd6f4;
                border: 1px solid #45475a;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #45475a;
                border-color: #6366f1;
            }
        """)
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn, alignment=Qt.AlignCenter)

        dialog.exec_()

    def auto_scan_cache(self):
        if self.is_scanning:
            return

        cache_dir = self.settings.get_cache_dir()

        if cache_dir:
            self.add_log(f"使用上次的缓存目录: {cache_dir}")
            self.start_scan_thread(cache_dir)
        else:
            default_cache = self.restorer.get_default_bilibili_cache_dir()
            if default_cache and default_cache.exists():
                reply = QMessageBox.question(
                    self,
                    "发现B站缓存",
                    f"检测到B站缓存目录:\n{default_cache}\n\n是否自动扫描？\n\n启用后将实时监控新视频",
                    QMessageBox.Yes | QMessageBox.No
                )
                if reply == QMessageBox.Yes:
                    self.settings.set_cache_dir(str(default_cache))
                    self.start_scan_thread(str(default_cache))
                else:
                    self.add_log("请手动拖拽缓存文件夹到窗口")
            else:
                self.add_log("未检测到B站缓存目录，请手动拖拽")

    def start_scan_thread(self, directory: str):
        if self.is_scanning:
            self.add_log("⚠ 扫描进行中，请稍后...")
            return

        self.is_scanning = True
        self.clear_video_list()
        QApplication.processEvents()

        self.add_log(f"🔍 开始扫描目录: {directory}")
        self.status_label.setText("扫描中...")

        self.scan_thread = ScanThread(self.restorer, directory, max_videos=MAX_CARDS_PER_BATCH)
        self.scan_thread.progress.connect(self.on_scan_progress)
        self.scan_thread.batch_found.connect(self.on_batch_found)
        self.scan_thread.finished.connect(lambda: self.on_scan_finished(directory))
        self.scan_thread.error.connect(self.on_scan_error)
        self.scan_thread.start()

    def on_batch_found(self, videos: List[VideoInfo]):
        for video_info in videos:
            self.add_video_card(video_info)
            QApplication.processEvents()
        self.video_layout.update()

    def on_scan_finished(self, directory: str):
        self.is_scanning = False
        self.status_label.setText("就绪")
        self.add_log(f"✓ 扫描完成，共找到 {len(self.video_cards)} 个视频")
        self._update_selected_count()

        self.start_watcher(directory)

        if len(self.video_cards) == 0:
            self.add_log("未找到缓存视频文件")

    def on_scan_error(self, error_msg: str):
        self.is_scanning = False
        self.status_label.setText("就绪")
        self.add_log(f"❌ {error_msg}")

    def on_scan_progress(self, message: str):
        self.status_label.setText(message)

    def rescan_cache(self):
        cache_dir = self.settings.get_cache_dir()
        if cache_dir:
            self.start_scan_thread(cache_dir)
        else:
            self.auto_scan_cache()

    def start_watcher(self, directory: str):
        if self.watcher:
            self.watcher.deleteLater()

        self.watcher = QFileSystemWatcher()
        self.watcher.addPath(directory)
        self.watcher.directoryChanged.connect(self.on_directory_changed)
        self.add_log(f"📁 已开启监控: {directory}")

    def on_directory_changed(self, path: str):
        """目录发生变化时触发"""
        current_time = QDateTime.currentMSecsSinceEpoch()

        # 3秒内只触发一次
        if current_time - self.last_check_time < 3000:
            return

        self.last_check_time = current_time

        # 如果正在检查中，跳过
        if self.is_checking:
            return

        self.add_log(f"🔄 检测到目录变化: {path}")
        self.is_checking = True
        QTimer.singleShot(5000, self.check_new_videos)  # 延迟5秒再检查

    def check_new_videos(self):
        """检查新增的视频"""
        self.is_checking = False

        if self.is_scanning:
            return

        cache_dir = self.settings.get_cache_dir()
        if not cache_dir:
            return

        existing_dirs = {str(card.video_info.cache_dir) for card in self.video_cards}

        new_dirs = []
        for item in Path(cache_dir).iterdir():
            if item.is_dir() and str(item) not in existing_dirs:
                if list(item.glob("*.m4s")):
                    new_dirs.append(item)

        if new_dirs:
            self.add_log(f"✨ 发现 {len(new_dirs)} 个新视频")
            for new_dir in new_dirs:
                self.add_single_directory(str(new_dir))
        else:
            # 不打印"未发现新视频"，减少日志刷屏
            pass

    def on_files_dropped(self, paths: List[str]):
        for path in paths:
            path_obj = Path(path)
            if path_obj.is_file():
                if path_obj.suffix == '.m4s':
                    self.add_single_directory(str(path_obj.parent))
                else:
                    self.add_log(f"⚠ 忽略文件: {path_obj.name}")
            elif path_obj.is_dir():
                m4s_files = list(path_obj.glob("*.m4s"))
                if m4s_files:
                    self.add_single_directory(str(path_obj))
                else:
                    self.add_multiple_directories(str(path_obj))

    def add_single_directory(self, directory: str):
        self.add_log(f"🔍 添加目录: {directory}")
        cache_dir = Path(directory)

        for card in self.video_cards:
            if str(card.video_info.cache_dir) == directory:
                self.add_log(f"  ⚠ 目录已存在，跳过")
                return

        def log_callback(msg):
            self.add_log(msg)

        info = self.restorer.parse_video_info(cache_dir, log_callback=log_callback)
        if info:
            self.add_video_card(info)
            self.add_log(f"  ✓ 已添加: {info.title}")
            self.settings.set_cache_dir(directory)
            parent_dir = str(Path(directory).parent)
            self.start_watcher(parent_dir)
        else:
            self.add_log(f"  ⚠ 未找到有效视频文件")
        self._update_selected_count()

    def add_multiple_directories(self, directory: str):
        self.add_log(f"🔍 批量扫描: {directory}")
        cache_dirs = self.restorer.scan_cache_dirs(directory)
        if not cache_dirs:
            self.add_log(f"  ⚠ 未找到缓存视频")
            return

        total_found = len(cache_dirs)
        if total_found > MAX_CARDS_PER_BATCH:
            self.add_log(f"  找到 {total_found} 个缓存，只添加前 {MAX_CARDS_PER_BATCH} 个")
            cache_dirs = cache_dirs[:MAX_CARDS_PER_BATCH]
        else:
            self.add_log(f"  找到 {total_found} 个缓存")

        added_count = 0
        skipped_count = 0

        for i, cache_dir in enumerate(cache_dirs):
            exists = False
            for card in self.video_cards:
                if str(card.video_info.cache_dir) == str(cache_dir):
                    exists = True
                    break
            if exists:
                skipped_count += 1
                continue

            def log_callback():
                pass

            info = self.restorer.parse_video_info(cache_dir, log_callback=log_callback)
            if info:
                self.add_video_card(info)
                added_count += 1

            if (i + 1) % 10 == 0:
                self.add_log(f"  进度: {i + 1}/{len(cache_dirs)}")
                QApplication.processEvents()

        self.add_log(f"  ✓ 已添加 {added_count} 个新视频 (跳过 {skipped_count} 个已存在)")
        self._update_selected_count()

    def start_processing(self):
        if not self.selected_videos:
            QMessageBox.warning(self, "警告", "请先选择要处理的视频")
            return
        if not self.output_dir:
            QMessageBox.warning(self, "警告", "请先选择输出目录")
            return

        reply = QMessageBox.question(
            self, "确认处理",
            f"将处理 {len(self.selected_videos)} 个视频，确定继续吗？",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return

        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)

        self.processing_thread = ProcessingThread(
            self.processor, self.selected_videos, self.output_dir,
            self.settings_panel.get_extract_mp3()
        )
        self.processing_thread.log.connect(self.add_log)
        self.processing_thread.finished.connect(self.processing_finished)
        self.processing_thread.start()
        self.status_label.setText("处理中...")
        self.add_log(f"🚀 开始处理 {len(self.selected_videos)} 个视频...")

    def stop_processing(self):
        if self.processing_thread and self.processing_thread.isRunning():
            self.processing_thread.stop()
            self.add_log("⏹ 正在停止...")

    def processing_finished(self, results: List[VideoInfo]):
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.status_label.setText("就绪")

        success_count = sum(1 for r in results if r.status == ProcessStatus.SUCCESS)
        failed_count = sum(1 for r in results if r.status == ProcessStatus.FAILED)
        self.add_log(f"\n🎉 处理完成！成功: {success_count}, 失败: {failed_count}")

        # 自动取消所有选中
        for card in self.video_cards:
            if card.is_selected:
                card.is_selected = False
                card.update_selected_style()  # 更新样式
        self.selected_videos.clear()
        self._update_selected_count()

        QMessageBox.information(
            self, "处理完成",
            f"处理完成！\n成功: {success_count}\n失败: {failed_count}\n\n输出目录: {self.output_dir}"
        )

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'video_layout'):
            self.video_layout.update()

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        paths = [url.toLocalFile() for url in event.mimeData().urls()]
        self.on_files_dropped(paths)

    def closeEvent(self, event):
        if self.watcher:
            self.watcher.deleteLater()
        self.restorer.cleanup_temp_files()
        event.accept()