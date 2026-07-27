"""MCP Vision OpenAI 配置管理

从环境变量读取 API 配置：
- VISION_API_KEY: API 密钥（必需）
- VISION_BASE_URL: API 地址（必需，如 https://api.openai.com/v1）
- VISION_MODEL: 视觉模型名称（必需，如 gpt-4o）
"""

import os
from dataclasses import dataclass

from .exceptions import ConfigurationError


@dataclass
class VisionConfig:
    """视觉模型配置"""
    api_key: str
    base_url: str
    model: str


def load_config() -> VisionConfig:
    """从环境变量加载配置

    Returns:
        VisionConfig 配置对象

    Raises:
        ConfigurationError: 缺少必需的配置项
    """
    api_key = os.environ.get("VISION_API_KEY")
    if not api_key:
        raise ConfigurationError(
            "未设置 VISION_API_KEY 环境变量。"
            "请在 MCP 配置的 env 中设置您的 API 密钥。"
        )

    base_url = os.environ.get("VISION_BASE_URL")
    if not base_url:
        raise ConfigurationError(
            "未设置 VISION_BASE_URL 环境变量。"
            "请在 MCP 配置的 env 中设置 API 地址，如 https://api.openai.com/v1"
        )

    model = os.environ.get("VISION_MODEL")
    if not model:
        raise ConfigurationError(
            "未设置 VISION_MODEL 环境变量。"
            "请在 MCP 配置的 env 中设置视觉模型名称，如 gpt-4o"
        )

    return VisionConfig(
        api_key=api_key,
        base_url=base_url.rstrip("/"),
        model=model,
    )
