"""
插件接口定义
所有插件必须实现此接口
"""
from abc import ABC, abstractmethod
from PyQt5.QtWidgets import QWidget
from typing import Optional, Dict, Any


class PluginInterface(ABC):
    """插件接口基类"""

    @abstractmethod
    def get_name(self) -> str:
        """
        获取插件名称

        Returns:
            str: 插件名称，显示在工具箱中
        """
        pass

    @abstractmethod
    def get_description(self) -> str:
        """
        获取插件描述

        Returns:
            str: 插件的简短描述
        """
        pass

    @abstractmethod
    def get_version(self) -> str:
        """
        获取插件版本

        Returns:
            str: 版本号，如 "1.0.0"
        """
        pass

    @abstractmethod
    def get_icon(self) -> Optional[str]:
        """
        获取插件图标路径

        Returns:
            Optional[str]: 图标文件路径，可以为None
        """
        pass

    @abstractmethod
    def get_category(self) -> str:
        """
        获取插件分类

        Returns:
            str: 分类名称，如 "开发工具"、"效率工具"等
        """
        pass

    @abstractmethod
    def get_widget(self) -> QWidget:
        """
        获取插件的GUI组件

        Returns:
            QWidget: 插件的主界面组件
        """
        pass

    def get_metadata(self) -> Dict[str, Any]:
        """
        获取插件元数据（可选）

        Returns:
            Dict[str, Any]: 额外的元数据信息
        """
        return {
            "name": self.get_name(),
            "description": self.get_description(),
            "version": self.get_version(),
            "category": self.get_category(),
        }

    def on_activate(self):
        """
        插件激活时调用（可选实现）
        """
        pass

    def on_deactivate(self):
        """
        插件停用时调用（可选实现）
        """
        pass

    def get_settings_widget(self) -> Optional[QWidget]:
        """
        获取插件设置界面（可选）

        Returns:
            Optional[QWidget]: 设置界面组件，可以为None
        """
        return None
