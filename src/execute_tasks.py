#!/usr/bin/env python3
"""
交互式任务执行工具
支持自动确认的任务执行流程
"""
import sys
import os
import argparse
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core import ProjectManager, TaskExecutor
from src.utils import app_logger


def load_project(project_path: str):
    """加载项目"""
    if not os.path.exists(project_path):
        print(f"❌ 项目路径不存在: {project_path}")
        return None

    project_file = os.path.join(project_path, "project.json")
    if not os.path.exists(project_file):
        print(f"❌ 项目文件不存在: {project_file}")
        return None

    # 简化的加载逻辑：直接从文件系统构建项目对象
    # 在完整实现中应该从JSON完整反序列化
    import json
    with open(project_file, 'r', encoding='utf-8') as f:
        project_data = json.load(f)

    from src.models import Project
    project = Project(
        name=project_data['name'],
        project_id=project_data['project_id'],
        workspace_path=project_data['workspace_path']
    )

    # 重新加载任务队列（简化版）
    # 实际应该完整反序列化
    print(f"✅ 项目已加载: {project.name}")
    print(f"   项目ID: {project.project_id}")

    return project


def execute_tasks_interactive(project_path: str, timeout: int = 5):
    """
    交互式执行项目任务

    Args:
        project_path: 项目路径
        timeout: 自动确认倒计时秒数
    """
    # 加载项目
    project = load_project(project_path)
    if not project:
        return

    # 创建任务执行器
    executor = TaskExecutor(project, auto_confirm_timeout=timeout)

    # 显示项目信息
    print("\n" + "="*70)
    print("🚀 交互式任务执行")
    print("="*70)
    print(f"项目: {project.name}")
    print(f"工作区: {project.workspace_path}")
    print("="*70)

    # 提示信息
    print("\n💡 提示:")
    print(f"  • 每个操作将在 {timeout} 秒后自动确认")
    print("  • 您可以随时输入 y/n 进行干预")
    print("  • 按回车键可立即跳过倒计时")
    print()

    # 执行所有任务
    try:
        stats = executor.execute_all_tasks_interactive()

        # 显示最终结果
        print("\n" + "="*70)
        print("✨ 任务执行完成")
        print("="*70)
        print(f"总任务数:   {stats['total']}")
        print(f"已完成:     {stats['completed']}")
        print(f"已跳过:     {stats['skipped']}")
        print(f"失败:       {stats['failed']}")
        print("="*70 + "\n")

    except KeyboardInterrupt:
        print("\n\n⚠️  任务执行已中断")
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        app_logger.error(f"任务执行失败: {e}", exc_info=True)


def execute_single_task(project_path: str, task_id: str, timeout: int = 5):
    """
    执行单个任务

    Args:
        project_path: 项目路径
        task_id: 任务ID
        timeout: 自动确认倒计时秒数
    """
    # 加载项目
    project = load_project(project_path)
    if not project:
        return

    # 创建任务执行器
    executor = TaskExecutor(project, auto_confirm_timeout=timeout)

    # 查找任务
    task = project.task_queue.get_task_by_id(task_id)
    if not task:
        print(f"❌ 任务不存在: {task_id}")
        return

    # 执行任务
    try:
        print(f"\n🎯 执行单个任务\n")
        success = executor.execute_task_interactive(task)

        if success:
            print(f"\n✅ 任务成功完成: {task.title}")
        else:
            print(f"\n⏭️  任务未完成: {task.title}")

    except KeyboardInterrupt:
        print("\n\n⚠️  任务执行已中断")
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        app_logger.error(f"任务执行失败: {e}", exc_info=True)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="交互式任务执行工具 - 支持自动确认和用户干预",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  交互式执行所有任务（5秒倒计时）:
    python src/execute_tasks.py ./projects/PRJ-ABC12345

  使用3秒倒计时:
    python src/execute_tasks.py ./projects/PRJ-ABC12345 --timeout 3

  执行单个任务:
    python src/execute_tasks.py ./projects/PRJ-ABC12345 --task TASK-12345678

  执行下一个任务:
    python src/execute_tasks.py ./projects/PRJ-ABC12345 --next

特性:
  ⏱️  倒计时自动确认
  ⚡ 可随时用户干预（y/n）
  🚀 支持批量执行
  📝 可回车跳过倒计时
        """
    )

    parser.add_argument(
        'project_path',
        help='项目路径'
    )

    parser.add_argument(
        '--timeout',
        type=int,
        default=5,
        help='自动确认倒计时秒数（默认5秒）'
    )

    parser.add_argument(
        '--task',
        help='执行指定的任务ID'
    )

    parser.add_argument(
        '--next',
        action='store_true',
        help='执行下一个待执行的任务'
    )

    args = parser.parse_args()

    # 根据参数执行不同操作
    if args.task:
        execute_single_task(args.project_path, args.task, args.timeout)
    elif args.next:
        # 执行下一个任务
        project = load_project(args.project_path)
        if project:
            executor = TaskExecutor(project, args.timeout)
            next_task = executor.get_next_task()
            if next_task:
                execute_single_task(args.project_path, next_task.id, args.timeout)
            else:
                print("✅ 没有待执行的任务")
    else:
        # 执行所有任务
        execute_tasks_interactive(args.project_path, args.timeout)


if __name__ == "__main__":
    main()
