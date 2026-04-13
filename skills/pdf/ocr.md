# OCR 功能

## 支持的 OCR 引擎

| 引擎 | 语言支持 | 特点 |
|------|----------|------|
| Tesseract | 100+ 语言 | 开源免费，支持中文 |
| PaddleOCR | 80+ 语言 | 中文效果最佳 |
| EasyOCR | 80+ 语言 | 深度学习，多语言 |

## 安装指南

### Tesseract

**Windows:**
```bash
# 使用 Chocolatey
choco install tesseract

# 或下载安装包
# https://github.com/UB-Mannheim/tesseract/wiki

# 安装中文语言包
# 下载 chi_sim.traineddata 到 tessdata 目录
```

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

### Python 库

```bash
pip install pytesseract pdf2image pillow

# PaddleOCR (可选)
pip install paddlepaddle paddleocr

# EasyOCR (可选)
pip install easyocr
```

### poppler (PDF 转图片)

**Windows:**
```bash
# 下载 poppler for Windows
# https://github.com/oschwartz10612/poppler-windows/releases

# 解压后将 bin 目录添加到 PATH
```

**macOS:**
```bash
brew install poppler
```

**Linux:**
```bash
sudo apt-get install poppler-utils
```

## 使用示例

### 基本用法

```bash
# 使用默认引擎 (Tesseract)
/pdf ocr scanned.pdf

# 指定语言
/pdf ocr scanned.pdf --lang chi_sim+eng

# 指定引擎
/pdf ocr scanned.pdf --engine paddleocr

# 输出到文件
/pdf ocr scanned.pdf -o output.txt
```

### Tesseract OCR

```python
import pytesseract
from pdf2image import convert_from_path
from PIL import Image

def ocr_tesseract(pdf_path, lang='chi_sim+eng'):
    """使用 Tesseract 进行 OCR"""
    # 转换 PDF 为图片
    images = convert_from_path(pdf_path, dpi=300)

    results = []
    for i, image in enumerate(images):
        # OCR 识别
        text = pytesseract.image_to_string(image, lang=lang)
        results.append({
            'page': i + 1,
            'text': text
        })

    return results

# 使用
results = ocr_tesseract("scanned.pdf")
for r in results:
    print(f"--- 第 {r['page']} 页 ---")
    print(r['text'])
```

### PaddleOCR

```python
from paddleocr import PaddleOCR
from pdf2image import convert_from_path

def ocr_paddle(pdf_path, lang='ch'):
    """使用 PaddleOCR 进行 OCR"""
    # 初始化 OCR
    ocr = PaddleOCR(use_angle_cls=True, lang=lang, show_log=False)

    # 转换 PDF 为图片
    images = convert_from_path(pdf_path, dpi=200)

    results = []
    for i, image in enumerate(images):
        # OCR 识别
        result = ocr.ocr(image, cls=True)

        # 整理结果
        text_lines = []
        for line in result:
            if line:
                for word_info in line:
                    text_lines.append(word_info[1][0])

        results.append({
            'page': i + 1,
            'text': '\n'.join(text_lines)
        })

    return results

# 使用
results = ocr_paddle("scanned.pdf", lang='ch')
```

### EasyOCR

```python
import easyocr
from pdf2image import convert_from_path

def ocr_easy(pdf_path, languages=['ch_sim', 'en']):
    """使用 EasyOCR 进行 OCR"""
    # 初始化阅读器
    reader = easyocr.Reader(languages)

    # 转换 PDF 为图片
    images = convert_from_path(pdf_path, dpi=200)

    results = []
    for i, image in enumerate(images):
        # OCR 识别
        result = reader.readtext(image)

        # 整理结果
        text_lines = [detection[1] for detection in result]

        results.append({
            'page': i + 1,
            'text': '\n'.join(text_lines)
        })

    return results
```

## 高级用法

### 带位置信息的 OCR

```python
import pytesseract
from pdf2image import convert_from_path

def ocr_with_positions(pdf_path, lang='chi_sim+eng'):
    """获取带位置信息的 OCR 结果"""
    images = convert_from_path(pdf_path, dpi=300)

    all_results = []
    for i, image in enumerate(images):
        # 获取详细数据
        data = pytesseract.image_to_data(
            image,
            lang=lang,
            output_type=pytesseract.Output.DICT
        )

        words = []
        for j in range(len(data['text'])):
            if data['text'][j].strip():
                words.append({
                    'text': data['text'][j],
                    'x': data['left'][j],
                    'y': data['top'][j],
                    'width': data['width'][j],
                    'height': data['height'][j],
                    'confidence': data['conf'][j]
                })

        all_results.append({
            'page': i + 1,
            'words': words
        })

    return all_results
```

