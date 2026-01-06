#!/usr/bin/env python3
"""
AI驱动的项目开发流程管理系统
主程序入口
"""

import sys
import argparse
from pathlib import Path
from typing import Optional

from project_manager import ProjectManager, Phase, Mode
from project_manager.auto_workflow import AutoWorkflow


def print_banner():
    """打印程序横幅"""
    print("=" * 60)
    print("🤖 AI驱动的项目开发流程管理系统")
    print("=" * 60)
    print("支持双模式管理：Developer Mode 和 Reviewer Mode")
    print("阶段：BASIC_DESIGN → DETAIL_DESIGN → DEVELOPMENT")
    print("=" * 60)


def print_status(manager: ProjectManager):
    """打印项目状态"""
    status = manager.get_current_status()
    print(f"\n📊 项目状态：{status['project_name']}")
    print(f"📍 当前阶段：{status['current_phase']}")
    print(f"🔄 迭代次数：{status['phase_iteration']}")
    print(f"🎯 当前模式：{status['current_mode']}")
    print(f"📈 项目状态：{status['status']}")
    if status['latest_score']:
        print(f"⭐ 最新评分：{status['latest_score']}分")
    print(f"🚫 阻塞问题：{status['blocked_issues_count']}个")
    print(f"💡 改进建议：{status['improvements_count']}个")
    print(f"📝 评审次数：{status['review_count']}次")
    if status['from_rollback']:
        print(f"⚠️  来自回退：是")
        if status['rollback_reason']:
            print(f"🔄 回退原因：{status['rollback_reason']}")
    print(f"🔄 回退次数：{status['rollback_count']}次")
    print(f"🔒 质量门禁：{status['quality_gates']}")


def interactive_mode(project_name: str):
    """交互式模式"""
    print_banner()
    
    try:
        manager = ProjectManager(project_name)
        print(f"✅ 项目 '{project_name}' 初始化成功")
        
        while True:
            print_status(manager)
            
            print("\n🔧 可用操作：")
            print("1. 切换到开发模式")
            print("2. 切换到评审模式")
            print("3. 执行当前阶段任务")
            print("4. 评审当前阶段成果")
            print("5. 检查阶段转换条件")
            print("6. 强制进入下一阶段")
            print("7. 进入下一次迭代")
            print("8. 导出项目报告")
            print("9. 运行自动化工作流")
            print("10. 运行智能工作流")
            print("11. 运行持续改进工作流")
            print("12. 退出")
            
            choice = input("\n请选择操作 (1-12): ").strip()
            
            if choice == "1":
                manager.set_mode("developer")
                print("✅ 已切换到开发模式")
                
            elif choice == "2":
                manager.set_mode("reviewer")
                print("✅ 已切换到评审模式")
                
            elif choice == "3":
                try:
                    result = manager.execute_phase()
                    print(f"✅ 执行结果：{result}")
                except Exception as e:
                    print(f"❌ 执行失败：{e}")
                    
            elif choice == "4":
                try:
                    result = manager.review_phase()
                    print(f"📊 评审结果：")
                    print(f"   总分：{result['score']}分")
                    print(f"   问题数：{len(result['issues'])}个")
                    print(f"   改进建议：{len(result['improvements'])}个")
                    
                    if result['improvements']:
                        print(f"   最重要改进：{result['improvements'][0]}")
                except Exception as e:
                    print(f"❌ 评审失败：{e}")
                    
            elif choice == "5":
                can_transition = manager.check_phase_transition()
                if can_transition:
                    print("✅ 可以进入下一阶段")
                else:
                    print("❌ 还不能进入下一阶段")
                    
            elif choice == "6":
                manager.force_next_phase()
                print("⚠️  已强制进入下一阶段")
                
            elif choice == "7":
                manager.next_iteration()
                print("✅ 已进入下一次迭代")
                
            elif choice == "8":
                report_file = manager.export_report()
                print(f"📄 项目报告已导出：{report_file}")
                
            elif choice == "9":
                try:
                    auto_workflow = AutoWorkflow(project_name)
                    result = auto_workflow.run_auto_workflow()
                    print(f"🤖 自动化工作流完成：{result['status']}")
                except Exception as e:
                    print(f"❌ 自动化工作流失败：{e}")
                    
            elif choice == "10":
                try:
                    target_score = float(input("请输入目标分数 (默认85.0): ") or "85.0")
                    auto_workflow = AutoWorkflow(project_name)
                    result = auto_workflow.run_smart_workflow(target_score)
                    print(f"🧠 智能工作流完成：{result['status']}")
                except Exception as e:
                    print(f"❌ 智能工作流失败：{e}")
                    
            elif choice == "11":
                try:
                    max_phases = int(input("请输入最大阶段数 (默认5): ") or "5")
                    auto_workflow = AutoWorkflow(project_name)
                    result = auto_workflow.run_continuous_improvement(max_phases)
                    print(f"🚀 持续改进工作流完成：{result['status']}")
                except Exception as e:
                    print(f"❌ 持续改进工作流失败：{e}")
                    
            elif choice == "12":
                print("👋 再见！")
                break
                
            else:
                print("❌ 无效选择，请重新输入")
                
    except Exception as e:
        print(f"❌ 初始化失败：{e}")
        sys.exit(1)


