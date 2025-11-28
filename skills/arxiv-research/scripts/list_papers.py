#!/usr/bin/env python3
"""List downloaded arXiv papers."""

import argparse
import os
import json
from pathlib import Path


def get_storage_path() -> Path:
    """Get paper storage directory."""
    return Path(os.environ.get("ARXIV_STORAGE_PATH", Path.home() / ".arxiv-papers"))


def list_papers() -> list[dict]:
    """List all downloaded papers."""
    storage = get_storage_path()

    if not storage.exists():
        return []

    papers = []
    for pdf_file in storage.glob("*.pdf"):
        # Convert filename back to arXiv ID
        paper_id = pdf_file.stem.replace("_", "/")
        stat = pdf_file.stat()

        papers.append({
            "paper_id": paper_id,
            "path": str(pdf_file),
            "size_bytes": stat.st_size,
            "downloaded_at": stat.st_mtime
        })

    # Sort by download time, newest first
    papers.sort(key=lambda x: x["downloaded_at"], reverse=True)
    return papers


def main():
    parser = argparse.ArgumentParser(description="List downloaded arXiv papers")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    papers = list_papers()

    if args.json:
        print(json.dumps(papers, indent=2))
    else:
        if not papers:
            storage = get_storage_path()
            print(f"No papers downloaded yet. Storage: {storage}")
        else:
            print(f"Downloaded papers ({len(papers)}):\n")
            for paper in papers:
                size_mb = paper["size_bytes"] / (1024 * 1024)
                print(f"  {paper['paper_id']} ({size_mb:.1f} MB)")
            print(f"\nStorage: {get_storage_path()}")


if __name__ == "__main__":
    main()
