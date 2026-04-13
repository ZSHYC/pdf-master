# LaTeX 排版

## 支持的引擎

| 引擎 | 特点 | 适用场景 |
|------|------|----------|
| pdflatex | 传统引擎，速度快 | 纯英文文档 |
| xelatex | 支持 Unicode 和系统字体 | 中文文档 |
| lualatex | 现代，可编程 | 复杂排版需求 |

## 基本用法

```bash
# 使用默认引擎 (xelatex)
/pdf latex document.tex

# 指定引擎
/pdf latex document.tex --engine pdflatex
/pdf latex document.tex --engine xelatex
/pdf latex document.tex --engine lualatex

# 指定输出目录
/pdf latex document.tex -o output/

# 多次编译（处理交叉引用）
/pdf latex document.tex --runs 2
```

## 安装指南

### Windows

```bash
# 推荐安装 MiKTeX
# 下载: https://miktex.org/download

# 或 TeX Live (完整版)
# 下载: https://tug.org/texlive/

# 添加到 PATH 后验证
pdflatex --version
xelatex --version
```

### macOS

```bash
# 使用 Homebrew 安装 MacTeX
brew install --cask mactex

# 或安装精简版
brew install --cask basictex

# 验证
pdflatex --version
```

### Linux

```bash
# Ubuntu/Debian
sudo apt-get install texlive-full  # 完整版
# 或精简版
sudo apt-get install texlive texlive-xetex texlive-latex-extra

# 中文支持
sudo apt-get install texlive-lang-chinese

# 验证
pdflatex --version
xelatex --version
```

## LaTeX 模板

### 中文文档模板

```latex
\documentclass[UTF8]{ctexart}

\title{文档标题}
\author{作者姓名}
\date{\today}

\begin{document}

\maketitle

\section{引言}
这是中文文档的内容。

\section{正文}
\subsection{第一节}
正文内容...

\begin{itemize}
    \item 列表项一
    \item 列表项二
\end{itemize}

\end{document}
```

### 学术论文模板

```latex
\documentclass[12pt, a4paper]{article}
\usepackage[UTF8]{ctex}
\usepackage{geometry}
\usepackage{graphicx}
\usepackage{amsmath}
\usepackage{hyperref}

\geometry{margin=2.5cm}

\title{论文标题}
\author{作者 \\ 单位}
\date{\today}

\begin{document}

\maketitle

\begin{abstract}
摘要内容...
\end{abstract}

\section{引言}
正文内容...

\section{方法}
\subsection{数据收集}
描述...

\section{结果}
结果展示...

\begin{equation}
E = mc^2
\end{equation}

\section{结论}
结论内容...

\end{document}
```

### 幻灯片模板

```latex
\documentclass[UTF8]{ctexbeamer}
\usetheme{Madrid}
\usecolortheme{default}

\title{演示标题}
\author{演讲者}
\date{\today}

\begin{document}

\begin{frame}
    \titlepage
\end{frame}

\begin{frame}{目录}
    \tableofcontents
\end{frame}

\section{第一部分}

\begin{frame}{幻灯片标题}
    内容要点：
    \begin{itemize}
        \item 第一点
        \item 第二点
        \item 第三点
    \end{itemize}
\end{frame}

\section{第二部分}

\begin{frame}{代码示例}
    \begin{verbatim}
    def hello():
        print("Hello, LaTeX!")
    \end{verbatim}
\end{frame}

\end{document}
```

## Python 实现

### 基本转换

```python
import subprocess
import os

def latex_to_pdf(tex_path, engine='xelatex', output_dir=None, runs=1):
    """将 LaTeX 文件转换为 PDF"""
    # 获取文件信息
    tex_dir = os.path.dirname(os.path.abspath(tex_path))
    tex_name = os.path.basename(tex_path)
    base_name = os.path.splitext(tex_name)[0]

    # 设置输出目录
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        output_arg = ['-output-directory', output_dir]
    else:
        output_arg = []
        output_dir = tex_dir

    # 编译命令
    cmd = [engine, '-interaction=nonstopmode'] + output_arg + [tex_name]

    # 多次编译（处理交叉引用）
    for _ in range(runs):
        result = subprocess.run(
            cmd,
            cwd=tex_dir,
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            raise RuntimeError(f"LaTeX 编译失败:\n{result.stderr}")

    # 返回 PDF 路径
    pdf_path = os.path.join(output_dir, f"{base_name}.pdf")
    return pdf_path if os.path.exists(pdf_path) else None

# 使用
pdf = latex_to_pdf("document.tex", engine='xelatex')
print(f"生成 PDF: {pdf}")
```

### 自动检测引擎

