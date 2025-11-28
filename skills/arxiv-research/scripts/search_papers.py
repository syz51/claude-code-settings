#!/usr/bin/env python3
"""Search arXiv for papers."""

import argparse
import json
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime


def search_arxiv(query: str, max_results: int = 10, categories: list[str] | None = None, date_from: str | None = None) -> list[dict]:
    """Search arXiv API and return results."""

    # Build query
    search_query = query
    if categories:
        cat_query = " OR ".join(f"cat:{cat}" for cat in categories)
        search_query = f"({query}) AND ({cat_query})"

    params = {
        "search_query": f"all:{search_query}",
        "start": 0,
        "max_results": max_results,
        "sortBy": "submittedDate",
        "sortOrder": "descending"
    }

    url = f"http://export.arxiv.org/api/query?{urllib.parse.urlencode(params)}"

    with urllib.request.urlopen(url, timeout=30) as response:
        data = response.read().decode("utf-8")

    # Parse XML
    ns = {"atom": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}
    root = ET.fromstring(data)

    results = []
    for entry in root.findall("atom:entry", ns):
        # Extract arXiv ID from id URL
        id_url = entry.find("atom:id", ns).text
        arxiv_id = id_url.split("/abs/")[-1]

        # Get published date
        published = entry.find("atom:published", ns).text[:10]

        # Filter by date if specified
        if date_from:
            if published < date_from:
                continue

        # Get categories
        cats = [cat.get("term") for cat in entry.findall("atom:category", ns)]

        # Get authors
        authors = [author.find("atom:name", ns).text for author in entry.findall("atom:author", ns)]

        results.append({
            "id": arxiv_id,
            "title": " ".join(entry.find("atom:title", ns).text.split()),
            "authors": authors,
            "abstract": " ".join(entry.find("atom:summary", ns).text.split()),
            "categories": cats,
            "published": published,
            "pdf_url": f"https://arxiv.org/pdf/{arxiv_id}.pdf"
        })

    return results


def main():
    parser = argparse.ArgumentParser(description="Search arXiv for papers")
    parser.add_argument("query", help="Search query")
    parser.add_argument("--max-results", "-n", type=int, default=10, help="Max results (default: 10)")
    parser.add_argument("--categories", "-c", nargs="+", help="Filter by categories (e.g., cs.AI cs.LG)")
    parser.add_argument("--date-from", "-d", help="Filter papers from date (YYYY-MM-DD)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    results = search_arxiv(args.query, args.max_results, args.categories, args.date_from)

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        for i, paper in enumerate(results, 1):
            print(f"\n[{i}] {paper['id']}")
            print(f"    Title: {paper['title']}")
            print(f"    Authors: {', '.join(paper['authors'][:3])}{'...' if len(paper['authors']) > 3 else ''}")
            print(f"    Date: {paper['published']}")
            print(f"    Categories: {', '.join(paper['categories'][:3])}")
            print(f"    Abstract: {paper['abstract'][:200]}...")

        print(f"\nFound {len(results)} papers")


if __name__ == "__main__":
    main()
