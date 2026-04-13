#!/usr/bin/env python3
"""
PDF Split Script - 拆分 PDF 文件

支持多种拆分模式：
- 按页数拆分（每 N 页一个文件）
- 按页范围拆分（提取指定页面）
- 提取单页

依赖: pypdf
"""

import argparse
import re
import sys
from pathlib import Path

try:
    from pypdf import PdfReader, PdfWriter
except ImportError:
    print("错误: 缺少 pypdf 库")
    print("请运行: pip install pypdf")
    sys.exit(1)


def parse_page_range(range_str: str, max_page: int) -> list[int]:
    """
    解析页码范围字符串。

    支持格式:
    - 单页: "5"
    - 范围: "1-5"
    - 多个: "1,3,5-7,10"

    Args:
        range_str: 页码范围字符串
        max_page: 最大页码

    Returns:
        list[int]: 页码列表（1-indexed）
    """
    pages = set()

    for part in range_str.split(','):
        part = part.strip()
        if '-' in part:
            start, end = part.split('-', 1)
            start = int(start.strip())
            end = int(end.strip())
            if start > end:
                start, end = end, start
            for p in range(start, end + 1):
                if 1 <= p <= max_page:
                    pages.add(p)
        else:
            p = int(part)
            if 1 <= p <= max_page:
                pages.add(p)

    return sorted(pages)


def split_by_pages(input_file: str, pages_per_file: int, output_pattern: str, verbose: bool = False) -> bool:
    """
    按固定页数拆分 PDF。

    Args:
        input_file: 输入 PDF 文件
        pages_per_file: 每个文件的页数
        output_pattern: 输出文件名模式（支持 {part} 占位符）
        verbose: 详细模式

    Returns:
        bool: 是否成功
    """
    try:
        reader = PdfReader(input_file)
        total_pages = len(reader.pages)

        if verbose:
            print(f"输入文件: {input_file}")
            print(f"总页数: {total_pages}")
            print(f"每文件页数: {pages_per_file}")

        part_num = 1
        start_page = 0

        while start_page < total_pages:
            writer = PdfWriter()
            end_page = min(start_page + pages_per_file, total_pages)

            for i in range(start_page, end_page):
                writer.add_page(reader.pages[i])

            # 生成输出文件名
            output_file = output_pattern.replace('{part}', f'{part_num:03d}')
            if '{part}' not in output_pattern:
                # 如果没有占位符，自动添加
                stem = Path(output_pattern).stem
                suffix = Path(output_pattern).suffix
                parent = Path(output_pattern).parent
                output_file = str(parent / f"{stem}_part{part_num:03d}{suffix}")

            Path(output_file).parent.mkdir(parents=True, exist_ok=True)

            with open(output_file, 'wb') as f:
                writer.write(f)

            if verbose:
                print(f"  创建: {output_file} (页 {start_page + 1}-{end_page})")

            part_num += 1
            start_page = end_page

        print(f"\n拆分完成! 共创建 {part_num - 1} 个文件")
        return True

    except Exception as e:
        print(f"错误: {e}")
        return False


def split_by_range(input_file: str, page_range: str, output_file: str, verbose: bool = False) -> bool:
    """
    按页码范围提取页面。

    Args:
        input_file: 输入 PDF 文件
        page_range: 页码范围
        output_file: 输出文件
        verbose: 详细模式

    Returns:
        bool: 是否成功
    """
    try:
        reader = PdfReader(input_file)
        total_pages = len(reader.pages)

        if verbose:
            print(f"输入文件: {input_file}")
            print(f"总页数: {total_pages}")

        pages = parse_page_range(page_range, total_pages)

        if not pages:
            print("错误: 没有有效的页码")
            return False

        if verbose:
            print(f"提取页码: {pages}")

        writer = PdfWriter()
        for page_num in pages:
            writer.add_page(reader.pages[page_num - 1])  # 转为 0-indexed

        Path(output_file).parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'wb') as f:
            writer.write(f)

        print(f"\n提取完成!")
        print(f"  提取页数: {len(pages)} 页")
        print(f"  输出文件: {output_file}")
        return True

    except Exception as e:
        print(f"错误: {e}")
        return False


def extract_single_pages(input_file: str, output_dir: str, verbose: bool = False) -> bool:
    """
    将每一页提取为单独的 PDF 文件。

    Args:
        input_file: 输入 PDF 文件
        output_dir: 输出目录
        verbose: 详细模式

    Returns:
        bool: 是否成功
    """
    try:
        reader = PdfReader(input_file)
        total_pages = len(reader.pages)

        if verbose:
            print(f"输入文件: {input_file}")
            print(f"总页数: {total_pages}")

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        input_stem = Path(input_file).stem

        for i in range(total_pages):
            writer = PdfWriter()
            writer.add_page(reader.pages[i])

            output_file = output_path / f"{input_stem}_page{i + 1:04d}.pdf"

            with open(output_file, 'wb') as f:
                writer.write(f)

            if verbose:
                print(f"  创建: {output_file}")

        print(f"\n拆分完成! 共创建 {total_pages} 个文件")
        print(f"  输出目录: {output_dir}")
        return True

    except Exception as e:
        print(f"错误: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description='拆分 PDF 文件',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
拆分模式:
  -p, --pages N       每 N 页拆分为一个文件
  -r, --range RANGE   提取指定页码范围
  -s, --single        每页拆分为单独文件

页码范围格式:
  单页: 5
  范围: 1-5
  多个: 1,3,5-7,10

示例:
  # 每 5 页拆分为一个文件
  %(prog)s input.pdf -p 5 -o output_{part}.pdf

  # 提取第 1-5 页和第 10 页
  %(prog)s input.pdf -r 1-5,10 -o extracted.pdf

  # 每页单独保存
  %(prog)s input.pdf -s -o ./pages/
'''
    )

    parser.add_argument(
        'input',
        help='输入 PDF 文件'
    )

    parser.add_argument(
        '-o', '--output',
        required=True,
        help='输出文件路径或目录'
    )

    parser.add_argument(
        '-p', '--pages',
        type=int,
        metavar='N',
        help='每 N 页拆分为一个文件'
    )

    parser.add_argument(
        '-r', '--range',
        metavar='RANGE',
        help='提取指定页码范围（如: 1-5,8,10-15）'
    )

    parser.add_argument(
        '-s', '--single',
        action='store_true',
        help='每页拆分为单独文件'
    )

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='显示详细处理信息'
    )

    args = parser.parse_args()

    # 检查输入文件
    if not Path(args.input).exists():
        print(f"错误: 文件不存在 - {args.input}")
        sys.exit(1)

    # 确定拆分模式
    modes = [args.pages, args.range, args.single].count(None)
    modes_selected = 3 - modes

    if modes_selected == 0:
        parser.error("请指定拆分模式: -p/--pages, -r/--range 或 -s/--single")

    if modes_selected > 1:
        parser.error("只能指定一种拆分模式")

    # 执行拆分
    success = False

    if args.pages:
        success = split_by_pages(args.input, args.pages, args.output, args.verbose)
    elif args.range:
        success = split_by_range(args.input, args.range, args.output, args.verbose)
    elif args.single:
        success = extract_single_pages(args.input, args.output, args.verbose)

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
