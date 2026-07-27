# Vision Analysis CLI

图片分析命令行工具，使用 OpenAI 兼容的视觉模型 API 分析图片内容。

## 功能

- 支持本地文件路径、URL、base64 编码的图片输入
- 调用 OpenAI 兼容的视觉模型 API
- 支持图片内容分析、文字提取、场景描述等

## 安装

1. 克隆仓库：
```bash
git clone https://github.com/liuyun847/mcp-vision-openai.git
cd mcp-vision-openai
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 配置：
编辑 `config.json` 文件，填入您的 API 配置：
```json
{
  "api_key": "your-api-key",
  "base_url": "https://api.openai.com/v1",
  "model": "gpt-4o"
}
```

## 使用

```bash
# 分析本地图片
python vision-cli.py --image "图片路径" --prompt "分析提示词"

# 分析 URL 图片
python vision-cli.py --image "图片URL" --prompt "分析提示词"

# 使用自定义配置文件
python vision-cli.py --config "其他配置文件路径" --image "图片" --prompt "提示词"
```

## 示例

```bash
# 描述图片内容
python vision-cli.py --image "photo.jpg" --prompt "详细描述这张图片的内容"

# 提取文字
python vision-cli.py --image "document.png" --prompt "提取图片中的所有文字"

# 分析图表
python vision-cli.py --image "chart.png" --prompt "解释这个图表显示的数据"
```

## 配置

配置文件 `config.json` 包含以下配置项：
- `api_key`: API 密钥
- `base_url`: API 地址
- `model`: 视觉模型名称

## 许可证

MIT