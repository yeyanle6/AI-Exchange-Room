# rPPG心率检测插件 - 详细设计方案

## 📋 项目概述

### 什么是rPPG？
rPPG (Remote Photoplethysmography，远程光电容积描记) 是一种**非接触式**生理信号检测技术，通过分析面部视频中皮肤颜色的微小变化来检测心率、呼吸率等生理指标。

### 核心原理
1. **光学原理**: 心脏搏动引起血液流动 → 皮肤下血液容量变化 → 皮肤反射光强度变化
2. **信号采集**: 普通RGB摄像头捕获面部视频
3. **信号处理**: 提取颜色通道的周期性变化 → 计算心率

---

## 🎯 功能需求

### 核心功能
1. **实时心率检测**
   - 通过摄像头实时采集面部视频
   - 实时显示当前心率 (BPM)
   - 心率波形可视化

2. **多算法支持**
   - GREEN: 绿色通道法（最简单，基准算法）
   - G-R: 绿-红差分法（抗光照干扰）
   - CHROM: 色度法（鲁棒性好）
   - POS: 平面正交投影法（最佳性能，推荐）
   - ICA: 独立成分分析（学术研究用）

3. **数据记录与分析**
   - 心率历史数据记录
   - 统计分析（平均心率、最大/最小值、标准差）
   - 数据导出（CSV/JSON格式）

4. **信号质量评估**
   - 实时信号质量指示器
   - 检测质量不足时提示用户
   - 自动过滤低质量数据

### 扩展功能
1. **呼吸率检测**（可选）
   - 从rPPG信号中提取呼吸成分

2. **血氧饱和度估计**（研究性质）
   - 需要更复杂的算法

3. **多人检测**（未来版本）
   - 同时检测多张脸的心率

---

## 🏗️ 技术架构

### 整体架构（MVC模式）

```
┌─────────────────────────────────────────────────────────────┐
│                        GUI Layer (View)                      │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────────┐   │
│  │ 视频显示区   │  │ 心率显示区    │  │ 波形图表区       │   │
│  │ - 实时画面   │  │ - 当前BPM    │  │ - rPPG波形       │   │
│  │ - ROI标记    │  │ - 信号质量    │  │ - 心率历史曲线   │   │
│  └─────────────┘  └──────────────┘  └──────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ 控制面板: [启动/停止] [算法选择] [设置] [导出数据]   │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              ↕
┌─────────────────────────────────────────────────────────────┐
│                    Controller Layer                          │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ VideoController: 管理视频采集线程                       │ │
│  │ SignalController: 管理信号处理线程                      │ │
│  │ DataController: 管理数据存储和导出                      │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              ↕
┌─────────────────────────────────────────────────────────────┐
│                      Core Layer (Model)                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │ 人脸检测模块  │  │ 信号提取模块  │  │ 心率计算模块     │  │
│  │ - Haar/DNN   │  │ - ROI追踪     │  │ - FFT频谱分析    │  │
│  │ - 68关键点    │  │ - 颜色提取    │  │ - 峰值检测       │  │
│  │ - ROI定位    │  │ - 去噪滤波    │  │ - BPM输出        │  │
│  └──────────────┘  └──────────────┘  └──────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ rPPG算法库: GREEN | G-R | CHROM | POS | ICA           │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## 💻 核心模块详细设计

### 模块1: 视频采集模块 (VideoCapture)

**职责**: 从摄像头实时采集视频帧

**技术方案**:
```python
class VideoCaptureThread(QThread):
    """
    视频采集线程，运行在独立线程避免阻塞UI
    """
    frame_ready = pyqtSignal(np.ndarray)  # 发送新帧

    def __init__(self, camera_id=0, fps=30):
        self.camera_id = camera_id  # 摄像头ID
        self.target_fps = fps       # 目标帧率
        self.cap = None

    def run(self):
        self.cap = cv2.VideoCapture(self.camera_id)
        self.cap.set(cv2.CAP_PROP_FPS, self.target_fps)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        while not self._stop_requested:
            ret, frame = self.cap.read()
            if ret:
                self.frame_ready.emit(frame)
            time.sleep(1.0 / self.target_fps)
