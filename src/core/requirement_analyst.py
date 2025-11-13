"""
需求分析师
负责与用户交互，澄清和细化需求
"""
import uuid
from typing import List, Dict, Optional, Tuple
from ..models import Requirement, UserStory, RequirementPriority, RequirementStatus
from ..utils import app_logger


class RequirementAnalyst:
    """
    AI需求分析师
    负责引导用户完成需求澄清，生成结构化的PRD
    """

    def __init__(self):
        self.logger = app_logger
        self.current_requirement: Optional[Requirement] = None

    def start_analysis(self, project_name: str, high_level_goal: str) -> Requirement:
        """
        开始需求分析

        Args:
            project_name: 项目名称
            high_level_goal: 用户的高层目标

        Returns:
            初始化的需求对象
        """
        self.current_requirement = Requirement(
            project_name=project_name,
            high_level_goal=high_level_goal
        )

        self.logger.info(f"开始需求分析: {project_name}")
        self.logger.info(f"高层目标: {high_level_goal}")

        return self.current_requirement

    def generate_clarification_questions(self) -> List[str]:
        """
        生成澄清问题
        这是模拟AI PM思考并提问的过程

        Returns:
            需要向用户澄清的问题列表
        """
        if not self.current_requirement:
            return []

        # 基于高层目标，生成一系列澄清问题
        questions = []

        # 1. 项目范围问题
        questions.append("这个项目的主要用户群体是谁？（例如：个人用户、企业用户、开发者等）")

        # 2. 功能范围问题
        questions.append("请列出您认为最核心的3-5个功能（按优先级排序）")

        # 3. 技术约束问题
        questions.append("是否有特定的技术栈要求或偏好？（例如：Web应用、移动应用、桌面应用等）")

        # 4. 数据和存储问题
        questions.append("数据如何存储？（本地存储、云端同步、数据库等）")

        # 5. 部署和运行环境
        questions.append("应用将在什么环境中运行？（本地运行、云部署、容器化等）")

        # 6. 性能和规模要求
        questions.append("预期的用户规模和性能要求是什么？（小型个人项目 vs 企业级应用）")

        # 7. 集成和依赖
        questions.append("是否需要集成第三方服务或API？")

        return questions

    def record_answer(self, question: str, answer: str):
        """
        记录用户对澄清问题的回答

        Args:
            question: 问题
            answer: 用户的回答
        """
        if self.current_requirement:
            self.current_requirement.add_qa(question, answer)
            self.logger.info(f"记录回答: Q: {question[:50]}... A: {answer[:50]}...")

    def analyze_answers_and_generate_stories(self) -> List[UserStory]:
        """
        分析所有问答，生成用户故事

        这个方法需要"AI思考"，在实际使用中，这里应该是调用AI模型
        但由于我们是协作模式，这里我们提供一个基于规则的简化版本

        Returns:
            生成的用户故事列表
        """
        if not self.current_requirement:
            return []

        stories = []

        # 这里是简化的规则推断
        # 在真实场景中，这应该通过AI模型分析所有QA来生成
        qa_dict = {qa['question']: qa['answer'] for qa in self.current_requirement.clarification_qa}

        # 基于回答生成用户故事
        story_counter = 1

        # 示例：从"核心功能"回答中提取用户故事
        for question, answer in qa_dict.items():
            if "核心" in question and "功能" in question:
                # 尝试分解答案中的功能点
                features = [f.strip() for f in answer.split('，') if f.strip()]
                for idx, feature in enumerate(features[:5], 1):  # 最多5个
                    story = UserStory(
                        id=f"US-{story_counter:03d}",
                        title=feature,
                        description=f"作为用户，我希望能够{feature}",
                        priority=RequirementPriority.HIGH if idx <= 2 else RequirementPriority.MEDIUM,
                        acceptance_criteria=[
                            f"{feature}功能可以正常使用",
                            "界面友好易用",
                            "性能满足要求"
                        ]
                    )
                    stories.append(story)
                    story_counter += 1

        # 添加技术搭建相关的用户故事
        setup_story = UserStory(
            id=f"US-{story_counter:03d}",
            title="项目初始化与环境搭建",
            description="搭建项目基础架构和开发环境",
            priority=RequirementPriority.HIGH,
            acceptance_criteria=[
                "项目目录结构清晰",
                "依赖管理配置完成",
                "基础框架搭建完成"
            ]
        )
        stories.insert(0, setup_story)  # 放在最前面

        # 将生成的用户故事添加到需求中
        for story in stories:
            self.current_requirement.add_user_story(story)

        self.logger.info(f"生成了 {len(stories)} 个用户故事")

        return stories

    def infer_tech_stack(self) -> Dict[str, str]:
        """
        基于需求推断技术栈

        Returns:
            推荐的技术栈
        """
        if not self.current_requirement:
            return {}

        tech_stack = {}

        # 从QA中推断
        qa_dict = {qa['question']: qa['answer'].lower() for qa in self.current_requirement.clarification_qa}

        # 查找技术栈相关的回答
        for question, answer in qa_dict.items():
            if "技术栈" in question or "技术" in question:
                # 尝试识别关键词
                if "web" in answer or "网页" in answer or "浏览器" in answer:
                    tech_stack["frontend"] = "React/Vue.js"
                    tech_stack["backend"] = "Python Flask/FastAPI"
                elif "移动" in answer or "手机" in answer or "mobile" in answer:
                    tech_stack["mobile"] = "React Native 或 Flutter"
                elif "桌面" in answer or "desktop" in answer:
                    tech_stack["desktop"] = "Electron 或 Python Tkinter"
                elif "python" in answer:
                    tech_stack["language"] = "Python"
                elif "javascript" in answer or "js" in answer:
                    tech_stack["language"] = "JavaScript/TypeScript"

        # 默认推荐
        if not tech_stack:
            tech_stack = {
                "language": "Python",
                "reason": "Python适合快速原型开发，生态丰富"
            }

        # 数据库推荐
        for question, answer in qa_dict.items():
            if "存储" in question or "数据" in question:
                if "本地" in answer:
                    tech_stack["database"] = "SQLite（轻量级本地数据库）"
                elif "云" in answer or "远程" in answer:
                    tech_stack["database"] = "PostgreSQL 或 MySQL"
                else:
                    tech_stack["database"] = "SQLite"

        self.current_requirement.tech_stack = tech_stack
        self.logger.info(f"推断技术栈: {tech_stack}")

        return tech_stack

    def finalize_requirement(self) -> Requirement:
        """
        完成需求分析，生成最终的PRD

        Returns:
            完成的需求文档
        """
        if not self.current_requirement:
            raise ValueError("没有正在进行的需求分析")

        # 确保用户故事已生成
        if not self.current_requirement.user_stories:
            self.analyze_answers_and_generate_stories()

        # 确保技术栈已推断
        if not self.current_requirement.tech_stack:
            self.infer_tech_stack()

        self.logger.info("需求分析完成")
        self.logger.info(f"共 {len(self.current_requirement.user_stories)} 个用户故事")

        return self.current_requirement

    def interactive_analysis(self, project_name: str, high_level_goal: str) -> Requirement:
        """
        交互式需求分析流程
        这是主入口，模拟与用户的完整对话过程

        Args:
            project_name: 项目名称
            high_level_goal: 高层目标

        Returns:
            完成的需求文档
        """
        # 1. 开始分析
        self.start_analysis(project_name, high_level_goal)

        # 2. 生成问题
        questions = self.generate_clarification_questions()

        print("\n" + "="*80)
        print(f"🤖 AI项目经理: 你好！让我们一起来明确 '{project_name}' 的需求。")
        print(f"📋 你的目标: {high_level_goal}")
        print("="*80 + "\n")

        print("我需要问你几个问题来更好地理解需求：\n")

        # 3. 逐个提问并记录答案
        for i, question in enumerate(questions, 1):
            print(f"❓ 问题 {i}/{len(questions)}: {question}")
            answer = input("💬 你的回答: ").strip()

            if not answer:
                answer = "无特殊要求"

            self.record_answer(question, answer)
            print()

        # 4. 分析并生成用户故事
        print("\n" + "="*80)
        print("🔍 正在分析需求并生成用户故事...")
        print("="*80 + "\n")

        stories = self.analyze_answers_and_generate_stories()

        print(f"✅ 已生成 {len(stories)} 个用户故事：\n")
        for story in stories:
            print(f"  • [{story.priority.value.upper()}] {story.title}")

        # 5. 推断技术栈
        tech_stack = self.infer_tech_stack()
        print(f"\n📦 推荐技术栈：")
        for key, value in tech_stack.items():
            print(f"  • {key}: {value}")

        # 6. 完成
        requirement = self.finalize_requirement()

        print("\n" + "="*80)
        print("✨ 需求分析完成！")
        print("="*80 + "\n")

        return requirement
