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
  <a href="#-ai-provider-配置">AI 配置</a> •
  <a href="#-架构设计">架构设计</a>
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
  <a href="https://github.com/zshyc/pdf-master/actions">
    <img src="https://img.shields.io/github/actions/workflow/status/zshyc/pdf-master/ci.yml?branch=main" alt="CI">
  </a>
</p>

---

## 📖 简介

**PDF-Master** 是一个为 [Claude Code](https://claude.ai/code) 设计的全能型 PDF 处理插件，提供 **28+ 种 PDF 操作能力**，覆盖解析、编辑、转换、AI 增强、OCR、安全等全场景需求。

### ✨ 核心亮点

- 🎯 **一站式解决方案** — 无需组合多个工具，一个插件覆盖所有 PDF 场景
- 🤖 **可配置 AI 支持** — 内置 8 大 AI 平台 + 支持自定义 Provider 配置
- 🔧 **灵活配置系统** — YAML 配置文件 + CLI 工具，轻松管理 AI Provider
- 🔒 **安全优先** — 加密、解密、涂抹、签名，企业级安全能力
- 🌐 **多语言 OCR** — 支持 Tesseract、PaddleOCR，覆盖 100+ 语言
- 📐 **LaTeX 渲染** — 支持 pdflatex、xelatex、lualatex 三大引擎
- 🪶 **轻量设计** — 模块化架构，按需安装依赖
- ✅ **完善测试** — 232 个测试用例，CI/CD 自动化验证

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
| 自定义 AI Provider | ✅ | ❌ | ❌ | ❌ |
| PDF 信息/验证 | ✅ | ❌ | ❌ | ❌ |
| PDF 压缩/修复 | ✅ | ❌ | ❌ | ❌ |
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

# 安装开发依赖（可选，用于开发和测试）
pip install -r requirements-dev.txt
```

### 配置 AI 服务（可选）

```bash
# 复制配置模板
cp config/config.yaml.example config/config.yaml

# 方式一：使用环境变量
export ANTHROPIC_API_KEY="your-claude-api-key"
export OPENAI_API_KEY="your-openai-api-key"

# 方式二：使用配置文件（推荐）
# 编辑 config/providers.yaml 添加你的 API 配置

# 方式三：使用 CLI 工具配置
python skills/pdf/scripts/pdf_config.py add
```

---

## 🤖 AI Provider 配置

PDF-Master 支持灵活的 AI Provider 配置系统，参考 [cc-switch](https://github.com/zshyc/cc-switch) 设计。

### 内置 Provider

| Provider | 类型 | 环境变量 | 默认模型 |
|----------|------|----------|----------|
| Claude | official | `ANTHROPIC_API_KEY` | claude-sonnet-4-6 |
| OpenAI | official | `OPENAI_API_KEY` | gpt-4o |
| Gemini | official | `GOOGLE_API_KEY` | gemini-2.0-flash-exp |
| DeepSeek | official | `DEEPSEEK_API_KEY` | deepseek-chat |
| Qwen | official | `QWEN_API_KEY` | qwen-turbo |
| 智谱 AI | official | `ZHIPU_API_KEY` | glm-4-flash |
| Moonshot | official | `MOONSHOT_API_KEY` | moonshot-v1-8k |
| Ollama | local | 无需 | llama3.2 |

### 添加自定义 Provider

```bash
# 列出所有 provider
python skills/pdf/scripts/pdf_config.py list

# 添加自定义 provider（交互式）
python skills/pdf/scripts/pdf_config.py add

# 或直接编辑 config/providers.yaml
```

### 配置文件示例

```yaml
# config/providers.yaml
providers:
  - id: my-custom-provider
    name: My Custom Provider
    type: openai-compatible
    api_base: https://my-api.example.com/v1
    models:
      - id: my-model
        name: My Model
        max_tokens: 4096
    cost_multiplier: 0.5
    env_key: MY_API_KEY

defaults:
  provider: claude
```

### CLI 配置工具

```bash
pdf-config list              # 列出所有 provider
pdf-config show <id>         # 显示 provider 详情
pdf-config add               # 添加自定义 provider
pdf-config remove <id>       # 删除 provider
pdf-config set-default <id>  # 设置默认 provider
pdf-config test <id>         # 测试 provider 连接
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
/pdf info document.pdf                 # PDF 信息
/pdf validate document.pdf             # 验证 PDF
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

### 🛠️ 工具脚本

| 功能 | 命令 | 说明 |
|------|------|------|
| PDF 信息 | `python scripts/pdf_info.py input.pdf` | 查看 PDF 详细信息 |
| PDF 验证 | `python scripts/pdf_validate.py input.pdf` | 验证 PDF 完整性 |
| PDF 压缩 | `python scripts/pdf_compress.py input.pdf -o output.pdf` | 压缩 PDF 大小 |
| PDF 修复 | `python scripts/pdf_repair.py input.pdf -o output.pdf` | 尝试修复损坏的 PDF |
| PDF 比较 | `python scripts/pdf_compare.py file1.pdf file2.pdf` | 比较两个 PDF 差异 |
| 批量处理 | `python scripts/batch_process.py *.pdf -o output/ --action compress` | 批量处理 PDF |

---

## 🏗️ 架构设计

```
pdf-master/
├── .claude-plugin/          # Claude Code 插件配置
│   ├── plugin.json          # 插件元数据
│   └── marketplace.json     # 市场配置
├── .github/workflows/       # CI/CD 配置
│   ├── ci.yml               # 持续集成
│   └── release.yml          # 自动发布
├── config/
│   ├── config.yaml.example  # 配置模板
│   └── providers.yaml       # AI Provider 配置
├── docs/                    # 文档
│   ├── CONFIGURATION.md     # 配置指南
│   ├── API.md               # API 文档
│   ├── EXAMPLES.md          # 使用示例
│   ├── CONTRIBUTING.md      # 贡献指南
│   └── TROUBLESHOOTING.md   # 故障排除
├── examples/                # 示例脚本
│   ├── basic_usage.sh
│   ├── batch_processing.sh
│   └── ai_workflow.sh
├── skills/
│   └── pdf/
│       ├── SKILL.md         # 主技能入口
│       ├── scripts/         # Python 脚本 (28+)
│       │   ├── ai_provider.py    # AI Provider 抽象层
│       │   ├── provider_manager.py # Provider 配置管理
│       │   ├── pdf_config.py     # 配置 CLI 工具
│       │   ├── extract_*.py      # 提取类脚本
│       │   ├── merge_pdfs.py     # 编辑类脚本
│       │   ├── pdf_info.py       # 工具类脚本
│       │   ├── pdf_validate.py
│       │   ├── pdf_compress.py
│       │   ├── pdf_repair.py
│       │   ├── pdf_compare.py
│       │   ├── batch_process.py
│       │   └── ...
│       └── *.md             # 专项文档
├── tests/                   # 测试 (232 个用例)
├── Makefile                 # 开发命令
├── pyproject.toml           # 项目配置
├── requirements.txt         # 核心依赖
└── requirements-dev.txt     # 开发依赖
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
│       │                                                     │
│       ▼                                                     │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              Provider Manager                        │   │
│  │  • load_providers()  • add_provider()               │   │
│  │  • list_providers()  • remove_provider()            │   │
│  │  • set_default()     • YAML config support          │   │
│  └─────────────────────────────────────────────────────┘   │
│       │                                                     │
│       ▼                                                     │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              AI Provider Interface                   │   │
│  │  • chat()  • complete()  • embed()                   │   │
│  │  • Fallback support  • Cost tracking                 │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔧 开发

### 运行测试

```bash
# 使用 Makefile
make test

# 或直接使用 pytest
pytest tests/ -v --cov=skills/pdf/scripts

# 运行单个测试
pytest tests/test_ai_provider.py -v
```

### 代码质量

```bash
# 格式化代码
make format

# 检查代码质量
make lint

# 运行所有检查
make all
```

### 开发设置

```bash
# 安装开发依赖
pip install -r requirements-dev.txt

# 安装 pre-commit hooks
pre-commit install
```

---

## 📋 Changelog

### v1.1.0 (2026-04-14)

**新增功能**
- ✨ 可配置 AI Provider 系统（参考 cc-switch 设计）
- ✨ Provider Manager + pdf_config CLI 工具
- ✨ 6 个新增工具脚本（info/validate/compress/repair/compare/batch）
- ✨ 完整文档体系（5 个核心文档 + 4 个示例文件）
- ✨ CI/CD 管道（GitHub Actions + Makefile + pre-commit）
- ✨ 12 个新测试文件，232 个测试用例

### v1.0.0 (2026-04-13)

**首次发布**
- ✨ 22 个 PDF 处理脚本
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
- [cc-switch](https://github.com/zshyc/cc-switch) - Provider 配置设计参考

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
