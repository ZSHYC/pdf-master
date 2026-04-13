# 故障排除

本文档包含 PDF-Master 的常见问题解答和故障排除指南。

## 目录

- [常见问题 FAQ](#常见问题-faq)
- [错误信息解读](#错误信息解读)
- [依赖问题解决](#依赖问题解决)
- [性能优化建议](#性能优化建议)

---

## 常见问题 FAQ

### Q: 安装依赖后仍然提示模块找不到？

**原因**: Python 环境未正确激活或使用了错误的 Python 版本。

**解决方案**:

```bash
# 检查当前 Python 版本
python --version

# 检查已安装的包
pip list | grep pypdf

# 确保在正确的虚拟环境中
which python  # Linux/macOS
where python  # Windows
```

### Q: AI 功能提示 "Missing API key"？

**原因**: 未设置 AI 提供商的 API Key 环境变量。

**解决方案**:

```bash
# 设置环境变量
export ANTHROPIC_API_KEY="your-api-key"

# 或在 ~/.bashrc 中永久设置
echo 'export ANTHROPIC_API_KEY="your-api-key"' >> ~/.bashrc
source ~/.bashrc
```

### Q: OCR 识别结果乱码？

**原因**: 未安装正确的语言包或语言设置不匹配。

**解决方案**:

```bash
# 检查已安装语言
tesseract --list-langs

# 安装中文语言包 (Linux)
sudo apt-get install tesseract-ocr-chi-sim

# 指定正确的语言
python ocr_pdf.py scanned.pdf -l chi_sim+eng
```

### Q: PDF 无法打开或提示损坏？

**原因**: PDF 文件可能损坏或加密。

**解决方案**:

```bash
# 尝试修复 PDF
qpdf --qdf damaged.pdf repaired.pdf

# 或使用 Ghostscript
gs -o repaired.pdf -sDEVICE=pdfwrite -dPDFSETTINGS=/prepress damaged.pdf
```

### Q: 提取的表格数据不完整？

**原因**: 表格边框不明显或 PDF 布局复杂。

**解决方案**:

```python
# 尝试调整 pdfplumber 设置
import pdfplumber

with pdfplumber.open("document.pdf") as pdf:
    page = pdf.pages[0]
    tables = page.extract_tables({
        "vertical_strategy": "text",
        "horizontal_strategy": "text"
    })
```

### Q: 大文件处理内存不足？

**原因**: 一次性加载整个文件到内存。

**解决方案**:

```python
# 分页处理
from pdf2image import convert_from_path

# 指定页面范围
images = convert_from_path(
    "large.pdf",
    first_page=1,
    last_page=10
)
```

### Q: Ollama 连接失败？

**原因**: Ollama 服务未运行或端口不正确。

**解决方案**:

```bash
# 检查 Ollama 服务状态
curl http://localhost:11434/api/tags

# 启动 Ollama 服务
ollama serve

# 检查模型是否下载
ollama list

# 下载模型
ollama pull llama3.2
```

---

## 错误信息解读

### File Not Found

```
Error: File not found: document.pdf
```

**含义**: 指定的文件不存在。

**排查步骤**:
1. 检查文件路径是否正确
2. 检查文件扩展名
3. 检查当前工作目录

### Not a PDF File

```
Error: Not a PDF file: document.txt
```

**含义**: 文件不是 PDF 格式。

**排查步骤**:
1. 检查文件扩展名
2. 使用 `file` 命令检查文件类型

### Missing Dependencies

```
Error: Missing required dependencies: pypdf, pdfplumber
```

**含义**: 缺少必要的 Python 库。

**解决方案**:

```bash
pip install pypdf pdfplumber
```

### Password Required

```
Error: PDF is encrypted. Please provide password.
```

**含义**: PDF 文件有密码保护。

**解决方案**:

```bash
python decrypt_pdf.py encrypted.pdf -o decrypted.pdf -p your_password
```

### OCR Failed

```
Error: OCR failed: Tesseract not installed
```

**含义**: OCR 引擎未正确安装。

**解决方案**:

```bash
# macOS
brew install tesseract

# Linux
sudo apt-get install tesseract-ocr

# Windows
choco install tesseract
```

### API Error

```
Error: API call failed: Rate limit exceeded
```

**含义**: API 调用频率超限。

**解决方案**:
1. 等待一段时间后重试
2. 使用指数退避重试
3. 升级 API 套餐

---

## 依赖问题解决

### pypdf 安装问题

```bash
# 升级 pip
pip install --upgrade pip

# 清除缓存重新安装
pip cache purge
pip install pypdf --no-cache-dir
```

### pdfplumber 安装问题

```bash
# 可能缺少系统依赖
# macOS
brew install cairo pango gdk-pixbuf

# Linux
sudo apt-get install libcairo2-dev
```

### pdf2image 安装问题

```bash
# 需要安装 poppler
# macOS
brew install poppler

# Linux
sudo apt-get install poppler-utils

# Windows
# 下载 poppler-windows 并添加到 PATH
```

### Tesseract 安装问题

**macOS:**

```bash
brew install tesseract
brew install tesseract-lang  # 所有语言包
```

**Linux:**

```bash
sudo apt-get install tesseract-ocr
sudo apt-get install tesseract-ocr-chi-sim  # 中文
```

**Windows:**

1. 下载安装包: https://github.com/UB-Mannheim/tesseract/wiki
2. 添加到 PATH
3. 设置 `TESSDATA_PREFIX` 环境变量

---

## 性能优化建议

### 大文件处理

1. **分页处理**: 不要一次性加载整个文件

```python
# 分批处理
for i in range(0, total_pages, batch_size):
    batch = convert_from_path(pdf_path, first_page=i+1, last_page=min(i+batch_size, total_pages))
    # 处理 batch
```

2. **降低分辨率**: OCR 和图片转换可降低 DPI

```bash
python ocr_pdf.py large.pdf --dpi 150  # 默认 300
```

3. **并行处理**: 利用多核 CPU

```python
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=4) as executor:
    executor.map(process_pdf, pdf_files)
```

### 内存优化

1. **及时释放资源**: 使用 `with` 语句

```python
with pdfplumber.open("document.pdf") as pdf:
    # 处理 pdf
# 自动关闭
```

2. **流式处理**: 避免存储所有中间结果

```python
# 边读边写，不存储在内存
with open(output_file, 'w') as f:
    for page in pdf.pages:
        f.write(page.extract_text())
```

### 网络优化 (AI 功能)

1. **使用缓存**: 避免重复调用

```python
import hashlib
import json

def get_cache_key(pdf_path):
    with open(pdf_path, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()
```

2. **批量请求**: 合并多个小请求

3. **使用本地模型**: Ollama 无网络延迟

```bash
python summarize_pdf.py document.pdf --provider ollama
```

---

## 调试技巧

### 启用详细输出

```bash
# 使用 -v 或 --verbose 参数
python merge_pdfs.py file1.pdf file2.pdf -o merged.pdf -v
```

### 日志记录

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

logger.debug("Debug message")
logger.info("Info message")
logger.error("Error message")
```

### 检查中间结果

```python
# 打印中间状态
print(f"Pages: {len(pdf.pages)}")
print(f"Text length: {len(text)}")
```

---

## 获取帮助

如果以上方法无法解决您的问题：

1. 查看 [GitHub Issues](https://github.com/zshyc/pdf-master/issues)
2. 创建新 Issue，包含：
   - 完整的错误信息
   - 复现步骤
   - 环境信息（Python 版本、操作系统）
   - 相关日志

3. 联系维护者: 17669757689@163.com
