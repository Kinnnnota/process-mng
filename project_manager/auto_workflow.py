"""
自动化工作流模块
实现AI自动推进项目进度，最小化手动干预
"""
import time
from typing import Dict, Any, Optional
from datetime import datetime

from .project_manager import ProjectManager
from .models import Phase, Mode


class AutoWorkflow:
    """自动化工作流管理器"""
    
    def __init__(self, project_name: str, auto_mode: bool = True):
        """
        初始化自动化工作流
        
        Args:
            project_name: 项目名称
            auto_mode: 是否启用自动模式
        """
        self.project_name = project_name
        self.manager = ProjectManager(project_name)
        self.auto_mode = auto_mode
        self.max_auto_iterations = 10  # 最大自动迭代次数
        self.auto_iteration_count = 0
        
    def run_auto_workflow(self) -> Dict[str, Any]:
        """
        运行自动化工作流
        
        Returns:
            工作流执行结果
        """
        print(f"🤖 开始自动化工作流：{self.project_name}")
        print(f"🔄 自动模式：{'启用' if self.auto_mode else '禁用'}")
        
        workflow_result = {
            'project_name': self.project_name,
            'start_time': datetime.now().isoformat(),
            'phases_completed': [],
            'total_iterations': 0,
            'final_score': None,
            'status': 'IN_PROGRESS'
        }
        
        try:
            while self.auto_iteration_count < self.max_auto_iterations:
                self.auto_iteration_count += 1
                print(f"\n🔄 第 {self.auto_iteration_count} 次自动迭代")
                
                # 检查项目状态
                status = self.manager.get_current_status()
                print(f"📍 当前阶段：{status['current_phase']}")
                print(f"📊 当前评分：{status['latest_score']}")
                
                # 检查是否需要回退
                rollback_target = self.manager.check_rollback_needed()
                if rollback_target:
                    print(f"⚠️  检测到需要回退到：{rollback_target.value}")
                    self.manager.rollback_to_phase(rollback_target, "自动检测到Critical问题")
                    continue
                
                # 执行当前阶段
                phase_result = self._execute_current_phase()
                workflow_result['total_iterations'] += 1
                
                # 检查是否可以进入下一阶段
                if self.manager.check_phase_transition():
                    print(f"✅ 阶段 {status['current_phase']} 完成，准备进入下一阶段")
                    self.manager.force_next_phase()
                    
                    # 记录完成的阶段
                    workflow_result['phases_completed'].append({
                        'phase': status['current_phase'],
                        'score': status['latest_score'],
                        'iterations': status['phase_iteration']
                    })
                    
                    # 检查是否完成所有阶段
                    new_status = self.manager.get_current_status()
                    if new_status['status'] == 'COMPLETED':
                        print("🎉 所有阶段已完成！")
                        workflow_result['status'] = 'COMPLETED'
                        workflow_result['final_score'] = new_status['latest_score']
                        break
                else:
                    print(f"🔄 阶段 {status['current_phase']} 需要继续迭代")
                    self.manager.next_iteration()
                
                # 短暂延迟，避免过于频繁的操作
                time.sleep(1)
            
            # 检查是否因为达到最大迭代次数而停止
            if self.auto_iteration_count >= self.max_auto_iterations:
                print(f"⚠️  达到最大自动迭代次数：{self.max_auto_iterations}")
                workflow_result['status'] = 'MAX_ITERATIONS_REACHED'
            
        except Exception as e:
            print(f"❌ 自动化工作流执行失败：{e}")
            workflow_result['status'] = 'ERROR'
            workflow_result['error'] = str(e)
        
        workflow_result['end_time'] = datetime.now().isoformat()
        return workflow_result
    
    def _execute_current_phase(self) -> Dict[str, Any]:
        """
        执行当前阶段（开发 + 评审）
        
        Returns:
            阶段执行结果
        """
        status = self.manager.get_current_status()
        current_phase = status['current_phase']
        
        print(f"🎨 执行阶段：{current_phase}")
        
        # 1. 开发模式 - 生成内容
        print("   📝 开发模式：生成内容...")
        self.manager.set_mode("developer")
        dev_result = self.manager.execute_phase()
        print(f"   ✅ 开发完成：{dev_result[:100]}...")
        
        # 2. 评审模式 - 评估内容
        print("   🔍 评审模式：评估内容...")
        self.manager.set_mode("reviewer")
        review_result = self.manager.review_phase()
        print(f"   📊 评审完成：{review_result['score']}分")
        
        # 3. 显示评审详情
        if review_result['issues']:
            print("   ⚠️  发现的问题：")
            for issue in review_result['issues']:
                print(f"      - {issue['level']}: {issue['description']}")
        
        if review_result['improvements']:
            print("   💡 改进建议：")
            for improvement in review_result['improvements']:
                print(f"      - {improvement}")
        
        return {
            'phase': current_phase,
            'dev_result': dev_result,
            'review_result': review_result
        }
    
    def run_smart_workflow(self, target_score: float = 85.0) -> Dict[str, Any]:
        """
        智能工作流 - 达到目标分数后自动进入下一阶段
        
        Args:
            target_score: 目标分数
            
        Returns:
            工作流执行结果
        """
        print(f"🧠 开始智能工作流：{self.project_name}")
        print(f"🎯 目标分数：{target_score}")
        
        workflow_result = {
            'project_name': self.project_name,
            'target_score': target_score,
            'start_time': datetime.now().isoformat(),
            'phases_completed': [],
            'total_iterations': 0,
            'final_score': None,
            'status': 'IN_PROGRESS'
        }
        
        try:
            while self.auto_iteration_count < self.max_auto_iterations:
                self.auto_iteration_count += 1
                print(f"\n🔄 第 {self.auto_iteration_count} 次智能迭代")
                
                # 检查项目状态
                status = self.manager.get_current_status()
                current_score = status['latest_score']
                
                print(f"📍 当前阶段：{status['current_phase']}")
                print(f"📊 当前评分：{current_score}")
                print(f"🎯 目标分数：{target_score}")
                
                # 检查是否需要回退
                rollback_target = self.manager.check_rollback_needed()
                if rollback_target:
                    print(f"⚠️  检测到需要回退到：{rollback_target.value}")
                    self.manager.rollback_to_phase(rollback_target, "自动检测到Critical问题")
                    continue
                
                # 执行当前阶段
                phase_result = self._execute_current_phase()
                workflow_result['total_iterations'] += 1
                
                # 检查是否达到目标分数
                if current_score and current_score >= target_score:
                    print(f"🎉 达到目标分数 {target_score}，准备进入下一阶段")
                    self.manager.force_next_phase()
                    
                    # 记录完成的阶段
                    workflow_result['phases_completed'].append({
                        'phase': status['current_phase'],
                        'score': current_score,
                        'iterations': status['phase_iteration']
                    })
                    
                    # 检查是否完成所有阶段
                    new_status = self.manager.get_current_status()
                    if new_status['status'] == 'COMPLETED':
                        print("🎉 所有阶段已完成！")
                        workflow_result['status'] = 'COMPLETED'
                        workflow_result['final_score'] = new_status['latest_score']
                        break
                else:
                    print(f"🔄 未达到目标分数，继续迭代")
                    self.manager.next_iteration()
                
                # 短暂延迟
                time.sleep(1)
            
            # 检查是否因为达到最大迭代次数而停止
            if self.auto_iteration_count >= self.max_auto_iterations:
                print(f"⚠️  达到最大智能迭代次数：{self.max_auto_iterations}")
                workflow_result['status'] = 'MAX_ITERATIONS_REACHED'
        
        except Exception as e:
            print(f"❌ 智能工作流执行失败：{e}")
            workflow_result['status'] = 'ERROR'
            workflow_result['error'] = str(e)
        
        workflow_result['end_time'] = datetime.now().isoformat()
        return workflow_result
    
    def run_continuous_improvement(self, max_phases: int = 5) -> Dict[str, Any]:
        """
        持续改进工作流 - 在达到通过分数后继续改进
        
        Args:
            max_phases: 最大阶段数
            
        Returns:
            工作流执行结果
        """
        print(f"🚀 开始持续改进工作流：{self.project_name}")
        
        workflow_result = {
            'project_name': self.project_name,
            'start_time': datetime.now().isoformat(),
            'phases_completed': [],
            'total_iterations': 0,
            'final_score': None,
            'status': 'IN_PROGRESS'
        }
        
        try:
            phase_count = 0
            while phase_count < max_phases and self.auto_iteration_count < self.max_auto_iterations:
                self.auto_iteration_count += 1
                print(f"\n🔄 第 {self.auto_iteration_count} 次改进迭代")
                
                # 检查项目状态
                status = self.manager.get_current_status()
                current_score = status['latest_score']
                
                print(f"📍 当前阶段：{status['current_phase']}")
                print(f"📊 当前评分：{current_score}")
                
                # 检查是否需要回退
                rollback_target = self.manager.check_rollback_needed()
                if rollback_target:
                    print(f"⚠️  检测到需要回退到：{rollback_target.value}")
                    self.manager.rollback_to_phase(rollback_target, "自动检测到Critical问题")
                    continue
                
                # 执行当前阶段
                phase_result = self._execute_current_phase()
                workflow_result['total_iterations'] += 1
                
                # 检查是否可以进入下一阶段
                if self.manager.check_phase_transition():
                    print(f"✅ 阶段 {status['current_phase']} 完成，准备进入下一阶段")
                    self.manager.force_next_phase()
                    phase_count += 1
                    
                    # 记录完成的阶段
                    workflow_result['phases_completed'].append({
                        'phase': status['current_phase'],
                        'score': current_score,
                        'iterations': status['phase_iteration']
                    })
                    
                    # 检查是否完成所有阶段
                    new_status = self.manager.get_current_status()
                    if new_status['status'] == 'COMPLETED':
                        print("🎉 所有阶段已完成！")
                        workflow_result['status'] = 'COMPLETED'
                        workflow_result['final_score'] = new_status['latest_score']
                        break
                else:
                    print(f"🔄 继续改进当前阶段")
                    self.manager.next_iteration()
                
                # 短暂延迟
                time.sleep(1)
            
            # 检查是否因为达到最大迭代次数而停止
            if self.auto_iteration_count >= self.max_auto_iterations:
                print(f"⚠️  达到最大改进迭代次数：{self.max_auto_iterations}")
                workflow_result['status'] = 'MAX_ITERATIONS_REACHED'
        
        except Exception as e:
            print(f"❌ 持续改进工作流执行失败：{e}")
            workflow_result['status'] = 'ERROR'
            workflow_result['error'] = str(e)
        
        workflow_result['end_time'] = datetime.now().isoformat()
        return workflow_result
    
    def get_workflow_status(self) -> Dict[str, Any]:
        """
        获取工作流状态
        
        Returns:
            工作流状态信息
        """
        status = self.manager.get_current_status()
        return {
            'project_name': self.project_name,
            'auto_mode': self.auto_mode,
            'auto_iteration_count': self.auto_iteration_count,
            'max_auto_iterations': self.max_auto_iterations,
            'project_status': status,
            'remaining_iterations': self.max_auto_iterations - self.auto_iteration_count
        }
