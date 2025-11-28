#!/usr/bin/env python3
"""Download paper from arXiv."""

import argparse
import os
import urllib.request
import json
from pathlib import Path


def get_storage_path() -> Path:
    """Get or create paper storage directory."""
    storage = Path(os.environ.get("ARXIV_STORAGE_PATH", Path.home() / ".arxiv-papers"))
    storage.mkdir(parents=True, exist_ok=True)
    return storage


def normalize_id(paper_id: str) -> str:
    """Normalize arXiv ID (remove arxiv: prefix if present)."""
    return paper_id.replace("arxiv:", "").replace("arXiv:", "").strip()


def download_paper(paper_id: str) -> dict:
    """Download a paper PDF from arXiv."""
    paper_id = normalize_id(paper_id)
    storage = get_storage_path()

    # Create safe filename
    safe_id = paper_id.replace("/", "_")
    pdf_path = storage / f"{safe_id}.pdf"

    if pdf_path.exists():
        return {
            "status": "exists",
            "paper_id": paper_id,
            "path": str(pdf_path),
            "message": f"Paper already downloaded at {pdf_path}"
        }

    # Download PDF
    pdf_url = f"https://arxiv.org/pdf/{paper_id}.pdf"

    try:
        req = urllib.request.Request(pdf_url, headers={"User-Agent": "arxiv-skill/1.0"})
        with urllib.request.urlopen(req, timeout=60) as response:
            pdf_data = response.read()

        with open(pdf_path, "wb") as f:
            f.write(pdf_data)

        return {
            "status": "downloaded",
            "paper_id": paper_id,
            "path": str(pdf_path),
            "size_bytes": len(pdf_data),
            "message": f"Downloaded to {pdf_path}"
        }
    except Exception as e:
        return {
            "status": "error",
            "paper_id": paper_id,
            "error": str(e)
        }


def main():
    parser = argparse.ArgumentParser(description="Download paper from arXiv")
    parser.add_argument("paper_id", help="arXiv paper ID (e.g., 2301.00234)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    result = download_paper(args.paper_id)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(result["message"] if "message" in result else result.get("error", "Unknown error"))


if __name__ == "__main__":
    main()
