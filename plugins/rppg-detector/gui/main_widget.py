"""
rPPG主界面 - 简化版
包含视频显示、心率显示、基本控制
"""

import cv2
import numpy as np
import time
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QGroupBox, QProgressBar, QComboBox)
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtGui import QImage, QPixmap

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.face_detector import FaceDetector
from core.roi_tracker import ROITracker
from core.signal_extractor import SignalExtractor
from core.rppg_algorithms import RPPGAlgorithms
from core.signal_processor import SignalProcessor
from core.heartrate_calculator import HeartRateCalculator
from utils.performance_monitor import PerformanceMonitor
from utils.data_recorder import DataRecorder
from config.config import RPPGConfig


class VideoProcessingThread(QThread):
    """视频处理线程"""
    frame_processed = pyqtSignal(np.ndarray, float, float, str)  # frame, hr, quality, status

    def __init__(self, camera_id=0):
        super().__init__()
        self.camera_id = camera_id
        self.running = False

        # 初始化组件
        self.face_detector = FaceDetector()
        self.roi_tracker = ROITracker("forehead_cheeks")
        self.signal_extractor = SignalExtractor(fps=30)
        self.signal_processor = SignalProcessor(fps=30)
        self.hr_calculator = HeartRateCalculator(fps=30)
        self.algorithm = "POS"

        self.start_time = time.time()

    def run(self):
        """运行线程"""
        cap = cv2.VideoCapture(self.camera_id)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        cap.set(cv2.CAP_PROP_FPS, 30)

        self.running = True

        while self.running:
            ret, frame = cap.read()
            if not ret:
                continue

            timestamp = time.time() - self.start_time

            # 检测人脸
            landmarks = self.face_detector.detect(frame)

            if landmarks is not None:
                # 更新ROI
                regions = self.roi_tracker.update(frame, landmarks)

                # 提取信号
                r, g, b = self.roi_tracker.get_combined_roi_signal(frame)
                self.signal_extractor.extract_from_roi(r, g, b, timestamp)

                # 绘制ROI
                frame = self.roi_tracker.draw_on_frame(frame, show_labels=True)

                # 计算心率
                if self.signal_extractor.is_ready():
                    _, r_sig, g_sig, b_sig = self.signal_extractor.get_raw_signals()

                    # 应用rPPG算法
                    pulse_signal = RPPGAlgorithms.process(self.algorithm, r_sig, g_sig, b_sig)

                    # 信号处理
                    _, _, filtered = self.signal_processor.process_pipeline(pulse_signal)

                    # 计算心率
                    hr, quality = self.hr_calculator.calculate(filtered)

                    status = f"心率: {hr:.1f} BPM | 质量: {quality:.0f}%"
                else:
                    hr, quality = 0, 0
                    buffer_size, max_size, pct = self.signal_extractor.get_buffer_status()
                    status = f"缓冲中... {pct:.0f}%"
            else:
                hr, quality = 0, 0
                status = "未检测到人脸"

            # 发送结果
            self.frame_processed.emit(frame, hr, quality, status)

            time.sleep(0.01)

        cap.release()

    def stop(self):
        """停止线程"""
        self.running = False


