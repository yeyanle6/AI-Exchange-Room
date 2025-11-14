#!/usr/bin/env python3
"""
多角色需求分析演示
展示AI委员会如何协作分析需求
"""
import sys
from pathlib import Path

# 添加src到路径
sys.path.insert(0, str(Path(__file__).parent))

from src.core.multi_agent_analyst import MultiAgentAnalyst, AgentRole


def demo_multi_agent_analysis():
    """演示多角色分析"""
    print("\n")
    print("╔═══════════════════════════════════════════════════════════════════════╗")
    print("║                                                                       ║")
    print("║              🎭 多角色AI需求分析系统 - 演示                            ║")
    print("║                                                                       ║")
    print("║  特点：                                                                ║")
    print("║    👤 产品经理 - 关注用户价值和商业目标                                ║")
    print("║    🏗️  技术架构师 - 关注技术可行性和架构                               ║")
    print("║    🎨 UX设计师 - 关注用户体验                                         ║")
    print("║    🔍 测试工程师 - 关注质量和测试                                     ║")
    print("║    ⚙️  DevOps - 关注部署和运维                                       ║")
    print("║    🔒 安全专家 - 关注安全和合规                                       ║")
    print("║                                                                       ║")
    print("╚═══════════════════════════════════════════════════════════════════════╝")
    print("\n")

    # 创建多角色分析系统
    analyst = MultiAgentAnalyst()

    # 示例项目
    project_name = "智能待办事项应用"
    high_level_goal = "创建一个AI驱动的待办事项应用，支持智能提醒、优先级推荐和自然语言输入"

    print(f"📋 项目: {project_name}")
    print(f"🎯 目标: {high_level_goal}")
    print()

    # 多角色分析
    result = analyst.analyze_requirement(project_name, high_level_goal)

    # 生成澄清问题
    print("\n" + "="*70)
    print("❓ 多角色澄清问题")
    print("="*70 + "\n")

    questions = analyst.generate_clarification_questions()

    current_role = None
    for i, q in enumerate(questions, 1):
        if q['role'] != current_role:
            current_role = q['role']
            print(f"\n{q['emoji']} {q['role']} ({q['asker']}) 的问题：")
            print("-" * 60)

        print(f"  {i}. {q['question']}")

    print("\n" + "="*70)
    print("✨ 多角色分析完成！")
    print("="*70)
    print("\n说明：")
    print("  • 每个角色从自己的专业角度提出问题")
    print("  • 所有角色的意见会被综合考虑")
    print("  • 最终形成全面的需求分析")
    print()


def demo_role_specific_analysis():
    """演示特定角色的分析"""
    print("\n" + "="*70)
    print("🎯 单角色深度分析演示")
    print("="*70 + "\n")

    from src.core.multi_agent_analyst import AIAgent

    # 只使用产品经理角色
    pm = AIAgent(AgentRole.PRODUCT_MANAGER)

    task = "分析'智能待办应用'的市场定位"
    context = {
        "目标用户": "个人知识工作者",
        "竞品": "Todoist, Things, TickTick"
    }

    print(f"📋 任务: {task}\n")

    analysis = pm.analyze(task, context)
    print(f"{pm.persona.emoji} {pm.persona.name} 的深度分析：")
    print(analysis)


def main():
    """主函数"""
    try:
        # 演示1：完整的多角色分析
        demo_multi_agent_analysis()

        # 演示2：单角色深度分析
        demo_role_specific_analysis()

    except KeyboardInterrupt:
        print("\n\n⚠️  演示已中断")
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