```

**关键参数**:
- **FPS**: 30fps（平衡性能和准确性）
- **分辨率**: 640x480（足够用于人脸检测）
- **色彩空间**: BGR → RGB转换

---

### 模块2: 人脸检测与ROI选择 (FaceDetector)

**职责**: 检测人脸位置并选择最佳ROI区域

**技术方案**:

#### 2.1 人脸检测
```python
class FaceDetector:
    """
    支持多种检测器，按优先级尝试
    """
    def __init__(self, method="dnn"):
        self.method = method

        if method == "dnn":
            # DNN方法（推荐，准确度高）
            self.net = cv2.dnn.readNetFromCaffe(
                "deploy.prototxt",
                "res10_300x300_ssd_iter_140000.caffemodel"
            )
        elif method == "haar":
            # Haar级联（轻量，速度快）
            self.face_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            )
        elif method == "mediapipe":
            # MediaPipe（最准确，支持关键点）
            import mediapipe as mp
            self.mp_face = mp.solutions.face_detection
            self.detector = self.mp_face.FaceDetection(
                model_selection=0,
                min_detection_confidence=0.5
            )

    def detect(self, frame):
        """返回 (x, y, w, h) 或 None"""
        if self.method == "dnn":
            return self._detect_dnn(frame)
        elif self.method == "haar":
            return self._detect_haar(frame)
        elif self.method == "mediapipe":
            return self._detect_mediapipe(frame)
