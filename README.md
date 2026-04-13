<p align="center">
  <img src="docs/logo.png" alt="PDF-Master Logo" width="200">
</p>

<h1 align="center">PDF-Master</h1>

<p align="center">
  <strong>🚀 全能型 PDF 处理 Claude Code 插件</strong>
</p>

<p align="center">
  <a href="#-功能特性">功能特性</a> •
  <a href="#-快速开始">快速开始</a> •
  <a href="#-使用指南">使用指南</a> •
  <a href="#-架构设计">架构设计</a> •
  <a href="#-贡献指南">贡献指南</a>
</p>

<p align="center">
  <a href="https://github.com/zshyc/pdf-master/blob/main/LICENSE">
    <img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License">
  </a>
  <a href="https://github.com/zshyc/pdf-master/stargazers">
    <img src="https://img.shields.io/github/stars/zshyc/pdf-master?style=social" alt="GitHub stars">
  </a>
  <a href="https://github.com/zshyc/pdf-master/issues">
    <img src="https://img.shields.io/github/issues/zshyc/pdf-master" alt="GitHub issues">
  </a>
  <a href="https://www.python.org/">
    <img src="https://img.shields.io/badge/python-3.8%2B-blue" alt="Python version">
  </a>
  <a href="https://www.anthropic.com/claude">
    <img src="https://img.shields.io/badge/Claude-Code-purple" alt="Claude Code">
  </a>
</p>

---

## 📖 简介