class RPPGMainWidget(QWidget):
    """rPPG主界面"""

    def __init__(self):
        super().__init__()
        self.video_thread = None
        self.init_ui()

    def init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout()

        # 标题
        title = QLabel("rPPG心率检测 - 基于MediaPipe Face Mesh")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # 主内容区
        content_layout = QHBoxLayout()

        # 左侧：视频
        video_panel = self._create_video_panel()
        content_layout.addWidget(video_panel, 3)

        # 右侧：心率和控制
        right_panel = self._create_right_panel()
        content_layout.addWidget(right_panel, 2)

        layout.addLayout(content_layout)

        self.setLayout(layout)
        self.setMinimumSize(1000, 600)

    def _create_video_panel(self):
        """创建视频面板"""
        panel = QGroupBox("视频显示")
        layout = QVBoxLayout()

        self.video_label = QLabel()
        self.video_label.setMinimumSize(640, 480)
        self.video_label.setStyleSheet("background: #000; border: 2px solid #3498db;")
        self.video_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.video_label)

        # 状态标签
        self.status_label = QLabel("等待开始...")
        self.status_label.setStyleSheet("font-size: 14px; color: #7f8c8d;")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)

        panel.setLayout(layout)
        return panel

    def _create_right_panel(self):
        """创建右侧面板"""
        panel = QWidget()
        layout = QVBoxLayout()

        # 心率显示
        hr_group = QGroupBox("实时心率")
        hr_layout = QVBoxLayout()

        self.hr_label = QLabel("-- BPM")
        self.hr_label.setStyleSheet("font-size: 48px; font-weight: bold; color: #e74c3c;")
        self.hr_label.setAlignment(Qt.AlignCenter)
        hr_layout.addWidget(self.hr_label)

        self.heart_icon = QLabel("❤️")
        self.heart_icon.setStyleSheet("font-size: 32px;")
        self.heart_icon.setAlignment(Qt.AlignCenter)
        hr_layout.addWidget(self.heart_icon)

        hr_group.setLayout(hr_layout)
        layout.addWidget(hr_group)

        # 信号质量
        quality_group = QGroupBox("信号质量")
        quality_layout = QVBoxLayout()

        self.quality_bar = QProgressBar()
        self.quality_bar.setRange(0, 100)
        self.quality_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid grey;
                border-radius: 5px;
                text-align: center;
                height: 25px;
            }
            QProgressBar::chunk {
                background-color: #27ae60;
            }
        """)
        quality_layout.addWidget(self.quality_bar)

        quality_group.setLayout(quality_layout)
        layout.addWidget(quality_group)

        # 控制按钮
        control_group = QGroupBox("控制")
        control_layout = QVBoxLayout()

        btn_layout = QHBoxLayout()
        self.start_btn = QPushButton("▶ 开始")
        self.stop_btn = QPushButton("⏹ 停止")
        self.stop_btn.setEnabled(False)

        self.start_btn.clicked.connect(self.start_detection)
        self.stop_btn.clicked.connect(self.stop_detection)

        btn_layout.addWidget(self.start_btn)
        btn_layout.addWidget(self.stop_btn)
        control_layout.addLayout(btn_layout)

        # 算法选择
        algo_layout = QHBoxLayout()
        algo_layout.addWidget(QLabel("算法:"))
        self.algo_combo = QComboBox()
        self.algo_combo.addItems(["POS (推荐)", "CHROM", "G-R", "GREEN"])
        algo_layout.addWidget(self.algo_combo)
        control_layout.addLayout(algo_layout)

        control_group.setLayout(control_layout)
        layout.addWidget(control_group)

        layout.addStretch()

        panel.setLayout(layout)
        return panel

    def start_detection(self):
        """开始检测"""
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)

        # 创建线程
        self.video_thread = VideoProcessingThread(camera_id=0)
        self.video_thread.frame_processed.connect(self.update_display)

        # 设置算法
        algo_text = self.algo_combo.currentText()
        if "POS" in algo_text:
            self.video_thread.algorithm = "POS"
        elif "CHROM" in algo_text:
            self.video_thread.algorithm = "CHROM"
        elif "G-R" in algo_text:
            self.video_thread.algorithm = "G-R"
        else:
            self.video_thread.algorithm = "GREEN"

        self.video_thread.start()

    def stop_detection(self):
        """停止检测"""
        if self.video_thread:
            self.video_thread.stop()
            self.video_thread.wait()

        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.status_label.setText("已停止")

    def update_display(self, frame, hr, quality, status):
        """更新显示"""
        # 更新视频
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_frame.shape
        bytes_per_line = ch * w
        qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qt_image)
        self.video_label.setPixmap(pixmap.scaled(640, 480, Qt.KeepAspectRatio))

        # 更新心率
        if hr > 0:
            self.hr_label.setText(f"{hr:.0f} BPM")
        else:
            self.hr_label.setText("-- BPM")

        # 更新质量
        self.quality_bar.setValue(int(quality))

        # 更新状态
        self.status_label.setText(status)

    def closeEvent(self, event):
        """关闭事件"""
        if self.video_thread:
            self.video_thread.stop()
            self.video_thread.wait()
        event.accept()
