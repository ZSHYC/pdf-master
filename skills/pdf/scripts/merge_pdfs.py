#!/usr/bin/env python3
"""
PDF Merge Script - 合并多个 PDF 文件为一个

使用 pypdf 库将多个 PDF 文件按顺序合并为一个 PDF 文件。

依赖: pypdf
"""

import argparse
import sys
from pathlib import Path

try:
    from pypdf import PdfReader, PdfWriter
except ImportError:
    print("错误: 缺少 pypdf 库")
    print("请运行: pip install pypdf")
    sys.exit(1)


def merge_pdfs(input_files: list[str], output_file: str, verbose: bool = False) -> bool:
    """
    合并多个 PDF 文件。

    Args:
        input_files: 输入 PDF 文件路径列表
        output_file: 输出 PDF 文件路径
        verbose: 是否显示详细信息

    Returns:
        bool: 合并是否成功
    """
    writer = PdfWriter()
    total_pages = 0

    # 验证所有输入文件存在
    for file_path in input_files:
        path = Path(file_path)
        if not path.exists():
            print(f"错误: 文件不存在 - {file_path}")
            return False
        if not path.suffix.lower() == '.pdf':
            print(f"警告: 文件可能不是 PDF 格式 - {file_path}")

    # 逐个添加 PDF
    for i, file_path in enumerate(input_files, 1):
        try:
            if verbose:
                print(f"[{i}/{len(input_files)}] 正在处理: {file_path}")

            reader = PdfReader(file_path)
            page_count = len(reader.pages)

            if verbose:
                print(f"    添加 {page_count} 页")

            for page in reader.pages:
                writer.add_page(page)

            total_pages += page_count

        except Exception as e:
            print(f"错误: 处理文件失败 - {file_path}")
            print(f"    原因: {e}")
            return False

    # 写入输出文件
    try:
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'wb') as f:
            writer.write(f)

        print(f"\n合并完成!")
        print(f"  输入文件: {len(input_files)} 个")
        print(f"  总页数: {total_pages} 页")
        print(f"  输出文件: {output_file}")
        return True

    except Exception as e:
        print(f"错误: 写入输出文件失败 - {output_file}")
        print(f"    原因: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description='合并多个 PDF 文件为一个',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例:
  %(prog)s file1.pdf file2.pdf file3.pdf -o merged.pdf
  %(prog)s part*.pdf -o combined.pdf -v
  %(prog)s --input-list files.txt -o output.pdf
'''
    )

    parser.add_argument(
        'files',
        nargs='*',
        help='要合并的 PDF 文件（按顺序）'
    )

    parser.add_argument(
        '-o', '--output',
        required=True,
        help='输出 PDF 文件路径'
    )

    parser.add_argument(
        '-l', '--input-list',
        help='包含文件列表的文本文件（每行一个文件路径）'
    )

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='显示详细处理信息'
    )

    args = parser.parse_args()

    # 获取输入文件列表
    input_files = []

    if args.input_list:
        # 从文件读取列表
        list_path = Path(args.input_list)
        if not list_path.exists():
            print(f"错误: 列表文件不存在 - {args.input_list}")
            sys.exit(1)

        with open(list_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    input_files.append(line)

    # 添加命令行指定的文件
    input_files.extend(args.files)

    if not input_files:
        parser.error("没有指定输入文件")

    # 执行合并
    success = merge_pdfs(input_files, args.output, args.verbose)
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
