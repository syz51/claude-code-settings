#!/usr/bin/env python3
"""Read/extract text from downloaded arXiv paper."""

import argparse
import os
import json
import sys
from pathlib import Path

try:
    import pymupdf
    HAS_PYMUPDF = True
except ImportError:
    HAS_PYMUPDF = False


def get_storage_path() -> Path:
    """Get paper storage directory."""
    return Path(os.environ.get("ARXIV_STORAGE_PATH", Path.home() / ".arxiv-papers"))


def normalize_id(paper_id: str) -> str:
    """Normalize arXiv ID."""
    return paper_id.replace("arxiv:", "").replace("arXiv:", "").strip()


def read_paper(paper_id: str, max_pages: int | None = None) -> dict:
    """Read text content from a downloaded paper."""
    paper_id = normalize_id(paper_id)
    storage = get_storage_path()

    safe_id = paper_id.replace("/", "_")
    pdf_path = storage / f"{safe_id}.pdf"

    if not pdf_path.exists():
        return {
            "status": "error",
            "paper_id": paper_id,
            "error": f"Paper not found. Download it first with: download_paper.py {paper_id}"
        }

    if not HAS_PYMUPDF:
        return {
            "status": "error",
            "paper_id": paper_id,
            "error": "pymupdf not installed. Run: uv pip install pymupdf"
        }

    try:
        doc = pymupdf.open(pdf_path)
        total_pages = len(doc)
        pages_to_read = min(max_pages, total_pages) if max_pages else total_pages

        text_parts = []
        for i in range(pages_to_read):
            page = doc[i]
            text = page.get_text()
            text_parts.append(f"--- Page {i+1} ---\n{text}")

        doc.close()

        return {
            "status": "success",
            "paper_id": paper_id,
            "total_pages": total_pages,
            "pages_read": pages_to_read,
            "content": "\n\n".join(text_parts)
        }
    except Exception as e:
        return {
            "status": "error",
            "paper_id": paper_id,
            "error": str(e)
        }


def main():
    parser = argparse.ArgumentParser(description="Read text from downloaded arXiv paper")
    parser.add_argument("paper_id", help="arXiv paper ID")
    parser.add_argument("--max-pages", "-p", type=int, help="Max pages to read")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    result = read_paper(args.paper_id, args.max_pages)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        if result["status"] == "error":
            print(f"Error: {result['error']}", file=sys.stderr)
            sys.exit(1)
        else:
            print(f"Paper: {result['paper_id']} ({result['pages_read']}/{result['total_pages']} pages)\n")
            print(result["content"])


if __name__ == "__main__":
    main()
