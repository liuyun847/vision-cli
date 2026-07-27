# MCP Vision OpenAI

为纯文本模型提供图片理解能力，通过 MCP 协议调用 OpenAI 兼容的视觉模型 API，让不支持多模态的 AI 助手也能"看懂"图片。

## 功能

- 支持本地文件路径、URL、base64 编码的图片输入
- 兼容所有 OpenAI 格式的视觉模型 API
- 通过 MCP 协议集成到 Trae IDE 等工具

## 安装

```bash
uv pip install .
```

## 配置

在 MCP 配置文件中添加：

```json
{
  "mcpServers": {
    "vision": {
      "command": "python",
      "args": ["-m", "mcp_vision_openai.server"],
      "env": {
        "VISION_API_KEY": "your-api-key",
        "VISION_BASE_URL": "your-base-url",
        "VISION_MODEL": "your-model-name"
      }
    }
  }
}
```

### 环境变量

| 变量 | 必需 | 说明 |
|------|------|------|
| `VISION_API_KEY` | 是 | API 密钥 |
| `VISION_BASE_URL` | 是 | API 地址，如 `https://api.openai.com/v1` |
| `VISION_MODEL` | 是 | 视觉模型名称，如 `gpt-4o` |

## 使用

AI 助手调用 `image_analysis` 工具：

```
image_analysis(image="/path/to/image.jpg", prompt="描述这张图片的内容")
```

## 许可证

MIT
