"""
AI-Exchange-Room 插件
AI驱动的自动编程系统
"""
import sys
from pathlib import Path
from PyQt5.QtWidgets import QWidget
from typing import Optional

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.toolbox.core.plugin_interface import PluginInterface
from src.gui.main_window import MainWindow as AIExchangeMainWindow


class AIExchangeRoomPlugin(PluginInterface):
    """AI-Exchange-Room 插件类"""

    def __init__(self):
        self._widget = None

    def get_name(self) -> str:
        return "AI-Exchange-Room"

    def get_description(self) -> str:
        return "AI驱动的自动编程系统 - 多角色需求分析、智能任务分解、项目管理"

    def get_version(self) -> str:
        return "1.0.1"

    def get_icon(self) -> Optional[str]:
        # 可以返回图标路径
        return None

    def get_category(self) -> str:
        return "开发工具"

    def get_widget(self) -> QWidget:
        """
        返回AI-Exchange-Room的主窗口作为widget

        注意: 这里我们创建一个包装器，将MainWindow的核心功能
        嵌入到一个普通widget中
        """
        if self._widget is None:
            # 创建包装器widget
            from PyQt5.QtWidgets import QVBoxLayout, QWidget as QW

            wrapper = QW()
            layout = QVBoxLayout(wrapper)
            layout.setContentsMargins(0, 0, 0, 0)

            # 创建AI-Exchange-Room的主窗口内容
            # 由于MainWindow是QMainWindow，我们需要提取其中央部件
            ai_window = AIExchangeMainWindow()
            central_widget = ai_window.centralWidget()

            # 从原窗口中移除central_widget（避免父子关系冲突）
            ai_window.setCentralWidget(QW())

            # 添加到包装器
            layout.addWidget(central_widget)

            # 保持对ai_window的引用，防止被垃圾回收
            wrapper._ai_window = ai_window

            self._widget = wrapper

        return self._widget

    def on_activate(self):
        """插件激活时调用"""
        print("AI-Exchange-Room 插件已激活")

    def on_deactivate(self):
        """插件停用时调用"""
        print("AI-Exchange-Room 插件已停用")
        if self._widget is not None:
            # 清理资源
            self._widget = None
