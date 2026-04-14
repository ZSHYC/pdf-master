---
name: pdf
description: PDF processing toolkit. Extract text/tables/images, merge/split/watermark, format conversion, AI summarization/translation, OCR, encryption/decryption, form handling. Use when working with PDF files, extracting content, converting formats, or applying AI enhancements.
argument-hint: <action> [file] [options]
allowed-tools:
  - Bash
  - Read
  - Glob
  - Grep
user-invocable: true
---

# PDF-Master

全能型 PDF 处理工具，提供 **40+ 种操作**。

## 快速命令

```bash
# 解析提取
/pdf extract document.pdf              # 提取所有内容
/pdf extract --text document.pdf       # 提取文本
/pdf extract --tables document.pdf     # 提取表格
/pdf extract --images document.pdf     # 提取图片
/pdf extract --metadata document.pdf   # 提取元数据

# 编辑修改
/pdf merge file1.pdf file2.pdf -o merged.pdf
/pdf split document.pdf
/pdf rotate document.pdf --angle 90
/pdf watermark document.pdf --image stamp.png

# 格式转换
/pdf convert --to-excel document.pdf
/pdf convert --to-markdown document.pdf
/pdf convert --to-images document.pdf
/pdf pdfa document.pdf -o archive.pdf --level 2b  # PDF/A 存档格式

# AI 增强
/pdf summarize document.pdf
/pdf ask document.pdf "主要观点是什么？"
/pdf translate document.pdf --to en

# OCR 识别
/pdf ocr scanned.pdf

# 安全权限
/pdf encrypt document.pdf --password secret
/pdf decrypt encrypted.pdf --password secret
/pdf redact document.pdf --text "sensitive"
/pdf sign document.pdf --cert cert.p12 --password secret  # 数字签名
/pdf verify document.pdf  # 验证签名
/pdf audit document.pdf   # 安全审计

# 表单处理
/pdf form-check document.pdf
/pdf form-fill document.pdf --data fields.json

# 书签管理
/pdf bookmarks list document.pdf
/pdf bookmarks add document.pdf --title "第一章" --page 1
/pdf bookmarks remove document.pdf --all

# 链接管理
/pdf links list document.pdf
/pdf links add document.pdf --page 1 --rect "100,100,200,120" --url "https://example.com"
/pdf links remove document.pdf --suspicious

# 注释管理
/pdf annotations list document.pdf
/pdf annotations add document.pdf --page 1 --pos "100,100" --contents "重要"
/pdf annotations remove document.pdf --type Highlight

# 批量重命名
/pdf rename *.pdf --rule metadata --template "{author} - {title}"
/pdf rename *.pdf --rule date --template "{date:%Y-%m-%d}_{filename}"
/pdf rename *.pdf --rule content --template "{title}"
/pdf rename *.pdf --rule custom --template "Document_{counter:04d}"
/pdf rename *.pdf --dry-run  # 预览重命名结果
```

## 执行脚本

所有脚本位于 `${CLAUDE_SKILL_DIR}/scripts/`：

```bash
python ${CLAUDE_SKILL_DIR}/scripts/extract_text.py input.pdf -o output.txt
python ${CLAUDE_SKILL_DIR}/scripts/merge_pdfs.py *.pdf -o merged.pdf
python ${CLAUDE_SKILL_DIR}/scripts/summarize_pdf.py document.pdf --provider claude
```

## AI Provider 配置

### 零配置设计

**安装即用！** PDF-Master 自动检测 Claude Code 已有的 API Key：

```bash
# 无需任何配置，直接使用
/pdf summarize document.pdf    # 自动使用 Claude
```

### 内置 Provider 预设（40+）

| 分类 | Provider | 环境变量 | 特点 |
|------|----------|----------|------|
| **官方** | Claude | `ANTHROPIC_API_KEY` | 默认使用，无需配置 |
| | OpenAI | `OPENAI_API_KEY` | GPT 系列 |
| | Gemini | `GOOGLE_API_KEY` | Google 最新模型 |
| **国内** | DeepSeek | `DEEPSEEK_API_KEY` | 性价比极高 |
| | 通义千问 | `QWEN_API_KEY` | 中文效果优秀 |
| | 智谱 GLM | `ZHIPU_API_KEY` | 国产大模型 |
| | Moonshot | `MOONSHOT_API_KEY` | 长文本能力强 |
| **聚合** | OpenRouter | `OPENROUTER_API_KEY` | 一个 Key 访问所有模型 |
| **本地** | Ollama | 无需 | 隐私安全，免费 |

### 快速切换 Provider

```bash
# 方式一：命令行指定
python ${CLAUDE_SKILL_DIR}/scripts/summarize_pdf.py doc.pdf --provider deepseek

# 方式二：设置环境变量
export PDF_MASTER_PROVIDER=qwen

# 方式三：配置文件
cp config/providers.yaml ~/.pdf-master/providers.yaml
```

## 详细文档

- [`reference.md`](reference.md) - 高级参考
- [`ai.md`](ai.md) - AI 功能详解
- [`ocr.md`](ocr.md) - OCR 配置
- [`forms.md`](forms.md) - 表单填写
- [`security.md`](security.md) - 安全功能
- [`latex.md`](latex.md) - LaTeX 排版

## 依赖安装

```bash
pip install pypdf pdfplumber PyMuPDF reportlab Pillow
pip install anthropic openai google-generativeai zhipuai ollama
pip install pytesseract pdf2image  # OCR
pip install pandas openpyxl        # 表格
```
