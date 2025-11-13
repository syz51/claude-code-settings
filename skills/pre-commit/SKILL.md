---
name: pre-commit
description: PROACTIVELY run before git commits. Detects project environment and runs appropriate linting, formatting, and test suite with coverage (Tools: Bash, Read, Glob, Grep, mcp__ide__getDiagnostics)
---

# Pre-Commit Validation

## Overview

Automatically detect and run linting, formatting, static analysis, and tests before git commits. Context-aware: skips tests if already passed recently in conversation. Fix issues or pause if unresolvable.

## When to Use

PROACTIVELY trigger before any git commit operation. Do not wait for user request.

**Trigger conditions:**

- User requests git commit
- User requests creating pull request
- Conversation naturally leads to commit point
- User says "commit these changes"

**Do NOT trigger for:**

- Reading code or exploring files
- Research or planning tasks
- User explicitly says "skip checks" or "commit without checks"

## Core Workflow

### 0. Check Conversation History

Before running checks, review conversation history to avoid redundant work:

**Look for recent test runs:**

- Check if tests ran in conversation within last few messages
- Check if they passed
- Check if code changed since test run

**Skip tests if:**

- Tests ran recently (within ~5-10 messages)
- Tests passed
- No code changes after test run

**Run tests if:**

- Tests failed
- Code changed after tests
- Tests not run recently
- Unclear from context

**Always run:** formatting, linting, type checking (fast operations)

### 1. Detect Project Tools

Use `scripts/detect_tools.py` to identify available tools:

```bash
python scripts/detect_tools.py
```

If script unavailable or fails, manually detect by checking:

**JavaScript/TypeScript:**

- Check `package.json` for scripts: `lint`, `format`, `test`, `type-check`
- Check devDependencies: `eslint`, `prettier`, `jest`, `vitest`, `typescript`

**Python:**

- Check for: `pyproject.toml`, `setup.py`, `requirements.txt`
- Check PATH for: `black`, `ruff`, `flake8`, `mypy`, `pyright`, `pytest`

**Go:**

- Check for: `go.mod`
- Tools: `gofmt`, `go vet`, `golangci-lint`, `go test`

**Rust:**

- Check for: `Cargo.toml`
- Tools: `cargo fmt`, `cargo clippy`, `cargo test`

### 2. Run Checks in Order

Execute in this sequence (stop at first failure):

1. **Formatting** - Auto-fixable, run first

   - JS: `npm run format` or `npx prettier --write .`
   - Python: `black .` or `ruff format .`
   - Go: `gofmt -w .`
   - Rust: `cargo fmt`

2. **Linting** - May require manual fixes

   - JS: `npm run lint` or `npx eslint .`
   - Python: `ruff check .` or `flake8 .`
   - Go: `golangci-lint run`
   - Rust: `cargo clippy -- -D warnings`

3. **IDE Diagnostics** - Language server checks

   - Use `mcp__ide__getDiagnostics` if available for real-time IDE errors
   - Python: `pyright .` (comprehensive type checking)
   - TS: Already covered by `tsc --noEmit`
   - Go: `go vet ./...` (already included)
   - Rust: `cargo check` (fast compilation check)

4. **Type Checking** - If applicable

   - TS: `npx tsc --noEmit`
   - Python: `mypy .` (if mypy preferred over pyright)

5. **Tests** - Final validation
   - JS: `npm test` or `npx jest` or `npx vitest run`
   - Python: `pytest`
   - Go: `go test ./...`
   - Rust: `cargo test`

### 3. Handle Results

**On success:**

- Proceed with git commit
- No output needed unless user asks

**On failure:**

- Parse error output
- Attempt automatic fixes for:
  - Formatting issues (re-run formatter)
  - Auto-fixable lint rules (use `--fix` flag)
  - Import ordering
  - Missing type annotations (simple cases)

**Cannot auto-fix:**

- Logic errors in tests
- Complex type errors
- Semantic lint violations
- Failing test assertions

When blocked:

1. Show concise error summary
2. Explain what failed
3. Pause and ask user how to proceed

## Error Fixing Strategy

### Auto-fixable

Run with fix flags:

- `eslint --fix`
- `prettier --write`
- `black .`
- `ruff check --fix`

### Requires analysis

1. Read error output carefully
2. Identify affected files (use line numbers)
3. Read relevant file sections
4. Apply targeted fixes
5. Re-run check to verify

### Multiple errors

Fix in batches:

- Group by file
- Fix highest-priority first (compilation errors before style)
- Re-run after each batch

## Example Usage

**Scenario 1:** User says "commit these changes" (no tests run yet)

```
1. Check conversation history → No recent test runs found
2. Detect tools: package.json found, has eslint + jest
3. Run prettier --write . → Success
4. Run eslint . → 3 errors found
5. Fix errors automatically with eslint --fix → 2 fixed, 1 remains
6. Read error: "no-unused-vars at src/app.ts:15"
7. Fix manually: Remove unused import
8. Run eslint . → Success
9. Check mcp__ide__getDiagnostics → 1 type error in src/app.ts
10. Fix type error
11. Run npm test → All pass
12. Proceed with git commit
```

**Scenario 2:** User ran tests 2 messages ago, now says "commit these changes"

```
1. Check conversation history → Tests passed 2 messages ago, no code changes since
2. Detect tools: package.json found, has eslint + jest
3. Run prettier --write . → Success
4. Run eslint . → Success
5. Check mcp__ide__getDiagnostics → No errors
6. Skip tests (already passed recently)
7. Proceed with git commit
```

## Resources

### scripts/detect_tools.py

Detects available tools and returns JSON with suggested commands. Run without loading into context:

```bash
python scripts/detect_tools.py [path]
```

Output format:

```json
{
  "project_path": "/path/to/project",
  "tools": {
    "eslint": "npx eslint .",
    "prettier": "npx prettier --check .",
    "jest": "npm test"
  }
}
```

## IDE Diagnostics Integration

If `mcp__ide__getDiagnostics` tool is available:

- Use it to fetch real-time diagnostics from language servers
- Complement or replace command-line type checkers
- Provides faster feedback than running full type checking
- Parse and fix diagnostics same as command-line tool output

Example:

```
mcp__ide__getDiagnostics → Returns errors from pyright/tsserver/etc
→ Parse errors → Fix issues → Re-check
```

## Notes

- **Context awareness:** Always check conversation history first - avoid re-running tests if they passed recently and no changes made
- Always use Bash tool with appropriate timeout (tests may take minutes)
- Check for coverage thresholds if configured
- Respect `.gitignore` - don't run checks on ignored files
- If project has pre-commit hooks configured, those take precedence
- For monorepos, run checks in affected packages only
- Prefer `mcp__ide__getDiagnostics` when available for faster feedback
