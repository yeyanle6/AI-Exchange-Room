#!/usr/bin/env python3
"""
AI ToolBox 主程序
插件化AI工具箱的启动入口
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QFont
from src.toolbox.gui.main_window import ToolBoxMainWindow


def main():
    """主函数"""
    print("=" * 70)
    print("🧰 AI ToolBox - AI驱动的智能工具箱")
    print("=" * 70)

    # 创建应用程序
    app = QApplication(sys.argv)
    app.setApplicationName("AI ToolBox")
    app.setOrganizationName("AI ToolBox")

    # 设置全局字体
    font = QFont("Arial", 10)
    app.setFont(font)

    # 创建并显示主窗口
    window = ToolBoxMainWindow()
    window.show()

    print("\n✨ 工具箱已启动！")
    print("=" * 70)

    # 运行应用程序
    sys.exit(app.exec_())


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n用户中断程序")
    except Exception as e:
        print(f"\n\n程序异常退出: {e}")
        import traceback
        traceback.print_exc()
