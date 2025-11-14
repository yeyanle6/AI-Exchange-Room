"""
监控仪表板界面组件
实时显示项目进度和统计信息
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QFrame, QScrollArea, QGroupBox, QGridLayout,
    QPushButton, QProgressBar
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QColor, QPalette
import sys
from pathlib import Path
from datetime import datetime
import random

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))


class MetricCard(QFrame):
    """指标卡片"""

    def __init__(self, title: str, value: str, icon: str = "📊", color: str = "#2196F3"):
        super().__init__()
        self.title = title
        self.value = value
        self.icon = icon
        self.color = color
        self._init_ui()

    def _init_ui(self):
        """初始化UI"""
        self.setFrameShape(QFrame.Box)
        self.setFrameShadow(QFrame.Raised)
        self.setMinimumHeight(120)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {self.color};
                border-radius: 10px;
                padding: 15px;
            }}
        """)

        layout = QVBoxLayout(self)

        # 图标和标题
        header_layout = QHBoxLayout()

        icon_label = QLabel(self.icon)
        icon_label.setFont(QFont("Arial", 24))
        header_layout.addWidget(icon_label)

        header_layout.addStretch()

        layout.addLayout(header_layout)

        # 数值
        self.value_label = QLabel(self.value)
        self.value_label.setFont(QFont("Arial", 28, QFont.Bold))
        self.value_label.setStyleSheet("color: white;")
        layout.addWidget(self.value_label)

        # 标题
        title_label = QLabel(self.title)
        title_label.setFont(QFont("Arial", 11))
        title_label.setStyleSheet("color: rgba(255, 255, 255, 0.9);")
        layout.addWidget(title_label)

    def update_value(self, value: str):
        """更新数值"""
        self.value_label.setText(value)


class ProgressSection(QFrame):
    """进度区域"""

    def __init__(self, title: str):
        super().__init__()
        self.title = title
        self.progress_bars = {}
        self._init_ui()

    def _init_ui(self):
        """初始化UI"""
        self.setFrameShape(QFrame.Box)
        self.setStyleSheet("background-color: white; border-radius: 10px; padding: 15px;")

        layout = QVBoxLayout(self)

        # 标题
        title_label = QLabel(self.title)
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(title_label)

        # 进度条容器
        self.progress_layout = QVBoxLayout()
        layout.addLayout(self.progress_layout)

    def add_progress(self, label: str, value: int, color: str = "#4CAF50"):
        """添加进度条"""
        item_layout = QVBoxLayout()

        # 标签
        label_widget = QLabel(f"{label}: {value}%")
        label_widget.setStyleSheet("color: #666;")
        item_layout.addWidget(label_widget)

        # 进度条
        progress = QProgressBar()
        progress.setValue(value)
        progress.setStyleSheet(f"""
            QProgressBar {{
                border: none;
                border-radius: 5px;
                background-color: #e0e0e0;
                height: 20px;
                text-align: center;
            }}
            QProgressBar::chunk {{
                background-color: {color};
                border-radius: 5px;
            }}
        """)
        item_layout.addWidget(progress)

        self.progress_layout.addLayout(item_layout)
        self.progress_bars[label] = (label_widget, progress)

    def update_progress(self, label: str, value: int):
        """更新进度"""
        if label in self.progress_bars:
            label_widget, progress = self.progress_bars[label]
            label_widget.setText(f"{label}: {value}%")
            progress.setValue(value)


class ActivityLog(QFrame):
    """活动日志"""

    def __init__(self):
        super().__init__()
        self._init_ui()

    def _init_ui(self):
        """初始化UI"""
        self.setFrameShape(QFrame.Box)
        self.setStyleSheet("background-color: white; border-radius: 10px; padding: 15px;")

        layout = QVBoxLayout(self)

        # 标题
        header_layout = QHBoxLayout()
        title_label = QLabel("📜 活动日志")
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        refresh_btn = QPushButton("🔄")
        refresh_btn.setMaximumWidth(40)
        header_layout.addWidget(refresh_btn)

        layout.addLayout(header_layout)

        # 滚动区域
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        log_container = QWidget()
        self.log_layout = QVBoxLayout(log_container)
        self.log_layout.setAlignment(Qt.AlignTop)

        scroll.setWidget(log_container)
        layout.addWidget(scroll)

    def add_log(self, time: str, message: str, level: str = "info"):
        """添加日志条目"""
        log_item = QFrame()
        log_item.setFrameShape(QFrame.NoFrame)
        item_layout = QHBoxLayout(log_item)
        item_layout.setContentsMargins(0, 5, 0, 5)

        # 时间
        time_label = QLabel(time)
        time_label.setStyleSheet("color: #999; font-size: 10px;")
        time_label.setFixedWidth(80)
        item_layout.addWidget(time_label)

        # 图标
        icons = {
            "info": "ℹ️",
            "success": "✅",
            "warning": "⚠️",
            "error": "❌"
        }
        icon_label = QLabel(icons.get(level, "ℹ️"))
        item_layout.addWidget(icon_label)

        # 消息
        msg_label = QLabel(message)
        msg_label.setWordWrap(True)
        msg_label.setStyleSheet("color: #333; font-size: 11px;")
        item_layout.addWidget(msg_label, stretch=1)

        self.log_layout.insertWidget(0, log_item)  # 新日志在顶部


