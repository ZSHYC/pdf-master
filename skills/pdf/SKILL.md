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

全能型 PDF 处理工具，提供 **25+ 种操作**。

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

# 表单处理
/pdf form-check document.pdf
/pdf form-fill document.pdf --data fields.json

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

设置环境变量选择 AI 平台：

| Provider | 环境变量 | 默认模型 |
|----------|----------|----------|
| Claude | `ANTHROPIC_API_KEY` | claude-3-5-sonnet |
| OpenAI | `OPENAI_API_KEY` | gpt-4o |
| Gemini | `GOOGLE_API_KEY` | gemini-2.0-flash |
| DeepSeek | `DEEPSEEK_API_KEY` | deepseek-chat |
| Qwen | `QWEN_API_KEY` | qwen-turbo |
| 智谱 | `ZHIPU_API_KEY` | glm-4-flash |
| Moonshot | `MOONSHOT_API_KEY` | moonshot-v1-8k |
| Ollama | 无需 | llama3.2 |

```bash
python ${CLAUDE_SKILL_DIR}/scripts/summarize_pdf.py doc.pdf --provider openai
python ${CLAUDE_SKILL_DIR}/scripts/qa_pdf.py doc.pdf --question "总结要点" --provider qwen
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
