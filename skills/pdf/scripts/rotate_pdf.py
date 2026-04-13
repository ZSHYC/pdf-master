#!/usr/bin/env python3
"""
PDF Rotate Script - 旋转 PDF 页面

支持：
- 旋转所有页面
- 旋转指定页面
- 多种旋转角度（90°, 180°, 270°）

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


def rotate_pdf(
    input_file: str,
    output_file: str,
    angle: int,
    pages: str | None = None,
    verbose: bool = False
) -> bool:
    """
    旋转 PDF 页面。

    Args:
        input_file: 输入 PDF 文件
        output_file: 输出 PDF 文件
        angle: 旋转角度（90, 180, 270）
        pages: 要旋转的页码范围（None 表示全部）
        verbose: 详细模式

    Returns:
        bool: 是否成功
    """
    try:
        reader = PdfReader(input_file)
        writer = PdfWriter()
        total_pages = len(reader.pages)

        if verbose:
            print(f"输入文件: {input_file}")
            print(f"总页数: {total_pages}")
            print(f"旋转角度: {angle}°")

        # 确定要旋转的页面
        pages_to_rotate = set()
        if pages:
            pages_to_rotate = set(parse_page_range(pages, total_pages))
            if verbose:
                print(f"旋转页面: {sorted(pages_to_rotate)}")
        else:
            pages_to_rotate = set(range(1, total_pages + 1))
            if verbose:
                print("旋转页面: 全部")

        # 处理每一页
        rotated_count = 0
        for i, page in enumerate(reader.pages):
            page_num = i + 1

            if page_num in pages_to_rotate:
                # 旋转页面
                writer.add_page(page)
                writer.pages[-1].rotate(angle)
                rotated_count += 1
            else:
                # 保持原样
                writer.add_page(page)

        # 复制元数据
        if reader.metadata:
            writer.add_metadata(reader.metadata)

        # 写入输出文件
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'wb') as f:
            writer.write(f)

        print(f"\n旋转完成!")
        print(f"  旋转页数: {rotated_count} 页")
        print(f"  旋转角度: {angle}°")
        print(f"  输出文件: {output_file}")
        return True

    except Exception as e:
        print(f"错误: {e}")
        return False


def get_page_rotations(input_file: str) -> None:
    """
    显示 PDF 各页的当前旋转角度。

    Args:
        input_file: 输入 PDF 文件
    """
    try:
        reader = PdfReader(input_file)
        total_pages = len(reader.pages)

        print(f"文件: {input_file}")
        print(f"总页数: {total_pages}")
        print("\n各页旋转角度:")
        print("-" * 30)

        for i, page in enumerate(reader.pages):
            rotation = page.get('/Rotate', 0)
            print(f"  第 {i + 1:4d} 页: {rotation}°")

    except Exception as e:
        print(f"错误: {e}")


def main():
    parser = argparse.ArgumentParser(
        description='旋转 PDF 页面',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
旋转角度:
  90   顺时针旋转 90 度
  180  旋转 180 度
  270  逆时针旋转 90 度（或顺时针 270 度）

页码范围格式:
  单页: 5
  范围: 1-5
  多个: 1,3,5-7,10

示例:
  # 所有页面旋转 90 度
  %(prog)s input.pdf -a 90 -o rotated.pdf

  # 仅旋转第 1-3 页
  %(prog)s input.pdf -a 180 -p 1-3 -o rotated.pdf

  # 查看各页当前旋转角度
  %(prog)s input.pdf --info
'''
    )

    parser.add_argument(
        'input',
        help='输入 PDF 文件'
    )

    parser.add_argument(
        '-o', '--output',
        help='输出 PDF 文件'
    )

    parser.add_argument(
        '-a', '--angle',
        type=int,
        choices=[90, 180, 270],
        help='旋转角度（90, 180, 270）'
    )

    parser.add_argument(
        '-p', '--pages',
        metavar='RANGE',
        help='要旋转的页码范围（默认: 全部）'
    )

    parser.add_argument(
        '--info',
        action='store_true',
        help='显示各页当前旋转角度'
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

    # 信息模式
    if args.info:
        get_page_rotations(args.input)
        sys.exit(0)

    # 旋转模式需要输出文件和角度
    if not args.output:
        parser.error("旋转模式需要指定输出文件 (-o/--output)")

    if not args.angle:
        parser.error("旋转模式需要指定角度 (-a/--angle)")

    # 执行旋转
    success = rotate_pdf(args.input, args.output, args.angle, args.pages, args.verbose)
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
