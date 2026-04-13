#!/usr/bin/env python3
"""
PDF Encrypt Script - 加密 PDF 文件

支持：
- 设置用户密码（打开密码）
- 设置所有者密码（权限密码）
- 设置权限（打印、复制、编辑等）

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


def encrypt_pdf(
    input_file: str,
    output_file: str,
    user_password: str,
    owner_password: str | None = None,
    allow_print: bool = True,
    allow_copy: bool = True,
    allow_modify: bool = False,
    allow_annotate: bool = True,
    allow_form_filling: bool = True,
    allow_extract: bool = False,
    use_128bit: bool = True,
    verbose: bool = False
) -> bool:
    """
    加密 PDF 文件。

    Args:
        input_file: 输入 PDF 文件
        output_file: 输出 PDF 文件
        user_password: 用户密码（打开文档需要）
        owner_password: 所有者密码（修改权限需要）
        allow_print: 允许打印
        allow_copy: 允许复制文本和图像
        allow_modify: 允许修改文档
        allow_annotate: 允许添加注释
        allow_form_filling: 允许填写表单
        allow_extract: 允许提取内容
        use_128bit: 使用 128 位加密（更安全）
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
            print(f"用户密码: {'*' * len(user_password)}")
            if owner_password:
                print(f"所有者密码: {'*' * len(owner_password)}")

        # 复制所有页面
        for page in reader.pages:
            writer.add_page(page)

        # 复制元数据
        if reader.metadata:
            writer.add_metadata(reader.metadata)

        # 如果未指定所有者密码，使用用户密码
        if owner_password is None:
            owner_password = user_password

        # 构建权限
        permissions = 0
        if allow_print:
            permissions |= 0b000000000100  # Print
        if allow_modify:
            permissions |= 0b000000001000  # Modify
        if allow_copy:
            permissions |= 0b000000010000  # Copy
        if allow_annotate:
            permissions |= 0b000000100000  # Annotate
        if allow_form_filling:
            permissions |= 0b000010000000  # Fill forms
        if allow_extract:
            permissions |= 0b000100000000  # Extract

        if verbose:
            print(f"\n权限设置:")
            print(f"  打印: {'允许' if allow_print else '禁止'}")
            print(f"  复制: {'允许' if allow_copy else '禁止'}")
            print(f"  修改: {'允许' if allow_modify else '禁止'}")
            print(f"  注释: {'允许' if allow_annotate else '禁止'}")
            print(f"  填表: {'允许' if allow_form_filling else '禁止'}")
            print(f"  提取: {'允许' if allow_extract else '禁止'}")
            print(f"  加密强度: {'128位' if use_128bit else '40位'}")

        # 加密
        writer.encrypt(
            user_password=user_password,
            owner_password=owner_password,
            use_128bit=use_128bit,
            permissions=permissions
        )

        # 创建输出目录
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)

        # 写入文件
        with open(output_file, 'wb') as f:
            writer.write(f)

        print(f"\n加密完成!")
        print(f"  输出文件: {output_file}")
        return True

    except Exception as e:
        print(f"错误: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description='加密 PDF 文件',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
权限说明:
  用户密码: 打开文档需要的密码
  所有者密码: 修改权限需要的密码（可选，默认与用户密码相同）

权限选项:
  --allow-print      允许打印（默认启用）
  --no-print         禁止打印
  --allow-copy       允许复制（默认启用）
  --no-copy          禁止复制
  --allow-modify     允许修改（默认禁用）
  --no-modify        禁止修改
  --allow-annotate   允许注释（默认启用）
  --no-annotate      禁止注释
  --allow-fill       允许填表（默认启用）
  --no-fill          禁止填表
  --allow-extract    允许提取（默认禁用）
  --no-extract       禁止提取

加密强度:
  --128bit           使用 128 位 AES 加密（默认，更安全）
  --40bit            使用 40 位 RC4 加密（兼容性更好）

示例:
  # 设置用户密码
  %(prog)s input.pdf -p mypassword -o encrypted.pdf

  # 设置用户密码和所有者密码
  %(prog)s input.pdf -p userpass -P ownerpass -o encrypted.pdf

  # 禁止打印和复制
  %(prog)s input.pdf -p mypassword --no-print --no-copy -o encrypted.pdf

  # 只允许打印，禁止其他所有操作
  %(prog)s input.pdf -p mypassword --allow-print --no-copy --no-modify -o encrypted.pdf
'''
    )

    parser.add_argument(
        'input',
        help='输入 PDF 文件'
    )

    parser.add_argument(
        '-o', '--output',
        required=True,
        help='输出 PDF 文件'
    )

    parser.add_argument(
        '-p', '--password',
        required=True,
        metavar='PASS',
        help='用户密码（打开文档需要）'
    )

    parser.add_argument(
        '-P', '--owner-password',
        metavar='PASS',
        help='所有者密码（修改权限需要，默认与用户密码相同）'
    )

    # 权限选项 - 打印
    print_group = parser.add_mutually_exclusive_group()
    print_group.add_argument(
        '--allow-print',
        action='store_true',
        dest='allow_print',
        default=True,
        help=argparse.SUPPRESS
    )
    print_group.add_argument(
        '--no-print',
        action='store_false',
        dest='allow_print',
        help='禁止打印'
    )

    # 权限选项 - 复制
    copy_group = parser.add_mutually_exclusive_group()
    copy_group.add_argument(
        '--allow-copy',
        action='store_true',
        dest='allow_copy',
        default=True,
        help=argparse.SUPPRESS
    )
    copy_group.add_argument(
        '--no-copy',
        action='store_false',
        dest='allow_copy',
        help='禁止复制'
    )

    # 权限选项 - 修改
    modify_group = parser.add_mutually_exclusive_group()
    modify_group.add_argument(
        '--allow-modify',
        action='store_true',
        dest='allow_modify',
        default=False,
        help='允许修改文档'
    )
    modify_group.add_argument(
        '--no-modify',
        action='store_false',
        dest='allow_modify',
        help=argparse.SUPPRESS
    )

    # 权限选项 - 注释
    annotate_group = parser.add_mutually_exclusive_group()
    annotate_group.add_argument(
        '--allow-annotate',
        action='store_true',
        dest='allow_annotate',
        default=True,
        help=argparse.SUPPRESS
    )
    annotate_group.add_argument(
        '--no-annotate',
        action='store_false',
        dest='allow_annotate',
        help='禁止添加注释'
    )

    # 权限选项 - 填表
    fill_group = parser.add_mutually_exclusive_group()
    fill_group.add_argument(
        '--allow-fill',
        action='store_true',
        dest='allow_form_filling',
        default=True,
        help=argparse.SUPPRESS
    )
    fill_group.add_argument(
        '--no-fill',
        action='store_false',
        dest='allow_form_filling',
        help='禁止填写表单'
    )

    # 权限选项 - 提取
    extract_group = parser.add_mutually_exclusive_group()
    extract_group.add_argument(
        '--allow-extract',
        action='store_true',
        dest='allow_extract',
        default=False,
        help='允许提取内容'
    )
    extract_group.add_argument(
        '--no-extract',
        action='store_false',
        dest='allow_extract',
        help=argparse.SUPPRESS
    )

    # 加密强度
    encrypt_group = parser.add_mutually_exclusive_group()
    encrypt_group.add_argument(
        '--128bit',
        action='store_true',
        dest='use_128bit',
        default=True,
        help=argparse.SUPPRESS
    )
    encrypt_group.add_argument(
        '--40bit',
        action='store_false',
        dest='use_128bit',
        help='使用 40 位加密（兼容性更好）'
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

    # 检查密码不为空
    if not args.password:
        print("错误: 用户密码不能为空")
        sys.exit(1)

    # 执行加密
    success = encrypt_pdf(
        args.input,
        args.output,
        user_password=args.password,
        owner_password=args.owner_password,
        allow_print=args.allow_print,
        allow_copy=args.allow_copy,
        allow_modify=args.allow_modify,
        allow_annotate=args.allow_annotate,
        allow_form_filling=args.allow_form_filling,
        allow_extract=args.allow_extract,
        use_128bit=args.use_128bit,
        verbose=args.verbose
    )
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
