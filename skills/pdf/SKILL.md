---
name: pdf
description: Use when the user wants to work with PDF files - extract text/tables/images, edit/merge/split PDFs, convert formats, OCR, AI summarization, LaTeX rendering, or any PDF-related task.
argument-hint: <action> [file] [options]
---

# PDF-Master

全能型 PDF 处理工具，提供 **20+ 种 PDF 操作能力**，覆盖解析、编辑、转换、AI 增强、OCR、安全等全场景需求。

## 快速开始

```bash
# 解析提取
/pdf extract document.pdf              # 提取所有内容
/pdf extract --text document.pdf       # 只提取文本
/pdf extract --tables document.pdf     # 只提取表格
/pdf extract --images document.pdf     # 只提取图片
/pdf extract --metadata document.pdf   # 只提取元数据

# 编辑修改
/pdf merge file1.pdf file2.pdf -o merged.pdf    # 合并
/pdf split document.pdf                         # 拆分
/pdf rotate document.pdf --angle 90             # 旋转
/pdf watermark document.pdf --image stamp.png   # 水印

# 格式转换
/pdf convert --to-excel document.pdf            # PDF -> Excel
/pdf convert --to-markdown document.pdf         # PDF -> Markdown
/pdf convert --to-images document.pdf           # PDF -> 图片

# AI 增强（支持 8 大 AI 平台）
/pdf summarize document.pdf                     # AI 摘要
/pdf ask document.pdf "What is this about?"     # AI 问答
/pdf translate document.pdf --to en             # AI 翻译

# OCR 识别
/pdf ocr scanned.pdf                            # OCR 识别（支持 Tesseract/PaddleOCR）

# 安全权限
/pdf encrypt document.pdf --password secret     # 加密
/pdf decrypt encrypted.pdf --password secret    # 解密
/pdf redact document.pdf --text "sensitive"     # 敏感信息涂抹

# 表单处理
/pdf form-check document.pdf                   # 检查表单字段
/pdf form-fill document.pdf --data fields.json # 填充表单
```

---

## 功能列表

### 解析提取

| 命令 | 脚本 | 说明 | 输出格式 |
|------|------|------|----------|
| extract --text | `extract_text.py` | 提取文本内容 | txt, md, json |
| extract --tables | `extract_tables.py` | 提取表格数据 | json, csv, xlsx |
| extract --images | `extract_images.py` | 提取图片 | png, jpg, tiff |
| extract --metadata | `extract_metadata.py` | 提取元数据 | json |

### 编辑修改

| 命令 | 脚本 | 说明 |
|------|------|------|
| merge | `merge_pdfs.py` | 合并多个 PDF |
| split | `split_pdf.py` | 拆分 PDF（按页/范围） |
| rotate | `rotate_pdf.py` | 旋转页面（90/180/270 度） |
| watermark | `watermark_pdf.py` | 添加水印（文字/图片） |

### 格式转换

| 命令 | 脚本 | 说明 |
|------|------|------|
| convert --to-images | `convert_pdf_to_images.py` | PDF -> 图片（PNG/JPEG） |
| convert --to-excel | `pdf_to_excel.py` | PDF -> Excel |
| convert --to-markdown | `pdf_to_markdown.py` | PDF -> Markdown |

### AI 增强

| 命令 | 脚本 | 说明 | 支持的 AI 平台 |
|------|------|------|----------------|
| summarize | `summarize_pdf.py` | AI 智能摘要 | Claude, OpenAI, Gemini, DeepSeek, Qwen, 智谱, Moonshot, Ollama |
| ask | `qa_pdf.py` | 文档问答 | 同上 |
| translate | `translate_pdf.py` | AI 翻译 | 同上 |

### OCR 识别

| 命令 | 脚本 | 说明 | 支持引擎 |
|------|------|------|----------|
| ocr | `ocr_pdf.py` | 扫描件文字识别 | Tesseract, PaddleOCR |

### 安全权限

| 命令 | 脚本 | 说明 |
|------|------|------|
| encrypt | `encrypt_pdf.py` | PDF 加密（AES-256） |
| decrypt | `decrypt_pdf.py` | PDF 解密 |
| redact | `redact_pdf.py` | 敏感信息涂抹 |

### 表单处理

| 命令 | 脚本 | 说明 |
|------|------|------|
| form-check | `check_fillable_fields.py` | 检查表单字段 |
| form-info | `extract_form_field_info.py` | 提取表单字段信息 |
| form-fill | `fill_fillable_fields.py` | 填充表单 |

---

## AI Provider 配置

PDF-Master 支持 **8 大 AI 平台**，提供统一的接口：

