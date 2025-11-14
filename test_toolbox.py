#!/usr/bin/env python3
"""
测试工具箱系统
"""
import sys
import os
from pathlib import Path

# 设置为offscreen模式（无需显示器）
os.environ['QT_QPA_PLATFORM'] = 'offscreen'

sys.path.insert(0, str(Path(__file__).parent))


def test_plugin_manager():
    """测试插件管理器"""
    print("\n测试1: 插件管理器...")
    try:
        from src.toolbox.core.plugin_manager import PluginManager

        manager = PluginManager()
        print("  ✓ PluginManager 创建成功")

        # 发现插件
        plugins = manager.discover_plugins()
        print(f"  ✓ 发现插件: {plugins}")

        # 加载插件
        count = manager.load_all_plugins()
        print(f"  ✓ 加载插件: {count}个")

        return True
    except Exception as e:
        print(f"  ✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_plugin_interface():
    """测试插件接口"""
    print("\n测试2: 插件接口...")
    try:
        from src.toolbox.core.plugin_interface import PluginInterface
        from plugins.template.plugin import MyToolPlugin

        plugin = MyToolPlugin()
        print(f"  ✓ 插件名称: {plugin.get_name()}")
        print(f"  ✓ 插件版本: {plugin.get_version()}")
        print(f"  ✓ 插件分类: {plugin.get_category()}")
        print(f"  ✓ 插件描述: {plugin.get_description()}")

        return True
    except Exception as e:
        print(f"  ✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_ai_exchange_room_plugin():
    """测试AI-Exchange-Room插件"""
    print("\n测试3: AI-Exchange-Room 插件...")
    try:
        from PyQt5.QtWidgets import QApplication
        from src.toolbox.core.plugin_manager import PluginManager

        if not QApplication.instance():
            app = QApplication(sys.argv)

        # 使用插件管理器加载插件
        manager = PluginManager()
        manager.discover_plugins()
        plugin = manager.load_plugin("ai-exchange-room")

        if plugin is None:
            print(f"  ✗ 无法加载AI-Exchange-Room插件")
            return False

        print(f"  ✓ 插件名称: {plugin.get_name()}")
        print(f"  ✓ 插件版本: {plugin.get_version()}")
        print(f"  ✓ 插件分类: {plugin.get_category()}")

        # 测试获取widget
        widget = plugin.get_widget()
        print(f"  ✓ Widget 创建成功: {type(widget).__name__}")

        return True
    except Exception as e:
        print(f"  ✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_toolbox_window():
    """测试工具箱主窗口"""
    print("\n测试4: 工具箱主窗口...")
    try:
        from PyQt5.QtWidgets import QApplication
        from src.toolbox.gui.main_window import ToolBoxMainWindow

        if not QApplication.instance():
            app = QApplication(sys.argv)

        window = ToolBoxMainWindow()
        print("  ✓ 主窗口创建成功")

        # 检查插件数量
        plugins_count = len(window.plugin_manager.get_all_plugins())
        print(f"  ✓ 已加载插件: {plugins_count}个")

        return True
    except Exception as e:
        print(f"  ✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_file_structure():
    """测试文件结构"""
    print("\n测试5: 文件结构...")

    required_files = [
        "toolbox_main.py",
        "src/toolbox/__init__.py",
        "src/toolbox/core/plugin_interface.py",
        "src/toolbox/core/plugin_manager.py",
        "src/toolbox/gui/main_window.py",
        "plugins/ai-exchange-room/plugin.py",
        "plugins/template/plugin.py",
        "TOOLBOX_README.md"
    ]

    base_path = Path(__file__).parent
    all_exist = True

    for file_path in required_files:
        full_path = base_path / file_path
        if full_path.exists():
            print(f"  ✓ {file_path}")
        else:
            print(f"  ✗ {file_path} 不存在")
            all_exist = False

    return all_exist


def main():
    """运行所有测试"""
    print("=" * 70)
    print("AI ToolBox 系统测试")
    print("=" * 70)

    tests = [
        ("插件管理器", test_plugin_manager),
        ("插件接口", test_plugin_interface),
        ("AI-Exchange-Room插件", test_ai_exchange_room_plugin),
        ("工具箱主窗口", test_toolbox_window),
        ("文件结构", test_file_structure)
    ]

    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n✗ 测试 '{name}' 异常: {e}")
            results.append((name, False))

    print("\n" + "=" * 70)
    print("测试总结")
    print("=" * 70)

    for name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{name}: {status}")

    all_passed = all(result for _, result in results)

    if all_passed:
        print("\n" + "=" * 70)
        print("🎉 所有测试通过！工具箱系统已准备就绪。")
        print("=" * 70)
        print("\n启动工具箱:")
        print("  python toolbox_main.py")
        print("\n功能特性:")
        print("  ✅ 插件化架构")
        print("  ✅ 自动插件发现和加载")
        print("  ✅ AI-Exchange-Room 已集成")
        print("  ✅ 插件模板可用")
    else:
        print("\n⚠️ 部分测试失败，请检查错误信息。")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
