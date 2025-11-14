"""
任务执行器
自动读取任务并引导Claude Code执行，支持自动确认
"""
import os
import time
from typing import Optional, List
from ..models import Project, Task, TaskStatus
from ..utils import app_logger, load_text
from ..utils.auto_confirm import AutoConfirm, BatchAutoConfirm


class TaskExecutor:
    """
    任务执行器
    负责管理任务执行流程，支持自动确认和进度跟踪
    """

    def __init__(self, project: Project, auto_confirm_timeout: int = 5):
        """
        初始化任务执行器

        Args:
            project: 项目对象
            auto_confirm_timeout: 自动确认倒计时秒数
        """
        self.project = project
        self.auto_confirm = AutoConfirm(auto_confirm_timeout)
        self.batch_confirm = BatchAutoConfirm(auto_confirm_timeout)
        self.logger = app_logger

    def get_next_task(self) -> Optional[Task]:
        """获取下一个待执行的任务"""
        return self.project.task_queue.get_next_task()

    def show_task_instruction(self, task: Task) -> str:
        """
        显示任务指令

        Args:
            task: 任务对象

        Returns:
            任务指令内容
        """
        task_file = self.project.get_task_file_path(task.id)

        if not os.path.exists(task_file):
            self.logger.error(f"任务文件不存在: {task_file}")
            return ""

        instruction = load_text(task_file)

        print("\n" + "="*70)
        print(f"📋 任务: {task.title}")
        print("="*70)
        print(instruction)
        print("="*70 + "\n")

        return instruction

    def execute_task_interactive(self, task: Task) -> bool:
        """
        交互式执行任务（引导用户/Claude Code完成）

        Args:
            task: 任务对象

        Returns:
            任务是否成功执行
        """
        # 1. 显示任务指令
        instruction = self.show_task_instruction(task)

        if not instruction:
            return False

        # 2. 确认是否开始任务
        if not self.auto_confirm.confirm(
            f"是否开始执行任务 [{task.id}] {task.title}？",
            auto_yes=True
        ):
            self.logger.info(f"任务已跳过: {task.title}")
            return False

        # 3. 标记任务开始
        task.start()
        self.logger.info(f"任务开始执行: {task.title}")

        # 4. 等待用户/Claude Code完成任务
        print("\n" + "─"*70)
        print("📝 任务执行阶段")
        print("─"*70)
        print("\n请按照上述任务指令完成开发工作。")
        print("完成后，系统将询问您是否完成任务。\n")

        # 5. 确认任务是否完成
        if not self.auto_confirm.confirm(
            "任务是否已完成？",
            timeout=10,  # 给更长时间让用户完成
            auto_yes=False  # 默认不自动确认完成
        ):
            self.logger.warning(f"任务未完成: {task.title}")
            return False

        # 6. 收集产出文件
        output_files = self._collect_output_files(task)

        # 7. 标记任务完成
        task.complete(output_files)
        self.logger.info(f"任务已完成: {task.title}")

        print(f"\n✅ 任务完成: {task.title}")
        if output_files:
            print(f"产出文件: {', '.join(output_files)}")

        return True

    def _collect_output_files(self, task: Task) -> List[str]:
        """
        收集任务产出的文件

        Args:
            task: 任务对象

        Returns:
            文件路径列表
        """
        print("\n请输入本任务产出的文件路径（多个文件用逗号分隔，直接回车跳过）:")
        user_input = input("文件路径: ").strip()

        if not user_input:
            return []

        # 解析文件路径
        files = [f.strip() for f in user_input.split(',') if f.strip()]
        return files

    def execute_all_tasks_interactive(self) -> dict:
        """
        交互式执行所有任务

        Returns:
            执行统计信息
        """
        stats = {
            'total': 0,
            'completed': 0,
            'skipped': 0,
            'failed': 0
        }

        print("\n" + "="*70)
        print("🚀 开始执行项目任务")
        print("="*70)
        print(f"项目: {self.project.name}")
        print(f"总任务数: {len(self.project.task_queue.tasks)}")
        print("="*70 + "\n")

        while True:
            # 获取下一个任务
            next_task = self.get_next_task()

            if not next_task:
                print("\n✨ 所有任务已完成！")
                break

            stats['total'] += 1

            # 显示进度
            task_stats = self.project.task_queue.get_statistics()
            print(f"\n进度: {task_stats['completed']}/{task_stats['total']} 已完成")

            # 执行任务
            try:
                success = self.execute_task_interactive(next_task)

                if success:
                    stats['completed'] += 1
                else:
                    stats['skipped'] += 1

                    # 任务被跳过，询问是否继续
                    if not self.auto_confirm.confirm(
                        "任务已跳过，是否继续执行下一个任务？",
                        auto_yes=True
                    ):
                        print("\n⏸️  任务执行已暂停")
                        break

            except Exception as e:
                self.logger.error(f"任务执行失败: {next_task.title} - {e}")
                next_task.fail(str(e))
                stats['failed'] += 1

                # 任务失败，询问是否继续
                if not self.auto_confirm.confirm(
                    f"任务失败：{e}\n是否继续执行下一个任务？",
                    auto_yes=False
                ):
                    print("\n⏸️  任务执行已暂停")
                    break

        # 显示最终统计
        print("\n" + "="*70)
        print("📊 执行统计")
        print("="*70)
        print(f"总任务数:   {stats['total']}")
        print(f"已完成:     {stats['completed']}")
        print(f"已跳过:     {stats['skipped']}")
        print(f"失败:       {stats['failed']}")
        print("="*70 + "\n")

        return stats

    def execute_task_batch(self, task_ids: List[str]) -> dict:
        """
        批量执行指定的任务

        Args:
            task_ids: 任务ID列表

        Returns:
            执行统计
        """
        stats = {
            'total': len(task_ids),
            'completed': 0,
            'skipped': 0,
            'failed': 0
        }

        print("\n" + "="*70)
        print(f"📦 批量执行 {len(task_ids)} 个任务")
        print("="*70 + "\n")

        for i, task_id in enumerate(task_ids, 1):
            task = self.project.task_queue.get_task_by_id(task_id)

            if not task:
                self.logger.warning(f"任务不存在: {task_id}")
                stats['failed'] += 1
                continue

            print(f"\n[{i}/{len(task_ids)}]")

            # 使用批量确认模式
            if not self.batch_confirm.confirm(
                f"是否执行任务 [{task.id}] {task.title}？"
            ):
                stats['skipped'] += 1
                continue

            try:
                # 显示任务指令
                self.show_task_instruction(task)

                # 标记开始
                task.start()

                # 简化版执行（不等待用户输入）
                print("⏳ 任务执行中...")
                time.sleep(1)  # 模拟执行

                # 自动完成
                task.complete()
                stats['completed'] += 1
                print(f"✅ 任务完成: {task.title}")

            except Exception as e:
                self.logger.error(f"任务执行失败: {task.title} - {e}")
                task.fail(str(e))
                stats['failed'] += 1

        return stats


