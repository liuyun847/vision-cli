"""MCP Vision OpenAI 异常定义"""


class VisionError(Exception):
    """MCP Vision 基础异常"""
    pass


class ConfigurationError(VisionError):
    """配置错误"""
    pass


class APIError(VisionError):
    """API 调用错误

    Args:
        status_code: HTTP 状态码
        message: 错误信息
    """

    def __init__(self, status_code: int, message: str) -> None:
        self.status_code = status_code
        self.message = message
        super().__init__(f"API 错误 ({status_code}): {message}")


class ImageError(VisionError):
    """图片处理错误"""
    pass
