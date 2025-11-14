# rPPG心率检测插件 - 增强可视化设计方案 v2.0

## 🎯 新增需求

基于用户反馈，新增以下专业级可视化功能：

### 1. 动态ROI追踪可视化
- ✅ 实时在视频上绘制ROI区域（彩色框）
- ✅ ROI随人脸移动自动跟踪
- ✅ 支持多ROI显示（前额、左脸颊、右脸颊）
- ✅ 可切换显示/隐藏ROI框

### 2. 多层数据性能面板
- ✅ **原始信号层**：RGB三通道原始数据
- ✅ **信号处理层**：归一化、去趋势、滤波后数据
- ✅ **频谱分析层**：FFT功率谱、频率分布
- ✅ **心率输出层**：BPM历史、变异性分析

### 3. ROI统计信息
- ✅ 实时亮度统计
- ✅ RGB均值和标准差
- ✅ ROI尺寸和位置
- ✅ 运动幅度（像素级）

---

## 🎨 新界面设计

### 整体布局（三栏式专业布局）

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│  rPPG心率检测 - 专业版                    [摄像头: 0 ▼] [算法: POS ▼] [⚙设置]   │
├──────────────────────────────┬──────────────────────────────────────────────────┤
│                              │  ┌─ 实时心率 ─────────────┬─ 信号质量 ─────────┐ │
│                              │  │       72 BPM           │  ████████░░ 85%    │ │
│      📹 视频显示区            │  │        ❤️              │  状态: 良好         │ │
│                              │  └────────────────────────┴────────────────────┘ │
│   ┌──────────────────┐       │  ┌─ 数据性能面板 ──────────────────────────────┐ │
│   │                  │       │  │ [①原始信号] [②处理中] [③频谱] [④心率] [⚡性能]│ │
│   │   实时画面        │       │  ├──────────────────────────────────────────────┤ │
│   │                  │       │  │  === 当前视图：① 原始信号 ===                 │ │
│   │  ┌─ ROI 1 ──┐   │       │  │                                              │ │
│   │  │ 前额区域  │   │       │  │  ┌─ ROI实时统计 ─────────────────────────┐   │ │
│   │  └──────────┘   │       │  │  │ ROI #1 (前额)   亮度: 125.3           │   │ │
│   │                  │       │  │  │   位置: (180, 95)  尺寸: 120x80       │   │ │
│   │  ┌ ROI 2 ┐  ┌ ROI 3 ┐  │       │  │   R: 152.4  G: 138.7  B: 115.2        │   │ │
│   │  │左脸颊 │  │右脸颊 │  │       │  │   运动: ▓▓░░░ 2.3px                   │   │ │
│   │  └──────┘  └──────┘  │       │  │  │                                       │   │ │
│   │                  │       │  │  │ ROI #2 (左脸颊) 亮度: 118.5           │   │ │
│   └──────────────────┘       │  │  │   位置: (150, 180) 尺寸: 80x100       │   │ │
│                              │  │  │   R: 145.2  G: 132.1  B: 108.9        │   │ │
├──────────────────────────────┤  │  └───────────────────────────────────────┘   │ │
│ 控制面板                      │  │                                              │ │
│ [▶ 开始] [⏹ 停止] [⏸ 暂停]   │  │  ┌─ 原始RGB信号波形 ─────────────────────┐   │ │
│ [📸 截图] [🎥 录制]           │  │  │  R通道 ─────────/\/\/\────────────     │   │ │
│                              │  │  │  G通道 ────────/\/\/\/\───────────     │   │ │
│ 显示选项:                     │  │  │  B通道 ───────/\/\/\──────────────     │   │ │
│ ☑ 显示ROI框                  │  │  │  时间: 0-10s   采样: 300帧            │   │ │
│ ☑ 显示关键点                 │  │  └───────────────────────────────────────┘   │ │
│ ☑ 显示统计信息               │  │                                              │ │
│ □ 慢速模式(15fps)            │  │  ┌─ 信号统计 ────────────────────────────┐   │ │
│                              │  │  │ 均值: R=150.2 G=136.5 B=112.8         │   │ │
│ ROI设置:                     │  │  │ 标准差: R=8.3 G=6.7 B=5.4             │   │ │
│ ○ 仅前额                     │  │  │ 信噪比: 12.5 dB                       │   │ │
│ ● 前额+脸颊(推荐)            │  │  │ 缓冲区: 300/300 (100%)                │   │ │
│ ○ 全脸                       │  │  └───────────────────────────────────────┘   │ │
└──────────────────────────────┴──────────────────────────────────────────────────┘
```

---

## 💻 核心实现：动态ROI追踪

### 1. ROI追踪器类

```python
import cv2
import numpy as np
from collections import deque
from dataclasses import dataclass

@dataclass
class ROIRegion:
    """ROI区域数据结构"""
    name: str              # 区域名称（前额、左脸颊等）
    rect: tuple           # (x, y, w, h)
    color: tuple          # BGR颜色
    active: bool = True   # 是否激活

    # 统计数据
    brightness: float = 0.0
    mean_rgb: tuple = (0, 0, 0)
    std_rgb: tuple = (0, 0, 0)
    motion: float = 0.0   # 运动幅度（像素）

