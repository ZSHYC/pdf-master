#!/usr/bin/env python3
"""
PDF Batch Rename Script

Rename PDF files based on various rules:
- Content-based: Extract title/subject from PDF content
- Metadata-based: Use PDF metadata (author, title, date, etc.)
- Date-based: Use creation/modification date
- Custom rules: Pattern-based naming with placeholders

Usage:
    python rename_pdf.py input.pdf --rule metadata --template "{author} - {title}"
    python rename_pdf.py *.pdf --rule date --template "{date:%Y-%m-%d}_{filename}"
    python rename_pdf.py *.pdf --rule content --template "{title}"
    python rename_pdf.py *.pdf --rule custom --template "Document_{counter:04d}"
    python rename_pdf.py *.pdf --dry-run  # Preview changes without renaming
"""

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Callable, Tuple

try:
    from pypdf import PdfReader
except ImportError:
    print("Error: Missing pypdf library")
    print("Run: pip install pypdf")
    sys.exit(1)

try:
    import pdfplumber
except ImportError:
    pdfplumber = None


# ============================================================================
# Naming Rules
# ============================================================================

class NamingRule:
    """Base class for naming rules."""

    def __init__(self, template: str):
        self.template = template

    def extract_info(self, pdf_path: Path) -> Dict[str, Any]:
        """Extract information from PDF for naming."""
        raise NotImplementedError

    def generate_name(self, pdf_path: Path, context: Dict[str, Any]) -> str:
        """Generate new filename based on template and extracted info."""
        info = self.extract_info(pdf_path)
        info.update(context)
        return self._format_template(self.template, info, pdf_path)

    def _format_template(self, template: str, info: Dict[str, Any], pdf_path: Path) -> str:
        """Format template string with extracted info."""
        result = template

        # Handle date formatting: {date:%Y-%m-%d}
        date_pattern = r'\{(date|creation_date|mod_date):([^}]+)\}'
        for match in re.finditer(date_pattern, template):
            field, fmt = match.groups()
            date_val = info.get(field)
            if date_val:
                if isinstance(date_val, datetime):
                    result = result.replace(match.group(0), date_val.strftime(fmt))
                elif isinstance(date_val, str):
                    result = result.replace(match.group(0), date_val)

        # Handle counter formatting: {counter:04d}
        counter_pattern = r'\{counter:([^}]+)\}'
        for match in re.finditer(counter_pattern, template):
            fmt = match.group(1)
            counter = info.get('counter', 1)
            try:
                formatted = f"{counter:{fmt}}"
                result = result.replace(match.group(0), formatted)
            except (ValueError, TypeError):
                pass

        # Replace simple placeholders
        for key, value in info.items():
            placeholder = f"{{{key}}}"
            if placeholder in result and value is not None:
                result = result.replace(placeholder, str(value))

        # Handle filename placeholder
        if "{filename}" in result:
            result = result.replace("{filename}", pdf_path.stem)

        if "{ext}" in result:
            result = result.replace("{ext}", pdf_path.suffix)

        # Clean up empty or None values
        result = re.sub(r'\s+-\s*$', '', result)  # Remove trailing " - "
        result = re.sub(r'^\s+-\s+', '', result)  # Remove leading " - "
        result = re.sub(r'\s+', '_', result)  # Replace spaces with underscores

        # Add .pdf extension if not present
        if not result.lower().endswith('.pdf'):
            result += '.pdf'

        return result


class MetadataNamingRule(NamingRule):
    """Rename based on PDF metadata."""

    def extract_info(self, pdf_path: Path) -> Dict[str, Any]:
        info = {
            'title': None,
            'author': None,
            'subject': None,
            'keywords': None,
            'creator': None,
            'producer': None,
            'creation_date': None,
            'mod_date': None,
            'date': None,
            'page_count': None,
        }

        try:
            with open(pdf_path, 'rb') as f:
                reader = PdfReader(f)
                info['page_count'] = len(reader.pages)

                if reader.metadata:
                    metadata = reader.metadata
                    info['title'] = metadata.get('/Title')
                    info['author'] = metadata.get('/Author')
                    info['subject'] = metadata.get('/Subject')
                    info['keywords'] = metadata.get('/Keywords')
                    info['creator'] = metadata.get('/Creator')
                    info['producer'] = metadata.get('/Producer')

                    # Parse dates
                    creation_date = metadata.get('/CreationDate')
                    if creation_date:
                        info['creation_date'] = parse_pdf_date(creation_date)
                        info['date'] = info['creation_date']

                    mod_date = metadata.get('/ModDate')
                    if mod_date:
                        info['mod_date'] = parse_pdf_date(mod_date)

        except Exception:
            pass

        return info


