# PDF-Master Architecture

This document describes the architecture and design decisions of PDF-Master.

## Overview

PDF-Master is a comprehensive Claude Code plugin for PDF processing. It provides a unified interface for parsing, editing, converting, and enhancing PDF documents with AI capabilities.

```
+------------------+     +------------------+     +------------------+
|   Claude Code    | --> |   PDF-Master     | --> |   PDF Libraries  |
|   CLI / Agent    |     |   Plugin Core    |     |   (pypdf, etc.)  |
+------------------+     +------------------+     +------------------+
                                |
                                v
                         +-------------+
                         | AI Provider |
                         | (8 platforms)|
                         +-------------+
```

## Directory Structure

```
pdf-master/
+-- .claude-plugin/           # Plugin configuration
|   +-- plugin.json           # Plugin metadata (name, version, skills)
|   +-- marketplace.json      # Marketplace configuration
|
+-- skills/pdf/               # Core skill implementation
|   +-- SKILL.md              # Skill entry point and documentation
|   +-- scripts/              # Python scripts (34 tools)
|   |   +-- extract_*.py      # Extraction scripts
|   |   +-- merge_*.py        # Merge/split scripts
|   |   +-- ocr_*.py          # OCR scripts
|   |   +-- ai_*.py           # AI enhancement scripts
|   |   +-- security_*.py     # Security scripts
|   |   +-- form_*.py         # Form handling scripts
|   |   +-- convert_*.py      # Conversion scripts
|   |   +-- *                 # Utility scripts
|   +-- ai_provider.py        # AI provider abstraction
|   +-- reference.md          # Reference documentation
|   +-- forms.md              # Form handling guide
|   +-- ai.md                 # AI integration guide
|   +-- ocr.md                # OCR documentation
|   +-- latex.md              # LaTeX rendering guide
|   +-- security.md           # Security documentation
|
+-- agents/                   # Sub-agent definitions (15 agents)
|   +-- pdf-explorer.md       # Fast structure exploration (haiku)
|   +-- pdf-analyzer.md       # Content analysis (sonnet)
|   +-- pdf-converter.md      # Format conversion (sonnet)
|   +-- pdf-extract.md        # Content extraction (sonnet)
|   +-- pdf-merge-split.md    # Merge/split operations (haiku)
|   +-- pdf-security.md       # Security operations (sonnet)
|   +-- pdf-ocr.md            # OCR processing (sonnet)
|   +-- pdf-ai.md             # AI enhancement (sonnet)
|   +-- pdf-form.md           # Form handling (haiku)
|   +-- pdf-batch.md          # Batch processing (sonnet)
|   +-- pdf-compare.md        # PDF comparison (sonnet)
|   +-- pdf-repair.md         # PDF repair (sonnet)
|   +-- pdf-compress.md       # PDF compression (haiku)
|   +-- pdf-watermark.md      # Watermark operations (haiku)
|   +-- pdf-metadata.md       # Metadata management (haiku)
|
+-- hooks/                    # Lifecycle hooks
|   +-- hooks.json            # Hook definitions
|
+-- bin/                      # CLI tools (auto-added to PATH)
|   +-- pdf-master            # Command-line entry point
|
+-- output-styles/            # Output style definitions
|   +-- pdf-report.md         # Report output style
|   +-- pdf-summary.md        # Summary output style
|
+-- tests/                    # Test suite (232 test cases)
|   +-- test_*.py             # Unit tests
|   +-- fixtures/             # Test fixtures
|
+-- docs/                     # Documentation
|   +-- API.md                # API reference
|   +-- CONFIGURATION.md      # Configuration guide
|   +-- CONTRIBUTING.md       # Contribution guidelines
|   +-- EXAMPLES.md           # Usage examples
|   +-- TROUBLESHOOTING.md    # Troubleshooting guide
|   +-- SECURITY_AUDIT.md     # Security audit report
|
+-- config/                   # Configuration templates
|   +-- config.yaml.example   # Sample configuration
|   +-- providers.yaml        # AI provider definitions
|
+-- examples/                 # Example scripts
|   +-- basic_usage.py        # Basic usage examples
|   +-- advanced_*.py         # Advanced examples
|
+-- .github/workflows/        # CI/CD pipelines
|   +-- ci.yml                # Continuous integration
|   +-- release.yml           # Release automation
|   +-- deploy-pages.yml      # GitHub Pages deployment
```

