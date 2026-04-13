<div align="center">

# PDF-Master

**🚀 全能型 PDF 处理 Claude Code 插件**

*一个插件，覆盖所有 PDF 场景 — 解析、编辑、转换、AI 增强、OCR、安全*

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/)
[![Claude Code](https://img.shields.io/badge/Claude-Code-purple)](https://claude.ai/code)
[![CI](https://github.com/zshyc/pdf-master/actions/workflows/ci.yml/badge.svg)](https://github.com/zshyc/pdf-master/actions)

[功能特性](#-功能特性) • [快速开始](#-快速开始) • [使用指南](#-使用指南) • [AI 配置](#-ai-provider-配置) • [开发](#-开发)

</div>

---

## 为什么选择 PDF-Master？

> **痛点**：处理 PDF 需要组合多个工具 — pypdf 提取文本、pdfplumber 提取表格、PyMuPDF 合并拆分、还要单独配置 OCR 和 AI...
> 
> **解法**：PDF-Master 一个插件搞定全部，**28+ 种操作**，开箱即用。

### 🎯 核心亮点

| 特性 | 说明 |
|------|------|
| 🧩 **一站式** | 无需组合多个工具，一个插件覆盖所有 PDF 场景 |
| 🤖 **8 大 AI 平台** | Claude / OpenAI / Gemini / DeepSeek / Qwen / 智谱 / Moonshot / Ollama |
| 🔍 **双引擎 OCR** | Tesseract + PaddleOCR，覆盖 100+ 语言 |
| 🔒 **企业级安全** | AES-256 加密、敏感信息涂抹、签名验证 |
| 📐 **LaTeX 渲染** | pdflatex / xelatex / lualatex 三大引擎 |
| ✅ **生产就绪** | 232 测试用例 + CI/CD + 完整文档 |

---

## 📊 功能对比

| 功能 | PDF-Master | pypdf | PyMuPDF | pdfplumber |
|:-----|:----------:|:-----:|:-------:|:----------:|
| 文本提取 | ✅ | ✅ | ✅ | ✅ |
| 表格提取 | ✅ | ❌ | ❌ | ✅ |
| 图片提取 | ✅ | ✅ | ✅ | ❌ |
| 合并/拆分 | ✅ | ✅ | ✅ | ❌ |
| 水印/旋转 | ✅ | ✅ | ✅ | ❌ |
| 加密/解密 | ✅ | ✅ | ✅ | ❌ |
| **OCR 识别** | ✅ | ❌ | ❌ | ❌ |
| **AI 摘要** | ✅ | ❌ | ❌ | ❌ |
| **AI 翻译** | ✅ | ❌ | ❌ | ❌ |
| **AI 问答** | ✅ | ❌ | ❌ | ❌ |
| 表单填充 | ✅ | ✅ | ❌ | ❌ |
| LaTeX 渲染 | ✅ | ❌ | ❌ | ❌ |
| PDF 压缩 | ✅ | ❌ | ✅ | ❌ |
| PDF 修复 | ✅ | ❌ | ✅ | ❌ |
| PDF 比较 | ✅ | ❌ | ❌ | ❌ |
| 批量处理 | ✅ | ❌ | ❌ | ❌ |

---

## 🚀 快速开始

### 前置要求

- Python 3.8+
- Claude Code CLI

### 安装

```bash
# 克隆仓库
git clone https://github.com/zshyc/pdf-master.git
cd pdf-master

# 安装核心依赖
pip install -r requirements.txt
```

### 在 Claude Code 中使用

```bash
# 加载插件后，使用 /pdf 命令
/pdf extract document.pdf              # 提取文本
/pdf merge file1.pdf file2.pdf -o merged.pdf
/pdf summarize document.pdf            # AI 摘要
/pdf ocr scanned.pdf                   # OCR 识别
```

### 配置 AI 服务（可选）

```bash
# 方式一：环境变量
export ANTHROPIC_API_KEY="your-key"

# 方式二：配置文件（推荐）
cp config/config.yaml.example config/config.yaml
# 编辑 config/providers.yaml

# 方式三：CLI 工具
python skills/pdf/scripts/pdf_config.py add
```

---

## 📚 使用指南

### 📤 解析提取

```bash
# 文本提取（支持布局保留）
python scripts/extract_text.py input.pdf -o output.txt

# 表格提取（JSON/CSV/Excel）
python scripts/extract_tables.py input.pdf -o tables.json

# 图片提取
python scripts/extract_images.py input.pdf -o images/

# 元数据提取
python scripts/extract_metadata.py input.pdf
```

### ✏️ 编辑修改

```bash
# 合并 PDF
python scripts/merge_pdfs.py file1.pdf file2.pdf -o merged.pdf

# 拆分 PDF
python scripts/split_pdf.py input.pdf -p 1-5 -o output.pdf

# 旋转页面
python scripts/rotate_pdf.py input.pdf --angle 90 -o output.pdf

# 添加水印
python scripts/watermark_pdf.py input.pdf --image stamp.png -o output.pdf
```

### 🔄 格式转换

```bash
# PDF → 图片
python scripts/convert_pdf_to_images.py input.pdf -o images/

# PDF → Excel
python scripts/pdf_to_excel.py input.pdf -o output.xlsx

# PDF → Markdown
python scripts/pdf_to_markdown.py input.pdf -o output.md
```

### 🤖 AI 增强

```bash
# 智能摘要
python scripts/summarize_pdf.py document.pdf --provider claude

# 文档问答
python scripts/qa_pdf.py document.pdf --question "主要观点是什么？"

# AI 翻译
python scripts/translate_pdf.py document.pdf --to en --provider openai
```

### 🔍 OCR 识别

```bash
# Tesseract OCR
python scripts/ocr_pdf.py scanned.pdf -o output.txt --engine tesseract --lang chi_sim+eng

# PaddleOCR（中文效果更佳）
python scripts/ocr_pdf.py scanned.pdf -o output.txt --engine paddleocr
```

### 🔐 安全权限

```bash
# 加密 PDF（AES-256）
python scripts/encrypt_pdf.py input.pdf -o output.pdf --password secret

# 解密 PDF
python scripts/decrypt_pdf.py encrypted.pdf -o output.pdf --password secret

# 敏感信息涂抹
python scripts/redact_pdf.py input.pdf -o output.pdf --keywords "密码,身份证"
```

### 📝 表单处理

```bash
# 检查表单字段
python scripts/check_fillable_fields.py form.pdf

# 填写表单
python scripts/fill_fillable_fields.py form.pdf --data fields.json -o output.pdf
```

### 🛠️ 工具脚本

```bash
python scripts/pdf_info.py input.pdf        # PDF 信息
python scripts/pdf_validate.py input.pdf    # 验证完整性
python scripts/pdf_compress.py input.pdf    # 压缩文件
python scripts/pdf_repair.py input.pdf      # 修复损坏
python scripts/pdf_compare.py a.pdf b.pdf   # 比较差异
python scripts/batch_process.py *.pdf       # 批量处理
```

---

## 🤖 AI Provider 配置

### 内置 Provider

| Provider | 环境变量 | 默认模型 |
|----------|----------|----------|
| Claude | `ANTHROPIC_API_KEY` | claude-sonnet-4-6 |
| OpenAI | `OPENAI_API_KEY` | gpt-4o |
| Gemini | `GOOGLE_API_KEY` | gemini-2.0-flash-exp |
| DeepSeek | `DEEPSEEK_API_KEY` | deepseek-chat |
| Qwen | `QWEN_API_KEY` | qwen-turbo |
| 智谱 AI | `ZHIPU_API_KEY` | glm-4-flash |
| Moonshot | `MOONSHOT_API_KEY` | moonshot-v1-8k |
| Ollama | 无需 | llama3.2 |

### 添加自定义 Provider

```yaml
# config/providers.yaml
providers:
  - id: my-provider
    name: My Custom Provider
    type: openai-compatible
    api_base: https://my-api.example.com/v1
    models:
      - id: my-model
        name: My Model
        max_tokens: 4096
    env_key: MY_API_KEY
```

### CLI 配置工具

```bash
pdf-config list              # 列出所有 provider
pdf-config show <id>         # 显示详情
pdf-config add               # 添加 provider
pdf-config remove <id>       # 删除 provider
pdf-config set-default <id>  # 设置默认
pdf-config test <id>         # 测试连接
```

---

## 🏗️ 项目结构

```
pdf-master/
├── .claude-plugin/          # 插件配置
│   ├── plugin.json          # 插件元数据
│   └── marketplace.json     # 市场配置
├── skills/pdf/              # 核心技能
│   ├── SKILL.md             # 技能入口
│   ├── scripts/             # Python 脚本 (34 个)
│   └── *.md                 # 专项文档
├── agents/                  # 子代理定义
│   ├── pdf-explorer.md      # 结构探索
│   ├── pdf-analyzer.md      # 内容分析
│   └── pdf-converter.md     # 格式转换
├── hooks/                   # 生命周期钩子
├── tests/                   # 测试 (232 用例)
├── docs/                    # 文档
├── config/                  # 配置模板
└── examples/                # 示例脚本
```

---

## 🔧 开发

### 运行测试

```bash
# 使用 Makefile
make test

# 或 pytest
pytest tests/ -v --cov=skills/pdf/scripts
```

### 代码质量

```bash
make format    # 格式化
make lint      # 检查
make all       # 全部检查
```

### 开发设置

```bash
pip install -r requirements-dev.txt
pre-commit install
```

---

## 📋 Changelog

### v1.1.0 (2026-04-14)

- ✨ 可配置 AI Provider 系统
- ✨ 6 个新增工具脚本（info/validate/compress/repair/compare/batch）
- 📚 完整文档体系（5 个核心文档 + 4 个示例文件）
- ✅ CI/CD 管道（GitHub Actions + Makefile + pre-commit）
- ✅ 12 个新测试文件，232 个测试用例

### v1.0.0 (2026-04-13)

- ✨ 22 个 PDF 处理脚本
- 🤖 支持 8 大 AI 平台
- 🔍 OCR 支持（Tesseract + PaddleOCR）
- 📐 LaTeX 渲染支持
- 🔐 完整安全能力

详见 [CHANGELOG.md](CHANGELOG.md)

---

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE)

---

## 🙏 致谢

- [pypdf](https://github.com/py-pdf/pypdf) - PDF 读写
- [PyMuPDF](https://github.com/pymupdf/PyMuPDF) - 高性能处理
- [pdfplumber](https://github.com/jsvine/pdfplumber) - 表格提取
- [reportlab](https://www.reportlab.com/) - PDF 生成
- [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR) - 中文 OCR
- [cc-switch](https://github.com/zshyc/cc-switch) - Provider 配置参考

---

## 📮 联系方式

- 作者: zshyc
- Email: 17669757689@163.com
- GitHub: [https://github.com/zshyc/pdf-master](https://github.com/zshyc/pdf-master)

---

<div align="center">

如果这个项目对你有帮助，请给一个 ⭐ Star 支持一下！

Made with ❤️ by zshyc

</div>
