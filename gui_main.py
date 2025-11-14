#!/usr/bin/env python3
"""
AI-Exchange-Room GUI主程序
启动图形界面版本
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QFont
from src.gui.main_window import MainWindow
from src.utils import app_logger


def main():
    """主函数"""
    app_logger.info("启动 AI-Exchange-Room GUI...")

    # 创建应用程序
    app = QApplication(sys.argv)
    app.setApplicationName("AI-Exchange-Room")
    app.setOrganizationName("AI-Exchange-Room")

    # 设置全局字体
    font = QFont("Arial", 10)
    app.setFont(font)

    # 创建并显示主窗口
    window = MainWindow()
    window.show()

    app_logger.info("GUI界面已启动")
    window.update_status("就绪 - 欢迎使用 AI-Exchange-Room")

    # 运行应用程序
    sys.exit(app.exec_())


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        app_logger.info("用户中断程序")
    except Exception as e:
        app_logger.error(f"程序异常退出: {e}")
        import traceback
        traceback.print_exc()
