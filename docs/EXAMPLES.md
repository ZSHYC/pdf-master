# 使用示例

本文档提供 PDF-Master 的常见使用场景示例。

## 目录

- [基础使用](#基础使用)
- [批量处理](#批量处理)
- [AI 功能使用](#ai-功能使用)
- [OCR 使用](#ocr-使用)
- [表单处理](#表单处理)
- [安全功能](#安全功能)
- [格式转换](#格式转换)

---

## 基础使用

### 提取文本

```bash
# 提取所有文本
python skills/pdf/scripts/extract_text.py document.pdf

# 保存到文件
python skills/pdf/scripts/extract_text.py document.pdf -o output.txt

# Markdown 格式
python skills/pdf/scripts/extract_text.py document.pdf -f markdown -o output.md

# 仅提取指定页面
python skills/pdf/scripts/extract_text.py document.pdf -p 1-5
```

### 提取表格

```bash
# 提取所有表格
python skills/pdf/scripts/extract_tables.py document.pdf

# 导出为 Excel
python skills/pdf/scripts/extract_tables.py document.pdf -f excel -o tables.xlsx
```

### 查看元数据

```bash
python skills/pdf/scripts/extract_metadata.py document.pdf
```

---

## 批量处理

### 批量提取文本

```bash
#!/bin/bash
# 批量提取所有 PDF 的文本

for pdf in *.pdf; do
    name=$(basename "$pdf" .pdf)
    python skills/pdf/scripts/extract_text.py "$pdf" -o "${name}.txt"
done
```

### 批量合并

```bash
#!/bin/bash
# 合并所有章节 PDF

python skills/pdf/scripts/merge_pdfs.py chapter*.pdf -o book.pdf -v
```

### 批量转换图片

```bash
#!/bin/bash
# 批量转换 PDF 为图片

for pdf in documents/*.pdf; do
    name=$(basename "$pdf" .pdf)
    python skills/pdf/scripts/convert_pdf_to_images.py "$pdf" -o "images/$name" --dpi 300
done
```

---

## AI 功能使用

### 生成摘要

```bash
# 使用默认 Claude
python skills/pdf/scripts/summarize_pdf.py document.pdf

# 使用 OpenAI
python skills/pdf/scripts/summarize_pdf.py document.pdf --provider openai

# 使用本地 Ollama
python skills/pdf/scripts/summarize_pdf.py document.pdf --provider ollama

# 保存摘要
python skills/pdf/scripts/summarize_pdf.py document.pdf -o summary.txt

# 英文摘要
python skills/pdf/scripts/summarize_pdf.py document.pdf -l en
```

### 文档问答

```bash
# 询问问题
python skills/pdf/scripts/qa_pdf.py document.pdf "这个文档的主要结论是什么？"

# 使用不同模型
python skills/pdf/scripts/qa_pdf.py document.pdf "作者是谁？" --provider openai
```

### 翻译文档

```bash
# 翻译为英文
python skills/pdf/scripts/translate_pdf.py document.pdf --to en

# 翻译为日文
python skills/pdf/scripts/translate_pdf.py document.pdf -t ja -o translated.txt
```

---

## OCR 使用

### 基本 OCR

```bash
# 中英文识别
python skills/pdf/scripts/ocr_pdf.py scanned.pdf

# 仅英文
python skills/pdf/scripts/ocr_pdf.py scanned.pdf -l eng

# 高精度识别
python skills/pdf/scripts/ocr_pdf.py scanned.pdf --dpi 400
```

### 批量 OCR

```bash
#!/bin/bash
# 批量 OCR 识别

for pdf in scanned/*.pdf; do
    name=$(basename "$pdf" .pdf)
    python skills/pdf/scripts/ocr_pdf.py "$pdf" -l chi_sim+eng -o "ocr_results/${name}.txt"
done
```

---

## 表单处理

### 检查表单字段

```bash
# 检查是否有表单
python skills/pdf/scripts/check_fillable_fields.py form.pdf

# 提取字段信息
python skills/pdf/scripts/extract_form_field_info.py form.pdf -o fields.json
```

### 填充表单

```bash
# 创建字段数据文件
cat > fields.json << 'EOF'
{
  "fields": {
    "name": "张三",
    "email": "zhangsan@example.com",
    "phone": "13800138000",
    "department": "技术部",
    "agree": true
  }
}
EOF

# 填充表单
python skills/pdf/scripts/fill_fillable_fields.py form.pdf -d fields.json -o filled_form.pdf
```

---

## 安全功能

### 加密 PDF

```bash
# 设置打开密码
python skills/pdf/scripts/encrypt_pdf.py document.pdf -o encrypted.pdf -p mypassword

# 设置不同密码
python skills/pdf/scripts/encrypt_pdf.py document.pdf -o encrypted.pdf -p userpwd --owner-password ownerpwd
```

### 解密 PDF

```bash
python skills/pdf/scripts/decrypt_pdf.py encrypted.pdf -o decrypted.pdf -p mypassword
```

### 敏感信息涂抹

```bash
# 涂抹特定文字
python skills/pdf/scripts/redact_pdf.py document.pdf --text "机密" -o redacted.pdf

# 使用正则表达式涂抹手机号
python skills/pdf/scripts/redact_pdf.py document.pdf -r "1[3-9]\d{9}" -o redacted.pdf

# 涂抹身份证号
python skills/pdf/scripts/redact_pdf.py document.pdf -r "\d{17}[\dXx]" -o redacted.pdf
```

---

## 格式转换

### PDF 转图片

```bash
# 基本转换
python skills/pdf/scripts/convert_pdf_to_images.py document.pdf

# 高分辨率
python skills/pdf/scripts/convert_pdf_to_images.py document.pdf --dpi 300

# 输出为 JPG
python skills/pdf/scripts/convert_pdf_to_images.py document.pdf -f jpg
```

### PDF 转 Excel

```bash
python skills/pdf/scripts/pdf_to_excel.py tables.pdf -o output.xlsx
```

### PDF 转 Markdown

```bash
python skills/pdf/scripts/pdf_to_markdown.py document.pdf -o output.md
```

---

## 编辑操作

### 合并 PDF

```bash
# 合并多个文件
python skills/pdf/scripts/merge_pdfs.py part1.pdf part2.pdf part3.pdf -o merged.pdf

# 使用通配符
python skills/pdf/scripts/merge_pdfs.py chapter*.pdf -o book.pdf -v

# 从列表文件读取
cat > files.txt << 'EOF'
cover.pdf
chapter1.pdf
chapter2.pdf
appendix.pdf
EOF
python skills/pdf/scripts/merge_pdfs.py -l files.txt -o book.pdf
```

### 拆分 PDF

```bash
# 每页一个文件
python skills/pdf/scripts/split_pdf.py document.pdf

# 每 5 页一个文件
python skills/pdf/scripts/split_pdf.py document.pdf -p 5

# 指定输出目录
python skills/pdf/scripts/split_pdf.py document.pdf -o ./split/
```

### 旋转页面

```bash
# 所有页面旋转 90 度
python skills/pdf/scripts/rotate_pdf.py document.pdf --angle 90

# 旋转 180 度
python skills/pdf/scripts/rotate_pdf.py document.pdf -a 180
```

### 添加水印

```bash
# 文字水印
python skills/pdf/scripts/watermark_pdf.py document.pdf --text "CONFIDENTIAL"

# 图片水印
python skills/pdf/scripts/watermark_pdf.py document.pdf --image logo.png -o watermarked.pdf
```

---

## 完整工作流示例

### 文档归档工作流

```bash
#!/bin/bash
# 完整的文档归档工作流

INPUT="report.pdf"
OUTPUT_DIR="archive"

mkdir -p "$OUTPUT_DIR"

# 1. 提取文本
python skills/pdf/scripts/extract_text.py "$INPUT" -f markdown -o "$OUTPUT_DIR/text.md"

# 2. 提取表格
python skills/pdf/scripts/extract_tables.py "$INPUT" -f excel -o "$OUTPUT_DIR/tables.xlsx"

# 3. 提取元数据
python skills/pdf/scripts/extract_metadata.py "$INPUT" -o "$OUTPUT_DIR/metadata.json"

# 4. 生成摘要
python skills/pdf/scripts/summarize_pdf.py "$INPUT" -o "$OUTPUT_DIR/summary.txt"

# 5. 转换为图片
python skills/pdf/scripts/convert_pdf_to_images.py "$INPUT" -o "$OUTPUT_DIR/images/"

echo "归档完成: $OUTPUT_DIR"
```

### 敏感文档处理流程

```bash
#!/bin/bash
# 敏感文档处理：涂抹 + 加密

INPUT="sensitive.pdf"

# 1. 涂抹敏感信息
python skills/pdf/scripts/redact_pdf.py "$INPUT"     -r "1[3-9]\d{9}"     -r "\d{17}[\dXx]"     -o temp_redacted.pdf

# 2. 加密
python skills/pdf/scripts/encrypt_pdf.py temp_redacted.pdf     -o processed.pdf     -p viewer123

# 3. 清理临时文件
rm temp_redacted.pdf

echo "敏感文档处理完成: processed.pdf"
```
