# 表单填写指南

## 检查表单字段

使用 `form-check` 命令查看 PDF 表单中的所有字段：

```bash
/pdf form-check document.pdf
```

输出示例：

```
表单字段列表:
1. name (Text) - 姓名
2. email (Text) - 邮箱
3. phone (Text) - 电话
4. gender (Choice) - 性别 [男, 女]
5. agree (CheckBox) - 同意条款
6. signature (Signature) - 签名
```

### 使用 Python 检查

```python
import fitz  # PyMuPDF

doc = fitz.open("document.pdf")

for page in doc:
    for widget in page.widgets():
        print(f"字段名: {widget.field_name}")
        print(f"类型: {widget.field_type_string}")
        print(f"值: {widget.field_value}")
        print(f"标志: {widget.field_flags}")
        print("---")

doc.close()
```

## 提取表单信息

```python
import fitz

def extract_form_fields(pdf_path):
    """提取所有表单字段信息"""
    doc = fitz.open(pdf_path)
    fields = []

    for page in doc:
        for widget in page.widgets():
            field = {
                "name": widget.field_name,
                "type": widget.field_type_string,
                "value": widget.field_value,
                "rect": widget.rect,
                "page": page.number
            }

            # 获取选项（下拉框/单选按钮）
            if widget.field_type_string in ["Choice", "RadioButton"]:
                field["options"] = widget.choice_values

            fields.append(field)

    doc.close()
    return fields

# 使用
fields = extract_form_fields("form.pdf")
import json
print(json.dumps(fields, indent=2, default=str))
```

## 填充表单

### 基本填充

```bash
/pdf form-fill document.pdf --data fields.json
```

### fields.json 格式

```json
{
  "fields": {
    "name": "张三",
    "email": "zhangsan@example.com",
    "phone": "13800138000",
    "gender": "男",
    "agree": true
  },
  "output": "filled_form.pdf",
  "flatten": false
}
```

### 字段类型映射

| 类型 | JSON 值 | 说明 |
|------|---------|------|
| Text | `"字符串"` | 文本输入 |
| CheckBox | `true` / `false` | 复选框 |
| RadioButton | `"选项值"` | 单选按钮，值为选项之一 |
| Choice | `"选项值"` | 下拉选择 |
| Signature | `"签名路径"` | 签名图片路径 |

### 使用 Python 填充

```python
import fitz

def fill_form(pdf_path, data, output_path, flatten=False):
    """填充 PDF 表单"""
    doc = fitz.open(pdf_path)

    for page in doc:
        for widget in page.widgets():
            field_name = widget.field_name
            if field_name in data:
                value = data[field_name]

                # 根据类型设置值
                if widget.field_type_string == "Text":
                    widget.field_value = str(value)
                elif widget.field_type_string == "CheckBox":
                    widget.field_value = "Yes" if value else "Off"
                elif widget.field_type_string == "Choice":
                    widget.field_value = value
                elif widget.field_type_string == "RadioButton":
                    widget.field_value = value

                widget.update()

    # 扁平化（使表单不可编辑）
    if flatten:
        for page in doc:
            page.clean_contents()

    doc.save(output_path)
    doc.close()

# 使用
data = {
    "name": "张三",
    "email": "zhangsan@example.com",
    "agree": True
}
fill_form("form.pdf", data, "filled_form.pdf")
```

## 高级操作

### 签名字段处理

```python
import fitz

def add_signature(pdf_path, field_name, signature_image, output_path):
    """在签名字段添加签名图片"""
    doc = fitz.open(pdf_path)

    for page in doc:
        for widget in page.widgets():
            if widget.field_name == field_name and \
               widget.field_type_string == "Signature":
                # 获取签名字段位置
                rect = widget.rect

                # 插入签名图片
                page.insert_image(rect, filename=signature_image)

                # 删除签名字段（可选）
                widget.delete()

    doc.save(output_path)
    doc.close()

# 使用
add_signature("contract.pdf", "signature", "sign.png", "signed.pdf")
```

### 下拉框选项处理

```python
import fitz

def get_dropdown_options(pdf_path, field_name):
    """获取下拉框的所有选项"""
    doc = fitz.open(pdf_path)

    for page in doc:
        for widget in page.widgets():
            if widget.field_name == field_name:
                options = widget.choice_values
                doc.close()
                return options

    doc.close()
    return []

# 使用
options = get_dropdown_options("form.pdf", "country")
print(f"可用选项: {options}")
```

### 扁平化表单

扁平化将表单字段转换为普通内容，使其不可编辑：

```python
import fitz

def flatten_form(pdf_path, output_path):
    """扁平化 PDF 表单"""
    doc = fitz.open(pdf_path)

    for page in doc:
        # 获取所有小部件
        widgets = list(page.widgets())

        for widget in widgets:
            # 将字段值渲染到页面
            if widget.field_value:
                # 文本字段
                if widget.field_type_string == "Text":
                    page.insert_text(
                        widget.rect.tl + (2, widget.rect.height - 4),
                        widget.field_value,
                        fontsize=10
                    )
                # 复选框
                elif widget.field_type_string == "CheckBox":
                    if widget.field_value == "Yes":
                        page.insert_text(
                            widget.rect.tl + (2, 10),
                            "X",
                            fontsize=10
                        )

            # 删除字段
            widget.delete()

    doc.save(output_path)
    doc.close()
```

### 验证表单数据

```python
import re

def validate_form_data(data):
    """验证表单数据"""
    errors = []

    # 邮箱验证
    if "email" in data:
        if not re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", data["email"]):
            errors.append("邮箱格式不正确")

    # 电话验证
    if "phone" in data:
        if not re.match(r"^1[3-9]\d{9}$", data["phone"]):
            errors.append("电话格式不正确")

    # 必填字段
    required = ["name", "email"]
    for field in required:
        if field not in data or not data[field]:
            errors.append(f"{field} 为必填字段")

    return errors

# 使用
data = {"name": "张三", "email": "invalid"}
errors = validate_form_data(data)
if errors:
    print(f"验证错误: {errors}")
```

## 完整示例

```bash
# 1. 检查表单字段
/pdf form-check application.pdf

# 2. 创建 fields.json
cat > fields.json << 'EOF'
{
  "fields": {
    "applicant_name": "李四",
    "id_number": "110101199001011234",
    "phone": "13900139000",
    "email": "lisi@example.com",
    "department": "技术部",
    "agree_terms": true
  },
  "output": "application_filled.pdf",
  "flatten": false
}
EOF

# 3. 填充表单
/pdf form-fill application.pdf --data fields.json

# 4. 验证结果
/pdf form-check application_filled.pdf
```