## Core Components

### 1. Plugin Configuration (.claude-plugin/)

**plugin.json** - Defines the plugin's identity and capabilities:

```json
{
  "name": "pdf-master",
  "version": "1.1.0",
  "skills": ["pdf"],
  "agents": ["pdf-explorer", "pdf-analyzer", ...],
  "hooks": ["SessionStart", "PreToolUse", "PostToolUse"]
}
```

### 2. Skills (skills/pdf/)

Skills are the primary interface for users. Each skill:

- Provides a `/pdf` command
- Dispatches to appropriate Python scripts
- Handles error cases gracefully

**Script Architecture:**

```
skills/pdf/scripts/
+-- Core extraction
|   +-- extract_text.py       # Text extraction with layout preservation
|   +-- extract_tables.py     # Table extraction (JSON/CSV/Excel)
|   +-- extract_images.py     # Image extraction
|   +-- extract_metadata.py   # Metadata extraction
|
+-- Editing operations
|   +-- merge_pdfs.py         # Merge multiple PDFs
|   +-- split_pdf.py          # Split PDF by pages
|   +-- rotate_pdf.py         # Rotate pages
|   +-- watermark_pdf.py      # Add watermarks
|
+-- Conversion
|   +-- convert_pdf_to_images.py  # PDF to images
|   +-- pdf_to_excel.py       # PDF to Excel
|   +-- pdf_to_markdown.py    # PDF to Markdown
|
+-- AI enhancement
|   +-- summarize_pdf.py      # AI summarization
|   +-- qa_pdf.py             # AI Q&A
|   +-- translate_pdf.py      # AI translation
|
+-- OCR
|   +-- ocr_pdf.py            # OCR with Tesseract/PaddleOCR
|
+-- Security
|   +-- encrypt_pdf.py        # AES-256 encryption
|   +-- decrypt_pdf.py        # Decryption
|   +-- redact_pdf.py         # Sensitive data redaction
|
+-- Forms
|   +-- check_fillable_fields.py  # Check form fields
|   +-- fill_fillable_fields.py   # Fill forms
|
+-- Utilities
    +-- pdf_info.py           # PDF information
    +-- pdf_validate.py       # PDF validation
    +-- pdf_compress.py       # PDF compression
    +-- pdf_repair.py         # PDF repair
    +-- pdf_compare.py        # PDF comparison
    +-- batch_process.py      # Batch processing
```

### 3. Agents (agents/)

Sub-agents provide specialized AI assistance with appropriate model selection:

| Agent | Model | Purpose |
|-------|-------|---------|
| pdf-explorer | haiku | Fast operations, metadata, structure |
| pdf-analyzer | sonnet | Deep content analysis |
| pdf-converter | sonnet | Format conversion |
| pdf-extract | sonnet | Content extraction |
| pdf-merge-split | haiku | Simple merge/split |
| pdf-security | sonnet | Security operations |
| pdf-ocr | sonnet | OCR processing |
| pdf-ai | sonnet | AI enhancement |
| pdf-form | haiku | Form handling |
| pdf-batch | sonnet | Batch processing |
| pdf-compare | sonnet | PDF comparison |
| pdf-repair | sonnet | PDF repair |
| pdf-compress | haiku | PDF compression |
| pdf-watermark | haiku | Watermark operations |
| pdf-metadata | haiku | Metadata management |

### 4. Hooks (hooks/)

Lifecycle hooks for automated behaviors:

```json
{
  "hooks": {
    "SessionStart": "Check PDF dependencies",
    "PreToolUse": "Block dangerous commands (rm -rf)",
    "PostToolUse": "Validate PDF after modifications",
    "PostToolUseFailure": "PDF operation error handling",
    "SubagentStart": "Inject context for sub-agents"
  }
}
```

### 5. AI Provider System (skills/pdf/ai_provider.py)

Abstracts multiple AI platforms:

