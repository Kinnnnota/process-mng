#!/usr/bin/env python3
"""
AI驱动的项目管理系统 - 使用示例
展示如何使用Claude API进行自动化开发和评审
"""

from project_manager import ProjectManager
from project_manager.auto_workflow import AutoWorkflow
from project_manager.ai_integration import AIIntegration
from project_manager.config_loader import get_config_loader


def example_1_basic_usage():
    """示例1: 基本使用流程"""
    print("=" * 60)
    print("示例1: 基本使用 - 手动控制开发和评审")
    print("=" * 60)

    # 创建项目
    pm = ProjectManager("example_project")

    # 开发模式 - 生成内容
    pm.set_mode("developer")
    print("\n📝 开发模式: 生成基本设计文档...")
    content = pm.execute_phase()
    print(f"生成内容预览: {content[:200]}...")

    # 评审模式 - 评审内容
    pm.set_mode("reviewer")
    print("\n🔍 评审模式: 评审基本设计文档...")
    review = pm.review_phase()
    print(f"评分: {review['score']}分")
    print(f"发现问题: {len(review['issues'])}个")

    # 检查是否可以进入下一阶段
    if pm.check_phase_transition():
        print("✅ 可以进入下一阶段")
    else:
        print("❌ 需要继续迭代")


def example_2_auto_workflow():
    """示例2: 自动化工作流"""
    print("\n" + "=" * 60)
    print("示例2: 自动化工作流 - 全自动运行")
    print("=" * 60)

    # 创建自动工作流
    workflow = AutoWorkflow("auto_project")

    # 运行自动工作流(会自动执行所有阶段)
    print("\n🤖 启动自动化工作流...")
    result = workflow.run_auto_workflow()

    # 显示结果
    print(f"\n工作流状态: {result['status']}")
    print(f"完成阶段数: {len(result['phases_completed'])}")
    print(f"总迭代次数: {result['total_iterations']}")

    if result['final_score']:
        print(f"最终评分: {result['final_score']}分")


def example_3_smart_workflow():
    """示例3: 智能工作流 - 达到目标分数后自动进入下阶段"""
    print("\n" + "=" * 60)
    print("示例3: 智能工作流 - 目标导向")
    print("=" * 60)

    # 创建自动工作流
    workflow = AutoWorkflow("smart_project")

    # 运行智能工作流,目标分数85分
    print("\n🧠 启动智能工作流(目标: 85分)...")
    result = workflow.run_smart_workflow(target_score=85.0)

    # 显示结果
    print(f"\n工作流状态: {result['status']}")
    print(f"目标分数: {result['target_score']}")
    print(f"完成阶段数: {len(result['phases_completed'])}")

    # 显示各阶段得分
    for phase_info in result['phases_completed']:
        print(f"  - {phase_info['phase']}: {phase_info['score']}分 "
              f"({phase_info['iterations']}次迭代)")


def example_4_ai_integration():
    """示例4: 直接使用AI集成"""
    print("\n" + "=" * 60)
    print("示例4: AI集成 - 直接使用AI生成和评审")
    print("=" * 60)

    from project_manager.models import Phase

    # 创建AI集成实例
    ai = AIIntegration()

    # 检查配置
    if not ai.validate_config():
        print("❌ AI配置无效,请设置ANTHROPIC_API_KEY")
        return

    print("✅ AI配置有效")
    print(f"Provider信息: {ai.get_provider_info()}")

    # 生成内容
    print("\n📝 生成基本设计内容...")
    content = ai.generate_content(
        phase=Phase.BASIC_DESIGN,
        context={"project_name": "test_project"}
    )
    print(f"生成内容长度: {len(content)} 字符")

    # 评审内容
    print("\n🔍 评审生成的内容...")
    review = ai.review_content(
        phase=Phase.BASIC_DESIGN,
        content=content
    )
    print(f"评审分数: {review['score']}分")
    print(f"发现问题: {len(review['issues'])}个")
    print(f"改进建议: {len(review['improvements'])}条")


def example_5_check_config():
    """示例5: 检查配置状态"""
    print("\n" + "=" * 60)
    print("示例5: 配置检查")
    print("=" * 60)

    # 获取配置加载器
    config_loader = get_config_loader()

    # 显示配置状态
    status = config_loader.get_config_status()
    print("\n📋 配置状态:")
    print(f"  .env文件: {status['env_file']}")
    print(f"  文件存在: {status['env_file_exists']}")
    print(f"  API Key配置: {'✅ 已配置' if status['claude_api_key_configured'] else '❌ 未配置'}")
    print(f"  使用模型: {status['claude_model']}")

    # 获取Claude配置
    claude_config = config_loader.get_claude_config()
    print("\n🤖 Claude配置:")
    print(f"  模型: {claude_config['model']}")
    print(f"  最大Token: {claude_config['max_tokens']}")
    print(f"  温度: {claude_config['temperature']}")
    print(f"  API Key: {'*' * 10 + (claude_config['api_key'][-4:] if claude_config['api_key'] else '未配置')}")


def main():
    """主函数 - 运行所有示例"""
    print("🚀 AI驱动的项目管理系统 - 使用示例")
    print("=" * 60)

    # 首先检查配置
    example_5_check_config()

    # 根据配置决定运行哪些示例
    config_loader = get_config_loader()
    if not config_loader.validate_config():
        print("\n" + "=" * 60)
        print("❌ 配置检查失败!")
        print("=" * 60)
        print("\n请按照以下步骤配置:")
        print("1. 复制 .env.example 文件为 .env")
        print("2. 在 .env 文件中设置你的 ANTHROPIC_API_KEY")
        print("3. 重新运行此示例")
        print("\n或者直接设置环境变量:")
        print("  export ANTHROPIC_API_KEY=your_key_here  (Linux/Mac)")
        print("  set ANTHROPIC_API_KEY=your_key_here     (Windows)")
        return

    print("\n" + "=" * 60)
    print("✅ 配置检查通过,开始运行示例")
    print("=" * 60)

    try:
        # 运行示例(根据需要取消注释)
        # example_1_basic_usage()
        # example_2_auto_workflow()
        # example_3_smart_workflow()
        example_4_ai_integration()

        print("\n" + "=" * 60)
        print("✅ 所有示例运行完成")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ 示例运行失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
