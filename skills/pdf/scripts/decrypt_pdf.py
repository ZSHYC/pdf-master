#!/usr/bin/env python3
"""
PDF Decrypt Script - 解密 PDF 文件

支持：
- 移除密码保护
- 支持用户密码和所有者密码

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


def is_encrypted(file_path: str) -> bool:
    """
    检查 PDF 是否加密。

    Args:
        file_path: PDF 文件路径

    Returns:
        bool: 是否加密
    """
    try:
        reader = PdfReader(file_path)
        return reader.is_encrypted
    except Exception:
        return False


def decrypt_pdf(
    input_file: str,
    output_file: str,
    password: str | None = None,
    verbose: bool = False
) -> bool:
    """
    解密 PDF 文件。

    Args:
        input_file: 输入 PDF 文件
        output_file: 输出 PDF 文件
        password: 密码（如果文档加密）
        verbose: 详细模式

    Returns:
        bool: 是否成功
    """
    try:
        reader = PdfReader(input_file)

        if verbose:
            print(f"输入文件: {input_file}")
            print(f"加密状态: {'是' if reader.is_encrypted else '否'}")

        # 检查是否加密
        if reader.is_encrypted:
            if not password:
                print("错误: 文档已加密，请提供密码")
                return False

            # 尝试解密
            if reader.decrypt(password) == 0:
                print("错误: 密码错误或解密失败")
                return False

            if verbose:
                print("解密状态: 成功")

        else:
            if verbose:
                print("文档未加密，将直接复制")

        writer = PdfWriter()
        total_pages = len(reader.pages)

        if verbose:
            print(f"总页数: {total_pages}")

        # 复制所有页面
        for i, page in enumerate(reader.pages):
            writer.add_page(page)
            if verbose and (i + 1) % 10 == 0:
                print(f"  处理进度: {i + 1}/{total_pages}")

        # 复制元数据
        if reader.metadata:
            writer.add_metadata(reader.metadata)

        # 创建输出目录
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)

        # 写入文件（不加密）
        with open(output_file, 'wb') as f:
            writer.write(f)

        print(f"\n解密完成!")
        print(f"  输出文件: {output_file}")
        return True

    except Exception as e:
        print(f"错误: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description='解密 PDF 文件',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
说明:
  此脚本用于移除 PDF 文件的密码保护。
  需要提供正确的密码才能解密。

  如果文档未加密，将直接复制到输出文件。

示例:
  # 解密文档
  %(prog)s encrypted.pdf -p mypassword -o decrypted.pdf

  # 解密并显示详细信息
  %(prog)s encrypted.pdf -p mypassword -o decrypted.pdf -v

  # 如果不确定文档是否加密，可以先检查
  %(prog)s document.pdf --check
'''
    )

    parser.add_argument(
        'input',
        help='输入 PDF 文件'
    )

    parser.add_argument(
        '-o', '--output',
        help='输出 PDF 文件（解密时必需）'
    )

    parser.add_argument(
        '-p', '--password',
        metavar='PASS',
        help='密码'
    )

    parser.add_argument(
        '--check',
        action='store_true',
        help='仅检查文档是否加密，不解密'
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

    # 仅检查加密状态
    if args.check:
        encrypted = is_encrypted(args.input)
        print(f"文件: {args.input}")
        print(f"加密状态: {'已加密' if encrypted else '未加密'}")
        if encrypted:
            print("\n提示: 使用 -p 参数提供密码进行解密")
        sys.exit(0)

    # 解密需要输出文件
    if not args.output:
        print("错误: 请指定输出文件 (-o)")
        sys.exit(1)

    # 检查是否需要密码
    reader = PdfReader(args.input)
    if reader.is_encrypted and not args.password:
        print("错误: 文档已加密，请提供密码 (-p)")
        sys.exit(1)

    # 执行解密
    success = decrypt_pdf(
        args.input,
        args.output,
        password=args.password,
        verbose=args.verbose
    )
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
