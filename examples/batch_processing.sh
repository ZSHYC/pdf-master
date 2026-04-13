#!/bin/bash
# PDF-Master 批量处理示例

set -e

SCRIPTS_DIR="../skills/pdf/scripts"
INPUT_DIR="./input_pdfs"
OUTPUT_DIR="./output"

echo "=== PDF-Master 批量处理示例 ==="
echo ""

# 创建目录
mkdir -p "$INPUT_DIR" "$OUTPUT_DIR"

# 检查输入目录
if [ -z "$(ls -A $INPUT_DIR/*.pdf 2>/dev/null)" ]; then
    echo "错误: 请将 PDF 文件放在 $INPUT_DIR 目录下"
    exit 1
fi

echo "批量提取文本"
echo "----------------------------------------"
for pdf in "$INPUT_DIR"/*.pdf; do
    name=$(basename "$pdf" .pdf)
    echo "处理: $name"
    python "$SCRIPTS_DIR/extract_text.py" "$pdf" -f markdown -o "$OUTPUT_DIR/${name}.md"
done
echo ""

echo "批量生成摘要 (需要配置 AI API Key)"
echo "----------------------------------------"
for pdf in "$INPUT_DIR"/*.pdf; do
    name=$(basename "$pdf" .pdf)
    echo "摘要: $name"
    python "$SCRIPTS_DIR/summarize_pdf.py" "$pdf" -o "$OUTPUT_DIR/${name}_summary.txt" 2>/dev/null || echo "跳过 (需要 API Key)"
done
echo ""

echo "合并所有 PDF"
echo "----------------------------------------"
python "$SCRIPTS_DIR/merge_pdfs.py "$INPUT_DIR"/*.pdf -o "$OUTPUT_DIR/merged.pdf" -v
echo ""

echo "批量转换为图片"
echo "----------------------------------------"
for pdf in "$INPUT_DIR"/*.pdf; do
    name=$(basename "$pdf" .pdf)
    echo "转换: $name"
    python "$SCRIPTS_DIR/convert_pdf_to_images.py" "$pdf" -o "$OUTPUT_DIR/images/$name/" --dpi 150
done
echo ""

echo "批量处理完成！"
echo "输出目录: $OUTPUT_DIR"
