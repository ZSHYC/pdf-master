#!/usr/bin/env python3
"""
PDF Watermark Script - 给 PDF 添加水印

支持：
- 文本水印
- 图片水印
- 自定义位置、透明度、角度

依赖: pypdf
"""

import argparse
import sys
from pathlib import Path

try:
    from pypdf import PdfReader, PdfWriter, Transformation
    from pypdf.generic import NameObject, NumberObject
except ImportError:
    print("错误: 缺少 pypdf 库")
    print("请运行: pip install pypdf")
    sys.exit(1)

# 尝试导入 PIL（可选依赖，用于文本水印）
try:
    from PIL import Image, ImageDraw, ImageFont
    HAS_PIL = True
except ImportError:
    HAS_PIL = False


def create_text_watermark(
    text: str,
    font_size: int = 50,
    font_color: tuple[int, int, int, int] = (128, 128, 128, 128),
    angle: float = 45,
    page_width: int = 595,
    page_height: int = 842
) -> str:
    """
    创建文本水印图片。

    Args:
        text: 水印文字
        font_size: 字体大小
        font_color: 字体颜色 (R, G, B, A)
        angle: 旋转角度
        page_width: 页面宽度
        page_height: 页面高度

    Returns:
        str: 临时图片文件路径
    """
    if not HAS_PIL:
        raise RuntimeError("创建文本水印需要 PIL 库，请运行: pip install Pillow")

    import tempfile

    # 创建透明背景图片
    img_width = max(page_width, int(len(text) * font_size * 0.6))
    img_height = max(page_height, int(font_size * 2))

    img = Image.new('RGBA', (img_width, img_height), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)

    # 尝试使用系统字体
    try:
        # Windows
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        try:
            # macOS
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", font_size)
        except:
            try:
                # Linux
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", font_size)
            except:
                # 使用默认字体
                font = ImageFont.load_default()

    # 计算文字位置（居中）
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (img_width - text_width) // 2
    y = (img_height - text_height) // 2

    # 绘制文字
    draw.text((x, y), text, font=font, fill=font_color)

    # 旋转
    img = img.rotate(angle, expand=True, fillcolor=(255, 255, 255, 0))

    # 保存临时文件
    temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
    img.save(temp_file.name, 'PNG')
    temp_file.close()

    return temp_file.name


def add_watermark(
    input_file: str,
    output_file: str,
    watermark_file: str | None = None,
    watermark_text: str | None = None,
    opacity: float = 0.3,
    position: str = 'center',
    angle: float = 45,
    font_size: int = 50,
    pages: str | None = None,
    verbose: bool = False
) -> bool:
    """
    给 PDF 添加水印。

    Args:
        input_file: 输入 PDF 文件
        output_file: 输出 PDF 文件
        watermark_file: 水印图片文件
        watermark_text: 水印文字
        opacity: 透明度 (0-1)
        position: 位置 (center, diagonal, top-left, etc.)
        angle: 文本水印角度
        font_size: 文本水印字体大小
        pages: 要添加水印的页码范围
        verbose: 详细模式

    Returns:
        bool: 是否成功
    """
    temp_watermark = None

    try:
        reader = PdfReader(input_file)
        writer = PdfWriter()
        total_pages = len(reader.pages)

        if verbose:
            print(f"输入文件: {input_file}")
            print(f"总页数: {total_pages}")

        # 确定水印文件
        if watermark_file:
            wm_file = watermark_file
            if verbose:
                print(f"水印图片: {watermark_file}")
        elif watermark_text:
            if verbose:
                print(f"水印文字: {watermark_text}")
                print(f"字体大小: {font_size}")
                print(f"旋转角度: {angle}°")

            # 获取第一页尺寸作为参考
            first_page = reader.pages[0]
            page_width = int(first_page.mediabox.width)
            page_height = int(first_page.mediabox.height)

            # 创建文本水印图片
            alpha = int(opacity * 255)
            temp_watermark = create_text_watermark(
                watermark_text,
                font_size=font_size,
                font_color=(128, 128, 128, alpha),
                angle=angle,
                page_width=page_width,
                page_height=page_height
            )
            wm_file = temp_watermark
            # 文本水印创建的是 PNG 文件，需要转换为 PDF
            is_image_watermark = True
        else:
            print("错误: 请指定水印图片或水印文字")
            return False

        # 读取水印
        # 如果是图片文件（PNG/JPG），需要先转换为 PDF
        if wm_file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
            # 使用 reportlab 将图片转换为 PDF
            from reportlab.lib.pagesizes import letter
            from reportlab.pdfgen import canvas
            import tempfile

            # 获取图片尺寸
            img = Image.open(wm_file)
            img_width, img_height = img.size
            img.close()

            # 创建临时 PDF 文件
            temp_pdf = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
            c = canvas.Canvas(temp_pdf.name, pagesize=(img_width, img_height))
            c.drawImage(wm_file, 0, 0, width=img_width, height=img_height)
            c.save()
            wm_pdf_file = temp_pdf.name
            temp_pdf.close()
        else:
            wm_pdf_file = wm_file

        wm_reader = PdfReader(wm_pdf_file)
        wm_page = wm_reader.pages[0]

        # 确定要添加水印的页面
        pages_to_watermark = set()
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

            pages_to_watermark = parse_range(pages, total_pages)
        else:
            pages_to_watermark = set(range(1, total_pages + 1))

        if verbose:
            if pages:
                print(f"添加水印页面: {sorted(pages_to_watermark)}")
            else:
                print("添加水印页面: 全部")
            print(f"透明度: {opacity}")
            print(f"位置: {position}")

        # 处理每一页
        watermarked_count = 0
        for i, page in enumerate(reader.pages):
            page_num = i + 1

            if page_num in pages_to_watermark:
                # 计算水印位置
                page_width = float(page.mediabox.width)
                page_height = float(page.mediabox.height)
                wm_width = float(wm_page.mediabox.width)
                wm_height = float(wm_page.mediabox.height)

                # 缩放水印
                scale = min(page_width / wm_width, page_height / wm_height) * 0.5
                wm_page.scale(scale, scale)

                # 计算位置偏移
                positions = {
                    'center': ((page_width - wm_width * scale) / 2,
                               (page_height - wm_height * scale) / 2),
                    'top-left': (50, page_height - wm_height * scale - 50),
                    'top-right': (page_width - wm_width * scale - 50,
                                  page_height - wm_height * scale - 50),
                    'bottom-left': (50, 50),
                    'bottom-right': (page_width - wm_width * scale - 50, 50),
                }

                x, y = positions.get(position, positions['center'])

                # 添加水印
                page.merge_transformed_page(
                    wm_page,
                    Transformation().translate(x, y),
                    over=True
                )
                watermarked_count += 1

            writer.add_page(page)

        # 复制元数据
        if reader.metadata:
            writer.add_metadata(reader.metadata)

        # 写入输出文件
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'wb') as f:
            writer.write(f)

        print(f"\n添加水印完成!")
        print(f"  处理页数: {watermarked_count} 页")
        print(f"  输出文件: {output_file}")
        return True

    except Exception as e:
        print(f"错误: {e}")
        return False

    finally:
        # 清理临时文件
        if temp_watermark:
            try:
                Path(temp_watermark).unlink()
            except:
                pass


