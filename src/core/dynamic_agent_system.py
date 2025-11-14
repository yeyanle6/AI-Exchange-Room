"""
动态多角色系统
根据项目类型和阶段自动选择和管理AI角色
"""
from typing import List, Dict, Set, Optional
from enum import Enum
from dataclasses import dataclass
from .multi_agent_analyst import AgentRole, AIAgent, MultiAgentAnalyst
from ..utils import app_logger


class ProjectType(Enum):
    """项目类型"""
    WEB_APP = "Web应用"
    MOBILE_APP = "移动应用"
    DESKTOP_APP = "桌面应用"
    CLI_TOOL = "命令行工具"
    LIBRARY = "库/框架"
    API_SERVICE = "API服务"
    DATA_ANALYSIS = "数据分析"
    AI_ML = "AI/机器学习"
    GAME = "游戏"
    EMBEDDED = "嵌入式系统"


class ProjectPhase(Enum):
    """项目阶段"""
    INCEPTION = "项目启动"
    REQUIREMENT = "需求分析"
    DESIGN = "设计阶段"
    IMPLEMENTATION = "开发实现"
    TESTING = "测试阶段"
    DEPLOYMENT = "部署上线"
    MAINTENANCE = "维护运营"


@dataclass
class RoleRequirement:
    """角色需求定义"""
    role: AgentRole
    required: bool = False  # 是否必需
    phases: Set[ProjectPhase] = None  # 适用的阶段
    project_types: Set[ProjectType] = None  # 适用的项目类型
    reason: str = ""  # 需要此角色的原因


