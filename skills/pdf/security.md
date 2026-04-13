# 安全功能

## 功能概览

| 功能 | 命令 | 说明 |
|------|------|------|
| 加密 | `/pdf encrypt` | 设置打开密码和权限密码 |
| 解密 | `/pdf decrypt` | 移除密码保护 |
| 涂抹 | `/pdf redact` | 永久移除敏感信息 |
| 权限 | `/pdf permissions` | 设置打印/复制/编辑权限 |

## 加密 PDF

### 基本用法

```bash
# 设置打开密码
/pdf encrypt document.pdf --password secret

# 设置打开密码和权限密码
/pdf encrypt document.pdf --user-pwd user123 --owner-pwd owner456

# 设置权限
/pdf encrypt document.pdf --password secret --no-print --no-copy
```

### 使用 Python 加密

```python
from pypdf import PdfReader, PdfWriter

def encrypt_pdf(input_path, output_path, user_password, owner_password=None,
                no_print=False, no_copy=False, no_modify=False):
    """加密 PDF 文件"""
    reader = PdfReader(input_path)
    writer = PdfWriter()

    # 复制所有页面
    for page in reader.pages:
        writer.add_page(page)

    # 设置权限
    permissions = 0xFFFFFFFF  # 默认全部权限
    if no_print:
        permissions &= ~0b00000100
    if no_copy:
        permissions &= ~0b00010000
    if no_modify:
        permissions &= ~0b00001000

    # 加密
    writer.encrypt(
        user_password=user_password,
        owner_password=owner_password or user_password,
        permissions=permissions,
        algorithm="AES-256"
    )

    # 保存
    with open(output_path, 'wb') as f:
        writer.write(f)

# 使用
encrypt_pdf(
    "document.pdf",
    "encrypted.pdf",
    user_password="user123",
    owner_password="owner456",
    no_print=True,
    no_copy=True
)
```

### 使用 qpdf 加密

```bash
# 基本加密
qpdf --encrypt userpwd ownerpwd 256 -- input.pdf encrypted.pdf

# 限制权限
# 40-bit: print=n, modify=n, extract=n, annotate=n
qpdf --encrypt userpwd ownerpwd 256 \
     --print=none --modify=none --extract=n \
     -- input.pdf encrypted.pdf
```

## 解密 PDF

### 基本用法

```bash
# 解密需要密码
/pdf decrypt encrypted.pdf --password secret -o decrypted.pdf
```

### 使用 Python 解密

```python
from pypdf import PdfReader, PdfWriter

def decrypt_pdf(input_path, output_path, password):
    """解密 PDF 文件"""
    reader = PdfReader(input_path)

    # 检查是否加密
    if reader.is_encrypted:
        # 尝试解密
        if not reader.decrypt(password):
            raise ValueError("密码错误")

    # 复制到新文件
    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)

    with open(output_path, 'wb') as f:
        writer.write(f)

# 使用
decrypt_pdf("encrypted.pdf", "decrypted.pdf", "secret")
```

### 使用 qpdf 解密

```bash
qpdf --decrypt --password=secret encrypted.pdf decrypted.pdf
```

### 暴力破解（仅用于合法场景）

```python
from pypdf import PdfReader

def crack_pdf_password(pdf_path, wordlist_path):
    """尝试破解 PDF 密码"""
    reader = PdfReader(pdf_path)

    if not reader.is_encrypted:
        return None

    with open(wordlist_path, 'r') as f:
        for line in f:
            password = line.strip()
            if reader.decrypt(password):
                return password

    return None
```

## 敏感信息涂抹

### 基本用法

```bash
# 涂抹特定文本
/pdf redact document.pdf --text "密码"

# 涂抹多个关键词
/pdf redact document.pdf --text "身份证号" --text "手机号"

# 使用正则表达式
/pdf redact document.pdf --regex "\d{17}[\dXx]"  # 身份证号
/pdf redact document.pdf --regex "1[3-9]\d{9}"   # 手机号

# 设置涂抹样式
/pdf redact document.pdf --text "机密" --color black --outline red
```

### 使用 PyMuPDF 涂抹

```python
import fitz

def redact_text(pdf_path, output_path, search_text, fill_color=(0, 0, 0)):
    """涂抹 PDF 中的特定文本"""
    doc = fitz.open(pdf_path)

    for page in doc:
        # 搜索文本
        areas = page.search_for(search_text)

        # 添加涂抹注释
        for area in areas:
            page.add_redact_annot(
                area,
                fill=fill_color
            )

        # 应用涂抹
        page.apply_redactions()

    doc.save(output_path)
    doc.close()

# 使用
redact_text("document.pdf", "redacted.pdf", "机密信息")
redact_text("document.pdf", "redacted.pdf", "密码", fill_color=(1, 0, 0))
```

### 正则表达式涂抹

