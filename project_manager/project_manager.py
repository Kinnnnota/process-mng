"""
项目管理器主模块
负责项目状态管理、模式切换、阶段执行等核心功能
"""
import json
import os
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path

from .models import (
    ProjectState, Phase, Mode, IssueLevel, Issue, ReviewResult,
    PhaseConfig
)
from .review_engine import ReviewEngine
from .requirements_engine import RequirementsEngine
from .issue_storage import IssueStorage
from .ai_integration import AIIntegration


class ProjectManager:
    """项目管理器主类"""
    
    def __init__(self, project_name: str):
        """
        初始化项目管理器
        
        Args:
            project_name: 项目名称
        """
        self.project_name = project_name
        self.project_dir = Path(f"project_manager/{project_name}")
        self.state_file = self.project_dir / "project_state.json"
        self.review_history_file = self.project_dir / "review_history.md"
        self.phase_outputs_dir = self.project_dir / "phase_outputs"
        
        # 创建目录结构
        self._create_project_structure()
        
        # 初始化评审引擎
        self.review_engine = ReviewEngine()

        # 初始化要件定义引擎
        self.requirements_engine = RequirementsEngine()

        # 初始化Issue存储管理器
        self.issue_storage = IssueStorage(self.project_dir)

        # 初始化AI集成
        self.ai_integration = AIIntegration(project_name=project_name)

        # 加载或创建项目状态
        self.state = self._load_or_create_state()
    
    def set_mode(self, mode: str) -> None:
        """
        设置当前模式
        
        Args:
            mode: "developer" 或 "reviewer"
        """
        if mode not in ["developer", "reviewer"]:
            raise ValueError("模式必须是 'developer' 或 'reviewer'")
        
        self.state.current_mode = Mode(mode)
        self.state.updated_at = datetime.now().isoformat()
        self._save_state()
    
    def execute_phase(self) -> str:
        """
        执行当前阶段任务
        
        Returns:
            生成的内容或状态信息
        """
        if self.state.current_mode == Mode.DEVELOPER:
            return self._execute_developer_phase()
        else:
            return "当前为评审模式，无法执行开发任务"
    
    def review_phase(self) -> Dict[str, Any]:
        """
        评审当前阶段成果 (黑箱评审 - 不依赖历史)

        Returns:
            评审结果字典
        """
        if self.state.current_mode != Mode.REVIEWER:
            raise ValueError("当前不是评审模式")

        # 读取当前阶段的输出文件
        content = self._read_phase_output()

        # 执行黑箱评审 - 不传递任何历史信息
        review_result = self.review_engine.evaluate(
            self.state.current_phase,
            content
        )

        # 将issue对象转换
        issues = [Issue(**issue) for issue in review_result['issues']]

        # 保存本次评审的issue到文件
        self.issue_storage.save_review_issues(
            phase=self.state.current_phase,
            iteration=self.state.phase_iteration + 1,
            issues=issues
        )

        # 更新阻塞issue文件
        critical_issues = [issue for issue in issues if issue.level == IssueLevel.CRITICAL]
        if critical_issues:
            self.issue_storage.add_blocked_issues(critical_issues)

        # 生成规整化的评审报告
        formatted_report = ReviewEngine.generate_formatted_review_report(
            phase=self.state.current_phase,
            issues=issues,
            checklist=review_result['checklist'],
            total_score=review_result['score'],
            content=content
        )

        # 更新项目状态
        self.state.phase_scores.append(review_result['score'])
        self.state.updated_at = datetime.now().isoformat()

        # 添加评审历史 (不包含issue,从文件读取)
        review_result_obj = ReviewResult(
            score=review_result['score'],
            issues=issues,  # 仅用于历史记录
            improvements=review_result['improvements'],
            checklist=review_result['checklist'],
            review_date=review_result['review_date'],
            phase=self.state.current_phase.value,
            iteration=self.state.phase_iteration + 1
        )
        self.state.review_history.append(review_result_obj)

        # 更新改进建议 (仅保留最新的)
        self.state.improvements = review_result['improvements']

        # 保存状态
        self._save_state()

        # 更新评审历史文件
        self._update_review_history(review_result)

        # 将规整化报告添加到返回结果中
        review_result['formatted_report'] = formatted_report

        return review_result
    
    def check_phase_transition(self) -> bool:
        """
        检查是否可以进入下一阶段
        
        Returns:
            是否可以进入下一阶段
        """
        if not self.state.review_history:
            return False
        
        latest_review = self.state.review_history[-1]
        
        # 检查是否达到最大迭代次数
        max_iterations = PhaseConfig.get_max_iterations(self.state.current_phase)
        if self.state.phase_iteration >= max_iterations:
            return True
        
        # 检查通过条件
        return self.review_engine.check_phase_transition(
            self.state.current_phase,
            latest_review.score,
            latest_review.issues
        )
    
    def force_next_phase(self) -> None:
        """强制进入下一阶段"""
        phase_order = [Phase.BASIC_DESIGN, Phase.DETAIL_DESIGN, Phase.DEVELOPMENT]
        current_index = phase_order.index(self.state.current_phase)
        
        if current_index < len(phase_order) - 1:
            self.state.current_phase = phase_order[current_index + 1]
            self.state.phase_iteration = 0
            self.state.status = "IN_PROGRESS"
            self.state.updated_at = datetime.now().isoformat()
            self._save_state()
            
            print(f"⚠️  警告：强制进入下一阶段 {self.state.current_phase.value}")
        else:
            self.state.status = "COMPLETED"
            self.state.updated_at = datetime.now().isoformat()
            self._save_state()
            print("🎉 项目已完成所有阶段")
    
    def next_iteration(self) -> None:
        """进入下一次迭代"""
        self.state.phase_iteration += 1
        self.state.status = "IN_PROGRESS"
        self.state.updated_at = datetime.now().isoformat()
        self._save_state()
    
    def rollback_to_phase(self, target_phase: Phase, reason: str = "") -> None:
        """回退到指定阶段"""
        # 检查是否可以回退到目标阶段
        rollback_targets = PhaseConfig.can_rollback_to(self.state.current_phase)
        if target_phase not in rollback_targets:
            raise ValueError(f"无法从 {self.state.current_phase.value} 回退到 {target_phase.value}")
        
        # 更新状态
        self.state.current_phase = target_phase
        self.state.phase_iteration = 0
        self.state.status = "IN_PROGRESS"
        self.state.from_rollback = True
        self.state.rollback_reason = reason
        self.state.rollback_count += 1
        self.state.quality_gates["total_rollbacks"] += 1
        self.state.updated_at = datetime.now().isoformat()
        
        # 更新阶段历史
        self.state.phase_history[target_phase.value].rollback_count += 1
        
        self._save_state()
        print(f"⚠️  回退到阶段：{target_phase.value}，原因：{reason}")
    
    def check_rollback_needed(self) -> Optional[Phase]:
        """检查是否需要回退"""
        if not self.state.review_history:
            return None
        
        latest_review = self.state.review_history[-1]
        
        # 检查Critical问题
        critical_issues = [issue for issue in latest_review.issues if issue.level == IssueLevel.CRITICAL]
        if critical_issues:
            # 获取回退触发条件
            rollback_conditions = PhaseConfig.get_rollback_conditions(self.state.current_phase)
            
            # 检查是否匹配回退条件
            for issue in critical_issues:
                for condition in rollback_conditions:
                    if condition.lower() in issue.description.lower():
                        return self.review_engine.should_rollback(self.state.current_phase, latest_review.issues)
        
        return None
    
    def get_current_status(self) -> Dict[str, Any]:
        """
        获取当前项目状态 (从文件读取issue信息)

        Returns:
            项目状态字典
        """
        return {
            'project_name': self.state.project_name,
            'current_phase': self.state.current_phase.value,
            'phase_iteration': self.state.phase_iteration,
            'current_mode': self.state.current_mode.value,
            'status': self.state.status,
            'latest_score': self.state.phase_scores[-1] if self.state.phase_scores else None,
            'blocked_issues_count': self.issue_storage.get_blocked_issues_count(),  # 从文件读取
            'improvements_count': len(self.state.improvements),
            'review_count': len(self.state.review_history),
            'from_rollback': self.state.from_rollback,
            'rollback_reason': self.state.rollback_reason,
            'rollback_count': self.state.rollback_count,
            'quality_gates': self.state.quality_gates,
            'created_at': self.state.created_at,
            'updated_at': self.state.updated_at
        }

    def get_blocked_issues(self) -> List[Issue]:
        """
        获取当前所有阻塞的issue (从文件读取)

        Returns:
            阻塞issue列表
        """
        return self.issue_storage.load_blocked_issues()

    def clear_blocked_issues(self) -> None:
        """清空所有阻塞issue"""
        self.issue_storage.clear_blocked_issues()
    
    def define_requirements(self, natural_language: str) -> Dict[str, Any]:
        """
        定义项目要件
        
        Args:
            natural_language: 自然语言描述
            
        Returns:
            要件配置和生成的文件路径
        """
        # 解析自然语言描述
        requirements = self.requirements_engine.parse_requirements(natural_language)
        
        # 生成配置文件
        config_files = self.requirements_engine.generate_config_files(requirements, self.project_name)
        
        # 更新项目状态
        if not hasattr(self.state, 'requirements'):
            self.state.requirements = {}
        self.state.requirements.update(requirements)
        self.state.updated_at = datetime.now().isoformat()
        self._save_state()
        
        return {
            'requirements': requirements,
            'config_files': config_files
        }
    
    def get_requirements(self) -> Dict[str, Any]:
        """
        获取项目要件配置
        
        Returns:
            要件配置字典
        """
        return getattr(self.state, 'requirements', {})
    
    def update_requirements(self, natural_language: str) -> Dict[str, Any]:
        """
        更新项目要件
        
        Args:
            natural_language: 新的自然语言描述
            
        Returns:
            更新后的要件配置
        """
        return self.define_requirements(natural_language)
    
    def export_report(self) -> str:
        """
        导出项目报告
        
        Returns:
            报告文件路径
        """
        report_file = self.project_dir / f"{self.project_name}_report.md"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(f"# {self.project_name} 项目报告\n\n")
            f.write(f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # 项目概览
            f.write("## 项目概览\n\n")
            status = self.get_current_status()
            f.write(f"- 项目名称：{status['project_name']}\n")
            f.write(f"- 当前阶段：{status['current_phase']}\n")
            f.write(f"- 阶段迭代：{status['phase_iteration']}\n")
            f.write(f"- 项目状态：{status['status']}\n")
            f.write(f"- 评审次数：{status['review_count']}\n\n")
            
            # 阶段评分历史
            f.write("## 阶段评分历史\n\n")
            for i, score in enumerate(self.state.phase_scores):
                f.write(f"- 第{i+1}次评审：{score}分\n")
            f.write("\n")
            
            # 阻塞问题
            if self.state.blocked_issues:
                f.write("## 阻塞问题\n\n")
                for issue in self.state.blocked_issues:
                    f.write(f"- **{issue.level.value}**：{issue.description}\n")
                f.write("\n")
            
            # 改进建议
            if self.state.improvements:
                f.write("## 改进建议\n\n")
                for improvement in self.state.improvements:
                    f.write(f"- {improvement}\n")
                f.write("\n")
            
            # 详细评审历史
            f.write("## 详细评审历史\n\n")
            for i, review in enumerate(self.state.review_history):
                f.write(f"### 第{i+1}次评审 ({review.review_date})\n\n")
                f.write(f"**总分：{review.score}分**\n\n")
                
                f.write("**检查项得分：**\n")
                for item, score in review.checklist.items():
                    f.write(f"- {item}：{score}分\n")
                f.write("\n")
                
                if review.issues:
                    f.write("**发现的问题：**\n")
                    for issue in review.issues:
                        f.write(f"- {issue.level.value}：{issue.description}\n")
                    f.write("\n")
        
        return str(report_file)
    
    def _create_project_structure(self) -> None:
        """创建项目目录结构"""
        # 创建主目录
        self.project_dir.mkdir(parents=True, exist_ok=True)
        
        # 创建阶段输出目录
        for phase in ["basic_design", "detail_design", "development", "unit_test", "integration_test"]:
            (self.phase_outputs_dir / phase).mkdir(parents=True, exist_ok=True)
    
    def _load_or_create_state(self) -> ProjectState:
        """加载或创建项目状态"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if content:  # 检查文件是否为空
                        data = json.loads(content)
                        return ProjectState.from_dict(data)
                    else:
                        # 文件为空，创建新状态
                        pass
            except (json.JSONDecodeError, FileNotFoundError):
                # JSON解析错误或文件不存在，创建新状态
                pass
        
        # 创建新状态 (blocked_issues已移除,存储在文件中)
        state = ProjectState(
            project_name=self.project_name,
            current_phase=Phase.BASIC_DESIGN,
            phase_iteration=0,
            current_mode=Mode.DEVELOPER,
            status="IN_PROGRESS",
            phase_scores=[],
            improvements=[],
            review_history=[],
            created_at=datetime.now().isoformat()
        )
        # 直接保存状态，不调用self._save_state()
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(state.to_dict(), f, ensure_ascii=False, indent=2)
        return state
    
    def _save_state(self) -> None:
        """保存项目状态"""
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(self.state.to_dict(), f, ensure_ascii=False, indent=2)
    
    def _execute_developer_phase(self) -> str:
        """
        执行开发者模式任务 - 使用AI生成内容

        Returns:
            生成的内容
        """
        phase = self.state.current_phase
        iteration = self.state.phase_iteration

        # 检查AI配置
        if not self.ai_integration.validate_config():
            raise RuntimeError(
                "AI配置无效。请设置ANTHROPIC_API_KEY环境变量或创建.env文件。"
                "参考.env.example文件进行配置。"
            )

        try:
            # 获取项目上下文
            context = self.ai_integration.get_current_context()

            print(f"🤖 使用AI生成 {phase.value} 内容...")

            # 使用AI生成内容
            content = self.ai_integration.generate_content(
                phase=phase,
                context=context
            )

            # 保存生成的内容到文件
            self._save_phase_output(content, phase, iteration)

            print(f"✅ {phase.value} 内容生成完成")

            return content

        except Exception as e:
            # 如果AI生成失败,回退到模板生成
            print(f"⚠️  AI生成失败: {e}")
            print(f"🔄 回退到模板生成...")
            return self._generate_template_content(phase, iteration)

    def _generate_template_content(self, phase: Phase, iteration: int) -> str:
        """
        使用模板生成内容(回退方案)

        Args:
            phase: 项目阶段
            iteration: 迭代次数

        Returns:
            生成的模板内容
        """
        if phase == Phase.BASIC_DESIGN:
            return self._generate_basic_design_document(iteration)
        elif phase == Phase.DETAIL_DESIGN:
            return self._generate_detail_design_document(iteration)
        elif phase == Phase.DEVELOPMENT:
            return self._generate_code_implementation(iteration)
        else:
            return f"# {phase.value} 模板内容\n\n待生成..."

    def _save_phase_output(self, content: str, phase: Phase, iteration: int) -> None:
        """
        保存阶段输出到文件

        Args:
            content: 输出内容
            phase: 项目阶段
            iteration: 迭代次数
        """
        # 创建输出目录
        output_dir = self.phase_outputs_dir / phase.value.lower()
        output_dir.mkdir(parents=True, exist_ok=True)

        # 根据阶段确定文件名和扩展名
        if phase == Phase.BASIC_DESIGN:
            filename = f"basic_design_v{iteration + 1}.md"
        elif phase == Phase.DETAIL_DESIGN:
            filename = f"detail_design_v{iteration + 1}.md"
        elif phase == Phase.DEVELOPMENT:
            filename = f"implementation_v{iteration + 1}.py"
        else:
            filename = f"output_v{iteration + 1}.md"

        output_file = output_dir / filename

        # 写入文件
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"📁 输出已保存: {output_file}")

    def _generate_basic_design_document(self, iteration: int) -> str:
        """生成基本设计文档"""
        content = f"""# {self.project_name} 基本设计文档 (第{iteration + 1}次迭代)

## 1. 项目概述
本项目是一个AI驱动的项目开发流程管理系统，支持双模式管理。

## 2. 系统架构
### 2.1 整体架构
- 项目管理器 (ProjectManager)
- 评审引擎 (ReviewEngine)
- 状态管理 (ProjectState)

### 2.2 核心模块
- **项目管理器**：负责项目状态管理和流程控制
- **评审引擎**：负责代码评审和评分
- **数据模型**：定义项目状态和数据结构

## 3. 接口设计
### 3.1 ProjectManager接口
- `set_mode(mode)`: 设置开发/评审模式
- `execute_phase()`: 执行当前阶段任务
- `review_phase()`: 评审当前阶段成果
- `check_phase_transition()`: 检查阶段转换条件

### 3.2 ReviewEngine接口
- `evaluate(phase, content)`: 评估内容
- `get_critical_issues()`: 获取关键问题
- `get_next_improvement()`: 获取改进建议

## 4. 数据结构
### 4.1 项目状态
```json
{{
    "project_name": "项目名称",
    "current_phase": "当前阶段",
    "phase_iteration": "迭代次数",
    "status": "项目状态"
}}
```

## 5. 异常处理
- 文件读写异常处理
- 状态转换异常处理
- 评审过程异常处理

## 6. 扩展性设计
- 支持自定义评审规则
- 支持多种输出格式
- 支持插件化扩展
"""
        
        # 保存设计文档
        design_file = self.phase_outputs_dir / "basic_design" / f"basic_design_v{iteration + 1}.md"
        with open(design_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        self.state.status = "READY_FOR_REVIEW"
        self._save_state()
        
        return f"基本设计文档已生成：{design_file}"
    
    def _generate_code_implementation(self, iteration: int) -> str:
        """生成代码实现"""
        content = f"""# {self.project_name} 代码实现 (第{iteration + 1}次迭代)

import json
import os
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path

class ProjectManager:
    \"\"\"项目管理器主类\"\"\"
    
    def __init__(self, project_name: str):
        self.project_name = project_name
        self.project_dir = Path(f"project_manager/{{project_name}}")
        self.state_file = self.project_dir / "project_state.json"
        self.review_engine = ReviewEngine()
        self.state = self._load_or_create_state()
    
    def set_mode(self, mode: str) -> None:
        \"\"\"设置当前模式\"\"\"
        if mode not in ["developer", "reviewer"]:
            raise ValueError("模式必须是 'developer' 或 'reviewer'")
        self.state.current_mode = Mode(mode)
        self._save_state()
    
    def execute_phase(self) -> str:
        \"\"\"执行当前阶段任务\"\"\"
        if self.state.current_mode == Mode.DEVELOPER:
            return self._execute_developer_phase()
        else:
            return "当前为评审模式，无法执行开发任务"
    
    def review_phase(self) -> Dict[str, Any]:
        \"\"\"评审当前阶段成果\"\"\"
        if self.state.current_mode != Mode.REVIEWER:
            raise ValueError("当前不是评审模式")
        
        content = self._read_phase_output()
        review_result = self.review_engine.evaluate(
            self.state.current_phase, 
            content
        )
        
        # 更新项目状态
        self.state.phase_scores.append(review_result['score'])
        self._save_state()
        
        return review_result
    
    def _save_state(self) -> None:
        \"\"\"保存项目状态\"\"\"
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(self.state.to_dict(), f, ensure_ascii=False, indent=2)

class ReviewEngine:
    \"\"\"评审引擎类\"\"\"
    
    def __init__(self):
        self.current_issues = []
        self.current_improvements = []
    
    def evaluate(self, phase: Phase, content: str) -> Dict[str, Any]:
        \"\"\"评估指定阶段的内容\"\"\"
        checklist = self._get_checklist_for_phase(phase)
        scores = self._evaluate_content(phase, content, checklist)
        total_score = self.calculate_score(scores)
        
        return {{
            'score': total_score,
            'issues': [asdict(issue) for issue in self.current_issues],
            'improvements': self.current_improvements,
            'checklist': scores
        }}
    
    def calculate_score(self, checklist: Dict[str, float]) -> float:
        \"\"\"计算总分\"\"\"
        total_score = 0.0
        for item, score in checklist.items():
            total_score += score
        return round(total_score, 2)
    
    def get_next_improvement(self) -> str:
        \"\"\"获取最重要的改进建议\"\"\"
        if not self.current_improvements:
            return "当前阶段工作质量良好，无需改进"
        
        critical_issues = self.get_critical_issues()
        if critical_issues:
            return f"Critical问题：{{critical_issues[0].description}}"
        
        return self.current_improvements[0]

# 错误处理示例
try:
    manager = ProjectManager("test_project")
    manager.set_mode("developer")
    result = manager.execute_phase()
    print(result)
except Exception as e:
    print(f"错误：{{e}}")
    # 记录错误日志
    with open("error.log", "a") as f:
        f.write(f"{{datetime.now()}}: {{e}}\\n")
"""
        
        # 保存代码文件
        code_file = self.phase_outputs_dir / "development" / f"implementation_v{iteration + 1}.py"
        with open(code_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        self.state.status = "READY_FOR_REVIEW"
        self._save_state()
        
        return f"代码实现已生成：{code_file}"
    
    def _generate_detail_design_document(self, iteration: int) -> str:
        """生成详细设计文档"""
        content = f"""# {self.project_name} 详细设计文档 (第{iteration + 1}次迭代)

## 1. 代码架构
### 1.1 类图设计
```mermaid
classDiagram
    class ProjectManager {{{{
        +project_name: str
        +state: ProjectState
        +review_engine: ReviewEngine
        +set_mode(mode)
        +execute_phase()
        +review_phase()
    }}}}
    
    class ReviewEngine {{{{
        +current_issues: List[Issue]
        +current_improvements: List[str]
        +evaluate(phase, content)
        +get_critical_issues()
        +get_next_improvement()
    }}}}
    
    class ProjectState {{{{
        +project_name: str
        +current_phase: Phase
        +phase_iteration: int
        +current_mode: Mode
        +status: str
        +to_dict()
        +from_dict()
    }}}}
    
    ProjectManager --> ProjectState
    ProjectManager --> ReviewEngine
```

## 2. 核心算法
### 2.1 评审算法伪代码
```
function evaluate(phase, content):
    checklist = get_checklist_for_phase(phase)
    scores = {{}}
    
    for item in checklist:
        score = evaluate_item(content, item)
        scores[item] = score
        
        if score < threshold:
            add_issue(level, description)
    
    total_score = calculate_total_score(scores)
    return {{score: total_score, issues: issues, improvements: improvements}}
```

## 3. 数据结构定义
### 3.1 核心数据结构
```python
@dataclass
class Issue:
    level: IssueLevel
    description: str
    line_number: Optional[int]
    file_path: Optional[str]
    created_at: str

@dataclass
class ReviewResult:
    score: float
    issues: List[Issue]
    improvements: List[str]
    checklist: Dict[str, float]
    review_date: str

@dataclass
class ProjectState:
    project_name: str
    current_phase: Phase
    phase_iteration: int
    current_mode: Mode
    status: str
    phase_scores: List[float]
    blocked_issues: List[Issue]
    improvements: List[str]
    review_history: List[ReviewResult]
    created_at: str
    updated_at: str
    from_rollback: bool
    rollback_count: int
    phase_history: Dict[str, PhaseHistory]
```

## 4. 关键流程时序图
### 4.1 评审流程
```mermaid
sequenceDiagram
    participant U as User
    participant PM as ProjectManager
    participant RE as ReviewEngine
    participant FS as FileSystem
    
    U->>PM: set_mode("reviewer")
    PM->>FS: read_phase_output()
    FS-->>PM: content
    PM->>RE: evaluate(phase, content)
    RE-->>PM: review_result
    PM->>FS: save_state()
    PM-->>U: review_result
```

## 5. 异常处理策略
### 5.1 异常分类
- **文件异常**: 文件不存在、权限不足、格式错误
- **状态异常**: 状态转换失败、数据不一致
- **评审异常**: 内容解析失败、评分计算错误

### 5.2 处理策略
```python
try:
    # 执行操作
    result = operation()
except FileNotFoundError:
    # 创建默认文件
    create_default_file()
except PermissionError:
    # 提示用户权限问题
    show_permission_error()
except Exception as e:
    # 记录错误日志
    log_error(e)
    # 返回错误信息
    return error_response(e)
```
"""
        
        # 保存设计文档
        design_file = self.phase_outputs_dir / "detail_design" / f"detail_design_v{iteration + 1}.md"
        with open(design_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        self.state.status = "READY_FOR_REVIEW"
        self._save_state()
        
        return f"详细设计文档已生成：{design_file}"
    
    def _read_phase_output(self) -> str:
        """读取当前阶段的输出文件"""
        phase_name = self.state.current_phase.value
        iteration = self.state.phase_iteration
        
        # 首先尝试查找带版本号的文件
        if self.state.current_phase == Phase.BASIC_DESIGN:
            file_patterns = [f"basic_design_v{iteration + 1}.md", f"{phase_name}.md"]
        elif self.state.current_phase == Phase.DETAIL_DESIGN:
            file_patterns = [f"detail_design_v{iteration + 1}.md", f"{phase_name}.md"]
        elif self.state.current_phase == Phase.DEVELOPMENT:
            file_patterns = [f"implementation_v{iteration + 1}.py", f"{phase_name}.py", f"{phase_name}.md"]
        else:
            file_patterns = [f"output_v{iteration + 1}.md", f"{phase_name}.md"]
        
        # 尝试查找文件
        for file_pattern in file_patterns:
            output_file = self.phase_outputs_dir / file_pattern
            if output_file.exists():
                try:
                    with open(output_file, 'r', encoding='utf-8') as f:
                        return f.read()
                except Exception as e:
                    print(f"读取文件失败: {e}")
                    continue
        
        # 如果找不到文件，返回默认内容
        return f"# {self.state.current_phase.value} 阶段输出\n\n当前阶段暂无输出内容。"
    
    def _update_review_history(self, review_result: Dict[str, Any]) -> None:
        """更新评审历史文件"""
        with open(self.review_history_file, 'a', encoding='utf-8') as f:
            f.write(f"## 第{len(self.state.review_history)}次评审 ({review_result['review_date']})\n\n")
            f.write(f"**阶段：** {self.state.current_phase.value}\n")
            f.write(f"**迭代：** {self.state.phase_iteration + 1}\n")
            f.write(f"**总分：** {review_result['score']}/25分\n\n")
            
            f.write("**专项评分：**\n")
            for item, score in review_result['checklist'].items():
                f.write(f"- {item}：{score}/25分\n")
            f.write("\n")
            
            if review_result['issues']:
                f.write("**问题分级：**\n")
                critical_issues = [issue for issue in review_result['issues'] if issue['level'] == 'CRITICAL']
                major_issues = [issue for issue in review_result['issues'] if issue['level'] == 'MAJOR']
                minor_issues = [issue for issue in review_result['issues'] if issue['level'] == 'MINOR']
                
                if critical_issues:
                    f.write("**CRITICAL（需回退）：**\n")
                    for issue in critical_issues:
                        f.write(f"- {issue['description']}\n")
                    f.write("\n")
                
                if major_issues:
                    f.write("**MAJOR（必须修复）：**\n")
                    for issue in major_issues:
                        f.write(f"- {issue['description']}\n")
                    f.write("\n")
                
                if minor_issues:
                    f.write("**MINOR（建议改进）：**\n")
                    for issue in minor_issues:
                        f.write(f"- {issue['description']}\n")
                    f.write("\n")
            
            if review_result['improvements']:
                f.write("**本次修改点（仅一个）：**\n")
                f.write(f"- {review_result['improvements'][0]}\n")
                f.write("\n")
            
            f.write("---\n\n")
