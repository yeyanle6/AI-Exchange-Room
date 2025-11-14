"""
需求分析界面组件
展示多角色AI讨论和需求分析结果
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QTextEdit, QLabel, QPushButton, QLineEdit,
    QCheckBox, QGroupBox, QScrollArea, QFrame,
    QProgressBar, QComboBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QTextCursor, QFont, QColor, QTextCharFormat
from typing import Dict, List, Optional
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.core.multi_agent_analyst import AgentRole, MultiAgentAnalyst


class AnalysisWorker(QThread):
    """后台分析线程"""
    message_received = pyqtSignal(str, str, str)  # role, name, message
    analysis_complete = pyqtSignal(dict)  # result
    progress_update = pyqtSignal(int)  # progress percentage
    error_occurred = pyqtSignal(str)  # error message

    def __init__(self, project_description: str, project_type: str = "desktop_app"):
        super().__init__()
        self.project_description = project_description
        self.project_type = project_type
        self.analyst = MultiAgentAnalyst()
        self._stop_requested = False

    def stop(self):
        """请求停止分析"""
        self._stop_requested = True

    def run(self):
        """执行需求分析"""
        try:
            # 模拟进度更新
            self.progress_update.emit(10)

            # 模拟各个AI角色的讨论
            role_messages = {
                AgentRole.PRODUCT_MANAGER: [
                    "让我从产品角度分析这个需求...",
                    "首先，我们需要明确目标用户群体是谁",
                    "核心价值主张应该是提升开发效率",
                    "建议将功能分为MVP版本和后续迭代"
                ],
                AgentRole.TECH_ARCHITECT: [
                    "从技术架构角度来看...",
                    "建议采用模块化设计，便于扩展",
                    "需要考虑系统的可维护性和性能",
                    "后端选用Python，前端使用PyQt5是合理的"
                ],
                AgentRole.UX_DESIGNER: [
                    "用户体验方面需要注意...",
                    "界面应该简洁直观，降低学习成本",
                    "建议参考VS Code的布局设计",
                    "颜色方案使用亮色主题，符合专业工具的定位"
                ],
                AgentRole.QA_ENGINEER: [
                    "从测试角度考虑...",
                    "需要确保每个功能模块都有单元测试",
                    "建议添加集成测试覆盖主要用户场景",
                    "性能测试也很重要，特别是AI分析部分"
                ],
                AgentRole.DEVOPS_ENGINEER: [
                    "部署和运维方面...",
                    "建议提供Docker镜像简化部署",
                    "需要考虑日志管理和监控",
                    "配置管理应该灵活，支持不同环境"
                ],
                AgentRole.SECURITY_EXPERT: [
                    "安全角度的考虑...",
                    "用户数据需要加密存储",
                    "API调用要有认证机制",
                    "建议进行安全审计和漏洞扫描"
                ]
            }

            total_messages = sum(len(msgs) for msgs in role_messages.values())
            current = 0

            for role, messages in role_messages.items():
                if self._stop_requested:
                    break
                persona = self.analyst.agents[role].persona
                for msg in messages:
                    if self._stop_requested:
                        break
                    self.message_received.emit(
                        role.value,
                        persona.name,
                        msg
                    )
                    current += 1
                    progress = 10 + int((current / total_messages) * 70)
                    self.progress_update.emit(progress)
                    self.msleep(800)  # 模拟思考时间

            self.progress_update.emit(90)

            # 执行实际分析
            result = self.analyst.analyze_requirement(
                self.project_description,
                max_rounds=1
            )

            self.progress_update.emit(100)
            self.analysis_complete.emit(result)

        except Exception as e:
            import traceback
            error_msg = f"分析过程出错: {str(e)}"
            print(f"[ERROR] {error_msg}\n{traceback.format_exc()}")
            self.error_occurred.emit(error_msg)


class RequirementAnalysisWidget(QWidget):
    """需求分析界面组件"""

    # 角色颜色映射
    ROLE_COLORS = {
        AgentRole.PRODUCT_MANAGER.value: "#2E7D32",  # 深绿
        AgentRole.TECH_ARCHITECT.value: "#1565C0",   # 深蓝
        AgentRole.UX_DESIGNER.value: "#6A1B9A",      # 紫色
        AgentRole.QA_ENGINEER.value: "#D84315",      # 深橙
        AgentRole.DEVOPS_ENGINEER.value: "#F57C00",  # 橙色
        AgentRole.SECURITY_EXPERT.value: "#C62828",  # 深红
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self.worker = None
        self.role_filters = {}  # 角色筛选状态
        self._init_ui()

    def _init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        # 顶部：项目描述输入
        top_group = self._create_input_section()
        layout.addWidget(top_group)

        # 中间：主分割器（讨论区 + 结果区）
        splitter = QSplitter(Qt.Horizontal)

        # 左侧：AI讨论区
        discussion_widget = self._create_discussion_section()
        splitter.addWidget(discussion_widget)

        # 右侧：分析结果区
        result_widget = self._create_result_section()
        splitter.addWidget(result_widget)

        splitter.setSizes([600, 400])
        layout.addWidget(splitter, stretch=1)

        # 底部：进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

    def _create_input_section(self) -> QGroupBox:
        """创建输入区域"""
        group = QGroupBox("📝 项目需求描述")
        layout = QVBoxLayout(group)

        # 需求输入框
        self.requirement_input = QTextEdit()
        self.requirement_input.setPlaceholderText(
            "请输入项目需求描述...\n\n"
            "例如：\n"
            "我需要开发一个AI驱动的代码审查工具，\n"
            "能够自动分析代码质量、发现潜在bug，\n"
            "并提供改进建议。"
        )
        self.requirement_input.setMaximumHeight(120)
        layout.addWidget(self.requirement_input)

        # 按钮行
        btn_layout = QHBoxLayout()

        self.analyze_btn = QPushButton("🚀 开始分析")
        self.analyze_btn.clicked.connect(self._start_analysis)
        self.analyze_btn.setMinimumHeight(35)
        btn_layout.addWidget(self.analyze_btn)

        self.clear_btn = QPushButton("🗑️ 清空")
        self.clear_btn.clicked.connect(self._clear_all)
        btn_layout.addWidget(self.clear_btn)

        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        return group

    def _create_discussion_section(self) -> QWidget:
        """创建讨论区域"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)

        # 标题和筛选
        header_layout = QHBoxLayout()
        header_label = QLabel("💬 AI角色讨论")
        header_label.setFont(QFont("Arial", 12, QFont.Bold))
        header_layout.addWidget(header_label)

        header_layout.addStretch()

        # 角色筛选按钮
        filter_label = QLabel("筛选:")
        header_layout.addWidget(filter_label)

        self.filter_combo = QComboBox()
        self.filter_combo.addItem("全部角色", None)
        self.filter_combo.addItem("👤 产品经理", AgentRole.PRODUCT_MANAGER.value)
        self.filter_combo.addItem("🏗️ 架构师", AgentRole.TECH_ARCHITECT.value)
        self.filter_combo.addItem("🎨 UX设计师", AgentRole.UX_DESIGNER.value)
        self.filter_combo.addItem("🔍 测试工程师", AgentRole.QA_ENGINEER.value)
        self.filter_combo.addItem("🚀 DevOps", AgentRole.DEVOPS_ENGINEER.value)
        self.filter_combo.addItem("🔒 安全专家", AgentRole.SECURITY_EXPERT.value)
        self.filter_combo.currentIndexChanged.connect(self._apply_filter)
        header_layout.addWidget(self.filter_combo)

        layout.addLayout(header_layout)

        # 讨论显示区
        self.discussion_area = QTextEdit()
        self.discussion_area.setReadOnly(True)
        self.discussion_area.setPlaceholderText("AI角色的讨论将在这里显示...")
        layout.addWidget(self.discussion_area)

        return widget

    def _create_result_section(self) -> QWidget:
        """创建结果区域"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)

        # 标题
        header_label = QLabel("📊 分析结果")
        header_label.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(header_label)

        # 结果显示区（使用标签页）
        from PyQt5.QtWidgets import QTabWidget

        self.result_tabs = QTabWidget()

        # 共识标签页
        self.consensus_area = QTextEdit()
        self.consensus_area.setReadOnly(True)
        self.consensus_area.setPlaceholderText("AI角色达成的共识...")
        self.result_tabs.addTab(self.consensus_area, "✅ 共识")

        # 关注点标签页
        self.concerns_area = QTextEdit()
        self.concerns_area.setReadOnly(True)
        self.concerns_area.setPlaceholderText("需要关注的问题...")
        self.result_tabs.addTab(self.concerns_area, "⚠️ 关注点")

        # 建议标签页
        self.suggestions_area = QTextEdit()
        self.suggestions_area.setReadOnly(True)
        self.suggestions_area.setPlaceholderText("改进建议...")
        self.result_tabs.addTab(self.suggestions_area, "💡 建议")

        layout.addWidget(self.result_tabs)

        return widget

    def _start_analysis(self):
        """开始需求分析"""
        requirement = self.requirement_input.toPlainText().strip()

        # 输入验证
        if not requirement:
            self._log_system_message("⚠️ 请输入项目需求描述")
            return

        if len(requirement) < 10:
            self._log_system_message("⚠️ 需求描述过短，请至少输入10个字符")
            return

        if len(requirement) > 5000:
            self._log_system_message("⚠️ 需求描述过长，请控制在5000字符以内")
            return

        # 如果已有线程在运行，先停止
        if self.worker is not None and self.worker.isRunning():
            self._log_system_message("⚠️ 上一个分析任务仍在运行，请稍候...")
            return

        # 清理旧线程
        if self.worker is not None:
            self.worker.deleteLater()
            self.worker = None

        # 清空之前的内容
        self.discussion_area.clear()
        self.consensus_area.clear()
        self.concerns_area.clear()
        self.suggestions_area.clear()

        # 显示进度条
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)

        # 禁用分析按钮
        self.analyze_btn.setEnabled(False)
        self.analyze_btn.setText("分析中...")

        # 创建并启动工作线程
        self.worker = AnalysisWorker(requirement)
        self.worker.message_received.connect(self._on_message_received)
        self.worker.analysis_complete.connect(self._on_analysis_complete)
        self.worker.progress_update.connect(self._on_progress_update)
        self.worker.error_occurred.connect(self._on_analysis_error)
        self.worker.start()

        self._log_system_message("🚀 开始需求分析，AI角色正在讨论...")

    def _on_message_received(self, role: str, name: str, message: str):
        """接收AI消息"""
        # 获取角色颜色
        color = self.ROLE_COLORS.get(role, "#000000")

        # 获取角色emoji
        role_emoji = {
            AgentRole.PRODUCT_MANAGER.value: "👤",
            AgentRole.TECH_ARCHITECT.value: "🏗️",
            AgentRole.UX_DESIGNER.value: "🎨",
            AgentRole.QA_ENGINEER.value: "🔍",
            AgentRole.DEVOPS_ENGINEER.value: "🚀",
            AgentRole.SECURITY_EXPERT.value: "🔒",
        }.get(role, "🤖")

        # 添加消息到讨论区
        cursor = self.discussion_area.textCursor()
        cursor.movePosition(QTextCursor.End)

        # 角色名称（加粗、彩色）
        format_name = QTextCharFormat()
        format_name.setFontWeight(QFont.Bold)
        format_name.setForeground(QColor(color))
        cursor.insertText(f"{role_emoji} {name}: ", format_name)

        # 消息内容
        format_message = QTextCharFormat()
        format_message.setForeground(QColor("#000000"))
        cursor.insertText(f"{message}\n", format_message)

        # 滚动到底部
        self.discussion_area.setTextCursor(cursor)
        self.discussion_area.ensureCursorVisible()

    def _on_analysis_complete(self, result: dict):
        """分析完成"""
        # 隐藏进度条
        self.progress_bar.setVisible(False)

        # 恢复按钮
        self.analyze_btn.setEnabled(True)
        self.analyze_btn.setText("🚀 开始分析")

        # 显示结果
        self._display_results(result)

        self._log_system_message("✅ 需求分析完成！")

    def _on_progress_update(self, progress: int):
        """更新进度"""
        self.progress_bar.setValue(progress)

    def _on_analysis_error(self, error_msg: str):
        """处理分析错误"""
        # 隐藏进度条
        self.progress_bar.setVisible(False)

        # 恢复按钮
        self.analyze_btn.setEnabled(True)
        self.analyze_btn.setText("🚀 开始分析")

        # 显示错误消息
        self._log_system_message(f"❌ 错误: {error_msg}")

    def _display_results(self, result: dict):
        """显示分析结果"""
        # 显示共识
        consensus = result.get("consensus", [])
        if consensus:
            self.consensus_area.append("📋 AI角色达成以下共识：\n")
            for i, item in enumerate(consensus, 1):
                self.consensus_area.append(f"{i}. {item}")
        else:
            self.consensus_area.append("暂无共识内容")

        # 显示关注点
        concerns = result.get("concerns", [])
        if concerns:
            self.concerns_area.append("⚠️ 需要关注的问题：\n")
            for i, item in enumerate(concerns, 1):
                self.concerns_area.append(f"{i}. {item}")
        else:
            self.concerns_area.append("暂无关注点")

        # 显示建议
        suggestions = result.get("suggestions", [])
        if suggestions:
            self.suggestions_area.append("💡 改进建议：\n")
            for i, item in enumerate(suggestions, 1):
                self.suggestions_area.append(f"{i}. {item}")
        else:
            self.suggestions_area.append("暂无建议")

    def _log_system_message(self, message: str):
        """记录系统消息"""
        cursor = self.discussion_area.textCursor()
        cursor.movePosition(QTextCursor.End)

        format_system = QTextCharFormat()
        format_system.setForeground(QColor("#888888"))
        format_system.setFontItalic(True)
        cursor.insertText(f"\n{message}\n\n", format_system)

        self.discussion_area.setTextCursor(cursor)
        self.discussion_area.ensureCursorVisible()

    def _apply_filter(self):
        """应用角色筛选"""
        # TODO: 实现筛选逻辑
        pass

    def _clear_all(self):
        """清空所有内容"""
        self.requirement_input.clear()
        self.discussion_area.clear()
        self.consensus_area.clear()
        self.concerns_area.clear()
        self.suggestions_area.clear()
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)
