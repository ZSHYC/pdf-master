#!/usr/bin/env python3
"""
PDF Redact Script - 敏感信息涂抹

支持：
- 永久删除 PDF 中的敏感文字
- 支持精确文字匹配
- 支持正则表达式匹配
- 多种涂抹样式

依赖: PyMuPDF (fitz)
"""

import argparse
import re
import sys
from pathlib import Path

try:
    import fitz  # PyMuPDF
except ImportError:
    print("错误: 缺少 PyMuPDF 库")
    print("请运行: pip install PyMuPDF")
    sys.exit(1)


def redact_pdf(
    input_file: str,
    output_file: str,
    patterns: list[str],
    is_regex: bool = False,
    case_sensitive: bool = False,
    fill_color: tuple[float, float, float] = (0, 0, 0),
    text_color: tuple[float, float, float] = (1, 1, 1),
    redact_style: str = 'blackout',
    pages: str | None = None,
    preview: bool = False,
    verbose: bool = False
) -> bool:
    """
    涂抹 PDF 中的敏感信息。

    Args:
        input_file: 输入 PDF 文件
        output_file: 输出 PDF 文件
        patterns: 要匹配的模式列表
        is_regex: 是否为正则表达式
        case_sensitive: 是否区分大小写
        fill_color: 填充颜色 (R, G, B) 范围 0-1
        text_color: 替换文字颜色 (R, G, B) 范围 0-1
        redact_style: 涂抹样式 (blackout, whiteout, redact, replace)
        pages: 要处理的页码范围
        preview: 预览模式（只显示将删除的内容，不实际删除）
        verbose: 详细模式

    Returns:
        bool: 是否成功
    """
    try:
        doc = fitz.open(input_file)
        total_pages = len(doc)

        if verbose:
            print(f"输入文件: {input_file}")
            print(f"总页数: {total_pages}")
            print(f"匹配模式: {patterns}")
            print(f"模式类型: {'正则表达式' if is_regex else '精确文字'}")
            print(f"区分大小写: {'是' if case_sensitive else '否'}")
            print(f"涂抹样式: {redact_style}")

        # 确定要处理的页面
        pages_to_process = set()
        if pages:
            def parse_range(s, max_p):
                result = set()
                for part in s.split(','):
                    part = part.strip()
                    if '-' in part:
                        start, end = part.split('-', 1)
                        start, end = int(start), int(end)
                        if start > end:
                            start, end = end, start
                        for p in range(start, end + 1):
                            if 1 <= p <= max_p:
                                result.add(p)
                    else:
                        p = int(part)
                        if 1 <= p <= max_p:
                            result.add(p)
                return result

            pages_to_process = parse_range(pages, total_pages)
        else:
            pages_to_process = set(range(1, total_pages + 1))

        total_matches = 0
        matches_detail = []

        # 处理每一页
        for page_num in range(1, total_pages + 1):
            if page_num not in pages_to_process:
                continue

            page = doc[page_num - 1]

            for pattern in patterns:
                # 搜索文本
                if is_regex:
                    # 正则表达式搜索
                    flags = 0 if case_sensitive else re.IGNORECASE
                    try:
                        regex = re.compile(pattern, flags)
                    except re.error as e:
                        print(f"警告: 无效的正则表达式 '{pattern}': {e}")
                        continue

                    # 获取页面文本
                    text_dict = page.get_text("dict")
                    for block in text_dict.get("blocks", []):
                        if block.get("type") != 0:  # 跳过非文本块
                            continue
                        for line in block.get("lines", []):
                            for span in line.get("spans", []):
                                text = span.get("text", "")
                                for match in regex.finditer(text):
                                    matched_text = match.group()
                                    # 搜索匹配文本的位置
                                    areas = page.search_for(matched_text)
                                    for area in areas:
                                        if redact_style == 'blackout':
                                            page.add_redact_annot(
                                                area,
                                                fill=fill_color,
                                                text=""
                                            )
                                        elif redact_style == 'whiteout':
                                            page.add_redact_annot(
                                                area,
                                                fill=(1, 1, 1),
                                                text=""
                                            )
                                        elif redact_style == 'redact':
                                            page.add_redact_annot(
                                                area,
                                                fill=fill_color,
                                                text="[REDACTED]",
                                                text_color=text_color
                                            )
                                        elif redact_style == 'replace':
                                            page.add_redact_annot(
                                                area,
                                                fill=fill_color,
                                                text="***",
                                                text_color=text_color
                                            )
                                        total_matches += 1
                                        matches_detail.append({
                                            'page': page_num,
                                            'text': matched_text,
                                            'rect': area
                                        })
                else:
                    # 精确文字搜索
                    text_to_find = pattern if case_sensitive else pattern.lower()
                    areas = page.search_for(text_to_find, quads=True)

                    for area in areas:
                        if redact_style == 'blackout':
                            page.add_redact_annot(
                                area,
                                fill=fill_color,
                                text=""
                            )
                        elif redact_style == 'whiteout':
                            page.add_redact_annot(
                                area,
                                fill=(1, 1, 1),
                                text=""
                            )
                        elif redact_style == 'redact':
                            page.add_redact_annot(
                                area,
                                fill=fill_color,
                                text="[REDACTED]",
                                text_color=text_color
                            )
                        elif redact_style == 'replace':
                            page.add_redact_annot(
                                area,
                                fill=fill_color,
                                text="***",
                                text_color=text_color
                            )
                        total_matches += 1
                        matches_detail.append({
                            'page': page_num,
                            'text': pattern,
                            'rect': area
                        })

        # 显示匹配详情
        if verbose and matches_detail:
            print(f"\n找到 {total_matches} 处匹配:")
            for detail in matches_detail[:20]:  # 只显示前 20 个
                print(f"  第 {detail['page']} 页: '{detail['text']}'")
            if len(matches_detail) > 20:
                print(f"  ... 还有 {len(matches_detail) - 20} 处")

        if preview:
            print(f"\n预览模式: 找到 {total_matches} 处将删除的内容")
            doc.close()
            return True

        if total_matches == 0:
            print("警告: 未找到匹配的内容")
            doc.close()
            return True

        # 应用涂抹
        for page_num in pages_to_process:
            page = doc[page_num - 1]
            page.apply_redactions()

        # 创建输出目录
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)

        # 保存文件
        doc.save(output_file, garbage=3, deflate=True)
        doc.close()

        print(f"\n涂抹完成!")
        print(f"  处理页数: {len(pages_to_process)}")
        print(f"  涂抹数量: {total_matches}")
        print(f"  输出文件: {output_file}")
        return True

    except Exception as e:
        print(f"错误: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description='涂抹 PDF 中的敏感信息',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
涂抹样式:
  blackout   黑色覆盖（默认）
  whiteout   白色覆盖
  redact     显示 [REDACTED] 标记
  replace    显示 *** 标记

匹配模式:
  -t, --text TEXT     精确匹配文字（可多次使用）
  -r, --regex PATTERN 正则表达式匹配（可多次使用）

常用正则表达式示例:
  邮箱:     -r '[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
  电话:     -r '\d{3,4}-\d{7,8}'
  手机:     -r '1[3-9]\d{9}'
  身份证:   -r '\d{17}[\dXx]'
  银行卡:   -r '\d{16,19}'
  信用卡:   -r '\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}'

示例:
  # 涂抹特定文字
  %(prog)s input.pdf -t "机密" -o redacted.pdf

  # 涂抹多个关键词
  %(prog)s input.pdf -t "密码" -t "账号" -o redacted.pdf

  # 使用正则表达式涂抹邮箱
  %(prog)s input.pdf -r '[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}' -o redacted.pdf

  # 涂抹身份证号
  %(prog)s input.pdf -r '\d{17}[\dXx]' --style redact -o redacted.pdf

  # 预览模式（查看将删除的内容）
  %(prog)s input.pdf -t "机密" --preview

  # 仅处理特定页面
  %(prog)s input.pdf -t "机密" -p 1-5 -o redacted.pdf
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

    # 匹配模式
    parser.add_argument(
        '-t', '--text',
        action='append',
        metavar='TEXT',
        help='精确匹配的文字（可多次使用）'
    )

    parser.add_argument(
        '-r', '--regex',
        action='append',
        metavar='PATTERN',
        help='正则表达式模式（可多次使用）'
    )

    parser.add_argument(
        '-i', '--ignore-case',
        action='store_true',
        help='忽略大小写'
    )

    parser.add_argument(
        '--style',
        choices=['blackout', 'whiteout', 'redact', 'replace'],
        default='blackout',
        help='涂抹样式（默认: blackout）'
    )

    parser.add_argument(
        '--fill-color',
        metavar='RGB',
        help='填充颜色，格式: R,G,B（范围 0-255，默认: 0,0,0 黑色）'
    )

    parser.add_argument(
        '--text-color',
        metavar='RGB',
        help='替换文字颜色，格式: R,G,B（范围 0-255，默认: 255,255,255 白色）'
    )

    parser.add_argument(
        '-p', '--pages',
        metavar='RANGE',
        help='要处理的页码范围（默认: 全部）'
    )

    parser.add_argument(
        '--preview',
        action='store_true',
        help='预览模式（只显示将删除的内容）'
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

    # 预览模式不需要输出文件
    if not args.preview and not args.output:
        print("错误: 请指定输出文件 (-o)")
        sys.exit(1)

    # 检查是否提供了匹配模式
    if not args.text and not args.regex:
        print("错误: 请指定至少一个匹配模式 (-t 或 -r)")
        sys.exit(1)

    # 收集所有模式
    patterns = []
    is_regex = False

    if args.text:
        patterns.extend(args.text)

    if args.regex:
        patterns.extend(args.regex)
        is_regex = True

    # 解析颜色
    fill_color = (0, 0, 0)  # 默认黑色
    if args.fill_color:
        try:
            r, g, b = map(int, args.fill_color.split(','))
            fill_color = (r / 255, g / 255, b / 255)
        except ValueError:
            print("错误: 无效的颜色格式，应为 R,G,B")
            sys.exit(1)

    text_color = (1, 1, 1)  # 默认白色
    if args.text_color:
        try:
            r, g, b = map(int, args.text_color.split(','))
            text_color = (r / 255, g / 255, b / 255)
        except ValueError:
            print("错误: 无效的颜色格式，应为 R,G,B")
            sys.exit(1)

    # 执行涂抹
    success = redact_pdf(
        args.input,
        args.output if args.output else '',
        patterns=patterns,
        is_regex=is_regex,
        case_sensitive=not args.ignore_case,
        fill_color=fill_color,
        text_color=text_color,
        redact_style=args.style,
        pages=args.pages,
        preview=args.preview,
        verbose=args.verbose
    )
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