class ContentNamingRule(NamingRule):
    """Rename based on PDF content (first page title extraction)."""

    def __init__(self, template: str, max_chars: int = 100):
        super().__init__(template)
        self.max_chars = max_chars

    def extract_info(self, pdf_path: Path) -> Dict[str, Any]:
        info = {
            'title': None,
            'first_line': None,
            'first_heading': None,
        }

        # Try metadata first
        metadata_rule = MetadataNamingRule(self.template)
        metadata_info = metadata_rule.extract_info(pdf_path)

        if metadata_info.get('title'):
            info['title'] = metadata_info['title']
            return info

        # Extract from content
        try:
            text = self._extract_first_page_text(pdf_path)
            if text:
                # Try to find a title-like line
                lines = [l.strip() for l in text.split('\n') if l.strip()]

                if lines:
                    # First non-empty line as title
                    info['first_line'] = self._clean_title(lines[0])

                    # Look for heading patterns
                    for line in lines[:5]:  # Check first 5 lines
                        if self._looks_like_title(line):
                            info['first_heading'] = self._clean_title(line)
                            break

                    # Use first heading or first line as title
                    info['title'] = info['first_heading'] or info['first_line']

        except Exception:
            pass

        return info

    def _extract_first_page_text(self, pdf_path: Path) -> Optional[str]:
        """Extract text from first page."""
        if pdfplumber:
            try:
                with pdfplumber.open(pdf_path) as pdf:
                    if pdf.pages:
                        return pdf.pages[0].extract_text() or ""
            except Exception:
                pass

        try:
            with open(pdf_path, 'rb') as f:
                reader = PdfReader(f)
                if reader.pages:
                    return reader.pages[0].extract_text() or ""
        except Exception:
            pass

        return None

    def _looks_like_title(self, line: str) -> bool:
        """Check if line looks like a title."""
        # Title heuristics
        if len(line) < 5 or len(line) > self.max_chars:
            return False
        if line.islower():
            return False
        if re.match(r'^[\d\.\-\)]+\s', line):  # Numbered list item
            return False
        if line.endswith('.'):  # Probably a sentence
            return False
        return True

    def _clean_title(self, title: str) -> str:
        """Clean extracted title for use in filename."""
        # Remove invalid filename characters
        title = re.sub(r'[<>:"/\\|?*]', '', title)
        # Truncate if too long
        if len(title) > self.max_chars:
            title = title[:self.max_chars].rsplit(' ', 1)[0]
        return title.strip()


class DateNamingRule(NamingRule):
    """Rename based on file/PDF dates."""

    def extract_info(self, pdf_path: Path) -> Dict[str, Any]:
        info = {
            'date': None,
            'creation_date': None,
            'mod_date': None,
            'file_created': None,
            'file_modified': None,
            'year': None,
            'month': None,
            'day': None,
        }

        # Get PDF dates
        metadata_rule = MetadataNamingRule(self.template)
        metadata_info = metadata_rule.extract_info(pdf_path)
        info.update(metadata_info)

        # Get file system dates
        try:
            stat = pdf_path.stat()
            info['file_created'] = datetime.fromtimestamp(stat.st_ctime)
            info['file_modified'] = datetime.fromtimestamp(stat.st_mtime)
        except Exception:
            pass

        # Determine primary date (PDF creation > file creation > file modified)
        if info['creation_date']:
            info['date'] = info['creation_date']
        elif info['file_created']:
            info['date'] = info['file_created']
        elif info['file_modified']:
            info['date'] = info['file_modified']

        # Extract date components
        if info['date']:
            if isinstance(info['date'], datetime):
                info['year'] = info['date'].year
                info['month'] = info['date'].strftime('%m')
                info['day'] = info['date'].strftime('%d')

        return info


class CustomNamingRule(NamingRule):
    """Rename using custom patterns and rules."""

    def __init__(self, template: str, patterns: Optional[Dict[str, str]] = None):
        super().__init__(template)
        self.patterns = patterns or {}

    def extract_info(self, pdf_path: Path) -> Dict[str, Any]:
        info = {
            'filename': pdf_path.stem,
            'ext': pdf_path.suffix,
            'parent_dir': pdf_path.parent.name,
            'size_kb': pdf_path.stat().st_size // 1024 if pdf_path.exists() else 0,
        }

        # Apply regex patterns to extract from original filename
        for name, pattern in self.patterns.items():
            match = re.search(pattern, pdf_path.stem)
            if match:
                if match.groups():
                    info[name] = match.group(1)
                else:
                    info[name] = match.group(0)

        return info


# ============================================================================
# Utility Functions
# ============================================================================

