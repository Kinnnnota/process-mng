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
    """评审引擎类 - 无状态黑箱评审"""

    def __init__(self):
        """
        初始化评审引擎
        注意: 此类设计为无状态,每次评审都是独立的黑箱过程
        不保存任何历史信息到实例变量
        """
        pass
    
    def evaluate(self, phase: Phase, content: str, file_path: Optional[str] = None) -> Dict[str, Any]:
        """
        评估指定阶段的内容 (黑箱评审 - 无状态)

        Args:
            phase: 当前阶段
            content: 要评估的内容
            file_path: 文件路径（可选）

        Returns:
            评审结果字典,包含所有issue和改进建议
        """
        # 使用局部变量而非实例变量,确保无状态
        issues: List[Issue] = []
        improvements: List[str] = []

        # 根据阶段获取检查清单
        checklist = PhaseConfig.get_checklist_for_phase(phase)

        # 执行评估 - 传递局部变量列表
        scores = self._evaluate_content(phase, content, checklist, issues, improvements)

        # 计算总分（100分制）
        total_score = self.calculate_score(scores)

        # 生成评审结果
        result = ReviewResult(
            score=total_score,
            issues=issues,
            improvements=improvements,
            checklist=scores,
            phase=phase.value
        )

        return {
            'score': total_score,
            'issues': [asdict(issue) for issue in issues],
            'improvements': improvements,
            'checklist': scores,
            'review_date': result.review_date,
            'phase': phase.value,
            'content': content,  # 保存内容以供后续分析使用
            'file_path': file_path
        }
    
    @staticmethod
    def get_critical_issues(issues: List[Issue]) -> List[Issue]:
        """获取Critical级别的问题"""
        return [issue for issue in issues if issue.level == IssueLevel.CRITICAL]

    @staticmethod
    def get_major_issues(issues: List[Issue]) -> List[Issue]:
        """获取Major级别的问题"""
        return [issue for issue in issues if issue.level == IssueLevel.MAJOR]

    @staticmethod
    def get_minor_issues(issues: List[Issue]) -> List[Issue]:
        """获取Minor级别的问题"""
        return [issue for issue in issues if issue.level == IssueLevel.MINOR]

    @staticmethod
    def get_next_improvement(issues: List[Issue], improvements: List[str]) -> str:
        """获取最重要的改进建议（只返回一个）"""
        if not improvements:
            return "当前阶段工作质量良好，无需改进"

        # 优先级：Critical > Major > Minor
        critical_issues = ReviewEngine.get_critical_issues(issues)
        if critical_issues:
            return f"Critical问题：{critical_issues[0].description}"

        major_issues = ReviewEngine.get_major_issues(issues)
        if major_issues:
            return f"Major问题：{major_issues[0].description}"

        return improvements[0]
    
    @staticmethod
    def generate_detailed_analysis(issue: Issue, content: str) -> Dict[str, str]:
        """
        生成详细的问题分析

        Args:
            issue: 问题对象
            content: 评审的内容

        Returns:
            包含四个维度的详细分析
        """
        analysis = {
            'problem_code': ReviewEngine._extract_problem_code(issue, content),
            'problem_reason': ReviewEngine._analyze_problem_reason(issue),
            'solution_method': ReviewEngine._provide_solution_method(issue),
            'precautions': ReviewEngine._list_precautions(issue)
        }
        return analysis

    @staticmethod
    def _extract_problem_code(issue: Issue, content: str) -> str:
        """提取问题代码片段"""
        if not content:
            return "无法提取代码片段"

        lines = content.split('\n')
        
        # 如果有行号，提取该行及上下文
        if issue.line_number and 0 < issue.line_number <= len(lines):
            start_line = max(0, issue.line_number - 3)
            end_line = min(len(lines), issue.line_number + 2)
            context_lines = lines[start_line:end_line]
            
            code_snippet = "\n".join([
                f"{i+start_line+1:4d}: {line}" 
                for i, line in enumerate(context_lines)
            ])
            return code_snippet
        
        # 根据问题描述关键词查找相关代码
        keywords = ReviewEngine._extract_keywords_from_description(issue.description)
        for i, line in enumerate(lines):
            if any(keyword in line for keyword in keywords):
                start_line = max(0, i - 2)
                end_line = min(len(lines), i + 3)
                context_lines = lines[start_line:end_line]

                code_snippet = "\n".join([
                    f"{j+start_line+1:4d}: {line}"
                    for j, line in enumerate(context_lines)
                ])
                return code_snippet

        return "相关代码片段未找到"

    @staticmethod
    def _extract_keywords_from_description(description: str) -> List[str]:
        """从问题描述中提取关键词"""
        keywords = []
        
        # 根据问题类型提取关键词
        if "函数" in description or "方法" in description:
            keywords.extend(["def ", "class ", "return"])
        elif "异常" in description or "错误" in description:
            keywords.extend(["try", "except", "raise", "error"])
        elif "性能" in description:
            keywords.extend(["for", "while", "import", "time"])
        elif "规范" in description:
            keywords.extend(["def", "class", "import", "from"])
        elif "测试" in description:
            keywords.extend(["test", "assert", "def test"])
        
        return keywords
    
    @staticmethod
    def _analyze_problem_reason(issue: Issue) -> str:
        """分析问题原因"""
        description = issue.description.lower()
        
        if "功能" in description or "实现" in description:
            return "核心功能实现不完整或逻辑错误，可能导致系统无法正常工作"
        elif "异常" in description or "错误" in description:
            return "缺少异常处理机制，可能导致程序崩溃或数据丢失"
        elif "性能" in description:
            return "算法复杂度高或资源使用不当，可能影响系统响应速度"
        elif "规范" in description:
            return "代码风格不符合PEP 8规范，影响代码可读性和维护性"
        elif "测试" in description:
            return "测试覆盖不全面，无法保证代码质量和功能正确性"
        elif "架构" in description:
            return "系统架构设计不合理，可能影响系统的可扩展性和维护性"
        elif "接口" in description:
            return "接口定义不清晰，可能导致模块间通信问题"
        else:
            return "代码质量需要改进，可能影响系统的稳定性和可维护性"
    
    @staticmethod
    def _provide_solution_method(issue: Issue) -> str:
        """提供修改方法"""
        description = issue.description.lower()
        
        if "功能" in description or "实现" in description:
            return """1. 检查核心业务逻辑是否正确
2. 确保所有功能点都有对应的实现
3. 添加必要的参数验证和边界条件处理
4. 完善函数返回值处理"""
        elif "异常" in description or "错误" in description:
            return """1. 添加try-except异常处理块
2. 对可能出错的操作进行防御性编程
3. 提供有意义的错误信息
4. 记录错误日志便于调试"""
        elif "性能" in description:
            return """1. 优化算法复杂度
2. 减少不必要的循环和计算
3. 使用更高效的数据结构
4. 考虑缓存机制"""
        elif "规范" in description:
            return """1. 遵循PEP 8编码规范
2. 统一命名风格（snake_case）
3. 添加适当的空行和注释
4. 控制函数和类的复杂度"""
        elif "测试" in description:
            return """1. 增加单元测试用例
2. 覆盖边界条件和异常情况
3. 提高测试覆盖率
4. 添加集成测试"""
        elif "架构" in description:
            return """1. 重新设计系统架构
2. 明确模块职责和边界
3. 降低模块间耦合度
4. 提高系统可扩展性"""
        elif "接口" in description:
            return """1. 明确接口参数和返回值
2. 定义清晰的API文档
3. 统一接口命名规范
4. 添加接口版本控制"""
        else:
            return """1. 分析具体问题原因
2. 制定改进计划
3. 逐步优化代码质量
4. 进行充分测试验证"""
    
    @staticmethod
    def _list_precautions(issue: Issue) -> str:
        """列出注意事项"""
        description = issue.description.lower()
        
        precautions = []
        
        if "功能" in description or "实现" in description:
            precautions.extend([
                "修改前需要充分理解业务逻辑",
                "确保修改不影响其他功能模块",
                "需要同步更新相关文档",
                "修改后必须进行回归测试"
            ])
        elif "异常" in description or "错误" in description:
            precautions.extend([
                "异常处理不要过于宽泛",
                "避免在异常处理中隐藏真正的错误",
                "确保异常信息对用户友好",
                "注意异常处理的性能影响"
            ])
        elif "性能" in description:
            precautions.extend([
                "性能优化前需要先进行性能分析",
                "避免过度优化影响代码可读性",
                "注意内存泄漏和资源释放",
                "性能改进需要量化验证"
            ])
        elif "规范" in description:
            precautions.extend([
                "代码规范修改需要团队统一",
                "避免为了规范而规范",
                "保持代码风格的一致性",
                "使用自动化工具检查规范"
            ])
        elif "测试" in description:
            precautions.extend([
                "测试用例需要维护和更新",
                "避免测试用例之间的依赖",
                "测试数据需要清理和隔离",
                "注意测试环境的配置"
            ])
        elif "架构" in description:
            precautions.extend([
                "架构修改需要评估影响范围",
                "确保向后兼容性",
                "需要充分的迁移计划",
                "考虑性能和稳定性影响"
            ])
        elif "接口" in description:
            precautions.extend([
                "接口修改需要版本控制",
                "确保接口的向后兼容",
                "需要更新接口文档",
                "注意接口的安全性"
            ])
        else:
            precautions.extend([
                "修改前需要充分评估影响",
                "确保修改的可回滚性",
                "需要充分的测试验证",
                "注意代码的可维护性"
            ])
        
        return "\n".join([f"- {precaution}" for precaution in precautions])
    
    @staticmethod
    def generate_formatted_review_report(
        phase: Phase,
        issues: List[Issue],
        checklist: Dict[str, float],
        total_score: float,
        content: str
    ) -> str:
        """
        生成格式化的评审报告

        Args:
            phase: 当前阶段
            issues: 发现的问题列表
            checklist: 检查项得分
            total_score: 总分
            content: 评审内容

        Returns:
            格式化的评审报告
        """
        report = []
        report.append(f"# {phase.value} 阶段评审报告")
        report.append(f"**评审时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"**评审阶段**: {phase.value}")
        report.append("")

        # 添加总分
        report.append(f"**总分**: {total_score}分")
        report.append("")

        # 添加检查项得分
        report.append("**检查项得分**:")
        for item, score in checklist.items():
            report.append(f"- {item}: {score}分")
        report.append("")

        # 添加发现的问题
        if issues:
            report.append("**发现的问题**:")
            for issue in issues:
                report.append(f"- [{issue.level.value}] {issue.description}")
            report.append("")

        # 添加最重要的改进建议（包含详细分析）
        if issues:
            most_important_issue = ReviewEngine._get_most_important_issue(issues)
            if most_important_issue:
                report.append("**最重要的改进建议**:")
                report.append("")

                analysis = ReviewEngine.generate_detailed_analysis(most_important_issue, content)

                report.append("## 问题分析")
                report.append("")
                report.append("### 1. 问题代码")
                report.append("```")
                report.append(analysis['problem_code'])
                report.append("```")
                report.append("")
                report.append("### 2. 问题原因")
                report.append(analysis['problem_reason'])
                report.append("")
                report.append("### 3. 修改方法")
                report.append(analysis['solution_method'])
                report.append("")
                report.append("### 4. 注意事项")
                report.append(analysis['precautions'])
        else:
            report.append("**最重要的改进建议**: 当前阶段工作质量良好，无需改进")

        return "\n".join(report)

    @staticmethod
    def _get_most_important_issue(issues: List[Issue]) -> Optional[Issue]:
        """获取最重要的问题"""
        critical_issues = ReviewEngine.get_critical_issues(issues)
        if critical_issues:
            return critical_issues[0]

        major_issues = ReviewEngine.get_major_issues(issues)
        if major_issues:
            return major_issues[0]

        minor_issues = ReviewEngine.get_minor_issues(issues)
        if minor_issues:
            return minor_issues[0]

        return None
    
    @staticmethod
    def calculate_score(checklist: Dict[str, float]) -> float:
        """计算总分（100分制）"""
        total_score = 0.0
        for item, score in checklist.items():
            total_score += score
        return round(total_score, 2)

    def _evaluate_content(
        self,
        phase: Phase,
        content: str,
        checklist: Dict[str, float],
        issues: List[Issue],
        improvements: List[str]
    ) -> Dict[str, float]:
        """评估内容并返回各项分数（仅核心开发阶段）"""
        scores = {}

        if phase == Phase.BASIC_DESIGN:
            scores = self._evaluate_basic_design(content, checklist, issues, improvements)
        elif phase == Phase.DETAIL_DESIGN:
            scores = self._evaluate_detail_design(content, checklist, issues, improvements)
        elif phase == Phase.DEVELOPMENT:
            scores = self._evaluate_development(content, checklist, issues, improvements)

        return scores
    
    def _evaluate_basic_design(
        self,
        content: str,
        checklist: Dict[str, float],
        issues: List[Issue],
        improvements: List[str]
    ) -> Dict[str, float]:
        """评估基本设计文档"""
        scores = {}

        # 业务完整性评估
        if "业务" in content and ("流程" in content or "逻辑" in content or "需求" in content):
            scores["业务完整性"] = 30.0
        else:
            scores["业务完整性"] = 20.0
            self._add_issue(IssueLevel.MAJOR, "业务逻辑描述不完整", issues, improvements)

        # 数据库设计评估
        if "数据库" in content and ("表" in content or "ER" in content or "字段" in content):
            scores["数据库设计"] = 25.0
        else:
            scores["数据库设计"] = 15.0
            self._add_issue(IssueLevel.MAJOR, "缺少数据库设计", issues, improvements)

        # 架构合理性评估
        if "架构" in content and ("系统" in content or "模块" in content or "分层" in content):
            scores["架构合理性"] = 25.0
        else:
            scores["架构合理性"] = 15.0
            self._add_issue(IssueLevel.MAJOR, "系统架构设计不清晰", issues, improvements)

        # 接口定义评估
        if "接口" in content and ("API" in content or "外部" in content or "协议" in content):
            scores["接口定义"] = 20.0
        else:
            scores["接口定义"] = 10.0
            self._add_issue(IssueLevel.MINOR, "建议增加接口定义", issues, improvements)

        return scores
    
    def _evaluate_detail_design(
        self,
        content: str,
        checklist: Dict[str, float],
        issues: List[Issue],
        improvements: List[str]
    ) -> Dict[str, float]:
        """评估详细设计文档"""
        scores = {}

        # 类设计评估
        if "类" in content and ("方法" in content or "函数" in content or "类图" in content):
            scores["类设计"] = 30.0
        else:
            scores["类设计"] = 20.0
            self._add_issue(IssueLevel.MAJOR, "类设计不完整", issues, improvements)

        # 数据结构评估
        if "数据结构" in content or "数据" in content or "类型" in content:
            scores["数据结构"] = 25.0
        else:
            scores["数据结构"] = 15.0
            self._add_issue(IssueLevel.MAJOR, "数据结构定义不清晰", issues, improvements)

        # 算法合理性评估
        if "算法" in content or "伪代码" in content or "逻辑" in content:
            scores["算法合理性"] = 25.0
        else:
            scores["算法合理性"] = 15.0
            self._add_issue(IssueLevel.MAJOR, "缺少算法设计", issues, improvements)

        # 模块耦合评估
        if "模块" in content or "耦合" in content or "依赖" in content:
            scores["模块耦合"] = 20.0
        else:
            scores["模块耦合"] = 10.0
            self._add_issue(IssueLevel.MINOR, "建议关注模块耦合度", issues, improvements)

        return scores
    
    def _evaluate_development(
        self,
        content: str,
        checklist: Dict[str, float],
        issues: List[Issue],
        improvements: List[str]
    ) -> Dict[str, float]:
        """评估开发实现"""
        scores = {}

        # 功能完整性评估
        if "def " in content or "class " in content:
            scores["功能完整性"] = 35.0
        else:
            scores["功能完整性"] = 20.0
            self._add_issue(IssueLevel.CRITICAL, "缺少核心功能实现", issues, improvements)

        # 代码规范评估
        if len(content.split('\n')) > 20:  # 基本代码结构
            scores["代码规范"] = 25.0
        else:
            scores["代码规范"] = 15.0
            self._add_issue(IssueLevel.MAJOR, "代码结构需要优化", issues, improvements)

        # 异常处理评估
        if "try" in content or "except" in content or "error" in content:
            scores["异常处理"] = 20.0
        else:
            scores["异常处理"] = 10.0
            self._add_issue(IssueLevel.MINOR, "建议增加异常处理机制", issues, improvements)

        # 性能评估
        if "性能" in content or "优化" in content or "效率" in content:
            scores["性能"] = 20.0
        else:
            scores["性能"] = 10.0
            self._add_issue(IssueLevel.MINOR, "建议关注性能优化", issues, improvements)

        return scores

    # 测试阶段评审方法已移除 - 留待人工确认

    @staticmethod
    def _add_issue(
        level: IssueLevel,
        description: str,
        issues: List[Issue],
        improvements: List[str],
        line_number: Optional[int] = None
    ):
        """添加问题"""
        issue = Issue(
            level=level,
            description=description,
            line_number=line_number
        )
        issues.append(issue)

        # 同时添加到改进建议
        if level == IssueLevel.MINOR:
            improvements.append(description)
        elif level == IssueLevel.MAJOR:
            improvements.append(f"必须修复: {description}")
        elif level == IssueLevel.CRITICAL:
            improvements.append(f"需回退: {description}")
    
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
