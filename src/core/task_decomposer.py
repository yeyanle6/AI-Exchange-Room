"""
任务分解器
将用户故事分解为可执行的开发任务
"""
import uuid
from typing import List, Dict
from ..models import Requirement, UserStory, Task, TaskType, TaskQueue
from ..utils import app_logger


class TaskDecomposer:
    """
    AI任务分解器
    负责将高层的用户故事分解为具体的、可执行的开发任务
    """

    def __init__(self):
        self.logger = app_logger

    def decompose_user_story(self, story: UserStory, project_context: Dict = None) -> List[Task]:
        """
        将一个用户故事分解为多个开发任务

        Args:
            story: 用户故事
            project_context: 项目上下文信息（如技术栈、现有文件等）

        Returns:
            任务列表
        """
        tasks = []
        tech_stack = project_context.get('tech_stack', {}) if project_context else {}

        # 特殊处理：项目初始化任务
        if "初始化" in story.title or "搭建" in story.title:
            tasks.extend(self._create_setup_tasks(story, tech_stack))
        else:
            # 通用功能实现任务分解
            tasks.extend(self._create_feature_tasks(story, tech_stack))

        self.logger.info(f"用户故事 '{story.title}' 分解为 {len(tasks)} 个任务")

        return tasks

    def _create_setup_tasks(self, story: UserStory, tech_stack: Dict) -> List[Task]:
        """
        创建项目初始化相关的任务

        Args:
            story: 用户故事
            tech_stack: 技术栈

        Returns:
            初始化任务列表
        """
        tasks = []

        # 任务1: 创建项目结构
        task1 = Task(
            id=self._generate_task_id(),
            title="创建项目目录结构",
            description="""
创建标准的项目目录结构：
- src/：源代码目录
- tests/：测试目录
- docs/：文档目录
- config/：配置文件目录
- README.md：项目说明文档
""",
            task_type=TaskType.SETUP,
            context_summary=f"这是新项目，技术栈：{tech_stack}",
            acceptance_criteria=[
                "项目目录结构清晰规范",
                "README.md包含项目基本信息",
                "所有必要的目录已创建"
            ],
            technical_notes=[
                "遵循行业最佳实践",
                "确保目录结构可扩展"
            ]
        )
        tasks.append(task1)

        # 任务2: 配置依赖管理
        language = tech_stack.get('language', 'Python')
        if 'python' in language.lower():
            task2 = Task(
                id=self._generate_task_id(),
                title="配置Python项目依赖",
                description="""
创建Python项目的依赖管理文件：
- requirements.txt：列出项目依赖
- setup.py 或 pyproject.toml：项目配置
- .gitignore：Git忽略文件配置
""",
                task_type=TaskType.SETUP,
                dependencies=[task1.id],
                context_summary="Python项目依赖配置",
                acceptance_criteria=[
                    "requirements.txt文件存在且格式正确",
                    ".gitignore配置适合Python项目",
                    "可以通过pip安装依赖"
                ],
                technical_notes=[
                    "包含常用的Python开发依赖",
                    "考虑使用虚拟环境"
                ]
            )
            tasks.append(task2)

        # 任务3: 创建主入口文件
        task3 = Task(
            id=self._generate_task_id(),
            title="创建应用主入口",
            description=f"""
创建应用的主入口文件：
- 如果是Python：src/main.py
- 包含基本的程序结构
- 添加必要的导入和初始化代码
""",
            task_type=TaskType.IMPLEMENTATION,
            dependencies=[task1.id],
            context_summary="应用主入口文件",
            acceptance_criteria=[
                "主入口文件可以成功运行",
                "包含基本的错误处理",
                "代码结构清晰"
            ]
        )
        tasks.append(task3)

        return tasks

    def _create_feature_tasks(self, story: UserStory, tech_stack: Dict) -> List[Task]:
        """
        创建功能实现相关的任务

        Args:
            story: 用户故事
            tech_stack: 技术栈

        Returns:
            功能实现任务列表
        """
        tasks = []

        # 任务1: 设计数据模型（如果需要）
        if self._needs_data_model(story):
            task1 = Task(
                id=self._generate_task_id(),
                title=f"设计数据模型: {story.title}",
                description=f"""
为功能 '{story.title}' 设计和实现数据模型：
- 定义必要的数据结构
- 创建数据模型类
- 实现数据验证逻辑

用户故事描述：{story.description}
""",
                task_type=TaskType.IMPLEMENTATION,
                context_summary=f"功能: {story.title}",
                acceptance_criteria=[
                    "数据模型定义清晰",
                    "字段类型正确",
                    "包含必要的验证"
                ],
                technical_notes=[
                    "考虑数据的持久化需求",
                    "遵循项目的数据模型规范"
                ]
            )
            tasks.append(task1)

        # 任务2: 实现核心逻辑
        task2_id = self._generate_task_id()
        task2 = Task(
            id=task2_id,
            title=f"实现核心功能: {story.title}",
            description=f"""
实现功能 '{story.title}' 的核心业务逻辑：

用户故事：{story.description}

验收标准：
{chr(10).join('- ' + criterion for criterion in story.acceptance_criteria)}

请创建必要的函数/类来实现此功能。
""",
            task_type=TaskType.IMPLEMENTATION,
            dependencies=[tasks[0].id] if tasks else [],
            context_summary=f"功能: {story.title}, 优先级: {story.priority.value}",
            acceptance_criteria=story.acceptance_criteria,
            technical_notes=[
                "确保代码可测试",
                "添加必要的错误处理",
                "遵循项目代码规范"
            ]
        )
        tasks.append(task2)

        # 任务3: 创建用户界面（如果需要）
        if self._needs_ui(story):
            task3 = Task(
                id=self._generate_task_id(),
                title=f"创建用户界面: {story.title}",
                description=f"""
为功能 '{story.title}' 创建用户界面：
- 设计界面布局
- 实现用户交互
- 连接后端逻辑

用户故事：{story.description}
""",
                task_type=TaskType.IMPLEMENTATION,
                dependencies=[task2_id],
                context_summary=f"UI for {story.title}",
                acceptance_criteria=[
                    "界面布局合理美观",
                    "交互流畅",
                    "与后端逻辑正确集成"
                ]
            )
            tasks.append(task3)

        # 任务4: 编写单元测试
        task4 = Task(
            id=self._generate_task_id(),
            title=f"编写单元测试: {story.title}",
            description=f"""
为功能 '{story.title}' 编写单元测试：
- 测试核心功能的各种场景
- 测试边界条件
- 测试错误处理

确保测试覆盖率达到80%以上。
""",
            task_type=TaskType.TESTING,
            dependencies=[task2_id],
            context_summary=f"测试 {story.title}",
            acceptance_criteria=[
                "所有测试通过",
                "测试覆盖主要场景",
                "包含边界条件测试"
            ],
            technical_notes=[
                "使用项目的测试框架",
                "测试应该是独立可运行的"
            ]
        )
        tasks.append(task4)

        return tasks

    def _needs_data_model(self, story: UserStory) -> bool:
        """判断是否需要数据模型"""
        keywords = ['数据', '存储', '记录', '保存', '查询', '列表', '管理']
        return any(keyword in story.title or keyword in story.description for keyword in keywords)

    def _needs_ui(self, story: UserStory) -> bool:
        """判断是否需要用户界面"""
        keywords = ['界面', '显示', '查看', '展示', 'UI', '页面', '窗口']
        # 如果是纯后端或API任务，不需要UI
        backend_keywords = ['API', '接口', '服务', '后端', 'backend']

        has_ui_keyword = any(keyword in story.title or keyword in story.description for keyword in keywords)
        is_backend_only = any(keyword in story.title or keyword in story.description for keyword in backend_keywords)

        return has_ui_keyword and not is_backend_only

    def _generate_task_id(self) -> str:
        """生成任务ID"""
        return f"TASK-{uuid.uuid4().hex[:8].upper()}"

    def decompose_requirement(self, requirement: Requirement) -> TaskQueue:
        """
        将整个需求文档分解为任务队列

        Args:
            requirement: 需求文档

        Returns:
            任务队列
        """
        task_queue = TaskQueue()

        project_context = {
            'tech_stack': requirement.tech_stack,
            'project_name': requirement.project_name
        }

        self.logger.info(f"开始分解需求，共 {len(requirement.user_stories)} 个用户故事")

        # 按优先级排序用户故事
        sorted_stories = sorted(
            requirement.user_stories,
            key=lambda s: (
                0 if "初始化" in s.title or "搭建" in s.title else 1,  # 初始化任务优先
                s.priority.value  # 然后按优先级
            )
        )

        # 分解每个用户故事
        for story in sorted_stories:
            tasks = self.decompose_user_story(story, project_context)
            for task in tasks:
                task_queue.add_task(task)

        stats = task_queue.get_statistics()
        self.logger.info(f"任务分解完成，共生成 {stats['total']} 个任务")

        return task_queue

    def generate_task_summary(self, task_queue: TaskQueue) -> str:
        """
        生成任务队列的摘要报告

        Args:
            task_queue: 任务队列

        Returns:
            摘要文本
        """
        stats = task_queue.get_statistics()

        summary = f"""
# 任务分解报告

## 任务统计
- 总任务数: {stats['total']}
- 待执行: {stats['pending']}
- 进行中: {stats['in_progress']}
- 已完成: {stats['completed']}
- 失败: {stats['failed']}
- 阻塞: {stats['blocked']}

## 任务列表

"""

        # 按类型分组
        tasks_by_type = {}
        for task in task_queue.tasks:
            task_type = task.task_type.value
            if task_type not in tasks_by_type:
                tasks_by_type[task_type] = []
            tasks_by_type[task_type].append(task)

        for task_type, tasks in tasks_by_type.items():
            summary += f"\n### {task_type.upper()} ({len(tasks)} 个任务)\n\n"
            for task in tasks:
                summary += f"- **[{task.id}]** {task.title}\n"
                if task.dependencies:
                    summary += f"  - 依赖: {', '.join(task.dependencies)}\n"

        return summary
