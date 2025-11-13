#!/usr/bin/env python3
"""
基本功能测试脚本
测试核心组件是否正常工作
"""
import sys
from pathlib import Path

# 添加src到路径
sys.path.insert(0, str(Path(__file__).parent))

from src.core import ProjectManager
from src.models import RequirementPriority


def test_project_creation():
    """测试项目创建"""
    print("测试1: 项目创建...")

    pm = ProjectManager(workspace_root="./test_projects")
    project = pm.create_new_project(
        project_name="测试待办事项应用",
        high_level_goal="创建一个简单的待办事项CLI应用，可以添加、查看和删除任务"
    )

    assert project is not None
    assert project.name == "测试待办事项应用"
    assert project.project_id.startswith("PRJ-")

    print(f"  ✅ 项目创建成功: {project.project_id}")
    print(f"     工作区: {project.workspace_path}")

    return project


def test_requirement_analysis(project):
    """测试需求分析（非交互式）"""
    print("\n测试2: 需求分析...")

    pm = ProjectManager(workspace_root="./test_projects")

    # 准备自动回答
    auto_answers = {
        "这个项目的主要用户群体是谁？（例如：个人用户、企业用户、开发者等）": "个人用户",
        "请列出您认为最核心的3-5个功能（按优先级排序）": "添加任务，查看任务列表，删除任务，标记任务完成",
        "是否有特定的技术栈要求或偏好？（例如：Web应用、移动应用、桌面应用等）": "Python CLI应用",
        "数据如何存储？（本地存储、云端同步、数据库等）": "本地JSON文件存储",
        "应用将在什么环境中运行？（本地运行、云部署、容器化等）": "本地运行",
        "预期的用户规模和性能要求是什么？（小型个人项目 vs 企业级应用）": "小型个人项目",
        "是否需要集成第三方服务或API？": "不需要"
    }

    project = pm.run_requirement_analysis(
        project,
        interactive=False,
        auto_answers=auto_answers
    )

    assert project.requirement is not None
    assert len(project.requirement.user_stories) > 0
    assert len(project.requirement.tech_stack) > 0

    print(f"  ✅ 需求分析完成")
    print(f"     用户故事数: {len(project.requirement.user_stories)}")
    print(f"     技术栈: {project.requirement.tech_stack}")

    return project


def test_task_planning(project):
    """测试任务规划"""
    print("\n测试3: 任务规划...")

    pm = ProjectManager(workspace_root="./test_projects")
    project = pm.run_task_planning(project)

    stats = project.task_queue.get_statistics()

    assert stats['total'] > 0
    assert stats['pending'] > 0

    print(f"  ✅ 任务规划完成")
    print(f"     总任务数: {stats['total']}")
    print(f"     待执行: {stats['pending']}")

    # 显示前3个任务
    print("\n     前3个任务:")
    for i, task in enumerate(project.task_queue.tasks[:3], 1):
        print(f"       {i}. [{task.id}] {task.title}")

    return project


def test_task_execution_flow(project):
    """测试任务执行流程"""
    print("\n测试4: 任务执行流程...")

    pm = ProjectManager(workspace_root="./test_projects")

    # 获取下一个任务
    next_task = pm.get_next_task(project)
    assert next_task is not None

    print(f"  📋 下一个任务: {next_task.title}")

    # 模拟任务开始
    pm.mark_task_started(project, next_task.id)
    assert next_task.status.value == "in_progress"
    print(f"  ✅ 任务已开始")

    # 模拟任务完成
    pm.mark_task_completed(project, next_task.id, ["test_file.py"])
    assert next_task.status.value == "completed"
    print(f"  ✅ 任务已完成")

    return project


def test_project_persistence(project):
    """测试项目持久化"""
    print("\n测试5: 项目持久化...")

    import os

    # 检查项目文件是否存在
    project_file = os.path.join(project.workspace_path, "project.json")
    prd_file = project.get_prd_path()

    assert os.path.exists(project_file)
    assert os.path.exists(prd_file)

    print(f"  ✅ 项目文件已保存: {project_file}")
    print(f"  ✅ PRD文档已保存: {prd_file}")

    # 检查任务文件
    tasks_dir = os.path.join(project.workspace_path, ".ai_tasks")
    assert os.path.exists(tasks_dir)

    task_files = os.listdir(tasks_dir)
    print(f"  ✅ 任务文件数: {len(task_files)}")


def test_dashboard(project):
    """测试仪表板"""
    print("\n测试6: 项目仪表板...")

    pm = ProjectManager(workspace_root="./test_projects")
    dashboard = pm.get_project_dashboard(project)

    print(dashboard)
    print("  ✅ 仪表板生成成功")


def main():
    """运行所有测试"""
    print("="*70)
    print("🧪 AI-Exchange-Room 基本功能测试")
    print("="*70 + "\n")

    try:
        # 测试1: 项目创建
        project = test_project_creation()

        # 测试2: 需求分析
        project = test_requirement_analysis(project)

        # 测试3: 任务规划
        project = test_task_planning(project)

        # 测试4: 任务执行流程
        project = test_task_execution_flow(project)

        # 测试5: 持久化
        test_project_persistence(project)

        # 测试6: 仪表板
        test_dashboard(project)

        print("\n" + "="*70)
        print("✨ 所有测试通过！")
        print("="*70)

        print(f"\n测试项目位置: {project.workspace_path}")
        print("\n您可以查看以下文件：")
        print(f"  • PRD文档: {project.get_prd_path()}")
        print(f"  • 任务摘要: {project.workspace_path}/docs/TASKS_SUMMARY.md")
        print(f"  • 任务指令: {project.workspace_path}/.ai_tasks/")

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
