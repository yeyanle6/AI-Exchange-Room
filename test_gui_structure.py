#!/usr/bin/env python3
"""
测试GUI代码结构
不需要显示器，仅测试代码导入和结构
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """测试模块导入"""
    print("测试1: 导入GUI模块...")
    try:
        from src.gui import MainWindow
        print("  ✓ MainWindow 导入成功")
    except Exception as e:
        print(f"  ✗ 导入失败: {e}")
        return False

    print("\n测试2: 导入PyQt5组件...")
    try:
        from PyQt5.QtWidgets import QApplication, QMainWindow
        from PyQt5.QtCore import Qt
        print("  ✓ PyQt5 组件导入成功")
    except Exception as e:
        print(f"  ✗ 导入失败: {e}")
        return False

    return True


def test_structure():
    """测试类结构"""
    print("\n测试3: 检查MainWindow类结构...")
    try:
        from src.gui.main_window import MainWindow

        # 检查必需的方法
        required_methods = [
            '_init_menubar',
            '_init_toolbar',
            '_init_central_widget',
            '_init_statusbar',
            '_create_sidebar',
            '_create_central_tabs',
            '_create_bottom_panel',
            '_apply_stylesheet',
            'add_central_tab',
            'log_ai_message',
            'log_output',
            'update_status'
        ]

        for method in required_methods:
            if hasattr(MainWindow, method):
                print(f"  ✓ 方法 {method} 存在")
            else:
                print(f"  ✗ 方法 {method} 不存在")
                return False

    except Exception as e:
        print(f"  ✗ 结构测试失败: {e}")
        return False

    return True


def test_file_structure():
    """测试文件结构"""
    print("\n测试4: 检查文件结构...")

    required_files = [
        "src/gui/__init__.py",
        "src/gui/main_window.py",
        "src/gui/widgets/__init__.py",
        "src/gui/styles/light_theme.qss",
        "gui_main.py"
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


def test_stylesheet():
    """测试样式表文件"""
    print("\n测试5: 检查样式表...")
    try:
        stylesheet_path = Path(__file__).parent / "src/gui/styles/light_theme.qss"
        content = stylesheet_path.read_text()

        # 检查关键样式
        key_styles = ["QMainWindow", "QMenuBar", "QTabWidget", "QTreeWidget", "QPushButton"]
        for style in key_styles:
            if style in content:
                print(f"  ✓ {style} 样式已定义")
            else:
                print(f"  ✗ {style} 样式缺失")
                return False

    except Exception as e:
        print(f"  ✗ 样式表测试失败: {e}")
        return False

    return True


def main():
    """运行所有测试"""
    print("=" * 70)
    print("GUI代码结构测试")
    print("=" * 70)

    tests = [
        ("模块导入", test_imports),
        ("类结构", test_structure),
        ("文件结构", test_file_structure),
        ("样式表", test_stylesheet)
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
        print("\n🎉 所有测试通过！GUI框架已准备就绪。")
        print("\n注意: 在有显示器的环境中运行以下命令启动GUI:")
        print("  python gui_main.py")
    else:
        print("\n⚠️ 部分测试失败，请检查错误信息。")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