```python
import fitz
import re

def redact_pattern(pdf_path, output_path, patterns):
    """
    使用正则表达式涂抹敏感信息

    patterns: [(pattern, description), ...]
    """
    doc = fitz.open(pdf_path)

    # 预定义模式
    default_patterns = {
        'phone': r'1[3-9]\d{9}',
        'id_card': r'\d{17}[\dXx]',
        'email': r'[\w\.-]+@[\w\.-]+\.\w+',
        'bank_card': r'\d{16,19}',
        'credit_card': r'\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}'
    }

    for page in doc:
        text = page.get_text()

        for pattern in patterns:
            if pattern in default_patterns:
                regex = default_patterns[pattern]
            else:
                regex = pattern

            # 查找匹配
            for match in re.finditer(regex, text):
                matched_text = match.group()
                areas = page.search_for(matched_text)

                for area in areas:
                    page.add_redact_annot(area, fill=(0, 0, 0))

        page.apply_redactions()

    doc.save(output_path)
    doc.close()

# 使用
redact_pattern("document.pdf", "cleaned.pdf", ['phone', 'id_card', 'email'])
```

### 涂抹特定区域

```python
import fitz

def redact_area(pdf_path, output_path, page_num, rect, fill=(0, 0, 0)):
    """
    涂抹 PDF 的特定区域

    rect: (x0, y0, x1, y1) 坐标
    """
    doc = fitz.open(pdf_path)
    page = doc[page_num]

    # 添加涂抹注释
    page.add_redact_annot(fitz.Rect(rect), fill=fill)

    # 应用涂抹
    page.apply_redactions()

    doc.save(output_path)
    doc.close()

# 使用 - 涂抹第1页的 (100, 100) 到 (300, 200) 区域
redact_area("document.pdf", "redacted.pdf", 0, (100, 100, 300, 200))
```

## 权限设置

### 权限类型

| 权限 | 说明 |
|------|------|
| 打印 | 是否允许打印 |
| 复制 | 是否允许复制文本 |
| 修改 | 是否允许编辑 |
| 注释 | 是否允许添加注释 |
| 表单填写 | 是否允许填写表单 |
| 提取 | 是否允许提取内容 |

### 使用 Python 设置权限

```python
from pypdf import PdfReader, PdfWriter

def set_permissions(input_path, output_path, owner_password,
                    allow_print=True, allow_copy=True,
                    allow_modify=True, allow_annotate=True):
    """设置 PDF 权限"""
    reader = PdfReader(input_path)
    writer = PdfWriter()

    for page in reader.pages:
        writer.add_page(page)

    # 计算权限值
    permissions = 0
    if allow_print:
        permissions |= 0b00000100  # Print
    if allow_modify:
        permissions |= 0b00001000  # Modify
    if allow_copy:
        permissions |= 0b00010000  # Copy
    if allow_annotate:
        permissions |= 0b00100000  # Annotate

    writer.encrypt(
        user_password="",
        owner_password=owner_password,
        permissions=permissions
    )

    with open(output_path, 'wb') as f:
        writer.write(f)

# 使用 - 只允许打印
set_permissions(
    "document.pdf",
    "restricted.pdf",
    owner_password="admin123",
    allow_print=True,
    allow_copy=False,
    allow_modify=False,
    allow_annotate=False
)
```

## 完整示例

### 敏感文档处理流程

```python
import fitz
from pypdf import PdfReader, PdfWriter

def process_sensitive_document(input_path, output_path):
    """处理敏感文档：涂抹 + 加密"""
    # 第一步：涂抹敏感信息
    doc = fitz.open(input_path)

    sensitive_patterns = [
        r'1[3-9]\d{9}',      # 手机号
        r'\d{17}[\dXx]',     # 身份证
        r'[\w\.-]+@[\w\.-]+\.\w+',  # 邮箱
        r'密码[:：]\s*\S+',  # 密码字段
    ]

    import re
    for page in doc:
        text = page.get_text()

        for pattern in sensitive_patterns:
            for match in re.finditer(pattern, text):
                areas = page.search_for(match.group())
                for area in areas:
                    page.add_redact_annot(area, fill=(0, 0, 0))

        page.apply_redactions()

    # 保存临时文件
    temp_path = output_path + ".temp"
    doc.save(temp_path)
    doc.close()

    # 第二步：加密
    reader = PdfReader(temp_path)
    writer = PdfWriter()

    for page in reader.pages:
        writer.add_page(page)

    writer.encrypt(
        user_password="viewer",
        owner_password="admin",
        permissions=0b00000100  # 仅允许打印
    )

    with open(output_path, 'wb') as f:
        writer.write(f)

    # 删除临时文件
    import os
    os.remove(temp_path)

    print(f"处理完成: {output_path}")

# 使用
process_sensitive_document("sensitive.pdf", "processed.pdf")
```

## 注意事项

1. **涂抹是不可逆的** - 涂抹后信息无法恢复，请先备份
2. **加密强度** - 推荐使用 AES-256 加密
3. **密码管理** - 权限密码应妥善保管，丢失后无法恢复权限
4. **合规要求** - 处理敏感信息时请遵守相关法规
