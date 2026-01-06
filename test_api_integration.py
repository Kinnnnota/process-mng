#!/usr/bin/env python3
"""
快速测试Claude API集成
验证配置和基本功能
"""

from project_manager.config_loader import get_config_loader
from project_manager.claude_provider import ClaudeProvider
from project_manager.ai_integration import AIIntegration
from project_manager.models import Phase


def test_config():
    """测试配置加载"""
    print("=" * 60)
    print("测试1: 配置加载")
    print("=" * 60)

    config_loader = get_config_loader()
    status = config_loader.get_config_status()

    print(f"✓ .env文件: {status['env_file']}")
    print(f"✓ 文件存在: {status['env_file_exists']}")
    print(f"✓ API Key配置: {status['claude_api_key_configured']}")
    print(f"✓ 使用模型: {status['claude_model']}")

    if not status['claude_api_key_configured']:
        print("\n❌ 错误: API Key未配置")
        print("请创建.env文件并设置ANTHROPIC_API_KEY")
        return False

    print("\n✅ 配置加载成功")
    return True


def test_claude_provider():
    """测试Claude Provider"""
    print("\n" + "=" * 60)
    print("测试2: Claude Provider")
    print("=" * 60)

    try:
        # 创建Provider
        provider = ClaudeProvider()

        # 验证配置
        if not provider.validate_config():
            print("❌ Provider配置无效")
            return False

        print("✓ Provider创建成功")
        print(f"✓ 模型: {provider.model}")

        # 测试简单的API调用
        print("\n正在测试API调用...")
        response = provider.generate(
            prompt="请用一句话介绍你自己",
            max_tokens=100
        )

        print(f"✓ API调用成功")
        print(f"✓ 响应长度: {len(response.content)} 字符")
        print(f"✓ 使用Token: 输入={response.usage['input_tokens']}, 输出={response.usage['output_tokens']}")
        print(f"✓ 响应内容: {response.content[:100]}...")

        print("\n✅ Claude Provider测试通过")
        return True

    except Exception as e:
        print(f"\n❌ Claude Provider测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_ai_integration():
    """测试AI集成"""
    print("\n" + "=" * 60)
    print("测试3: AI集成")
    print("=" * 60)

    try:
        # 创建AI集成实例
        ai = AIIntegration()

        # 验证配置
        if not ai.validate_config():
            print("❌ AI配置无效")
            return False

        print("✓ AI集成创建成功")

        # 获取Provider信息
        info = ai.get_provider_info()
        print(f"✓ Provider: {info['provider']}")
        print(f"✓ 模型: {info['model']}")

        # 测试生成内容
        print("\n正在测试内容生成...")
        content = ai.generate_content(
            phase=Phase.BASIC_DESIGN,
            context={"project_name": "test_project"},
            max_tokens=500
        )

        print(f"✓ 内容生成成功")
        print(f"✓ 生成内容长度: {len(content)} 字符")
        print(f"✓ 内容预览:\n{content[:200]}...")

        # 测试评审内容
        print("\n正在测试内容评审...")
        review = ai.review_content(
            phase=Phase.BASIC_DESIGN,
            content="这是一个简单的测试内容",
            max_tokens=500
        )

        print(f"✓ 内容评审成功")
        print(f"✓ 评分: {review['score']}")
        print(f"✓ 问题数: {len(review['issues'])}")
        print(f"✓ 改进建议数: {len(review['improvements'])}")

        print("\n✅ AI集成测试通过")
        return True

    except Exception as e:
        print(f"\n❌ AI集成测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主测试函数"""
    print("🧪 Claude API集成测试")
    print("=" * 60)

    results = []

    # 测试1: 配置
    if test_config():
        results.append(True)

        # 测试2: Claude Provider
        if test_claude_provider():
            results.append(True)

            # 测试3: AI集成
            results.append(test_ai_integration())
        else:
            results.append(False)
    else:
        print("\n⚠️  跳过后续测试，请先配置API Key")
        return

    # 显示测试结果
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)

    test_names = ["配置加载", "Claude Provider", "AI集成"]
    for i, (name, result) in enumerate(zip(test_names, results), 1):
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{i}. {name}: {status}")

    all_passed = all(results)
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 所有测试通过！系统已准备就绪")
        print("=" * 60)
        print("\n下一步:")
        print("  1. 运行 python example_usage.py 查看完整示例")
        print("  2. 运行 python main.py auto --project 'my_project' 启动自动工作流")
    else:
        print("❌ 部分测试失败，请检查配置")
        print("=" * 60)


if __name__ == "__main__":
    main()