class ROITracker:
    """
    动态ROI追踪器
    """
    def __init__(self, roi_mode="forehead_cheeks"):
        self.roi_mode = roi_mode
        self.regions = []
        self.prev_frame = None

        # 颜色方案（美观的配色）
        self.colors = {
            'forehead': (0, 255, 0),      # 绿色
            'left_cheek': (255, 100, 0),  # 橙色
            'right_cheek': (255, 0, 100), # 粉色
            'full_face': (0, 200, 255)    # 黄色
        }

    def update(self, frame, face_box):
        """
        更新ROI区域

        Args:
            frame: 当前帧
            face_box: 人脸框 (x, y, w, h)

        Returns:
            List[ROIRegion]: ROI区域列表
        """
        x, y, w, h = face_box
        self.regions = []

        if self.roi_mode == "forehead_only":
            # 仅前额区域
            forehead = self._extract_forehead(x, y, w, h)
            self.regions.append(ROIRegion(
                name="前额",
                rect=forehead,
                color=self.colors['forehead']
            ))

        elif self.roi_mode == "forehead_cheeks":
            # 前额 + 双脸颊（推荐）
            forehead = self._extract_forehead(x, y, w, h)
            left_cheek = self._extract_left_cheek(x, y, w, h)
            right_cheek = self._extract_right_cheek(x, y, w, h)

            self.regions.extend([
                ROIRegion("前额", forehead, self.colors['forehead']),
                ROIRegion("左脸颊", left_cheek, self.colors['left_cheek']),
                ROIRegion("右脸颊", right_cheek, self.colors['right_cheek'])
            ])

        elif self.roi_mode == "full_face":
            # 全脸
            self.regions.append(ROIRegion(
                name="全脸",
                rect=(x, y, w, h),
                color=self.colors['full_face']
            ))

        # 更新每个ROI的统计信息
        for region in self.regions:
            self._update_roi_stats(frame, region)

        return self.regions

    def _extract_forehead(self, x, y, w, h):
        """提取前额区域"""
        # 前额：人脸上1/3区域，左右各缩进10%
        margin = int(w * 0.1)
        forehead_h = int(h * 0.35)

        return (
            x + margin,
            y + int(h * 0.05),
            w - 2 * margin,
            forehead_h
        )

    def _extract_left_cheek(self, x, y, w, h):
        """提取左脸颊区域"""
        # 左脸颊：中间1/3高度，左半边
        cheek_y = y + int(h * 0.35)
        cheek_h = int(h * 0.4)
        cheek_w = int(w * 0.35)

        return (
            x + int(w * 0.1),
            cheek_y,
            cheek_w,
            cheek_h
        )

    def _extract_right_cheek(self, x, y, w, h):
        """提取右脸颊区域"""
        cheek_y = y + int(h * 0.35)
        cheek_h = int(h * 0.4)
        cheek_w = int(w * 0.35)

        return (
            x + w - cheek_w - int(w * 0.1),
            cheek_y,
            cheek_w,
            cheek_h
        )

    def _update_roi_stats(self, frame, region: ROIRegion):
        """更新ROI统计信息"""
        rx, ry, rw, rh = region.rect

        # 提取ROI区域
        roi_frame = frame[ry:ry+rh, rx:rx+rw]

        if roi_frame.size == 0:
            return

        # 计算亮度
        gray = cv2.cvtColor(roi_frame, cv2.COLOR_BGR2GRAY)
        region.brightness = np.mean(gray)

        # 计算RGB均值和标准差
        mean_b, mean_g, mean_r = cv2.mean(roi_frame)[:3]
        region.mean_rgb = (mean_r, mean_g, mean_b)

        std_b = np.std(roi_frame[:, :, 0])
        std_g = np.std(roi_frame[:, :, 1])
        std_r = np.std(roi_frame[:, :, 2])
        region.std_rgb = (std_r, std_g, std_b)

        # 计算运动幅度（与上一帧比较）
        if self.prev_frame is not None:
            prev_roi = self.prev_frame[ry:ry+rh, rx:rx+rw]
            if prev_roi.shape == roi_frame.shape:
                diff = cv2.absdiff(roi_frame, prev_roi)
                region.motion = np.mean(diff)

        self.prev_frame = frame.copy()

    def draw_on_frame(self, frame, show_labels=True):
        """
        在视频帧上绘制ROI

        Args:
            frame: 视频帧
            show_labels: 是否显示标签

        Returns:
            绘制后的帧
        """
        display_frame = frame.copy()

        for region in self.regions:
            if not region.active:
                continue

            x, y, w, h = region.rect
            color = region.color

            # 绘制矩形框（粗线）
            cv2.rectangle(display_frame, (x, y), (x+w, y+h), color, 2)

            # 绘制半透明填充
            overlay = display_frame.copy()
            cv2.rectangle(overlay, (x, y), (x+w, y+h), color, -1)
            cv2.addWeighted(overlay, 0.15, display_frame, 0.85, 0, display_frame)

            if show_labels:
                # 绘制标签背景
                label = region.name
                font = cv2.FONT_HERSHEY_SIMPLEX
                font_scale = 0.5
                thickness = 1

                (text_w, text_h), _ = cv2.getTextSize(label, font, font_scale, thickness)

                # 标签背景
                cv2.rectangle(display_frame,
                             (x, y - text_h - 8),
                             (x + text_w + 8, y),
                             color, -1)

                # 标签文字
                cv2.putText(display_frame, label,
                           (x + 4, y - 4),
                           font, font_scale, (255, 255, 255), thickness)

                # 显示亮度信息
                brightness_text = f"{region.brightness:.1f}"
                cv2.putText(display_frame, brightness_text,
                           (x + 4, y + h - 8),
                           font, 0.4, color, 1)

        return display_frame