def main():
    parser = argparse.ArgumentParser(
        description='给 PDF 添加水印',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
水印类型:
  -i, --image FILE    使用图片作为水印
  -t, --text TEXT     使用文字作为水印

位置选项:
  center      居中（默认）
  diagonal    对角线
  top-left    左上角
  top-right   右上角
  bottom-left 左下角
  bottom-right 右下角

示例:
  # 添加图片水印
  %(prog)s input.pdf -i logo.png -o watermarked.pdf

  # 添加文字水印
  %(prog)s input.pdf -t "机密文件" -o watermarked.pdf

  # 自定义透明度和位置
  %(prog)s input.pdf -t "DRAFT" --opacity 0.5 --position diagonal -o output.pdf

  # 仅给指定页面添加水印
  %(prog)s input.pdf -t "SAMPLE" -p 1-5 -o output.pdf
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

    # 水印类型（互斥）
    watermark_group = parser.add_mutually_exclusive_group(required=True)
    watermark_group.add_argument(
        '-i', '--image',
        metavar='FILE',
        help='水印图片文件'
    )
    watermark_group.add_argument(
        '-t', '--text',
        metavar='TEXT',
        help='水印文字'
    )

    parser.add_argument(
        '--opacity',
        type=float,
        default=0.3,
        help='透明度 (0-1, 默认: 0.3)'
    )

    parser.add_argument(
        '--position',
        choices=['center', 'diagonal', 'top-left', 'top-right', 'bottom-left', 'bottom-right'],
        default='center',
        help='水印位置（默认: center）'
    )

    parser.add_argument(
        '--angle',
        type=float,
        default=45,
        help='文字水印旋转角度（默认: 45）'
    )

    parser.add_argument(
        '--font-size',
        type=int,
        default=50,
        help='文字水印字体大小（默认: 50）'
    )

    parser.add_argument(
        '-p', '--pages',
        metavar='RANGE',
        help='要添加水印的页码范围（默认: 全部）'
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

    # 检查水印图片
    if args.image and not Path(args.image).exists():
        print(f"错误: 水印图片不存在 - {args.image}")
        sys.exit(1)

    # 检查透明度范围
    if not 0 <= args.opacity <= 1:
        print("错误: 透明度必须在 0-1 之间")
        sys.exit(1)

    # 文本水印需要 PIL
    if args.text and not HAS_PIL:
        print("错误: 使用文字水印需要 Pillow 库")
        print("请运行: pip install Pillow")
        sys.exit(1)

    # 执行添加水印
    success = add_watermark(
        args.input,
        args.output,
        watermark_file=args.image,
        watermark_text=args.text,
        opacity=args.opacity,
        position=args.position,
        angle=args.angle,
        font_size=args.font_size,
        pages=args.pages,
        verbose=args.verbose
    )
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
