"""
自动确认系统
支持倒计时和用户干预的智能确认机制
"""
import sys
import time
import threading
from typing import Optional, Callable


class AutoConfirm:
    """
    自动确认工具
    在倒计时结束前允许用户干预，否则自动确认
    """

    def __init__(self, default_timeout: int = 5):
        """
        初始化自动确认系统

        Args:
            default_timeout: 默认倒计时秒数
        """
        self.default_timeout = default_timeout
        self.user_input = None
        self.input_received = False

    def _get_user_input(self, prompt: str):
        """在后台线程中获取用户输入"""
        try:
            self.user_input = input(prompt)
            self.input_received = True
        except:
            pass

    def confirm(self,
                message: str,
                timeout: Optional[int] = None,
                auto_yes: bool = True) -> bool:
        """
        确认操作，支持倒计时自动确认

        Args:
            message: 确认消息
            timeout: 倒计时秒数（None则使用默认值）
            auto_yes: 倒计时结束后是否自动确认（True=是，False=否）

        Returns:
            True表示确认，False表示取消

        示例:
            >>> auto_confirm = AutoConfirm()
            >>> if auto_confirm.confirm("是否写入文件？"):
            >>>     # 执行写入操作
        """
        if timeout is None:
            timeout = self.default_timeout

        # 重置状态
        self.user_input = None
        self.input_received = False

        # 显示倒计时提示
        default_action = "确认" if auto_yes else "取消"
        print(f"\n{message}")
        print(f"将在 {timeout} 秒后自动{default_action} (输入 y/n 可立即选择，回车跳过倒计时)")

        # 在后台线程中获取用户输入
        input_thread = threading.Thread(
            target=self._get_user_input,
            args=(f"请选择 [{'Y' if auto_yes else 'y'}/{'n' if auto_yes else 'N'}]: ",),
            daemon=True
        )
        input_thread.start()

        # 倒计时显示
        for remaining in range(timeout, 0, -1):
            if self.input_received:
                break

            # 显示倒计时进度条
            self._show_countdown(remaining, timeout)
            time.sleep(1)

        # 清除倒计时显示
        print("\r" + " " * 80 + "\r", end="")

        # 处理用户输入
        if self.input_received and self.user_input is not None:
            user_choice = self.user_input.strip().lower()
            if user_choice in ['y', 'yes', '是']:
                print("✓ 用户选择：确认")
                return True
            elif user_choice in ['n', 'no', '否']:
                print("✗ 用户选择：取消")
                return False
            elif user_choice == '':
                # 回车键 - 跳过倒计时，使用默认值
                print(f"⚡ 跳过倒计时，{default_action}")
                return auto_yes
            else:
                print(f"? 无效输入，使用默认值：{default_action}")
                return auto_yes
        else:
            # 倒计时结束，自动确认
            print(f"⏱ 倒计时结束，自动{default_action}")
            return auto_yes

    def _show_countdown(self, remaining: int, total: int):
        """显示倒计时进度条"""
        # 计算进度
        progress = (total - remaining) / total
        bar_length = 30
        filled_length = int(bar_length * progress)

        # 创建进度条
        bar = '█' * filled_length + '░' * (bar_length - filled_length)

        # 显示
        sys.stdout.write(f"\r⏳ [{bar}] {remaining}秒 ")
        sys.stdout.flush()

    def confirm_action(self,
                      action_name: str,
                      action_func: Callable,
                      timeout: Optional[int] = None,
                      auto_yes: bool = True) -> bool:
        """
        确认并执行操作

        Args:
            action_name: 操作名称
            action_func: 要执行的函数
            timeout: 倒计时秒数
            auto_yes: 是否自动确认

        Returns:
            操作是否成功执行

        示例:
            >>> def write_file():
            >>>     with open('test.txt', 'w') as f:
            >>>         f.write('hello')
            >>>
            >>> auto_confirm = AutoConfirm()
            >>> auto_confirm.confirm_action("写入文件", write_file)
        """
        if self.confirm(f"是否执行操作：{action_name}？", timeout, auto_yes):
            try:
                action_func()
                print(f"✅ 操作完成：{action_name}")
                return True
            except Exception as e:
                print(f"❌ 操作失败：{action_name} - {e}")
                return False
        else:
            print(f"⏭️  操作已跳过：{action_name}")
            return False