class AutomatedTaskExecutor(TaskExecutor):
    """
    自动化任务执行器
    完全自动化执行任务，适合与Claude Code API集成
    """

    def __init__(self, project: Project, auto_confirm_timeout: int = 3):
        super().__init__(project, auto_confirm_timeout)

    def execute_task_automated(self, task: Task) -> bool:
        """
        自动化执行任务（无需用户干预）

        Args:
            task: 任务对象

        Returns:
            是否成功
        """
        # 显示任务信息
        print(f"\n🤖 自动执行任务: {task.title}")

        # 加载任务指令
        instruction = self.show_task_instruction(task)

        if not instruction:
            return False

        # 自动确认并开始
        if self.auto_confirm.confirm(
            f"自动执行任务 [{task.id}]？",
            timeout=3,
            auto_yes=True
        ):
            task.start()

            # TODO: 这里应该调用Claude API执行任务
            # 当前版本是手动引导版，所以暂时跳过
            print("📝 请使用Claude Code执行此任务")

            return True

        return False

    def execute_all_automated(self) -> dict:
        """
        全自动执行所有任务

        Returns:
            执行统计
        """
        stats = {
            'total': 0,
            'completed': 0,
            'failed': 0
        }

        while True:
            next_task = self.get_next_task()

            if not next_task:
                break

            stats['total'] += 1

            try:
                if self.execute_task_automated(next_task):
                    # 注意：在真实的自动化场景中，这里应该等待任务完成
                    # 当前只是标记为开始，需要后续手动确认完成
                    pass
                else:
                    stats['failed'] += 1

            except Exception as e:
                self.logger.error(f"任务执行失败: {e}")
                next_task.fail(str(e))
                stats['failed'] += 1

        return stats
