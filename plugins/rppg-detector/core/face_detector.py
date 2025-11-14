"""
人脸检测模块 - 使用MediaPipe Face Mesh (468特征点)
"""

import cv2
import numpy as np
from typing import Optional, List, Tuple


class FaceDetector:
    """
    人脸检测器 - 使用MediaPipe Face Mesh获取468个面部特征点
    """

    def __init__(self,
                 min_detection_confidence: float = 0.5,
                 min_tracking_confidence: float = 0.5):
        """
        初始化人脸检测器

        Args:
            min_detection_confidence: 最小检测置信度
            min_tracking_confidence: 最小追踪置信度
        """
        try:
            import mediapipe as mp
            self.mp_face_mesh = mp.solutions.face_mesh
            self.mp_drawing = mp.solutions.drawing_utils
            self.mp_drawing_styles = mp.solutions.drawing_styles

            # 初始化Face Mesh
            self.face_mesh = self.mp_face_mesh.FaceMesh(
                max_num_faces=1,
                refine_landmarks=True,
                min_detection_confidence=min_detection_confidence,
                min_tracking_confidence=min_tracking_confidence
            )

            self.has_mediapipe = True
            print("✓ MediaPipe Face Mesh 初始化成功")

        except ImportError:
            print("⚠ MediaPipe未安装，请运行: pip install mediapipe")
            self.has_mediapipe = False
            self.face_mesh = None

        self.last_landmarks = None
        self.face_detected = False

    def detect(self, frame: np.ndarray) -> Optional[np.ndarray]:
        """
        检测人脸并返回468个特征点

        Args:
            frame: BGR格式的图像帧

        Returns:
            landmarks: (468, 2) 的numpy数组，每行是(x, y)坐标，失败返回None
        """
        if not self.has_mediapipe:
            return None

        # 转换为RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # 处理图像
        results = self.face_mesh.process(rgb_frame)

        if not results.multi_face_landmarks:
            self.face_detected = False
            return None

        # 获取第一个检测到的人脸
        face_landmarks = results.multi_face_landmarks[0]

        # 转换为像素坐标
        h, w = frame.shape[:2]
        landmarks = []

        for landmark in face_landmarks.landmark:
            x = int(landmark.x * w)
            y = int(landmark.y * h)
            landmarks.append([x, y])

        landmarks = np.array(landmarks)

        self.last_landmarks = landmarks
        self.face_detected = True

        return landmarks

    def get_face_box(self, landmarks: np.ndarray) -> Tuple[int, int, int, int]:
        """
        从特征点计算人脸边界框

        Args:
            landmarks: (468, 2) 特征点数组

        Returns:
            (x, y, w, h): 人脸边界框
        """
        x_min = np.min(landmarks[:, 0])
        x_max = np.max(landmarks[:, 0])
        y_min = np.min(landmarks[:, 1])
        y_max = np.max(landmarks[:, 1])

        x = int(x_min)
        y = int(y_min)
        w = int(x_max - x_min)
        h = int(y_max - y_min)

        return (x, y, w, h)

    def draw_landmarks(self, frame: np.ndarray, landmarks: np.ndarray,
                       draw_all: bool = False) -> np.ndarray:
        """
        在图像上绘制特征点

        Args:
            frame: 输入图像
            landmarks: 特征点数组
            draw_all: 是否绘制所有468个点（False时只绘制关键点）

        Returns:
            绘制后的图像
        """
        display_frame = frame.copy()

        if draw_all:
            # 绘制所有点
            for point in landmarks:
                cv2.circle(display_frame, tuple(point), 1, (0, 255, 0), -1)
        else:
            # 只绘制关键点（前额、脸颊等）
            key_indices = [10, 67, 109, 151, 337, 338, 116, 345]
            for idx in key_indices:
                if idx < len(landmarks):
                    point = landmarks[idx]
                    cv2.circle(display_frame, tuple(point), 3, (0, 255, 0), -1)

        return display_frame

    def is_face_detected(self) -> bool:
        """是否检测到人脸"""
        return self.face_detected

    def release(self):
        """释放资源"""
        if self.face_mesh is not None:
            self.face_mesh.close()
