# 贡献指南

感谢您有兴趣为 PDF-Master 做出贡献！本文档将帮助您了解开发流程和规范。

## 目录

- [开发环境搭建](#开发环境搭建)
- [代码风格指南](#代码风格指南)
- [提交规范](#提交规范)
- [PR 流程](#pr-流程)
- [测试规范](#测试规范)

---

## 开发环境搭建

### 系统要求

- Python 3.10+
- Git

### 克隆仓库

```bash
git clone https://github.com/zshyc/pdf-master.git
cd pdf-master
```

### 创建虚拟环境

```bash
# 使用 venv
python -m venv venv

# 激活虚拟环境
# Linux/macOS
source venv/bin/activate

# Windows
venv\Scriptsctivate
```

### 安装依赖

```bash
# 安装核心依赖
pip install -r requirements.txt

# 安装开发依赖
pip install pytest black flake8 mypy
```

### 安装外部工具

#### OCR 工具

```bash
# macOS
brew install tesseract tesseract-lang poppler

# Linux
sudo apt-get install tesseract-ocr poppler-utils

# Windows
choco install tesseract poppler
```

#### LaTeX (可选)

```bash
# macOS
brew install --cask mactex

# Linux
sudo apt-get install texlive-full

# Windows
# 下载安装 MiKTeX: https://miktex.org/
```

---

## 代码风格指南

### Python 代码规范

遵循 PEP 8 规范，使用以下工具检查：

```bash
# 格式化代码
black skills/pdf/scripts/

# 检查代码风格
flake8 skills/pdf/scripts/

# 类型检查
mypy skills/pdf/scripts/
```

### 代码结构

每个脚本应包含：

1. **模块文档字符串** - 说明脚本用途
2. **参数解析** - 使用 argparse
3. **主函数** - 实现核心逻辑
4. **错误处理** - 统一的错误处理

示例：

```python
#!/usr/bin/env python3
"""
Script Description

Detailed explanation of what this script does.

Usage:
    python script.py <input> [options]
"""

import argparse
import sys
from pathlib import Path

def main_function(input_path: str, output_path: str) -> bool:
    """
    Main function description.
    
    Args:
        input_path: Input file path
        output_path: Output file path
        
    Returns:
        bool: Success status
    """
    try:
        # Implementation
        return True
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return False

def main():
    parser = argparse.ArgumentParser(description="Script description")
    parser.add_argument("input", help="Input file")
    parser.add_argument("-o", "--output", help="Output file")
    args = parser.parse_args()
    
    success = main_function(args.input, args.output)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
```

### 命名规范

- **文件名**: 小写下划线，如 `extract_text.py`
- **函数名**: 小写下划线，如 `extract_text()`
- **类名**: 大驼峰，如 `AIProvider`
- **常量**: 大写下划线，如 `DEFAULT_DPI`

---

## 提交规范

### Commit Message 格式

使用 Conventional Commits 规范：

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

### Type 类型

| 类型 | 说明 |
|------|------|
| feat | 新功能 |
| fix | Bug 修复 |
| docs | 文档更新 |
| style | 代码格式（不影响功能） |
| refactor | 重构 |
| perf | 性能优化 |
| test | 测试相关 |
| chore | 构建/工具相关 |

### 示例

```bash
# 新功能
git commit -m "feat(ai): add DeepSeek provider support"

# Bug 修复
git commit -m "fix(ocr): handle empty PDF pages correctly"

# 文档更新
git commit -m "docs: update API documentation"
```

---

## PR 流程

### 创建 PR

1. Fork 仓库
2. 创建功能分支：`git checkout -b feature/your-feature`
3. 提交更改
4. 推送分支：`git push origin feature/your-feature`
5. 创建 Pull Request

### PR 标题格式

```
<type>: <description>
```

示例：
- `feat: add batch processing support`
- `fix: resolve memory leak in OCR module`

### PR 检查清单

- [ ] 代码符合风格规范
- [ ] 添加了必要的测试
- [ ] 更新了相关文档
- [ ] 所有测试通过
- [ ] 没有引入新的警告

### 代码审查

所有 PR 需要至少一位维护者审查后才能合并。

---

## 测试规范

### 运行测试

```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_extract_text.py

# 带覆盖率报告
pytest --cov=skills/pdf/scripts/
```

### 测试文件结构

```
tests/
├── __init__.py
├── test_extract_text.py
├── test_merge_pdfs.py
├── test_ai_provider.py
└── fixtures/
    ├── sample.pdf
    └── expected_output.txt
```

### 测试用例示例

```python
import pytest
from pathlib import Path
from skills.pdf.scripts.extract_text import extract_text

class TestExtractText:
    def test_extract_text_basic(self, tmp_path):
        """Test basic text extraction"""
        input_pdf = Path("tests/fixtures/sample.pdf")
        output = tmp_path / "output.txt"
        
        result = extract_text(str(input_pdf), output_file=str(output))
        
        assert output.exists()
        assert len(result) > 0
        
    def test_extract_text_invalid_file(self):
        """Test with invalid file"""
        with pytest.raises(FileNotFoundError):
            extract_text("nonexistent.pdf")
```

### 测试覆盖要求

- 新功能：覆盖率 >= 80%
- Bug 修复：添加回归测试
- 核心模块：覆盖率 >= 90%

---

## 添加新功能

### 添加新的 AI Provider

1. 在 `ai_provider.py` 中添加新类：

```python
class NewProvider(OpenAIProvider):
    PROVIDER_NAME = "newprovider"
    DEFAULT_MODEL = "model-name"
    ENV_KEY = "NEWPROVIDER_API_KEY"
    BASE_URL = "https://api.newprovider.com/v1"
```

2. 注册到 PROVIDERS 字典

3. 添加测试用例

4. 更新文档

### 添加新的脚本

1. 创建脚本文件：`skills/pdf/scripts/new_script.py`
2. 遵循代码规范
3. 添加 CLI 参数
4. 编写测试用例
5. 更新 API 文档

---

## 问题反馈

如果您发现问题或有功能建议：

1. 检查是否已有相关 Issue
2. 创建新 Issue，包含：
   - 问题描述
   - 复现步骤
   - 期望行为
   - 实际行为
   - 环境信息

---

## 联系方式

- 作者: zshyc
- Email: 17669757689@163.com
- GitHub: https://github.com/zshyc/pdf-master
