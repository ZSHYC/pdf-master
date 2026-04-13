# 高级参考文档

## Python 库使用指南

### pypdf

纯 Python 库，无需外部依赖，适合基础操作。

```python
from pypdf import PdfReader, PdfWriter

# 读取 PDF
reader = PdfReader("document.pdf")
print(f"页数: {len(reader.pages)}")

# 提取文本
for page in reader.pages:
    text = page.extract_text()
    print(text)

# 合并 PDF
writer = PdfWriter()
for pdf in ["file1.pdf", "file2.pdf"]:
    writer.append(pdf)
writer.write("merged.pdf")

# 拆分 PDF
reader = PdfReader("document.pdf")
writer = PdfWriter()
writer.append_pages_from_reader(reader, [0, 1])  # 前2页
writer.write("first_two_pages.pdf")

# 加密
writer = PdfWriter()
writer.append("document.pdf")
writer.encrypt("password")
writer.write("encrypted.pdf")

# 添加水印
from pypdf import PdfReader, PdfWriter, Transformation
reader = PdfReader("document.pdf")
watermark = PdfReader("stamp.pdf").pages[0]
writer = PdfWriter()
for page in reader.pages:
    page.merge_page(watermark)
    writer.add_page(page)
writer.write("watermarked.pdf")
```

### pdfplumber

基于 pdfminer，擅长表格提取。

```python
import pdfplumber

with pdfplumber.open("document.pdf") as pdf:
    # 提取文本
    for page in pdf.pages:
        text = page.extract_text()
        print(text)

    # 提取表格
    for page in pdf.pages:
        tables = page.extract_tables()
        for table in tables:
            for row in table:
                print(row)

    # 提取图片
    for page in pdf.pages:
        images = page.images
        for img in images:
            print(f"图片位置: ({img['x0']}, {img['top']})")
```

### PyMuPDF (fitz)

高性能库，支持图像提取和渲染。

```python
import fitz  # PyMuPDF

# 打开文档
doc = fitz.open("document.pdf")

# 提取文本
for page in doc:
    text = page.get_text()
    print(text)

# 提取图片
for page in doc:
    images = page.get_images()
    for img_index, img in enumerate(images):
        xref = img[0]
        pix = fitz.Pixmap(doc, xref)
        pix.save(f"image_{img_index}.png")

# 渲染页面为图片
page = doc[0]
pix = page.get_pixmap(dpi=150)
pix.save("page_1.png")

# 添加注释
page = doc[0]
annot = page.add_highlight_annot(fitz.Rect(100, 100, 200, 120))
annot.set_colors(stroke=(1, 1, 0))  # 黄色高亮

# 文本搜索
for page in doc:
    areas = page.search_for("关键词")
    for area in areas:
        print(f"找到: {area}")

doc.close()
```

## 命令行工具

### pdftotext (poppler)

提取 PDF 文本内容。

```bash
# 基本用法
pdftotext document.pdf output.txt

# 保留布局
pdftotext -layout document.pdf output.txt

# 指定页面范围
pdftotext -f 1 -l 5 document.pdf output.txt  # 第1-5页

# 输出到 stdout
pdftotext document.pdf -
```

### qpdf

强大的 PDF 操作工具。

```bash
# 合并 PDF
qpdf --empty --add file1.pdf --add file2.pdf -- output.pdf

# 拆分 PDF
qpdf --split-pages document.pdf output_%d.pdf

# 加密
qpdf --encrypt user_password owner_password 256 -- document.pdf encrypted.pdf

# 解密
qpdf --decrypt --password=secret encrypted.pdf decrypted.pdf

# 旋转
qpdf --rotate=+90:1 document.pdf rotated.pdf  # 第1页顺时针90度

# 线性化(优化网页浏览)
qpdf --linearize document.pdf optimized.pdf

# 检查 PDF
qpdf --check document.pdf
```

### pdftk

PDF 工具包。

```bash
# 合并
pdftk file1.pdf file2.pdf cat output merged.pdf

# 拆分
pdftk document.pdf burst output page_%d.pdf

# 旋转
pdftk document.pdf cat 1-endsouth output rotated.pdf

# 加密
pdftk document.pdf output encrypted.pdf user_pw secret

# 解密
pdftk encrypted.pdf input_pw secret output decrypted.pdf

# 提取页面
pdftk document.pdf cat 1-5 output pages_1-5.pdf
```

## 常见问题解决方案

### 问题：提取的文本乱码

```python
# 方案1：使用 PyMuPDF 指定编码
import fitz
doc = fitz.open("document.pdf")
for page in doc:
    text = page.get_text("text", flags=fitz.TEXT_PRESERVE_WHITESPACE)

# 方案2：使用 OCR
import pytesseract
from pdf2image import convert_from_path
images = convert_from_path("document.pdf")
for img in images:
    text = pytesseract.image_to_string(img, lang='chi_sim+eng')
```

### 问题：表格提取不完整

```python
# 方案1：调整 pdfplumber 设置
import pdfplumber
with pdfplumber.open("document.pdf") as pdf:
    page = pdf.pages[0]
    tables = page.extract_tables({
        "vertical_strategy": "text",
        "horizontal_strategy": "text"
    })

# 方案2：使用 camelot
import camelot
tables = camelot.read_pdf("document.pdf", flavor='stream')
```

### 问题：PDF 无法打开或损坏

```bash
# 修复 PDF
qpdf --qdf document.pdf repaired.pdf

# 或使用 Ghostscript
gs -o repaired.pdf -sDEVICE=pdfwrite -dPDFSETTINGS=/prepress document.pdf
```

### 问题：PDF 文件过大

```bash
# 使用 Ghostscript 压缩
gs -sDEVICE=pdfwrite -dCompatibilityLevel=1.4 -dPDFSETTINGS=/ebook \
   -dNOPAUSE -dBATCH -sOutputFile=compressed.pdf document.pdf

# 压缩级别选项：
# /screen  - 72 dpi, 最小文件
# /ebook   - 150 dpi, 中等质量
# /printer - 300 dpi, 高质量
```

### 问题：提取图片质量低

```python
import fitz
doc = fitz.open("document.pdf")

# 使用更高的 DPI
page = doc[0]
pix = page.get_pixmap(dpi=300)  # 默认 72
pix.save("high_quality.png")

# 提取原始图片
for img_index, img in enumerate(page.get_images()):
    xref = img[0]
    pix = fitz.Pixmap(doc, xref)
    if pix.n > 4:  # CMYK 转换
        pix = fitz.Pixmap(fitz.csRGB, pix)
    pix.save(f"original_{img_index}.png")
```

### 问题：中文 PDF 处理

```python
# PyMuPDF 处理中文
import fitz
doc = fitz.open("chinese.pdf")
for page in doc:
    # 确保使用 UTF-8
    text = page.get_text()
    with open("output.txt", "w", encoding="utf-8") as f:
        f.write(text)

# OCR 中文
import pytesseract
from pdf2image import convert_from_path
images = convert_from_path("chinese.pdf")
for img in images:
    text = pytesseract.image_to_string(img, lang='chi_sim')
    print(text)
```
