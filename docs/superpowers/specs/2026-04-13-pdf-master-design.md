# PDF-Master 插件设计文档

## 一、项目概述

| 项目 | 说明 |
|------|------|
| **名称** | pdf-master |
| **定位** | 全能型 PDF 处理 Claude Code 插件，覆盖所有主流 PDF 功能 |
| **架构** | Claude Skill + MCP Server（可选） |
| **技术栈** | Python (后端库) + Markdown (Skill) |
| **版本** | 1.0.0 完整版本 |
| **作者** | zshyc (17669757689@163.com) |
| **仓库** | https://github.com/zshyc/pdf-master |

### 核心价值

- **最全面**：覆盖解析提取、编辑转换、AI 增强、OCR、LaTeX 排版、安全权限等所有主流 PDF 功能
- **最方便**：自然语言接口，用户说一句话完成复杂操作
- **质量保证**：基于成熟库实现，不会产生幻觉
- **效果最好**：专业库 + AI 理解，两者结合

---

## 二、架构设计

### 2.1 整体架构

```
┌─────────────────────────────────────────────────────────────────────┐
│                          用户层                                      │
│  "帮我提取这个 PDF 的表格并转成 Excel"                               │
└─────────────────────────────────┬───────────────────────────────────┘
                                  │
┌─────────────────────────────────▼───────────────────────────────────┐
│                    Claude Code Skill 层                              │
│  skills/pdf/SKILL.md (自然语言理解 → 工具调用编排)                   │
├─────────────────────────────────────────────────────────────────────┤
│  📖 解析模块  │  ✏️ 编辑模块  │  🔄 转换模块  │  🤖 AI 模块          │
│  🔍 OCR 模块  │  📐 LaTeX 模块  │  🔒 安全模块                       │
└─────────────────────────────────┬───────────────────────────────────┘
                                  │ MCP Protocol (可选)
┌─────────────────────────────────▼───────────────────────────────────┐
│                        MCP Server 层 (可选)                          │
│  mcp-server/src/pdf_master/                                        │
│  ├── core/          # 核心引擎                                      │
│  ├── parsers/       # 解析模块                                      │
│  ├── editors/       # 编辑模块                                      │
│  ├── converters/    # 转换模块                                      │
│  ├── ai/            # AI 增强模块                                   │
│  ├── ocr/           # OCR 模块                                      │
│  ├── latex/         # LaTeX 模块                                    │
│  └── security/      # 安全模块                                      │
└─────────────────────────────────┬───────────────────────────────────┘
                                  │
┌─────────────────────────────────▼───────────────────────────────────┐
│                        依赖库层                                      │
│  PyMuPDF │ pdfplumber │ Tesseract │ PaddleOCR │ Transformers        │
│  pypdf │ reportlab │ camelot │ tabula-py │ pdf2image                │
└─────────────────────────────────────────────────────────────────────┘
```

### 2.2 文件结构

```
pdf-master/
├── .claude-plugin/
│   ├── plugin.json              # 插件元数据
│   └── marketplace.json         # Marketplace 配置
├── .mcp.json                    # MCP Server 配置（可选）
├── README.md                    # 用户文档
├── LICENSE                      # 许可证
├── skills/
│   └── pdf/
│       ├── SKILL.md             # 主 skill 文件
│       ├── reference.md         # 高级参考文档
│       ├── forms.md             # 表单填写指南
│       ├── ai.md                # AI 增强功能
│       ├── ocr.md               # OCR 功能
│       ├── latex.md             # LaTeX 排版
│       ├── security.md          # 安全功能
│       └── scripts/             # Python 脚本
│           ├── check_fillable_fields.py
│           ├── extract_form_field_info.py
│           ├── fill_fillable_fields.py
│           ├── convert_pdf_to_images.py
│           ├── ocr_pdf.py
│           ├── summarize_pdf.py
│           ├── translate_pdf.py
│           ├── extract_tables.py
│           ├── merge_pdfs.py
│           ├── split_pdf.py
│           ├── rotate_pdf.py
│           ├── watermark_pdf.py
│           ├── encrypt_pdf.py
│           ├── decrypt_pdf.py
│           ├── sign_pdf.py
│           ├── redact_pdf.py
│           ├── latex_to_pdf.py
│           └── pdf_to_latex.py
├── mcp-server/                  # MCP Server 实现（可选）
│   ├── pyproject.toml
│   └── src/
│       └── pdf_master/
│           ├── __init__.py
│           ├── server.py
│           ├── core/
│           │   ├── __init__.py
│           │   ├── engine.py
│           │   ├── config.py
│           │   └── errors.py
│           ├── parsers/
│           │   ├── __init__.py
│           │   ├── text.py
│           │   ├── tables.py
│           │   ├── images.py
│           │   └── metadata.py
│           ├── editors/
│           │   ├── __init__.py
│           │   ├── merge.py
│           │   ├── split.py
│           │   ├── rotate.py
│           │   └── watermark.py
│           ├── converters/
│           │   ├── __init__.py
│           │   ├── to_word.py
│           │   ├── to_excel.py
│           │   ├── to_markdown.py
│           │   └── to_image.py
│           ├── ai/
│           │   ├── __init__.py
│           │   ├── summarizer.py
│           │   ├── qa.py
│           │   ├── translator.py
│           │   └── providers/
│           ├── ocr/
│           │   ├── __init__.py
│           │   ├── tesseract.py
│           │   ├── paddleocr.py
│           │   └── cloud_ocr.py
│           ├── latex/
│           │   ├── __init__.py
│           │   ├── compiler.py
│           │   └── templates/
│           └── security/
│               ├── __init__.py
│               ├── encrypt.py
│               ├── sign.py
│               └── redact.py
└── config/
    └── config.yaml.example
```

