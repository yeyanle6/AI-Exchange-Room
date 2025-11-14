"""
AI ToolBox 主窗口
插件化工具箱的主界面
"""
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QListWidget, QListWidgetItem, QStackedWidget,
    QLabel, QPushButton, QFrame, QScrollArea,
    QAction, QMenu, QMenuBar, QStatusBar, QToolBar,
    QSplitter, QGroupBox, QGridLayout
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QIcon, QPixmap, QColor
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.toolbox.core.plugin_manager import PluginManager
from src.toolbox.core.plugin_interface import PluginInterface


class PluginCard(QFrame):
    """插件卡片"""

    def __init__(self, plugin: PluginInterface, parent=None):
        super().__init__(parent)
        self.plugin = plugin
        self._init_ui()

    def _init_ui(self):
        """初始化UI"""
        self.setFrameShape(QFrame.Box)
        self.setFrameShadow(QFrame.Raised)
        self.setMinimumHeight(120)
        self.setMaximumHeight(150)
        self.setCursor(Qt.PointingHandCursor)

        # 设置样式
        self.setStyleSheet("""
            PluginCard {
                background-color: white;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                padding: 15px;
            }
            PluginCard:hover {
                border: 2px solid #007acc;
                background-color: #f8f8f8;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        # 标题行
        title_layout = QHBoxLayout()

        # 图标
        icon_label = QLabel("🔧")
        icon_label.setFont(QFont("Arial", 24))
        title_layout.addWidget(icon_label)

        # 名称和版本
        name_label = QLabel(self.plugin.get_name())
        name_font = QFont("Arial", 14, QFont.Bold)
        name_label.setFont(name_font)
        title_layout.addWidget(name_label)

        version_label = QLabel(f"v{self.plugin.get_version()}")
        version_label.setStyleSheet("color: #666; font-size: 10px;")
        title_layout.addWidget(version_label)

        title_layout.addStretch()
        layout.addLayout(title_layout)

        # 描述
        desc_label = QLabel(self.plugin.get_description())
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: #555; font-size: 11px;")
        desc_label.setMaximumHeight(40)
        layout.addWidget(desc_label)

        # 分类标签
        category_label = QLabel(f"📂 {self.plugin.get_category()}")
        category_label.setStyleSheet("""
            color: #007acc;
            font-size: 10px;
            background-color: #e6f3ff;
            border-radius: 3px;
            padding: 3px 8px;
        """)
        category_label.setMaximumWidth(150)
        layout.addWidget(category_label)

        layout.addStretch()


class ToolBoxMainWindow(QMainWindow):
    """工具箱主窗口"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("🧰 AI ToolBox - AI驱动的智能工具箱")
        self.setGeometry(100, 100, 1400, 900)

        # 初始化插件管理器
        self.plugin_manager = PluginManager()

        # 初始化UI
        self._init_menubar()
        self._init_toolbar()
        self._init_central_widget()
        self._init_statusbar()

        # 应用样式
        self._apply_stylesheet()

        # 加载插件
        self._load_plugins()

    def _init_menubar(self):
        """初始化菜单栏"""
        menubar = self.menuBar()

        # 文件菜单
        file_menu = menubar.addMenu("文件(&F)")

        refresh_action = QAction("刷新插件", self)
        refresh_action.setShortcut("F5")
        refresh_action.triggered.connect(self._reload_plugins)
        file_menu.addAction(refresh_action)

        file_menu.addSeparator()

        exit_action = QAction("退出", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # 查看菜单
        view_menu = menubar.addMenu("查看(&V)")

        home_action = QAction("工具箱首页", self)
        home_action.setShortcut("Ctrl+H")
        home_action.triggered.connect(self._show_home)
        view_menu.addAction(home_action)

        # 帮助菜单
        help_menu = menubar.addMenu("帮助(&H)")

        about_action = QAction("关于", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

    def _init_toolbar(self):
        """初始化工具栏"""
        toolbar = QToolBar("主工具栏")
        toolbar.setIconSize(QSize(24, 24))
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        # 首页按钮
        home_btn = QAction("🏠 首页", self)
        home_btn.triggered.connect(self._show_home)
        toolbar.addAction(home_btn)

        toolbar.addSeparator()

        # 刷新按钮
        refresh_btn = QAction("🔄 刷新", self)
        refresh_btn.triggered.connect(self._reload_plugins)
        toolbar.addAction(refresh_btn)

    def _init_central_widget(self):
        """初始化中央部件"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)

        # 堆叠窗口（首页 + 插件页面）
        self.stacked_widget = QStackedWidget()

        # 创建首页
        home_page = self._create_home_page()
        self.stacked_widget.addWidget(home_page)

        layout.addWidget(self.stacked_widget)

    def _create_home_page(self) -> QWidget:
        """创建首页"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(20, 20, 20, 20)

        # 欢迎标题
        welcome_label = QLabel("🧰 AI ToolBox")
        welcome_font = QFont("Arial", 28, QFont.Bold)
        welcome_label.setFont(welcome_font)
        welcome_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(welcome_label)

        subtitle = QLabel("AI驱动的智能工具箱 - 让AI为你工作")
        subtitle_font = QFont("Arial", 14)
        subtitle.setFont(subtitle_font)
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: #666; margin-bottom: 20px;")
        layout.addWidget(subtitle)

        layout.addSpacing(20)

        # 插件网格
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        scroll_content = QWidget()
        self.plugins_grid = QGridLayout(scroll_content)
        self.plugins_grid.setSpacing(20)
        self.plugins_grid.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)

        # 统计信息
        stats_label = QLabel()
        stats_label.setAlignment(Qt.AlignCenter)
        stats_label.setStyleSheet("color: #888; font-size: 11px; margin-top: 10px;")
        self.stats_label = stats_label
        layout.addWidget(stats_label)

        return page

    def _load_plugins(self):
        """加载所有插件"""
        print("\n" + "="*60)
        print("🔍 开始加载插件...")
        print("="*60)

        # 加载插件
        count = self.plugin_manager.load_all_plugins()

        # 更新界面
        self._update_plugin_grid()
        self._update_stats(count)

    def _update_plugin_grid(self):
        """更新插件网格"""
        # 清空现有内容
        while self.plugins_grid.count():
            item = self.plugins_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # 添加插件卡片
        plugins = self.plugin_manager.get_all_plugins()
        row, col = 0, 0
        max_cols = 3

        for plugin in plugins:
            card = PluginCard(plugin)
            card.mousePressEvent = lambda e, p=plugin: self._open_plugin(p)
            self.plugins_grid.addWidget(card, row, col)

            col += 1
            if col >= max_cols:
                col = 0
                row += 1

    def _update_stats(self, count: int):
        """更新统计信息"""
        categories = self.plugin_manager.get_categories()
        stats_text = f"已加载 {count} 个插件 | {len(categories)} 个分类"
        self.stats_label.setText(stats_text)

    def _open_plugin(self, plugin: PluginInterface):
        """打开插件"""
        try:
            # 激活插件
            plugin.on_activate()

            # 获取插件widget
            plugin_widget = plugin.get_widget()

            # 添加到堆叠窗口
            self.stacked_widget.addWidget(plugin_widget)
            self.stacked_widget.setCurrentWidget(plugin_widget)

            # 更新状态栏
            self.statusBar().showMessage(f"已打开: {plugin.get_name()}")

        except Exception as e:
            print(f"打开插件失败: {e}")
            import traceback
            traceback.print_exc()

    def _show_home(self):
        """显示首页"""
        self.stacked_widget.setCurrentIndex(0)
        self.statusBar().showMessage("工具箱首页")

    def _reload_plugins(self):
        """重新加载插件"""
        print("\n🔄 重新加载插件...")
        self.plugin_manager = PluginManager()
        self._load_plugins()
        self._show_home()

    def _show_about(self):
        """显示关于信息"""
        from PyQt5.QtWidgets import QMessageBox
        QMessageBox.about(
            self,
            "关于 AI ToolBox",
            "🧰 AI ToolBox v1.0.0\n\n"
            "AI驱动的智能工具箱\n"
            "让AI为你工作，提升效率\n\n"
            "Powered by Claude Code"
        )

    def _init_statusbar(self):
        """初始化状态栏"""
        statusbar = QStatusBar()
        self.setStatusBar(statusbar)
        statusbar.showMessage("就绪")

    def _apply_stylesheet(self):
        """应用样式表"""
        stylesheet = """
            QMainWindow {
                background-color: #f5f5f5;
            }

            QMenuBar {
                background-color: #f5f5f5;
                border-bottom: 1px solid #e0e0e0;
            }

            QMenuBar::item:selected {
                background-color: #e0e0e0;
            }

            QToolBar {
                background-color: #f5f5f5;
                border-bottom: 1px solid #e0e0e0;
                spacing: 5px;
                padding: 5px;
            }

            QStatusBar {
                background-color: #007acc;
                color: white;
            }

            QPushButton {
                background-color: #007acc;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }

            QPushButton:hover {
                background-color: #005a9e;
            }
        """
        self.setStyleSheet(stylesheet)