| 提供商 | 环境变量 | 默认模型 | 说明 |
|--------|----------|----------|------|
| Claude | `ANTHROPIC_API_KEY` | claude-3-5-sonnet | Anthropic Claude |
| OpenAI | `OPENAI_API_KEY` | gpt-4o | OpenAI GPT |
| Gemini | `GOOGLE_API_KEY` | gemini-2.0-flash | Google Gemini |
| DeepSeek | `DEEPSEEK_API_KEY` | deepseek-chat | DeepSeek |
| Qwen | `QWEN_API_KEY` | qwen-turbo | 通义千问 |
| 智谱 | `ZHIPU_API_KEY` | glm-4-flash | 智谱 GLM |
| Moonshot | `MOONSHOT_API_KEY` | moonshot-v1-8k | Moonshot AI |
| Ollama | 无需 | llama3.2 | 本地运行 |

### 使用示例

```bash
# 使用默认 Claude
export ANTHROPIC_API_KEY=your_key
python summarize_pdf.py document.pdf

# 指定 AI 平台
python summarize_pdf.py document.pdf --provider openai
python summarize_pdf.py document.pdf --provider qwen
python summarize_pdf.py document.pdf --provider ollama --model llama3.2

# 文档问答
python qa_pdf.py document.pdf --question "主要观点是什么？" --provider claude

# 翻译
python translate_pdf.py document.pdf --to en --provider openai
```

---

## 脚本工具

所有脚本位于 `skills/pdf/scripts/` 目录：

### 核心模块

| 文件 | 说明 |
|------|------|
| `ai_provider.py` | AI 提供商统一接口（支持 8 大平台） |
| `pdf_utils.py` | PDF 公共工具（页码解析、进度显示、批量处理） |
| `form_utils.py` | 表单处理公共模块 |
| `_utils.py` | 内部工具函数 |

### 使用方式

```bash
# 直接运行脚本
python skills/pdf/scripts/extract_text.py input.pdf -o output.txt

# 指定输出格式
python skills/pdf/scripts/extract_text.py input.pdf -f markdown

# 批量合并
python skills/pdf/scripts/merge_pdfs.py *.pdf -o merged.pdf

# 指定页码范围
python skills/pdf/scripts/split_pdf.py input.pdf -p 1-5 -o part1.pdf
```

---

## 配置系统

配置文件位于 `config/config.yaml`，参考 `config/config.yaml.example`。

### AI 配置

```yaml
ai:
  default_provider: claude
  providers:
    claude:
      model: claude-3-5-sonnet
      max_tokens: 4096
    openai:
      model: gpt-4o
    qwen:
      model: qwen-turbo
    ollama:
      base_url: http://localhost:11434
      model: llama3.2
```

### OCR 配置

```yaml
ocr:
  default_engine: tesseract
  engines:
    tesseract:
      languages: [chi_sim, eng]
    paddleocr:
      use_gpu: false
      lang: ch
```

### 输出配置

```yaml
output:
  default_format: markdown
  default_dir: ./output
```

---

## 参数说明

### extract_text.py

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `pdf` | PDF 文件路径 | 必填 |
| `-o, --output` | 输出文件路径 | stdout |
| `-f, --format` | 输出格式 (text/markdown/json) | text |

### merge_pdfs.py

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `pdfs` | PDF 文件列表 | 必填 |
| `-o, --output` | 输出文件路径 | 必填 |

### split_pdf.py

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `pdf` | PDF 文件路径 | 必填 |
| `-o, --output-dir` | 输出目录 | 当前目录 |
| `-p, --pages` | 每个文件的页数 | 1 |

### summarize_pdf.py

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `pdf` | PDF 文件路径 | 必填 |
| `-o, --output` | 输出文件路径 | stdout |
| `--provider` | AI 提供商 | claude |
| `--model` | 模型名称 | 默认模型 |
| `-l, --language` | 摘要语言 | zh |

### ocr_pdf.py

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `pdf` | PDF 文件路径 | 必填 |
| `-o, --output` | 输出文件路径 | stdout |
| `-l, --lang` | OCR 语言 | chi_sim+eng |
| `-f, --format` | 输出格式 (text/json) | text |

---

## 详细文档

| 文档 | 说明 |
|------|------|
| [`reference.md`](reference.md) | 高级参考文档 |
| [`forms.md`](forms.md) | 表单填写指南 |
| [`ai.md`](ai.md) | AI 增强功能详解 |
| [`ocr.md`](ocr.md) | OCR 功能配置 |
| [`latex.md`](latex.md) | LaTeX 排版 |
| [`security.md`](security.md) | 安全功能说明 |
| [`docs/SECURITY_AUDIT.md`](docs/SECURITY_AUDIT.md) | 安全审计报告 |

---

## 依赖安装

```bash
# 核心依赖
pip install pypdf pdfplumber PyMuPDF reportlab Pillow

# AI 功能
pip install anthropic openai google-generativeai zhipuai ollama

# OCR 功能
pip install pytesseract pdf2image
# 或 PaddleOCR
pip install paddlepaddle paddleocr

# 表格/Excel
pip install pandas openpyxl
```
