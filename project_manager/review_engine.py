"""
评审引擎模块
负责对项目各阶段成果进行评审和评分
"""
from typing import Dict, List, Optional, Any
import json
import os
from datetime import datetime

from .models import (
    Phase, IssueLevel, Issue, ReviewResult, 
    PhaseConfig
)
from dataclasses import asdict


class ReviewEngine:
    """评审引擎类"""
    
    def __init__(self):
        self.current_issues: List[Issue] = []
        self.current_improvements: List[str] = []
    
    def evaluate(self, phase: Phase, content: str, file_path: Optional[str] = None) -> Dict[str, Any]:
        """
        评估指定阶段的内容
        
        Args:
            phase: 当前阶段
            content: 要评估的内容
            file_path: 文件路径（可选）
            
        Returns:
            评估结果字典
        """
        self.current_issues = []
        self.current_improvements = []
        
        # 根据阶段获取检查清单
        checklist = PhaseConfig.get_checklist_for_phase(phase)
        
        # 执行评估
        scores = self._evaluate_content(phase, content, checklist)
        
        # 计算总分（25分制）
        total_score = self.calculate_score(scores)
        
        # 生成评审结果
        result = ReviewResult(
            score=total_score,
            issues=self.current_issues,
            improvements=self.current_improvements,
            checklist=scores,
            phase=phase.value
        )
        
        return {
            'score': total_score,
            'issues': [asdict(issue) for issue in self.current_issues],
            'improvements': self.current_improvements,
            'checklist': scores,
            'review_date': result.review_date,
            'phase': phase.value
        }
    
    def get_critical_issues(self) -> List[Issue]:
        """获取Critical级别的问题"""
        return [issue for issue in self.current_issues if issue.level == IssueLevel.CRITICAL]
    
    def get_major_issues(self) -> List[Issue]:
        """获取Major级别的问题"""
        return [issue for issue in self.current_issues if issue.level == IssueLevel.MAJOR]
    
    def get_minor_issues(self) -> List[Issue]:
        """获取Minor级别的问题"""
        return [issue for issue in self.current_issues if issue.level == IssueLevel.MINOR]
    
    def get_next_improvement(self) -> str:
        """获取最重要的改进建议（只返回一个）"""
        if not self.current_improvements:
            return "当前阶段工作质量良好，无需改进"
        
        # 优先级：Critical > Major > Minor
        critical_issues = self.get_critical_issues()
        if critical_issues:
            return f"Critical问题：{critical_issues[0].description}"
        
        major_issues = self.get_major_issues()
        if major_issues:
            return f"Major问题：{major_issues[0].description}"
        
        return self.current_improvements[0]
    
    def calculate_score(self, checklist: Dict[str, float]) -> float:
        """计算总分（100分制）"""
        total_score = 0.0
        for item, score in checklist.items():
            total_score += score
        return round(total_score, 2)
    
    def _evaluate_content(self, phase: Phase, content: str, checklist: Dict[str, float]) -> Dict[str, float]:
        """评估内容并返回各项分数"""
        scores = {}
        
        if phase == Phase.BASIC_DESIGN:
            scores = self._evaluate_basic_design(content, checklist)
        elif phase == Phase.DETAIL_DESIGN:
            scores = self._evaluate_detail_design(content, checklist)
        elif phase == Phase.DEVELOPMENT:
            scores = self._evaluate_development(content, checklist)
        elif phase == Phase.UNIT_TEST:
            scores = self._evaluate_unit_test(content, checklist)
        elif phase == Phase.INTEGRATION_TEST:
            scores = self._evaluate_integration_test(content, checklist)
        
        return scores
    
    def _evaluate_basic_design(self, content: str, checklist: Dict[str, float]) -> Dict[str, float]:
        """评估基本设计文档"""
        scores = {}
        
        # 业务完整性评估
        if "业务" in content and ("流程" in content or "逻辑" in content or "需求" in content):
            scores["业务完整性"] = 30.0
        else:
            scores["业务完整性"] = 20.0
            self._add_issue(IssueLevel.MAJOR, "业务逻辑描述不完整")
        
        # 数据库设计评估
        if "数据库" in content and ("表" in content or "ER" in content or "字段" in content):
            scores["数据库设计"] = 25.0
        else:
            scores["数据库设计"] = 15.0
            self._add_issue(IssueLevel.MAJOR, "缺少数据库设计")
        
        # 架构合理性评估
        if "架构" in content and ("系统" in content or "模块" in content or "分层" in content):
            scores["架构合理性"] = 25.0
        else:
            scores["架构合理性"] = 15.0
            self._add_issue(IssueLevel.MAJOR, "系统架构设计不清晰")
        
        # 接口定义评估
        if "接口" in content and ("API" in content or "外部" in content or "协议" in content):
            scores["接口定义"] = 20.0
        else:
            scores["接口定义"] = 10.0
            self._add_issue(IssueLevel.MINOR, "建议增加接口定义")
        
        return scores
    
    def _evaluate_detail_design(self, content: str, checklist: Dict[str, float]) -> Dict[str, float]:
        """评估详细设计文档"""
        scores = {}
        
        # 类设计评估
        if "类" in content and ("方法" in content or "函数" in content or "类图" in content):
            scores["类设计"] = 30.0
        else:
            scores["类设计"] = 20.0
            self._add_issue(IssueLevel.MAJOR, "类设计不完整")
        
        # 数据结构评估
        if "数据结构" in content or "数据" in content or "类型" in content:
            scores["数据结构"] = 25.0
        else:
            scores["数据结构"] = 15.0
            self._add_issue(IssueLevel.MAJOR, "数据结构定义不清晰")
        
        # 算法合理性评估
        if "算法" in content or "伪代码" in content or "逻辑" in content:
            scores["算法合理性"] = 25.0
        else:
            scores["算法合理性"] = 15.0
            self._add_issue(IssueLevel.MAJOR, "缺少算法设计")
        
        # 模块耦合评估
        if "模块" in content or "耦合" in content or "依赖" in content:
            scores["模块耦合"] = 20.0
        else:
            scores["模块耦合"] = 10.0
            self._add_issue(IssueLevel.MINOR, "建议关注模块耦合度")
        
        return scores
    
    def _evaluate_development(self, content: str, checklist: Dict[str, float]) -> Dict[str, float]:
        """评估开发实现"""
        scores = {}
        
        # 功能完整性评估
        if "def " in content or "class " in content:
            scores["功能完整性"] = 35.0
        else:
            scores["功能完整性"] = 20.0
            self._add_issue(IssueLevel.CRITICAL, "缺少核心功能实现")
        
        # 代码规范评估
        if len(content.split('\n')) > 20:  # 基本代码结构
            scores["代码规范"] = 25.0
        else:
            scores["代码规范"] = 15.0
            self._add_issue(IssueLevel.MAJOR, "代码结构需要优化")
        
        # 异常处理评估
        if "try" in content or "except" in content or "error" in content:
            scores["异常处理"] = 20.0
        else:
            scores["异常处理"] = 10.0
            self._add_issue(IssueLevel.MINOR, "建议增加异常处理机制")
        
        # 性能评估
        if "性能" in content or "优化" in content or "效率" in content:
            scores["性能"] = 20.0
        else:
            scores["性能"] = 10.0
            self._add_issue(IssueLevel.MINOR, "建议关注性能优化")
        
        return scores
    
    def _evaluate_unit_test(self, content: str, checklist: Dict[str, float]) -> Dict[str, float]:
        """评估单元测试"""
        scores = {}
        
        # 覆盖率评估
        if "覆盖" in content or "coverage" in content.lower() or "覆盖率" in content:
            scores["覆盖率"] = 35.0
        else:
            scores["覆盖率"] = 20.0
            self._add_issue(IssueLevel.MINOR, "建议关注测试覆盖率")
        
        # 边界测试评估
        if "边界" in content or "edge" in content.lower() or "边界值" in content:
            scores["边界测试"] = 30.0
        else:
            scores["边界测试"] = 20.0
            self._add_issue(IssueLevel.MINOR, "建议增加边界测试")
        
        # 异常测试评估
        if "异常" in content or "exception" in content.lower() or "错误" in content:
            scores["异常测试"] = 35.0
        else:
            scores["异常测试"] = 20.0
            self._add_issue(IssueLevel.MINOR, "建议增加异常测试")
        
        return scores
    
    def _evaluate_integration_test(self, content: str, checklist: Dict[str, float]) -> Dict[str, float]:
        """评估集成测试"""
        scores = {}
        
        # 集成完整性评估
        if "集成" in content or "integration" in content.lower() or "模块" in content:
            scores["集成完整性"] = 40.0
        else:
            scores["集成完整性"] = 25.0
            self._add_issue(IssueLevel.MAJOR, "缺少模块集成测试")
        
        # 性能达标评估
        if "性能" in content or "performance" in content.lower() or "效率" in content:
            scores["性能达标"] = 30.0
        else:
            scores["性能达标"] = 15.0
            self._add_issue(IssueLevel.MINOR, "建议增加性能测试")
        
        # 稳定性评估
        if "稳定" in content or "stability" in content.lower() or "可靠性" in content:
            scores["稳定性"] = 30.0
        else:
            scores["稳定性"] = 15.0
            self._add_issue(IssueLevel.MINOR, "建议关注系统稳定性")
        
        return scores
    
    def _add_issue(self, level: IssueLevel, description: str, line_number: Optional[int] = None):
        """添加问题"""
        issue = Issue(
            level=level,
            description=description,
            line_number=line_number
        )
        self.current_issues.append(issue)
        
        # 同时添加到改进建议
        if level == IssueLevel.MINOR:
            self.current_improvements.append(description)
        elif level == IssueLevel.MAJOR:
            self.current_improvements.append(f"必须修复: {description}")
        elif level == IssueLevel.CRITICAL:
            self.current_improvements.append(f"需回退: {description}")
    
    def check_phase_transition(self, phase: Phase, score: float, issues: List[Issue]) -> bool:
        """检查是否可以进入下一阶段"""
        max_iterations = PhaseConfig.get_max_iterations(phase)
        pass_threshold = PhaseConfig.get_pass_threshold(phase)
        
        # 检查Critical问题
        critical_issues = [issue for issue in issues if issue.level == IssueLevel.CRITICAL]
        if critical_issues:
            return False
        
        # 检查分数阈值
        if score < pass_threshold:
            return False
        
        return True
    
    def should_rollback(self, phase: Phase, issues: List[Issue]) -> Optional[Phase]:
        """检查是否需要回退"""
        critical_issues = [issue for issue in issues if issue.level == IssueLevel.CRITICAL]
        if not critical_issues:
            return None
        
        # 获取可以回退到的阶段
        rollback_targets = PhaseConfig.can_rollback_to(phase)
        if rollback_targets:
            return rollback_targets[0]  # 回退到第一个可回退的阶段
        
        return None
