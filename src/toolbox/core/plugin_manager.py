"""
插件管理器
负责发现、加载和管理所有插件
"""
import os
import sys
import importlib.util
from pathlib import Path
from typing import List, Dict, Optional
from .plugin_interface import PluginInterface


class PluginManager:
    """插件管理器"""

    def __init__(self, plugins_dir: str = "plugins"):
        """
        初始化插件管理器

        Args:
            plugins_dir: 插件目录路径
        """
        self.plugins_dir = Path(plugins_dir)
        self.plugins: Dict[str, PluginInterface] = {}
        self._ensure_plugins_dir()

    def _ensure_plugins_dir(self):
        """确保插件目录存在"""
        if not self.plugins_dir.exists():
            self.plugins_dir.mkdir(parents=True, exist_ok=True)
            print(f"创建插件目录: {self.plugins_dir}")

    def discover_plugins(self) -> List[str]:
        """
        发现所有可用插件

        Returns:
            List[str]: 插件ID列表
        """
        discovered = []

        if not self.plugins_dir.exists():
            return discovered

        # 遍历插件目录
        for item in self.plugins_dir.iterdir():
            if not item.is_dir():
                continue

            # 跳过特殊目录
            if item.name.startswith(('_', '.')):
                continue

            # 查找plugin.py文件
            plugin_file = item / "plugin.py"
            if plugin_file.exists():
                discovered.append(item.name)
                print(f"发现插件: {item.name}")

        return discovered

    def load_plugin(self, plugin_id: str) -> Optional[PluginInterface]:
        """
        加载指定插件

        Args:
            plugin_id: 插件ID（目录名）

        Returns:
            Optional[PluginInterface]: 插件实例，失败返回None
        """
        try:
            plugin_dir = self.plugins_dir / plugin_id
            plugin_file = plugin_dir / "plugin.py"

            if not plugin_file.exists():
                print(f"插件文件不存在: {plugin_file}")
                return None

            # 动态加载模块
            spec = importlib.util.spec_from_file_location(
                f"plugins.{plugin_id}.plugin",
                plugin_file
            )
            module = importlib.util.module_from_spec(spec)
            sys.modules[spec.name] = module
            spec.loader.exec_module(module)

            # 查找PluginInterface的实现类
            plugin_class = None
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (isinstance(attr, type) and
                    issubclass(attr, PluginInterface) and
                    attr is not PluginInterface):
                    plugin_class = attr
                    break

            if plugin_class is None:
                print(f"插件 {plugin_id} 中未找到PluginInterface实现")
                return None

            # 实例化插件
            plugin = plugin_class()
            self.plugins[plugin_id] = plugin

            print(f"✓ 加载插件成功: {plugin.get_name()} v{plugin.get_version()}")
            return plugin

        except Exception as e:
            print(f"✗ 加载插件失败 {plugin_id}: {e}")
            import traceback
            traceback.print_exc()
            return None

    def load_all_plugins(self) -> int:
        """
        加载所有插件

        Returns:
            int: 成功加载的插件数量
        """
        plugin_ids = self.discover_plugins()
        loaded_count = 0

        for plugin_id in plugin_ids:
            if self.load_plugin(plugin_id):
                loaded_count += 1

        print(f"\n插件加载完成: {loaded_count}/{len(plugin_ids)}")
        return loaded_count

    def get_plugin(self, plugin_id: str) -> Optional[PluginInterface]:
        """
        获取已加载的插件

        Args:
            plugin_id: 插件ID

        Returns:
            Optional[PluginInterface]: 插件实例，未找到返回None
        """
        return self.plugins.get(plugin_id)

    def get_all_plugins(self) -> List[PluginInterface]:
        """
        获取所有已加载的插件

        Returns:
            List[PluginInterface]: 插件实例列表
        """
        return list(self.plugins.values())

    def get_plugins_by_category(self, category: str) -> List[PluginInterface]:
        """
        按分类获取插件

        Args:
            category: 分类名称

        Returns:
            List[PluginInterface]: 该分类下的插件列表
        """
        return [
            plugin for plugin in self.plugins.values()
            if plugin.get_category() == category
        ]

    def get_categories(self) -> List[str]:
        """
        获取所有插件分类

        Returns:
            List[str]: 分类列表
        """
        categories = set()
        for plugin in self.plugins.values():
            categories.add(plugin.get_category())
        return sorted(list(categories))

    def unload_plugin(self, plugin_id: str) -> bool:
        """
        卸载插件

        Args:
            plugin_id: 插件ID

        Returns:
            bool: 是否成功
        """
        if plugin_id in self.plugins:
            plugin = self.plugins[plugin_id]
            try:
                plugin.on_deactivate()
                del self.plugins[plugin_id]
                print(f"卸载插件: {plugin.get_name()}")
                return True
            except Exception as e:
                print(f"卸载插件失败: {e}")
                return False
        return False

    def reload_plugin(self, plugin_id: str) -> Optional[PluginInterface]:
        """
        重新加载插件

        Args:
            plugin_id: 插件ID

        Returns:
            Optional[PluginInterface]: 重新加载的插件实例
        """
        self.unload_plugin(plugin_id)
        return self.load_plugin(plugin_id)
