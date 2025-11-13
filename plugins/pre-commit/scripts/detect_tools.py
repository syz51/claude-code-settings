#!/usr/bin/env python3
"""
Detects available linting, formatting, testing, and static analysis tools in a project.

Usage:
    python detect_tools.py [project_path]

Returns JSON with detected tools and suggested commands.
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, Any


def detect_javascript_tools(project_path: Path) -> Dict[str, Any]:
    """Detect JavaScript/TypeScript tools."""
    tools = {}

    package_json = project_path / "package.json"
    if not package_json.exists():
        return tools

    try:
        import json as json_lib

        with open(package_json) as f:
            package_data = json_lib.load(f)

        scripts = package_data.get("scripts", {})
        dev_deps = package_data.get("devDependencies", {})
        deps = package_data.get("dependencies", {})
        all_deps = {**dev_deps, **deps}

        # Check for common tools
        if "eslint" in all_deps or "lint" in scripts:
            tools["eslint"] = scripts.get("lint", "npx eslint .")

        if "prettier" in all_deps or "format" in scripts:
            tools["prettier"] = scripts.get("format", "npx prettier --check .")

        if "jest" in all_deps or "test" in scripts:
            tools["jest"] = scripts.get("test", "npm test")

        if "vitest" in all_deps:
            tools["vitest"] = scripts.get("test", "npx vitest run")

        if "typescript" in all_deps or "tsc" in scripts:
            tools["typescript"] = scripts.get("type-check", "npx tsc --noEmit")

    except Exception:
        pass

    return tools


def detect_python_tools(project_path: Path) -> Dict[str, Any]:
    """Detect Python tools."""
    tools = {}

    # Check for config files
    pyproject_toml = project_path / "pyproject.toml"
    setup_py = project_path / "setup.py"
    requirements = project_path / "requirements.txt"

    if not (pyproject_toml.exists() or setup_py.exists() or requirements.exists()):
        return tools

    # Common Python tools
    common_tools = {
        "black": "black --check .",
        "flake8": "flake8 .",
        "pylint": "pylint **/*.py",
        "mypy": "mypy .",
        "ruff": "ruff check .",
        "pytest": "pytest",
        "pyright": "pyright .",
    }

    for tool, command in common_tools.items():
        # Check if tool is available in PATH
        if os.system(f"which {tool} > /dev/null 2>&1") == 0:
            tools[tool] = command

    return tools


def detect_go_tools(project_path: Path) -> Dict[str, Any]:
    """Detect Go tools."""
    tools = {}

    go_mod = project_path / "go.mod"
    if not go_mod.exists():
        return tools

    tools["gofmt"] = "gofmt -l ."
    tools["go-vet"] = "go vet ./..."
    tools["go-test"] = "go test ./..."

    # Check for golangci-lint
    if os.system("which golangci-lint > /dev/null 2>&1") == 0:
        tools["golangci-lint"] = "golangci-lint run"

    return tools


def detect_rust_tools(project_path: Path) -> Dict[str, Any]:
    """Detect Rust tools."""
    tools = {}

    cargo_toml = project_path / "Cargo.toml"
    if not cargo_toml.exists():
        return tools

    tools["rustfmt"] = "cargo fmt -- --check"
    tools["clippy"] = "cargo clippy -- -D warnings"
    tools["cargo-test"] = "cargo test"

    return tools


def main():
    project_path = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
    project_path = project_path.resolve()

    all_tools = {}

    # Detect tools for different languages
    all_tools.update(detect_javascript_tools(project_path))
    all_tools.update(detect_python_tools(project_path))
    all_tools.update(detect_go_tools(project_path))
    all_tools.update(detect_rust_tools(project_path))

    result = {"project_path": str(project_path), "tools": all_tools}

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
