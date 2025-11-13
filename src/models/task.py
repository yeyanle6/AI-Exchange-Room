"""
任务模型
定义开发任务的数据结构
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime
from enum import Enum


class TaskStatus(Enum):
    """任务状态"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"


class TaskType(Enum):
    """任务类型"""
    SETUP = "setup"  # 环境搭建
    IMPLEMENTATION = "implementation"  # 功能实现
    TESTING = "testing"  # 测试
    DEBUGGING = "debugging"  # 调试
    REFACTORING = "refactoring"  # 重构
    DOCUMENTATION = "documentation"  # 文档


@dataclass
class Task:
    """开发任务（工单）"""
    id: str
    title: str
    description: str
    task_type: TaskType
    status: TaskStatus = TaskStatus.PENDING

    # 上下文信息
    related_files: List[str] = field(default_factory=list)  # 相关文件路径
    dependencies: List[str] = field(default_factory=list)  # 依赖的其他任务ID
    context_summary: str = ""  # 上下文摘要

    # 执行信息
    acceptance_criteria: List[str] = field(default_factory=list)
    technical_notes: List[str] = field(default_factory=list)

    # 时间追踪
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    started_at: Optional[str] = None
    completed_at: Optional[str] = None

    # 执行结果
    output_files: List[str] = field(default_factory=list)  # 产出的文件
    execution_log: List[str] = field(default_factory=list)  # 执行日志
    error_message: Optional[str] = None

    def start(self):
        """开始任务"""
        self.status = TaskStatus.IN_PROGRESS
        self.started_at = datetime.now().isoformat()

    def complete(self, output_files: List[str] = None):
        """完成任务"""
        self.status = TaskStatus.COMPLETED
        self.completed_at = datetime.now().isoformat()
        if output_files:
            self.output_files.extend(output_files)

    def fail(self, error_message: str):
        """任务失败"""
        self.status = TaskStatus.FAILED
        self.error_message = error_message

    def block(self, reason: str):
        """任务阻塞"""
        self.status = TaskStatus.BLOCKED
        self.error_message = reason

    def add_log(self, message: str):
        """添加执行日志"""
        timestamp = datetime.now().isoformat()
        self.execution_log.append(f"[{timestamp}] {message}")

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "task_type": self.task_type.value,
            "status": self.status.value,
            "related_files": self.related_files,
            "dependencies": self.dependencies,
            "context_summary": self.context_summary,
            "acceptance_criteria": self.acceptance_criteria,
            "technical_notes": self.technical_notes,
            "created_at": self.created_at,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "output_files": self.output_files,
            "execution_log": self.execution_log,
            "error_message": self.error_message
        }

    def to_instruction_text(self) -> str:
        """
        转换为给AI程序员的指令文本
        这是"文本驱动"开发的关键：生成明确、可执行的指令
        """
        text = f"""# 开发任务: {self.title}

## 任务ID
{self.id}

## 任务类型
{self.task_type.value}

## 任务描述
{self.description}

## 上下文信息
{self.context_summary}

## 相关文件
"""
        if self.related_files:
            for file_path in self.related_files:
                text += f"- {file_path}\n"
        else:
            text += "无现有相关文件（这是新创建的模块）\n"

        if self.dependencies:
            text += f"\n## 依赖任务\n"
            text += f"本任务依赖以下任务完成:\n"
            for dep in self.dependencies:
                text += f"- {dep}\n"

        text += "\n## 验收标准\n"
        if self.acceptance_criteria:
            for i, criterion in enumerate(self.acceptance_criteria, 1):
                text += f"{i}. {criterion}\n"
        else:
            text += "无明确验收标准\n"

        if self.technical_notes:
            text += "\n## 技术要点\n"
            for note in self.technical_notes:
                text += f"- {note}\n"

        text += "\n## 期望产出\n"
        text += "请完成上述任务，并确保代码质量。如遇到问题，请记录详细的错误信息。\n"

        return text


@dataclass
class TaskQueue:
    """任务队列"""
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task):
        """添加任务"""
        self.tasks.append(task)

    def get_next_task(self) -> Optional[Task]:
        """获取下一个待执行的任务（考虑依赖关系）"""
        completed_task_ids = {t.id for t in self.tasks if t.status == TaskStatus.COMPLETED}

        for task in self.tasks:
            if task.status == TaskStatus.PENDING:
                # 检查依赖是否都已完成
                if all(dep in completed_task_ids for dep in task.dependencies):
                    return task
        return None

    def get_task_by_id(self, task_id: str) -> Optional[Task]:
        """根据ID获取任务"""
        for task in self.tasks:
            if task.id == task_id:
                return task
        return None

    def get_statistics(self) -> Dict:
        """获取任务统计"""
        stats = {
            "total": len(self.tasks),
            "pending": 0,
            "in_progress": 0,
            "completed": 0,
            "failed": 0,
            "blocked": 0
        }
        for task in self.tasks:
            stats[task.status.value] += 1
        return stats

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "tasks": [task.to_dict() for task in self.tasks],
            "statistics": self.get_statistics()
        }