class BatchAutoConfirm:
    """
    批量自动确认工具
    用于处理多个连续的确认操作
    """

    def __init__(self, timeout: int = 5):
        """
        初始化批量确认系统

        Args:
            timeout: 每个确认的倒计时秒数
        """
        self.auto_confirm = AutoConfirm(timeout)
        self.all_yes = False  # 是否对所有操作都选择"是"
        self.all_no = False   # 是否对所有操作都选择"否"

    def confirm(self, message: str, timeout: Optional[int] = None) -> bool:
        """
        批量确认（支持"全部是"和"全部否"）

        Args:
            message: 确认消息
            timeout: 倒计时秒数

        Returns:
            True表示确认，False表示取消
        """
        # 如果已经选择了"全部是"或"全部否"
        if self.all_yes:
            print(f"✓ {message} - 自动确认（全部是模式）")
            return True
        if self.all_no:
            print(f"✗ {message} - 自动取消（全部否模式）")
            return False

        # 修改提示，增加"全部"选项
        print(f"\n{message}")
        print(f"选项: [y]是 [n]否 [a]全部是 [x]全部否 [回车]自动确认")

        # 重置状态
        self.auto_confirm.user_input = None
        self.auto_confirm.input_received = False

        # 获取用户输入（带倒计时）
        input_thread = threading.Thread(
            target=self.auto_confirm._get_user_input,
            args=("请选择: ",),
            daemon=True
        )
        input_thread.start()

        # 倒计时
        for remaining in range(timeout or self.auto_confirm.default_timeout, 0, -1):
            if self.auto_confirm.input_received:
                break
            self.auto_confirm._show_countdown(remaining, timeout or self.auto_confirm.default_timeout)
            time.sleep(1)

        print("\r" + " " * 80 + "\r", end="")

        # 处理输入
        if self.auto_confirm.input_received and self.auto_confirm.user_input is not None:
            choice = self.auto_confirm.user_input.strip().lower()

            if choice in ['y', 'yes', '是']:
                print("✓ 确认")
                return True
            elif choice in ['n', 'no', '否']:
                print("✗ 取消")
                return False
            elif choice in ['a', 'all', '全部']:
                print("✓✓✓ 全部确认（后续操作将自动确认）")
                self.all_yes = True
                return True
            elif choice in ['x', 'none', '全部否']:
                print("✗✗✗ 全部取消（后续操作将自动取消）")
                self.all_no = True
                return False
            elif choice == '':
                print("⚡ 自动确认")
                return True

        # 默认确认
        print("⏱ 自动确认")
        return True


# 便捷函数
def quick_confirm(message: str, timeout: int = 5, auto_yes: bool = True) -> bool:
    """
    快速确认函数

    Args:
        message: 确认消息
        timeout: 倒计时秒数
        auto_yes: 是否自动确认

    Returns:
        True表示确认，False表示取消
    """
    ac = AutoConfirm(timeout)
    return ac.confirm(message, timeout, auto_yes)


def batch_confirm(messages: list, timeout: int = 3) -> list:
    """
    批量确认多个操作

    Args:
        messages: 确认消息列表
        timeout: 每个确认的倒计时秒数

    Returns:
        确认结果列表（True/False）
    """
    batch = BatchAutoConfirm(timeout)
    results = []

    for i, message in enumerate(messages, 1):
        print(f"\n[{i}/{len(messages)}]")
        result = batch.confirm(message, timeout)
        results.append(result)

    return results
