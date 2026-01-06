"""
AI Provider抽象接口
定义统一的AI模型调用接口,支持多种后端
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass


@dataclass
class AIMessage:
    """AI消息数据类"""
    role: str  # "user" or "assistant"
    content: str


@dataclass
class AIResponse:
    """AI响应数据类"""
    content: str
    model: str
    usage: Dict[str, int]  # {"input_tokens": 0, "output_tokens": 0}
    finish_reason: str = "stop"

    def __str__(self):
        return self.content


class AIProvider(ABC):
    """AI Provider抽象基类"""

    def __init__(self, api_key: Optional[str] = None, **kwargs):
        """
        初始化AI Provider

        Args:
            api_key: API密钥
            **kwargs: 其他配置参数
        """
        self.api_key = api_key
        self.config = kwargs

    @abstractmethod
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 4096,
        temperature: float = 1.0,
        **kwargs
    ) -> AIResponse:
        """
        生成AI响应

        Args:
            prompt: 用户提示词
            system_prompt: 系统提示词
            max_tokens: 最大生成token数
            temperature: 温度参数(0-1)
            **kwargs: 其他模型参数

        Returns:
            AI响应对象
        """
        pass

    @abstractmethod
    def chat(
        self,
        messages: List[AIMessage],
        system_prompt: Optional[str] = None,
        max_tokens: int = 4096,
        temperature: float = 1.0,
        **kwargs
    ) -> AIResponse:
        """
        多轮对话

        Args:
            messages: 对话历史消息列表
            system_prompt: 系统提示词
            max_tokens: 最大生成token数
            temperature: 温度参数(0-1)
            **kwargs: 其他模型参数

        Returns:
            AI响应对象
        """
        pass

    def validate_config(self) -> bool:
        """
        验证配置是否有效

        Returns:
            配置是否有效
        """
        return self.api_key is not None and len(self.api_key) > 0

    def get_model_info(self) -> Dict[str, Any]:
        """
        获取模型信息

        Returns:
            模型信息字典
        """
        return {
            "provider": self.__class__.__name__,
            "api_key_configured": self.api_key is not None,
            "config": self.config
        }
