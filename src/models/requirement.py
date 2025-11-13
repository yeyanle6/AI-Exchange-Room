"""
需求模型
定义项目需求的数据结构
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime
from enum import Enum


class RequirementStatus(Enum):
    """需求状态"""
    DRAFT = "draft"  # 草稿
    CLARIFYING = "clarifying"  # 澄清中
    CONFIRMED = "confirmed"  # 已确认
    REFINED = "refined"  # 已细化


class RequirementPriority(Enum):
    """需求优先级"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class UserStory:
    """用户故事"""
    id: str
    title: str
    description: str
    acceptance_criteria: List[str] = field(default_factory=list)
    priority: RequirementPriority = RequirementPriority.MEDIUM
    status: RequirementStatus = RequirementStatus.DRAFT

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "acceptance_criteria": self.acceptance_criteria,
            "priority": self.priority.value,
            "status": self.status.value
        }


@dataclass
class Requirement:
    """需求文档"""
    project_name: str
    high_level_goal: str  # 用户的高层目标
    clarification_qa: List[Dict[str, str]] = field(default_factory=list)  # 澄清问答记录
    user_stories: List[UserStory] = field(default_factory=list)
    tech_stack: Dict[str, str] = field(default_factory=dict)  # 技术栈选型
    constraints: List[str] = field(default_factory=list)  # 约束条件
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    version: str = "1.0"

    def add_qa(self, question: str, answer: str):
        """添加澄清问答"""
        self.clarification_qa.append({
            "question": question,
            "answer": answer,
            "timestamp": datetime.now().isoformat()
        })
        self.updated_at = datetime.now().isoformat()

    def add_user_story(self, story: UserStory):
        """添加用户故事"""
        self.user_stories.append(story)
        self.updated_at = datetime.now().isoformat()

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "project_name": self.project_name,
            "high_level_goal": self.high_level_goal,
            "clarification_qa": self.clarification_qa,
            "user_stories": [story.to_dict() for story in self.user_stories],
            "tech_stack": self.tech_stack,
            "constraints": self.constraints,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "version": self.version
        }

    def to_text(self) -> str:
        """转换为人类可读的文本格式（这是"文本驱动"的核心）"""
        text = f"""# 项目需求规格文档 (PRD)

## 项目名称
{self.project_name}

## 高层目标
{self.high_level_goal}

## 需求澄清记录
"""
        for i, qa in enumerate(self.clarification_qa, 1):
            text += f"\n### Q{i}: {qa['question']}\n"
            text += f"**A**: {qa['answer']}\n"

        text += "\n## 用户故事\n"
        for i, story in enumerate(self.user_stories, 1):
            text += f"\n### US-{i}: {story.title}\n"
            text += f"**描述**: {story.description}\n"
            text += f"**优先级**: {story.priority.value}\n"
            if story.acceptance_criteria:
                text += "**验收标准**:\n"
                for criterion in story.acceptance_criteria:
                    text += f"- {criterion}\n"

        text += "\n## 技术栈\n"
        for category, tech in self.tech_stack.items():
            text += f"- **{category}**: {tech}\n"

        if self.constraints:
            text += "\n## 约束条件\n"
            for constraint in self.constraints:
                text += f"- {constraint}\n"

        text += f"\n---\n*文档版本: {self.version}*\n"
        text += f"*最后更新: {self.updated_at}*\n"

        return text