---

## 三、功能模块设计

### 3.1 解析提取模块

| 功能 | 工具/脚本 | 输出格式 | 依赖库 |
|------|-----------|----------|--------|
| 文本提取 | `extract_text()` | txt/md/json | pypdf, pdfplumber |
| 表格识别 | `extract_tables.py` | csv/xlsx/json | pdfplumber, camelot, tabula-py |
| 图片提取 | `extract_images()` | png/jpg/tiff | pypdf, pdfimages |
| 元数据读取 | `extract_metadata()` | json | pypdf |
| 目录提取 | `extract_toc()` | json/md | pypdf |
| 链接提取 | `extract_links()` | json | pypdf |
| 表单数据 | `extract_form_field_info.py` | json | pypdf |
| 注释提取 | `extract_annotations()` | json | pypdf |
| 嵌入文件 | `extract_embedded()` | 原始文件 | pypdf |

### 3.2 编辑修改模块

| 功能 | 工具/脚本 | 说明 | 依赖库 |
|------|-----------|------|--------|
| 合并 | `merge_pdfs.py` | 多 PDF 合并 | pypdf, qpdf |
| 拆分 | `split_pdf.py` | 按页/范围拆分 | pypdf, qpdf |
| 旋转 | `rotate_pdf.py` | 旋转页面 | pypdf |
| 裁剪 | `crop_pdf()` | 裁剪页面 | pypdf |
| 缩放 | `scale_pdf()` | 调整页面大小 | pypdf |
| 重排 | `reorder_pdf()` | 调整页面顺序 | pypdf |
| 水印 | `watermark_pdf.py` | 添加水印 | pypdf |
| 页眉页脚 | `add_header_footer()` | 添加页眉页脚 | reportlab |
| 页码 | `add_page_numbers()` | 添加页码 | reportlab |
| 文字编辑 | `edit_text()` | 修改文字 | pypdf |
| 图片插入 | `insert_image()` | 插入图片 | pypdf, reportlab |
| 注释 | `add_annotation()` | 添加注释 | pypdf |
| 表单填充 | `fill_fillable_fields.py` | 填充表单 | pypdf, pdf-lib |

### 3.3 格式转换模块

| 源格式 | 目标格式 | 工具/脚本 | 依赖库 |
|--------|----------|-----------|--------|
| PDF | Word | `pdf_to_word.py` | pdf2docx, python-docx |
| PDF | Excel | `pdf_to_excel.py` | pdfplumber, pandas, openpyxl |
| PDF | PPT | `pdf_to_ppt.py` | python-pptx |
| PDF | HTML | `pdf_to_html()` | pdf2htmlEX |
| PDF | Markdown | `pdf_to_markdown.py` | marker, pdfplumber |
| PDF | 图片 | `convert_pdf_to_images.py` | pdf2image, pypdfium2 |
| PDF | EPUB | `pdf_to_epub()` | ebooklib |
| PDF | LaTeX | `pdf_to_latex.py` | mathpix (API) |
| Word | PDF | `word_to_pdf()` | python-docx, libreoffice |
| Excel | PDF | `excel_to_pdf()` | openpyxl, libreoffice |
| 图片 | PDF | `image_to_pdf()` | Pillow, img2pdf |
| 网页 | PDF | `url_to_pdf()` | wkhtmltopdf, playwright |

