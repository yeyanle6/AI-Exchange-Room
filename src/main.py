#!/usr/bin/env python3
"""
AI-Exchange-Room 主入口
AI驱动的自动编程系统
"""
import sys
import os
import argparse
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core import ProjectManager
from src.models import ProjectPhase
from src.utils import app_logger


def print_banner():
    """打印欢迎横幅"""
    banner = """
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║              🤖 AI-Exchange-Room v0.1                            ║
║                                                                  ║
║          AI驱动的自动编程系统                                      ║
║          From Requirements to Code, Automatically                ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
"""
    print(banner)


def create_new_project_interactive():
    """交互式创建新项目"""
    print("\n📦 创建新项目\n")
    print("让我们开始一个全新的软件项目！")
    print("-" * 70)

    # 获取项目名称
    project_name = input("\n项目名称: ").strip()
    while not project_name:
        print("  ⚠️  项目名称不能为空")
        project_name = input("项目名称: ").strip()

    # 获取高层目标
    print(f"\n很好！现在请描述一下'{project_name}'的高层目标。")
    print("例如: '我想创建一个待办事项应用，可以添加、删除和标记任务'")
    high_level_goal = input("\n高层目标: ").strip()
    while not high_level_goal:
        print("  ⚠️  请描述您的项目目标")
        high_level_goal = input("高层目标: ").strip()

    return project_name, high_level_goal


def run_project_lifecycle():
    """运行完整的项目生命周期"""
    print_banner()

    # 创建项目管理器
    pm = ProjectManager()

    # 阶段1: 创建项目
    project_name, high_level_goal = create_new_project_interactive()
    project = pm.create_new_project(project_name, high_level_goal)

    print(f"\n✅ 项目已创建！")
    print(f"   项目ID: {project.project_id}")
    print(f"   工作区: {project.workspace_path}\n")

    # 阶段2: 需求分析
    print("\n" + "="*70)
    print("📋 阶段 1/3: 需求分析")
    print("="*70)

    try:
        project = pm.run_requirement_analysis(project, interactive=True)

        # 显示PRD保存位置
        print(f"\n📄 需求文档已保存至: {project.get_prd_path()}")

    except KeyboardInterrupt:
        print("\n\n⚠️  需求分析被中断")
        print(f"项目状态已保存至: {project.workspace_path}")
        return

    # 阶段3: 任务规划
    print("\n" + "="*70)
    print("📝 阶段 2/3: 任务规划")
    print("="*70)

    try:
        project = pm.run_task_planning(project)

        # 显示任务摘要
        print(f"\n📊 任务摘要已保存至: {os.path.join(project.docs_path, 'TASKS_SUMMARY.md')}")

        # 显示仪表板
        print(pm.get_project_dashboard(project))

    except Exception as e:
        print(f"\n❌ 任务规划失败: {e}")
        return

    # 阶段4: 任务执行引导
    print("\n" + "="*70)
    print("⚙️  阶段 3/3: 任务执行")
    print("="*70)

    print(f"""
现在，所有任务已经准备就绪！

任务文件位置: {project.workspace_path}/.ai_tasks/

下一步操作:
1. 查看任务摘要: {os.path.join(project.docs_path, 'TASKS_SUMMARY.md')}
2. 逐个执行任务（您可以手动执行，或者使用AI助手如Claude Code）

对于每个任务：
  - 任务指令在: {project.workspace_path}/.ai_tasks/[TASK-ID].md
  - 阅读任务描述和验收标准
  - 实现功能
  - 将代码保存到: {project.src_path}/

您可以重新运行此程序来查看项目状态。

项目ID: {project.project_id}
""")

    print("\n" + "="*70)
    print("✨ 项目初始化完成！祝您开发顺利！")
    print("="*70 + "\n")


def list_projects():
    """列出所有项目"""
    pm = ProjectManager()
    projects = pm.list_projects()

    if not projects:
        print("没有找到任何项目。")
        print("使用 'python src/main.py' 创建新项目。")
        return

    print(f"\n找到 {len(projects)} 个项目:\n")
    for project_id in projects:
        print(f"  • {project_id}")


def show_project_status(project_id: str):
    """显示项目状态"""
    pm = ProjectManager()
    project = pm.load_project(project_id)

    if not project:
        print(f"项目不存在: {project_id}")
        return

    print(pm.get_project_dashboard(project))


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="AI-Exchange-Room: AI驱动的自动编程系统",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  创建新项目（交互式）:
    python src/main.py

  列出所有项目:
    python src/main.py --list

  查看项目状态:
    python src/main.py --status PRJ-ABC12345
        """
    )

    parser.add_argument(
        '--list',
        action='store_true',
        help='列出所有项目'
    )

    parser.add_argument(
        '--status',
        metavar='PROJECT_ID',
        help='显示项目状态'
    )

    parser.add_argument(
        '--new-project',
        metavar='GOAL',
        help='快速创建新项目（非交互式）'
    )

    args = parser.parse_args()

    # 根据参数执行不同操作
    if args.list:
        list_projects()
    elif args.status:
        show_project_status(args.status)
    elif args.new_project:
        print("快速创建模式暂未实现，请使用交互式模式。")
    else:
        # 默认：交互式创建新项目
        try:
            run_project_lifecycle()
        except KeyboardInterrupt:
            print("\n\n👋 再见！")
        except Exception as e:
            app_logger.error(f"发生错误: {e}", exc_info=True)
            print(f"\n❌ 发生错误: {e}")
            sys.exit(1)


if __name__ == "__main__":
    main()
