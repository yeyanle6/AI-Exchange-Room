"""
插件模板
复制此文件并修改以创建新插件
"""
import sys
from pathlib import Path
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from typing import Optional

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.toolbox.core.plugin_interface import PluginInterface


class MyToolWidget(QWidget):
    """工具的主界面组件"""

    def __init__(self):
        super().__init__()
        self._init_ui()

    def _init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout(self)

        # 添加标题
        title = QLabel("我的工具")
        title.setStyleSheet("font-size: 24px; font-weight: bold; margin: 20px;")
        layout.addWidget(title)

        # 添加按钮
        button = QPushButton("点击我")
        button.clicked.connect(self._on_button_click)
        layout.addWidget(button)

        layout.addStretch()

    def _on_button_click(self):
        """按钮点击事件"""
        print("按钮被点击了！")


class MyToolPlugin(PluginInterface):
    """
    我的工具插件

    修改这个类的实现来创建你自己的插件
    """

    def __init__(self):
        self._widget = None

    def get_name(self) -> str:
        """插件名称"""
        return "我的工具"

    def get_description(self) -> str:
        """插件描述"""
        return "这是一个示例插件，展示如何创建新工具"

    def get_version(self) -> str:
        """版本号"""
        return "1.0.0"

    def get_icon(self) -> Optional[str]:
        """图标路径（可选）"""
        return None

    def get_category(self) -> str:
        """分类"""
        return "示例工具"

    def get_widget(self) -> QWidget:
        """返回工具的GUI组件"""
        if self._widget is None:
            self._widget = MyToolWidget()
        return self._widget

    def on_activate(self):
        """插件激活时调用"""
        print(f"{self.get_name()} 已激活")

    def on_deactivate(self):
        """插件停用时调用"""
        print(f"{self.get_name()} 已停用")
        if self._widget is not None:
            self._widget = None
