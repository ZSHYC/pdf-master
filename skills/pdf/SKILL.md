---
name: pdf
description: Use when the user wants to work with PDF files - extract text/tables/images, edit/merge/split PDFs, convert formats, OCR, AI summarization, LaTeX rendering, or any PDF-related task.
argument-hint: <action> [file] [options]
---

# PDF Master

全能型 PDF 处理工具。

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
/pdf convert --to-excel document.pdf            # PDF → Excel
/pdf convert --to-markdown document.pdf         # PDF → Markdown
/pdf convert --to-images document.pdf           # PDF → 图片

# AI 增强
/pdf summarize document.pdf                     # AI 摘要
/pdf ask document.pdf "What is this about?"     # AI 问答
/pdf translate document.pdf --to en             # AI 翻译

# OCR
/pdf ocr scanned.pdf                            # OCR 识别

# 安全
/pdf encrypt document.pdf --password secret     # 加密
/pdf decrypt encrypted.pdf --password secret    # 解密
/pdf redact document.pdf --text "sensitive"     # 敏感信息涂抹

# LaTeX
/pdf latex document.tex                         # LaTeX → PDF

# 表单
/pdf form-check document.pdf                   # 检查表单字段
/pdf form-fill document.pdf --data fields.json # 填充表单
```

## 支持的操作

| 类别 | 命令 | 说明 |
|------|------|------|
| 解析 | extract | 提取文本、表格、图片、元数据 |
| 编辑 | merge, split, rotate, watermark | 编辑 PDF |
| 转换 | convert | PDF → Excel/Markdown/图片 |
| AI | summarize, ask, translate | AI 增强 |
| OCR | ocr | OCR 识别 |
| 安全 | encrypt, decrypt, redact | 安全权限 |
| LaTeX | latex | LaTeX → PDF |
| 表单 | form-check, form-fill | 表单操作 |

## 详细文档

- `reference.md` - 高级参考文档
- `forms.md` - 表单填写指南
- `ai.md` - AI 增强功能
- `ocr.md` - OCR 功能
- `latex.md` - LaTeX 排版
- `security.md` - 安全功能
