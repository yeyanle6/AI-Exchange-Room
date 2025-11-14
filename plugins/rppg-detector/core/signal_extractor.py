"""
信号提取模块 - 从ROI区域提取RGB时间序列信号
"""

import numpy as np
from collections import deque
from typing import Tuple, Optional
from ..config.config import RPPGConfig


class SignalExtractor:
    """
    信号提取器
    从ROI区域提取RGB颜色通道的时间序列信号
    """

    def __init__(self, buffer_size: Optional[int] = None, fps: int = 30):
        """
        初始化信号提取器

        Args:
            buffer_size: 缓冲区大小（帧数），默认为10秒的帧数
            fps: 帧率
        """
        if buffer_size is None:
            buffer_size = RPPGConfig.BUFFER_WINDOW_SEC * fps

        self.buffer_size = buffer_size
        self.fps = fps

        # 信号缓冲区
        self.signal_buffer = {
            'red': deque(maxlen=buffer_size),
            'green': deque(maxlen=buffer_size),
            'blue': deque(maxlen=buffer_size),
            'timestamps': deque(maxlen=buffer_size)
        }

        self.frame_count = 0

    def extract_from_roi(self, r: float, g: float, b: float, timestamp: float):
        """
        添加ROI的RGB信号到缓冲区

        Args:
            r: 红色通道平均值
            g: 绿色通道平均值
            b: 蓝色通道平均值
            timestamp: 时间戳（秒）
        """
        self.signal_buffer['red'].append(r)
        self.signal_buffer['green'].append(g)
        self.signal_buffer['blue'].append(b)
        self.signal_buffer['timestamps'].append(timestamp)

        self.frame_count += 1

    def get_raw_signals(self) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """
        获取原始信号

        Returns:
            (timestamps, r_signal, g_signal, b_signal)
        """
        timestamps = np.array(self.signal_buffer['timestamps'])
        r = np.array(self.signal_buffer['red'])
        g = np.array(self.signal_buffer['green'])
        b = np.array(self.signal_buffer['blue'])

        return timestamps, r, g, b

    def get_normalized_signals(self) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        获取归一化的信号（去除直流分量，标准化方差）

        Returns:
            (r_norm, g_norm, b_norm)
        """
        r = np.array(self.signal_buffer['red'])
        g = np.array(self.signal_buffer['green'])
        b = np.array(self.signal_buffer['blue'])

        if len(r) < 10:
            return r, g, b

        # 归一化：(x - mean) / std
        r_norm = (r - np.mean(r)) / (np.std(r) + 1e-8)
        g_norm = (g - np.mean(g)) / (np.std(g) + 1e-8)
        b_norm = (b - np.mean(b)) / (np.std(b) + 1e-8)

        return r_norm, g_norm, b_norm

    def get_signal_length(self) -> int:
        """获取当前信号长度"""
        return len(self.signal_buffer['red'])

    def is_ready(self) -> bool:
        """
        信号是否准备好（达到最小长度）

        Returns:
            True if ready
        """
        return self.get_signal_length() >= RPPGConfig.MIN_SIGNAL_LENGTH

    def clear(self):
        """清空缓冲区"""
        self.signal_buffer['red'].clear()
        self.signal_buffer['green'].clear()
        self.signal_buffer['blue'].clear()
        self.signal_buffer['timestamps'].clear()
        self.frame_count = 0

    def get_buffer_status(self) -> Tuple[int, int, float]:
        """
        获取缓冲区状态

        Returns:
            (current_size, max_size, fill_percentage)
        """
        current = self.get_signal_length()
        maximum = self.buffer_size
        percentage = (current / maximum) * 100 if maximum > 0 else 0

        return current, maximum, percentage

    def calculate_snr(self) -> float:
        """
        计算信号的信噪比

        Returns:
            SNR in dB
        """
        g = np.array(self.signal_buffer['green'])

        if len(g) < 30:
            return 0.0

        # 信号功率
        signal_power = np.var(g)

        # 噪声估计（通过一阶差分）
        noise = np.diff(g)
        noise_power = np.var(noise)

        # SNR (dB)
        if noise_power > 0:
            snr = 10 * np.log10(signal_power / noise_power)
        else:
            snr = 100.0  # 非常高的SNR

        return snr

    def get_statistics(self) -> dict:
        """
        获取信号统计信息

        Returns:
            统计字典
        """
        r = np.array(self.signal_buffer['red'])
        g = np.array(self.signal_buffer['green'])
        b = np.array(self.signal_buffer['blue'])

        if len(r) == 0:
            return {
                'mean_r': 0, 'mean_g': 0, 'mean_b': 0,
                'std_r': 0, 'std_g': 0, 'std_b': 0,
                'snr': 0, 'length': 0
            }

        stats = {
            'mean_r': np.mean(r),
            'mean_g': np.mean(g),
            'mean_b': np.mean(b),
            'std_r': np.std(r),
            'std_g': np.std(g),
            'std_b': np.std(b),
            'snr': self.calculate_snr(),
            'length': len(r)
        }

        return stats
