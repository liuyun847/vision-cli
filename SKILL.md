---
name: vision-analysis
description: 使用视觉模型分析图片内容，支持本地文件、URL 和 base64 编码输入, 需要读图时调用
---

# 图片分析技能

## 描述
使用 OpenAI 兼容的视觉模型 API 分析图片内容，提取文字、描述场景、识别对象等。

## 使用场景
- 需要分析图片内容时
- 提取图片中的文字信息
- 描述图片场景或对象
- 回答关于图片的问题

## 使用方式
调用技能目录下的 `vision-cli.py` 命令行工具进行分析：

```bash
# 分析本地图片
python vision-cli.py --image "图片路径" --prompt "分析提示词"

# 分析 URL 图片
python vision-cli.py --image "图片URL" --prompt "分析提示词"

# 使用自定义配置文件
python vision-cli.py --config "其他配置文件路径" --image "图片" --prompt "提示词"
```

注意：默认自动加载技能目录中的 `config.json`，通常不需要指定 `--config` 参数。


## 示例
```bash
# 描述图片内容
python vision-cli.py --image "photo.jpg" --prompt "详细描述这张图片的内容"

# 提取文字
python vision-cli.py --image "document.png" --prompt "提取图片中的所有文字"

# 分析图表
python vision-cli.py --image "chart.png" --prompt "解释这个图表显示的数据"
```