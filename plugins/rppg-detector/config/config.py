"""
rPPG心率检测插件 - 配置文件
"""


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
    ROI_METHOD = "forehead_cheeks"  # "forehead_only" | "forehead_cheeks" | "full_face"

    # MediaPipe Face Mesh 关键点索引
    # 前额区域关键点
    FOREHEAD_INDICES = [10, 67, 69, 104, 108, 109, 151, 299, 337, 338]

    # 左脸颊关键点
    LEFT_CHEEK_INDICES = [116, 117, 118, 119, 100, 101, 36, 142, 126, 135]

    # 右脸颊关键点
    RIGHT_CHEEK_INDICES = [345, 346, 347, 348, 329, 330, 266, 371, 355, 364]

    # 鼻梁关键点（备用）
    NOSE_BRIDGE_INDICES = [6, 197, 195, 5]

    # === 人脸检测 ===
    FACE_DETECTOR = "mediapipe"  # "mediapipe" | "dnn" | "haar"
    FACE_DETECTION_CONFIDENCE = 0.5
    FACE_TRACKING_CONFIDENCE = 0.5

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

    # === 性能监控 ===
    ENABLE_PERFORMANCE_MONITOR = True
    PERFORMANCE_UPDATE_INTERVAL = 1.0  # 性能更新间隔（秒）

    # === 颜色方案 ===
    COLORS = {
        'forehead': (0, 255, 0),      # 绿色
        'left_cheek': (255, 100, 0),  # 橙色
        'right_cheek': (255, 0, 100), # 粉色
        'full_face': (0, 200, 255)    # 黄色
    }
