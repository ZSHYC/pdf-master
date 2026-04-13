#!/usr/bin/env python3
import argparse, sys
from pathlib import Path

HAS_PIKEPDF = False
try:
    import pikepdf
    HAS_PIKEPDF = True
except ImportError:
    pass

try:
    from pypdf import PdfReader, PdfWriter
except ImportError:
    print("Error: Missing pypdf"); sys.exit(1)

def repair_pdf(input_path: str, output_path: str, verbose: bool = False):
    if HAS_PIKEPDF:
        try:
            pdf = pikepdf.open(input_path, allow_overwriting_input=False)
            pdf.save(output_path)
            pdf.close()
            print(f"Repaired with pikepdf: {output_path}")
            return True
        except Exception as e:
            if verbose: print(f"pikepdf failed: {e}, trying pypdf")
    
    try:
        reader = PdfReader(input_path)
        writer = PdfWriter()
        for page in reader.pages:
            writer.add_page(page)
        with open(output_path, "wb") as f:
            writer.write(f)
        print(f"Repaired with pypdf: {output_path}")
        return True
    except Exception as e:
        print(f"Repair failed: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Repair PDF files")
    parser.add_argument("input", help="Input PDF file")
    parser.add_argument("-o", "--output", required=True, help="Output PDF file")
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()
    success = repair_pdf(args.input, args.output, args.verbose)
    sys.exit(0 if success else 1)

if __name__ == "__main__": main()