### 3.4 AI 增强模块

| 功能 | 工具/脚本 | 支持模型 | 依赖库 |
|------|-----------|----------|--------|
| 智能摘要 | `summarize_pdf.py` | Claude/GPT/Gemini/国产模型 | anthropic, openai, transformers |
| 文档问答 | `qa_pdf.py` | 同上 | 同上 + langchain |
| 智能翻译 | `translate_pdf.py` | 同上 | 同上 |
| 布局分析 | `analyze_layout()` | AI 模型 | layout-parser |
| 信息抽取 | `extract_info()` | AI 模型 | spacy, transformers |
| 对比分析 | `compare_pdfs()` | AI 模型 | difflib, anthropic |

#### 3.4.1 AI 模型调用实现

**支持的 AI 提供商：**

| 提供商 | API Key 环境变量 | 默认模型 | 调用方式 |
|--------|------------------|----------|----------|
| Claude | `ANTHROPIC_API_KEY` | claude-sonnet-4-6 | anthropic SDK |
| OpenAI | `OPENAI_API_KEY` | gpt-4 | openai SDK |
| Gemini | `GOOGLE_API_KEY` | gemini-pro | google-generativeai |
| DeepSeek | `DEEPSEEK_API_KEY` | deepseek-chat | openai 兼容 |
| 通义千问 | `QWEN_API_KEY` | qwen-max | openai 兼容 |
| 智谱 GLM | `ZHIPU_API_KEY` | glm-4 | zhipuai SDK |
| Moonshot | `MOONSHOT_API_KEY` | moonshot-v1-8k | openai 兼容 |
| Ollama | 无需 | llama3 | 本地 HTTP |

**AI 调用核心代码示例：**

```python
# skills/pdf/scripts/ai_provider.py

import os
from typing import Optional, Dict, Any
from dataclasses import dataclass

@dataclass
class AIConfig:
    provider: str
    api_key: Optional[str] = None
    model: str = ""
    base_url: Optional[str] = None

class AIProvider:
    """统一的 AI 提供商接口"""
    
    PROVIDERS = {
        "claude": {
            "env_key": "ANTHROPIC_API_KEY",
            "default_model": "claude-sonnet-4-6",
            "sdk": "anthropic"
        },
        "openai": {
            "env_key": "OPENAI_API_KEY",
            "default_model": "gpt-4",
            "sdk": "openai"
        },
        "gemini": {
            "env_key": "GOOGLE_API_KEY",
            "default_model": "gemini-pro",
            "sdk": "google.generativeai"
        },
        "deepseek": {
            "env_key": "DEEPSEEK_API_KEY",
            "default_model": "deepseek-chat",
            "base_url": "https://api.deepseek.com/v1",
            "sdk": "openai"  # OpenAI 兼容
        },
        "qwen": {
            "env_key": "QWEN_API_KEY",
            "default_model": "qwen-max",
            "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
            "sdk": "openai"  # OpenAI 兼容
        },
        "zhipu": {
            "env_key": "ZHIPU_API_KEY",
            "default_model": "glm-4",
            "sdk": "zhipuai"
        },
        "moonshot": {
            "env_key": "MOONSHOT_API_KEY",
            "default_model": "moonshot-v1-8k",
            "base_url": "https://api.moonshot.cn/v1",
            "sdk": "openai"  # OpenAI 兼容
        },
        "ollama": {
            "env_key": None,
            "default_model": "llama3",
            "base_url": "http://localhost:11434",
            "sdk": "ollama"
        }
    }
    
    def __init__(self, provider: str = "claude", model: Optional[str] = None):
        self.provider = provider
        self.config = self.PROVIDERS.get(provider)
        if not self.config:
            raise ValueError(f"Unknown provider: {provider}")
        
        # 获取 API Key
        self.api_key = None
        if self.config["env_key"]:
            self.api_key = os.environ.get(self.config["env_key"])
            if not self.api_key:
                raise ValueError(f"Missing API key: {self.config['env_key']}")
        
        # 设置模型
        self.model = model or self.config["default_model"]
        
        # 初始化客户端
        self._init_client()
    
    def _init_client(self):
        """初始化 AI 客户端"""
        sdk = self.config["sdk"]
        
        if sdk == "anthropic":
            import anthropic
            self.client = anthropic.Anthropic(api_key=self.api_key)
        
        elif sdk == "openai":
            import openai
            self.client = openai.OpenAI(
                api_key=self.api_key,
                base_url=self.config.get("base_url")
            )
        
        elif sdk == "google.generativeai":
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            self.client = genai.GenerativeModel(self.model)
        
        elif sdk == "zhipuai":
            from zhipuai import ZhipuAI
            self.client = ZhipuAI(api_key=self.api_key)
        
        elif sdk == "ollama":
            import ollama
            self.client = ollama
    
    def chat(self, messages: list, **kwargs) -> str:
        """统一的聊天接口"""
        sdk = self.config["sdk"]
        
        if sdk == "anthropic":
            # Claude 格式
            response = self.client.messages.create(
                model=self.model,
                max_tokens=kwargs.get("max_tokens", 4096),
                messages=messages
            )
            return response.content[0].text
        
        elif sdk == "openai":
            # OpenAI 兼容格式
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                **kwargs
            )
            return response.choices[0].message.content
        
        elif sdk == "google.generativeai":
            # Gemini 格式
            prompt = "\n".join([m["content"] for m in messages])
            response = self.client.generate_content(prompt)
            return response.text
        
        elif sdk == "zhipuai":
            # 智谱格式
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages
            )
            return response.choices[0].message.content
        
        elif sdk == "ollama":
            # Ollama 格式
            response = self.client.chat(
                model=self.model,
                messages=messages
            )
            return response["message"]["content"]
    
    def summarize(self, text: str, language: str = "zh") -> str:
        """生成摘要"""
        if language == "zh":
            prompt = f"请对以下内容生成简洁的中文摘要，突出关键要点：\n\n{text}"
        else:
            prompt = f"Please summarize the following content concisely:\n\n{text}"
        
        return self.chat([{"role": "user", "content": prompt}])
    
    def qa(self, question: str, context: str) -> str:
        """基于上下文回答问题"""
        prompt = f"""基于以下内容回答问题。如果内容中没有相关信息，请说明。

内容：
{context}

问题：{question}

回答："""
        return self.chat([{"role": "user", "content": prompt}])
    
    def translate(self, text: str, target_language: str = "en") -> str:
        """翻译文本"""
        prompt = f"请将以下内容翻译成{target_language}：\n\n{text}"
        return self.chat([{"role": "user", "content": prompt}])
```