class DynamicAgentSystem:
    """
    动态AI角色系统
    根据项目特征自动选择合适的AI角色
    """

    # 角色需求规则库
    ROLE_RULES = {
        AgentRole.PRODUCT_MANAGER: RoleRequirement(
            role=AgentRole.PRODUCT_MANAGER,
            required=True,  # 产品经理总是需要的
            phases={ProjectPhase.INCEPTION, ProjectPhase.REQUIREMENT, ProjectPhase.DESIGN},
            project_types=None,  # 所有项目类型
            reason="定义产品价值和用户需求"
        ),

        AgentRole.TECH_ARCHITECT: RoleRequirement(
            role=AgentRole.TECH_ARCHITECT,
            required=True,  # 架构师总是需要的
            phases={ProjectPhase.REQUIREMENT, ProjectPhase.DESIGN, ProjectPhase.IMPLEMENTATION},
            project_types=None,
            reason="设计技术架构和技术选型"
        ),

        AgentRole.UX_DESIGNER: RoleRequirement(
            role=AgentRole.UX_DESIGNER,
            required=False,
            phases={ProjectPhase.DESIGN, ProjectPhase.IMPLEMENTATION},
            project_types={
                ProjectType.WEB_APP,
                ProjectType.MOBILE_APP,
                ProjectType.DESKTOP_APP,
                ProjectType.GAME
            },
            reason="有用户界面的项目需要UX设计"
        ),

        AgentRole.QA_ENGINEER: RoleRequirement(
            role=AgentRole.QA_ENGINEER,
            required=False,
            phases={ProjectPhase.DESIGN, ProjectPhase.IMPLEMENTATION, ProjectPhase.TESTING},
            project_types=None,  # 所有项目都建议有测试
            reason="确保代码质量和测试覆盖"
        ),

        AgentRole.DEVOPS_ENGINEER: RoleRequirement(
            role=AgentRole.DEVOPS_ENGINEER,
            required=False,
            phases={ProjectPhase.IMPLEMENTATION, ProjectPhase.DEPLOYMENT, ProjectPhase.MAINTENANCE},
            project_types={
                ProjectType.WEB_APP,
                ProjectType.MOBILE_APP,
                ProjectType.API_SERVICE
            },
            reason="需要部署和运维的项目"
        ),

        AgentRole.SECURITY_EXPERT: RoleRequirement(
            role=AgentRole.SECURITY_EXPERT,
            required=False,
            phases={ProjectPhase.DESIGN, ProjectPhase.IMPLEMENTATION, ProjectPhase.TESTING},
            project_types={
                ProjectType.WEB_APP,
                ProjectType.API_SERVICE
            },
            reason="涉及用户数据或网络访问的项目"
        )
    }

    def __init__(self):
        self.logger = app_logger
        self.active_roles: Set[AgentRole] = set()
        self.project_type: Optional[ProjectType] = None
        self.current_phase: Optional[ProjectPhase] = None

    def analyze_project_needs(self, project_description: str,
                             project_type: Optional[ProjectType] = None) -> Dict:
        """
        分析项目并推荐需要的角色

        Args:
            project_description: 项目描述
            project_type: 项目类型（可选，会自动推断）

        Returns:
            分析结果
        """
        # 如果没有指定项目类型，尝试推断
        if not project_type:
            project_type = self._infer_project_type(project_description)

        self.project_type = project_type

        # 推荐角色
        recommended_roles = self._recommend_roles(project_type, project_description)

        return {
            "project_type": project_type.value,
            "recommended_roles": recommended_roles,
            "analysis": self._explain_role_selection(recommended_roles)
        }

    def _infer_project_type(self, description: str) -> ProjectType:
        """推断项目类型"""
        description_lower = description.lower()

        # 关键词映射
        type_keywords = {
            ProjectType.WEB_APP: ["web", "网站", "网页", "浏览器", "前端", "后端"],
            ProjectType.MOBILE_APP: ["移动", "手机", "ios", "android", "app"],
            ProjectType.DESKTOP_APP: ["桌面", "客户端", "qt", "gui"],
            ProjectType.CLI_TOOL: ["命令行", "cli", "终端", "脚本"],
            ProjectType.LIBRARY: ["库", "框架", "sdk", "package"],
            ProjectType.API_SERVICE: ["api", "接口", "服务", "微服务"],
            ProjectType.DATA_ANALYSIS: ["数据分析", "可视化", "报表", "统计"],
            ProjectType.AI_ML: ["ai", "机器学习", "深度学习", "模型", "训练"],
            ProjectType.GAME: ["游戏", "game"],
            ProjectType.EMBEDDED: ["嵌入式", "硬件", "单片机"]
        }

        # 计算匹配分数
        scores = {}
        for ptype, keywords in type_keywords.items():
            score = sum(1 for kw in keywords if kw in description_lower)
            if score > 0:
                scores[ptype] = score

        # 返回得分最高的类型
        if scores:
            return max(scores.items(), key=lambda x: x[1])[0]
        else:
            # 默认为Web应用
            return ProjectType.WEB_APP

    def _recommend_roles(self, project_type: ProjectType,
                        description: str) -> List[Dict]:
        """
        推荐角色

        Args:
            project_type: 项目类型
            description: 项目描述

        Returns:
            推荐的角色列表
        """
        recommended = []

        for role, rule in self.ROLE_RULES.items():
            # 检查是否必需
            if rule.required:
                recommended.append({
                    "role": role,
                    "priority": "必需",
                    "reason": rule.reason
                })
                continue

            # 检查项目类型匹配
            if rule.project_types is not None:
                if project_type not in rule.project_types:
                    continue

            # 检查描述中的特殊需求
            if self._has_special_need(role, description):
                recommended.append({
                    "role": role,
                    "priority": "推荐",
                    "reason": self._get_special_reason(role, description)
                })
                continue

            # 可选角色
            recommended.append({
                "role": role,
                "priority": "可选",
                "reason": rule.reason
            })

        return recommended

    def _has_special_need(self, role: AgentRole, description: str) -> bool:
        """检查是否有特殊需求需要此角色"""
        description_lower = description.lower()

        special_needs = {
            AgentRole.SECURITY_EXPERT: ["安全", "加密", "认证", "授权", "隐私"],
            AgentRole.DEVOPS_ENGINEER: ["部署", "运维", "ci/cd", "docker", "kubernetes"],
            AgentRole.QA_ENGINEER: ["测试", "质量", "稳定"],
            AgentRole.UX_DESIGNER: ["界面", "ui", "ux", "用户体验", "交互"]
        }

        keywords = special_needs.get(role, [])
        return any(kw in description_lower for kw in keywords)

    def _get_special_reason(self, role: AgentRole, description: str) -> str:
        """获取特殊需求的原因"""
        return f"项目描述中提到了相关需求，建议引入{role.value}"

    def _explain_role_selection(self, recommended_roles: List[Dict]) -> str:
        """解释角色选择"""
        lines = ["根据项目分析，建议以下角色配置：\n"]

        # 按优先级分组
        by_priority = {"必需": [], "推荐": [], "可选": []}
        for r in recommended_roles:
            by_priority[r["priority"]].append(r)

        for priority in ["必需", "推荐", "可选"]:
            roles = by_priority[priority]
            if roles:
                lines.append(f"\n{priority}角色：")
                for r in roles:
                    agent = AIAgent(r["role"])
                    lines.append(f"  {agent.persona.emoji} {r['role'].value} - {r['reason']}")

        return "\n".join(lines)

    def select_roles_for_phase(self, phase: ProjectPhase) -> List[AgentRole]:
        """
        为特定阶段选择角色

        Args:
            phase: 项目阶段

        Returns:
            适用的角色列表
        """
        self.current_phase = phase
        roles = []

        for role, rule in self.ROLE_RULES.items():
            # 检查阶段匹配
            if rule.phases is None or phase in rule.phases:
                # 检查项目类型匹配
                if rule.project_types is None or self.project_type in rule.project_types:
                    roles.append(role)

        self.logger.info(f"阶段 {phase.value} 选择角色: {[r.value for r in roles]}")
        return roles

    def create_phase_team(self, phase: ProjectPhase) -> MultiAgentAnalyst:
        """
        为特定阶段创建AI团队

        Args:
            phase: 项目阶段

        Returns:
            配置好的多角色分析系统
        """
        roles = self.select_roles_for_phase(phase)
        return MultiAgentAnalyst(roles=roles)