def parse_pdf_date(date_str: Optional[str]) -> Optional[datetime]:
    """Parse PDF date format (D:YYYYMMDDHHmmss) to datetime."""
    if not date_str:
        return None

    try:
        # Remove 'D:' prefix if present
        if date_str.startswith('D:'):
            date_str = date_str[2:]

        # Parse the date components
        year = int(date_str[0:4])
        month = int(date_str[4:6]) if len(date_str) > 4 else 1
        day = int(date_str[6:8]) if len(date_str) > 6 else 1
        hour = int(date_str[8:10]) if len(date_str) > 8 else 0
        minute = int(date_str[10:12]) if len(date_str) > 10 else 0
        second = int(date_str[12:14]) if len(date_str) > 14 else 0

        return datetime(year, month, day, hour, minute, second)

    except Exception:
        return None


def sanitize_filename(name: str) -> str:
    """Sanitize filename by removing/replacing invalid characters."""
    # Remove invalid characters
    name = re.sub(r'[<>:"/\\|?*]', '', name)
    # Replace multiple spaces/underscores with single underscore
    name = re.sub(r'[\s_]+', '_', name)
    # Remove leading/trailing spaces and underscores
    name = name.strip('_ ')
    # Truncate to reasonable length
    if len(name) > 200:
        name = name[:200]
    return name


def generate_unique_name(target_dir: Path, desired_name: str, original_path: Optional[Path] = None) -> str:
    """Generate unique filename if target already exists."""
    target_path = target_dir / desired_name

    if not target_path.exists():
        return desired_name

    if original_path and target_path.resolve() == original_path.resolve():
        return desired_name  # Same file, no conflict

    # Generate unique name with suffix
    stem = Path(desired_name).stem
    ext = Path(desired_name).suffix

    counter = 1
    while True:
        new_name = f"{stem}_{counter}{ext}"
        if not (target_dir / new_name).exists():
            return new_name
        counter += 1
        if counter > 9999:  # Safety limit
            raise ValueError(f"Cannot generate unique name for {desired_name}")


class ProgressReporter:
    """Progress reporter for batch operations."""

    def __init__(self, total: int, desc: str = "Processing"):
        self.total = total
        self.current = 0
        self.desc = desc

    def update(self, current: int, msg: Optional[str] = None):
        self.current = current
        pct = (current / self.total * 100) if self.total > 0 else 0
        s = f"{self.desc}: {round(pct)}% ({current}/{self.total})"
        sys.stderr.write(f"\r{s}" + " " * 10)
        sys.stderr.flush()

    def finish(self):
        sys.stderr.write("\n")
        sys.stderr.flush()


# ============================================================================
# Batch Rename Function
# ============================================================================

def batch_rename(
    files: List[Path],
    rule: NamingRule,
    output_dir: Optional[Path] = None,
    dry_run: bool = False,
    verbose: bool = False,
    conflict_strategy: str = "unique"
) -> Dict[str, Any]:
    """
    Batch rename PDF files.

    Args:
        files: List of PDF file paths to rename
        rule: Naming rule to apply
        output_dir: Output directory (default: same directory)
        dry_run: If True, preview changes without renaming
        verbose: If True, print detailed progress
        conflict_strategy: How to handle name conflicts ('unique', 'skip', 'overwrite')

    Returns:
        Dictionary with results
    """
    results = {
        'total': len(files),
        'renamed': 0,
        'skipped': 0,
        'errors': 0,
        'changes': []
    }

    progress = ProgressReporter(len(files), "Renaming")
    counter = 1

    for i, pdf_path in enumerate(files, 1):
        pdf_path = Path(pdf_path)

        if not pdf_path.exists():
            results['errors'] += 1
            results['changes'].append({
                'original': str(pdf_path),
                'error': 'File not found'
            })
            progress.update(i)
            continue

        if pdf_path.suffix.lower() != '.pdf':
            results['skipped'] += 1
            progress.update(i)
            continue

        try:
            # Generate new name
            context = {'counter': counter}
            new_name = rule.generate_name(pdf_path, context)
            new_name = sanitize_filename(new_name)

            # Determine output directory
            target_dir = output_dir if output_dir else pdf_path.parent

            # Handle conflicts
            if conflict_strategy == "unique":
                new_name = generate_unique_name(target_dir, new_name, pdf_path)

            new_path = target_dir / new_name

            # Record change
            change = {
                'original': str(pdf_path),
                'new_name': new_name,
                'new_path': str(new_path),
            }

            if dry_run:
                change['status'] = 'preview'
                results['renamed'] += 1
            else:
                # Perform rename
                target_dir.mkdir(parents=True, exist_ok=True)

                if conflict_strategy == "skip" and new_path.exists():
                    change['status'] = 'skipped_exists'
                    results['skipped'] += 1
                else:
                    if conflict_strategy == "overwrite" and new_path.exists():
                        new_path.unlink()

                    pdf_path.rename(new_path)
                    change['status'] = 'renamed'
                    results['renamed'] += 1
                    counter += 1

            results['changes'].append(change)

            if verbose:
                print(f"  {pdf_path.name} -> {new_name}")

        except Exception as e:
            results['errors'] += 1
            results['changes'].append({
                'original': str(pdf_path),
                'error': str(e)
            })

        progress.update(i)

    progress.finish()
    return results