**使用示例：**

```python
# 智能摘要
from ai_provider import AIProvider

# 使用 Claude
ai = AIProvider("claude")
summary = ai.summarize(pdf_text)

# 使用 OpenAI
ai = AIProvider("openai", model="gpt-4-turbo")
summary = ai.summarize(pdf_text)

# 使用国产模型（通义千问）
ai = AIProvider("qwen")
summary = ai.summarize(pdf_text)

# 使用本地模型（Ollama）
ai = AIProvider("ollama", model="llama3")
summary = ai.summarize(pdf_text)

# 文档问答
answer = ai.qa("这个文档的主要观点是什么？", pdf_text)

# 翻译
translated = ai.translate(pdf_text, target_language="en")
```

**配置文件示例（~/.pdf-master/config.yaml）：**

```yaml
ai:
  default_provider: claude
  
  providers:
    claude:
      api_key: ${ANTHROPIC_API_KEY}
      model: claude-sonnet-4-6
    
    openai:
      api_key: ${OPENAI_API_KEY}
      model: gpt-4
    
    gemini:
      api_key: ${GOOGLE_API_KEY}
      model: gemini-pro
    
    deepseek:
      api_key: ${DEEPSEEK_API_KEY}
      model: deepseek-chat
      base_url: https://api.deepseek.com/v1
    
    qwen:
      api_key: ${QWEN_API_KEY}
      model: qwen-max
      base_url: https://dashscope.aliyuncs.com/compatible-mode/v1
    
    zhipu:
      api_key: ${ZHIPU_API_KEY}
      model: glm-4
    
    moonshot:
      api_key: ${MOONSHOT_API_KEY}
      model: moonshot-v1-8k
      base_url: https://api.moonshot.cn/v1
    
    ollama:
      base_url: http://localhost:11434
      model: llama3
```

### 3.5 OCR 模块

| 功能 | 工具/脚本 | 支持引擎 | 依赖库 |
|------|-----------|----------|--------|
| 本地 OCR | `ocr_pdf.py` | Tesseract, PaddleOCR | pytesseract, paddleocr |
| 云端 OCR | `cloud_ocr.py` | Google Vision, Azure, AWS | google-cloud-vision, azure-cognitiveservices |
| 手写识别 | `handwriting_ocr()` | 云端 OCR | 同上 |
| 多语言 OCR | `multilingual_ocr()` | 所有引擎 | 同上 |