def init_project(project_name: str):
    """初始化项目"""
    try:
        manager = ProjectManager(project_name)
        print(f"✅ 项目 '{project_name}' 初始化成功")
        print_status(manager)
    except Exception as e:
        print(f"❌ 初始化失败：{e}")
        sys.exit(1)

def define_requirements_mode(project_name: str, requirements: str):
    """要件定义模式"""
    try:
        manager = ProjectManager(project_name)
        print(f"🔧 开始定义项目要件：{project_name}")
        print(f"📝 需求描述：{requirements}")
        
        result = manager.define_requirements(requirements)
        
        print(f"✅ 要件定义完成！")
        print(f"📊 技术栈：{result['requirements']['tech_stack']['language']}")
        if result['requirements']['tech_stack']['framework']:
            print(f"🏗️  框架：{result['requirements']['tech_stack']['framework']}")
        if result['requirements']['tech_stack']['database']:
            print(f"🗄️  数据库：{result['requirements']['tech_stack']['database']}")
        print(f"🚀 部署平台：{result['requirements']['deployment']['platform']}")
        
        print(f"📁 生成的配置文件：")
        for config_type, file_path in result['config_files'].items():
            print(f"   - {config_type}: {file_path}")
        
        print_status(manager)
    except Exception as e:
        print(f"❌ 要件定义失败：{e}")
        sys.exit(1)

def get_requirements_mode(project_name: str):
    """获取要件配置模式"""
    try:
        manager = ProjectManager(project_name)
        requirements = manager.get_requirements()
        
        if not requirements:
            print(f"❌ 项目 '{project_name}' 尚未定义要件")
            return
        
        print(f"📋 项目要件配置：{project_name}")
        print(f"🔧 技术栈：{requirements['tech_stack']['language']}")
        if requirements['tech_stack']['framework']:
            print(f"🏗️  框架：{requirements['tech_stack']['framework']}")
        if requirements['tech_stack']['database']:
            print(f"🗄️  数据库：{requirements['tech_stack']['database']}")
        print(f"🚀 部署平台：{requirements['deployment']['platform']}")
        print(f"📊 项目类型：{requirements['project_type']}")
        
    except Exception as e:
        print(f"❌ 获取要件失败：{e}")
        sys.exit(1)

def dev_mode(project_name: str, phase: str):
    """开发模式"""
    try:
        manager = ProjectManager(project_name)
        manager.set_mode("developer")
        
        if phase != "current":
            # 这里可以添加阶段切换逻辑
            pass
        
        result = manager.execute_phase()
        print(f"✅ 开发执行结果：{result}")
        print_status(manager)
    except Exception as e:
        print(f"❌ 开发模式失败：{e}")
        sys.exit(1)

