"""
多角色需求分析系统
模拟多个AI角色从不同角度分析需求
"""
from typing import List, Dict, Optional
from dataclasses import dataclass, field
from enum import Enum
from ..models import Requirement, UserStory, RequirementPriority
from ..utils import app_logger


class AgentRole(Enum):
    """AI角色类型"""
    PRODUCT_MANAGER = "产品经理"
    TECH_ARCHITECT = "技术架构师"
    UX_DESIGNER = "UX设计师"
    QA_ENGINEER = "测试工程师"
    DEVOPS_ENGINEER = "DevOps工程师"
    SECURITY_EXPERT = "安全专家"


@dataclass
class AgentPersona:
    """AI角色人设"""
    role: AgentRole
    name: str
    emoji: str
    focus_areas: List[str]
    prompt_template: str
    priority_weight: Dict[str, float] = field(default_factory=dict)


class AIAgent:
    """单个AI角色代理"""

    # 角色人设定义
    PERSONAS = {
        AgentRole.PRODUCT_MANAGER: AgentPersona(
            role=AgentRole.PRODUCT_MANAGER,
            name="Alex",
            emoji="👤",
            focus_areas=["用户价值", "商业目标", "市场需求", "功能优先级"],
            prompt_template="""你是一位经验丰富的产品经理Alex。

你的核心关注点：
- 用户价值和需求
- 商业目标和ROI
- 市场竞争力
- 功能优先级排序

你的工作风格：
- 数据驱动决策
- 关注用户痛点
- 平衡各方需求
- 务实且高效

当前任务：{task}
项目背景：{context}

请从产品经理的角度给出你的分析和建议：""",
            priority_weight={"business_value": 0.4, "user_impact": 0.4, "effort": 0.2}
        ),

        AgentRole.TECH_ARCHITECT: AgentPersona(
            role=AgentRole.TECH_ARCHITECT,
            name="Taylor",
            emoji="🏗️",
            focus_areas=["技术可行性", "系统架构", "性能优化", "技术债务"],
            prompt_template="""你是一位资深技术架构师Taylor。

你的核心关注点：
- 技术可行性评估
- 系统架构设计
- 性能和扩展性
- 技术选型
- 技术债务管理

你的工作风格：
- 深思熟虑
- 关注长期价值
- 平衡创新与稳定
- 注重代码质量

当前任务：{task}
项目背景：{context}

请从技术架构师的角度给出你的分析和建议：""",
            priority_weight={"technical_complexity": 0.5, "scalability": 0.3, "maintainability": 0.2}
        ),

        AgentRole.UX_DESIGNER: AgentPersona(
            role=AgentRole.UX_DESIGNER,
            name="Morgan",
            emoji="🎨",
            focus_areas=["用户体验", "交互设计", "易用性", "可访问性"],
            prompt_template="""你是一位创意十足的UX设计师Morgan。

你的核心关注点：
- 用户体验和满意度
- 交互设计的直观性
- 界面美观性
- 可访问性
- 用户旅程优化

你的工作风格：
- 以用户为中心
- 注重细节
- 追求简洁优雅
- 数据验证设计

当前任务：{task}
项目背景：{context}

请从UX设计师的角度给出你的分析和建议：""",
            priority_weight={"user_experience": 0.6, "usability": 0.3, "aesthetics": 0.1}
        ),

        AgentRole.QA_ENGINEER: AgentPersona(
            role=AgentRole.QA_ENGINEER,
            name="Quinn",
            emoji="🔍",
            focus_areas=["质量标准", "测试策略", "边界情况", "性能测试"],
            prompt_template="""你是一位严谨的测试工程师Quinn。

你的核心关注点：
- 质量标准和验收标准
- 测试策略和覆盖率
- 边界情况和异常处理
- 性能和压力测试
- 自动化测试

你的工作风格：
- 追求零缺陷
- 关注边界情况
- 预防性思维
- 系统性测试

当前任务：{task}
项目背景：{context}

请从测试工程师的角度给出你的分析和建议：""",
            priority_weight={"testability": 0.4, "quality_risk": 0.4, "test_coverage": 0.2}
        ),

        AgentRole.DEVOPS_ENGINEER: AgentPersona(
            role=AgentRole.DEVOPS_ENGINEER,
            name="Devon",
            emoji="⚙️",
            focus_areas=["部署策略", "CI/CD", "监控告警", "运维效率"],
            prompt_template="""你是一位高效的DevOps工程师Devon。

你的核心关注点：
- 部署策略和自动化
- CI/CD流程
- 监控和告警
- 系统可靠性
- 运维效率

你的工作风格：
- 自动化优先
- 关注稳定性
- 快速响应
- 持续改进

当前任务：{task}
项目背景：{context}

请从DevOps工程师的角度给出你的分析和建议：""",
            priority_weight={"deployability": 0.4, "reliability": 0.3, "automation": 0.3}
        ),

        AgentRole.SECURITY_EXPERT: AgentPersona(
            role=AgentRole.SECURITY_EXPERT,
            name="Sam",
            emoji="🔒",
            focus_areas=["安全漏洞", "数据保护", "合规性", "隐私保护"],
            prompt_template="""你是一位警惕的安全专家Sam。

你的核心关注点：
- 安全漏洞和威胁
- 数据保护和加密
- 合规性（GDPR等）
- 隐私保护
- 安全最佳实践

你的工作风格：
- 零信任原则
- 预防为主
- 深度防御
- 持续监控

当前任务：{task}
项目背景：{context}

请从安全专家的角度给出你的分析和建议：""",
            priority_weight={"security_risk": 0.6, "compliance": 0.3, "privacy": 0.1}
        )
    }

    def __init__(self, role: AgentRole):
        """
        初始化AI角色

        Args:
            role: 角色类型
        """
        self.persona = self.PERSONAS[role]
        self.role = role
        self.conversation_history: List[Dict] = []

    def analyze(self, task: str, context: Dict) -> str:
        """
        分析任务并给出建议

        Args:
            task: 任务描述
            context: 上下文信息

        Returns:
            分析结果
        """
        # 构建提示词
        prompt = self.persona.prompt_template.format(
            task=task,
            context=self._format_context(context)
        )

        # 在实际实现中，这里应该调用Claude API
        # 现在返回模拟的响应
        return self._simulate_response(task, context)

    def _format_context(self, context: Dict) -> str:
        """格式化上下文信息"""
        lines = []
        for key, value in context.items():
            lines.append(f"- {key}: {value}")
        return "\n".join(lines)

    def _simulate_response(self, task: str, context: Dict) -> str:
        """
        模拟角色响应（实际应该调用Claude API）

        这里提供一个基于规则的简化响应
        """
        responses = {
            AgentRole.PRODUCT_MANAGER: f"""
从产品角度分析：

**用户价值评估**
这个需求能够为用户带来{self._estimate_value(task)}的价值。

**优先级建议**
建议优先级：{self._suggest_priority(task)}

**关键问题**
1. 目标用户群体的具体画像是什么？
2. 核心使用场景是什么？
3. 成功指标如何定义？

**建议**
建议先从MVP（最小可行产品）开始，快速验证核心假设。
""",
            AgentRole.TECH_ARCHITECT: f"""
从技术架构角度分析：

**技术可行性**
{self._assess_feasibility(task)}

**架构建议**
推荐采用{self._suggest_architecture(context)}架构。

**技术栈推荐**
- 后端：Python FastAPI
- 数据库：PostgreSQL/SQLite
- 缓存：Redis（如需要）

**技术风险**
需要注意{self._identify_risks(task)}。
""",
            AgentRole.UX_DESIGNER: f"""
从用户体验角度分析：

**用户旅程**
用户的核心旅程应该是：进入 → 完成任务 → 获得反馈

**交互设计建议**
1. 保持界面简洁
2. 减少用户操作步骤
3. 提供即时反馈

**可访问性**
- 支持键盘导航
- 适配屏幕阅读器
- 提供高对比度模式

**体验优化**
建议添加引导流程，降低学习成本。
""",
            AgentRole.QA_ENGINEER: f"""
从测试角度分析：

**测试策略**
建议采用三层测试策略：
1. 单元测试（覆盖率 >80%）
2. 集成测试
3. 端到端测试

**测试重点**
需要重点测试：
- 边界条件
- 异常处理
- 并发场景
- 性能压力

**质量门禁**
- 所有测试通过
- 代码覆盖率达标
- 无高危漏洞

**建议**
建议在开发初期就引入TDD（测试驱动开发）。
""",
            AgentRole.DEVOPS_ENGINEER: f"""
从运维角度分析：

**部署策略**
推荐使用Docker容器化部署。

**CI/CD流程**
1. 代码提交 → 自动测试
2. 测试通过 → 构建镜像
3. 自动部署到测试环境
4. 手动确认 → 生产发布

**监控告警**
需要监控：
- 应用性能（响应时间）
- 错误率
- 资源使用率

**建议**
建议使用GitHub Actions实现自动化流程。
""",
            AgentRole.SECURITY_EXPERT: f"""
从安全角度分析：

**安全风险评估**
{self._assess_security_risks(task)}

**必须实施的安全措施**
1. 输入验证和清理
2. 身份认证和授权
3. 数据加密（传输和存储）
4. SQL注入防护
5. XSS防护

**合规性检查**
- 数据隐私保护
- 用户同意管理
- 数据保留策略

**安全建议**
建议进行安全代码审查和漏洞扫描。
"""
        }

        return responses.get(self.role, "暂无分析")

    def _estimate_value(self, task: str) -> str:
        """估算用户价值"""
        if "核心" in task or "重要" in task:
            return "高"
        elif "优化" in task or "改进" in task:
            return "中"
        else:
            return "中等"

    def _suggest_priority(self, task: str) -> str:
        """建议优先级"""
        if "核心" in task or "基础" in task:
            return "P0（高优先级）"
        else:
            return "P1（中优先级）"

    def _assess_feasibility(self, task: str) -> str:
        """评估技术可行性"""
        return "技术上可行，建议采用成熟的技术栈以降低风险"

    def _suggest_architecture(self, context: Dict) -> str:
        """建议架构"""
        return "前后端分离的微服务"

    def _identify_risks(self, task: str) -> str:
        """识别技术风险"""
        return "性能瓶颈和数据一致性"

    def _assess_security_risks(self, task: str) -> str:
        """评估安全风险"""
        return "中等风险，需要实施基本的安全防护措施"