### 3.6 LaTeX 排版模块

| 功能 | 工具/脚本 | 说明 | 依赖库 |
|------|-----------|------|--------|
| LaTeX → PDF | `latex_to_pdf.py` | 编译 LaTeX | pdflatex, xelatex, lualatex |
| 模板渲染 | `render_template()` | 变量替换 | jinja2 |
| 公式排版 | `render_formula()` | 数学公式 | sympy, latex |
| 论文格式 | `render_paper()` | 学术论文 | latex templates |
| 书籍排版 | `render_book()` | 书籍排版 | latex templates |
| 幻灯片 | `render_slides()` | Beamer 幻灯片 | latex templates |

### 3.7 安全权限模块

| 功能 | 工具/脚本 | 说明 | 依赖库 |
|------|-----------|------|--------|
| 加密 | `encrypt_pdf.py` | 密码保护 | pypdf, qpdf |
| 解密 | `decrypt_pdf.py` | 移除密码 | pypdf, qpdf |
| 权限设置 | `set_permissions()` | 打印/复制/编辑权限 | pypdf, qpdf |
| 数字签名 | `sign_pdf.py` | 证书签名 | pyHanko, cryptography |
| 签名验证 | `verify_signature()` | 验证签名 | pyHanko |
| 敏感涂抹 | `redact_pdf.py` | 永久删除敏感信息 | pypdf, pymupdf |
| 合规检查 | `validate_pdf()` | PDF/A、WCAG 检查 | veraPDF |

---

## 四、配置设计

### 4.1 配置文件结构

```yaml
# ~/.pdf-master/config.yaml

# AI 模型配置
ai:
  default_provider: claude
  providers:
    claude:
      api_key: ${ANTHROPIC_API_KEY}
      model: claude-sonnet-4-6
    openai:
      api_key: ${OPENAI_API_KEY}
      model: gpt-4
    gemini:
      api_key: ${GOOGLE_API_KEY}
      model: gemini-pro
    deepseek:
      api_key: ${DEEPSEEK_API_KEY}
      model: deepseek-chat
    qwen:
      api_key: ${QWEN_API_KEY}
      model: qwen-max
    zhipu:
      api_key: ${ZHIPU_API_KEY}
      model: glm-4
    moonshot:
      api_key: ${MOONSHOT_API_KEY}
      model: moonshot-v1-8k
    ollama:
      base_url: http://localhost:11434
      model: llama3

# OCR 配置
ocr:
  default_engine: tesseract
  engines:
    tesseract:
      path: /usr/bin/tesseract
      languages: [chi_sim, eng]
    paddleocr:
      use_gpu: false
      lang: ch
    google_vision:
      credentials: ${GOOGLE_APPLICATION_CREDENTIALS}
    azure:
      endpoint: ${AZURE_COGNITIVE_ENDPOINT}
      key: ${AZURE_COGNITIVE_KEY}

# LaTeX 配置
latex:
  default_engine: pdflatex
  engines:
    local:
      texlive_path: /usr/local/texlive
    online:
      service: overleaf
      api_key: ${OVERLEAF_API_KEY}

# 输出配置
output:
  default_format: markdown
  default_dir: ./output
  preserve_structure: true

# 性能配置
performance:
  max_file_size_mb: 100
  batch_size: 10
  timeout_seconds: 300
```

---

## 五、错误处理设计

### 5.1 错误分类

```python
class PDFMasterError(Exception):
    """基础错误类"""
    error_code: str
    message: str
    suggestion: str
    retry_possible: bool

class FileNotFoundError(PDFMasterError):
    """文件不存在"""
    error_code = "FILE_NOT_FOUND"
    suggestion = "请检查文件路径是否正确"

class PasswordRequiredError(PDFMasterError):
    """需要密码"""
    error_code = "PASSWORD_REQUIRED"
    suggestion = "请提供 PDF 密码"

class CorruptedPDFError(PDFMasterError):
    """PDF 损坏"""
    error_code = "CORRUPTED_PDF"
    suggestion = "尝试使用 qpdf 修复"

class UnsupportedFormatError(PDFMasterError):
    """不支持的格式"""
    error_code = "UNSUPPORTED_FORMAT"
    suggestion = "检查文件是否为有效 PDF"

class OCRFailedError(PDFMasterError):
    """OCR 失败"""
    error_code = "OCR_FAILED"
    suggestion = "检查 OCR 引擎是否正确安装"
```

