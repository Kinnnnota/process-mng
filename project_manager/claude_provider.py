"""
Claude API Provider实现
使用Anthropic Claude API进行AI生成
"""
import json
import os
from typing import Dict, Any, Optional, List
import urllib.request
import urllib.error

from .ai_provider import AIProvider, AIMessage, AIResponse


class ClaudeProvider(AIProvider):
    """Claude API Provider"""

    # 默认模型配置
    DEFAULT_MODEL = "claude-3-5-sonnet-20241022"
    API_BASE_URL = "https://api.anthropic.com/v1"
    API_VERSION = "2023-06-01"

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        api_base: Optional[str] = None,
        **kwargs
    ):
        """
        初始化Claude Provider

        Args:
            api_key: Anthropic API密钥
            model: 使用的模型名称
            api_base: API基础URL(用于自定义端点)
            **kwargs: 其他配置参数
        """
        super().__init__(api_key, **kwargs)
        self.model = model or self.DEFAULT_MODEL
        self.api_base = api_base or self.API_BASE_URL

        # 如果没有传入api_key,尝试从环境变量读取
        if not self.api_key:
            self.api_key = os.getenv("ANTHROPIC_API_KEY")

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
        messages = [AIMessage(role="user", content=prompt)]
        return self.chat(
            messages=messages,
            system_prompt=system_prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            **kwargs
        )

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

        Raises:
            ValueError: API配置无效
            RuntimeError: API调用失败
        """
        if not self.validate_config():
            raise ValueError("Claude API密钥未配置。请设置ANTHROPIC_API_KEY环境变量或传入api_key参数")

        # 构建请求体
        payload = {
            "model": self.model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": [
                {"role": msg.role, "content": msg.content}
                for msg in messages
            ]
        }

        # 添加系统提示词
        if system_prompt:
            payload["system"] = system_prompt

        # 添加其他参数
        if "top_p" in kwargs:
            payload["top_p"] = kwargs["top_p"]
        if "top_k" in kwargs:
            payload["top_k"] = kwargs["top_k"]
        if "stop_sequences" in kwargs:
            payload["stop_sequences"] = kwargs["stop_sequences"]

        # 发送请求
        try:
            response_data = self._make_request("/messages", payload)
            return self._parse_response(response_data)
        except Exception as e:
            raise RuntimeError(f"Claude API调用失败: {str(e)}")

    def _make_request(self, endpoint: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        发送HTTP请求到Claude API

        Args:
            endpoint: API端点
            payload: 请求数据

        Returns:
            响应数据

        Raises:
            urllib.error.HTTPError: HTTP请求失败
        """
        url = f"{self.api_base}{endpoint}"
        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key,
            "anthropic-version": self.API_VERSION
        }

        # 构建请求
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(url, data=data, headers=headers, method='POST')

        try:
            with urllib.request.urlopen(req, timeout=120) as response:
                response_data = json.loads(response.read().decode('utf-8'))
                return response_data
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8')
            try:
                error_data = json.loads(error_body)
                error_msg = error_data.get('error', {}).get('message', error_body)
            except:
                error_msg = error_body
            raise RuntimeError(f"HTTP {e.code}: {error_msg}")
        except urllib.error.URLError as e:
            raise RuntimeError(f"网络错误: {str(e.reason)}")
        except Exception as e:
            raise RuntimeError(f"请求失败: {str(e)}")

    def _parse_response(self, response_data: Dict[str, Any]) -> AIResponse:
        """
        解析API响应

        Args:
            response_data: API返回的原始数据

        Returns:
            AI响应对象
        """
        # 提取内容
        content = ""
        if "content" in response_data and len(response_data["content"]) > 0:
            # Claude返回的content是一个列表
            for content_block in response_data["content"]:
                if content_block.get("type") == "text":
                    content += content_block.get("text", "")

        # 提取使用量信息
        usage = response_data.get("usage", {})
        usage_dict = {
            "input_tokens": usage.get("input_tokens", 0),
            "output_tokens": usage.get("output_tokens", 0)
        }

        # 构建响应对象
        return AIResponse(
            content=content,
            model=response_data.get("model", self.model),
            usage=usage_dict,
            finish_reason=response_data.get("stop_reason", "stop")
        )

    def get_model_info(self) -> Dict[str, Any]:
        """
        获取模型信息

        Returns:
            模型信息字典
        """
        info = super().get_model_info()
        info.update({
            "model": self.model,
            "api_base": self.api_base,
            "api_version": self.API_VERSION
        })
        return info

    def validate_config(self) -> bool:
        """
        验证配置是否有效

        Returns:
            配置是否有效
        """
        return super().validate_config() and self.model is not None
