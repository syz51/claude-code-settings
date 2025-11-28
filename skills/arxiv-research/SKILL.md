---
name: arxiv-research
description: Search, download, and analyze academic papers from arXiv. Use when users ask about research papers, academic literature, scientific studies, or want to find papers on specific topics. Triggers on queries like "find papers about X", "search arXiv for Y", "what's the latest research on Z", "download paper arxiv:1234.5678", or any request involving academic paper discovery and analysis.
---

# arXiv Research

Search and analyze academic papers from arXiv.

## Scripts

All scripts in `scripts/` directory. Run with `uv run --with pymupdf python <script>` (pymupdf only needed for read_paper.py).

### search_papers.py
```bash
python scripts/search_papers.py "query" [-n MAX] [-c CATEGORIES...] [-d DATE_FROM] [--json]
```
- `query`: search terms
- `-n`: max results (default 10)
- `-c`: filter categories (e.g., `-c cs.AI cs.LG`)
- `-d`: papers from date (YYYY-MM-DD)

### download_paper.py
```bash
python scripts/download_paper.py PAPER_ID [--json]
```
Downloads PDF to `~/.arxiv-papers/`

### list_papers.py
```bash
python scripts/list_papers.py [--json]
```
Lists all downloaded papers.

### read_paper.py
```bash
uv run --with pymupdf python scripts/read_paper.py PAPER_ID [-p MAX_PAGES] [--json]
```
Extracts text from downloaded PDF. Requires pymupdf.

## Workflows

### Literature Search
1. Search: `python scripts/search_papers.py "topic"`
2. Download interesting papers: `python scripts/download_paper.py ID`
3. Read: `uv run --with pymupdf python scripts/read_paper.py ID`

### Research Survey
1. Broad search with more results: `python scripts/search_papers.py "topic" -n 20`
2. Download multiple papers
3. Read and synthesize findings

## arXiv Categories

- **cs.AI** - Artificial Intelligence
- **cs.LG** - Machine Learning
- **cs.CL** - Computation and Language (NLP)
- **cs.CV** - Computer Vision
- **stat.ML** - Statistics: Machine Learning

Storage: `~/.arxiv-papers/` (override with `ARXIV_STORAGE_PATH` env var)