### 5.2 错误处理流程

```python
class ErrorHandler:
    def handle(self, error: Exception) -> PDFMasterError:
        # 1. 错误分类
        classified_error = self.classify(error)

        # 2. 自动重试（可重试错误）
        if classified_error.retry_possible:
            result = self.retry()
            if result.success:
                return result

        # 3. 降级方案（主方案失败时）
        fallback_result = self.fallback()
        if fallback_result.success:
            return fallback_result

        # 4. 用户确认（破坏性操作）
        if self.is_destructive():
            return self.ask_user_confirmation()

        # 5. 回滚机制（操作失败后恢复）
        self.rollback()

        return classified_error
```

---

## 六、依赖管理

### 6.1 核心依赖（必装）

```toml
[project.dependencies]
pypdf = ">=4.0.0"
pdfplumber = ">=0.10.0"
reportlab = ">=4.0.0"
Pillow = ">=10.0.0"
```

### 6.2 可选依赖

```toml
[project.optional-dependencies]
ocr = [
    "pytesseract>=0.3.10",
    "paddleocr>=2.7.0",
    "pdf2image>=1.16.0"
]
ai = [
    "anthropic>=0.18.0",
    "openai>=1.0.0",
    "transformers>=4.30.0"
]
latex = [
    "jinja2>=3.0.0"
]
tables = [
    "camelot-py>=0.11.0",
    "tabula-py>=2.7.0",
    "pandas>=2.0.0"
]
convert = [
    "pdf2docx>=0.5.0",
    "python-docx>=1.0.0",
    "openpyxl>=3.1.0",
    "python-pptx>=0.6.21"
]
security = [
    "pyHanko>=0.20.0",
    "cryptography>=41.0.0"
]
all = [
    "pdf-master[ocr,ai,latex,tables,convert,security]"
]
```

---

## 七、测试计划

### 7.1 单元测试

- 每个脚本独立测试
- 覆盖正常流程和异常流程
- 使用 pytest 框架

### 7.2 集成测试

- 端到端工作流测试
- 多模块协作测试
- 性能测试（大文件处理）

### 7.3 测试用例

| 模块 | 测试用例 | 预期结果 |
|------|----------|----------|
| 解析 | 提取文本、表格、图片 | 正确提取内容 |
| 编辑 | 合并、拆分、旋转 | 操作成功 |
| 转换 | PDF → Word/Excel/图片 | 格式正确 |
| AI | 摘要、问答、翻译 | 结果合理 |
| OCR | 扫描件识别 | 文字正确 |
| LaTeX | 编译 LaTeX | PDF 生成成功 |
| 安全 | 加密、解密、签名 | 操作成功 |

---

## 八、文档计划

### 8.1 用户文档

- **README.md**：快速开始、安装指南、基本用法
- **API.md**：所有脚本和函数的 API 文档
- **EXAMPLES.md**：常见用例和示例代码
- **BEST_PRACTICES.md**：最佳实践和性能优化

### 8.2 开发者文档

- **CONTRIBUTING.md**：贡献指南
- **ARCHITECTURE.md**：架构设计文档
- **CHANGELOG.md**：版本更新日志

---

## 九、发布计划

### 9.1 发布渠道

1. **GitHub**：主要代码仓库
2. **Claude Code Marketplace**：插件发布
3. **PyPI**：Python 包发布（可选）

### 9.2 版本规划

- **v1.0.0**：完整版本，包含所有功能
- **v1.1.0**：性能优化、bug 修复
- **v1.2.0**：新增功能、用户反馈改进

---

## 十、风险与缓解

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| 依赖库兼容性问题 | 高 | 使用虚拟环境、版本锁定 |
| 大文件处理性能 | 中 | 分块处理、流式处理 |
| OCR 准确率 | 中 | 多引擎支持、后处理校验 |
| AI API 成本 | 中 | 本地模型支持、缓存机制 |
| LaTeX 编译失败 | 低 | 在线服务备选、错误提示 |

---

## 十一、总结

pdf-master 是一个全能型 PDF 处理插件，设计目标是：

1. **功能最全**：覆盖所有主流 PDF 功能
2. **使用最便**：自然语言接口，一句话完成操作
3. **质量最高**：基于成熟库，不会产生幻觉
4. **效果最好**：专业库 + AI 理解，两者结合

通过模块化设计、完善的错误处理、灵活的配置系统，pdf-master 将成为 Claude Code 生态中最强大的 PDF 处理工具。