```
BaseAIProvider (abstract)
    |
    +-- ClaudeProvider (Anthropic)
    +-- OpenAIProvider
    |       +-- OpenAI (GPT-4)
    |       +-- DeepSeek
    |       +-- Moonshot
    +-- GeminiProvider (Google)
    +-- QwenProvider (Alibaba)
    +-- ZhipuProvider (Zhipu AI)
    +-- OllamaProvider (Local)
```

**Provider Selection Flow:**

```
User Request --> Provider Factory --> Selected Provider --> API Call
                     |
                     v
              config/providers.yaml
              Environment Variables
```

## Data Flow

### PDF Processing Pipeline

```
1. Input Validation
   |
   v
2. PDF Library Selection (pypdf/PyMuPDF/pdfplumber)
   |
   v
3. Processing Operation
   |
   v
4. Output Generation
   |
   v
5. Validation (hooks)
   |
   v
6. Return Result
```

### AI Enhancement Pipeline

```
1. PDF Content Extraction
   |
   v
2. Text Chunking (if needed)
   |
   v
3. Provider Selection
   |
   v
4. API Call
   |
   v
5. Response Processing
   |
   v
6. Return Result
```

## Dependencies

### Core Libraries

| Library | Purpose |
|---------|---------|
| pypdf | PDF reading/writing |
| PyMuPDF | High-performance PDF operations |
| pdfplumber | Table extraction |
| reportlab | PDF generation |
| Pillow | Image processing |

### Optional Libraries

| Library | Purpose |
|---------|---------|
| pytesseract | Tesseract OCR |
| paddleocr | PaddleOCR (better Chinese) |
| anthropic | Claude API |
| openai | OpenAI API |
| google-generativeai | Gemini API |

## Configuration

### Environment Variables

```bash
ANTHROPIC_API_KEY=your-key     # Claude
OPENAI_API_KEY=your-key        # OpenAI
GOOGLE_API_KEY=your-key        # Gemini
DEEPSEEK_API_KEY=your-key      # DeepSeek
QWEN_API_KEY=your-key          # Qwen
ZHIPU_API_KEY=your-key         # Zhipu AI
MOONSHOT_API_KEY=your-key      # Moonshot
```

### Config Files

- `config/config.yaml` - Main configuration
- `config/providers.yaml` - AI provider definitions

## Error Handling

All scripts follow a unified error handling pattern:

```python
try:
    result = process_pdf(input_path)
    return result
except FileNotFoundError:
    print(f"Error: File not found: {input_path}", file=sys.stderr)
    sys.exit(1)
except PdfReadError as e:
    print(f"Error: Invalid PDF: {e}", file=sys.stderr)
    sys.exit(1)
except Exception as e:
    print(f"Error: {e}", file=sys.stderr)
    sys.exit(1)
```

## Testing

### Test Structure

```
tests/
+-- test_extract_*.py      # Extraction tests
+-- test_merge_*.py        # Merge tests
+-- test_ai_provider.py    # AI provider tests
+-- test_ocr_*.py          # OCR tests
+-- fixtures/              # Test PDFs
    +-- sample.pdf
    +-- encrypted.pdf
    +-- form.pdf
```

### Running Tests

```bash
# All tests
pytest

# Specific test
pytest tests/test_extract_text.py -v

# With coverage
pytest --cov=skills/pdf/scripts/
```

## Security Considerations

1. **Encryption**: AES-256 for PDF encryption
2. **Redaction**: Secure removal of sensitive data
3. **Input Validation**: All inputs validated before processing
4. **Hook Protection**: Dangerous commands blocked by PreToolUse hook

See [docs/SECURITY_AUDIT.md](SECURITY_AUDIT.md) for detailed security analysis.

## Performance Optimization

1. **Lazy Loading**: AI providers loaded on demand
2. **Caching**: Configuration cached in memory
3. **Model Selection**: Haiku for simple tasks, Sonnet for complex
4. **Batch Processing**: Parallel processing for multiple files

## Future Roadmap

1. **More AI Providers**: Additional AI platform support
2. **Enhanced OCR**: Better handwriting recognition
3. **PDF/A Compliance**: Archive format support
4. **Cloud Storage**: Direct cloud storage integration
5. **Web Interface**: Optional web UI for non-CLI users
