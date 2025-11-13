#!/usr/bin/env python3
"""
CLI工具集
提供快速查看和管理任务的命令行工具
"""
import sys
import os
import json
from pathlib import Path


def load_project_info(project_path: str) -> dict:
    """加载项目信息"""
    project_file = os.path.join(project_path, "project.json")
    if not os.path.exists(project_file):
        return None

    with open(project_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def show_next_task(project_path: str):
    """显示下一个待执行的任务"""
    project_info = load_project_info(project_path)
    if not project_info:
        print(f"❌ 项目不存在: {project_path}")
        return

    # 找到下一个待执行的任务
    tasks = project_info.get('task_queue', {}).get('tasks', [])
    completed_ids = {t['id'] for t in tasks if t['status'] == 'completed'}

    next_task = None
    for task in tasks:
        if task['status'] == 'pending':
            # 检查依赖
            deps = task.get('dependencies', [])
            if all(dep in completed_ids for dep in deps):
                next_task = task
                break

    if not next_task:
        print("✅ 所有任务已完成或没有可执行的任务！")
        return

    # 显示任务信息
    print("\n" + "="*70)
    print(f"📋 下一个任务")
    print("="*70)
    print(f"\n任务ID: {next_task['id']}")
    print(f"标题: {next_task['title']}")
    print(f"类型: {next_task['task_type']}")
    print(f"\n描述:")
    print(next_task['description'])

    if next_task.get('acceptance_criteria'):
        print(f"\n验收标准:")
        for i, criterion in enumerate(next_task['acceptance_criteria'], 1):
            print(f"  {i}. {criterion}")

    if next_task.get('dependencies'):
        print(f"\n依赖任务: {', '.join(next_task['dependencies'])}")

    # 显示任务文件位置
    task_file = os.path.join(project_path, ".ai_tasks", f"{next_task['id']}.md")
    print(f"\n📄 任务详细指令: {task_file}")
    print("="*70 + "\n")


def show_all_tasks(project_path: str):
    """显示所有任务"""
    project_info = load_project_info(project_path)
    if not project_info:
        print(f"❌ 项目不存在: {project_path}")
        return

    tasks = project_info.get('task_queue', {}).get('tasks', [])
    stats = project_info.get('task_queue', {}).get('statistics', {})

    print("\n" + "="*70)
    print(f"📊 任务列表 ({project_info['name']})")
    print("="*70)

    # 按状态分组
    by_status = {}
    for task in tasks:
        status = task['status']
        if status not in by_status:
            by_status[status] = []
        by_status[status].append(task)

    status_names = {
        'completed': '✅ 已完成',
        'in_progress': '⚙️  进行中',
        'pending': '⏳ 待执行',
        'failed': '❌ 失败',
        'blocked': '🚫 阻塞'
    }

    for status, name in status_names.items():
        if status in by_status:
            print(f"\n{name} ({len(by_status[status])})")
            print("-" * 70)
            for task in by_status[status]:
                print(f"  [{task['id']}] {task['title']}")

    # 显示统计
    print("\n" + "="*70)
    print("统计:")
    print(f"  总任务数: {stats.get('total', 0)}")
    print(f"  已完成: {stats.get('completed', 0)} ({stats.get('completed', 0) / stats.get('total', 1) * 100:.1f}%)")
    print(f"  进行中: {stats.get('in_progress', 0)}")
    print(f"  待执行: {stats.get('pending', 0)}")
    print("="*70 + "\n")


def show_task_detail(project_path: str, task_id: str):
    """显示任务详情"""
    task_file = os.path.join(project_path, ".ai_tasks", f"{task_id}.md")

    if not os.path.exists(task_file):
        print(f"❌ 任务不存在: {task_id}")
        return

    print("\n" + "="*70)
    print(f"📋 任务详情: {task_id}")
    print("="*70 + "\n")

    with open(task_file, 'r', encoding='utf-8') as f:
        print(f.read())


def show_prd(project_path: str):
    """显示PRD文档"""
    prd_file = os.path.join(project_path, "docs", "PRD.md")

    if not os.path.exists(prd_file):
        print(f"❌ PRD文档不存在")
        return

    with open(prd_file, 'r', encoding='utf-8') as f:
        print(f.read())


def main():
    """主函数"""
    if len(sys.argv) < 3:
        print("""
使用方法:
  python src/cli_tools.py <project_path> <command> [args]

命令:
  next              - 显示下一个待执行的任务
  list              - 显示所有任务列表
  task <task_id>    - 显示特定任务的详细信息
  prd               - 显示项目需求文档

示例:
  python src/cli_tools.py ./projects/PRJ-ABC12345 next
  python src/cli_tools.py ./projects/PRJ-ABC12345 list
  python src/cli_tools.py ./projects/PRJ-ABC12345 task TASK-12345678
  python src/cli_tools.py ./projects/PRJ-ABC12345 prd
        """)
        return

    project_path = sys.argv[1]
    command = sys.argv[2]

    if command == "next":
        show_next_task(project_path)
    elif command == "list":
        show_all_tasks(project_path)
    elif command == "task" and len(sys.argv) >= 4:
        task_id = sys.argv[3]
        show_task_detail(project_path, task_id)
    elif command == "prd":
        show_prd(project_path)
    else:
        print(f"❌ 未知命令: {command}")


if __name__ == "__main__":
    main()