def review_mode(project_name: str, phase: str):
    """评审模式"""
    try:
        manager = ProjectManager(project_name)
        manager.set_mode("reviewer")
        
        if phase != "current":
            # 这里可以添加阶段切换逻辑
            pass
        
        result = manager.review_phase()
        print(f"📊 评审结果：")
        print(f"   总分：{result['score']}分")
        print(f"   问题数：{len(result['issues'])}个")
        print(f"   改进建议：{len(result['improvements'])}个")
        
        if result['improvements']:
            print(f"   最重要改进：{result['improvements'][0]}")
        
        print_status(manager)
    except Exception as e:
        print(f"❌ 评审模式失败：{e}")
        sys.exit(1)

def status_mode(project_name: str):
    """状态查看模式"""
    try:
        manager = ProjectManager(project_name)
        print_status(manager)
    except Exception as e:
        print(f"❌ 状态查看失败：{e}")
        sys.exit(1)

def report_mode(project_name: str):
    """报告生成模式"""
    try:
        manager = ProjectManager(project_name)
        report_file = manager.export_report()
        print(f"📄 项目报告已导出：{report_file}")
    except Exception as e:
        print(f"❌ 报告生成失败：{e}")
        sys.exit(1)

def auto_workflow_mode(project_name: str):
    """自动化工作流模式"""
    try:
        auto_workflow = AutoWorkflow(project_name)
        result = auto_workflow.run_auto_workflow()
        print(f"🤖 自动化工作流完成：{result['status']}")
        print(f"📊 完成阶段数：{len(result['phases_completed'])}")
        print(f"🔄 总迭代次数：{result['total_iterations']}")
        if result['final_score']:
            print(f"⭐ 最终评分：{result['final_score']}分")
    except Exception as e:
        print(f"❌ 自动化工作流失败：{e}")
        sys.exit(1)

def smart_workflow_mode(project_name: str, target_score: float):
    """智能工作流模式"""
    try:
        auto_workflow = AutoWorkflow(project_name)
        result = auto_workflow.run_smart_workflow(target_score)
        print(f"🧠 智能工作流完成：{result['status']}")
        print(f"📊 完成阶段数：{len(result['phases_completed'])}")
        print(f"🔄 总迭代次数：{result['total_iterations']}")
        if result['final_score']:
            print(f"⭐ 最终评分：{result['final_score']}分")
    except Exception as e:
        print(f"❌ 智能工作流失败：{e}")
        sys.exit(1)

def continuous_improvement_mode(project_name: str, max_phases: int):
    """持续改进工作流模式"""
    try:
        auto_workflow = AutoWorkflow(project_name)
        result = auto_workflow.run_continuous_improvement(max_phases)
        print(f"🚀 持续改进工作流完成：{result['status']}")
        print(f"📊 完成阶段数：{len(result['phases_completed'])}")
        print(f"🔄 总迭代次数：{result['total_iterations']}")
        if result['final_score']:
            print(f"⭐ 最终评分：{result['final_score']}分")
    except Exception as e:
        print(f"❌ 持续改进工作流失败：{e}")
        sys.exit(1)


