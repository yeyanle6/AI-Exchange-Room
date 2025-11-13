"""
项目管理器
管理项目的完整生命周期和状态持久化
"""
import os
import uuid
from typing import Optional
from datetime import datetime

from ..models import Project, ProjectPhase, Task, TaskStatus
from ..utils import save_json, load_json, save_text, load_text, app_logger
from .requirement_analyst import RequirementAnalyst
from .task_decomposer import TaskDecomposer


class ProjectManager:
    """
    AI项目管理器
    负责协调整个项目的生命周期
    """

    def __init__(self, workspace_root: str = "./projects"):
        """
        初始化项目管理器

        Args:
            workspace_root: 项目工作区根目录
        """
        self.workspace_root = workspace_root
        self.logger = app_logger
        self.current_project: Optional[Project] = None

        # 创建组件
        self.requirement_analyst = RequirementAnalyst()
        self.task_decomposer = TaskDecomposer()

        # 确保工作区目录存在
        os.makedirs(workspace_root, exist_ok=True)

    def create_new_project(self, project_name: str, high_level_goal: str) -> Project:
        """
        创建新项目

        Args:
            project_name: 项目名称
            high_level_goal: 高层目标

        Returns:
            创建的项目对象
        """
        # 生成项目ID
        project_id = f"PRJ-{uuid.uuid4().hex[:8].upper()}"

        # 创建项目工作区
        project_workspace = os.path.join(self.workspace_root, project_id)

        # 创建项目对象
        project = Project(
            name=project_name,
            project_id=project_id,
            workspace_path=project_workspace,
            phase=ProjectPhase.INITIALIZATION
        )

        # 保存高层目标
        project.metadata['high_level_goal'] = high_level_goal

        self.current_project = project
        self.logger.info(f"创建新项目: {project_name} (ID: {project_id})")

        # 保存项目
        self.save_project(project)

        return project

    def run_requirement_analysis(self, project: Project,
                                 interactive: bool = True,
                                 auto_answers: dict = None) -> Project:
        """
        运行需求分析阶段

        Args:
            project: 项目对象
            interactive: 是否交互式（命令行输入）
            auto_answers: 自动回答（用于非交互式测试）

        Returns:
            更新后的项目
        """
        self.logger.info(f"开始需求分析阶段: {project.name}")
        project.update_phase(ProjectPhase.REQUIREMENT_ANALYSIS)

        # 获取高层目标
        high_level_goal = project.metadata.get('high_level_goal', '')
        if project.requirement:
            high_level_goal = project.requirement.high_level_goal

        if interactive:
            # 交互式需求分析
            requirement = self.requirement_analyst.interactive_analysis(
                project.name,
                high_level_goal
            )
        else:
            # 非交互式（自动化测试用）
            self.requirement_analyst.start_analysis(
                project.name,
                high_level_goal
            )

            # 使用提供的答案
            if auto_answers:
                questions = self.requirement_analyst.generate_clarification_questions()
                for question in questions:
                    answer = auto_answers.get(question, "默认答案")
                    self.requirement_analyst.record_answer(question, answer)

            # 生成用户故事
            self.requirement_analyst.analyze_answers_and_generate_stories()
            self.requirement_analyst.infer_tech_stack()
            requirement = self.requirement_analyst.finalize_requirement()

        # 保存需求文档
        project.requirement = requirement
        self.save_requirement_document(project)

        # 保存项目状态
        self.save_project(project)

        self.logger.info("需求分析阶段完成")
        return project

    def run_task_planning(self, project: Project) -> Project:
        """
        运行任务规划阶段

        Args:
            project: 项目对象

        Returns:
            更新后的项目
        """
        if not project.requirement:
            raise ValueError("需求文档未完成，无法进行任务规划")

        self.logger.info(f"开始任务规划阶段: {project.name}")
        project.update_phase(ProjectPhase.TASK_PLANNING)

        # 分解需求为任务
        task_queue = self.task_decomposer.decompose_requirement(project.requirement)
        project.task_queue = task_queue

        # 生成任务摘要
        summary = self.task_decomposer.generate_task_summary(task_queue)
        summary_path = os.path.join(project.docs_path, "TASKS_SUMMARY.md")
        save_text(summary, summary_path)

        self.logger.info(f"任务规划完成，生成了 {len(task_queue.tasks)} 个任务")

        # 保存每个任务的指令文件
        for task in task_queue.tasks:
            self.save_task_instruction(project, task)

        # 保存项目状态
        self.save_project(project)

        return project

    def get_next_task(self, project: Project) -> Optional[Task]:
        """
        获取下一个待执行的任务

        Args:
            project: 项目对象

        Returns:
            下一个任务，如果没有则返回None
        """
        return project.task_queue.get_next_task()

    def mark_task_started(self, project: Project, task_id: str):
        """
        标记任务开始

        Args:
            project: 项目对象
            task_id: 任务ID
        """
        task = project.task_queue.get_task_by_id(task_id)
        if task:
            task.start()
            self.logger.info(f"任务开始: {task.title}")
            self.save_project(project)

    def mark_task_completed(self, project: Project, task_id: str, output_files: list = None):
        """
        标记任务完成

        Args:
            project: 项目对象
            task_id: 任务ID
            output_files: 产出的文件列表
        """
        task = project.task_queue.get_task_by_id(task_id)
        if task:
            task.complete(output_files)
            self.logger.info(f"任务完成: {task.title}")
            self.save_project(project)

    def mark_task_failed(self, project: Project, task_id: str, error_message: str):
        """
        标记任务失败

        Args:
            project: 项目对象
            task_id: 任务ID
            error_message: 错误信息
        """
        task = project.task_queue.get_task_by_id(task_id)
        if task:
            task.fail(error_message)
            self.logger.error(f"任务失败: {task.title} - {error_message}")
            self.save_project(project)

    def save_project(self, project: Project):
        """
        保存项目状态

        Args:
            project: 项目对象
        """
        project_file = os.path.join(project.workspace_path, "project.json")
        save_json(project.to_dict(), project_file)
        self.logger.debug(f"项目状态已保存: {project_file}")

    def load_project(self, project_id: str) -> Optional[Project]:
        """
        加载项目

        Args:
            project_id: 项目ID

        Returns:
            项目对象，如果不存在则返回None
        """
        project_workspace = os.path.join(self.workspace_root, project_id)
        project_file = os.path.join(project_workspace, "project.json")

        if not os.path.exists(project_file):
            self.logger.warning(f"项目不存在: {project_id}")
            return None

        # 这里简化处理，实际应该完整反序列化
        self.logger.info(f"加载项目: {project_id}")
        # TODO: 实现完整的项目加载逻辑
        return None

    def save_requirement_document(self, project: Project):
        """
        保存需求文档为Markdown格式

        Args:
            project: 项目对象
        """
        if not project.requirement:
            return

        prd_path = project.get_prd_path()
        prd_text = project.requirement.to_text()
        save_text(prd_text, prd_path)

        self.logger.info(f"需求文档已保存: {prd_path}")

    def save_task_instruction(self, project: Project, task: Task):
        """
        保存任务指令文件

        Args:
            project: 项目对象
            task: 任务对象
        """
        task_file = project.get_task_file_path(task.id)
        instruction_text = task.to_instruction_text()
        save_text(instruction_text, task_file)

        self.logger.debug(f"任务指令已保存: {task_file}")

    def get_project_dashboard(self, project: Project) -> str:
        """
        获取项目仪表板（摘要）

        Args:
            project: 项目对象

        Returns:
            仪表板文本
        """
        stats = project.task_queue.get_statistics()
        progress_percentage = (stats['completed'] / stats['total'] * 100) if stats['total'] > 0 else 0

        dashboard = f"""
╔══════════════════════════════════════════════════════════════╗
║                    项目仪表板                                 ║
╠══════════════════════════════════════════════════════════════╣
║ 项目名称: {project.name:<48} ║
║ 项目ID:   {project.project_id:<48} ║
║ 当前阶段: {project.phase.value:<48} ║
╠══════════════════════════════════════════════════════════════╣
║ 任务进度                                                      ║
║   总任务数:   {stats['total']:<3}                                          ║
║   已完成:     {stats['completed']:<3}  ({progress_percentage:>5.1f}%)                            ║
║   进行中:     {stats['in_progress']:<3}                                          ║
║   待执行:     {stats['pending']:<3}                                          ║
║   失败:       {stats['failed']:<3}                                          ║
║   阻塞:       {stats['blocked']:<3}                                          ║
╠══════════════════════════════════════════════════════════════╣
║ 工作区: {project.workspace_path:<46} ║
╚══════════════════════════════════════════════════════════════╝
"""
        return dashboard

    def list_projects(self) -> list:
        """
        列出所有项目

        Returns:
            项目ID列表
        """
        if not os.path.exists(self.workspace_root):
            return []

        projects = []
        for item in os.listdir(self.workspace_root):
            item_path = os.path.join(self.workspace_root, item)
            if os.path.isdir(item_path) and item.startswith("PRJ-"):
                projects.append(item)

        return projects
