"""
rPPG心率检测插件
基于MediaPipe Face Mesh (468特征点) 的非接触式心率检测
"""

import sys
import os

# 添加插件目录到Python路径
plugin_dir = os.path.dirname(os.path.abspath(__file__))
if plugin_dir not in sys.path:
    sys.path.insert(0, plugin_dir)

from PyQt5.QtWidgets import QWidget
from gui.main_widget import RPPGMainWidget

# 导入插件接口
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
from toolbox.core.plugin_interface import PluginInterface


class RPPGDetectorPlugin(PluginInterface):
    """
    rPPG心率检测插件
    """

    def get_name(self) -> str:
        return "rPPG心率检测"

    def get_version(self) -> str:
        return "1.0.0"

    def get_description(self) -> str:
        return "基于MediaPipe Face Mesh的非接触式心率检测，支持多种rPPG算法"

    def get_category(self) -> str:
        return "健康监测"

    def get_icon(self) -> str:
        return "❤️"

    def get_widget(self) -> QWidget:
        """返回主界面widget"""
        return RPPGMainWidget()

    def on_activate(self) -> None:
        """插件激活时调用"""
        print("✓ rPPG心率检测插件已激活")

    def on_deactivate(self) -> None:
        """插件停用时调用"""
        print("✓ rPPG心率检测插件已停用")