```python
def detect_engine(tex_content):
    """根据文档内容自动检测合适的引擎"""
    # 检查中文
    if '\\usepackage{ctex}' in tex_content or \
       'ctexart' in tex_content or \
       'ctexbook' in tex_content:
        return 'xelatex'

    # 检查特殊包
    if 'fontspec' in tex_content or \
       'unicode-math' in tex_content:
        return 'xelatex'

    # 检查 Lua 特性
    if 'luatex' in tex_content.lower() or \
       'lua' in tex_content.lower():
        return 'lualatex'

    # 默认使用 pdflatex
    return 'pdflatex'

def smart_latex_to_pdf(tex_path):
    """智能选择引擎编译"""
    with open(tex_path, 'r', encoding='utf-8') as f:
        content = f.read()

    engine = detect_engine(content)
    print(f"使用引擎: {engine}")

    return latex_to_pdf(tex_path, engine=engine)
```

### 处理编译错误

```python
import re

def parse_latex_errors(log_content):
    """解析 LaTeX 编译错误"""
    errors = []

    # 匹配错误行
    error_pattern = r'! (.+?)\nl\.(\d+)'
    for match in re.finditer(error_pattern, log_content, re.DOTALL):
        errors.append({
            'message': match.group(1),
            'line': int(match.group(2))
        })

    return errors

def latex_to_pdf_safe(tex_path, engine='xelatex'):
    """安全的 LaTeX 编译"""
    try:
        tex_dir = os.path.dirname(os.path.abspath(tex_path))
        tex_name = os.path.basename(tex_path)

        result = subprocess.run(
            [engine, '-interaction=nonstopmode', tex_name],
            cwd=tex_dir,
            capture_output=True,
            text=True
        )

        # 检查日志文件
        log_name = os.path.splitext(tex_name)[0] + '.log'
        log_path = os.path.join(tex_dir, log_name)

        if os.path.exists(log_path):
            with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
                log_content = f.read()

            errors = parse_latex_errors(log_content)
            if errors:
                print(f"发现 {len(errors)} 个错误:")
                for e in errors:
                    print(f"  行 {e['line']}: {e['message']}")

        return result.returncode == 0

    except Exception as e:
        print(f"编译异常: {e}")
        return False
```

## 高级功能

### 自动安装缺失宏包

```python
import subprocess

def install_package(package_name):
    """自动安装 LaTeX 宏包 (MiKTeX)"""
    try:
        # MiKTeX
        subprocess.run(
            ['miktex-console', 'install', package_name],
            check=True
        )
        print(f"已安装宏包: {package_name}")
        return True
    except:
        pass

    try:
        # tlmgr (TeX Live)
        subprocess.run(
            ['tlmgr', 'install', package_name],
            check=True
        )
        print(f"已安装宏包: {package_name}")
        return True
    except:
        pass

    return False
```

### 批量转换

```python
import os
from concurrent.futures import ThreadPoolExecutor

def batch_latex_to_pdf(tex_dir, output_dir, engine='xelatex'):
    """批量转换 LaTeX 文件"""
    os.makedirs(output_dir, exist_ok=True)

    tex_files = [
        f for f in os.listdir(tex_dir)
        if f.endswith('.tex')
    ]

    def convert(tex_file):
        tex_path = os.path.join(tex_dir, tex_file)
        try:
            pdf_path = latex_to_pdf(tex_path, engine, output_dir)
            return tex_file, pdf_path, None
        except Exception as e:
            return tex_file, None, str(e)

    with ThreadPoolExecutor(max_workers=4) as executor:
        results = list(executor.map(convert, tex_files))

    for tex_file, pdf_path, error in results:
        if pdf_path:
            print(f"成功: {tex_file} -> {pdf_path}")
        else:
            print(f"失败: {tex_file} - {error}")
```

### 从字符串生成 PDF

```python
import tempfile
import os

def latex_string_to_pdf(latex_content, output_path, engine='xelatex'):
    """从 LaTeX 字符串生成 PDF"""
    with tempfile.TemporaryDirectory() as temp_dir:
        # 写入临时文件
        tex_path = os.path.join(temp_dir, 'document.tex')
        with open(tex_path, 'w', encoding='utf-8') as f:
            f.write(latex_content)

        # 编译
        pdf_path = latex_to_pdf(tex_path, engine, temp_dir)

        # 复制到目标位置
        if pdf_path:
            import shutil
            shutil.copy(pdf_path, output_path)
            return output_path

    return None

# 使用
latex_code = r'''
\documentclass{article}
\usepackage[UTF8]{ctex}
\begin{document}
Hello, 世界！
\end{document}
'''

latex_string_to_pdf(latex_code, 'output.pdf')
```

## 常见问题

### 中文显示乱码

```latex
% 解决方案：使用 ctex 包
\documentclass[UTF8]{ctexart}
% 或
\documentclass{article}
\usepackage[UTF8]{ctex}
```

### 找不到字体

```latex
% 指定系统字体
\usepackage{fontspec}
\setmainfont{SimSun}
\setsansfont{SimHei}
\setmonofont{Consolas}
```

### 图片路径问题

```latex
% 设置图片搜索路径
\usepackage{graphicx}
\graphicspath{{images/}{figures/}}

% 使用相对路径
\includegraphics[width=0.8\textwidth]{./images/figure1.png}
```
