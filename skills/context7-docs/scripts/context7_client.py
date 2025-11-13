#!/usr/bin/env python3
"""
Context7 API Client
Fetches documentation for libraries using Context7's API endpoints.
"""

import os
import sys
import json
import argparse
from typing import Optional, Dict, Any
import urllib.request
import urllib.error
import urllib.parse


class Context7Client:
    """Client for interacting with Context7 API."""

    BASE_URL = "https://context7.com/api/v1"

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Context7 client.

        Args:
            api_key: Context7 API key. If not provided, reads from CONTEXT7_API_KEY env var.
        """
        self.api_key = api_key or os.environ.get("CONTEXT7_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Context7 API key required. Set CONTEXT7_API_KEY environment variable "
                "or pass api_key parameter. Get key at: https://context7.com/dashboard"
            )

    def _make_request(self, url: str) -> Dict[str, Any]:
        """Make HTTP request to Context7 API with authentication."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "X-Context7-Source": "claude-skill"
        }

        req = urllib.request.Request(url, headers=headers)

        try:
            with urllib.request.urlopen(req) as response:
                return json.loads(response.read().decode())
        except urllib.error.HTTPError as e:
            error_body = e.read().decode()
            try:
                error_data = json.loads(error_body)
                if e.code == 429:
                    retry_after = error_data.get("retryAfterSeconds", "unknown")
                    raise Exception(f"Rate limited. Retry after {retry_after} seconds")
                elif e.code == 401:
                    raise Exception("Authentication failed. Check API key")
                elif e.code == 404:
                    raise Exception("Library not found")
                else:
                    raise Exception(f"API error {e.code}: {error_data.get('error', error_body)}")
            except json.JSONDecodeError:
                raise Exception(f"HTTP {e.code}: {error_body}")
        except urllib.error.URLError as e:
            raise Exception(f"Network error: {e.reason}")

    def search_library(self, library_name: str) -> Dict[str, Any]:
        """
        Search for a library and resolve to Context7-compatible ID.

        Args:
            library_name: Name of library to search (e.g., "React", "Next.js")

        Returns:
            Dict with search results containing library IDs and metadata
        """
        encoded_name = urllib.parse.quote(library_name)
        url = f"{self.BASE_URL}/search?q={encoded_name}"
        return self._make_request(url)

    def get_docs(
        self,
        library_id: str,
        topic: Optional[str] = None,
        tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Fetch documentation for a library.

        Args:
            library_id: Context7 library ID (format: /org/project or /org/project/version)
            topic: Optional topic to filter docs (e.g., "routing", "hooks")
            tokens: Optional max tokens to retrieve (default: 5000)

        Returns:
            Dict with documentation content
        """
        # Remove leading slash if present
        library_id = library_id.lstrip("/")

        url = f"{self.BASE_URL}/{library_id}"

        # Add query parameters
        params = {}
        if topic:
            params["topic"] = topic
        if tokens:
            params["tokens"] = str(tokens)

        if params:
            query_string = urllib.parse.urlencode(params)
            url = f"{url}?{query_string}"

        return self._make_request(url)


def main():
    """CLI interface for Context7 client."""
    parser = argparse.ArgumentParser(
        description="Context7 API client for fetching library documentation"
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Search command
    search_parser = subparsers.add_parser("search", help="Search for a library")
    search_parser.add_argument("library_name", help="Name of library to search")
    search_parser.add_argument("--json", action="store_true", help="Output raw JSON")

    # Docs command
    docs_parser = subparsers.add_parser("docs", help="Fetch documentation")
    docs_parser.add_argument("library_id", help="Library ID (e.g., vercel/next.js)")
    docs_parser.add_argument("--topic", help="Focus on specific topic")
    docs_parser.add_argument("--tokens", type=int, help="Max tokens to retrieve")
    docs_parser.add_argument("--json", action="store_true", help="Output raw JSON")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        client = Context7Client()

        if args.command == "search":
            result = client.search_library(args.library_name)

            if args.json:
                print(json.dumps(result, indent=2))
            else:
                if "results" in result and result["results"]:
                    print(f"\nFound {len(result['results'])} results for '{args.library_name}':\n")
                    for i, lib in enumerate(result["results"], 1):
                        print(f"{i}. {lib.get('title', 'N/A')}")
                        print(f"   ID: {lib.get('id', 'N/A')}")
                        print(f"   Description: {lib.get('description', 'N/A')}")
                        print()
                else:
                    print(f"No results found for '{args.library_name}'")

        elif args.command == "docs":
            result = client.get_docs(args.library_id, args.topic, args.tokens)

            if args.json:
                print(json.dumps(result, indent=2))
            else:
                # Pretty print documentation
                if "content" in result:
                    print(result["content"])
                else:
                    print(json.dumps(result, indent=2))

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
