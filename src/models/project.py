"""
项目模型
管理整个项目的生命周期
"""
from dataclasses import dataclass, field
from typing import Optional, Dict
from datetime import datetime
from enum import Enum
import os

from .requirement import Requirement
from .task import TaskQueue


class ProjectPhase(Enum):
    """项目阶段"""
    INITIALIZATION = "initialization"  # 初始化
    REQUIREMENT_ANALYSIS = "requirement_analysis"  # 需求分析
    TASK_PLANNING = "task_planning"  # 任务规划
    DEVELOPMENT = "development"  # 开发中
    TESTING = "testing"  # 测试
    COMPLETED = "completed"  # 已完成
    ARCHIVED = "archived"  # 已归档


@dataclass
class Project:
    """项目"""
    name: str
    project_id: str
    workspace_path: str  # 项目工作区路径

    requirement: Optional[Requirement] = None
    task_queue: TaskQueue = field(default_factory=TaskQueue)

    phase: ProjectPhase = ProjectPhase.INITIALIZATION
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())

    metadata: Dict = field(default_factory=dict)  # 元数据

    def __post_init__(self):
        """初始化后处理"""
        # 确保工作区目录存在
        os.makedirs(self.workspace_path, exist_ok=True)

        # 创建项目子目录
        self.docs_path = os.path.join(self.workspace_path, "docs")
        self.src_path = os.path.join(self.workspace_path, "src")
        self.tasks_path = os.path.join(self.workspace_path, ".ai_tasks")

        for path in [self.docs_path, self.src_path, self.tasks_path]:
            os.makedirs(path, exist_ok=True)

    def update_phase(self, new_phase: ProjectPhase):
        """更新项目阶段"""
        self.phase = new_phase
        self.updated_at = datetime.now().isoformat()

    def get_prd_path(self) -> str:
        """获取PRD文档路径"""
        return os.path.join(self.docs_path, "PRD.md")

    def get_task_file_path(self, task_id: str) -> str:
        """获取任务指令文件路径"""
        return os.path.join(self.tasks_path, f"{task_id}.md")

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "name": self.name,
            "project_id": self.project_id,
            "workspace_path": self.workspace_path,
            "requirement": self.requirement.to_dict() if self.requirement else None,
            "task_queue": self.task_queue.to_dict(),
            "phase": self.phase.value,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "metadata": self.metadata
        }

    def get_summary(self) -> str:
        """获取项目摘要"""
        task_stats = self.task_queue.get_statistics()
        return f"""
项目: {self.name} (ID: {self.project_id})
阶段: {self.phase.value}
工作区: {self.workspace_path}
任务统计: {task_stats['completed']}/{task_stats['total']} 已完成
创建时间: {self.created_at}
"""
