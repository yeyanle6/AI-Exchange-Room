"""
rPPG算法模块 - 实现多种rPPG算法
包括: GREEN, G-R, CHROM, POS, ICA
"""

import numpy as np
from typing import Tuple


class RPPGAlgorithms:
    """
    rPPG算法集合
    """

    @staticmethod
    def algorithm_green(r: np.ndarray, g: np.ndarray, b: np.ndarray) -> np.ndarray:
        """
        GREEN算法 - 最简单的基准算法
        直接使用绿色通道

        原理：血红蛋白对绿光吸收最强

        Args:
            r, g, b: RGB信号（已归一化）

        Returns:
            pulse_signal: 脉搏信号
        """
        return g

    @staticmethod
    def algorithm_g_minus_r(r: np.ndarray, g: np.ndarray, b: np.ndarray) -> np.ndarray:
        """
        G-R算法 - 绿色减红色
        改进版GREEN算法

        优点：减少光照变化影响

        Args:
            r, g, b: RGB信号（已归一化）

        Returns:
            pulse_signal: 脉搏信号
        """
        return g - r

    @staticmethod
    def algorithm_chrom(r: np.ndarray, g: np.ndarray, b: np.ndarray) -> np.ndarray:
        """
        CHROM算法 (Chrominance-based)
        De Haan & Jeanne, IEEE TBME 2013

        通过色度投影消除光照影响

        Args:
            r, g, b: RGB信号（原始信号，未归一化）

        Returns:
            pulse_signal: 脉搏信号
        """
        # 归一化
        r_norm = r / (np.mean(r) + 1e-8)
        g_norm = g / (np.mean(g) + 1e-8)
        b_norm = b / (np.mean(b) + 1e-8)

        # CHROM线性组合
        X = 3 * r_norm - 2 * g_norm
        Y = 1.5 * r_norm + g_norm - 1.5 * b_norm

        # 计算脉搏信号
        std_X = np.std(X)
        std_Y = np.std(Y)

        if std_Y > 1e-8:
            alpha = std_X / std_Y
        else:
            alpha = 1.0

        signal = X - alpha * Y

        return signal

    @staticmethod
    def algorithm_pos(r: np.ndarray, g: np.ndarray, b: np.ndarray) -> np.ndarray:
        """
        POS算法 (Plane-Orthogonal-to-Skin)
        Wang et al., IEEE TBME 2017

        平面正交投影，鲁棒性最好（推荐算法）

        Args:
            r, g, b: RGB信号（原始信号，未归一化）

        Returns:
            pulse_signal: 脉搏信号
        """
        # 归一化
        r_norm = r / (np.mean(r) + 1e-8)
        g_norm = g / (np.mean(g) + 1e-8)
        b_norm = b / (np.mean(b) + 1e-8)

        # 构建信号矩阵
        C = np.array([r_norm, g_norm, b_norm])

        # POS投影向量
        P = np.array([[0, 1, -1],
                     [-2, 1, 1]])

        # 投影
        S = np.dot(P, C)

        # 组合
        std_S0 = np.std(S[0])
        std_S1 = np.std(S[1])

        if std_S1 > 1e-8:
            h = std_S0 / std_S1
        else:
            h = 1.0

        signal = S[0] + h * S[1]

        return signal

    @staticmethod
    def algorithm_ica(r: np.ndarray, g: np.ndarray, b: np.ndarray) -> np.ndarray:
        """
        ICA算法 (Independent Component Analysis)
        独立成分分析

        需要 scikit-learn

        Args:
            r, g, b: RGB信号

        Returns:
            pulse_signal: 脉搏信号
        """
        try:
            from sklearn.decomposition import FastICA

            # 构建信号矩阵 (n_samples, n_features)
            signals = np.array([r, g, b]).T

            # ICA分解
            ica = FastICA(n_components=3, random_state=0, max_iter=1000)
            components = ica.fit_transform(signals)

            # 选择最接近脉搏的成分
            # 通常选择方差最大的成分
            variances = np.var(components, axis=0)
            best_component = np.argmax(variances)

            pulse_signal = components[:, best_component]

            return pulse_signal

        except ImportError:
            print("⚠ ICA算法需要安装 scikit-learn: pip install scikit-learn")
            # 降级到CHROM算法
            return RPPGAlgorithms.algorithm_chrom(r, g, b)

    @staticmethod
    def process(algorithm: str, r: np.ndarray, g: np.ndarray, b: np.ndarray) -> np.ndarray:
        """
        根据算法名称处理信号

        Args:
            algorithm: 算法名称 ("GREEN", "G-R", "CHROM", "POS", "ICA")
            r, g, b: RGB信号

        Returns:
            pulse_signal: 脉搏信号
        """
        algorithm = algorithm.upper()

        if algorithm == "GREEN":
            return RPPGAlgorithms.algorithm_green(r, g, b)
        elif algorithm == "G-R":
            return RPPGAlgorithms.algorithm_g_minus_r(r, g, b)
        elif algorithm == "CHROM":
            return RPPGAlgorithms.algorithm_chrom(r, g, b)
        elif algorithm == "POS":
            return RPPGAlgorithms.algorithm_pos(r, g, b)
        elif algorithm == "ICA":
            return RPPGAlgorithms.algorithm_ica(r, g, b)
        else:
            print(f"⚠ 未知算法 '{algorithm}'，使用默认算法 POS")
            return RPPGAlgorithms.algorithm_pos(r, g, b)

    @staticmethod
    def get_available_algorithms() -> list:
        """获取可用算法列表"""
        return ["GREEN", "G-R", "CHROM", "POS", "ICA"]