class ProjectLifecycleManager:
    """
    项目生命周期管理器
    管理不同阶段的角色切换
    """

    def __init__(self, project_type: ProjectType):
        self.project_type = project_type
        self.dynamic_system = DynamicAgentSystem()
        self.dynamic_system.project_type = project_type
        self.phase_history: List[Dict] = []

    def execute_phase(self, phase: ProjectPhase, task_description: str) -> Dict:
        """
        执行项目阶段

        Args:
            phase: 项目阶段
            task_description: 阶段任务描述

        Returns:
            执行结果
        """
        print(f"\n{'='*70}")
        print(f"📍 进入阶段: {phase.value}")
        print(f"{'='*70}\n")

        # 为当前阶段组建团队
        team = self.dynamic_system.create_phase_team(phase)
        active_roles = self.dynamic_system.select_roles_for_phase(phase)

        print(f"🎭 本阶段参与角色：")
        for role in active_roles:
            agent = AIAgent(role)
            print(f"  {agent.persona.emoji} {agent.persona.name} ({role.value})")
        print()

        # 执行分析
        result = team.analyze_requirement(
            project_name=f"{self.project_type.value} - {phase.value}",
            high_level_goal=task_description
        )

        # 记录历史
        self.phase_history.append({
            "phase": phase,
            "roles": active_roles,
            "result": result
        })

        return result

    def get_phase_summary(self) -> str:
        """获取项目各阶段总结"""
        lines = ["\n" + "="*70]
        lines.append("📊 项目阶段总结")
        lines.append("="*70 + "\n")

        for record in self.phase_history:
            lines.append(f"阶段: {record['phase'].value}")
            lines.append(f"参与角色: {', '.join(r.value for r in record['roles'])}")
            lines.append("")

        return "\n".join(lines)
