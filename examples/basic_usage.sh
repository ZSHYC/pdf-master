#!/bin/bash
# PDF-Master 基础使用示例

set -e  # 遇到错误时退出

SCRIPTS_DIR="../skills/pdf/scripts"

echo "=== PDF-Master 基础使用示例 ==="
echo ""

# 示例文件
SAMPLE_PDF="sample.pdf"

if [ ! -f "$SAMPLE_PDF" ]; then
    echo "错误: 请将示例 PDF 文件放在当前目录下"
    exit 1
fi

echo "1. 提取文本"
echo "----------------------------------------"
python "$SCRIPTS_DIR/extract_text.py" "$SAMPLE_PDF" -o output.txt
echo "输出: output.txt"
echo ""

echo "2. 提取表格"
echo "----------------------------------------"
python "$SCRIPTS_DIR/extract_tables.py" "$SAMPLE_PDF" -f excel -o tables.xlsx
echo "输出: tables.xlsx"
echo ""

echo "3. 查看元数据"
echo "----------------------------------------"
python "$SCRIPTS_DIR/extract_metadata.py" "$SAMPLE_PDF"
echo ""

echo "4. 提取图片"
echo "----------------------------------------"
python "$SCRIPTS_DIR/extract_images.py" "$SAMPLE_PDF" -o ./extracted_images/
echo ""

echo "5. 转换为图片"
echo "----------------------------------------"
python "$SCRIPTS_DIR/convert_pdf_to_images.py" "$SAMPLE_PDF" --dpi 150 -o ./pdf_images/
echo ""

echo "基础使用示例完成！"
