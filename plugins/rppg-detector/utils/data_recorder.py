"""
数据记录模块
"""

import json
import csv
from datetime import datetime
from typing import List, Dict
from collections import deque
from ..config.config import RPPGConfig


class DataRecorder:
    """
    数据记录器
    记录心率、信号质量等数据
    """

    def __init__(self, max_points: int = None):
        """
        初始化数据记录器

        Args:
            max_points: 最大记录点数
        """
        if max_points is None:
            max_points = RPPGConfig.MAX_RECORD_POINTS

        self.max_points = max_points

        # 数据缓冲区
        self.data_points = deque(maxlen=max_points)

        # 会话信息
        self.session_start = datetime.now()
        self.algorithm = RPPGConfig.DEFAULT_ALGORITHM

    def record_data_point(self, timestamp: float, heart_rate: float,
                          signal_quality: float, **kwargs):
        """
        记录一个数据点

        Args:
            timestamp: 时间戳（秒）
            heart_rate: 心率 (BPM)
            signal_quality: 信号质量 (0-100)
            **kwargs: 其他参数
        """
        data_point = {
            'timestamp': timestamp,
            'datetime': datetime.now().isoformat(),
            'heart_rate': heart_rate,
            'signal_quality': signal_quality
        }

        # 添加额外参数
        data_point.update(kwargs)

        self.data_points.append(data_point)

    def get_data_points(self) -> List[Dict]:
        """获取所有数据点"""
        return list(self.data_points)

    def get_statistics(self) -> Dict:
        """
        计算统计信息

        Returns:
            统计字典
        """
        if len(self.data_points) == 0:
            return {
                'count': 0,
                'avg_hr': 0,
                'min_hr': 0,
                'max_hr': 0,
                'std_hr': 0,
                'avg_quality': 0
            }

        import numpy as np

        hrs = [p['heart_rate'] for p in self.data_points]
        qualities = [p['signal_quality'] for p in self.data_points]

        stats = {
            'count': len(self.data_points),
            'avg_hr': np.mean(hrs),
            'min_hr': np.min(hrs),
            'max_hr': np.max(hrs),
            'std_hr': np.std(hrs),
            'avg_quality': np.mean(qualities)
        }

        return stats

    def export_to_csv(self, filename: str):
        """
        导出数据到CSV文件

        Args:
            filename: 文件名
        """
        if len(self.data_points) == 0:
            print("⚠ 没有数据可导出")
            return

        with open(filename, 'w', newline='') as csvfile:
            # 获取所有字段名
            fieldnames = list(self.data_points[0].keys())

            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for point in self.data_points:
                writer.writerow(point)

        print(f"✓ 数据已导出到 {filename}")

    def export_to_json(self, filename: str):
        """
        导出数据到JSON文件

        Args:
            filename: 文件名
        """
        if len(self.data_points) == 0:
            print("⚠ 没有数据可导出")
            return

        # 准备导出数据
        export_data = {
            'session_info': {
                'start_time': self.session_start.isoformat(),
                'end_time': datetime.now().isoformat(),
                'algorithm': self.algorithm,
                'duration_sec': (datetime.now() - self.session_start).total_seconds()
            },
            'statistics': self.get_statistics(),
            'data_points': list(self.data_points)
        }

        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2)

        print(f"✓ 数据已导出到 {filename}")

    def clear(self):
        """清空数据"""
        self.data_points.clear()
        self.session_start = datetime.now()

    def set_algorithm(self, algorithm: str):
        """设置算法名称"""
        self.algorithm = algorithm

    def get_session_duration(self) -> float:
        """获取会话时长（秒）"""
        return (datetime.now() - self.session_start).total_seconds()
