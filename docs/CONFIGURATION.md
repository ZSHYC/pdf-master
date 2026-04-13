# 配置指南

本文档详细介绍 PDF-Master 的配置选项，包括 AI Provider 配置、OCR 配置、环境变量设置等。

## 目录

- [AI Provider 配置](#ai-provider-配置)
- [OCR 配置](#ocr-配置)
- [输出配置](#输出配置)
- [环境变量配置](#环境变量配置)
- [YAML 配置文件](#yaml-配置文件)
- [成本管理配置](#成本管理配置)

---

## AI Provider 配置

PDF-Master 支持 8 个 AI 提供商，可通过环境变量或 YAML 配置文件进行配置。

### 支持的提供商

| 提供商 | 标识符 | 环境变量 | 默认模型 | 类型 |
|--------|--------|----------|----------|------|
| Anthropic Claude | claude | ANTHROPIC_API_KEY | claude-3-5-sonnet-20241022 | 云端 |
| OpenAI | openai | OPENAI_API_KEY | gpt-4o | 云端 |
| Google Gemini | gemini | GOOGLE_API_KEY | gemini-2.0-flash-exp | 云端 |
| DeepSeek | deepseek | DEEPSEEK_API_KEY | deepseek-chat | 云端 |
| 通义千问 | qwen | QWEN_API_KEY | qwen-turbo | 云端 |
| 智谱 GLM | zhipu | ZHIPU_API_KEY | glm-4-flash | 云端 |
| Moonshot | moonshot | MOONSHOT_API_KEY | moonshot-v1-8k | 云端 |
| Ollama | ollama | 无需 | llama3.2 | 本地 |

### 环境变量配置

#### Linux / macOS

编辑 ~/.bashrc 或 ~/.zshrc:

```bash
export ANTHROPIC_API_KEY="your-anthropic-api-key"
export OPENAI_API_KEY="your-openai-api-key"
export GOOGLE_API_KEY="your-google-api-key"
export DEEPSEEK_API_KEY="your-deepseek-api-key"
export QWEN_API_KEY="your-qwen-api-key"
export ZHIPU_API_KEY="your-zhipu-api-key"
export MOONSHOT_API_KEY="your-moonshot-api-key"
export OLLAMA_BASE_URL="http://localhost:11434"
```

使配置生效:

```bash
source ~/.bashrc
```

#### Windows (PowerShell)

```powershell
[Environment]::SetEnvironmentVariable("ANTHROPIC_API_KEY", "your-api-key", "User")
[Environment]::SetEnvironmentVariable("OPENAI_API_KEY", "your-api-key", "User")
```

#### Windows (CMD)

```cmd
setx ANTHROPIC_API_KEY "your-api-key"
setx OPENAI_API_KEY "your-api-key"
```

### 指定 AI Provider

#### 命令行指定

```bash
python summarize_pdf.py document.pdf
python summarize_pdf.py document.pdf --provider openai
python summarize_pdf.py document.pdf --provider qwen
python summarize_pdf.py document.pdf --provider ollama --model llama3.2
```

### 模型选择建议

| 场景 | 推荐提供商 | 推荐模型 | 说明 |
|------|-----------|----------|------|
| 日常使用 | Claude | claude-3-5-sonnet-20241022 | 性价比高 |
| 中文优化 | 通义千问 | qwen-turbo | 中文效果好 |
| 成本敏感 | DeepSeek | deepseek-chat | 价格低廉 |
| 隐私要求 | Ollama | llama3.2 | 本地运行 |

---

## OCR 配置

### 支持的 OCR 引擎

| 引擎 | 特点 | 语言支持 | 适用场景 |
|------|------|----------|----------|
| Tesseract | 开源免费 | 100+ 语言 | 通用 OCR |
| PaddleOCR | 中文最佳 | 80+ 语言 | 中文文档 |
| EasyOCR | 深度学习 | 80+ 语言 | 多语言混合 |

### Tesseract 安装

#### Windows

```bash
choco install tesseract
```

#### macOS

```bash
brew install tesseract
brew install tesseract-lang
```

#### Linux

```bash
sudo apt-get install tesseract-ocr
sudo apt-get install tesseract-ocr-chi-sim
```

### poppler 安装

#### Windows

下载: https://github.com/oschwartz10612/poppler-windows/releases

#### macOS

```bash
brew install poppler
```

#### Linux

```bash
sudo apt-get install poppler-utils
```

### OCR 语言配置

```bash
python ocr_pdf.py scanned.pdf -l chi_sim
python ocr_pdf.py scanned.pdf -l chi_sim+eng
```

---

## YAML 配置文件

### 配置文件示例

```yaml
ai:
  default_provider: claude
  providers:
    claude:
      api_key: ${ANTHROPIC_API_KEY}
      model: claude-3-5-sonnet-20241022
    openai:
      api_key: ${OPENAI_API_KEY}
      model: gpt-4o
    ollama:
      base_url: http://localhost:11434
      model: llama3.2

ocr:
  default_engine: tesseract
  engines:
    tesseract:
      languages: [chi_sim, eng]

output:
  default_format: markdown
  default_dir: ./output
```

---

## 成本管理配置

### Token 使用估算

| 模型 | 输入价格 | 输出价格 |
|------|----------|----------|
| Claude 3.5 Sonnet | $3/1M tokens | $15/1M tokens |
| GPT-4o | $2.5/1M tokens | $10/1M tokens |
| DeepSeek | $0.14/1M tokens | $0.28/1M tokens |

### 成本控制策略

1. 限制文本长度
2. 使用缓存
3. 选择合适模型

---

## 常见配置问题

### API Key 配置后仍然报错

1. 检查环境变量是否正确设置
2. 是否重启了终端
3. API Key 是否有效

### Ollama 连接失败

```bash
curl http://localhost:11434/api/tags
ollama list
ollama pull llama3.2
```