def print_results(results: Dict[str, Any], dry_run: bool = False):
    """Print rename results."""
    action = "Would rename" if dry_run else "Renamed"

    print(f"\n{'=' * 60}")
    print(f"Batch Rename {'Preview' if dry_run else 'Results'}")
    print(f"{'=' * 60}")
    print(f"Total files: {results['total']}")
    print(f"{action}: {results['renamed']}")
    print(f"Skipped: {results['skipped']}")
    print(f"Errors: {results['errors']}")

    if results['changes']:
        print(f"\n{'Changes:' if not dry_run else 'Preview:'}")
        for change in results['changes']:
            if 'error' in change:
                print(f"  ERROR: {change['original']} - {change['error']}")
            else:
                print(f"  {Path(change['original']).name} -> {change['new_name']}")


# ============================================================================
# Main CLI
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Batch rename PDF files using various naming rules",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Naming Rules:
  metadata    Use PDF metadata (title, author, date, etc.)
  content     Extract title from PDF content
  date        Use creation/modification dates
  custom      Custom pattern-based naming

Template Placeholders:
  {title}          PDF title from metadata or content
  {author}         PDF author
  {subject}        PDF subject
  {keywords}       PDF keywords
  {date}           Primary date (creation or file date)
  {creation_date}  PDF creation date
  {mod_date}       PDF modification date
  {year}           Year from date
  {month}          Month from date
  {day}            Day from date
  {filename}       Original filename (without extension)
  {ext}            File extension
  {counter}        Sequential number
  {page_count}     Number of pages
  {parent_dir}     Parent directory name

Date Formatting:
  {date:%Y-%m-%d}        Format date as YYYY-MM-DD
  {date:%Y/%m/%d}        Format date as YYYY/MM/DD

Counter Formatting:
  {counter:04d}          Format counter as 4-digit zero-padded

Examples:
  %(prog)s *.pdf --rule metadata --template "{author} - {title}"
  %(prog)s *.pdf --rule date --template "{date:%Y-%m-%d}_{filename}"
  %(prog)s *.pdf --rule content --template "{title}"
  %(prog)s *.pdf --rule custom --template "Document_{counter:04d}"
  %(prog)s *.pdf --rule metadata --template "{year}/{author}/{title}"
        """
    )

    parser.add_argument(
        "files",
        nargs="+",
        help="Input PDF files (supports wildcards)"
    )

    parser.add_argument(
        "--rule", "-r",
        choices=["metadata", "content", "date", "custom"],
        default="metadata",
        help="Naming rule to apply (default: metadata)"
    )

    parser.add_argument(
        "--template", "-t",
        default="{title}",
        help="Filename template (default: {title})"
    )

    parser.add_argument(
        "--output", "-o",
        help="Output directory (default: same as source)"
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without renaming files"
    )

    parser.add_argument(
        "--conflict",
        choices=["unique", "skip", "overwrite"],
        default="unique",
        help="How to handle name conflicts (default: unique)"
    )

    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results in JSON format"
    )

    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Show detailed progress"
    )

    args = parser.parse_args()

    # Collect PDF files
    files = []
    for f in args.files:
        path = Path(f)
        if path.is_dir():
            files.extend(path.glob("*.pdf"))
        elif path.suffix.lower() == ".pdf":
            files.append(path)

    if not files:
        print("No PDF files found", file=sys.stderr)
        sys.exit(1)

    # Create naming rule
    rule_classes = {
        "metadata": MetadataNamingRule,
        "content": ContentNamingRule,
        "date": DateNamingRule,
        "custom": CustomNamingRule,
    }

    rule_class = rule_classes[args.rule]
    rule = rule_class(args.template)

    # Get output directory
    output_dir = Path(args.output) if args.output else None

    # Perform rename
    results = batch_rename(
        files=files,
        rule=rule,
        output_dir=output_dir,
        dry_run=args.dry_run,
        verbose=args.verbose,
        conflict_strategy=args.conflict
    )

    # Output results
    if args.json:
        print(json.dumps(results, indent=2, ensure_ascii=False))
    else:
        print_results(results, args.dry_run)


if __name__ == "__main__":
    main()