### 表格 OCR

```python
import pytesseract
from pdf2image import convert_from_path
import cv2
import numpy as np

def ocr_table(pdf_path, page_num=0):
    """识别 PDF 中的表格"""
    images = convert_from_path(pdf_path, dpi=300)
    image = images[page_num]

    # 转换为 OpenCV 格式
    img = np.array(image)
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

    # 检测表格线
    thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)[1]

    # 水平线
    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1))
    horizontal = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, horizontal_kernel, iterations=2)

    # 垂直线
    vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 40))
    vertical = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, vertical_kernel, iterations=2)

    # 合并线条
    table_mask = cv2.add(horizontal, vertical)

    # 使用 Tesseract 识别表格
    data = pytesseract.image_to_data(
        image,
        lang='chi_sim+eng',
        output_type=pytesseract.Output.DICT
    )

    return data
```

### 图像预处理提高识别率

```python
import cv2
import numpy as np
from pdf2image import convert_from_path
import pytesseract

def preprocess_image(image):
    """图像预处理"""
    # 转换为 numpy 数组
    img = np.array(image)

    # 转换为灰度图
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

    # 去噪
    denoised = cv2.medianBlur(gray, 3)

    # 二值化
    _, binary = cv2.threshold(
        denoised, 0, 255,
        cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )

    # 形态学操作（去除噪点）
    kernel = np.ones((1, 1), np.uint8)
    cleaned = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)

    return cleaned

def ocr_with_preprocessing(pdf_path, lang='chi_sim+eng'):
    """带预处理的 OCR"""
    images = convert_from_path(pdf_path, dpi=300)

    results = []
    for i, image in enumerate(images):
        # 预处理
        processed = preprocess_image(image)

        # OCR
        text = pytesseract.image_to_string(processed, lang=lang)

        results.append({
            'page': i + 1,
            'text': text
        })

    return results
```

### 批量 OCR

```python
import os
from concurrent.futures import ThreadPoolExecutor
from pdf2image import convert_from_path
import pytesseract

def ocr_single_pdf(pdf_path, output_dir, lang='chi_sim+eng'):
    """处理单个 PDF"""
    try:
        images = convert_from_path(pdf_path, dpi=200)
        all_text = []

        for i, image in enumerate(images):
            text = pytesseract.image_to_string(image, lang=lang)
            all_text.append(f"--- 第 {i+1} 页 ---\n{text}")

        # 保存结果
        base_name = os.path.splitext(os.path.basename(pdf_path))[0]
        output_path = os.path.join(output_dir, f"{base_name}.txt")

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n\n'.join(all_text))

        return True
    except Exception as e:
        print(f"处理 {pdf_path} 失败: {e}")
        return False

def batch_ocr(pdf_dir, output_dir, lang='chi_sim+eng', workers=4):
    """批量 OCR 处理"""
    os.makedirs(output_dir, exist_ok=True)

    pdf_files = [
        os.path.join(pdf_dir, f)
        for f in os.listdir(pdf_dir)
        if f.endswith('.pdf')
    ]

    with ThreadPoolExecutor(max_workers=workers) as executor:
        results = list(executor.map(
            lambda p: ocr_single_pdf(p, output_dir, lang),
            pdf_files
        ))

    print(f"处理完成: {sum(results)}/{len(results)} 成功")
```

## 常见问题

### 语言包未找到

```bash
# 检查已安装语言
tesseract --list-langs

# 手动下载语言包
# Windows: 下载到 C:\Program Files\Tesseract-OCR\tessdata\
# Linux: sudo apt-get install tesseract-ocr-chi-sim
```

### 识别效果差

```python
# 1. 提高扫描 DPI
images = convert_from_path(pdf_path, dpi=400)  # 默认 200

# 2. 图像预处理
# 参考上面的 preprocess_image 函数

# 3. 尝试不同引擎
# 中文推荐: PaddleOCR
# 英文推荐: Tesseract
# 多语言: EasyOCR
```

### 内存不足

```python
from pdf2image import convert_from_path

# 分批处理
def ocr_large_pdf(pdf_path, batch_size=10):
    """处理大型 PDF"""
    # 获取页数
    images = convert_from_path(pdf_path, first_page=1, last_page=1)
    total_pages = len(convert_from_path(pdf_path))

    results = []
    for start in range(0, total_pages, batch_size):
        end = min(start + batch_size, total_pages)
        batch = convert_from_path(
            pdf_path,
            first_page=start + 1,
            last_page=end
        )

        for image in batch:
            # 处理图片
            pass
```