```

#### 2.2 ROI选择策略

**方案A: 全脸ROI**（最简单）
```python
# 使用整个检测到的人脸区域
roi = frame[y:y+h, x:x+w]
```

**方案B: 前额+脸颊ROI**（推荐，研究证明最佳）
```python
# 根据人脸位置计算子区域
forehead = frame[y:y+h//3, x:x+w]           # 上1/3
left_cheek = frame[y+h//3:y+2*h//3, x:x+w//3]  # 左脸颊
right_cheek = frame[y+h//3:y+2*h//3, x+2*w//3:x+w]  # 右脸颊

# 组合多个ROI的信号
roi_list = [forehead, left_cheek, right_cheek]
```

**方案C: 基于关键点的ROI**（最准确，需要额外计算）
```python
# 使用dlib或MediaPipe检测68个面部关键点
# 选择额头、鼻子、脸颊等稳定区域
landmarks = self.landmark_detector(frame)
forehead_points = landmarks[17:27]  # 眉毛上方
roi = self._extract_roi_from_landmarks(frame, forehead_points)
```

**推荐**: 先实现方案B，未来可扩展到方案C

---

### 模块3: 信号提取模块 (SignalExtractor)

**职责**: 从ROI区域提取rPPG原始信号

**技术流程**:

```python
class SignalExtractor:
    """
    信号提取和预处理
    """
    def __init__(self, buffer_size=300):  # 10秒@30fps
        self.buffer_size = buffer_size
        self.signal_buffer = {
            'red': deque(maxlen=buffer_size),
            'green': deque(maxlen=buffer_size),
            'blue': deque(maxlen=buffer_size),
            'timestamps': deque(maxlen=buffer_size)
        }

    def extract_from_roi(self, roi_frame, timestamp):
        """
        从ROI提取颜色信号
        """
        # 1. 计算ROI的平均颜色值
        mean_color = cv2.mean(roi_frame)[:3]  # (B, G, R)

        # 2. 空间平均（可选：使用加权平均，中心权重更高）
        # weighted_mean = self._weighted_spatial_average(roi_frame)

        # 3. 添加到缓冲区
        self.signal_buffer['red'].append(mean_color[2])
        self.signal_buffer['green'].append(mean_color[1])
        self.signal_buffer['blue'].append(mean_color[0])
        self.signal_buffer['timestamps'].append(timestamp)

        return mean_color

    def get_normalized_signals(self):
        """
        获取归一化的信号
        """
        r = np.array(self.signal_buffer['red'])
        g = np.array(self.signal_buffer['green'])
        b = np.array(self.signal_buffer['blue'])

        # 归一化（去除直流分量）
        r = (r - np.mean(r)) / np.std(r)
        g = (g - np.mean(g)) / np.std(g)
        b = (b - np.mean(b)) / np.std(b)

        return r, g, b
```

**关键技术点**:
1. **空间平均**: 对ROI内所有像素求平均，降低噪声
2. **时间缓冲**: 保持足够长度的信号窗口（建议8-12秒）
3. **归一化**: 去除直流分量，标准化方差

---

### 模块4: rPPG算法模块 (RPPGAlgorithms)

**职责**: 实现多种rPPG算法，从RGB信号中提取脉搏信号

#### 算法1: GREEN（最简单，基准）
```python
def algorithm_green(r, g, b):
    """
    直接使用绿色通道
    原理：血红蛋白对绿光吸收最强
    """
    return g
```

#### 算法2: G-R（改进版）
```python
def algorithm_g_minus_r(r, g, b):
    """
    绿色减红色
    优点：减少光照变化影响
    """
    return g - r
```

#### 算法3: CHROM（色度法，中等复杂度）
```python
def algorithm_chrom(r, g, b):
    """
    CHROM算法 (De Haan & Jeanne, 2013)
    通过色度投影消除光照影响
    """
    # 归一化
    r_norm = r / np.mean(r)
    g_norm = g / np.mean(g)
    b_norm = b / np.mean(b)

    # CHROM线性组合
    X = 3 * r_norm - 2 * g_norm
    Y = 1.5 * r_norm + g_norm - 1.5 * b_norm

    # 计算脉搏信号
    alpha = np.std(X) / np.std(Y)
    signal = X - alpha * Y

    return signal
```

#### 算法4: POS（推荐，最佳性能）
```python
def algorithm_pos(r, g, b):
    """
    POS算法 (Wang et al., 2017)
    平面正交投影，鲁棒性最好
    """
    # 归一化
    r_norm = r / np.mean(r)
    g_norm = g / np.mean(g)
    b_norm = b / np.mean(b)

    # 构建信号矩阵
    C = np.array([r_norm, g_norm, b_norm])

    # POS投影向量
    P = np.array([[0, 1, -1], [-2, 1, 1]])

    # 投影
    S = np.dot(P, C)

    # 组合
    signal = S[0] + (np.std(S[0]) / np.std(S[1])) * S[1]

    return signal
```

#### 算法5: ICA（学术用，复杂）
```python
def algorithm_ica(r, g, b):
    """
    ICA算法（独立成分分析）
    需要 scikit-learn
    """
    from sklearn.decomposition import FastICA

    # 构建信号矩阵
    signals = np.array([r, g, b]).T

    # ICA分解
    ica = FastICA(n_components=3, random_state=0)
    components = ica.fit_transform(signals)

    # 选择最接近脉搏的成分（通常是频率在0.7-4Hz的成分）
    # 这里需要额外的选择逻辑
    pulse_signal = self._select_pulse_component(components)

    return pulse_signal
```

**算法比较**:
| 算法 | 复杂度 | 准确度 | 抗干扰性 | 推荐场景 |
|------|-------|--------|---------|---------|
| GREEN | 低 | 中 | 差 | 理想光照，静止 |
| G-R | 低 | 中+ | 中 | 一般光照 |
| CHROM | 中 | 高 | 高 | 光照变化 |
| POS | 中 | 最高 | 最高 | **通用推荐** |
| ICA | 高 | 高 | 中 | 研究用途 |

---

### 模块5: 信号处理模块 (SignalProcessor)

**职责**: 滤波、降噪、频谱分析

#### 5.1 带通滤波
```python
class SignalProcessor:
    def __init__(self, fps=30):
        self.fps = fps

        # 设计带通滤波器
        # 心率范围: 40-200 BPM = 0.67-3.33 Hz
        self.lowcut = 0.67   # 40 BPM
        self.highcut = 3.33  # 200 BPM

    def bandpass_filter(self, signal):
        """
        巴特沃斯带通滤波器
        """
        from scipy.signal import butter, filtfilt

        nyquist = self.fps / 2.0
        low = self.lowcut / nyquist
        high = self.highcut / nyquist

        b, a = butter(4, [low, high], btype='band')
        filtered = filtfilt(b, a, signal)

        return filtered
```

#### 5.2 去趋势化
```python
def detrend_signal(self, signal):
    """
    去除低频趋势（例如呼吸、运动）
    """
    from scipy.signal import detrend
    return detrend(signal, type='linear')
```

#### 5.3 降噪（可选）
```python
def denoise_wavelet(self, signal):
    """
    小波去噪
    """
    import pywt

    # 小波分解
    coeffs = pywt.wavedec(signal, 'db4', level=4)

    # 软阈值去噪
    threshold = np.std(coeffs[-1]) * np.sqrt(2 * np.log(len(signal)))
    coeffs[1:] = [pywt.threshold(c, threshold, mode='soft') for c in coeffs[1:]]

    # 重构
    denoised = pywt.waverec(coeffs, 'db4')

    return denoised[:len(signal)]
```

---

### 模块6: 心率计算模块 (HeartRateCalculator)

**职责**: 从处理后的信号中计算心率

#### 方法1: FFT频谱分析（推荐）
```python
class HeartRateCalculator:
    def __init__(self, fps=30):
        self.fps = fps

    def calculate_hr_fft(self, signal):
        """
        通过FFT找到主频率
        """
        # 1. 计算FFT
        fft_result = np.fft.fft(signal)
        fft_freqs = np.fft.fftfreq(len(signal), 1.0 / self.fps)

        # 2. 只保留正频率部分
        positive_freqs = fft_freqs[:len(fft_freqs)//2]
        positive_fft = np.abs(fft_result[:len(fft_result)//2])

        # 3. 限制在心率范围 (0.67-3.33 Hz)
        valid_idx = np.where((positive_freqs >= 0.67) & (positive_freqs <= 3.33))[0]
        valid_freqs = positive_freqs[valid_idx]
        valid_fft = positive_fft[valid_idx]

        # 4. 找到最大峰值
        peak_idx = np.argmax(valid_fft)
        heart_rate_hz = valid_freqs[peak_idx]
        heart_rate_bpm = heart_rate_hz * 60

        # 5. 计算信号质量（功率集中度）
        signal_quality = self._calculate_quality(valid_fft, peak_idx)

        return heart_rate_bpm, signal_quality

    def _calculate_quality(self, fft_values, peak_idx):
        """
        信号质量评估：峰值功率占比
        """
        peak_power = fft_values[peak_idx]
        total_power = np.sum(fft_values)
        quality = peak_power / total_power

        # 归一化到0-100
        quality_score = min(100, quality * 500)

        return quality_score
```

#### 方法2: 峰值检测（辅助验证）
```python
def calculate_hr_peak(self, signal):
    """
    通过检测波峰计算心率
    """
    from scipy.signal import find_peaks

    # 找到所有峰值
    peaks, properties = find_peaks(
        signal,
        distance=self.fps*0.3,  # 最小峰值间隔（200BPM对应）
        prominence=0.1           # 峰值显著性
    )

    if len(peaks) < 2:
        return None

    # 计算平均峰值间隔
    peak_intervals = np.diff(peaks) / self.fps  # 转换为秒
    avg_interval = np.mean(peak_intervals)

    # 转换为BPM
    heart_rate_bpm = 60 / avg_interval

    return heart_rate_bpm
```

---

### 模块7: 信号质量评估 (QualityAssessor)

**职责**: 实时评估信号质量，给用户反馈

```python
class SignalQualityAssessor:
    """
    多维度评估信号质量
    """
    def assess(self, signal, roi_frame, face_detected):
        """
        返回质量分数 (0-100) 和提示信息
        """
        quality_score = 100
        issues = []

        # 1. 人脸检测稳定性
        if not face_detected:
            quality_score -= 50
            issues.append("未检测到人脸")
            return quality_score, issues

        # 2. ROI亮度检查
        brightness = np.mean(roi_frame)
        if brightness < 50:
            quality_score -= 20
            issues.append("光线过暗")
        elif brightness > 200:
            quality_score -= 20
            issues.append("光线过亮")

        # 3. 运动检测（帧间差异）
        if hasattr(self, 'prev_roi'):
            motion = np.mean(np.abs(roi_frame - self.prev_roi))
            if motion > 10:
                quality_score -= 15
                issues.append("运动过大，请保持静止")
        self.prev_roi = roi_frame.copy()

        # 4. 信号信噪比
        if len(signal) > 30:
            snr = self._calculate_snr(signal)
            if snr < 5:
                quality_score -= 15
                issues.append("信号噪声过大")

        # 5. 频谱峰值清晰度
        if len(signal) > 100:
            peak_clarity = self._calculate_peak_clarity(signal)
            if peak_clarity < 0.3:
                quality_score -= 10
                issues.append("信号不稳定")

        quality_score = max(0, quality_score)

        return quality_score, issues

    def _calculate_snr(self, signal):
        """计算信噪比"""
        signal_power = np.var(signal)
        noise_estimate = np.var(np.diff(signal))
        snr = 10 * np.log10(signal_power / noise_estimate)
        return snr
```

---

## 🎨 GUI界面设计

### 整体布局（PyQt5）

```python
class RPPGPluginWidget(QWidget):
    """
    rPPG插件主界面
    """
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        main_layout = QHBoxLayout()

        # === 左侧：视频显示 (60%) ===
        left_panel = self._create_video_panel()

        # === 右侧：数据显示 (40%) ===
        right_panel = self._create_data_panel()

        main_layout.addWidget(left_panel, 6)
        main_layout.addWidget(right_panel, 4)

        self.setLayout(main_layout)

    def _create_video_panel(self):
        """视频显示面板"""
        panel = QWidget()
        layout = QVBoxLayout()

        # 1. 视频显示标签
        self.video_label = QLabel()
        self.video_label.setMinimumSize(640, 480)
        self.video_label.setStyleSheet("border: 2px solid #ccc;")
        layout.addWidget(self.video_label)

        # 2. 控制按钮组
        control_layout = QHBoxLayout()

        self.start_btn = QPushButton("▶ 开始检测")
        self.stop_btn = QPushButton("⏹ 停止")
        self.stop_btn.setEnabled(False)

        self.camera_combo = QComboBox()
        self.camera_combo.addItems(["摄像头 0", "摄像头 1"])

        self.algo_combo = QComboBox()
        self.algo_combo.addItems(["POS (推荐)", "CHROM", "G-R", "GREEN", "ICA"])

        control_layout.addWidget(QLabel("摄像头:"))
        control_layout.addWidget(self.camera_combo)
        control_layout.addWidget(QLabel("算法:"))
        control_layout.addWidget(self.algo_combo)
        control_layout.addWidget(self.start_btn)
        control_layout.addWidget(self.stop_btn)

        layout.addLayout(control_layout)

        panel.setLayout(layout)
        return panel

    def _create_data_panel(self):
        """数据显示面板"""
        panel = QWidget()
        layout = QVBoxLayout()

        # 1. 心率显示卡片
        hr_card = self._create_hr_card()
        layout.addWidget(hr_card)

        # 2. 信号质量指示器
        quality_card = self._create_quality_card()
        layout.addWidget(quality_card)

        # 3. rPPG波形图
        wave_card = self._create_wave_chart()
        layout.addWidget(wave_card, 1)

        # 4. 心率历史曲线图
        history_card = self._create_history_chart()
        layout.addWidget(history_card, 1)

        # 5. 统计信息
        stats_card = self._create_stats_card()
        layout.addWidget(stats_card)

        # 6. 数据导出按钮
        export_btn = QPushButton("📊 导出数据")
        layout.addWidget(export_btn)

        panel.setLayout(layout)
        return panel

    def _create_hr_card(self):
        """心率显示卡片"""
        card = QGroupBox("实时心率")
        layout = QVBoxLayout()

        # 大号心率显示
        self.hr_label = QLabel("-- BPM")
        self.hr_label.setStyleSheet("""
            QLabel {
                font-size: 48px;
                font-weight: bold;
                color: #e74c3c;
                qproperty-alignment: AlignCenter;
            }
        """)
        layout.addWidget(self.hr_label)

        # 心跳动画图标
        self.heart_icon = QLabel("❤️")
        self.heart_icon.setStyleSheet("font-size: 32px; qproperty-alignment: AlignCenter;")
        layout.addWidget(self.heart_icon)

        card.setLayout(layout)
        return card

    def _create_quality_card(self):
        """信号质量卡片"""
        card = QGroupBox("信号质量")
        layout = QVBoxLayout()

        # 质量进度条
        self.quality_bar = QProgressBar()
        self.quality_bar.setRange(0, 100)
        self.quality_bar.setValue(0)
        self.quality_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid grey;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #27ae60;
            }
        """)
        layout.addWidget(self.quality_bar)

        # 提示信息
        self.quality_tips = QLabel("等待开始检测...")
        self.quality_tips.setWordWrap(True)
        self.quality_tips.setStyleSheet("color: #7f8c8d; font-size: 12px;")
        layout.addWidget(self.quality_tips)

        card.setLayout(layout)
        return card

    def _create_wave_chart(self):
        """rPPG波形图"""
        card = QGroupBox("rPPG信号波形")
        layout = QVBoxLayout()

        # 使用 pyqtgraph 绘制实时波形
        import pyqtgraph as pg

        self.wave_plot = pg.PlotWidget()
        self.wave_plot.setBackground('w')
        self.wave_plot.setLabel('left', 'Amplitude')
        self.wave_plot.setLabel('bottom', 'Time (s)')
        self.wave_plot.showGrid(x=True, y=True)

        self.wave_curve = self.wave_plot.plot(pen=pg.mkPen('#3498db', width=2))

        layout.addWidget(self.wave_plot)
        card.setLayout(layout)
        return card

    def _create_history_chart(self):
        """心率历史曲线"""
        card = QGroupBox("心率历史")
        layout = QVBoxLayout()

        import pyqtgraph as pg

        self.history_plot = pg.PlotWidget()
        self.history_plot.setBackground('w')
        self.history_plot.setLabel('left', 'Heart Rate (BPM)')
        self.history_plot.setLabel('bottom', 'Time (s)')
        self.history_plot.showGrid(x=True, y=True)
        self.history_plot.setYRange(40, 200)

        self.history_curve = self.history_plot.plot(
            pen=pg.mkPen('#e74c3c', width=2),
            symbol='o',
            symbolSize=5
        )

        layout.addWidget(self.history_plot)
        card.setLayout(layout)
        return card

    def _create_stats_card(self):
        """统计信息卡片"""
        card = QGroupBox("统计数据")
        layout = QGridLayout()

        # 平均心率
        layout.addWidget(QLabel("平均:"), 0, 0)
        self.avg_hr_label = QLabel("--")
        layout.addWidget(self.avg_hr_label, 0, 1)

        # 最小心率
        layout.addWidget(QLabel("最小:"), 1, 0)
        self.min_hr_label = QLabel("--")
        layout.addWidget(self.min_hr_label, 1, 1)

        # 最大心率
        layout.addWidget(QLabel("最大:"), 0, 2)
        self.max_hr_label = QLabel("--")
        layout.addWidget(self.max_hr_label, 0, 3)

        # 标准差
        layout.addWidget(QLabel("标准差:"), 1, 2)
        self.std_hr_label = QLabel("--")
        layout.addWidget(self.std_hr_label, 1, 3)

        card.setLayout(layout)
        return card
```

### 界面效果描述

```
┌──────────────────────────────────────────────────────────────────┐
│  rPPG心率检测                                                     │
├──────────────────────────────┬───────────────────────────────────┤
│                              │  ┌─ 实时心率 ─────────────────┐  │
│                              │  │                             │  │
│      视频画面                 │  │        72 BPM              │  │
│    (显示ROI框)                │  │          ❤️                │  │
│                              │  └─────────────────────────────┘  │
│                              │  ┌─ 信号质量 ─────────────────┐  │
│                              │  │  ████████░░ 85%            │  │
│                              │  │  提示: 信号良好             │  │
│                              │  └─────────────────────────────┘  │
├──────────────────────────────┤  ┌─ rPPG信号波形 ─────────────┐  │
│ 摄像头: [摄像头0 ▼]           │  │  ╱╲  ╱╲  ╱╲  ╱╲           │  │
│ 算法: [POS(推荐) ▼]          │  │ ╱  ╲╱  ╲╱  ╲╱  ╲          │  │
│ [▶开始] [⏹停止]              │  └─────────────────────────────┘  │
└──────────────────────────────┤  ┌─ 心率历史 ─────────────────┐  │
                               │  │    ●──●──●                 │  │
                               │  │  ●          ●──●           │  │
                               │  └─────────────────────────────┘  │
                               │  ┌─ 统计数据 ─────────────────┐  │
                               │  │ 平均:72  最大:85           │  │
                               │  │ 最小:65  标准差:4.2        │  │
                               │  └─────────────────────────────┘  │
                               │  [ 📊 导出数据 ]                 │
                               └───────────────────────────────────┘
```

---

## 📦 技术栈与依赖

### 必需依赖
```txt
# requirements_rppg.txt

# GUI框架
PyQt5>=5.15.0

# 计算机视觉
opencv-python>=4.8.0
opencv-contrib-python>=4.8.0  # 可选，包含额外算法

# 数值计算
numpy>=1.24.0
scipy>=1.10.0

# 信号处理（可选）
pywt>=1.4.0  # 小波变换

# 可视化
pyqtgraph>=0.13.0
matplotlib>=3.7.0  # 备用

# 人脸检测（可选，选其一）
mediapipe>=0.10.0  # Google MediaPipe，推荐
dlib>=19.24.0      # 或者用dlib

# 机器学习（仅ICA算法需要）
scikit-learn>=1.3.0
```

### 预训练模型下载
```python
# 需要下载的模型文件
models/
├── deploy.prototxt  # DNN人脸检测配置
├── res10_300x300_ssd_iter_140000.caffemodel  # DNN权重
└── shape_predictor_68_face_landmarks.dat  # 68关键点检测（可选）
```

**下载地址**:
- DNN模型: https://github.com/opencv/opencv/tree/master/samples/dnn/face_detector
- 68关键点: http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2

---

## 🔧 关键参数配置

```python
# config/rppg_config.py

class RPPGConfig:
    """rPPG系统配置"""

    # === 摄像头参数 ===
    CAMERA_ID = 0
    CAMERA_FPS = 30
    CAMERA_WIDTH = 640
    CAMERA_HEIGHT = 480

    # === 信号缓冲 ===
    BUFFER_WINDOW_SEC = 10  # 信号窗口长度（秒）
    MIN_SIGNAL_LENGTH = 150  # 最小信号长度（帧数，5秒@30fps）

    # === 心率范围 ===
    MIN_HR_BPM = 40   # 最小心率
    MAX_HR_BPM = 200  # 最大心率
    MIN_HR_HZ = MIN_HR_BPM / 60.0
    MAX_HR_HZ = MAX_HR_BPM / 60.0

    # === 滤波器参数 ===
    BANDPASS_ORDER = 4  # 巴特沃斯滤波器阶数

    # === ROI选择 ===
    ROI_METHOD = "forehead_cheeks"  # "full_face" | "forehead_cheeks" | "landmarks"
    FOREHEAD_RATIO = 0.3  # 前额占人脸高度的比例

    # === 人脸检测 ===
    FACE_DETECTOR = "dnn"  # "dnn" | "haar" | "mediapipe"
    FACE_DETECTION_CONFIDENCE = 0.5

    # === 算法选择 ===
    DEFAULT_ALGORITHM = "POS"  # "GREEN" | "G-R" | "CHROM" | "POS" | "ICA"

    # === 信号质量阈值 ===
    QUALITY_EXCELLENT = 80
    QUALITY_GOOD = 60
    QUALITY_FAIR = 40
    QUALITY_POOR = 20

    # === 数据记录 ===
    RECORD_ENABLED = True
    RECORD_INTERVAL = 1.0  # 记录间隔（秒）
    MAX_RECORD_POINTS = 1000  # 最大记录点数
```

---

## 🚀 实现步骤规划

### Phase 1: 基础框架（第1-2天）
- [x] 创建插件基本结构
- [x] 实现视频采集线程
- [x] 实现人脸检测（Haar方法）
- [x] 基础GUI界面搭建
- [x] 显示视频流和ROI框

**验收标准**: 能打开摄像头，检测人脸，标记ROI

### Phase 2: 核心算法（第3-4天）
- [x] 实现信号提取模块
- [x] 实现GREEN算法（基准）
- [x] 实现CHROM算法
- [x] 实现POS算法（重点）
- [x] 实现带通滤波器
- [x] 实现FFT心率计算

**验收标准**: 能从视频中计算出心率值

### Phase 3: 信号处理优化（第5天）
- [x] 实现信号质量评估
- [x] 添加去趋势化
- [x] 添加峰值检测验证
- [x] 优化缓冲区管理

**验收标准**: 心率稳定，误差<5 BPM

### Phase 4: GUI完善（第6天）
- [x] 完善波形图表
- [x] 添加心率历史曲线
- [x] 添加统计数据显示
- [x] 实现心跳动画效果
- [x] 添加信号质量反馈

**验收标准**: 界面美观，实时更新流畅

### Phase 5: 数据管理（第7天）
- [x] 实现数据记录功能
- [x] 实现CSV/JSON导出
- [x] 添加统计分析
- [x] 添加设置面板

**验收标准**: 能导出完整数据

### Phase 6: 测试与优化（第8天）
- [x] 性能优化（降低CPU占用）
- [x] 多种光照条件测试
- [x] 运动情况测试
- [x] 边界情况处理
- [x] 文档编写

**验收标准**: 稳定运行，CPU<30%

---

## ⚠️ 技术难点与解决方案

### 难点1: 光照变化
**问题**: 环境光变化导致信号波动
**解决方案**:
- 使用CHROM/POS算法（已归一化）
- 添加亮度检测和自动增益控制
- 提示用户调整光照

### 难点2: 运动伪影
**问题**: 头部运动引入噪声
**解决方案**:
- 使用光流法追踪ROI
- 运动检测并降低质量评分
- 提示用户保持静止

### 难点3: 实时性能
**问题**: 处理延迟，界面卡顿
**解决方案**:
- 多线程架构（视频、处理、显示分离）
- 降低处理分辨率
- 使用高效的NumPy向量化操作
- 限制图表刷新率（10Hz足够）

### 难点4: 人脸检测失败
**问题**: 特殊角度、遮挡检测失败
**解决方案**:
- 多检测器备份（DNN → MediaPipe → Haar）
- 添加置信度阈值
- 短时间丢失时用上一帧ROI

### 难点5: 心率跳变
**问题**: 计算结果不稳定
**解决方案**:
- 使用滑动窗口平滑（3-5秒）
- 卡尔曼滤波器平滑输出
- 异常值检测（超出±20 BPM则忽略）

---

## 📊 性能指标目标

| 指标 | 目标值 | 说明 |
|------|-------|------|
| 心率误差 | ±5 BPM | 与标准心率计对比 |
| 响应时间 | <10秒 | 从开始到显示稳定心率 |
| CPU占用 | <30% | 单核占用率 |
| 内存占用 | <200MB | 包含所有库 |
| FPS | ≥20fps | 视频显示帧率 |
| 信号处理延迟 | <100ms | 单帧处理时间 |

---

## 🧪 测试计划

### 单元测试
```python
# tests/test_rppg_algorithms.py
def test_pos_algorithm():
    """测试POS算法"""
    # 生成模拟信号
    r, g, b = generate_synthetic_ppg(hr=72, fps=30, duration=10)

    # 运行算法
    signal = algorithm_pos(r, g, b)

    # 计算心率
    hr, quality = calculate_hr_fft(signal, fps=30)

    # 验证误差
    assert abs(hr - 72) < 5, f"Heart rate error too large: {hr}"
```

### 集成测试
- 使用录制好的视频测试
- 对比真实心率设备（如Apple Watch）
- 不同光照条件测试
- 不同肤色人群测试

### 压力测试
- 长时间运行（1小时+）
- 快速移动测试
- 多人切换测试

---

## 📝 数据导出格式

### CSV格式
```csv
timestamp,heart_rate_bpm,signal_quality,algorithm
2024-01-01 10:00:00,72.5,85.3,POS
2024-01-01 10:00:01,73.2,87.1,POS
2024-01-01 10:00:02,71.8,84.9,POS
```

### JSON格式
```json
{
  "session_info": {
    "start_time": "2024-01-01T10:00:00",
    "end_time": "2024-01-01T10:05:00",
    "duration_sec": 300,
    "algorithm": "POS",
    "camera_fps": 30
  },
  "statistics": {
    "avg_hr": 72.5,
    "min_hr": 65.0,
    "max_hr": 85.0,
    "std_hr": 4.2,
    "avg_quality": 83.5
  },
  "data_points": [
    {"timestamp": "2024-01-01T10:00:00", "hr": 72.5, "quality": 85.3},
    {"timestamp": "2024-01-01T10:00:01", "hr": 73.2, "quality": 87.1}
  ]
}
```

---

## 🔮 未来扩展方向

### 短期扩展（1-2个月）
1. **呼吸率检测**: 从rPPG信号中提取呼吸成分（0.1-0.5 Hz）
2. **血氧估计**: 利用R/IR比值（需要研究验证）
3. **多人检测**: 同时追踪多张脸

### 中期扩展（3-6个月）
1. **深度学习方法**: 使用CNN-LSTM端到端心率检测
2. **移动端适配**: 支持手机摄像头
3. **云端分析**: 上传数据到服务器进行长期分析

### 长期扩展（6个月+）
1. **健康监测系统**: 集成运动、睡眠数据
2. **异常检测**: 心律不齐预警
3. **医疗级认证**: FDA/CFDA认证

---

## 📚 参考文献

### 核心论文
1. **POS算法**: Wang et al. "Algorithmic Principles of Remote PPG" (IEEE TBME, 2017)
2. **CHROM算法**: De Haan & Jeanne. "Robust Pulse Rate From Chrominance-Based rPPG" (IEEE TBME, 2013)
3. **综述**: Rouast et al. "Remote Heart Rate Measurement Using Low-Cost RGB Face Video: A Technical Literature Review" (Frontiers, 2018)

### 开源项目
- https://github.com/prouast/heartbeat
- https://github.com/bughht/Realtime-rPPG-Application
- https://github.com/ubicomplab/rPPG-Toolbox

---

## ✅ 验收清单

### 功能验收
- [ ] 能打开摄像头并显示视频
- [ ] 能检测人脸并标记ROI
- [ ] 能实时计算心率（误差<5 BPM）
- [ ] 支持至少3种算法切换
- [ ] 实时显示rPPG波形
- [ ] 显示心率历史曲线
- [ ] 显示信号质量评分
- [ ] 能导出CSV/JSON数据
- [ ] 界面美观流畅

### 性能验收
- [ ] CPU占用<30%
- [ ] 响应时间<10秒
- [ ] 视频显示≥20fps
- [ ] 长时间运行稳定（无内存泄漏）

### 代码质量
- [ ] 代码结构清晰，模块化
- [ ] 关键函数有注释
- [ ] 有README和使用说明
- [ ] 符合插件接口规范

---

## 🎓 总结

这是一个**技术难度中等偏上**的项目，涉及：
- 计算机视觉（人脸检测、ROI追踪）
- 数字信号处理（滤波、FFT、峰值检测）
- 生理信号分析（rPPG算法）
- 实时系统设计（多线程、性能优化）
- GUI开发（PyQt5、图表可视化）

**预估工作量**: 6-8个完整工作日

**技术风险**: 中等（主流技术栈，有开源参考）

**创新点**:
- 集成到工具箱插件系统
- 多算法对比功能
- 完善的信号质量评估
- 美观的实时可视化界面

**建议**: 先实现基础功能（GREEN算法 + 简单GUI），验证可行性后再逐步添加高级功能。