def demo_mode():
    """演示模式"""
    print_banner()
    print("🎬 开始演示模式...")
    
    project_name = "demo_project"
    
    try:
        manager = ProjectManager(project_name)
        print(f"✅ 创建演示项目：{project_name}")
        
        # 演示基本设计阶段
        print("\n🎨 阶段1：基本设计阶段")
        manager.set_mode("developer")
        result = manager.execute_phase()
        print(f"   生成基本设计文档：{result}")
        
        manager.set_mode("reviewer")
        review_result = manager.review_phase()
        print(f"   评审结果：{review_result['score']}分")
        
        # 演示详细设计阶段
        print("\n📋 阶段2：详细设计阶段")
        manager.force_next_phase()
        manager.set_mode("developer")
        result = manager.execute_phase()
        print(f"   生成详细设计文档：{result}")
        
        manager.set_mode("reviewer")
        review_result = manager.review_phase()
        print(f"   评审结果：{review_result['score']}分")
        
        # 演示开发阶段
        print("\n💻 阶段3：开发阶段")
        manager.force_next_phase()
        manager.set_mode("developer")
        result = manager.execute_phase()
        print(f"   生成代码实现：{result}")
        
        manager.set_mode("reviewer")
        review_result = manager.review_phase()
        print(f"   评审结果：{review_result['score']}分")
        
        # 演示单元测试阶段
        print("\n🧪 阶段4：单元测试阶段")
        manager.force_next_phase()
        manager.set_mode("developer")
        result = manager.execute_phase()
        print(f"   生成单元测试用例：{result}")
        
        manager.set_mode("reviewer")
        review_result = manager.review_phase()
        print(f"   评审结果：{review_result['score']}分")
        
        # 演示集成测试阶段
        print("\n🔗 阶段5：集成测试阶段")
        manager.force_next_phase()
        manager.set_mode("developer")
        result = manager.execute_phase()
        print(f"   生成集成测试用例：{result}")
        
        manager.set_mode("reviewer")
        review_result = manager.review_phase()
        print(f"   评审结果：{review_result['score']}分")
        
        # 导出报告
        print("\n📄 导出项目报告")
        report_file = manager.export_report()
        print(f"   报告文件：{report_file}")
        
        print("\n🎉 演示完成！")
        
    except Exception as e:
        print(f"❌ 演示失败：{e}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="AI驱动的项目开发流程管理系统",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例：
  python main.py init --project "我的项目"     # 初始化项目
  python main.py define --project "我的项目" --requirements "使用Python和Django开发一个Web应用，使用PostgreSQL数据库，部署到AWS"  # 定义项目要件
  python main.py requirements --project "我的项目"  # 查看项目要件
  python main.py dev --phase current              # 执行开发模式
  python main.py review --phase current           # 执行评审模式
  python main.py status                           # 查看状态
  python main.py report                           # 生成报告
  python main.py auto --project "我的项目"          # 运行自动化工作流
  python main.py smart --project "我的项目" --score 85.0  # 运行智能工作流
  python main.py improve --project "我的项目" --phases 5  # 运行持续改进工作流
  python main.py demo                             # 运行演示模式
        """
    )
    
    parser.add_argument(
        "command",
        choices=["init", "dev", "review", "status", "report", "auto", "smart", "improve", "demo", "define", "requirements"],
        help="命令类型"
    )
    
    parser.add_argument(
        "--project", "-p",
        help="项目名称"
    )
    
    parser.add_argument(
        "--phase", "-ph",
        choices=["current", "basic_design", "detail_design", "development"],
        default="current",
        help="指定阶段 (默认: current)"
    )
    
    parser.add_argument(
        "--score", "-s",
        type=float,
        default=85.0,
        help="智能工作流目标分数 (默认: 85.0)"
    )
    
    parser.add_argument(
        "--phases", "-phases",
        type=int,
        default=5,
        help="持续改进工作流最大阶段数 (默认: 5)"
    )
    
    parser.add_argument(
        "--requirements", "-r",
        help="项目要件描述（自然语言）"
    )
    
    args = parser.parse_args()
    
    # 处理演示模式
    if args.command == "demo":
        demo_mode()
        return
    
    # 处理初始化命令
    if args.command == "init":
        if not args.project:
            print("❌ 错误：初始化项目需要指定 --project")
            parser.print_help()
            sys.exit(1)
        init_project(args.project)
        return
    
    # 其他命令需要项目名称
    if not args.project:
        print("❌ 错误：需要指定 --project")
        parser.print_help()
        sys.exit(1)
    
    # 处理其他命令
    if args.command == "dev":
        dev_mode(args.project, args.phase)
    elif args.command == "review":
        review_mode(args.project, args.phase)
    elif args.command == "status":
        status_mode(args.project)
    elif args.command == "report":
        report_mode(args.project)
    elif args.command == "auto":
        auto_workflow_mode(args.project)
    elif args.command == "smart":
        smart_workflow_mode(args.project, args.score)
    elif args.command == "improve":
        continuous_improvement_mode(args.project, args.phases)
    elif args.command == "define":
        if not args.requirements:
            print("❌ 错误：要件定义需要指定 --requirements")
            parser.print_help()
            sys.exit(1)
        define_requirements_mode(args.project, args.requirements)
    elif args.command == "requirements":
        get_requirements_mode(args.project)
    else:
        print("❌ 错误：无效的命令")
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
