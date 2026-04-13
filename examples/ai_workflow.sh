#!/bin/bash
# PDF-Master AI 工作流示例

set -e

SCRIPTS_DIR="../skills/pdf/scripts"

echo "=== PDF-Master AI 工作流示例 ==="
echo ""

# 检查 API Key
if [ -z "$ANTHROPIC_API_KEY" ] && [ -z "$OPENAI_API_KEY" ] && [ -z "$QWEN_API_KEY" ]; then
    echo "警告: 未检测到 AI API Key"
    echo "请设置以下环境变量之一:"
    echo "  export ANTHROPIC_API_KEY='your-key'"
    echo "  export OPENAI_API_KEY='your-key'"
    echo "  export QWEN_API_KEY='your-key'"
    echo ""
    echo "或者使用本地 Ollama:"
    echo "  ollama pull llama3.2"
    echo ""
    exit 1
fi

SAMPLE_PDF="sample.pdf"

if [ ! -f "$SAMPLE_PDF" ]; then
    echo "错误: 请将示例 PDF 文件放在当前目录下"
    exit 1
fi

echo "1. AI 摘要"
echo "----------------------------------------"
if [ -n "$ANTHROPIC_API_KEY" ]; then
    PROVIDER="claude"
elif [ -n "$OPENAI_API_KEY" ]; then
    PROVIDER="openai"
elif [ -n "$QWEN_API_KEY" ]; then
    PROVIDER="qwen"
fi

python "$SCRIPTS_DIR/summarize_pdf.py" "$SAMPLE_PDF" --provider "$PROVIDER" -o summary.txt
echo "摘要已保存: summary.txt"
echo ""

echo "2. AI 问答"
echo "----------------------------------------"
python "$SCRIPTS_DIR/qa_pdf.py" "$SAMPLE_PDF" "这个文档的主要内容是什么？" --provider "$PROVIDER"
echo ""

echo "3. AI 翻译"
echo "----------------------------------------"
python "$SCRIPTS_DIR/translate_pdf.py" "$SAMPLE_PDF" --to en --provider "$PROVIDER" -o translated_en.txt
echo "英文翻译已保存: translated_en.txt"
echo ""

echo "4. 使用 Ollama 本地模型 (可选)"
echo "----------------------------------------"
if command -v ollama &> /dev/null; then
    echo "检测到 Ollama，尝试使用本地模型..."
    python "$SCRIPTS_DIR/summarize_pdf.py" "$SAMPLE_PDF" --provider ollama -o summary_local.txt || echo "Ollama 未配置或模型未下载"
else
    echo "Ollama 未安装，跳过本地模型示例"
fi
echo ""

echo "AI 工作流示例完成！"
