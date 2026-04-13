#!/usr/bin/env python3
import argparse, sys, os
from pathlib import Path

try:
    from pypdf import PdfReader, PdfWriter
except ImportError:
    print("Error: Missing pypdf"); sys.exit(1)

class ProgressReporter:
    def __init__(self, total, desc="Processing"):
        self.total, self.current, self.desc = total, 0, desc
    def update(self, current, msg=None):
        self.current = current
        pct = (current / self.total * 100) if self.total > 0 else 0
        s = self.desc + ": " + str(round(pct)) + "% (" + str(current) + "/" + str(self.total) + ")"
        sys.stderr.write(chr(13) + s + " " * 10)
        sys.stderr.flush()
    def finish(self):
        sys.stderr.write(chr(10))
        sys.stderr.flush()

def batch_compress(files, output_dir, verbose=False):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    progress = ProgressReporter(len(files), "Compressing")
    for i, f in enumerate(files, 1):
        try:
            reader = PdfReader(f)
            writer = PdfWriter()
            for page in reader.pages:
                writer.add_page(page)
            out_file = output_dir / Path(f).name
            with open(out_file, "wb") as out:
                writer.write(out)
        except Exception as e:
            sys.stderr.write(chr(10) + "Error: " + str(e) + chr(10))
        progress.update(i)
    progress.finish()
    print("Processed", len(files), "files to", output_dir)

def batch_merge(files, output_file, verbose=False):
    writer = PdfWriter()
    progress = ProgressReporter(len(files), "Merging")
    for i, f in enumerate(files, 1):
        try:
            for page in PdfReader(f).pages:
                writer.add_page(page)
        except Exception as e:
            sys.stderr.write(chr(10) + "Error: " + str(e) + chr(10))
        progress.update(i)
    progress.finish()
    with open(output_file, "wb") as out:
        writer.write(out)
    print("Merged", len(files), "files to", output_file)

def main():
    parser = argparse.ArgumentParser(description="Batch process PDF files")
    parser.add_argument("files", nargs="+", help="Input PDF files")
    parser.add_argument("-o", "--output", required=True, help="Output file/dir")
    parser.add_argument("--action", choices=["compress", "merge"], default="compress")
    args = parser.parse_args()
    files = [f for f in args.files if Path(f).suffix.lower() == ".pdf"]
    if not files: print("No PDF files"); sys.exit(1)
    if args.action == "compress": batch_compress(files, args.output)
    elif args.action == "merge": batch_merge(files, args.output)

if __name__ == "__main__": main()
