# Changelog

All notable changes to PDF-Master will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.4.1] - 2026-04-14

### Fixed
- **sign_pdf.py**: Fixed endesive API compatibility - key and cert must be cryptography objects, not bytes
- **encrypt_pdf.py**: Fixed pypdf API compatibility - `permissions` → `permissions_flag`
- **bookmarks.py**: Fixed Windows console encoding issue - Unicode bullet → ASCII dash
- **watermark_pdf.py**: Fixed image watermark support - PNG/JPG now properly converted to PDF before applying

### Dependencies
- Added `endesive` to optional dependencies for digital signature support

## [1.4.0] - 2026-04-14

### Added
- **PDF/A Conversion**: Support for PDF/A-1b/2b/3b archive format conversion and validation
- **Security Audit**: Detect JavaScript/embedded files/suspicious links and other security risks
- **Bookmark Management**: Add/delete/extract PDF bookmarks
- **Link Management**: Extract/add/delete PDF hyperlinks
- **Annotation Management**: Add/delete/extract PDF annotations (text/highlight/underline)
- **Test Coverage**: Extended to 343 test cases

## [1.3.0] - 2026-04-14

### Added
- **Digital Signatures**: X.509 certificate signing, verification, timestamp service support
- **Signature Algorithms**: RSA/ECDSA support, visible/invisible signatures
- **Test Coverage**: 282 test cases (25 new signature tests)
- **Research Report**: 30 agent teams parallel research output

## [1.2.0] - 2026-04-14

### Fixed
- **Security Enhancements**: Fixed hooks security vulnerabilities, added sensitive file protection
- **Configuration**: Added `.env.example` and `settings.json`

### Added
- **Batch Rename**: Support content/metadata/date/custom rules
- **Test Coverage**: 257 test cases, 60%+ coverage
