#!/usr/bin/env python3
"""
PDF Annotations Management Script - PDF 注释管理

支持：
- 提取所有注释
- 添加注释（文本、高亮、下划线、删除线）
- 删除注释
- 按类型/作者筛选

依赖: pypdf
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    from pypdf import PdfReader, PdfWriter
    from pypdf.generic import DictionaryObject, ArrayObject, NameObject, NumberObject, TextStringObject
except ImportError:
    print("错误: 缺少 pypdf 库")
    print("请运行: pip install pypdf")
    sys.exit(1)


# ============================================================
# 注释数据类
# ============================================================

@dataclass
class PDFAnnotation:
    """PDF 注释信息"""
    page: int  # 0-indexed
    annot_type: str  # Text, Highlight, Underline, StrikeOut, etc.
    rect: Tuple[float, float, float, float]
    contents: str = ""
    author: str = ""
    modified: Optional[str] = None
    color: Optional[Tuple[float, float, float]] = None
    annotation_index: int = 0

    def to_dict(self) -> Dict[str, Any]:
        result = {
            "page": self.page + 1,
            "type": self.annot_type,
            "rect": list(self.rect),
            "contents": self.contents,
            "author": self.author,
        }
        if self.modified:
            result["modified"] = self.modified
        if self.color:
            result["color"] = list(self.color)
        return result


@dataclass
class AnnotationExtractionResult:
    """注释提取结果"""
    file_path: str
    total_annotations: int
    by_type: Dict[str, int] = field(default_factory=dict)
    by_author: Dict[str, int] = field(default_factory=dict)
    annotations: List[PDFAnnotation] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "file_path": self.file_path,
            "total_annotations": self.total_annotations,
            "by_type": self.by_type,
            "by_author": self.by_author,
            "annotations": [a.to_dict() for a in self.annotations]
        }


# ============================================================
# 注释提取
# ============================================================

def extract_annotations(
    pdf_path: str,
    filter_type: Optional[str] = None,
    filter_author: Optional[str] = None
) -> AnnotationExtractionResult:
    """提取 PDF 中所有注释.

    Args:
        pdf_path: PDF 文件路径
        filter_type: 按类型筛选
        filter_author: 按作者筛选

    Returns:
        AnnotationExtractionResult
    """
    reader = PdfReader(pdf_path)
    result = AnnotationExtractionResult(
        file_path=pdf_path,
        total_annotations=0,
        by_type={},
        by_author={}
    )

    for page_num, page in enumerate(reader.pages):
        try:
            page_obj = page.get_object() if hasattr(page, 'get_object') else page

            if "/Annots" not in page_obj:
                continue

            annots = page_obj["/Annots"]
            for annot_idx, annot in enumerate(annots):
                try:
                    annot_obj = annot.get_object() if hasattr(annot, 'get_object') else annot

                    if "/Subtype" not in annot_obj:
                        continue

                    # Get annotation type
                    annot_type = str(annot_obj["/Subtype"]).replace("/", "")

                    # Skip link annotations (handled by links.py)
                    if annot_type == "Link":
                        continue

                    # Apply type filter
                    if filter_type and annot_type.lower() != filter_type.lower():
                        continue

                    # Get rectangle
                    rect = annot_obj.get("/Rect", [0, 0, 0, 0])
                    rect_tuple = (float(rect[0]), float(rect[1]), float(rect[2]), float(rect[3]))

                    # Get contents
                    contents = str(annot_obj.get("/Contents", ""))

                    # Get author
                    author = str(annot_obj.get("/T", ""))  # /T is title/author

                    # Apply author filter
                    if filter_author and filter_author.lower() not in author.lower():
                        continue

                    # Get modification date
                    modified = None
                    if "/M" in annot_obj:
                        modified = str(annot_obj["/M"])

                    # Get color
                    color = None
                    if "/C" in annot_obj:
                        c = annot_obj["/C"]
                        if isinstance(c, list) and len(c) == 3:
                            color = (float(c[0]), float(c[1]), float(c[2]))

                    annotation = PDFAnnotation(
                        page=page_num,
                        annot_type=annot_type,
                        rect=rect_tuple,
                        contents=contents,
                        author=author,
                        modified=modified,
                        color=color,
                        annotation_index=annot_idx
                    )

                    result.annotations.append(annotation)
                    result.total_annotations += 1

                    # Count by type
                    result.by_type[annot_type] = result.by_type.get(annot_type, 0) + 1

                    # Count by author
                    author_key = author if author else "Unknown"
                    result.by_author[author_key] = result.by_author.get(author_key, 0) + 1

                except Exception:
                    continue

        except Exception:
            continue

    return result


def list_annotations(
    pdf_path: str,
    output_format: str = "text",
    filter_type: Optional[str] = None,
    filter_author: Optional[str] = None
) -> str:
    """列出 PDF 中所有注释.

    Args:
        pdf_path: PDF 文件路径
        output_format: 输出格式 (text/json)
        filter_type: 按类型筛选
        filter_author: 按作者筛选

    Returns:
        格式化的注释列表
    """
    result = extract_annotations(pdf_path, filter_type, filter_author)

    if output_format == "json":
        return json.dumps(result.to_dict(), indent=2, ensure_ascii=False)

    lines = [
        f"Annotations in {pdf_path}:",
        f"  Total: {result.total_annotations}",
        ""
    ]

    if result.by_type:
        lines.append("  By Type:")
        for t, count in sorted(result.by_type.items()):
            lines.append(f"    {t}: {count}")
        lines.append("")

    if result.by_author:
        lines.append("  By Author:")
        for author, count in sorted(result.by_author.items()):
            lines.append(f"    {author}: {count}")
        lines.append("")

    if not result.annotations:
        lines.append("  (No annotations found)")
    else:
        lines.append("  Details:")
        for annot in result.annotations:
            page_str = f"Page {annot.page + 1}"
            type_str = annot.annot_type
            rect_str = f"[{annot.rect[0]:.1f}, {annot.rect[1]:.1f}, {annot.rect[2]:.1f}, {annot.rect[3]:.1f}]"
            lines.append(f"    [{type_str}] {page_str} {rect_str}")
            if annot.contents:
                # Truncate long contents
                contents_preview = annot.contents[:100] + "..." if len(annot.contents) > 100 else annot.contents
                contents_preview = contents_preview.replace("\n", " ")
                lines.append(f"      Contents: {contents_preview}")
            if annot.author:
                lines.append(f"      Author: {annot.author}")

    return "\n".join(lines)


# ============================================================
# 注释添加
# ============================================================

def add_text_annotation(
    pdf_path: str,
    output_path: str,
    page: int,
    x: float,
    y: float,
    contents: str,
    author: str = "",
    color: Optional[Tuple[float, float, float]] = None
) -> bool:
    """添加文本注释（便签）.

    Args:
        pdf_path: 输入 PDF 路径
        output_path: 输出 PDF 路径
        page: 页码（1-indexed）
        x: X 坐标
        y: Y 坐标
        contents: 注释内容
        author: 作者
        color: RGB 颜色

    Returns:
        是否成功
    """
    reader = PdfReader(pdf_path)
    writer = PdfWriter()

    # Copy all pages
    for page_obj in reader.pages:
        writer.add_page(page_obj)

    # Get the target page
    page_num = page - 1
    if page_num < 0 or page_num >= len(reader.pages):
        print(f"错误: 页码 {page} 超出范围 (1-{len(reader.pages)})")
        return False

    # Create text annotation
    annot = DictionaryObject()
    annot[NameObject("/Type")] = NameObject("/Annot")
    annot[NameObject("/Subtype")] = NameObject("/Text")

    # Set rectangle (typical note icon is about 20x20)
    rect = ArrayObject([
        NumberObject(x),
        NumberObject(y),
        NumberObject(x + 20),
        NumberObject(y + 20)
    ])
    annot[NameObject("/Rect")] = rect

    # Set contents
    annot[NameObject("/Contents")] = TextStringObject(contents)

    # Set author
    if author:
        annot[NameObject("/T")] = TextStringObject(author)

    # Set color
    if color:
        annot[NameObject("/C")] = ArrayObject([
            NumberObject(color[0]),
            NumberObject(color[1]),
            NumberObject(color[2])
        ])

    # Set modification date
    annot[NameObject("/M")] = TextStringObject(datetime.now().strftime("D:%Y%m%d%H%M%S"))

    # Add annotation to page
    writer_page = writer.pages[page_num]
    if "/Annots" not in writer_page:
        writer_page[NameObject("/Annots")] = ArrayObject()
    writer_page["/Annots"].append(annot)

    # Write output
    with open(output_path, "wb") as f:
        writer.write(f)

    return True


def add_highlight_annotation(
    pdf_path: str,
    output_path: str,
    page: int,
    rect: Tuple[float, float, float, float],
    contents: str = "",
    author: str = "",
    color: Tuple[float, float, float] = (1, 1, 0)  # Yellow default
) -> bool:
    """添加高亮注释.

    Args:
        pdf_path: 输入 PDF 路径
        output_path: 输出 PDF 路径
        page: 页码（1-indexed）
        rect: 高亮区域 (x1, y1, x2, y2)
        contents: 注释内容
        author: 作者
        color: RGB 颜色

    Returns:
        是否成功
    """
    reader = PdfReader(pdf_path)
    writer = PdfWriter()

    # Copy all pages
    for page_obj in reader.pages:
        writer.add_page(page_obj)

    # Get the target page
    page_num = page - 1
    if page_num < 0 or page_num >= len(reader.pages):
        print(f"错误: 页码 {page} 超出范围 (1-{len(reader.pages)})")
        return False

    # Create highlight annotation
    annot = DictionaryObject()
    annot[NameObject("/Type")] = NameObject("/Annot")
    annot[NameObject("/Subtype")] = NameObject("/Highlight")

    # Set rectangle
    annot[NameObject("/Rect")] = ArrayObject([
        NumberObject(rect[0]),
        NumberObject(rect[1]),
        NumberObject(rect[2]),
        NumberObject(rect[3])
    ])

    # Set contents
    if contents:
        annot[NameObject("/Contents")] = TextStringObject(contents)

    # Set author
    if author:
        annot[NameObject("/T")] = TextStringObject(author)

    # Set color
    annot[NameObject("/C")] = ArrayObject([
        NumberObject(color[0]),
        NumberObject(color[1]),
        NumberObject(color[2])
    ])

    # Set modification date
    annot[NameObject("/M")] = TextStringObject(datetime.now().strftime("D:%Y%m%d%H%M%S"))

    # Add annotation to page
    writer_page = writer.pages[page_num]
    if "/Annots" not in writer_page:
        writer_page[NameObject("/Annots")] = ArrayObject()
    writer_page["/Annots"].append(annot)

    # Write output
    with open(output_path, "wb") as f:
        writer.write(f)

    return True


# ============================================================
# 注释删除
# ============================================================

def remove_annotations(
    pdf_path: str,
    output_path: str,
    filter_type: Optional[str] = None,
    filter_author: Optional[str] = None,
    remove_all: bool = False
) -> int:
    """删除 PDF 注释.

    Args:
        pdf_path: 输入 PDF 路径
        output_path: 输出 PDF 路径
        filter_type: 按类型删除
        filter_author: 按作者删除
        remove_all: 删除所有注释

    Returns:
        删除的注释数量
    """
    reader = PdfReader(pdf_path)
    writer = PdfWriter()

    removed_count = 0

    for page_num, page in enumerate(reader.pages):
        # Add page to writer
        writer.add_page(page)

        # Get annotations
        writer_page = writer.pages[page_num]
        if "/Annots" not in writer_page:
            continue

        new_annots = ArrayObject()

        for annot in writer_page["/Annots"]:
            try:
                annot_obj = annot.get_object() if hasattr(annot, 'get_object') else annot

                # Determine if we should remove
                should_remove = False

                if remove_all:
                    # Remove all except Links
                    if "/Subtype" in annot_obj and annot_obj["/Subtype"] != "/Link":
                        should_remove = True
                elif filter_type:
                    if "/Subtype" in annot_obj:
                        annot_type = str(annot_obj["/Subtype"]).replace("/", "")
                        if annot_type.lower() == filter_type.lower():
                            should_remove = True
                elif filter_author:
                    if "/T" in annot_obj:
                        author = str(annot_obj["/T"])
                        if filter_author.lower() in author.lower():
                            should_remove = True

                if should_remove:
                    removed_count += 1
                else:
                    new_annots.append(annot)

            except Exception:
                new_annots.append(annot)

        # Update annotations
        if new_annots:
            writer_page[NameObject("/Annots")] = new_annots
        else:
            if "/Annots" in writer_page:
                del writer_page["/Annots"]

    # Write output
    with open(output_path, "wb") as f:
        writer.write(f)

    return removed_count


# ============================================================
# 主函数
# ============================================================

def main() -> int:
    """主入口"""
    parser = argparse.ArgumentParser(
        description="PDF 注释管理工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 列出所有注释
  %(prog)s list document.pdf

  # 按类型筛选
  %(prog)s list document.pdf --type Highlight

  # 按作者筛选
  %(prog)s list document.pdf --author "John"

  # 输出 JSON 格式
  %(prog)s list document.pdf --json

  # 添加文本注释
  %(prog)s add document.pdf -o output.pdf --page 1 --pos 100,100 --contents "重要内容"

  # 添加高亮
  %(prog)s add document.pdf -o output.pdf --page 1 --highlight --rect "100,100,200,120"

  # 删除所有注释
  %(prog)s remove document.pdf -o output.pdf --all

  # 删除特定类型
  %(prog)s remove document.pdf -o output.pdf --type Text
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="命令")

    # List command
    list_parser = subparsers.add_parser("list", help="列出注释")
    list_parser.add_argument("input", help="输入 PDF 文件")
    list_parser.add_argument("--type", help="按类型筛选")
    list_parser.add_argument("--author", help="按作者筛选")
    list_parser.add_argument("--json", action="store_true", help="输出 JSON 格式")

    # Add command
    add_parser = subparsers.add_parser("add", help="添加注释")
    add_parser.add_argument("input", help="输入 PDF 文件")
    add_parser.add_argument("-o", "--output", required=True, help="输出 PDF 文件")
    add_parser.add_argument("--page", type=int, required=True, help="页码 (1-indexed)")
    add_parser.add_argument("--pos", help="文本注释位置 (x,y)")
    add_parser.add_argument("--rect", help="高亮区域 (x1,y1,x2,y2)")
    add_parser.add_argument("--highlight", action="store_true", help="添加高亮注释")
    add_parser.add_argument("--underline", action="store_true", help="添加下划线注释")
    add_parser.add_argument("--strikeout", action="store_true", help="添加删除线注释")
    add_parser.add_argument("--contents", default="", help="注释内容")
    add_parser.add_argument("--author", default="", help="作者")
    add_parser.add_argument("--color", help="RGB 颜色 (如: 1,1,0 表示黄色)")

    # Remove command
    remove_parser = subparsers.add_parser("remove", help="删除注释")
    remove_parser.add_argument("input", help="输入 PDF 文件")
    remove_parser.add_argument("-o", "--output", required=True, help="输出 PDF 文件")
    remove_parser.add_argument("--all", action="store_true", help="删除所有注释")
    remove_parser.add_argument("--type", help="按类型删除")
    remove_parser.add_argument("--author", help="按作者删除")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # Execute command
    if args.command == "list":
        result = list_annotations(
            args.input,
            "json" if args.json else "text",
            args.type,
            args.author
        )
        print(result)

    elif args.command == "add":
        # Parse color
        color = None
        if args.color:
            try:
                parts = [float(x.strip()) for x in args.color.split(",")]
                if len(parts) == 3:
                    color = tuple(parts)
            except Exception:
                print("错误: 颜色格式无效，使用 R,G,B 格式 (如: 1,1,0)")
                return 1

        if args.highlight or args.underline or args.strikeout:
            # Add markup annotation
            if not args.rect:
                print("错误: 需要 --rect 指定区域")
                return 1
            try:
                rect_parts = [float(x.strip()) for x in args.rect.split(",")]
                if len(rect_parts) != 4:
                    raise ValueError("Invalid rect")
                rect = tuple(rect_parts)
            except Exception:
                print("错误: rect 格式无效，使用 x1,y1,x2,y2 格式")
                return 1

            # TODO: Support underline and strikeout
            success = add_highlight_annotation(
                args.input,
                args.output,
                args.page,
                rect,
                args.contents,
                args.author,
                color or (1, 1, 0)
            )
        elif args.pos:
            # Add text annotation
            try:
                pos_parts = [float(x.strip()) for x in args.pos.split(",")]
                if len(pos_parts) != 2:
                    raise ValueError("Invalid pos")
                x, y = pos_parts
            except Exception:
                print("错误: pos 格式无效，使用 x,y 格式")
                return 1

            success = add_text_annotation(
                args.input,
                args.output,
                args.page,
                x,
                y,
                args.contents,
                args.author,
                color
            )
        else:
            print("错误: 需要 --pos 或 --highlight/--underline/--strikeout")
            return 1

        if success:
            print(f"成功: 注释已添加，输出到 {args.output}")
        else:
            print("失败: 无法添加注释")
            return 1

    elif args.command == "remove":
        if not (args.all or args.type or args.author):
            print("错误: 需要指定 --all, --type 或 --author")
            return 1

        count = remove_annotations(
            args.input,
            args.output,
            args.type,
            args.author,
            args.all
        )
        print(f"成功: 已删除 {count} 个注释，输出到 {args.output}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
