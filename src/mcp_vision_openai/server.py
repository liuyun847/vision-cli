"""MCP Vision OpenAI 服务器

支持 OpenAI 兼容格式的视觉模型 API，用于图片分析。
"""

import base64
import mimetypes
import re
from pathlib import Path
from typing import Annotated, Optional
from urllib.parse import urlparse

import requests
from mcp.server.fastmcp import FastMCP
from pydantic import Field

from .config import load_config
from .exceptions import APIError, ConfigurationError, ImageError

# 初始化 MCP 服务器
mcp = FastMCP("Vision")

# 初始化 mimetypes
mimetypes.init()


def encode_image_to_base64(image_data: bytes) -> str:
    """将图片数据编码为 base64"""
    return base64.b64encode(image_data).decode("utf-8")


def get_mime_type(file_path: str, image_data: Optional[bytes] = None) -> str:
    """获取图片的 MIME 类型

    Args:
        file_path: 文件路径或 URL
        image_data: 可选的图片数据，用于文件头检测

    Returns:
        MIME 类型字符串，默认 image/jpeg
    """
    # 先尝试从文件扩展名获取
    mime_type, _ = mimetypes.guess_type(file_path)
    if mime_type and mime_type.startswith("image/"):
        return mime_type

    # 从文件头检测
    if image_data:
        if image_data.startswith(b"\x89PNG\r\n\x1a\n"):
            return "image/png"
        elif image_data.startswith(b"\xff\xd8\xff"):
            return "image/jpeg"
        elif image_data.startswith(b"RIFF") and b"WEBP" in image_data[0:12]:
            return "image/webp"
        elif image_data.startswith(b"GIF8"):
            return "image/gif"

    return "image/jpeg"


def is_url(string: str) -> bool:
    """检查字符串是否为 URL"""
    try:
        result = urlparse(string)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False


def is_base64(string: str) -> bool:
    """检查字符串是否为 base64 编码"""
    # 处理 data URL
    if string.startswith("data:image"):
        pattern = r"base64,(.*)"
        match = re.search(pattern, string)
        if match:
            string = match.group(1)

    try:
        if not isinstance(string, str):
            return False
        if not re.match(r"^[A-Za-z0-9+/]*={0,2}$", string):
            return False
        if len(string) < 4:
            return False
        base64.b64decode(string)
        return True
    except Exception:
        return False


def extract_mime_from_data_url(data_url: str) -> str:
    """从 data URL 提取 MIME 类型"""
    pattern = r"data:(image/[^;]+)"
    match = re.search(pattern, data_url)
    if match:
        return match.group(1)
    return "image/jpeg"


def load_image_from_url(url: str) -> tuple[str, str]:
    """从 URL 下载图片并转为 base64

    Args:
        url: 图片 URL

    Returns:
        (base64 编码, MIME 类型) 元组

    Raises:
        ImageError: 下载失败
    """
    try:
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()

        content_type = response.headers.get("Content-Type")
        if not content_type or not content_type.startswith("image/"):
            content_type = get_mime_type(url, response.content)

        return encode_image_to_base64(response.content), content_type
    except requests.RequestException as e:
        raise ImageError(f"从 URL 下载图片失败: {url}, 错误: {e}")


def load_image_from_path(path: str) -> tuple[str, str]:
    """从本地路径加载图片并转为 base64

    Args:
        path: 图片文件路径

    Returns:
        (base64 编码, MIME 类型) 元组

    Raises:
        FileNotFoundError: 文件不存在
        PermissionError: 无读取权限
    """
    file_path = Path(path)

    if not file_path.exists():
        raise FileNotFoundError(f"图片文件不存在: {path}")

    if not file_path.is_file():
        raise ImageError(f"路径不是文件: {path}")

    try:
        with open(file_path, "rb") as f:
            image_data = f.read()
            mime_type = get_mime_type(str(file_path), image_data)
            return encode_image_to_base64(image_data), mime_type
    except PermissionError:
        raise PermissionError(f"无权限读取图片文件: {path}")