**PDF-Master** 是一个为 [Claude Code](https://claude.ai/code) 设计的全能型 PDF 处理插件，提供 **20+ 种 PDF 操作能力**，覆盖解析、编辑、转换、AI 增强、OCR、安全等全场景需求。

### ✨ 核心亮点

- 🎯 **一站式解决方案** — 无需组合多个工具，一个插件覆盖所有 PDF 场景
- 🤖 **多 AI 支持** — 支持 Claude、OpenAI、Gemini、DeepSeek、Qwen、智谱、Moonshot、Ollama 八大 AI 平台
- 🔒 **安全优先** — 加密、解密、涂抹、签名，企业级安全能力
- 🌐 **多语言 OCR** — 支持 Tesseract、PaddleOCR，覆盖 100+ 语言
- 📐 **LaTeX 渲染** — 支持 pdflatex、xelatex、lualatex 三大引擎
- 🪶 **轻量设计** — 模块化架构，按需安装依赖

---

## 📊 功能对比

| 功能 | PDF-Master | pypdf | PyMuPDF | pdfplumber |
|------|:----------:|:-----:|:-------:|:----------:|
| 文本提取 | ✅ | ✅ | ✅ | ✅ |
| 表格提取 | ✅ | ❌ | ❌ | ✅ |
| 图片提取 | ✅ | ✅ | ✅ | ❌ |
| PDF 合并/拆分 | ✅ | ✅ | ✅ | ❌ |
| 水印添加 | ✅ | ✅ | ✅ | ❌ |
| 加密/解密 | ✅ | ✅ | ✅ | ❌ |
| OCR 支持 | ✅ | ❌ | ❌ | ❌ |
| AI 摘要/问答 | ✅ | ❌ | ❌ | ❌ |
| AI 翻译 | ✅ | ❌ | ❌ | ❌ |
| 表单填充 | ✅ | ✅ | ❌ | ❌ |
| LaTeX 渲染 | ✅ | ❌ | ❌ | ❌ |
| 多 AI 平台 | ✅ | ❌ | ❌ | ❌ |

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
pip install pypdf pdfplumber PyMuPDF reportlab Pillow

# 安装 AI 功能依赖（可选）
pip install anthropic openai google-generativeai

# 安装 OCR 依赖（可选）
pip install pytesseract pdf2image
# 或使用 PaddleOCR
pip install paddlepaddle paddleocr
```

### 配置 AI 服务（可选）

```bash
# 复制配置模板
cp config/config.yaml.example config/config.yaml

# 设置 API 密钥（选择你使用的 AI 平台）
export ANTHROPIC_API_KEY="your-claude-api-key"
export OPENAI_API_KEY="your-openai-api-key"
export GOOGLE_API_KEY="your-google-api-key"
export DEEPSEEK_API_KEY="your-deepseek-api-key"
export QWEN_API_KEY="your-qwen-api-key"
export ZHIPU_API_KEY="your-zhipu-api-key"
export MOONSHOT_API_KEY="your-moonshot-api-key"
# Ollama 无需 API Key，本地运行即可
```

---

## 📚 使用指南

### 在 Claude Code 中使用

加载插件后，使用 `/pdf` 命令：

```
/pdf extract document.pdf              # 提取文本
/pdf extract-tables report.pdf         # 提取表格
/pdf merge file1.pdf file2.pdf -o merged.pdf
/pdf split document.pdf -p 1-5         # 拆分页面
/pdf summarize document.pdf            # AI 摘要
/pdf translate document.pdf --to en    # AI 翻译
/pdf ocr scanned.pdf                   # OCR 识别
```

### 📤 解析提取

| 功能 | 命令 | 说明 |
|------|------|------|
| 文本提取 | `python scripts/extract_text.py input.pdf output.txt` | 支持布局保留、坐标导出 |
| 表格提取 | `python scripts/extract_tables.py input.pdf output.json` | 支持 JSON/CSV/Excel |
| 图片提取 | `python scripts/extract_images.py input.pdf output_dir/` | 保持原始格式 |
| 元数据提取 | `python scripts/extract_metadata.py input.pdf` | 标题、作者、创建时间等 |

### ✏️ 编辑修改

| 功能 | 命令 | 说明 |
|------|------|------|
| 合并 PDF | `python scripts/merge_pdfs.py file1.pdf file2.pdf -o merged.pdf` | 支持多文件、页面排序 |
| 拆分 PDF | `python scripts/split_pdf.py input.pdf -p 1-5 -o output.pdf` | 支持页面范围 |
| 旋转页面 | `python scripts/rotate_pdf.py input.pdf -d 90 -o output.pdf` | 90/180/270 度 |
| 添加水印 | `python scripts/watermark_pdf.py input.pdf watermark.pdf -o output.pdf` | 支持文字/图片水印 |

### 🔄 格式转换

| 功能 | 命令 | 说明 |
|------|------|------|
| PDF → 图片 | `python scripts/convert_pdf_to_images.py input.pdf output_dir/` | PNG/JPEG，可调分辨率 |
| PDF → Excel | `python scripts/pdf_to_excel.py input.pdf output.xlsx` | 表格数据转换 |
| PDF → Markdown | `python scripts/pdf_to_markdown.py input.pdf output.md` | 保留文档结构 |

### 🤖 AI 增强

| 功能 | 命令 | 说明 |
|------|------|------|
| 智能摘要 | `python scripts/summarize_pdf.py input.pdf --provider claude` | 支持多种 AI 平台 |
| 文档问答 | `python scripts/qa_pdf.py input.pdf --question "主要内容是什么？"` | 基于文档内容回答 |
| AI 翻译 | `python scripts/translate_pdf.py input.pdf --to en --provider openai` | 支持多语言 |

### 🔍 OCR 识别

```bash
# Tesseract OCR
python scripts/ocr_pdf.py scanned.pdf output.txt --engine tesseract --lang chi_sim+eng

# PaddleOCR（中文效果更佳）
python scripts/ocr_pdf.py scanned.pdf output.txt --engine paddleocr
```

### 📐 LaTeX 渲染

```bash
# 使用 pdflatex
python scripts/latex_to_pdf.py document.tex output.pdf --engine pdflatex

# 使用 xelatex（支持中文）
python scripts/latex_to_pdf.py document.tex output.pdf --engine xelatex
```

### 🔐 安全权限

| 功能 | 命令 | 说明 |
|------|------|------|
| 加密 PDF | `python scripts/encrypt_pdf.py input.pdf output.pdf --password secret123` | AES-256 加密 |
| 解密 PDF | `python scripts/decrypt_pdf.py encrypted.pdf output.pdf --password secret123` | 移除密码保护 |
| 敏感信息涂抹 | `python scripts/redact_pdf.py input.pdf output.pdf --keywords "密码,身份证"` | 永久移除敏感内容 |

### 📝 表单处理

```bash
# 检查是否可填写表单
python scripts/check_fillable_fields.py form.pdf

# 提取表单字段信息
python scripts/extract_form_field_info.py form.pdf fields.json

# 填写表单
python scripts/fill_fillable_fields.py form.pdf field_values.json output.pdf
```

---

## 🏗️ 架构设计

```
pdf-master/
├── .claude-plugin/          # Claude Code 插件配置
│   ├── plugin.json          # 插件元数据
│   └── marketplace.json     # 市场配置
├── skills/
│   └── pdf/
│       ├── SKILL.md         # 主技能入口
│       ├── scripts/         # Python 脚本
│       │   ├── ai_provider.py    # AI 平台抽象层
│       │   ├── extract_*.py      # 提取类脚本
│       │   ├── merge_pdfs.py     # 编辑类脚本
│       │   ├── ocr_pdf.py        # OCR 脚本
│       │   └── ...
│       ├── ai.md            # AI 功能文档
│       ├── forms.md         # 表单处理文档
│       ├── latex.md         # LaTeX 文档
│       ├── ocr.md           # OCR 文档
│       ├── reference.md     # 高级参考
│       └── security.md      # 安全功能文档
├── config/
│   └── config.yaml.example  # 配置模板
└── docs/
    └── superpowers/
        ├── specs/           # 设计文档
        └── plans/           # 实现计划
```

### AI Provider 架构

```
┌─────────────────────────────────────────────────────────────┐
│                      AI Provider Layer                      │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐          │
│  │ Claude  │ │ OpenAI  │ │ Gemini  │ │DeepSeek │          │
│  └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘          │
│       │           │           │           │                │
│  ┌────┴────┐ ┌────┴────┐ ┌────┴────┐ ┌────┴────┐          │
│  │  Qwen   │ │ 智谱AI  │ │Moonshot │ │ Ollama  │          │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘          │
│                           │                                 │
│                           ▼                                 │
│              ┌─────────────────────┐                       │
│              │   Unified Interface │                       │
│              │   (ai_provider.py)  │                       │
│              └─────────────────────┘                       │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔧 配置说明

### config.yaml

```yaml
# AI 提供商配置
ai:
  default_provider: claude  # 默认使用的 AI 平台
  providers:
    claude:
      model: claude-sonnet-4-6
      max_tokens: 4096
    openai:
      model: gpt-4o
    gemini:
      model: gemini-1.5-pro

# OCR 配置
ocr:
  default_engine: paddleocr
  languages:
    - chi_sim  # 简体中文
    - eng      # 英文

# LaTeX 配置
latex:
  default_engine: xelatex
  timeout: 60
```

---

## 🤝 贡献指南

我们欢迎所有形式的贡献！

### 如何贡献

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'feat: Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

### 开发设置

```bash
# 克隆你的 fork
git clone https://github.com/your-username/pdf-master.git

# 安装开发依赖
pip install -r requirements-dev.txt

# 运行测试
pytest tests/

# 代码格式化
black skills/pdf/scripts/
isort skills/pdf/scripts/
```

### 代码规范

- 遵循 PEP 8 编码规范
- 使用类型注解
- 编写文档字符串
- 保持函数简洁，单一职责

---

## 📋 Changelog

### v1.0.0 (2026-04-13)

**首次发布**

- ✨ 20+ PDF 处理脚本
- 🤖 支持 8 大 AI 平台
- 🔍 OCR 支持（Tesseract + PaddleOCR）
- 📐 LaTeX 渲染支持
- 🔐 完整安全能力（加密/解密/涂抹）
- 📝 表单处理能力
- 📚 完整文档

---

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。

---

## 🙏 致谢

本项目依赖以下优秀的开源项目：

- [pypdf](https://github.com/py-pdf/pypdf) - PDF 读写
- [PyMuPDF](https://github.com/pymupdf/PyMuPDF) - 高性能 PDF 处理
- [pdfplumber](https://github.com/jsvine/pdfplumber) - 表格提取
- [reportlab](https://www.reportlab.com/) - PDF 生成
- [pdf2image](https://github.com/Belval/pdf2image) - PDF 转图片
- [pytesseract](https://github.com/madmaze/pytesseract) - Tesseract 封装
- [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR) - 中文 OCR

---

## 📮 联系方式

- 作者: zshyc
- Email: 17669757689@163.com
- GitHub: [https://github.com/zshyc/pdf-master](https://github.com/zshyc/pdf-master)

---

<p align="center">
  如果这个项目对你有帮助，请给一个 ⭐ Star 支持一下！
</p>

<p align="center">
  Made with ❤️ by zshyc
</p>
