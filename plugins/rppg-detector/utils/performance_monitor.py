"""
性能监控模块
"""

import time
import psutil
from collections import deque
from typing import Dict


class PerformanceMonitor:
    """
    性能监控器
    监控CPU、FPS、内存等
    """

    def __init__(self, window_size: int = 30):
        """
        初始化性能监控器

        Args:
            window_size: 滑动窗口大小
        """
        self.window_size = window_size

        # FPS监控
        self.frame_times = deque(maxlen=window_size)
        self.last_frame_time = time.time()
        self.frame_count = 0

        # CPU监控
        self.cpu_usage = deque(maxlen=window_size)

        # 处理延迟
        self.processing_times = deque(maxlen=window_size)

        # 开始时间
        self.start_time = time.time()

        # 进程对象
        self.process = psutil.Process()

    def record_frame(self):
        """记录一帧处理完成"""
        current_time = time.time()
        frame_time = current_time - self.last_frame_time
        self.frame_times.append(frame_time)
        self.last_frame_time = current_time
        self.frame_count += 1

    def record_processing_time(self, processing_time: float):
        """
        记录处理时间

        Args:
            processing_time: 处理时间（秒）
        """
        self.processing_times.append(processing_time * 1000)  # 转换为毫秒

    def update_cpu(self):
        """更新CPU使用率"""
        try:
            cpu_percent = self.process.cpu_percent(interval=None)
            self.cpu_usage.append(cpu_percent)
        except:
            pass

    def get_fps(self) -> float:
        """获取当前FPS"""
        if len(self.frame_times) == 0:
            return 0.0

        avg_frame_time = sum(self.frame_times) / len(self.frame_times)

        if avg_frame_time < 1e-8:
            return 0.0

        fps = 1.0 / avg_frame_time
        return fps

    def get_avg_cpu(self) -> float:
        """获取平均CPU使用率"""
        if len(self.cpu_usage) == 0:
            return 0.0

        return sum(self.cpu_usage) / len(self.cpu_usage)

    def get_avg_latency(self) -> float:
        """获取平均处理延迟（毫秒）"""
        if len(self.processing_times) == 0:
            return 0.0

        return sum(self.processing_times) / len(self.processing_times)

    def get_memory_usage(self) -> float:
        """获取内存使用（MB）"""
        try:
            mem_info = self.process.memory_info()
            return mem_info.rss / (1024 * 1024)  # 转换为MB
        except:
            return 0.0

    def get_runtime(self) -> float:
        """获取运行时间（秒）"""
        return time.time() - self.start_time

    def get_runtime_formatted(self) -> str:
        """获取格式化的运行时间 HH:MM:SS"""
        runtime = self.get_runtime()
        hours = int(runtime // 3600)
        minutes = int((runtime % 3600) // 60)
        seconds = int(runtime % 60)

        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    def get_stats(self) -> Dict:
        """
        获取所有性能统计

        Returns:
            统计字典
        """
        return {
            'fps': self.get_fps(),
            'avg_cpu': self.get_avg_cpu(),
            'avg_latency': self.get_avg_latency(),
            'memory_mb': self.get_memory_usage(),
            'runtime': self.get_runtime(),
            'runtime_formatted': self.get_runtime_formatted(),
            'frame_count': self.frame_count
        }

    def reset(self):
        """重置监控器"""
        self.frame_times.clear()
        self.cpu_usage.clear()
        self.processing_times.clear()
        self.frame_count = 0
        self.start_time = time.time()
        self.last_frame_time = time.time()
