# Changelog

All notable changes to PDF-Master will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2026-04-14

### Added

#### New Features
- **Configurable AI Provider System**: Customizable AI provider configuration via YAML files
- **6 New Tool Scripts**: pdf_info, pdf_validate, pdf_compress, pdf_repair, pdf_compare, batch_process
- **Complete Documentation System**: 5 core documents + 4 example files

#### Infrastructure
- **CI/CD Pipeline**: GitHub Actions workflow with automated testing
- **Makefile**: Build automation with test, format, lint commands
- **Pre-commit Hooks**: Code quality automation

#### Testing
- **12 New Test Files**: Comprehensive test coverage
- **232 Test Cases**: Full coverage for all PDF operations

### Fixed

#### Code Quality (Official Spec Audit)
- **PEP 8 Compliance**: Split imports, added docstrings, type hints
- **Agent Configuration**: Migrated from `disallowedTools` to `allowed-tools` whitelist
- **Hooks Configuration**: Fixed matcher patterns and event types
- **Shell Scripts**: Fixed syntax errors in batch_processing.sh

#### Project Files
- **CONTRIBUTING.md**: Contribution guidelines
- **CODE_OF_CONDUCT.md**: Community code of conduct
- **Issue/PR Templates**: GitHub issue and PR templates
- **ARCHITECTURE.md**: Project architecture documentation

### Changed
- **Git Permissions**: Set execute permission for bin/pdf-master
- **Model Info**: Updated AI model references to claude-sonnet-4-6

## [1.0.0] - 2026-04-13

### Added

#### Core Features
- **PDF Extraction**: Extract text, tables, images, and metadata from PDF files
- **PDF Editing**: Merge, split, rotate, and add watermarks to PDFs
- **Format Conversion**: Convert PDF to Excel, Markdown, and images
- **AI Enhancement**: Summarize, Q&A, and translate PDFs with 8 AI platforms
- **OCR Support**: Recognize text from scanned PDFs (Tesseract/PaddleOCR)
- **Security**: Encrypt, decrypt, and redact sensitive information
- **Form Handling**: Check, extract, and fill PDF form fields

#### Plugin Components
- **Skills**: Main PDF processing skill with 20+ operations
- **Agents**: Three specialized subagents (pdf-explorer, pdf-analyzer, pdf-converter)
- **Hooks**: SessionStart dependency check, PostToolUse PDF validation
- **Output Styles**: pdf-report and pdf-summary styles

#### AI Provider Support
- Claude (Anthropic)
- OpenAI (GPT)
- Google Gemini
- DeepSeek
- Qwen (通义千问)
- 智谱 GLM
- Moonshot AI
- Ollama (local)

#### Documentation
- Comprehensive README with usage examples
- Reference documentation for advanced features
- AI configuration guide
- OCR setup instructions
- Form handling guide
- Security features documentation
- LaTeX rendering support

### Technical Details
- Python-based scripts with CLI support
- Modular architecture for easy extension
- Configuration via YAML files
- Environment variable support for API keys
- Progress display for long operations
- Batch processing capabilities

## [Unreleased]

### Planned
- Web UI for PDF operations
- Cloud storage integration
- Batch processing dashboard
- Custom AI prompt templates
- PDF comparison tool
- Digital signature support
