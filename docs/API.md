# API 文档

本文档详细介绍 PDF-Master 所有脚本的命令行参数、输入输出格式和返回码。

## 解析提取模块

### extract_text.py - 文本提取

**用法:**
```bash
python extract_text.py <input> [options]
```

**参数:**

| 参数 | 简写 | 说明 | 默认值 |
|------|------|------|--------|
| input | - | 输入 PDF 文件路径 | 必需 |
| --output | -o | 输出文件路径 | stdout |
| --format | -f | 输出格式 (text/markdown/json) | text |
| --method | -m | 提取方法 (pypdf/pdfplumber) | pdfplumber |
| --pages | -p | 页面范围 (如 1-5, 1,3,5) | 全部 |

**示例:**
```bash
python extract_text.py document.pdf
python extract_text.py document.pdf -o output.md -f markdown
```

---

### extract_tables.py - 表格提取

**用法:**
```bash
python extract_tables.py <input> [options]
```

**参数:**

| 参数 | 简写 | 说明 | 默认值 |
|------|------|------|--------|
| input | - | 输入 PDF 文件路径 | 必需 |
| --output | -o | 输出文件路径 | stdout |
| --format | -f | 输出格式 (json/csv/excel) | json |

---

### extract_metadata.py - 元数据提取

**用法:**
```bash
python extract_metadata.py <input> [options]
```

**参数:**

| 参数 | 简写 | 说明 | 默认值 |
|------|------|------|--------|
| input | - | 输入 PDF 文件路径 | 必需 |
| --output | -o | 输出文件路径 | stdout |

---

## 编辑修改模块

### merge_pdfs.py - PDF 合并

**用法:**
```bash
python merge_pdfs.py <files...> -o <output> [options]
```

**参数:**

| 参数 | 简写 | 说明 | 默认值 |
|------|------|------|--------|
| files | - | 要合并的 PDF 文件列表 | 必需 |
| --output | -o | 输出文件路径 | 必需 |
| --input-list | -l | 包含文件列表的文本文件 | - |
| --verbose | -v | 显示详细信息 | - |

**示例:**
```bash
python merge_pdfs.py file1.pdf file2.pdf -o merged.pdf
```

---

### split_pdf.py - PDF 拆分

**用法:**
```bash
python split_pdf.py <input> [options]
```

**参数:**

| 参数 | 简写 | 说明 | 默认值 |
|------|------|------|--------|
| input | - | 输入 PDF 文件路径 | 必需 |
| --output-dir | -o | 输出目录 | 源文件目录 |
| --pages | -p | 每个文件的页数 | 1 |

---

### rotate_pdf.py - PDF 旋转

**用法:**
```bash
python rotate_pdf.py <input> [options]
```

**参数:**

| 参数 | 简写 | 说明 | 默认值 |
|------|------|------|--------|
| input | - | 输入 PDF 文件路径 | 必需 |
| --output | -o | 输出文件路径 | rotated_<input> |
| --angle | -a | 旋转角度 (90/180/270) | 90 |

---

### watermark_pdf.py - 添加水印

**用法:**
```bash
python watermark_pdf.py <input> [options]
```

**参数:**

| 参数 | 简写 | 说明 | 默认值 |
|------|------|------|--------|
| input | - | 输入 PDF 文件路径 | 必需 |
| --output | -o | 输出文件路径 | watermarked_<input> |
| --text | -t | 水印文字 | - |
| --image | -i | 水印图片路径 | - |

---

## 格式转换模块

### convert_pdf_to_images.py - PDF 转图片

**用法:**
```bash
python convert_pdf_to_images.py <input> [options]
```

**参数:**

| 参数 | 简写 | 说明 | 默认值 |
|------|------|------|--------|
| input | - | 输入 PDF 文件路径 | 必需 |
| --output-dir | -o | 输出目录 | <input>_images |
| --dpi | - | 分辨率 | 200 |
| --format | -f | 图片格式 (png/jpg) | png |

---

### pdf_to_excel.py - PDF 转 Excel

**用法:**
```bash
python pdf_to_excel.py <input> [options]
```

**参数:**

| 参数 | 简写 | 说明 | 默认值 |
|------|------|------|--------|
| input | - | 输入 PDF 文件路径 | 必需 |
| --output | -o | 输出 Excel 文件路径 | <input>.xlsx |

---

## AI 增强模块

### summarize_pdf.py - AI 摘要

