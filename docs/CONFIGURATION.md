# 配置指南

本文档详细介绍 PDF-Master 的配置选项。

## 目录

- [零配置设计](#零配置设计)
- [AI Provider 配置](#ai-provider-配置)
- [OCR 配置](#ocr-配置)
- [输出配置](#输出配置)
- [环境变量配置](#环境变量配置)
- [YAML 配置文件](#yaml-配置文件)
- [成本管理配置](#成本管理配置)

---

## 零配置设计

### 设计理念

**安装即用！** PDF-Master 采用零配置设计：

```
用户安装 Claude Code → 已有 ANTHROPIC_API_KEY → 自动检测并使用
```

无需任何配置，即可使用 AI 功能：

```bash
# 直接使用，自动检测 Claude API Key
/pdf summarize document.pdf
```

### 自动检测优先级

| 优先级 | 来源 | 说明 |
|--------|------|------|
| 1 | 环境变量 | `ANTHROPIC_API_KEY` 等 |
| 2 | 用户配置 | `~/.pdf-master/providers.yaml` |
| 3 | 项目配置 | `./config/providers.yaml` |
| 4 | Claude Code 设置 | 自动检测已安装工具的配置 |

---

## AI Provider 配置

### Provider 预设库（40+）

PDF-Master 内置 40+ Provider 预设，按分类组织：

#### 🟠 官方 Provider

| Provider | 环境变量 | 默认模型 | 特点 |
|----------|----------|----------|------|
| Claude | `ANTHROPIC_API_KEY` | claude-sonnet-4-6 | **默认使用** |
| OpenAI | `OPENAI_API_KEY` | gpt-4o | GPT 系列 |
| Gemini | `GOOGLE_API_KEY` | gemini-2.0-flash-exp | Google 最新 |

#### 🔴 国内官方 Provider

| Provider | 环境变量 | 默认模型 | 特点 |
|----------|----------|----------|------|
| DeepSeek | `DEEPSEEK_API_KEY` | deepseek-chat | 性价比极高 |
| 通义千问 | `QWEN_API_KEY` | qwen-turbo | 中文效果优秀 |
| 智谱 GLM | `ZHIPU_API_KEY` | glm-4-flash | 国产大模型 |
| Moonshot | `MOONSHOT_API_KEY` | moonshot-v1-8k | 长文本能力强 |
| 豆包 | `DOUBAO_API_KEY` | doubao-pro-32k | 字节跳动 |
| MiniMax | `MINIMAX_API_KEY` | abab6.5-chat | ABAB 系列 |
| 阶跃星辰 | `STEPFUN_API_KEY` | step-1-8k | Step 系列 |

#### 🟣 聚合平台 Provider

| Provider | 环境变量 | 特点 |
|----------|----------|------|
| OpenRouter | `OPENROUTER_API_KEY` | 一个 Key 访问所有模型 |
| SiliconFlow | `SILICONFLOW_API_KEY` | 国内聚合平台，性价比高 |
| ModelScope | `MODELSCOPE_API_KEY` | 阿里云模型聚合 |
| AiHubMix | `AIHUBMIX_API_KEY` | 多模型聚合 |

#### ⚫ 本地 Provider

| Provider | 地址 | 特点 |
|----------|------|------|
| Ollama | http://localhost:11434 | 本地运行，隐私安全 |
| LM Studio | http://localhost:1234 | 本地推理 |
| vLLM | http://localhost:8000 | 高性能推理 |

### 快速配置

#### 方式一：环境变量（推荐）

```bash
# Linux / macOS
export ANTHROPIC_API_KEY="your-key"      # Claude（默认）
export OPENAI_API_KEY="your-key"         # OpenAI
export DEEPSEEK_API_KEY="your-key"       # DeepSeek

# Windows PowerShell
[Environment]::SetEnvironmentVariable("ANTHROPIC_API_KEY", "your-key", "User")
```

#### 方式二：配置文件

```bash
# 复制配置模板
cp config/providers.yaml ~/.pdf-master/providers.yaml

# 编辑配置
nano ~/.pdf-master/providers.yaml
```

#### 方式三：命令行指定

```bash
# 单次使用指定 Provider
/pdf summarize document.pdf --provider deepseek
/pdf summarize document.pdf --provider qwen --model qwen-max
```

### 切换默认 Provider

```bash
# 方式一：环境变量
export PDF_MASTER_PROVIDER=qwen

# 方式二：配置文件
# 编辑 ~/.pdf-master/providers.yaml
default_provider: qwen
```

### 模型选择建议

| 场景 | 推荐提供商 | 推荐模型 | 说明 |
|------|-----------|----------|------|
| 日常使用 | Claude | claude-sonnet-4-6 | 默认，无需配置 |
| 中文优化 | 通义千问 | qwen-turbo | 中文效果好 |
| 成本敏感 | DeepSeek | deepseek-chat | 价格低廉 |
| 长文本 | Moonshot | moonshot-v1-128k | 128K 上下文 |
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
      model: claude-sonnet-4-6
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
| Claude Sonnet 4.6 | $3/1M tokens | $15/1M tokens |
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

### 如何使用 Claude Code 已有的 API Key？

**无需配置！** PDF-Master 自动检测 Claude Code 的 `ANTHROPIC_API_KEY`，直接使用即可。
