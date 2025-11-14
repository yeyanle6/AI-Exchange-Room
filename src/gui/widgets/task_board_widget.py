"""
任务看板界面组件
实现看板式任务管理（待办、进行中、已完成）
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QScrollArea, QFrame, QLineEdit,
    QTextEdit, QGroupBox, QListWidget, QListWidgetItem,
    QSplitter, QComboBox
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QColor, QPalette
from typing import List, Dict
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))


class TaskCard(QFrame):
    """任务卡片"""

    clicked = pyqtSignal(object)  # 任务被点击

    def __init__(self, task_id: str, title: str, description: str = "", priority: str = "medium"):
        super().__init__()
        self.task_id = task_id
        self.title = title
        self.description = description
        self.priority = priority

        self._init_ui()

    def _init_ui(self):
        """初始化UI"""
        self.setFrameShape(QFrame.Box)
        self.setFrameShadow(QFrame.Raised)
        self.setLineWidth(1)
        self.setMaximumHeight(120)
        self.setMinimumHeight(80)
        self.setCursor(Qt.PointingHandCursor)

        # 设置背景色
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor("#ffffff"))
        self.setPalette(palette)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(5)

        # 标题
        title_label = QLabel(self.title)
        title_font = QFont("Arial", 10, QFont.Bold)
        title_label.setFont(title_font)
        title_label.setWordWrap(True)
        layout.addWidget(title_label)

        # 描述
        if self.description:
            desc_label = QLabel(self.description[:60] + "..." if len(self.description) > 60 else self.description)
            desc_label.setStyleSheet("color: #666; font-size: 9px;")
            desc_label.setWordWrap(True)
            layout.addWidget(desc_label)

        # 优先级标签
        priority_colors = {
            "high": "#d32f2f",
            "medium": "#f57c00",
            "low": "#388e3c"
        }
        priority_label = QLabel(f"优先级: {self.priority.upper()}")
        priority_label.setStyleSheet(f"color: {priority_colors.get(self.priority, '#666')}; font-size: 8px; font-weight: bold;")
        layout.addWidget(priority_label)

        layout.addStretch()

    def mousePressEvent(self, event):
        """鼠标点击事件"""
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self)
        super().mousePressEvent(event)

    def enterEvent(self, event):
        """鼠标进入"""
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor("#f5f5f5"))
        self.setPalette(palette)
        super().enterEvent(event)

    def leaveEvent(self, event):
        """鼠标离开"""
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor("#ffffff"))
        self.setPalette(palette)
        super().leaveEvent(event)


class TaskColumn(QFrame):
    """任务列"""

    task_added = pyqtSignal(str, object)  # column_id, task
    task_clicked = pyqtSignal(object)  # task

    def __init__(self, column_id: str, title: str, color: str):
        super().__init__()
        self.column_id = column_id
        self.title = title
        self.color = color
        self.tasks = []

        self._init_ui()

    def _init_ui(self):
        """初始化UI"""
        self.setFrameShape(QFrame.Box)
        self.setMinimumWidth(300)
        self.setMaximumWidth(400)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # 列标题
        header = QFrame()
        header.setStyleSheet(f"background-color: {self.color}; border-radius: 5px; padding: 10px;")
        header_layout = QHBoxLayout(header)

        title_label = QLabel(self.title)
        title_label.setFont(QFont("Arial", 12, QFont.Bold))
        title_label.setStyleSheet("color: white;")
        header_layout.addWidget(title_label)

        self.count_label = QLabel("0")
        self.count_label.setStyleSheet("color: white; background-color: rgba(0,0,0,0.3); border-radius: 10px; padding: 3px 8px;")
        header_layout.addWidget(self.count_label)

        header_layout.addStretch()

        layout.addWidget(header)

        # 任务列表（滚动区域）
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        self.task_container = QWidget()
        self.task_layout = QVBoxLayout(self.task_container)
        self.task_layout.setAlignment(Qt.AlignTop)
        self.task_layout.setSpacing(10)

        scroll.setWidget(self.task_container)
        layout.addWidget(scroll)

    def add_task(self, task: TaskCard):
        """添加任务"""
        self.tasks.append(task)
        task.clicked.connect(self.task_clicked.emit)
        self.task_layout.addWidget(task)
        self._update_count()

    def remove_task(self, task: TaskCard):
        """移除任务"""
        if task in self.tasks:
            self.tasks.remove(task)
            self.task_layout.removeWidget(task)
            task.deleteLater()
            self._update_count()

    def clear_tasks(self):
        """清空所有任务"""
        for task in self.tasks[:]:
            self.remove_task(task)

    def _update_count(self):
        """更新任务计数"""
        self.count_label.setText(str(len(self.tasks)))


class TaskBoardWidget(QWidget):
    """任务看板界面组件"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.columns = {}
        self.current_task = None
        self._init_ui()
        self._add_demo_tasks()

    def _init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        # 顶部工具栏
        toolbar = self._create_toolbar()
        layout.addWidget(toolbar)

        # 主分割器
        splitter = QSplitter(Qt.Horizontal)

        # 左侧：看板
        board_widget = self._create_board()
        splitter.addWidget(board_widget)

        # 右侧：任务详情
        details_widget = self._create_details_panel()
        splitter.addWidget(details_widget)

        splitter.setSizes([800, 300])
        layout.addWidget(splitter, stretch=1)

    def _create_toolbar(self) -> QWidget:
        """创建工具栏"""
        toolbar = QFrame()
        toolbar.setStyleSheet("background-color: #f5f5f5; padding: 10px; border-radius: 5px;")
        layout = QHBoxLayout(toolbar)

        # 标题
        title = QLabel("📋 任务看板")
        title.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(title)

        layout.addStretch()

        # 筛选
        filter_label = QLabel("筛选:")
        layout.addWidget(filter_label)

        self.filter_combo = QComboBox()
        self.filter_combo.addItem("全部任务", "all")
        self.filter_combo.addItem("高优先级", "high")
        self.filter_combo.addItem("中优先级", "medium")
        self.filter_combo.addItem("低优先级", "low")
        layout.addWidget(self.filter_combo)

        # 按钮
        self.add_task_btn = QPushButton("➕ 新建任务")
        self.add_task_btn.clicked.connect(self._add_new_task)
        layout.addWidget(self.add_task_btn)

        self.refresh_btn = QPushButton("🔄 刷新")
        self.refresh_btn.clicked.connect(self._refresh_board)
        layout.addWidget(self.refresh_btn)

        return toolbar

    def _create_board(self) -> QWidget:
        """创建看板"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setSpacing(15)

        # 创建三列
        pending_col = TaskColumn("pending", "📝 待办", "#2196F3")
        pending_col.task_clicked.connect(self._on_task_clicked)
        self.columns["pending"] = pending_col
        layout.addWidget(pending_col)

        in_progress_col = TaskColumn("in_progress", "⚙️ 进行中", "#FF9800")
        in_progress_col.task_clicked.connect(self._on_task_clicked)
        self.columns["in_progress"] = in_progress_col
        layout.addWidget(in_progress_col)

        completed_col = TaskColumn("completed", "✅ 已完成", "#4CAF50")
        completed_col.task_clicked.connect(self._on_task_clicked)
        self.columns["completed"] = completed_col
        layout.addWidget(completed_col)

        return widget

    def _create_details_panel(self) -> QWidget:
        """创建任务详情面板"""
        widget = QGroupBox("📄 任务详情")
        layout = QVBoxLayout(widget)

        # 任务标题
        title_label = QLabel("标题:")
        layout.addWidget(title_label)

        self.detail_title = QLineEdit()
        self.detail_title.setPlaceholderText("任务标题")
        layout.addWidget(self.detail_title)

        # 任务描述
        desc_label = QLabel("描述:")
        layout.addWidget(desc_label)

        self.detail_description = QTextEdit()
        self.detail_description.setPlaceholderText("任务详细描述...")
        self.detail_description.setMaximumHeight(150)
        layout.addWidget(self.detail_description)

        # 优先级
        priority_label = QLabel("优先级:")
        layout.addWidget(priority_label)

        self.detail_priority = QComboBox()
        self.detail_priority.addItem("高", "high")
        self.detail_priority.addItem("中", "medium")
        self.detail_priority.addItem("低", "low")
        layout.addWidget(self.detail_priority)

        # 状态
        status_label = QLabel("状态:")
        layout.addWidget(status_label)

        self.detail_status = QComboBox()
        self.detail_status.addItem("待办", "pending")
        self.detail_status.addItem("进行中", "in_progress")
        self.detail_status.addItem("已完成", "completed")
        self.detail_status.currentIndexChanged.connect(self._on_status_changed)
        layout.addWidget(self.detail_status)

        layout.addStretch()

        # 按钮
        btn_layout = QHBoxLayout()

        self.save_btn = QPushButton("💾 保存")
        self.save_btn.clicked.connect(self._save_task)
        self.save_btn.setEnabled(False)
        btn_layout.addWidget(self.save_btn)

        self.delete_btn = QPushButton("🗑️ 删除")
        self.delete_btn.clicked.connect(self._delete_task)
        self.delete_btn.setEnabled(False)
        btn_layout.addWidget(self.delete_btn)

        layout.addLayout(btn_layout)

        return widget

    def _add_demo_tasks(self):
        """添加演示任务"""
        # 待办任务
        task1 = TaskCard("1", "实现用户登录功能", "开发用户登录界面和后端API", "high")
        self.columns["pending"].add_task(task1)

        task2 = TaskCard("2", "编写单元测试", "为新功能编写完整的单元测试", "medium")
        self.columns["pending"].add_task(task2)

        task3 = TaskCard("3", "更新文档", "更新README和API文档", "low")
        self.columns["pending"].add_task(task3)

        # 进行中任务
        task4 = TaskCard("4", "优化数据库查询", "提升数据库查询性能", "high")
        self.columns["in_progress"].add_task(task4)

        task5 = TaskCard("5", "设计新界面", "设计用户设置界面的原型", "medium")
        self.columns["in_progress"].add_task(task5)

        # 已完成任务
        task6 = TaskCard("6", "修复登录bug", "修复用户登录时的空指针异常", "high")
        self.columns["completed"].add_task(task6)

        task7 = TaskCard("7", "配置CI/CD", "配置GitHub Actions自动化流程", "medium")
        self.columns["completed"].add_task(task7)

    def _on_task_clicked(self, task: TaskCard):
        """任务被点击"""
        self.current_task = task

        # 更新详情面板
        self.detail_title.setText(task.title)
        self.detail_description.setPlainText(task.description)

        # 设置优先级
        priority_index = {"high": 0, "medium": 1, "low": 2}.get(task.priority, 1)
        self.detail_priority.setCurrentIndex(priority_index)

        # 设置状态
        for column_id, column in self.columns.items():
            if task in column.tasks:
                status_index = {"pending": 0, "in_progress": 1, "completed": 2}.get(column_id, 0)
                self.detail_status.setCurrentIndex(status_index)
                break

        # 启用按钮
        self.save_btn.setEnabled(True)
        self.delete_btn.setEnabled(True)

    def _on_status_changed(self):
        """状态改变"""
        if not self.current_task:
            return

        new_status = self.detail_status.currentData()

        # 找到当前任务所在的列
        current_column = None
        for column in self.columns.values():
            if self.current_task in column.tasks:
                current_column = column
                break

        if current_column and current_column.column_id != new_status:
            # 移动任务到新列
            current_column.remove_task(self.current_task)
            self.columns[new_status].add_task(self.current_task)

    def _add_new_task(self):
        """添加新任务"""
        # 清空详情面板
        self.detail_title.clear()
        self.detail_description.clear()
        self.detail_priority.setCurrentIndex(1)  # medium
        self.detail_status.setCurrentIndex(0)  # pending

        self.current_task = None
        self.save_btn.setEnabled(True)
        self.delete_btn.setEnabled(False)

        # 聚焦到标题输入
        self.detail_title.setFocus()

    def _save_task(self):
        """保存任务"""
        title = self.detail_title.text().strip()
        if not title:
            return

        description = self.detail_description.toPlainText().strip()
        priority = self.detail_priority.currentData()
        status = self.detail_status.currentData()

        if self.current_task:
            # 更新现有任务
            # 找到任务所在的列
            for column in self.columns.values():
                if self.current_task in column.tasks:
                    column.remove_task(self.current_task)
                    break

        # 创建新任务
        import time
        task_id = str(int(time.time() * 1000))
        new_task = TaskCard(task_id, title, description, priority)
        self.columns[status].add_task(new_task)

        self.current_task = new_task

    def _delete_task(self):
        """删除任务"""
        if not self.current_task:
            return

        # 找到任务并删除
        for column in self.columns.values():
            if self.current_task in column.tasks:
                column.remove_task(self.current_task)
                break

        # 清空详情面板
        self.detail_title.clear()
        self.detail_description.clear()
        self.current_task = None
        self.save_btn.setEnabled(False)
        self.delete_btn.setEnabled(False)

    def _refresh_board(self):
        """刷新看板"""
        # TODO: 从后端重新加载任务
        pass
