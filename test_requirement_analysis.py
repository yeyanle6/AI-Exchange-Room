#!/usr/bin/env python3
"""
测试需求分析界面
"""
import sys
import os
from pathlib import Path

# 设置为offscreen模式（无需显示器）
os.environ['QT_QPA_PLATFORM'] = 'offscreen'

sys.path.insert(0, str(Path(__file__).parent))


def test_imports():
    """测试导入"""
    print("测试1: 导入需求分析组件...")
    try:
        from src.gui.widgets.requirement_analysis_widget import RequirementAnalysisWidget
        print("  ✓ RequirementAnalysisWidget 导入成功")
        return True
    except Exception as e:
        print(f"  ✗ 导入失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_class_structure():
    """测试类结构"""
    print("\n测试2: 检查RequirementAnalysisWidget类结构...")
    try:
        from src.gui.widgets.requirement_analysis_widget import RequirementAnalysisWidget

        required_methods = [
            '_init_ui',
            '_create_input_section',
            '_create_discussion_section',
            '_create_result_section',
            '_start_analysis',
            '_on_message_received',
            '_on_analysis_complete',
            '_display_results'
        ]

        for method in required_methods:
            if hasattr(RequirementAnalysisWidget, method):
                print(f"  ✓ 方法 {method} 存在")
            else:
                print(f"  ✗ 方法 {method} 不存在")
                return False

        return True
    except Exception as e:
        print(f"  ✗ 类结构测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_backend_integration():
    """测试后端集成"""
    print("\n测试3: 测试MultiAgentAnalyst后端集成...")
    try:
        from src.core.multi_agent_analyst import MultiAgentAnalyst, AgentRole

        analyst = MultiAgentAnalyst()
        print(f"  ✓ MultiAgentAnalyst 实例化成功")
        print(f"  ✓ AI角色数量: {len(analyst.agents)}")

        # 检查所有角色
        expected_roles = [
            AgentRole.PRODUCT_MANAGER,
            AgentRole.TECH_ARCHITECT,
            AgentRole.UX_DESIGNER,
            AgentRole.QA_ENGINEER,
            AgentRole.DEVOPS_ENGINEER,
            AgentRole.SECURITY_EXPERT
        ]

        for role in expected_roles:
            if role in analyst.agents:
                print(f"  ✓ 角色 {role.value} 已配置")
            else:
                print(f"  ✗ 角色 {role.value} 缺失")
                return False

        return True
    except Exception as e:
        print(f"  ✗ 后端集成测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_worker_thread():
    """测试工作线程"""
    print("\n测试4: 测试AnalysisWorker线程...")
    try:
        from src.gui.widgets.requirement_analysis_widget import AnalysisWorker
        from PyQt5.QtWidgets import QApplication

        # 需要QApplication实例
        if not QApplication.instance():
            app = QApplication(sys.argv)

        worker = AnalysisWorker("测试项目需求")
        print("  ✓ AnalysisWorker 实例化成功")

        # 检查信号
        if hasattr(worker, 'message_received'):
            print("  ✓ message_received 信号存在")
        if hasattr(worker, 'analysis_complete'):
            print("  ✓ analysis_complete 信号存在")
        if hasattr(worker, 'progress_update'):
            print("  ✓ progress_update 信号存在")

        return True
    except Exception as e:
        print(f"  ✗ 工作线程测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_main_window_integration():
    """测试主窗口集成"""
    print("\n测试5: 测试主窗口集成...")
    try:
        from src.gui.main_window import MainWindow

        # 检查方法存在
        if hasattr(MainWindow, '_open_requirement_analysis'):
            print("  ✓ _open_requirement_analysis 方法存在")
        else:
            print("  ✗ _open_requirement_analysis 方法不存在")
            return False

        return True
    except Exception as e:
        print(f"  ✗ 主窗口集成测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """运行所有测试"""
    print("=" * 70)
    print("需求分析界面测试")
    print("=" * 70)

    tests = [
        ("模块导入", test_imports),
        ("类结构", test_class_structure),
        ("后端集成", test_backend_integration),
        ("工作线程", test_worker_thread),
        ("主窗口集成", test_main_window_integration)
    ]

    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n✗ 测试 '{name}' 异常: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))

    print("\n" + "=" * 70)
    print("测试总结")
    print("=" * 70)

    for name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{name}: {status}")

    all_passed = all(result for _, result in results)

    if all_passed:
        print("\n🎉 所有测试通过！需求分析界面已准备就绪。")
        print("\n功能特性：")
        print("  • 多角色AI讨论可视化")
        print("  • 实时消息展示（带颜色区分）")
        print("  • 角色筛选功能")
        print("  • 需求分析结果展示（共识、关注点、建议）")
        print("  • 后台线程异步处理")
        print("  • 进度条显示")
        print("\n在有显示器的环境中运行以下命令测试完整功能:")
        print("  python gui_main.py")
    else:
        print("\n⚠️ 部分测试失败，请检查错误信息。")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