def process_image(image: str) -> tuple[str, str]:
    """处理图片输入，支持 URL、文件路径、base64

    Args:
        image: 图片输入

    Returns:
        (base64 编码, MIME 类型) 元组

    Raises:
        ImageError: 图片处理失败
    """
    # 处理 data URL
    if image.startswith("data:image"):
        mime_type = extract_mime_from_data_url(image)
        pattern = r"base64,(.*)"
        match = re.search(pattern, image)
        if match:
            return match.group(1), mime_type
        raise ImageError("无效的 data URL 格式")

    # 处理纯 base64
    if is_base64(image):
        return image, "image/jpeg"

    # 处理 URL
    if is_url(image):
        return load_image_from_url(image)

    # 处理文件路径
    try:
        return load_image_from_path(image)
    except (FileNotFoundError, PermissionError) as e:
        raise ImageError(f"图片处理失败: {e}")


def call_vision_api(
    base64_image: str,
    mime_type: str,
    prompt: str,
) -> str:
    """调用 OpenAI 兼容的视觉模型 API

    Args:
        base64_image: base64 编码的图片
        mime_type: 图片 MIME 类型
        prompt: 分析提示词

    Returns:
        模型返回的描述文本

    Raises:
        APIError: API 调用失败
        ConfigurationError: 配置错误
    """
    config = load_config()

    # 构建请求 URL
    if config.base_url.endswith("/chat/completions"):
        url = config.base_url
    else:
        url = f"{config.base_url}/chat/completions"

    # 构建请求头
    headers = {
        "Authorization": f"Bearer {config.api_key}",
        "Content-Type": "application/json",
    }

    # 构建请求体
    payload = {
        "model": config.model,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{mime_type};base64,{base64_image}"
                        },
                    },
                ],
            }
        ],
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=120)
        response.raise_for_status()
        data = response.json()

        # 提取回复内容
        if "choices" in data and len(data["choices"]) > 0:
            return data["choices"][0]["message"]["content"]
        elif "error" in data:
            error = data["error"]
            raise APIError(
                status_code=response.status_code,
                message=error.get("message", "未知错误"),
            )
        else:
            raise APIError(
                status_code=response.status_code,
                message=f"意外的响应格式: {data}",
            )
    except requests.exceptions.Timeout:
        raise APIError(status_code=408, message="API 请求超时")
    except requests.exceptions.RequestException as e:
        raise APIError(status_code=500, message=f"API 请求失败: {e}")


@mcp.tool()
def image_analysis(
    image: Annotated[
        str,
        Field(
            description=(
                "要分析的图片，支持以下四种格式之一："
                "1) 本地文件路径（绝对路径或相对路径）；"
                "2) 图片 URL（以 http:// 或 https:// 开头）；"
                "3) base64 编码字符串（不带 data: 前缀）；"
                "4) data URL，形如 data:image/<mime>;base64,<data>。"
            ),
        ),
    ],
    prompt: Annotated[
        str,
        Field(
            description="分析提示词，描述你希望从图片中获取的信息或执行的任务。",
        ),
    ],
) -> str:
    """分析图片并返回描述

    Returns:
        图片的描述文本

    Examples:
        image_analysis(image="/path/to/image.jpg", prompt="描述这张图片的内容")
        image_analysis(image="https://example.com/image.jpg", prompt="图片中有什么文字？")
        image_analysis(image="base64_encoded_data", prompt="提取图片中的表格数据")
    """
    try:
        # 处理图片
        base64_image, mime_type = process_image(image)

        # 调用 API
        result = call_vision_api(base64_image, mime_type, prompt)

        return result

    except ImageError as e:
        return f"图片处理错误: {e}"
    except APIError as e:
        return f"API 调用错误: {e}"
    except ConfigurationError as e:
        return f"配置错误: {e}"
    except Exception as e:
        return f"未知错误: {e}"


def main() -> None:
    """启动 MCP 服务器"""
    mcp.run()


if __name__ == "__main__":
    main()
