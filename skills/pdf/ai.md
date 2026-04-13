# AI 增强功能

## 支持的 AI 提供商

| 提供商 | 环境变量 | 模型 |
|--------|----------|------|
| Anthropic | `ANTHROPIC_API_KEY` | Claude 3.5 Sonnet |
| OpenAI | `OPENAI_API_KEY` | GPT-4o |
| Google | `GOOGLE_API_KEY` | Gemini 1.5 Pro |

## 环境变量配置

### Linux / macOS

```bash
# 编辑 ~/.bashrc 或 ~/.zshrc
export ANTHROPIC_API_KEY="your-api-key-here"
export OPENAI_API_KEY="your-openai-key"
export GOOGLE_API_KEY="your-google-key"
```

### Windows (PowerShell)

```powershell
# 设置用户环境变量
[Environment]::SetEnvironmentVariable("ANTHROPIC_API_KEY", "your-key", "User")
```

### Windows (CMD)

```cmd
setx ANTHROPIC_API_KEY "your-key"
```

## 功能说明

### summarize - AI 摘要

生成 PDF 文档的智能摘要。

```bash
/pdf summarize document.pdf

# 指定语言
/pdf summarize document.pdf --lang zh

# 指定长度
/pdf summarize document.pdf --length short   # short/medium/long
```

**Python 实现：**

```python
import fitz
from anthropic import Anthropic

def summarize_pdf(pdf_path, lang="zh"):
    """使用 AI 生成 PDF 摘要"""
    # 提取文本
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()

    # 调用 AI
    client = Anthropic()
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        messages=[{
            "role": "user",
            "content": f"""请用{lang}总结以下文档内容：

{text[:10000]}  # 限制长度

请提供：
1. 主题概述
2. 关键要点（3-5个）
3. 结论
"""
        }]
    )

    return message.content[0].text
```

### ask - AI 问答

对 PDF 内容进行提问。

```bash
/pdf ask document.pdf "这篇文章的主要结论是什么？"

/pdf ask document.pdf "列出文中的所有日期"

/pdf ask document.pdf "作者是谁？" --provider openai
```

**Python 实现：**

```python
import fitz
from anthropic import Anthropic

def ask_pdf(pdf_path, question, provider="anthropic"):
    """对 PDF 进行问答"""
    # 提取文本
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()

    # 选择提供商
    if provider == "anthropic":
        client = Anthropic()
        model = "claude-sonnet-4-20250514"
    elif provider == "openai":
        from openai import OpenAI
        client = OpenAI()
        model = "gpt-4o"

    # 调用 AI
    if provider == "anthropic":
        response = client.messages.create(
            model=model,
            max_tokens=1024,
            messages=[{
                "role": "user",
                "content": f"""根据以下文档内容回答问题。

文档内容：
{text[:10000]}

问题：{question}

请基于文档内容回答，如果文档中没有相关信息，请说明。"""
            }]
        )
        return response.content[0].text
    else:
        response = client.chat.completions.create(
            model=model,
            messages=[{
                "role": "user",
                "content": f"""根据以下文档内容回答问题。

文档内容：
{text[:10000]}

问题：{question}"""
            }]
        )
        return response.choices[0].message.content
```

### translate - AI 翻译

翻译 PDF 内容到目标语言。

```bash
# 翻译为英文
/pdf translate document.pdf --to en

# 翻译为日文
/pdf translate document.pdf --to ja

# 指定页面范围
/pdf translate document.pdf --to en --pages 1-10
```

**Python 实现：**

```python
import fitz
from anthropic import Anthropic

LANGUAGE_MAP = {
    "zh": "中文",
    "en": "English",
    "ja": "日本語",
    "ko": "한국어",
    "fr": "Français",
    "de": "Deutsch",
    "es": "Español"
}

def translate_pdf(pdf_path, target_lang, pages=None):
    """翻译 PDF 内容"""
    doc = fitz.open(pdf_path)
    client = Anthropic()
    target = LANGUAGE_MAP.get(target_lang, target_lang)

    results = []
    page_range = range(len(doc)) if pages is None else pages

    for i in page_range:
        page = doc[i]
        text = page.get_text()

        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            messages=[{
                "role": "user",
                "content": f"""将以下文本翻译成{target}。
保持原文格式，只输出翻译结果，不要添加任何说明。

{text}"""
            }]
        )

        results.append({
            "page": i + 1,
            "translation": response.content[0].text
        })

    doc.close()
    return results
```

## 高级用法

### 批量处理

```python
import os
from anthropic import Anthropic
import fitz

def batch_summarize(pdf_dir):
    """批量生成摘要"""
    client = Anthropic()
    results = {}

    for filename in os.listdir(pdf_dir):
        if filename.endswith(".pdf"):
            pdf_path = os.path.join(pdf_dir, filename)

            # 提取文本
            doc = fitz.open(pdf_path)
            text = "".join(page.get_text() for page in doc)
            doc.close()

            # 生成摘要
            message = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=500,
                messages=[{
                    "role": "user",
                    "content": f"用一句话总结：{text[:5000]}"
                }]
            )

            results[filename] = message.content[0].text

    return results
```

### 多文档问答

```python
from anthropic import Anthropic
import fitz

def multi_doc_query(pdf_paths, question):
    """在多个文档中搜索答案"""
    client = Anthropic()

    # 收集所有文档内容
    context = ""
    for pdf_path in pdf_paths:
        doc = fitz.open(pdf_path)
        text = "".join(page.get_text() for page in doc)
        doc.close()
        context += f"\n--- {pdf_path} ---\n{text[:3000]}\n"

    # 提问
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        messages=[{
            "role": "user",
            "content": f"""基于以下多个文档回答问题，并注明信息来源。

文档内容：
{context}

问题：{question}"""
        }]
    )

    return response.content[0].text
```

### 使用缓存优化

```python
import hashlib
import json
from pathlib import Path
from anthropic import Anthropic
import fitz

def cached_summarize(pdf_path, cache_dir=".cache"):
    """带缓存的摘要生成"""
    # 计算文件哈希
    with open(pdf_path, "rb") as f:
        file_hash = hashlib.md5(f.read()).hexdigest()

    # 检查缓存
    cache_file = Path(cache_dir) / f"{file_hash}.json"
    if cache_file.exists():
        return json.loads(cache_file.read_text())

    # 生成摘要
    doc = fitz.open(pdf_path)
    text = "".join(page.get_text() for page in doc)
    doc.close()

    client = Anthropic()
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=500,
        messages=[{"role": "user", "content": f"总结：{text[:5000]}"}]
    )

    result = response.content[0].text

    # 保存缓存
    cache_file.parent.mkdir(exist_ok=True)
    cache_file.write_text(json.dumps({"summary": result}))

    return result
```

## 错误处理

```python
import os
from anthropic import Anthropic, APIError, RateLimitError

def safe_ai_call(text, max_retries=3):
    """安全的 AI 调用"""
    if not os.getenv("ANTHROPIC_API_KEY"):
        raise ValueError("未设置 ANTHROPIC_API_KEY 环境变量")

    client = Anthropic()

    for attempt in range(max_retries):
        try:
            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1024,
                messages=[{"role": "user", "content": text}]
            )
            return response.content[0].text

        except RateLimitError:
            if attempt < max_retries - 1:
                import time
                time.sleep(2 ** attempt)  # 指数退避
                continue
            raise

        except APIError as e:
            raise RuntimeError(f"API 调用失败: {e}")
```