class MultiAgentAnalyst:
    """
    多角色需求分析系统
    协调多个AI角色共同分析需求
    """

    def __init__(self, roles: Optional[List[AgentRole]] = None):
        """
        初始化多角色分析系统

        Args:
            roles: 要启用的角色列表，None表示启用所有角色
        """
        if roles is None:
            roles = list(AgentRole)

        self.agents: Dict[AgentRole, AIAgent] = {
            role: AIAgent(role) for role in roles
        }

        self.logger = app_logger
        self.discussion_history: List[Dict] = []

    def analyze_requirement(self, project_name: str, high_level_goal: str) -> Dict:
        """
        多角色分析需求

        Args:
            project_name: 项目名称
            high_level_goal: 高层目标

        Returns:
            分析结果字典
        """
        self.logger.info(f"开始多角色需求分析: {project_name}")

        context = {
            "项目名称": project_name,
            "高层目标": high_level_goal
        }

        # 第一轮：所有角色并行分析
        print("\n" + "="*70)
        print("🎭 多角色需求分析")
        print("="*70 + "\n")

        analyses = {}
        for role, agent in self.agents.items():
            print(f"{agent.persona.emoji} {agent.persona.name} ({role.value}) 正在分析...")

            task = f"请分析项目'{project_name}'的需求：{high_level_goal}"
            analysis = agent.analyze(task, context)
            analyses[role] = analysis

            print(f"\n{agent.persona.emoji} {agent.persona.name} 的分析：")
            print(analysis)
            print()

        # 第二轮：综合分析和讨论
        consensus = self._build_consensus(analyses, context)

        return {
            "individual_analyses": analyses,
            "consensus": consensus,
            "context": context
        }

    def _build_consensus(self, analyses: Dict[AgentRole, str], context: Dict) -> Dict:
        """
        构建共识

        Args:
            analyses: 各角色的分析结果
            context: 上下文信息

        Returns:
            共识结果
        """
        print("\n" + "="*70)
        print("🤝 形成共识")
        print("="*70 + "\n")

        # 提取关键点
        consensus = {
            "core_requirements": [],
            "technical_approach": "",
            "priorities": [],
            "risks": [],
            "next_steps": []
        }

        # 从产品经理的分析中提取核心需求
        if AgentRole.PRODUCT_MANAGER in analyses:
            consensus["core_requirements"].append("用户价值驱动")
            consensus["priorities"].append("优先实现核心功能")

        # 从架构师的分析中提取技术方案
        if AgentRole.TECH_ARCHITECT in analyses:
            consensus["technical_approach"] = "采用成熟技术栈，注重可扩展性"

        # 从测试的分析中提取质量要求
        if AgentRole.QA_ENGINEER in analyses:
            consensus["core_requirements"].append("高质量标准")
            consensus["risks"].append("测试覆盖率")

        # 从安全的分析中提取安全要求
        if AgentRole.SECURITY_EXPERT in analyses:
            consensus["core_requirements"].append("安全优先")
            consensus["risks"].append("安全漏洞")

        print("共识结论：")
        print(f"✓ 核心需求: {', '.join(consensus['core_requirements'])}")
        print(f"✓ 技术方案: {consensus['technical_approach']}")
        print(f"✓ 优先级: {', '.join(consensus['priorities'])}")
        print(f"✓ 风险点: {', '.join(consensus['risks'])}")
        print()

        return consensus

    def generate_clarification_questions(self) -> List[Dict]:
        """
        生成澄清问题（多角色视角）

        Returns:
            问题列表
        """
        questions = []

        for role, agent in self.agents.items():
            role_questions = self._generate_role_questions(agent)
            questions.extend(role_questions)

        return questions

    def _generate_role_questions(self, agent: AIAgent) -> List[Dict]:
        """
        生成特定角色的问题

        Args:
            agent: AI角色

        Returns:
            问题列表
        """
        # 基于角色的关注点生成问题
        questions = []

        role_specific_questions = {
            AgentRole.PRODUCT_MANAGER: [
                "主要用户群体的具体画像是什么？",
                "核心使用场景有哪些？",
                "成功的关键指标是什么？"
            ],
            AgentRole.TECH_ARCHITECT: [
                "预期的数据规模和并发量是多少？",
                "是否有特定的技术栈要求？",
                "是否需要考虑与现有系统的集成？"
            ],
            AgentRole.UX_DESIGNER: [
                "用户最常见的使用设备是什么？",
                "是否有品牌设计规范？",
                "目标用户的技术熟练度如何？"
            ],
            AgentRole.QA_ENGINEER: [
                "质量标准和验收标准是什么？",
                "是否有性能要求（响应时间等）？",
                "预期的稳定性要求是多少？"
            ],
            AgentRole.DEVOPS_ENGINEER: [
                "部署环境是什么？（云/本地）",
                "是否需要高可用部署？",
                "监控和日志有什么要求？"
            ],
            AgentRole.SECURITY_EXPERT: [
                "是否涉及敏感数据？",
                "有哪些合规性要求？",
                "用户认证方式的偏好？"
            ]
        }

        role_questions = role_specific_questions.get(agent.role, [])

        for q in role_questions:
            questions.append({
                "role": agent.role.value,
                "emoji": agent.persona.emoji,
                "question": q,
                "asker": agent.persona.name
            })

        return questions
