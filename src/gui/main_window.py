"""
AI-Exchange-Room 主窗口
实现三栏布局：侧边栏、中央区、底部面板
"""
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QTabWidget, QTreeWidget, QTreeWidgetItem,
    QTextEdit, QLabel, QPushButton, QStatusBar, QMenuBar,
    QMenu, QAction, QToolBar
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QFont
from pathlib import Path


class MainWindow(QMainWindow):
    """
    主窗口类
    参考VS Code的布局设计
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("AI-Exchange-Room - AI驱动的自动编程系统")
        self.setGeometry(100, 100, 1400, 900)

        # 初始化UI组件
        self._init_menubar()
        self._init_toolbar()
        self._init_central_widget()
        self._init_statusbar()

        # 应用样式
        self._apply_stylesheet()

    def _init_menubar(self):
        """初始化菜单栏"""
        menubar = self.menuBar()

        # 文件菜单
        file_menu = menubar.addMenu("文件(&F)")

        new_project = QAction("新建项目...", self)
        new_project.setShortcut("Ctrl+Shift+N")
        file_menu.addAction(new_project)

        open_project = QAction("打开项目...", self)
        open_project.setShortcut("Ctrl+O")
        file_menu.addAction(open_project)

        file_menu.addSeparator()

        exit_action = QAction("退出", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # 视图菜单
        view_menu = menubar.addMenu("视图(&V)")

        toggle_sidebar = QAction("切换侧边栏", self)
        toggle_sidebar.setShortcut("Ctrl+B")
        view_menu.addAction(toggle_sidebar)

        toggle_panel = QAction("切换底部面板", self)
        toggle_panel.setShortcut("Ctrl+J")
        view_menu.addAction(toggle_panel)

        # 项目菜单
        project_menu = menubar.addMenu("项目(&P)")

        analyze_req = QAction("需求分析...", self)
        analyze_req.setShortcut("Ctrl+Shift+A")
        project_menu.addAction(analyze_req)

        task_board = QAction("任务看板", self)
        task_board.setShortcut("Ctrl+Shift+T")
        project_menu.addAction(task_board)

        # 帮助菜单
        help_menu = menubar.addMenu("帮助(&H)")

        about = QAction("关于", self)
        help_menu.addAction(about)

    def _init_toolbar(self):
        """初始化工具栏"""
        toolbar = QToolBar("主工具栏")
        toolbar.setIconSize(QSize(24, 24))
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        # 添加工具栏按钮
        new_btn = QAction("新建", self)
        toolbar.addAction(new_btn)

        open_btn = QAction("打开", self)
        toolbar.addAction(open_btn)

        toolbar.addSeparator()

        analyze_btn = QAction("需求分析", self)
        toolbar.addAction(analyze_btn)

        tasks_btn = QAction("任务管理", self)
        toolbar.addAction(tasks_btn)

        monitor_btn = QAction("项目监控", self)
        toolbar.addAction(monitor_btn)

    def _init_central_widget(self):
        """初始化中央部件 - 三栏布局"""
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 主布局
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 创建主分割器（左右分割）
        main_splitter = QSplitter(Qt.Horizontal)

        # === 左侧边栏：项目浏览器 ===
        self.sidebar = self._create_sidebar()
        main_splitter.addWidget(self.sidebar)

        # === 右侧分割器（上下分割）===
        right_splitter = QSplitter(Qt.Vertical)

        # 中央区域：标签页
        self.central_tabs = self._create_central_tabs()
        right_splitter.addWidget(self.central_tabs)

        # 底部面板：AI对话、终端、输出
        self.bottom_panel = self._create_bottom_panel()
        right_splitter.addWidget(self.bottom_panel)

        # 设置初始比例（上70%，下30%）
        right_splitter.setSizes([700, 300])

        main_splitter.addWidget(right_splitter)

        # 设置初始比例（左20%，右80%）
        main_splitter.setSizes([250, 1150])

        main_layout.addWidget(main_splitter)

    def _create_sidebar(self) -> QWidget:
        """创建侧边栏 - 项目浏览器"""
        sidebar = QWidget()
        sidebar.setMinimumWidth(200)
        sidebar.setMaximumWidth(400)

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(5, 5, 5, 5)

        # 标题
        title = QLabel("📁 项目浏览器")
        title.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(title)

        # 项目树
        self.project_tree = QTreeWidget()
        self.project_tree.setHeaderLabel("项目列表")
        self.project_tree.setAlternatingRowColors(True)

        # 添加示例项目
        demo_item = QTreeWidgetItem(self.project_tree)
        demo_item.setText(0, "📦 AI-Exchange-Room")
        demo_item.setExpanded(True)

        # 子项目
        src_item = QTreeWidgetItem(demo_item)
        src_item.setText(0, "📂 src")

        core_item = QTreeWidgetItem(src_item)
        core_item.setText(0, "📂 core")

        gui_item = QTreeWidgetItem(src_item)
        gui_item.setText(0, "📂 gui")

        docs_item = QTreeWidgetItem(demo_item)
        docs_item.setText(0, "📂 docs")

        layout.addWidget(self.project_tree)

        return sidebar

    def _create_central_tabs(self) -> QTabWidget:
        """创建中央标签页区域"""
        tabs = QTabWidget()
        tabs.setTabsClosable(True)
        tabs.setMovable(True)
        tabs.setDocumentMode(True)

        # 欢迎页
        welcome_tab = self._create_welcome_tab()
        tabs.addTab(welcome_tab, "🏠 欢迎")

        # 禁止关闭欢迎页
        tabs.tabBar().setTabButton(0, tabs.tabBar().RightSide, None)

        return tabs

    def _create_welcome_tab(self) -> QWidget:
        """创建欢迎标签页"""
        welcome = QWidget()
        layout = QVBoxLayout(welcome)
        layout.setAlignment(Qt.AlignCenter)

        # 标题
        title = QLabel("🎯 AI-Exchange-Room")
        title_font = QFont("Arial", 24, QFont.Bold)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # 副标题
        subtitle = QLabel("AI驱动的自动编程系统")
        subtitle_font = QFont("Arial", 14)
        subtitle.setFont(subtitle_font)
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: #666;")
        layout.addWidget(subtitle)

        layout.addSpacing(30)

        # 快速开始按钮
        btn_layout = QVBoxLayout()
        btn_layout.setSpacing(10)

        new_project_btn = QPushButton("📝 新建项目")
        new_project_btn.setMinimumHeight(40)
        new_project_btn.setMaximumWidth(200)
        btn_layout.addWidget(new_project_btn, alignment=Qt.AlignCenter)

        open_project_btn = QPushButton("📂 打开项目")
        open_project_btn.setMinimumHeight(40)
        open_project_btn.setMaximumWidth(200)
        btn_layout.addWidget(open_project_btn, alignment=Qt.AlignCenter)

        demo_btn = QPushButton("🎨 查看演示")
        demo_btn.setMinimumHeight(40)
        demo_btn.setMaximumWidth(200)
        btn_layout.addWidget(demo_btn, alignment=Qt.AlignCenter)

        layout.addLayout(btn_layout)

        layout.addStretch()

        # 功能特性
        features = QLabel(
            "✨ 核心功能\n\n"
            "• 多角色AI需求分析\n"
            "• 智能任务分解\n"
            "• 自动化执行监控\n"
            "• 实时项目仪表板"
        )
        features.setStyleSheet("color: #555; font-size: 12px;")
        features.setAlignment(Qt.AlignCenter)
        layout.addWidget(features)

        return welcome

    def _create_bottom_panel(self) -> QTabWidget:
        """创建底部面板"""
        panel = QTabWidget()
        panel.setTabPosition(QTabWidget.South)
        panel.setMinimumHeight(150)

        # AI对话标签页
        ai_chat = QTextEdit()
        ai_chat.setReadOnly(True)
        ai_chat.setPlaceholderText("AI多角色讨论将在这里显示...")
        ai_chat.append("👤 产品经理: 准备开始需求分析...")
        ai_chat.append("🏗️ 架构师: 等待项目信息...")
        panel.addTab(ai_chat, "💬 AI对话")

        # 终端标签页
        terminal = QTextEdit()
        terminal.setReadOnly(True)
        terminal.setPlaceholderText("命令行输出...")
        terminal.setStyleSheet("background-color: #1e1e1e; color: #d4d4d4; font-family: 'Consolas', 'Monaco', monospace;")
        panel.addTab(terminal, "⌨️ 终端")

        # 输出标签页
        output = QTextEdit()
        output.setReadOnly(True)
        output.setPlaceholderText("系统输出日志...")
        panel.addTab(output, "📋 输出")

        # 任务详情标签页
        task_detail = QTextEdit()
        task_detail.setReadOnly(True)
        task_detail.setPlaceholderText("任务详细信息...")
        panel.addTab(task_detail, "📝 任务详情")

        return panel

    def _init_statusbar(self):
        """初始化状态栏"""
        statusbar = QStatusBar()
        self.setStatusBar(statusbar)

        # 左侧状态信息
        self.status_label = QLabel("就绪")
        statusbar.addWidget(self.status_label)

        # 右侧信息
        statusbar.addPermanentWidget(QLabel("项目: 无"))
        statusbar.addPermanentWidget(QLabel("AI角色: 6个"))
        statusbar.addPermanentWidget(QLabel("任务: 0"))

    def _apply_stylesheet(self):
        """应用亮色主题样式表"""
        # 内联样式表 - 亮色主题（参考VS Code Light）
        stylesheet = """
            /* 主窗口 */
            QMainWindow {
                background-color: #f3f3f3;
            }

            /* 菜单栏 */
            QMenuBar {
                background-color: #f3f3f3;
                border-bottom: 1px solid #e0e0e0;
                padding: 4px;
            }

            QMenuBar::item {
                background-color: transparent;
                padding: 4px 8px;
            }

            QMenuBar::item:selected {
                background-color: #e0e0e0;
            }

            QMenu {
                background-color: #ffffff;
                border: 1px solid #d0d0d0;
            }

            QMenu::item:selected {
                background-color: #e0e0e0;
            }

            /* 工具栏 */
            QToolBar {
                background-color: #f3f3f3;
                border-bottom: 1px solid #e0e0e0;
                spacing: 3px;
                padding: 3px;
            }

            QToolButton {
                background-color: transparent;
                border: 1px solid transparent;
                border-radius: 3px;
                padding: 5px;
            }

            QToolButton:hover {
                background-color: #e0e0e0;
                border: 1px solid #d0d0d0;
            }

            /* 标签页 */
            QTabWidget::pane {
                border: 1px solid #d0d0d0;
                background-color: #ffffff;
            }

            QTabBar::tab {
                background-color: #e8e8e8;
                border: 1px solid #d0d0d0;
                border-bottom: none;
                padding: 8px 16px;
                margin-right: 2px;
            }

            QTabBar::tab:selected {
                background-color: #ffffff;
                border-bottom: 2px solid #007acc;
            }

            QTabBar::tab:hover:!selected {
                background-color: #f0f0f0;
            }

            /* 树形控件 */
            QTreeWidget {
                background-color: #ffffff;
                border: 1px solid #d0d0d0;
                alternate-background-color: #f9f9f9;
            }

            QTreeWidget::item:hover {
                background-color: #e8e8e8;
            }

            QTreeWidget::item:selected {
                background-color: #cce8ff;
                color: #000000;
            }

            /* 文本编辑器 */
            QTextEdit {
                background-color: #ffffff;
                border: 1px solid #d0d0d0;
                color: #000000;
            }

            /* 按钮 */
            QPushButton {
                background-color: #007acc;
                color: #ffffff;
                border: none;
                border-radius: 3px;
                padding: 8px 16px;
                font-weight: bold;
            }

            QPushButton:hover {
                background-color: #005a9e;
            }

            QPushButton:pressed {
                background-color: #004578;
            }

            /* 状态栏 */
            QStatusBar {
                background-color: #007acc;
                color: #ffffff;
            }

            QStatusBar QLabel {
                color: #ffffff;
                padding: 0 10px;
            }

            /* 分割器 */
            QSplitter::handle {
                background-color: #e0e0e0;
            }

            QSplitter::handle:horizontal {
                width: 1px;
            }

            QSplitter::handle:vertical {
                height: 1px;
            }
        """

        self.setStyleSheet(stylesheet)

    def add_central_tab(self, widget: QWidget, title: str, closable: bool = True):
        """添加中央标签页"""
        index = self.central_tabs.addTab(widget, title)
        if not closable:
            self.central_tabs.tabBar().setTabButton(
                index,
                self.central_tabs.tabBar().RightSide,
                None
            )
        self.central_tabs.setCurrentIndex(index)
        return index

    def log_ai_message(self, role: str, message: str):
        """在AI对话面板中记录消息"""
        ai_chat = self.bottom_panel.widget(0)
        if isinstance(ai_chat, QTextEdit):
            ai_chat.append(f"{role}: {message}")

    def log_output(self, message: str):
        """在输出面板中记录日志"""
        output = self.bottom_panel.widget(2)
        if isinstance(output, QTextEdit):
            output.append(message)

    def update_status(self, message: str):
        """更新状态栏消息"""
        self.status_label.setText(message)
