#!/usr/bin/env python3
import argparse, json, sys
from pathlib import Path
from typing import Dict, Any, List

try:
    from pypdf import PdfReader
except ImportError:
    print("Error: Missing pypdf"); sys.exit(1)

def compare_pdfs(file1: str, file2: str, verbose: bool = False) -> Dict[str, Any]:
    result = {"file1": file1, "file2": file2, "differences": []}
    
    with open(file1, "rb") as f1, open(file2, "rb") as f2:
        r1, r2 = PdfReader(f1), PdfReader(f2)
        pages1, pages2 = len(r1.pages), len(r2.pages)
        
        if pages1 != pages2:
            result["differences"].append(f"Page count: {pages1} vs {pages2}")
        
        # Compare each page
        for i in range(min(pages1, pages2)):
            p1, p2 = r1.pages[i], r2.pages[i]
            # Compare page size
            w1, h1 = float(p1.mediabox.width), float(p1.mediabox.height)
            w2, h2 = float(p2.mediabox.width), float(p2.mediabox.height)
            if abs(w1-w2) > 0.1 or abs(h1-h2) > 0.1:
                result["differences"].append(f"Page {i+1} size differs")
        
        # Compare metadata
        m1, m2 = r1.metadata or {}, r2.metadata or {}
        for key in set(list(m1.keys()) + list(m2.keys())):
            v1, v2 = m1.get(key), m2.get(key)
            if v1 != v2:
                result["differences"].append(f"Metadata {key} differs")
    
    result["identical"] = len(result["differences"]) == 0
    return result

def main():
    parser = argparse.ArgumentParser(description="Compare two PDF files")
    parser.add_argument("file1", help="First PDF file")
    parser.add_argument("file2", help="Second PDF file")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()
    
    result = compare_pdfs(args.file1, args.file2, args.verbose)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        if result["identical"]:
            print("PDFs are identical")
        else:
            print("Differences found:")
            for d in result["differences"]:
                print(f"  - {d}")
    sys.exit(0 if result["identical"] else 1)

if __name__ == "__main__": main()