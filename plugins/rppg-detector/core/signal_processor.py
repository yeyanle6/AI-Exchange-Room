"""
信号处理模块 - 滤波、去趋势、频谱分析
"""

import numpy as np
from scipy import signal
from typing import Tuple, Optional
from ..config.config import RPPGConfig


class SignalProcessor:
    """
    信号处理器
    """

    def __init__(self, fps: int = 30):
        """
        初始化信号处理器

        Args:
            fps: 采样率（帧率）
        """
        self.fps = fps

        # 心率范围 (Hz)
        self.lowcut = RPPGConfig.MIN_HR_HZ
        self.highcut = RPPGConfig.MAX_HR_HZ

        # 滤波器阶数
        self.order = RPPGConfig.BANDPASS_ORDER

    def detrend(self, signal_data: np.ndarray) -> np.ndarray:
        """
        去趋势化（去除低频趋势）

        Args:
            signal_data: 输入信号

        Returns:
            去趋势后的信号
        """
        if len(signal_data) < 10:
            return signal_data

        detrended = signal.detrend(signal_data, type='linear')
        return detrended

    def bandpass_filter(self, signal_data: np.ndarray) -> np.ndarray:
        """
        巴特沃斯带通滤波器

        Args:
            signal_data: 输入信号

        Returns:
            滤波后的信号
        """
        if len(signal_data) < 30:
            return signal_data

        nyquist = self.fps / 2.0
        low = self.lowcut / nyquist
        high = self.highcut / nyquist

        # 确保频率在有效范围内
        low = max(0.001, min(low, 0.999))
        high = max(low + 0.001, min(high, 0.999))

        try:
            b, a = signal.butter(self.order, [low, high], btype='band')
            filtered = signal.filtfilt(b, a, signal_data)
            return filtered
        except Exception as e:
            print(f"⚠ 带通滤波失败: {e}")
            return signal_data

    def normalize(self, signal_data: np.ndarray) -> np.ndarray:
        """
        归一化信号（零均值，单位方差）

        Args:
            signal_data: 输入信号

        Returns:
            归一化信号
        """
        if len(signal_data) < 2:
            return signal_data

        mean = np.mean(signal_data)
        std = np.std(signal_data)

        if std < 1e-8:
            return signal_data - mean

        normalized = (signal_data - mean) / std
        return normalized

    def moving_average(self, signal_data: np.ndarray, window_size: int = 5) -> np.ndarray:
        """
        移动平均滤波

        Args:
            signal_data: 输入信号
            window_size: 窗口大小

        Returns:
            平滑后的信号
        """
        if len(signal_data) < window_size:
            return signal_data

        kernel = np.ones(window_size) / window_size
        smoothed = np.convolve(signal_data, kernel, mode='same')
        return smoothed

    def compute_fft(self, signal_data: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        计算FFT频谱

        Args:
            signal_data: 输入信号

        Returns:
            (frequencies, power): 频率数组和功率谱
        """
        n = len(signal_data)

        if n < 30:
            return np.array([]), np.array([])

        # 计算FFT
        fft_result = np.fft.fft(signal_data)
        fft_freqs = np.fft.fftfreq(n, 1.0 / self.fps)

        # 只保留正频率部分
        positive_freqs = fft_freqs[:n//2]
        positive_fft = np.abs(fft_result[:n//2])

        # 计算功率谱
        power = positive_fft ** 2

        return positive_freqs, power

    def find_peak_frequency(self, signal_data: np.ndarray) -> Tuple[float, float, np.ndarray, np.ndarray]:
        """
        找到功率谱的峰值频率

        Args:
            signal_data: 输入信号

        Returns:
            (peak_freq, peak_power, all_freqs, all_power)
        """
        freqs, power = self.compute_fft(signal_data)

        if len(freqs) == 0:
            return 0.0, 0.0, freqs, power

        # 限制在心率范围内
        valid_idx = np.where((freqs >= self.lowcut) & (freqs <= self.highcut))[0]

        if len(valid_idx) == 0:
            return 0.0, 0.0, freqs, power

        valid_freqs = freqs[valid_idx]
        valid_power = power[valid_idx]

        # 找到最大峰值
        peak_idx = np.argmax(valid_power)
        peak_freq = valid_freqs[peak_idx]
        peak_power = valid_power[peak_idx]

        return peak_freq, peak_power, freqs, power

    def process_pipeline(self, signal_data: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        完整的信号处理流程

        Args:
            signal_data: 原始信号

        Returns:
            (normalized, detrended, filtered): 归一化、去趋势、滤波后的信号
        """
        # 1. 归一化
        normalized = self.normalize(signal_data)

        # 2. 去趋势
        detrended = self.detrend(normalized)

        # 3. 带通滤波
        filtered = self.bandpass_filter(detrended)

        return normalized, detrended, filtered

    def calculate_signal_quality(self, signal_data: np.ndarray) -> float:
        """
        计算信号质量分数（基于功率谱峰值清晰度）

        Args:
            signal_data: 输入信号

        Returns:
            quality_score: 0-100
        """
        if len(signal_data) < 60:
            return 0.0

        freqs, power = self.compute_fft(signal_data)

        if len(freqs) == 0:
            return 0.0

        # 限制在心率范围内
        valid_idx = np.where((freqs >= self.lowcut) & (freqs <= self.highcut))[0]

        if len(valid_idx) == 0:
            return 0.0

        valid_power = power[valid_idx]

        # 计算峰值功率占比
        peak_power = np.max(valid_power)
        total_power = np.sum(valid_power)

        if total_power < 1e-8:
            return 0.0

        # 功率集中度
        concentration = peak_power / total_power

        # 归一化到0-100
        quality_score = min(100, concentration * 500)

        return quality_score
