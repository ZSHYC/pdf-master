#!/usr/bin/env python3
"""
PDF Utilities - 公共工具模块

提供 PDF 处理脚本的公共功能：
- 页码范围解析
- 进度显示
- 批量文件处理
- 错误处理装饰器
"""

from __future__ import annotations

import glob
import os
import sys
import time
from pathlib import Path
from typing import Callable, Iterator, List, Optional, Set, TypeVar

T = TypeVar('T')


def parse_page_range(range_str: str, max_page: int) -> List[int]:
    """
    解析页码范围字符串为页码列表。

    支持格式:
        - 单页: "5"
        - 范围: "1-5"
        - 多个: "1,3,5-7,10"

    Args:
        range_str: 页码范围字符串
        max_page: 最大有效页码（PDF 总页数）

    Returns:
        排序后的页码列表（1-indexed）

    Raises:
        ValueError: 当页码范围格式无效时

    Examples:
        >>> parse_page_range("1-5", 10)
        [1, 2, 3, 4, 5]
        >>> parse_page_range("1,3,5-7", 10)
        [1, 3, 5, 6, 7]
    """
    pages: Set[int] = set()

    for part in range_str.split(','):
        part = part.strip()
        if not part:
            continue

        if '-' in part:
            start_str, end_str = part.split('-', 1)
            try:
                start = int(start_str.strip())
                end = int(end_str.strip())
            except ValueError:
                raise ValueError(f"无效的页码范围格式: '{part}'")

            if start > end:
                start, end = end, start

            for p in range(start, end + 1):
                if 1 <= p <= max_page:
                    pages.add(p)
        else:
            try:
                p = int(part)
            except ValueError:
                raise ValueError(f"无效的页码: '{part}'")

            if 1 <= p <= max_page:
                pages.add(p)

    return sorted(pages)


def parse_page_range_zero_indexed(range_str: str, total_pages: int) -> List[int]:
    """
    解析页码范围字符串为 0-indexed 页码列表。

    与 parse_page_range 类似，但返回 0-indexed 页码列表。

    Args:
        range_str: 页码范围字符串（用户输入为 1-indexed）
        total_pages: PDF 总页数

    Returns:
        0-indexed 页码列表

    Examples:
        >>> parse_page_range_zero_indexed("1-3", 10)
        [0, 1, 2]
    """
    one_indexed = parse_page_range(range_str, total_pages)
    return [p - 1 for p in one_indexed]


class ProgressReporter:
    """
    进度报告器，用于显示处理进度。

    Attributes:
        total: 总任务数
        current: 当前已完成任务数
        start_time: 开始时间
        desc: 任务描述

    Examples:
        >>> reporter = ProgressReporter(100, "Processing pages")
        >>> for i in range(100):
        ...     reporter.update(i + 1)
        ...     # do work
        >>> reporter.finish()
    """

    def __init__(self, total: int, desc: str = "Processing") -> None:
        """
        初始化进度报告器。

        Args:
            total: 总任务数
            desc: 任务描述（默认: "Processing"）
        """
        self.total = total
        self.current = 0
        self.start_time = time.time()
        self.desc = desc
        self._last_update = 0.0

    def update(self, current: int, message: Optional[str] = None) -> None:
        """
        更新进度显示。

        Args:
            current: 当前已完成任务数
            message: 可选的附加消息
        """
        self.current = current
        elapsed = time.time() - self.start_time

        # 限制更新频率（最多每 0.1 秒更新一次）
        if time.time() - self._last_update < 0.1 and current < self.total:
            return
        self._last_update = time.time()

        if self.total > 0:
            percent = (current / self.total) * 100
            bar_length = 30
            filled = int(bar_length * current / self.total)
            bar = '█' * filled + '░' * (bar_length - filled)

            # 计算 ETA
            if current > 0:
                eta = (elapsed / current) * (self.total - current)
                eta_str = self._format_time(eta)
            else:
                eta_str = "--:--"

            progress_line = f"\r{self.desc}: [{bar}] {percent:5.1f}% ({current}/{self.total}) ETA: {eta_str}"
        else:
            progress_line = f"\r{self.desc}: {current} items processed"

        if message:
            progress_line += f" - {message}"

        # 清除行尾并打印
        sys.stderr.write(progress_line + ' ' * 20)
        sys.stderr.flush()

    def _format_time(self, seconds: float) -> str:
        """格式化时间为 MM:SS 格式。"""
        if seconds < 0:
            return "--:--"
        minutes = int(seconds / 60)
        secs = int(seconds % 60)
        return f"{minutes:02d}:{secs:02d}"

    def finish(self, message: Optional[str] = None) -> None:
        """
        完成进度显示。

        Args:
            message: 可选的完成消息
        """
        self.update(self.total)
        elapsed = time.time() - self.start_time

        sys.stderr.write('\n')
        if message:
            sys.stderr.write(f"{message}\n")
        else:
            sys.stderr.write(f"Completed in {self._format_time(elapsed)}\n")
        sys.stderr.flush()