class MonitoringDashboardWidget(QWidget):
    """监控仪表板界面组件"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.metric_cards = {}
        self._init_ui()
        self._start_auto_refresh()
        self._add_demo_logs()

    def _init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)

        # 标题栏
        header = self._create_header()
        layout.addWidget(header)

        # 滚动区域
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(15)

        # 顶部：指标卡片
        metrics_layout = self._create_metrics_section()
        content_layout.addLayout(metrics_layout)

        # 中间：进度区域
        progress_section = self._create_progress_section()
        content_layout.addWidget(progress_section)

        # 底部：活动日志和统计图表
        bottom_layout = QHBoxLayout()

        # 活动日志
        self.activity_log = ActivityLog()
        bottom_layout.addWidget(self.activity_log, stretch=1)

        # 统计信息
        stats_widget = self._create_stats_section()
        bottom_layout.addWidget(stats_widget, stretch=1)

        content_layout.addLayout(bottom_layout)

        scroll.setWidget(content_widget)
        layout.addWidget(scroll)

    def _create_header(self) -> QWidget:
        """创建标题栏"""
        header = QFrame()
        header.setStyleSheet("background-color: #f5f5f5; padding: 10px; border-radius: 5px;")
        layout = QHBoxLayout(header)

        # 标题
        title = QLabel("📊 监控仪表板")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        layout.addWidget(title)

        # 时间
        self.time_label = QLabel()
        self._update_time()
        self.time_label.setStyleSheet("color: #666;")
        layout.addWidget(self.time_label)

        layout.addStretch()

        # 刷新按钮
        refresh_btn = QPushButton("🔄 刷新数据")
        refresh_btn.clicked.connect(self._refresh_data)
        layout.addWidget(refresh_btn)

        return header

    def _create_metrics_section(self) -> QHBoxLayout:
        """创建指标区域"""
        layout = QHBoxLayout()
        layout.setSpacing(15)

        # 总任务数
        total_tasks_card = MetricCard("总任务数", "15", "📝", "#2196F3")
        self.metric_cards["total_tasks"] = total_tasks_card
        layout.addWidget(total_tasks_card)

        # 已完成任务
        completed_card = MetricCard("已完成", "8", "✅", "#4CAF50")
        self.metric_cards["completed"] = completed_card
        layout.addWidget(completed_card)

        # 进行中任务
        in_progress_card = MetricCard("进行中", "5", "⚙️", "#FF9800")
        self.metric_cards["in_progress"] = in_progress_card
        layout.addWidget(in_progress_card)

        # 完成率
        completion_card = MetricCard("完成率", "53%", "📈", "#9C27B0")
        self.metric_cards["completion"] = completion_card
        layout.addWidget(completion_card)

        return layout

    def _create_progress_section(self) -> ProgressSection:
        """创建进度区域"""
        self.progress_section = ProgressSection("📊 项目进度")

        # 添加示例进度条
        self.progress_section.add_progress("需求分析", 100, "#4CAF50")
        self.progress_section.add_progress("开发进度", 65, "#2196F3")
        self.progress_section.add_progress("测试覆盖", 45, "#FF9800")
        self.progress_section.add_progress("文档完成", 30, "#9C27B0")

        return self.progress_section

    def _create_stats_section(self) -> QFrame:
        """创建统计信息区域"""
        frame = QFrame()
        frame.setFrameShape(QFrame.Box)
        frame.setStyleSheet("background-color: white; border-radius: 10px; padding: 15px;")

        layout = QVBoxLayout(frame)

        # 标题
        title = QLabel("📈 项目统计")
        title.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(title)

        # 统计项
        stats_grid = QGridLayout()

        stats = [
            ("代码行数", "2,850"),
            ("文件数", "28"),
            ("函数数", "156"),
            ("测试数", "42"),
            ("Bug数", "3"),
            ("团队成员", "6"),
        ]

        for i, (label, value) in enumerate(stats):
            row = i // 2
            col = i % 2

            # 标签
            label_widget = QLabel(label)
            label_widget.setStyleSheet("color: #666; font-size: 11px;")
            stats_grid.addWidget(label_widget, row * 2, col)

            # 值
            value_widget = QLabel(value)
            value_widget.setFont(QFont("Arial", 16, QFont.Bold))
            value_widget.setStyleSheet("color: #333;")
            stats_grid.addWidget(value_widget, row * 2 + 1, col)

        layout.addLayout(stats_grid)
        layout.addStretch()

        return frame

    def _add_demo_logs(self):
        """添加演示日志"""
        logs = [
            ("10:30:15", "需求分析完成", "success"),
            ("10:28:42", "开始执行任务: 实现用户登录", "info"),
            ("10:25:18", "测试通过: 用户注册功能", "success"),
            ("10:20:05", "发现潜在问题: 密码加密强度不足", "warning"),
            ("10:15:33", "代码审查完成", "success"),
            ("10:10:22", "构建成功", "success"),
        ]

        for time, msg, level in logs:
            self.activity_log.add_log(time, msg, level)

    def _update_time(self):
        """更新时间显示"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time_label.setText(f"最后更新: {current_time}")

    def _refresh_data(self):
        """刷新数据"""
        # 模拟数据更新
        self._update_time()

        # 随机更新指标
        total = random.randint(10, 20)
        completed = random.randint(5, total)
        in_progress = random.randint(0, total - completed)
        completion = int((completed / total) * 100)

        self.metric_cards["total_tasks"].update_value(str(total))
        self.metric_cards["completed"].update_value(str(completed))
        self.metric_cards["in_progress"].update_value(str(in_progress))
        self.metric_cards["completion"].update_value(f"{completion}%")

        # 更新进度
        self.progress_section.update_progress("开发进度", random.randint(50, 100))
        self.progress_section.update_progress("测试覆盖", random.randint(30, 80))
        self.progress_section.update_progress("文档完成", random.randint(20, 60))

        # 添加日志
        current_time = datetime.now().strftime("%H:%M:%S")
        self.activity_log.add_log(current_time, "数据已刷新", "info")

    def _start_auto_refresh(self):
        """启动自动刷新"""
        # 每30秒自动刷新时间
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_time)
        self.timer.start(30000)  # 30秒
