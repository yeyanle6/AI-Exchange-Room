"""
ROI追踪器 - 基于MediaPipe 468特征点的精确ROI定位
"""

import cv2
import numpy as np
from typing import List, Tuple, Optional
from dataclasses import dataclass
from ..config.config import RPPGConfig


@dataclass
class ROIRegion:
    """ROI区域数据结构"""
    name: str              # 区域名称（前额、左脸颊等）
    indices: List[int]     # 特征点索引列表
    points: np.ndarray     # 实际像素坐标
    color: Tuple[int, int, int]  # BGR颜色
    active: bool = True    # 是否激活

    # 统计数据
    brightness: float = 0.0
    mean_rgb: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    std_rgb: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    motion: float = 0.0    # 运动幅度（像素）
    rect: Tuple[int, int, int, int] = (0, 0, 0, 0)  # 边界框


class ROITracker:
    """
    动态ROI追踪器
    基于MediaPipe Face Mesh的468个特征点精确定位ROI区域
    """

    def __init__(self, roi_mode: str = "forehead_cheeks"):
        """
        初始化ROI追踪器

        Args:
            roi_mode: ROI模式
                - "forehead_only": 仅前额
                - "forehead_cheeks": 前额+双脸颊（推荐）
                - "full_face": 全脸
        """
        self.roi_mode = roi_mode
        self.regions: List[ROIRegion] = []
        self.prev_frame = None

        # 从配置加载颜色方案
        self.colors = RPPGConfig.COLORS

        # ROI特征点索引定义
        self.roi_indices = {
            'forehead': RPPGConfig.FOREHEAD_INDICES,
            'left_cheek': RPPGConfig.LEFT_CHEEK_INDICES,
            'right_cheek': RPPGConfig.RIGHT_CHEEK_INDICES
        }

    def update(self, frame: np.ndarray, landmarks: np.ndarray) -> List[ROIRegion]:
        """
        更新ROI区域

        Args:
            frame: 当前帧
            landmarks: 468个特征点 (468, 2)

        Returns:
            ROI区域列表
        """
        self.regions = []

        if self.roi_mode == "forehead_only":
            # 仅前额区域
            forehead_points = landmarks[self.roi_indices['forehead']]
            region = ROIRegion(
                name="前额",
                indices=self.roi_indices['forehead'],
                points=forehead_points,
                color=self.colors['forehead']
            )
            self.regions.append(region)

        elif self.roi_mode == "forehead_cheeks":
            # 前额 + 双脸颊（推荐）
            forehead_points = landmarks[self.roi_indices['forehead']]
            left_cheek_points = landmarks[self.roi_indices['left_cheek']]
            right_cheek_points = landmarks[self.roi_indices['right_cheek']]

            self.regions.extend([
                ROIRegion("前额", self.roi_indices['forehead'],
                         forehead_points, self.colors['forehead']),
                ROIRegion("左脸颊", self.roi_indices['left_cheek'],
                         left_cheek_points, self.colors['left_cheek']),
                ROIRegion("右脸颊", self.roi_indices['right_cheek'],
                         right_cheek_points, self.colors['right_cheek'])
            ])

        elif self.roi_mode == "full_face":
            # 全脸（使用所有特征点的凸包）
            region = ROIRegion(
                name="全脸",
                indices=list(range(len(landmarks))),
                points=landmarks,
                color=self.colors['full_face']
            )
            self.regions.append(region)

        # 更新每个ROI的统计信息
        for region in self.regions:
            self._update_roi_stats(frame, region)

        return self.regions

    def _update_roi_stats(self, frame: np.ndarray, region: ROIRegion):
        """
        更新ROI统计信息

        Args:
            frame: 当前帧
            region: ROI区域
        """
        # 创建ROI mask
        mask = np.zeros(frame.shape[:2], dtype=np.uint8)
        hull = cv2.convexHull(region.points)
        cv2.fillConvexPoly(mask, hull, 255)

        # 提取ROI区域
        roi_frame = cv2.bitwise_and(frame, frame, mask=mask)

        # 计算边界框
        x, y, w, h = cv2.boundingRect(hull)
        region.rect = (x, y, w, h)

        # 只处理mask内的像素
        roi_pixels = frame[mask > 0]

        if len(roi_pixels) == 0:
            return

        # 计算亮度（使用灰度）
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray_roi = gray[mask > 0]
        region.brightness = np.mean(gray_roi)

        # 计算RGB均值
        mean_b = np.mean(roi_pixels[:, 0])
        mean_g = np.mean(roi_pixels[:, 1])
        mean_r = np.mean(roi_pixels[:, 2])
        region.mean_rgb = (mean_r, mean_g, mean_b)

        # 计算RGB标准差
        std_b = np.std(roi_pixels[:, 0])
        std_g = np.std(roi_pixels[:, 1])
        std_r = np.std(roi_pixels[:, 2])
        region.std_rgb = (std_r, std_g, std_b)

        # 计算运动幅度（与上一帧比较）
        if self.prev_frame is not None:
            prev_roi_pixels = self.prev_frame[mask > 0]
            if len(prev_roi_pixels) == len(roi_pixels):
                diff = np.abs(roi_pixels.astype(float) - prev_roi_pixels.astype(float))
                region.motion = np.mean(diff)

        self.prev_frame = frame.copy()

    def draw_on_frame(self, frame: np.ndarray,
                     show_labels: bool = True,
                     show_points: bool = False) -> np.ndarray:
        """
        在视频帧上绘制ROI

        Args:
            frame: 视频帧
            show_labels: 是否显示标签
            show_points: 是否显示特征点

        Returns:
            绘制后的帧
        """
        display_frame = frame.copy()

        for region in self.regions:
            if not region.active:
                continue

            color = region.color

            # 计算凸包
            hull = cv2.convexHull(region.points)

            # 绘制半透明填充
            overlay = display_frame.copy()
            cv2.fillConvexPoly(overlay, hull, color)
            cv2.addWeighted(overlay, 0.15, display_frame, 0.85, 0, display_frame)

            # 绘制边框
            cv2.polylines(display_frame, [hull], True, color, 2)

            # 绘制特征点（可选）
            if show_points:
                for point in region.points:
                    cv2.circle(display_frame, tuple(point), 2, color, -1)

            if show_labels:
                # 获取边界框
                x, y, w, h = region.rect

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

    def get_roi_mask(self, frame_shape: Tuple[int, int], region_index: int = 0) -> np.ndarray:
        """
        获取指定ROI的mask

        Args:
            frame_shape: 帧的形状 (height, width)
            region_index: ROI区域索引

        Returns:
            mask数组
        """
        if region_index >= len(self.regions):
            return None

        region = self.regions[region_index]
        mask = np.zeros(frame_shape, dtype=np.uint8)
        hull = cv2.convexHull(region.points)
        cv2.fillConvexPoly(mask, hull, 255)

        return mask

    def extract_roi_pixels(self, frame: np.ndarray, region_index: int = 0) -> Optional[np.ndarray]:
        """
        提取指定ROI区域的像素值

        Args:
            frame: 输入帧
            region_index: ROI区域索引

        Returns:
            ROI区域的像素数组，形状为 (N, 3)
        """
        mask = self.get_roi_mask(frame.shape[:2], region_index)

        if mask is None:
            return None

        roi_pixels = frame[mask > 0]
        return roi_pixels

    def get_combined_roi_signal(self, frame: np.ndarray) -> Tuple[float, float, float]:
        """
        获取所有激活ROI的组合信号（RGB平均值）

        Args:
            frame: 输入帧

        Returns:
            (R, G, B) 组合平均值
        """
        all_r, all_g, all_b = [], [], []

        for i, region in enumerate(self.regions):
            if not region.active:
                continue

            roi_pixels = self.extract_roi_pixels(frame, i)
            if roi_pixels is not None and len(roi_pixels) > 0:
                # BGR to RGB
                all_b.append(np.mean(roi_pixels[:, 0]))
                all_g.append(np.mean(roi_pixels[:, 1]))
                all_r.append(np.mean(roi_pixels[:, 2]))

        # 计算所有ROI的平均
        if len(all_r) > 0:
            mean_r = np.mean(all_r)
            mean_g = np.mean(all_g)
            mean_b = np.mean(all_b)
            return (mean_r, mean_g, mean_b)
        else:
            return (0.0, 0.0, 0.0)

    def set_roi_mode(self, mode: str):
        """切换ROI模式"""
        if mode in ["forehead_only", "forehead_cheeks", "full_face"]:
            self.roi_mode = mode