```

---

## 📊 数据性能面板实现

### 1. 多标签页数据面板

```python
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                             QTabWidget, QGroupBox, QLabel, QGridLayout)
import pyqtgraph as pg

class DataPerformancePanel(QWidget):
    """
    数据性能面板 - 多标签页设计
    """
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # 创建标签页
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #ccc;
                background: white;
            }
            QTabBar::tab {
                background: #f0f0f0;
                padding: 8px 16px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background: white;
                border-bottom: 2px solid #3498db;
            }
        """)

        # 标签页1: 原始信号
        tab1 = self._create_raw_signal_tab()
        self.tab_widget.addTab(tab1, "① 原始信号")

        # 标签页2: 处理中
        tab2 = self._create_processing_tab()
        self.tab_widget.addTab(tab2, "② 处理中")

        # 标签页3: 频谱分析
        tab3 = self._create_spectrum_tab()
        self.tab_widget.addTab(tab3, "③ 频谱")

        # 标签页4: 心率输出
        tab4 = self._create_heartrate_tab()
        self.tab_widget.addTab(tab4, "④ 心率")

        # 标签页5: 性能监控
        tab5 = self._create_performance_tab()
        self.tab_widget.addTab(tab5, "⚡ 性能")

        layout.addWidget(self.tab_widget)
        self.setLayout(layout)

    def _create_raw_signal_tab(self):
        """标签页1: 原始信号"""
        tab = QWidget()
        layout = QVBoxLayout()

        # === ROI统计信息 ===
        roi_stats_group = QGroupBox("ROI实时统计")
        roi_stats_layout = QVBoxLayout()

        # 为每个ROI创建统计显示
        self.roi_stat_labels = []
        for i in range(3):  # 最多3个ROI
            roi_widget = self._create_roi_stat_widget(i)
            roi_stats_layout.addWidget(roi_widget)
            self.roi_stat_labels.append(roi_widget)

        roi_stats_group.setLayout(roi_stats_layout)
        layout.addWidget(roi_stats_group)

        # === 原始RGB波形图 ===
        wave_group = QGroupBox("原始RGB信号波形")
        wave_layout = QVBoxLayout()

        # 创建pyqtgraph绘图窗口
        self.raw_plot = pg.PlotWidget()
        self.raw_plot.setBackground('w')
        self.raw_plot.setLabel('left', 'Intensity', units='')
        self.raw_plot.setLabel('bottom', 'Time', units='s')
        self.raw_plot.addLegend()
        self.raw_plot.showGrid(x=True, y=True, alpha=0.3)

        # 创建三条曲线
        self.raw_r_curve = self.raw_plot.plot(pen=pg.mkPen('#e74c3c', width=2), name='R通道')
        self.raw_g_curve = self.raw_plot.plot(pen=pg.mkPen('#27ae60', width=2), name='G通道')
        self.raw_b_curve = self.raw_plot.plot(pen=pg.mkPen('#3498db', width=2), name='B通道')

        wave_layout.addWidget(self.raw_plot)
        wave_group.setLayout(wave_layout)
        layout.addWidget(wave_group, 1)

        # === 信号统计 ===
        stats_group = QGroupBox("信号统计")
        stats_layout = QGridLayout()

        # 均值
        stats_layout.addWidget(QLabel("均值:"), 0, 0)
        self.raw_mean_label = QLabel("R=-- G=-- B=--")
        stats_layout.addWidget(self.raw_mean_label, 0, 1)

        # 标准差
        stats_layout.addWidget(QLabel("标准差:"), 1, 0)
        self.raw_std_label = QLabel("R=-- G=-- B=--")
        stats_layout.addWidget(self.raw_std_label, 1, 1)

        # 信噪比
        stats_layout.addWidget(QLabel("信噪比:"), 0, 2)
        self.raw_snr_label = QLabel("-- dB")
        stats_layout.addWidget(self.raw_snr_label, 0, 3)

        # 缓冲区状态
        stats_layout.addWidget(QLabel("缓冲区:"), 1, 2)
        self.buffer_status_label = QLabel("0/300 (0%)")
        stats_layout.addWidget(self.buffer_status_label, 1, 3)

        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)

        tab.setLayout(layout)
        return tab

    def _create_roi_stat_widget(self, roi_index):
        """创建单个ROI统计组件"""
        widget = QGroupBox(f"ROI #{roi_index + 1}")
        widget.setVisible(False)  # 初始隐藏

        layout = QGridLayout()
        layout.setSpacing(5)

        # 区域名称
        name_label = QLabel("--")
        name_label.setStyleSheet("font-weight: bold; color: #2c3e50;")
        layout.addWidget(QLabel("区域:"), 0, 0)
        layout.addWidget(name_label, 0, 1, 1, 3)

        # 位置和尺寸
        layout.addWidget(QLabel("位置:"), 1, 0)
        pos_label = QLabel("(--, --)")
        layout.addWidget(pos_label, 1, 1)

        layout.addWidget(QLabel("尺寸:"), 1, 2)
        size_label = QLabel("--x--")
        layout.addWidget(size_label, 1, 3)

        # RGB值
        layout.addWidget(QLabel("RGB:"), 2, 0)
        rgb_label = QLabel("R=-- G=-- B=--")
        layout.addWidget(rgb_label, 2, 1, 1, 3)

        # 亮度
        layout.addWidget(QLabel("亮度:"), 3, 0)
        brightness_label = QLabel("--")
        layout.addWidget(brightness_label, 3, 1)

        # 运动幅度
        layout.addWidget(QLabel("运动:"), 3, 2)
        motion_label = QLabel("--")
        motion_progress = QLabel("░░░░░")
        layout.addWidget(motion_label, 3, 3)

        widget.setLayout(layout)

        # 保存标签引用
        widget.name_label = name_label
        widget.pos_label = pos_label
        widget.size_label = size_label
        widget.rgb_label = rgb_label
        widget.brightness_label = brightness_label
        widget.motion_label = motion_label

        return widget

    def _create_processing_tab(self):
        """标签页2: 信号处理"""
        tab = QWidget()
        layout = QVBoxLayout()

        # === 处理步骤对比 ===
        steps_group = QGroupBox("处理步骤")
        steps_layout = QVBoxLayout()

        # 步骤1: 归一化
        step1_plot = pg.PlotWidget(title="步骤1: 归一化")
        step1_plot.setBackground('w')
        step1_plot.setMaximumHeight(150)
        self.norm_curve = step1_plot.plot(pen=pg.mkPen('#3498db', width=2))
        steps_layout.addWidget(step1_plot)

        # 步骤2: 去趋势
        step2_plot = pg.PlotWidget(title="步骤2: 去趋势")
        step2_plot.setBackground('w')
        step2_plot.setMaximumHeight(150)
        self.detrend_curve = step2_plot.plot(pen=pg.mkPen('#9b59b6', width=2))
        steps_layout.addWidget(step2_plot)

        # 步骤3: 带通滤波
        step3_plot = pg.PlotWidget(title="步骤3: 带通滤波 (0.67-3.33Hz)")
        step3_plot.setBackground('w')
        step3_plot.setMaximumHeight(150)
        self.filtered_curve = step3_plot.plot(pen=pg.mkPen('#27ae60', width=2))
        steps_layout.addWidget(step3_plot)

        steps_group.setLayout(steps_layout)
        layout.addWidget(steps_group)

        # === 滤波器参数 ===
        filter_group = QGroupBox("滤波器参数")
        filter_layout = QGridLayout()

        filter_layout.addWidget(QLabel("类型:"), 0, 0)
        filter_layout.addWidget(QLabel("Butterworth 4阶"), 0, 1)

        filter_layout.addWidget(QLabel("通带:"), 1, 0)
        filter_layout.addWidget(QLabel("0.67 - 3.33 Hz"), 1, 1)

        filter_layout.addWidget(QLabel("对应BPM:"), 2, 0)
        filter_layout.addWidget(QLabel("40 - 200 BPM"), 2, 1)

        filter_group.setLayout(filter_layout)
        layout.addWidget(filter_group)

        tab.setLayout(layout)
        return tab

    def _create_spectrum_tab(self):
        """标签页3: 频谱分析"""
        tab = QWidget()
        layout = QVBoxLayout()

        # === FFT功率谱 ===
        spectrum_group = QGroupBox("FFT功率谱")
        spectrum_layout = QVBoxLayout()

        self.spectrum_plot = pg.PlotWidget()
        self.spectrum_plot.setBackground('w')
        self.spectrum_plot.setLabel('left', 'Power', units='a.u.')
        self.spectrum_plot.setLabel('bottom', 'Frequency', units='Hz')
        self.spectrum_plot.showGrid(x=True, y=True, alpha=0.3)

        # 功率谱曲线
        self.spectrum_curve = self.spectrum_plot.plot(
            pen=pg.mkPen('#e74c3c', width=2),
            fillLevel=0,
            brush=(231, 76, 60, 50)
        )

        # 标记峰值位置
        self.peak_marker = pg.ScatterPlotItem(
            size=10,
            pen=pg.mkPen(None),
            brush=pg.mkBrush(255, 0, 0, 200)
        )
        self.spectrum_plot.addItem(self.peak_marker)

        # 标记心率范围
        self.hr_region = pg.LinearRegionItem(
            values=[0.67, 3.33],
            brush=(100, 100, 200, 30),
            movable=False
        )
        self.spectrum_plot.addItem(self.hr_region)

        spectrum_layout.addWidget(self.spectrum_plot)
        spectrum_group.setLayout(spectrum_layout)
        layout.addWidget(spectrum_group, 1)

        # === 频谱统计 ===
        stats_group = QGroupBox("频谱分析结果")
        stats_layout = QGridLayout()

        stats_layout.addWidget(QLabel("主频率:"), 0, 0)
        self.peak_freq_label = QLabel("-- Hz")
        self.peak_freq_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #e74c3c;")
        stats_layout.addWidget(self.peak_freq_label, 0, 1)

        stats_layout.addWidget(QLabel("对应心率:"), 0, 2)
        self.peak_hr_label = QLabel("-- BPM")
        self.peak_hr_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #e74c3c;")
        stats_layout.addWidget(self.peak_hr_label, 0, 3)

        stats_layout.addWidget(QLabel("峰值功率:"), 1, 0)
        self.peak_power_label = QLabel("--")
        stats_layout.addWidget(self.peak_power_label, 1, 1)

        stats_layout.addWidget(QLabel("功率集中度:"), 1, 2)
        self.power_concentration_label = QLabel("--%")
        stats_layout.addWidget(self.power_concentration_label, 1, 3)

        stats_layout.addWidget(QLabel("信号质量:"), 2, 0)
        self.spectrum_quality_label = QLabel("--")
        stats_layout.addWidget(self.spectrum_quality_label, 2, 1)

        stats_layout.addWidget(QLabel("置信度:"), 2, 2)
        self.confidence_label = QLabel("--%")
        stats_layout.addWidget(self.confidence_label, 2, 3)

        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)

        tab.setLayout(layout)
        return tab

    def _create_heartrate_tab(self):
        """标签页4: 心率输出"""
        tab = QWidget()
        layout = QVBoxLayout()

        # === 心率历史曲线 ===
        history_group = QGroupBox("心率历史曲线")
        history_layout = QVBoxLayout()

        self.hr_history_plot = pg.PlotWidget()
        self.hr_history_plot.setBackground('w')
        self.hr_history_plot.setLabel('left', 'Heart Rate', units='BPM')
        self.hr_history_plot.setLabel('bottom', 'Time', units='s')
        self.hr_history_plot.showGrid(x=True, y=True, alpha=0.3)
        self.hr_history_plot.setYRange(40, 200)

        # 心率曲线
        self.hr_curve = self.hr_history_plot.plot(
            pen=pg.mkPen('#e74c3c', width=3),
            symbol='o',
            symbolSize=6,
            symbolBrush=(231, 76, 60, 200)
        )

        # 添加正常心率范围标记
        self.normal_hr_region = pg.LinearRegionItem(
            values=[60, 100],
            orientation='horizontal',
            brush=(100, 200, 100, 30),
            movable=False
        )
        self.hr_history_plot.addItem(self.normal_hr_region)

        history_layout.addWidget(self.hr_history_plot)
        history_group.setLayout(history_layout)
        layout.addWidget(history_group, 2)

        # === 心率变异性 (HRV) ===
        hrv_group = QGroupBox("心率变异性 (HRV)")
        hrv_layout = QVBoxLayout()

        # HRV柱状图
        self.hrv_plot = pg.PlotWidget()
        self.hrv_plot.setBackground('w')
        self.hrv_plot.setLabel('left', 'Count')
        self.hrv_plot.setLabel('bottom', 'Heart Rate (BPM)')
        self.hrv_plot.setMaximumHeight(150)

        self.hrv_bars = pg.BarGraphItem(x=[], height=[], width=0.8, brush='b')
        self.hrv_plot.addItem(self.hrv_bars)

        hrv_layout.addWidget(self.hrv_plot)
        hrv_group.setLayout(hrv_layout)
        layout.addWidget(hrv_group, 1)

        # === 统计数据 ===
        stats_group = QGroupBox("统计数据")
        stats_layout = QGridLayout()

        stats_layout.addWidget(QLabel("平均心率:"), 0, 0)
        self.avg_hr_label = QLabel("-- BPM")
        stats_layout.addWidget(self.avg_hr_label, 0, 1)

        stats_layout.addWidget(QLabel("最小心率:"), 0, 2)
        self.min_hr_label = QLabel("-- BPM")
        stats_layout.addWidget(self.min_hr_label, 0, 3)

        stats_layout.addWidget(QLabel("最大心率:"), 1, 0)
        self.max_hr_label = QLabel("-- BPM")
        stats_layout.addWidget(self.max_hr_label, 1, 1)

        stats_layout.addWidget(QLabel("标准差:"), 1, 2)
        self.std_hr_label = QLabel("-- BPM")
        stats_layout.addWidget(self.std_hr_label, 1, 3)

        stats_layout.addWidget(QLabel("RMSSD:"), 2, 0)
        self.rmssd_label = QLabel("-- ms")
        stats_layout.addWidget(self.rmssd_label, 2, 1)

        stats_layout.addWidget(QLabel("数据点:"), 2, 2)
        self.data_points_label = QLabel("0")
        stats_layout.addWidget(self.data_points_label, 2, 3)

        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)

        tab.setLayout(layout)
        return tab

    def _create_performance_tab(self):
        """标签页5: 性能监控"""
        tab = QWidget()
        layout = QVBoxLayout()

        # === CPU使用率 ===
        cpu_group = QGroupBox("CPU使用率")
        cpu_layout = QVBoxLayout()

        self.cpu_plot = pg.PlotWidget()
        self.cpu_plot.setBackground('w')
        self.cpu_plot.setLabel('left', 'CPU Usage', units='%')
        self.cpu_plot.setLabel('bottom', 'Time', units='s')
        self.cpu_plot.setYRange(0, 100)
        self.cpu_plot.setMaximumHeight(150)

        self.cpu_curve = self.cpu_plot.plot(pen=pg.mkPen('#3498db', width=2))

        cpu_layout.addWidget(self.cpu_plot)
        cpu_group.setLayout(cpu_layout)
        layout.addWidget(cpu_group)

        # === 帧率监控 ===
        fps_group = QGroupBox("帧率监控")
        fps_layout = QVBoxLayout()

        self.fps_plot = pg.PlotWidget()
        self.fps_plot.setBackground('w')
        self.fps_plot.setLabel('left', 'FPS')
        self.fps_plot.setLabel('bottom', 'Time', units='s')
        self.fps_plot.setYRange(0, 35)
        self.fps_plot.setMaximumHeight(150)

        self.fps_curve = self.fps_plot.plot(pen=pg.mkPen('#27ae60', width=2))

        fps_layout.addWidget(self.fps_plot)
        fps_group.setLayout(fps_layout)
        layout.addWidget(fps_group)

        # === 性能统计 ===
        stats_group = QGroupBox("性能统计")
        stats_layout = QGridLayout()

        stats_layout.addWidget(QLabel("平均FPS:"), 0, 0)
        self.avg_fps_label = QLabel("-- fps")
        stats_layout.addWidget(self.avg_fps_label, 0, 1)

        stats_layout.addWidget(QLabel("平均CPU:"), 0, 2)
        self.avg_cpu_label = QLabel("--%")
        stats_layout.addWidget(self.avg_cpu_label, 0, 3)

        stats_layout.addWidget(QLabel("处理延迟:"), 1, 0)
        self.latency_label = QLabel("-- ms")
        stats_layout.addWidget(self.latency_label, 1, 1)

        stats_layout.addWidget(QLabel("内存占用:"), 1, 2)
        self.memory_label = QLabel("-- MB")
        stats_layout.addWidget(self.memory_label, 1, 3)

        stats_layout.addWidget(QLabel("运行时间:"), 2, 0)
        self.runtime_label = QLabel("00:00:00")
        stats_layout.addWidget(self.runtime_label, 2, 1)

        stats_layout.addWidget(QLabel("处理帧数:"), 2, 2)
        self.frame_count_label = QLabel("0")
        stats_layout.addWidget(self.frame_count_label, 2, 3)

        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)

        layout.addStretch()

        tab.setLayout(layout)
        return tab

    # === 更新方法 ===

    def update_roi_stats(self, roi_regions):
        """更新ROI统计信息"""
        for i, region in enumerate(roi_regions):
            if i >= len(self.roi_stat_labels):
                break

            widget = self.roi_stat_labels[i]
            widget.setVisible(True)
            widget.setTitle(f"ROI #{i+1} - {region.name}")

            # 更新各个标签
            widget.name_label.setText(region.name)

            x, y, w, h = region.rect
            widget.pos_label.setText(f"({x}, {y})")
            widget.size_label.setText(f"{w}x{h}")

            r, g, b = region.mean_rgb
            widget.rgb_label.setText(f"R={r:.1f} G={g:.1f} B={b:.1f}")

            widget.brightness_label.setText(f"{region.brightness:.1f}")

            # 运动幅度可视化
            motion_bars = int(region.motion / 2)  # 0-10的范围
            motion_visual = "▓" * min(motion_bars, 5) + "░" * (5 - min(motion_bars, 5))
            widget.motion_label.setText(f"{region.motion:.1f}px {motion_visual}")

        # 隐藏多余的ROI显示
        for i in range(len(roi_regions), len(self.roi_stat_labels)):
            self.roi_stat_labels[i].setVisible(False)

    def update_raw_signals(self, timestamps, r_signal, g_signal, b_signal):
        """更新原始信号波形"""
        self.raw_r_curve.setData(timestamps, r_signal)
        self.raw_g_curve.setData(timestamps, g_signal)
        self.raw_b_curve.setData(timestamps, b_signal)

        # 更新统计信息
        self.raw_mean_label.setText(
            f"R={np.mean(r_signal):.1f} G={np.mean(g_signal):.1f} B={np.mean(b_signal):.1f}"
        )
        self.raw_std_label.setText(
            f"R={np.std(r_signal):.1f} G={np.std(g_signal):.1f} B={np.std(b_signal):.1f}"
        )

    def update_processed_signals(self, timestamps, norm_signal, detrend_signal, filtered_signal):
        """更新处理后的信号"""
        self.norm_curve.setData(timestamps, norm_signal)
        self.detrend_curve.setData(timestamps, detrend_signal)
        self.filtered_curve.setData(timestamps, filtered_signal)

    def update_spectrum(self, frequencies, power, peak_freq, peak_power):
        """更新频谱"""
        self.spectrum_curve.setData(frequencies, power)

        # 更新峰值标记
        self.peak_marker.setData([peak_freq], [peak_power])

        # 更新统计
        peak_hr = peak_freq * 60
        self.peak_freq_label.setText(f"{peak_freq:.3f} Hz")
        self.peak_hr_label.setText(f"{peak_hr:.1f} BPM")
        self.peak_power_label.setText(f"{peak_power:.2f}")

        # 计算功率集中度
        total_power = np.sum(power)
        concentration = (peak_power / total_power * 100) if total_power > 0 else 0
        self.power_concentration_label.setText(f"{concentration:.1f}%")

    def update_heartrate(self, timestamps, hr_values):
        """更新心率历史"""
        self.hr_curve.setData(timestamps, hr_values)

        if len(hr_values) > 0:
            self.avg_hr_label.setText(f"{np.mean(hr_values):.1f} BPM")
            self.min_hr_label.setText(f"{np.min(hr_values):.1f} BPM")
            self.max_hr_label.setText(f"{np.max(hr_values):.1f} BPM")
            self.std_hr_label.setText(f"{np.std(hr_values):.1f} BPM")
            self.data_points_label.setText(f"{len(hr_values)}")
```

---

## 🎮 完整的主界面集成

```python
class RPPGPluginWidget(QWidget):
    """
    rPPG插件主界面 - v2.0 增强版
    """
    def __init__(self):
        super().__init__()
        self.init_ui()

        # 核心组件
        self.roi_tracker = ROITracker(roi_mode="forehead_cheeks")
        self.video_thread = None
        self.processing_thread = None

    def init_ui(self):
        main_layout = QHBoxLayout()

        # === 左侧：视频显示 + 控制 (40%) ===
        left_panel = self._create_left_panel()

        # === 右侧：数据面板 (60%) ===
        right_panel = self._create_right_panel()

        main_layout.addWidget(left_panel, 4)
        main_layout.addWidget(right_panel, 6)

        self.setLayout(main_layout)

    def _create_left_panel(self):
        """左侧面板：视频 + 控制"""
        panel = QWidget()
        layout = QVBoxLayout()

        # 视频显示
        self.video_label = QLabel()
        self.video_label.setMinimumSize(640, 480)
        self.video_label.setStyleSheet("border: 2px solid #3498db; background: #000;")
        self.video_label.setScaledContents(False)
        layout.addWidget(self.video_label, 1)

        # 控制面板
        control_panel = self._create_control_panel()
        layout.addWidget(control_panel)

        panel.setLayout(layout)
        return panel

    def _create_right_panel(self):
        """右侧面板：数据展示"""
        panel = QWidget()
        layout = QVBoxLayout()

        # 顶部：心率 + 质量
        top_row = QHBoxLayout()

        # 心率卡片
        hr_card = QGroupBox("实时心率")
        hr_layout = QVBoxLayout()
        self.hr_display = QLabel("-- BPM")
        self.hr_display.setStyleSheet("font-size: 36px; font-weight: bold; color: #e74c3c;")
        self.hr_display.setAlignment(Qt.AlignCenter)
        hr_layout.addWidget(self.hr_display)
        self.heart_icon = QLabel("❤️")
        self.heart_icon.setStyleSheet("font-size: 24px;")
        self.heart_icon.setAlignment(Qt.AlignCenter)
        hr_layout.addWidget(self.heart_icon)
        hr_card.setLayout(hr_layout)
        top_row.addWidget(hr_card)

        # 质量卡片
        quality_card = QGroupBox("信号质量")
        quality_layout = QVBoxLayout()
        self.quality_bar = QProgressBar()
        self.quality_bar.setRange(0, 100)
        quality_layout.addWidget(self.quality_bar)
        self.quality_status = QLabel("等待检测...")
        quality_layout.addWidget(self.quality_status)
        quality_card.setLayout(quality_layout)
        top_row.addWidget(quality_card)

        layout.addLayout(top_row)

        # 数据性能面板
        self.data_panel = DataPerformancePanel()
        layout.addWidget(self.data_panel, 1)

        panel.setLayout(layout)
        return panel

    def _create_control_panel(self):
        """创建控制面板"""
        panel = QGroupBox("控制面板")
        layout = QVBoxLayout()

        # 主控制按钮
        btn_row = QHBoxLayout()
        self.start_btn = QPushButton("▶ 开始")
        self.stop_btn = QPushButton("⏹ 停止")
        self.pause_btn = QPushButton("⏸ 暂停")
        self.screenshot_btn = QPushButton("📸 截图")

        self.stop_btn.setEnabled(False)
        self.pause_btn.setEnabled(False)

        btn_row.addWidget(self.start_btn)
        btn_row.addWidget(self.stop_btn)
        btn_row.addWidget(self.pause_btn)
        btn_row.addWidget(self.screenshot_btn)

        layout.addLayout(btn_row)

        # 显示选项
        display_options = QGroupBox("显示选项")
        display_layout = QVBoxLayout()

        self.show_roi_check = QCheckBox("显示ROI框")
        self.show_roi_check.setChecked(True)

        self.show_landmarks_check = QCheckBox("显示关键点")
        self.show_stats_check = QCheckBox("显示统计信息")

        display_layout.addWidget(self.show_roi_check)
        display_layout.addWidget(self.show_landmarks_check)
        display_layout.addWidget(self.show_stats_check)

        display_options.setLayout(display_layout)
        layout.addWidget(display_options)

        # ROI设置
        roi_options = QGroupBox("ROI设置")
        roi_layout = QVBoxLayout()

        self.roi_mode_group = QButtonGroup()

        roi_forehead = QRadioButton("仅前额")
        roi_cheeks = QRadioButton("前额+脸颊 (推荐)")
        roi_full = QRadioButton("全脸")

        roi_cheeks.setChecked(True)

        self.roi_mode_group.addButton(roi_forehead, 0)
        self.roi_mode_group.addButton(roi_cheeks, 1)
        self.roi_mode_group.addButton(roi_full, 2)

        roi_layout.addWidget(roi_forehead)
        roi_layout.addWidget(roi_cheeks)
        roi_layout.addWidget(roi_full)

        roi_options.setLayout(roi_layout)
        layout.addWidget(roi_options)

        panel.setLayout(layout)
        return panel
```

---

## 📝 更新的文件结构

```
plugins/rppg-detector/
├── plugin.py                      # 插件入口
├── core/
│   ├── __init__.py
│   ├── roi_tracker.py             # ✨ ROI追踪器（新增）
│   ├── face_detector.py           # 人脸检测
│   ├── signal_extractor.py        # 信号提取
│   ├── rppg_algorithms.py         # rPPG算法
│   ├── signal_processor.py        # 信号处理
│   └── heartrate_calculator.py    # 心率计算
├── gui/
│   ├── __init__.py
│   ├── main_widget.py             # 主界面
│   ├── data_panel.py              # ✨ 数据性能面板（新增）
│   ├── video_display.py           # 视频显示组件
│   └── control_panel.py           # 控制面板
├── utils/
│   ├── __init__.py
│   ├── performance_monitor.py     # ✨ 性能监控（新增）
│   └── data_recorder.py           # 数据记录
├── config/
│   └── config.py                  # 配置文件
└── README.md
```

---

## 🎯 新增功能总结

### 1. 动态ROI追踪
- ✅ 实时在视频上绘制ROI（绿色前额、橙色左脸颊、粉色右脸颊）
- ✅ ROI自动跟随人脸移动
- ✅ 半透明填充 + 清晰边框
- ✅ 显示ROI名称和亮度

### 2. 五标签页数据面板
- **① 原始信号**: ROI统计 + RGB波形 + 信号统计
- **② 处理中**: 归一化、去趋势、滤波三步骤可视化
- **③ 频谱**: FFT功率谱 + 峰值标记 + 频谱统计
- **④ 心率**: 历史曲线 + HRV柱状图 + 统计数据
- **⚡ 性能**: CPU/FPS监控 + 性能统计

### 3. 详细统计信息
- ROI: 位置、尺寸、RGB、亮度、运动幅度
- 信号: 均值、标准差、信噪比、缓冲区状态
- 频谱: 主频率、峰值功率、功率集中度
- 心率: 平均、最小、最大、标准差、RMSSD
- 性能: FPS、CPU、延迟、内存、运行时间

---

## ✅ 您的需求已全部覆盖

1. ✅ **动态追踪ROI区域** - 实时绘制、自动跟随
2. ✅ **ROI数据** - 位置、尺寸、RGB、亮度、运动
3. ✅ **信号处理数据** - 归一化、去趋势、滤波可视化
4. ✅ **处理后数据** - 频谱分析、峰值检测
5. ✅ **心率波动数据** - 历史曲线、HRV、统计

这个设计方案是否满足您的需求？我可以立即开始实现！
