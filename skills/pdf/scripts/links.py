#!/usr/bin/env python3
"""
PDF Links Management Script - PDF 链接管理

支持：
- 提取所有链接
- 添加链接（内部/外部）
- 删除链接
- 更新链接

依赖: pypdf
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
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
# 链接数据类
# ============================================================

@dataclass
class PDFLink:
    """PDF 链接信息"""
    page: int  # 0-indexed
    rect: Tuple[float, float, float, float]  # x1, y1, x2, y2
    link_type: str  # "uri" or "internal"
    target: str  # URL or page number
    annotation_index: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "page": self.page + 1,
            "rect": list(self.rect),
            "type": self.link_type,
            "target": self.target
        }


@dataclass
class LinkExtractionResult:
    """链接提取结果"""
    file_path: str
    total_links: int
    internal_links: int
    external_links: int
    suspicious_links: int
    links: List[PDFLink] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "file_path": self.file_path,
            "total_links": self.total_links,
            "internal_links": self.internal_links,
            "external_links": self.external_links,
            "suspicious_links": self.suspicious_links,
            "links": [l.to_dict() for l in self.links]
        }


# ============================================================
# 链接提取
# ============================================================

# Suspicious URL patterns
SUSPICIOUS_PATTERNS = [
    r"javascript:",
    r"data:",
    r"vbscript:",
    r"file://",
    r"\.exe$",
    r"\.bat$",
    r"\.cmd$",
    r"\.scr$",
]


def extract_links(pdf_path: str, include_suspicious_check: bool = True) -> LinkExtractionResult:
    """提取 PDF 中所有链接.

    Args:
        pdf_path: PDF 文件路径
        include_suspicious_check: 是否检查可疑链接

    Returns:
        LinkExtractionResult
    """
    reader = PdfReader(pdf_path)
    result = LinkExtractionResult(
        file_path=pdf_path,
        total_links=0,
        internal_links=0,
        external_links=0,
        suspicious_links=0
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

                    # Check if it's a link annotation
                    if "/Subtype" not in annot_obj:
                        continue
                    if annot_obj["/Subtype"] != "/Link":
                        continue

                    # Get rectangle
                    rect = annot_obj.get("/Rect", [0, 0, 0, 0])
                    rect_tuple = (float(rect[0]), float(rect[1]), float(rect[2]), float(rect[3]))

                    # Get link target
                    link_type = "unknown"
                    target = ""

                    if "/A" in annot_obj:
                        action = annot_obj["/A"]
                        if "/URI" in action:
                            link_type = "uri"
                            target = str(action["/URI"])
                            result.external_links += 1
                        elif "/D" in action:
                            link_type = "internal"
                            dest = action["/D"]
                            if isinstance(dest, list) and len(dest) > 0:
                                # Internal page reference
                                if isinstance(dest[0], int):
                                    target = f"Page {dest[0] + 1}"
                                else:
                                    target = str(dest)
                            else:
                                target = str(dest)
                            result.internal_links += 1
                        elif "/S" in action:
                            # Action type
                            action_type = str(action["/S"])
                            if action_type == "/GoTo":
                                link_type = "internal"
                                target = str(action.get("/D", "unknown"))
                                result.internal_links += 1
                            elif action_type == "/URI":
                                link_type = "uri"
                                target = str(action.get("/URI", "unknown"))
                                result.external_links += 1

                    elif "/Dest" in annot_obj:
                        link_type = "internal"
                        dest = annot_obj["/Dest"]
                        if isinstance(dest, list) and len(dest) > 0:
                            if isinstance(dest[0], int):
                                target = f"Page {dest[0] + 1}"
                            else:
                                target = str(dest)
                        else:
                            target = str(dest)
                        result.internal_links += 1

                    if link_type != "unknown" and target:
                        link = PDFLink(
                            page=page_num,
                            rect=rect_tuple,
                            link_type=link_type,
                            target=target,
                            annotation_index=annot_idx
                        )

                        # Check for suspicious links
                        if include_suspicious_check and link_type == "uri":
                            for pattern in SUSPICIOUS_PATTERNS:
                                if re.search(pattern, target, re.IGNORECASE):
                                    result.suspicious_links += 1
                                    link.link_type = "suspicious"
                                    break

                        result.links.append(link)
                        result.total_links += 1

                except Exception as e:
                    if "--debug" in sys.argv:
                        print(f"Warning: Error parsing annotation: {e}")
                    continue

        except Exception as e:
            if "--debug" in sys.argv:
                print(f"Warning: Error processing page {page_num}: {e}")
            continue

    return result


def list_links(pdf_path: str, output_format: str = "text") -> str:
    """列出 PDF 中所有链接.

    Args:
        pdf_path: PDF 文件路径
        output_format: 输出格式 (text/json)

    Returns:
        格式化的链接列表
    """
    result = extract_links(pdf_path)

    if output_format == "json":
        return json.dumps(result.to_dict(), indent=2, ensure_ascii=False)

    lines = [
        f"Links in {pdf_path}:",
        f"  Total: {result.total_links}",
        f"  Internal: {result.internal_links}",
        f"  External: {result.external_links}",
        f"  Suspicious: {result.suspicious_links}",
        ""
    ]

    if not result.links:
        lines.append("  (No links found)")
    else:
        for link in result.links:
            type_label = link.link_type.upper()
            page_str = f"Page {link.page + 1}"
            rect_str = f"[{link.rect[0]:.1f}, {link.rect[1]:.1f}, {link.rect[2]:.1f}, {link.rect[3]:.1f}]"
            lines.append(f"  [{type_label}] {page_str} {rect_str}")
            lines.append(f"    Target: {link.target}")

    return "\n".join(lines)


# ============================================================
# 链接添加
# ============================================================

def add_link(
    pdf_path: str,
    output_path: str,
    page: int,
    rect: Tuple[float, float, float, float],
    target: str,
    link_type: str = "uri"
) -> bool:
    """添加链接到 PDF.

    Args:
        pdf_path: 输入 PDF 路径
        output_path: 输出 PDF 路径
        page: 页码（1-indexed）
        rect: 链接区域 (x1, y1, x2, y2)
        target: 目标 URL 或页码
        link_type: 链接类型 (uri/internal)

    Returns:
        是否成功
    """
    reader = PdfReader(pdf_path)
    writer = PdfWriter()

    # Copy all pages
    for page_obj in reader.pages:
        writer.add_page(page_obj)

    # Get the target page
    page_num = page - 1  # Convert to 0-indexed
    if page_num < 0 or page_num >= len(reader.pages):
        print(f"错误: 页码 {page} 超出范围 (1-{len(reader.pages)})")
        return False

    # Create link annotation
    link_annotation = DictionaryObject()
    link_annotation[NameObject("/Type")] = NameObject("/Annot")
    link_annotation[NameObject("/Subtype")] = NameObject("/Link")
    link_annotation[NameObject("/Rect")] = ArrayObject([
        NumberObject(rect[0]),
        NumberObject(rect[1]),
        NumberObject(rect[2]),
        NumberObject(rect[3])
    ])

    # Create action
    action = DictionaryObject()

    if link_type == "uri":
        action[NameObject("/S")] = NameObject("/URI")
        action[NameObject("/URI")] = TextStringObject(target)
    elif link_type == "internal":
        action[NameObject("/S")] = NameObject("/GoTo")
        # Parse target as page number
        try:
            target_page = int(target) - 1  # Convert to 0-indexed
            action[NameObject("/D")] = ArrayObject([
                NumberObject(target_page),
                NameObject("/Fit")
            ])
        except ValueError:
            # Named destination
            action[NameObject("/D")] = TextStringObject(target)

    link_annotation[NameObject("/A")] = action

    # Add annotation to page
    writer_page = writer.pages[page_num]
    if "/Annots" not in writer_page:
        writer_page[NameObject("/Annots")] = ArrayObject()
    writer_page["/Annots"].append(link_annotation)

    # Write output
    with open(output_path, "wb") as f:
        writer.write(f)

    return True


# ============================================================
# 链接删除
# ============================================================

def remove_links(
    pdf_path: str,
    output_path: str,
    target_pattern: Optional[str] = None,
    remove_all: bool = False,
    remove_suspicious: bool = False
) -> int:
    """删除 PDF 链接.

    Args:
        pdf_path: 输入 PDF 路径
        output_path: 输出 PDF 路径
        target_pattern: 目标匹配模式
        remove_all: 是否删除所有链接
        remove_suspicious: 是否只删除可疑链接

    Returns:
        删除的链接数量
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

                # Check if it's a link
                if "/Subtype" not in annot_obj or annot_obj["/Subtype"] != "/Link":
                    new_annots.append(annot)
                    continue

                # Determine if we should remove
                should_remove = False

                if remove_all:
                    should_remove = True
                elif remove_suspicious:
                    # Check for suspicious patterns
                    if "/A" in annot_obj:
                        action = annot_obj["/A"]
                        if "/URI" in action:
                            uri = str(action["/URI"])
                            for pattern in SUSPICIOUS_PATTERNS:
                                if re.search(pattern, uri, re.IGNORECASE):
                                    should_remove = True
                                    break
                elif target_pattern:
                    # Check if target matches pattern
                    target = ""
                    if "/A" in annot_obj:
                        action = annot_obj["/A"]
                        if "/URI" in action:
                            target = str(action["/URI"])
                        elif "/D" in action:
                            target = str(action["/D"])
                    elif "/Dest" in annot_obj:
                        target = str(annot_obj["/Dest"])

                    if re.search(target_pattern, target, re.IGNORECASE):
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
        description="PDF 链接管理工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 列出所有链接
  %(prog)s list document.pdf

  # 列出链接（JSON 格式）
  %(prog)s list document.pdf --json

  # 添加外部链接
  %(prog)s add document.pdf -o output.pdf --page 1 --rect "100,100,200,120" --url "https://example.com"

  # 添加内部链接
  %(prog)s add document.pdf -o output.pdf --page 1 --rect "100,100,200,120" --page-target 5

  # 删除所有链接
  %(prog)s remove document.pdf -o output.pdf --all

  # 删除可疑链接
  %(prog)s remove document.pdf -o output.pdf --suspicious

  # 删除匹配模式的链接
  %(prog)s remove document.pdf -o output.pdf --pattern "example.com"
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="命令")

    # List command
    list_parser = subparsers.add_parser("list", help="列出链接")
    list_parser.add_argument("input", help="输入 PDF 文件")
    list_parser.add_argument("--json", action="store_true", help="输出 JSON 格式")

    # Add command
    add_parser = subparsers.add_parser("add", help="添加链接")
    add_parser.add_argument("input", help="输入 PDF 文件")
    add_parser.add_argument("-o", "--output", required=True, help="输出 PDF 文件")
    add_parser.add_argument("--page", type=int, required=True, help="页码 (1-indexed)")
    add_parser.add_argument("--rect", required=True, help="链接区域 (x1,y1,x2,y2)")
    add_parser.add_argument("--url", help="目标 URL")
    add_parser.add_argument("--page-target", type=int, help="目标页码")

    # Remove command
    remove_parser = subparsers.add_parser("remove", help="删除链接")
    remove_parser.add_argument("input", help="输入 PDF 文件")
    remove_parser.add_argument("-o", "--output", required=True, help="输出 PDF 文件")
    remove_parser.add_argument("--all", action="store_true", help="删除所有链接")
    remove_parser.add_argument("--suspicious", action="store_true", help="只删除可疑链接")
    remove_parser.add_argument("--pattern", help="删除匹配模式的链接")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # Execute command
    if args.command == "list":
        result = list_links(args.input, "json" if args.json else "text")
        print(result)

    elif args.command == "add":
        # Parse rectangle
        try:
            rect_parts = [float(x.strip()) for x in args.rect.split(",")]
            if len(rect_parts) != 4:
                raise ValueError("Invalid rect format")
            rect = tuple(rect_parts)
        except Exception:
            print("错误: rect 格式无效，使用 x1,y1,x2,y2 格式")
            return 1

        if args.url:
            success = add_link(args.input, args.output, args.page, rect, args.url, "uri")
        elif args.page_target:
            success = add_link(args.input, args.output, args.page, rect, str(args.page_target), "internal")
        else:
            print("错误: 需要 --url 或 --page-target")
            return 1

        if success:
            print(f"成功: 链接已添加，输出到 {args.output}")
        else:
            print("失败: 无法添加链接")
            return 1

    elif args.command == "remove":
        if not (args.all or args.suspicious or args.pattern):
            print("错误: 需要指定 --all, --suspicious 或 --pattern")
            return 1

        count = remove_links(
            args.input,
            args.output,
            args.pattern,
            args.all,
            args.suspicious
        )
        print(f"成功: 已删除 {count} 个链接，输出到 {args.output}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
