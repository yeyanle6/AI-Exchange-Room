#!/usr/bin/env python3
"""
自动确认系统演示
展示倒计时自动确认和用户干预功能
"""
import sys
from pathlib import Path

# 添加src到路径
sys.path.insert(0, str(Path(__file__).parent))

from src.utils import AutoConfirm, BatchAutoConfirm, quick_confirm


def demo_basic_auto_confirm():
    """演示基本的自动确认"""
    print("="*70)
    print("演示 1: 基本自动确认")
    print("="*70)
    print("\n说明：将在5秒后自动确认，您可以在倒计时期间输入 y/n 来干预\n")

    ac = AutoConfirm(timeout=5)

    # 示例1：默认自动确认
    result1 = ac.confirm("是否创建新文件 test.txt？", auto_yes=True)
    print(f"结果: {result1}\n")

    # 示例2：默认自动取消
    result2 = ac.confirm("是否删除所有文件？", auto_yes=False)
    print(f"结果: {result2}\n")


def demo_quick_confirm():
    """演示快速确认函数"""
    print("\n" + "="*70)
    print("演示 2: 快速确认函数")
    print("="*70)
    print("\n说明：简化的确认函数，默认3秒自动确认\n")

    # 使用快速确认函数
    result = quick_confirm("是否保存修改？", timeout=3)
    print(f"结果: {result}\n")


def demo_batch_confirm():
    """演示批量确认"""
    print("\n" + "="*70)
    print("演示 3: 批量确认（支持全部是/全部否）")
    print("="*70)
    print("\n说明：处理多个操作时，可以选择 [a]全部是 或 [x]全部否\n")

    batch = BatchAutoConfirm(timeout=3)

    tasks = [
        "创建目录 src/",
        "创建目录 tests/",
        "创建文件 README.md",
        "创建文件 .gitignore",
        "初始化 git 仓库"
    ]

    results = []
    for i, task in enumerate(tasks, 1):
        print(f"\n[{i}/{len(tasks)}]")
        result = batch.confirm(task)
        results.append(result)

    print("\n执行结果:")
    for task, result in zip(tasks, results):
        status = "✅" if result else "⏭️"
        print(f"  {status} {task}")


def demo_with_action():
    """演示带操作的确认"""
    print("\n" + "="*70)
    print("演示 4: 确认并执行操作")
    print("="*70)
    print("\n说明：确认后自动执行操作\n")

    ac = AutoConfirm(timeout=5)

    def write_file():
        """模拟写文件操作"""
        print("  💾 正在写入文件...")
        import time
        time.sleep(1)
        print("  ✅ 文件写入完成")

    # 确认并执行
    ac.confirm_action(
        action_name="写入配置文件",
        action_func=write_file,
        timeout=3,
        auto_yes=True
    )


def demo_integration_scenario():
    """演示集成场景：模拟任务执行流程"""
    print("\n" + "="*70)
    print("演示 5: 集成场景 - 模拟任务执行流程")
    print("="*70)
    print("\n说明：模拟一个完整的开发任务执行流程\n")

    batch = BatchAutoConfirm(timeout=3)

    # 场景：执行一个开发任务
    print("📋 任务: 创建用户认证模块\n")
    print("任务描述:")
    print("  - 创建 auth.py 文件")
    print("  - 实现登录和注册功能")
    print("  - 添加单元测试\n")

    # 步骤1：确认开始任务
    if not batch.confirm("是否开始执行此任务？"):
        print("任务已取消")
        return

    # 步骤2：确认每个子步骤
    steps = [
        "创建 src/auth.py 文件",
        "实现 login() 函数",
        "实现 register() 函数",
        "创建 tests/test_auth.py",
        "运行单元测试"
    ]

    print("\n开始执行子步骤：\n")

    for i, step in enumerate(steps, 1):
        print(f"步骤 {i}/{len(steps)}")
        if batch.confirm(step):
            print(f"  ⚙️  执行中...")
            import time
            time.sleep(0.5)
            print(f"  ✅ 完成\n")
        else:
            print(f"  ⏭️  已跳过\n")

    print("="*70)
    print("✨ 任务执行流程演示完成")
    print("="*70)


def main():
    """主函数"""
    print("\n")
    print("╔═══════════════════════════════════════════════════════════════════════╗")
    print("║                                                                       ║")
    print("║              🎯 自动确认系统 - 功能演示                                ║")
    print("║                                                                       ║")
    print("║  特性：                                                                ║")
    print("║    ⏱️  倒计时自动确认（默认5秒）                                        ║")
    print("║    ⚡ 用户可随时干预（输入 y/n）                                        ║")
    print("║    🚀 支持批量操作（全部是/全部否）                                     ║")
    print("║    📝 可回车跳过倒计时                                                 ║")
    print("║                                                                       ║")
    print("╚═══════════════════════════════════════════════════════════════════════╝")
    print("\n")

    try:
        # 演示1：基本自动确认
        demo_basic_auto_confirm()

        # 演示2：快速确认
        demo_quick_confirm()

        # 演示3：批量确认
        demo_batch_confirm()

        # 演示4：带操作的确认
        demo_with_action()

        # 演示5：集成场景
        demo_integration_scenario()

        print("\n" + "="*70)
        print("✨ 所有演示完成！")
        print("="*70)
        print("\n提示：在实际使用中，您可以：")
        print("  • 调整倒计时时长（timeout参数）")
        print("  • 设置默认动作（auto_yes参数）")
        print("  • 批量操作时选择'全部是'或'全部否'")
        print("  • 按回车键立即跳过倒计时")
        print()

    except KeyboardInterrupt:
        print("\n\n⚠️  演示已中断")
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