def expand_pdf_files(pattern: str) -> List[str]:
    """
    展开通配符或目录为 PDF 文件列表。

    Args:
        pattern: 文件路径、通配符模式或目录

    Returns:
        匹配的 PDF 文件列表（按名称排序）

    Examples:
        >>> expand_pdf_files("*.pdf")
        ['file1.pdf', 'file2.pdf']
        >>> expand_pdf_files("/path/to/pdfs/")
        ['/path/to/pdfs/doc1.pdf', '/path/to/pdfs/doc2.pdf']
    """
    pattern = os.path.expanduser(pattern)
    files: List[str] = []

    if os.path.isdir(pattern):
        # 目录：查找所有 PDF 文件
        files = sorted(glob.glob(os.path.join(pattern, "*.pdf")))
        files.extend(sorted(glob.glob(os.path.join(pattern, "*.PDF"))))
    else:
        # 通配符或具体文件
        files = sorted(glob.glob(pattern))

    return [f for f in files if f.lower().endswith('.pdf')]


def validate_pdf_file(file_path: str) -> Path:
    """
    验证 PDF 文件是否存在且可读。

    Args:
        file_path: PDF 文件路径

    Returns:
        Path 对象

    Raises:
        FileNotFoundError: 文件不存在
        ValueError: 文件不是 PDF 格式
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"文件不存在: {file_path}")

    if path.suffix.lower() != '.pdf':
        raise ValueError(f"文件不是 PDF 格式: {file_path}")

    return path


def safe_filename(name: str, max_length: int = 200) -> str:
    """
    生成安全的文件名，移除非法字符。

    Args:
        name: 原始文件名
        max_length: 最大长度限制

    Returns:
        安全的文件名
    """
    # Windows 非法字符
    illegal_chars = '<>:"/\|?*'
    for char in illegal_chars:
        name = name.replace(char, '_')

    # 移除控制字符
    name = ''.join(c for c in name if ord(c) >= 32)

    # 限制长度
    if len(name) > max_length:
        name = name[:max_length]

    return name.strip()


def print_error(message: str, suggestion: Optional[str] = None) -> None:
    """
    打印格式化的错误消息。

    Args:
        message: 错误消息
        suggestion: 可选的解决建议
    """
    print(f"错误: {message}", file=sys.stderr)
    if suggestion:
        print(f"建议: {suggestion}", file=sys.stderr)


def print_warning(message: str) -> None:
    """
    打印格式化的警告消息。

    Args:
        message: 警告消息
    """
    print(f"警告: {message}", file=sys.stderr)


def print_success(message: str) -> None:
    """
    打印格式化的成功消息。

    Args:
        message: 成功消息
    """
    print(f"✓ {message}", file=sys.stderr)
