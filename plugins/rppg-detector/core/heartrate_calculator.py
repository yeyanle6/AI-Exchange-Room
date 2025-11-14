"""
心率计算模块 - 从信号中计算心率
"""

import numpy as np
from typing import Tuple, Optional
from scipy.signal import find_peaks
from collections import deque
from .signal_processor import SignalProcessor


class HeartRateCalculator:
    """
    心率计算器
    使用FFT频谱分析和峰值检测计算心率
    """

    def __init__(self, fps: int = 30, smoothing_window: int = 3):
        """
        初始化心率计算器

        Args:
            fps: 帧率
            smoothing_window: 平滑窗口大小（帧数）
        """
        self.fps = fps
        self.processor = SignalProcessor(fps)
        self.smoothing_window = smoothing_window

        # 心率历史（用于平滑）
        self.hr_history = deque(maxlen=smoothing_window)

        # 最新心率
        self.current_hr = 0.0
        self.signal_quality = 0.0

    def calculate_hr_fft(self, signal_data: np.ndarray) -> Tuple[float, float]:
        """
        通过FFT频谱分析计算心率

        Args:
            signal_data: 输入信号

        Returns:
            (heart_rate_bpm, signal_quality)
        """
        if len(signal_data) < 60:
            return 0.0, 0.0

        # 找到峰值频率
        peak_freq, peak_power, freqs, power = self.processor.find_peak_frequency(signal_data)

        # 转换为BPM
        heart_rate_bpm = peak_freq * 60.0

        # 计算信号质量
        signal_quality = self.processor.calculate_signal_quality(signal_data)

        return heart_rate_bpm, signal_quality

    def calculate_hr_peaks(self, signal_data: np.ndarray) -> Optional[float]:
        """
        通过峰值检测计算心率（辅助方法）

        Args:
            signal_data: 输入信号

        Returns:
            heart_rate_bpm or None
        """
        if len(signal_data) < 60:
            return None

        # 找到所有峰值
        peaks, properties = find_peaks(
            signal_data,
            distance=self.fps * 0.3,  # 最小峰值间隔（200BPM对应）
            prominence=0.1             # 峰值显著性
        )

        if len(peaks) < 2:
            return None

        # 计算平均峰值间隔
        peak_intervals = np.diff(peaks) / self.fps  # 转换为秒
        avg_interval = np.mean(peak_intervals)

        if avg_interval < 1e-8:
            return None

        # 转换为BPM
        heart_rate_bpm = 60.0 / avg_interval

        # 检查是否在合理范围内
        if 40 <= heart_rate_bpm <= 200:
            return heart_rate_bpm
        else:
            return None

    def calculate(self, signal_data: np.ndarray) -> Tuple[float, float]:
        """
        计算心率（主方法）

        使用FFT方法，并用峰值检测验证

        Args:
            signal_data: 输入信号

        Returns:
            (heart_rate_bpm, signal_quality)
        """
        # 使用FFT方法
        hr_fft, quality = self.calculate_hr_fft(signal_data)

        # 使用峰值检测验证
        hr_peaks = self.calculate_hr_peaks(signal_data)

        # 如果两种方法结果接近，增加置信度
        if hr_peaks is not None and abs(hr_fft - hr_peaks) < 10:
            quality = min(100, quality * 1.2)
        elif hr_peaks is not None and abs(hr_fft - hr_peaks) > 20:
            # 结果差异大，降低置信度
            quality *= 0.7

        # 添加到历史
        if quality > 30:  # 只有质量较好的才加入历史
            self.hr_history.append(hr_fft)

        # 平滑输出
        if len(self.hr_history) > 0:
            smoothed_hr = np.median(list(self.hr_history))
        else:
            smoothed_hr = hr_fft

        self.current_hr = smoothed_hr
        self.signal_quality = quality

        return smoothed_hr, quality

    def get_current_hr(self) -> float:
        """获取当前心率"""
        return self.current_hr

    def get_signal_quality(self) -> float:
        """获取信号质量"""
        return self.signal_quality

    def reset(self):
        """重置计算器"""
        self.hr_history.clear()
        self.current_hr = 0.0
        self.signal_quality = 0.0

    def is_valid_hr(self, hr: float) -> bool:
        """
        检查心率是否在有效范围内

        Args:
            hr: 心率 (BPM)

        Returns:
            True if valid
        """
        return 40 <= hr <= 200

    def calculate_hrv_statistics(self, hr_history: list) -> dict:
        """
        计算心率变异性(HRV)统计指标

        Args:
            hr_history: 心率历史列表

        Returns:
            HRV统计字典
        """
        if len(hr_history) < 10:
            return {
                'mean_hr': 0,
                'std_hr': 0,
                'min_hr': 0,
                'max_hr': 0,
                'rmssd': 0
            }

        hr_array = np.array(hr_history)

        # 计算RR间期（毫秒）
        rr_intervals = 60000.0 / hr_array  # BPM to ms

        # 计算RMSSD (Root Mean Square of Successive Differences)
        successive_diffs = np.diff(rr_intervals)
        rmssd = np.sqrt(np.mean(successive_diffs ** 2))

        stats = {
            'mean_hr': np.mean(hr_array),
            'std_hr': np.std(hr_array),
            'min_hr': np.min(hr_array),
            'max_hr': np.max(hr_array),
            'rmssd': rmssd
        }

        return stats
