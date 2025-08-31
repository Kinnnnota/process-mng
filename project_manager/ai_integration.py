"""
AI集成模块
负责将Cursor AI与项目管理模板集成
"""
import json
import os
from typing import Dict, List, Optional, Any
from pathlib import Path
from datetime import datetime

from .models import Phase, Mode, ProjectState
from .project_manager import ProjectManager


class AIIntegration:
    """AI集成器类"""
    
    def __init__(self, project_name: str):
        """
        初始化AI集成器
        
        Args:
            project_name: 项目名称
        """
        self.project_name = project_name
        self.project_manager = ProjectManager(project_name)
        self.prompts_dir = Path("project_manager/prompts")
        self.config_file = Path("config.yaml")
        
    def get_current_context(self) -> Dict[str, Any]:
        """
        获取当前项目上下文信息
        
        Returns:
            项目上下文字典
        """
        status = self.project_manager.get_current_status()
        
        return {
            "project_name": status['project_name'],
            "current_phase": status['current_phase'],
            "phase_iteration": status['phase_iteration'],
            "current_mode": status['current_mode'],
            "status": status['status'],
            "latest_score": status['latest_score'],
            "blocked_issues_count": status['blocked_issues_count'],
            "improvements_count": status['improvements_count'],
            "review_count": status['review_count'],
            "from_rollback": status['from_rollback'],
            "rollback_reason": status['rollback_reason'],
            "rollback_count": status['rollback_count'],
            "quality_gates": status['quality_gates']
        }
    
    def get_phase_requirements(self, phase: Phase) -> Dict[str, Any]:
        """
        获取指定阶段的要求
        
        Args:
            phase: 项目阶段
            
        Returns:
            阶段要求字典
        """
        # 读取配置文件
        if self.config_file.exists():
            import yaml
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                
            phase_config = config.get('phases', {}).get(phase.value, {})
            
            return {
                "focus_goals": phase_config.get('focus_goals', []),
                "required_outputs": phase_config.get('required_outputs', []),
                "review_weights": phase_config.get('review_weights', {}),
                "pass_score": phase_config.get('pass_score', 80),
                "max_iterations": phase_config.get('max_iterations', 5)
            }
        
        return {}
    
    def get_development_prompt(self, phase: Phase) -> str:
        """
        获取开发模式提示词
        
        Args:
            phase: 项目阶段
            
        Returns:
            提示词内容
        """
        prompt_file = self.prompts_dir / "developer_mode.md"
        
        if prompt_file.exists():
            with open(prompt_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 根据阶段提取对应的提示词部分
            if phase == Phase.BASIC_DESIGN:
                return self._extract_section(content, "设计阶段提示词")
            elif phase == Phase.DETAIL_DESIGN:
                return self._extract_section(content, "设计阶段提示词")
            elif phase == Phase.DEVELOPMENT:
                return self._extract_section(content, "开发阶段提示词")
            elif phase == Phase.UNIT_TEST:
                return self._extract_section(content, "测试阶段提示词")
            elif phase == Phase.INTEGRATION_TEST:
                return self._extract_section(content, "测试阶段提示词")
        
        return ""
    
    def get_review_prompt(self, phase: Phase) -> str:
        """
        获取评审模式提示词
        
        Args:
            phase: 项目阶段
            
        Returns:
            提示词内容
        """
        prompt_file = self.prompts_dir / "reviewer_mode.md"
        
        if prompt_file.exists():
            with open(prompt_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 根据阶段提取对应的提示词部分
            if phase == Phase.BASIC_DESIGN:
                return self._extract_section(content, "设计阶段评审提示词")
            elif phase == Phase.DETAIL_DESIGN:
                return self._extract_section(content, "设计阶段评审提示词")
            elif phase == Phase.DEVELOPMENT:
                return self._extract_section(content, "开发阶段评审提示词")
            elif phase == Phase.UNIT_TEST:
                return self._extract_section(content, "测试阶段评审提示词")
            elif phase == Phase.INTEGRATION_TEST:
                return self._extract_section(content, "测试阶段评审提示词")
        
        return ""
    
    def _extract_section(self, content: str, section_name: str) -> str:
        """
        从内容中提取指定部分
        
        Args:
            content: 完整内容
            section_name: 部分名称
            
        Returns:
            提取的内容
        """
        lines = content.split('\n')
        start_index = -1
        end_index = -1
        
        for i, line in enumerate(lines):
            if section_name in line:
                start_index = i
                break
        
        if start_index == -1:
            return ""
        
        # 查找下一个部分开始
        for i in range(start_index + 1, len(lines)):
            if lines[i].startswith('## ') and '阶段' in lines[i]:
                end_index = i
                break
        
        if end_index == -1:
            end_index = len(lines)
        
        return '\n'.join(lines[start_index:end_index])
    
    def generate_ai_instruction(self, task: str) -> str:
        """
        生成AI指令
        
        Args:
            task: 任务描述
            
        Returns:
            AI指令
        """
        context = self.get_current_context()
        phase = Phase(context['current_phase'])
        
        instruction = f"""
# AI开发指令

## 项目上下文
- 项目名称：{context['project_name']}
- 当前阶段：{context['current_phase']}
- 阶段迭代：{context['phase_iteration']}
- 当前模式：{context['current_mode']}
- 项目状态：{context['status']}
- 最新评分：{context['latest_score']}分
- 阻塞问题：{context['blocked_issues_count']}个
- 改进建议：{context['improvements_count']}个
- 评审次数：{context['review_count']}次

## 任务要求
{task}

## 开发要求
请严格按照以下要求进行开发：

### 1. 阶段要求
"""
        
        # 添加阶段特定要求
        phase_requirements = self.get_phase_requirements(phase)
        if phase_requirements:
            instruction += f"""
- 关注目标：{', '.join(phase_requirements.get('focus_goals', []))}
- 必需输出：{', '.join(phase_requirements.get('required_outputs', []))}
- 评审权重：{phase_requirements.get('review_weights', {})}
- 通过分数：{phase_requirements.get('pass_score', 80)}分
- 最大迭代：{phase_requirements.get('max_iterations', 5)}次
"""
        
        # 添加开发模式提示词
        if context['current_mode'] == 'developer':
            dev_prompt = self.get_development_prompt(phase)
            if dev_prompt:
                instruction += f"""
### 2. 开发模式提示词
{dev_prompt}
"""
        else:
            review_prompt = self.get_review_prompt(phase)
            if review_prompt:
                instruction += f"""
### 2. 评审模式提示词
{review_prompt}
"""
        
        instruction += """
### 3. 代码质量要求
- 遵循PEP 8编码规范
- 包含完整的类型注解
- 添加详细的docstring
- 实现完整的错误处理
- 考虑性能优化
- 确保测试覆盖率80%以上

### 4. 文件组织要求
严格按照项目目录结构组织文件：
```
project_manager/{project_name}/phase_outputs/{phase}/output_v{iteration}.md
```

### 5. 状态更新要求
完成开发后必须：
1. 更新项目状态文件
2. 记录开发日志
3. 更新阶段迭代次数
4. 设置状态为READY_FOR_REVIEW

请按照以上要求完成开发任务。
"""
        
        return instruction
    
    def validate_ai_output(self, output: str, phase: Phase) -> Dict[str, Any]:
        """
        验证AI输出是否符合要求
        
        Args:
            output: AI输出内容
            phase: 项目阶段
            
        Returns:
            验证结果
        """
        phase_requirements = self.get_phase_requirements(phase)
        required_outputs = phase_requirements.get('required_outputs', [])
        
        validation_result = {
            "valid": True,
            "missing_items": [],
            "quality_score": 0,
            "suggestions": []
        }
        
        # 检查必需输出项
        for required_output in required_outputs:
            if required_output.lower() not in output.lower():
                validation_result["missing_items"].append(required_output)
                validation_result["valid"] = False
        
        # 检查代码质量
        quality_score = 0
        
        # 检查是否包含类型注解
        if "def " in output and ":" in output:
            quality_score += 20
        
        # 检查是否包含docstring
        if '"""' in output or "'''" in output:
            quality_score += 20
        
        # 检查是否包含错误处理
        if "try:" in output or "except" in output:
            quality_score += 20
        
        # 检查是否包含测试
        if "test" in output.lower() or "assert" in output:
            quality_score += 20
        
        # 检查代码规范
        if "import" in output and "from" in output:
            quality_score += 20
        
        validation_result["quality_score"] = quality_score
        
        # 生成改进建议
        if quality_score < 80:
            validation_result["suggestions"].append("建议提高代码质量，确保包含完整的类型注解、docstring、错误处理和测试")
        
        if validation_result["missing_items"]:
            validation_result["suggestions"].append(f"缺少必需输出项：{', '.join(validation_result['missing_items'])}")
        
        return validation_result
    
    def update_project_state(self, output: str, phase: Phase) -> None:
        """
        更新项目状态
        
        Args:
            output: AI输出内容
            phase: 项目阶段
        """
        # 保存输出文件
        output_dir = self.project_manager.phase_outputs_dir / phase.value.lower()
        output_dir.mkdir(parents=True, exist_ok=True)
        
        iteration = self.project_manager.state.phase_iteration
        if phase == Phase.BASIC_DESIGN:
            output_file = output_dir / f"basic_design_v{iteration + 1}.md"
        elif phase == Phase.DETAIL_DESIGN:
            output_file = output_dir / f"detail_design_v{iteration + 1}.md"
        elif phase == Phase.DEVELOPMENT:
            output_file = output_dir / f"implementation_v{iteration + 1}.py"
        elif phase == Phase.UNIT_TEST:
            output_file = output_dir / f"unit_test_v{iteration + 1}.py"
        elif phase == Phase.INTEGRATION_TEST:
            output_file = output_dir / f"integration_test_v{iteration + 1}.py"
        else:
            output_file = output_dir / f"output_v{iteration + 1}.md"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(output)
        
        # 更新项目状态
        self.project_manager.state.status = "READY_FOR_REVIEW"
        self.project_manager.state.updated_at = datetime.now().isoformat()
        self.project_manager._save_state()
        
        print(f"✅ 输出已保存到：{output_file}")
        print(f"✅ 项目状态已更新为：READY_FOR_REVIEW")


def create_ai_instruction(project_name: str, task: str) -> str:
    """
    创建AI指令的便捷函数
    
    Args:
        project_name: 项目名称
        task: 任务描述
        
    Returns:
        AI指令
    """
    ai_integration = AIIntegration(project_name)
    return ai_integration.generate_ai_instruction(task)


def validate_and_update(project_name: str, output: str) -> Dict[str, Any]:
    """
    验证AI输出并更新项目状态的便捷函数
    
    Args:
        project_name: 项目名称
        output: AI输出内容
        
    Returns:
        验证结果
    """
    ai_integration = AIIntegration(project_name)
    context = ai_integration.get_current_context()
    phase = Phase(context['current_phase'])
    
    # 验证输出
    validation_result = ai_integration.validate_ai_output(output, phase)
    
    # 如果验证通过，更新项目状态
    if validation_result["valid"]:
        ai_integration.update_project_state(output, phase)
    
    return validation_result
