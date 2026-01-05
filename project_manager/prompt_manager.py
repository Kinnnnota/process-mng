"""
提示词管理器
用于统一管理分离的提示词文件，包括评审标准、生成模板、阶段配置和工作流规则
"""

import os
import json
from typing import Dict, Any, Optional
from pathlib import Path


class PromptManager:
    """提示词管理器，负责加载和管理各种提示词模板"""
    
    def __init__(self, prompts_dir: str = "prompts"):
        """
        初始化提示词管理器
        
        Args:
            prompts_dir: 提示词文件目录
        """
        self.prompts_dir = Path(prompts_dir)
        self._standards = None
        self._templates = None
        self._configs = None
        self._workflows = None
        
    def get_review_standards(self, phase: str) -> Dict[str, Any]:
        """
        获取指定阶段的评审标准
        
        Args:
            phase: 阶段名称
            
        Returns:
            评审标准字典
        """
        if self._standards is None:
            self._load_standards()
        
        return self._standards.get(phase, {})
    
    def get_generation_template(self, phase: str) -> str:
        """
        获取指定阶段的生成模板
        
        Args:
            phase: 阶段名称
            
        Returns:
            生成模板字符串
        """
        if self._templates is None:
            self._load_templates()
        
        return self._templates.get(phase, "")
    
    def get_phase_config(self, phase: str) -> Dict[str, Any]:
        """
        获取指定阶段的配置
        
        Args:
            phase: 阶段名称
            
        Returns:
            阶段配置字典
        """
        if self._configs is None:
            self._load_configs()
        
        return self._configs.get(phase, {})
    
    def get_workflow_rules(self, workflow_type: str) -> Dict[str, Any]:
        """
        获取指定工作流类型的规则
        
        Args:
            workflow_type: 工作流类型
            
        Returns:
            工作流规则字典
        """
        if self._workflows is None:
            self._load_workflows()
        
        return self._workflows.get(workflow_type, {})
    
    def _load_standards(self):
        """加载评审标准"""
        standards_file = self.prompts_dir / "standards" / "review_standards.md"
        if standards_file.exists():
            content = standards_file.read_text(encoding='utf-8')
            self._standards = self._parse_standards(content)
        else:
            self._standards = {}
    
    def _load_templates(self):
        """加载生成模板"""
        templates_file = self.prompts_dir / "templates" / "generation_templates.md"
        if templates_file.exists():
            content = templates_file.read_text(encoding='utf-8')
            self._templates = self._parse_templates(content)
        else:
            self._templates = {}
    
    def _load_configs(self):
        """加载阶段配置"""
        configs_file = self.prompts_dir / "configs" / "phase_configs.md"
        if configs_file.exists():
            content = configs_file.read_text(encoding='utf-8')
            self._configs = self._parse_configs(content)
        else:
            self._configs = {}
    
    def _load_workflows(self):
        """加载工作流规则"""
        workflows_file = self.prompts_dir / "workflows" / "workflow_rules.md"
        if workflows_file.exists():
            content = workflows_file.read_text(encoding='utf-8')
            self._workflows = self._parse_workflows(content)
        else:
            self._workflows = {}
    
    def _parse_standards(self, content: str) -> Dict[str, Any]:
        """解析评审标准内容"""
        standards = {}
        current_phase = None
        
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('### ') and '阶段评审标准' in line:
                current_phase = line.replace('### ', '').replace(' 阶段评审标准', '')
                standards[current_phase] = {}
            elif line.startswith('- **') and current_phase and '%' in line:
                # 解析权重配置，格式：- **业务完整性 (30%)**：需求覆盖是否完整
                try:
                    # 提取项目名称和权重
                    start = line.find('**') + 2
                    end = line.find('**', start)
                    if start > 1 and end > start:
                        item_part = line[start:end]
                        # 提取项目名称（去掉权重部分）
                        item = item_part.split(' (')[0]
                        # 提取权重
                        weight_part = item_part.split('(')[1].split(')')[0]
                        weight = float(weight_part.replace('%', ''))
                        standards[current_phase][item] = weight
                except (ValueError, IndexError):
                    # 如果解析失败，跳过这一行
                    continue
        
        return standards
    
    def _parse_templates(self, content: str) -> Dict[str, str]:
        """解析生成模板内容"""
        templates = {}
        current_phase = None
        current_template = []
        
        lines = content.split('\n')
        for line in lines:
            if line.startswith('## ') and '阶段生成模板' in line:
                if current_phase and current_template:
                    templates[current_phase] = '\n'.join(current_template)
                current_phase = line.replace('## ', '').replace(' 阶段生成模板', '')
                current_template = [line]
            elif current_phase:
                current_template.append(line)
        
        # 添加最后一个模板
        if current_phase and current_template:
            templates[current_phase] = '\n'.join(current_template)
        
        return templates
    
    def _parse_configs(self, content: str) -> Dict[str, Any]:
        """解析阶段配置内容"""
        configs = {}
        current_phase = None
        
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('### ') and '（' in line and '）' in line:
                current_phase = line.split('（')[0].replace('### ', '')
                configs[current_phase] = {}
            elif line.startswith('- **') and current_phase and '：' in line:
                # 解析配置项，格式：- **通过分数**：80分
                try:
                    # 提取键名
                    start = line.find('**') + 2
                    end = line.find('**', start)
                    if start > 1 and end > start:
                        key = line[start:end]
                        # 提取值
                        value = line.split('：', 1)[1]
                        configs[current_phase][key] = value
                except (ValueError, IndexError):
                    # 如果解析失败，跳过这一行
                    continue
        
        return configs
    
    def _parse_workflows(self, content: str) -> Dict[str, Any]:
        """解析工作流规则内容"""
        workflows = {}
        current_workflow = None
        current_rules = []
        
        lines = content.split('\n')
        for line in lines:
            if line.startswith('### ') and '模式' in line:
                if current_workflow and current_rules:
                    workflows[current_workflow] = '\n'.join(current_rules)
                current_workflow = line.replace('### ', '').replace('模式', '').strip()
                current_rules = [line]
            elif current_workflow:
                current_rules.append(line)
        
        # 添加最后一个工作流
        if current_workflow and current_rules:
            workflows[current_workflow] = '\n'.join(current_rules)
        
        return workflows
    
    def format_template(self, template: str, **kwargs) -> str:
        """
        格式化模板，替换占位符
        
        Args:
            template: 模板字符串
            **kwargs: 替换参数
            
        Returns:
            格式化后的模板
        """
        formatted = template
        for key, value in kwargs.items():
            placeholder = f"{{{{{key}}}}}"
            formatted = formatted.replace(placeholder, str(value))
        return formatted
    
    def get_combined_prompt(self, phase: str, mode: str, **kwargs) -> str:
        """
        获取组合后的提示词
        
        Args:
            phase: 阶段名称
            mode: 模式（developer/reviewer）
            **kwargs: 模板参数
            
        Returns:
            组合后的提示词
        """
        if mode == "developer":
            template = self.get_generation_template(phase)
            return self.format_template(template, **kwargs)
        elif mode == "reviewer":
            standards = self.get_review_standards(phase)
            config = self.get_phase_config(phase)
            
            # 构建评审提示词
            prompt = f"""# {phase} 阶段评审

## 评审标准
"""
            for item, weight in standards.items():
                prompt += f"- {item}：{weight}%\n"
            
            prompt += f"""
## 通过条件
- 总分 ≥ {config.get('通过分数', '80')}分
- 无Critical级别问题
- 迭代次数 ≤ {config.get('最大迭代', '5')}次

## 评审要求
请严格按照评审标准进行评估，并提供具体的改进建议。
"""
            return prompt
        
        return ""
    
    def reload(self):
        """重新加载所有提示词文件"""
        self._standards = None
        self._templates = None
        self._configs = None
        self._workflows = None
        
        self._load_standards()
        self._load_templates()
        self._load_configs()
        self._load_workflows()
    
    def get_all_phases(self) -> list:
        """获取所有阶段列表"""
        if self._configs is None:
            self._load_configs()
        return list(self._configs.keys())
    
    def get_all_workflows(self) -> list:
        """获取所有工作流类型列表"""
        if self._workflows is None:
            self._load_workflows()
        return list(self._workflows.keys())
    
    def validate_phase(self, phase: str) -> bool:
        """
        验证阶段是否有效
        
        Args:
            phase: 阶段名称
            
        Returns:
            是否有效
        """
        return phase in self.get_all_phases()
    
    def get_phase_info(self, phase: str) -> Dict[str, Any]:
        """
        获取阶段完整信息
        
        Args:
            phase: 阶段名称
            
        Returns:
            阶段信息字典
        """
        if not self.validate_phase(phase):
            return {}
        
        return {
            'name': phase,
            'config': self.get_phase_config(phase),
            'standards': self.get_review_standards(phase),
            'template': self.get_generation_template(phase)
        }