**用法:**
```bash
python summarize_pdf.py <input> [options]
```

**参数:**

| 参数 | 简写 | 说明 | 默认值 |
|------|------|------|--------|
| input | - | 输入 PDF 文件路径 | 必需 |
| --output | -o | 输出文件路径 | stdout |
| --provider | -p | AI 提供商 | claude |
| --model | -m | 模型名称 | 默认模型 |
| --language | -l | 摘要语言 (zh/en) | zh |
| --max-length | - | 最大摘要长度 | 500 |

**支持的 AI 提供商:** claude, openai, gemini, deepseek, qwen, zhipu, moonshot, ollama

---

### translate_pdf.py - AI 翻译

**用法:**
```bash
python translate_pdf.py <input> [options]
```

**参数:**

| 参数 | 简写 | 说明 | 默认值 |
|------|------|------|--------|
| input | - | 输入 PDF 文件路径 | 必需 |
| --output | -o | 输出文件路径 | stdout |
| --to | -t | 目标语言 | en |
| --provider | -p | AI 提供商 | claude |

---

### qa_pdf.py - AI 问答

**用法:**
```bash
python qa_pdf.py <input> <question> [options]
```

**参数:**

| 参数 | 简写 | 说明 | 默认值 |
|------|------|------|--------|
| input | - | 输入 PDF 文件路径 | 必需 |
| question | - | 问题内容 | 必需 |
| --provider | -p | AI 提供商 | claude |

---

## OCR 模块

### ocr_pdf.py - OCR 识别

**用法:**
```bash
python ocr_pdf.py <input> [options]
```

**参数:**

| 参数 | 简写 | 说明 | 默认值 |
|------|------|------|--------|
| input | - | 输入 PDF 文件路径 | 必需 |
| --output | -o | 输出文件路径 | stdout |
| --lang | -l | OCR 语言 | chi_sim+eng |
| --format | -f | 输出格式 (text/json) | text |
| --dpi | - | 图片 DPI | 300 |

---

## 安全模块

### encrypt_pdf.py - PDF 加密

**用法:**
```bash
python encrypt_pdf.py <input> [options]
```

**参数:**

| 参数 | 简写 | 说明 | 默认值 |
|------|------|------|--------|
| input | - | 输入 PDF 文件路径 | 必需 |
| --output | -o | 输出文件路径 | 必需 |
| --password | -p | 用户密码 | 必需 |

---

### decrypt_pdf.py - PDF 解密

**用法:**
```bash
python decrypt_pdf.py <input> [options]
```

**参数:**

| 参数 | 简写 | 说明 | 默认值 |
|------|------|------|--------|
| input | - | 输入 PDF 文件路径 | 必需 |
| --output | -o | 输出文件路径 | 必需 |
| --password | -p | PDF 密码 | 必需 |

---

### redact_pdf.py - 敏感信息涂抹

**用法:**
```bash
python redact_pdf.py <input> [options]
```

**参数:**

| 参数 | 简写 | 说明 | 默认值 |
|------|------|------|--------|
| input | - | 输入 PDF 文件路径 | 必需 |
| --output | -o | 输出文件路径 | 必需 |
| --text | -t | 要涂抹的文本 | - |
| --regex | -r | 正则表达式模式 | - |

---

## 表单模块

### check_fillable_fields.py - 检查表单字段

**用法:**
```bash
python check_fillable_fields.py <input>
```

---

### extract_form_field_info.py - 提取表单字段信息

**用法:**
```bash
python extract_form_field_info.py <input> [options]
```

---

### fill_fillable_fields.py - 填充表单

**用法:**
```bash
python fill_fillable_fields.py <input> --data <json> [options]
```

**参数:**

| 参数 | 简写 | 说明 | 默认值 |
|------|------|------|--------|
| input | - | 输入 PDF 文件路径 | 必需 |
| --data | -d | 字段数据 JSON 文件 | 必需 |
| --output | -o | 输出 PDF 文件路径 | 必需 |

---

## 返回码说明

| 返回码 | 说明 |
|--------|------|
| 0 | 成功 |
| 1 | 失败 |

---

## 错误处理

| 错误信息 | 原因 | 解决方案 |
|----------|------|----------|
| File not found | 文件不存在 | 检查文件路径 |
| Not a PDF file | 文件不是 PDF 格式 | 确认文件扩展名 |
| Missing API key | 未设置 API Key | 设置环境变量 |
| No text found | PDF 无文本内容 | 尝试 OCR |
