"""
配置加载器
从环境变量和配置文件加载AI Provider配置
"""
import os
from pathlib import Path
from typing import Dict, Any, Optional


class ConfigLoader:
    """配置加载器类"""

    def __init__(self, env_file: Optional[str] = None):
        """
        初始化配置加载器

        Args:
            env_file: .env文件路径,默认为项目根目录的.env
        """
        self.env_file = env_file or self._find_env_file()
        self._load_env_file()

    def _find_env_file(self) -> Optional[Path]:
        """
        查找.env文件

        Returns:
            .env文件路径,如果找不到返回None
        """
        # 从当前目录开始向上查找
        current = Path.cwd()
        while current != current.parent:
            env_path = current / ".env"
            if env_path.exists():
                return env_path
            current = current.parent

        # 尝试项目根目录
        project_root = Path(__file__).parent.parent
        env_path = project_root / ".env"
        if env_path.exists():
            return env_path

        return None

    def _load_env_file(self):
        """从.env文件加载环境变量"""
        if not self.env_file or not Path(self.env_file).exists():
            return

        try:
            with open(self.env_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    # 跳过空行和注释
                    if not line or line.startswith('#'):
                        continue

                    # 解析键值对
                    if '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()
                        # 去除引号
                        if value.startswith('"') and value.endswith('"'):
                            value = value[1:-1]
                        elif value.startswith("'") and value.endswith("'"):
                            value = value[1:-1]

                        # 只在环境变量未设置时才设置
                        if key not in os.environ:
                            os.environ[key] = value
        except Exception as e:
            print(f"⚠️  加载.env文件失败: {e}")

    def get_claude_config(self) -> Dict[str, Any]:
        """
        获取Claude API配置

        Returns:
            配置字典
        """
        return {
            "api_key": os.getenv("ANTHROPIC_API_KEY"),
            "model": os.getenv("CLAUDE_MODEL", "claude-3-5-sonnet-20241022"),
            "api_base": os.getenv("ANTHROPIC_API_BASE"),
            "max_tokens": int(os.getenv("MAX_TOKENS", "4096")),
            "temperature": float(os.getenv("TEMPERATURE", "1.0"))
        }

    def get_config(self, provider: str = "claude") -> Dict[str, Any]:
        """
        获取指定provider的配置

        Args:
            provider: provider名称(claude/openai/etc)

        Returns:
            配置字典
        """
        if provider.lower() == "claude":
            return self.get_claude_config()
        else:
            raise ValueError(f"不支持的provider: {provider}")

    def validate_config(self, provider: str = "claude") -> bool:
        """
        验证配置是否完整

        Args:
            provider: provider名称

        Returns:
            配置是否有效
        """
        config = self.get_config(provider)
        if provider.lower() == "claude":
            return config.get("api_key") is not None and len(config["api_key"]) > 0
        return False

    def get_config_status(self) -> Dict[str, Any]:
        """
        获取配置状态

        Returns:
            配置状态字典
        """
        return {
            "env_file": str(self.env_file) if self.env_file else "未找到",
            "env_file_exists": self.env_file and Path(self.env_file).exists(),
            "claude_api_key_configured": bool(os.getenv("ANTHROPIC_API_KEY")),
            "claude_model": os.getenv("CLAUDE_MODEL", "claude-3-5-sonnet-20241022")
        }


# 全局配置加载器实例
_config_loader = None


def get_config_loader() -> ConfigLoader:
    """
    获取全局配置加载器实例(单例模式)

    Returns:
        配置加载器实例
    """
    global _config_loader
    if _config_loader is None:
        _config_loader = ConfigLoader()
    return _config_loader
