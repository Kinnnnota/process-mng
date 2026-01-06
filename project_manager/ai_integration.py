"""
AI集成模块
负责将Claude AI与项目管理模板集成,提供自动化的AI生成和评审功能
"""
import json
import os
from typing import Dict, List, Optional, Any
from pathlib import Path
from datetime import datetime

from .models import Phase, Mode, ProjectState
from .claude_provider import ClaudeProvider
from .config_loader import get_config_loader
from .prompt_manager import PromptManager
from .issue_storage import IssueStorage


class AIIntegration:
    """AI集成器类"""

    def __init__(self, project_name: str = None, ai_provider: Optional[ClaudeProvider] = None):
        """
        初始化AI集成器

        Args:
            project_name: 项目名称(可选,用于与ProjectManager集成)
            ai_provider: AI Provider实例(可选,默认创建Claude Provider)
        """
        self.project_name = project_name
        self.prompt_manager = PromptManager("project_manager/prompts")
        self.config_file = Path("config.yaml")

        # 初始化AI Provider
        if ai_provider:
            self.ai_provider = ai_provider
        else:
            config_loader = get_config_loader()
            claude_config = config_loader.get_claude_config()
            self.ai_provider = ClaudeProvider(**claude_config)
        
    def generate_content(
        self,
        phase: Phase,
        context: Optional[Dict[str, Any]] = None,
        max_tokens: int = 4096,
        temperature: float = 1.0
    ) -> str:
        """
        使用AI生成指定阶段的内容

        Args:
            phase: 项目阶段
            context: 项目上下文信息
            max_tokens: 最大生成token数
            temperature: 温度参数

        Returns:
            生成的内容
        """
        # 获取生成模板
        generation_template = self.prompt_manager.get_generation_template(phase.value)

        # 构建系统提示词
        system_prompt = f"""你是一个专业的软件开发专家,正在为项目的{phase.value}阶段生成高质量的内容。
请严格按照提供的模板和要求生成内容,确保内容完整、专业、符合规范。"""

        # 构建用户提示词
        user_prompt = generation_template

        # 如果有上下文信息,添加到提示词中
        if context:
            context_str = json.dumps(context, ensure_ascii=False, indent=2)
            user_prompt = f"""# 项目上下文
{context_str}

# 生成任务
{generation_template}"""

        # 调用AI生成
        try:
            response = self.ai_provider.generate(
                prompt=user_prompt,
                system_prompt=system_prompt,
                max_tokens=max_tokens,
                temperature=temperature
            )
            return response.content
        except Exception as e:
            raise RuntimeError(f"AI生成失败: {str(e)}")

    def review_content(
        self,
        phase: Phase,
        content: str,
        max_tokens: int = 4096,
        temperature: float = 0.3
    ) -> Dict[str, Any]:
        """
        使用AI评审指定阶段的内容

        Args:
            phase: 项目阶段
            content: 待评审的内容
            max_tokens: 最大生成token数
            temperature: 温度参数(评审使用较低温度以保证稳定性)

        Returns:
            评审结果字典,包含score, issues, improvements等
        """
        # 获取评审提示词
        review_prompt = self.prompt_manager.get_combined_prompt(phase.value, "reviewer")

        # 构建系统提示词
        system_prompt = f"""你是一个严格的代码评审专家,正在对项目的{phase.value}阶段进行专业评审。
请按照评审标准仔细检查内容,给出客观公正的评分和详细的问题报告。

评审结果必须严格按照以下JSON格式返回:
{{
    "score": 85,
    "issues": [
        {{
            "level": "CRITICAL",
            "category": "功能完整性",
            "description": "问题描述",
            "location": "具体位置",
            "suggestion": "改进建议"
        }}
    ],
    "improvements": [
        "改进建议1",
        "改进建议2"
    ],
    "summary": "总体评价"
}}"""

        # 构建用户提示词
        user_prompt = f"""# 评审标准
{review_prompt}

# 待评审内容
```
{content}
```

请严格按照评审标准进行评审,并以JSON格式返回评审结果。"""

        # 调用AI评审
        try:
            response = self.ai_provider.generate(
                prompt=user_prompt,
                system_prompt=system_prompt,
                max_tokens=max_tokens,
                temperature=temperature
            )

            # 解析评审结果
            review_result = self._parse_review_result(response.content)
            return review_result
        except Exception as e:
            raise RuntimeError(f"AI评审失败: {str(e)}")

    def _parse_review_result(self, response_content: str) -> Dict[str, Any]:
        """
        解析AI返回的评审结果

        Args:
            response_content: AI返回的原始内容

        Returns:
            解析后的评审结果字典
        """
        try:
            # 尝试提取JSON内容
            content = response_content.strip()

            # 如果包含markdown代码块,提取其中的JSON
            if "```json" in content:
                start = content.find("```json") + 7
                end = content.find("```", start)
                content = content[start:end].strip()
            elif "```" in content:
                start = content.find("```") + 3
                end = content.find("```", start)
                content = content[start:end].strip()

            # 解析JSON
            result = json.loads(content)

            # 验证必需字段
            if "score" not in result:
                result["score"] = 0
            if "issues" not in result:
                result["issues"] = []
            if "improvements" not in result:
                result["improvements"] = []
            if "summary" not in result:
                result["summary"] = "无评价"

            return result
        except json.JSONDecodeError as e:
            # 如果JSON解析失败,返回一个基本的结果
            return {
                "score": 0,
                "issues": [{
                    "level": "CRITICAL",
                    "category": "评审格式错误",
                    "description": f"AI返回的评审结果格式不正确: {str(e)}",
                    "location": "整体",
                    "suggestion": "请重新生成评审结果"
                }],
                "improvements": ["确保返回正确的JSON格式"],
                "summary": f"评审结果解析失败: {response_content[:200]}"
            }

    def get_current_context(self) -> Dict[str, Any]:
        """
        获取当前项目上下文信息

        Returns:
            项目上下文字典
        """
        if not self.project_name:
            return {}

        # 这里需要导入ProjectManager,为了避免循环导入,延迟导入
        from .project_manager import ProjectManager
        project_manager = ProjectManager(self.project_name)
        status = project_manager.get_current_status()

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
        return self.prompt_manager.get_generation_template(phase.value)
    
    def get_review_prompt(self, phase: Phase) -> str:
        """
        获取评审模式提示词
        
        Args:
            phase: 项目阶段
            
        Returns:
            提示词内容
        """
        return self.prompt_manager.get_combined_prompt(phase.value, "reviewer")
    

    
    def get_provider_info(self) -> Dict[str, Any]:
        """
        获取AI Provider信息

        Returns:
            Provider信息字典
        """
        return self.ai_provider.get_model_info()

    def validate_config(self) -> bool:
        """
        验证AI配置是否有效

        Returns:
            配置是否有效
        """
        return self.ai_provider.validate_config()


# 便捷函数
def create_ai_integration(project_name: Optional[str] = None) -> AIIntegration:
    """
    创建AI集成实例的便捷函数

    Args:
        project_name: 项目名称

    Returns:
        AI集成实例
    """
    return AIIntegration(project_name=project_name)
