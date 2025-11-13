---
name: context7-docs
description: Fetch up-to-date library documentation using Context7's API. Use when code generation, setup steps, or library/API documentation is needed. Provides progressive token usage vs MCP - metadata ~100 words always in context, full skill under 5k words when triggered, resources loaded as needed.
---

# Context7 Documentation Fetcher

## Overview

Fetch up-to-date documentation and code examples for any library using Context7's HTTP API. This skill replicates Context7 MCP functionality with token-efficient progressive disclosure.

**When to use:**
- Code generation requiring current library APIs
- Setup/configuration steps for frameworks or tools
- Library documentation or usage examples
- API reference lookups

## Setup

**API Key Required:** Set `CONTEXT7_API_KEY` environment variable. Get key from https://context7.com/dashboard

```bash
export CONTEXT7_API_KEY="your-api-key"
```

## Quick Start

### Two-Step Workflow

1. **Search** for library to get Context7-compatible ID
2. **Fetch** documentation using that ID

**Exception:** Skip search if user provides exact ID format (`/org/project` or `/org/project/version`)

## Searching for Libraries

Use `scripts/context7_client.py search` to resolve library names to Context7 IDs.

**Basic search:**
```bash
python scripts/context7_client.py search "React"
```

**Output format:**
```
Found 3 results for 'React':

1. React
   ID: /facebook/react
   Description: JavaScript library for building user interfaces

2. React Router
   ID: /remix-run/react-router
   Description: Declarative routing for React
```

**Selection criteria:**
- Exact name matches prioritized
- Description relevance to query intent
- Documentation coverage (higher code snippet count)
- Source reputation (High/Medium preferred)

**Common patterns:**
```bash
# Framework search
python scripts/context7_client.py search "Next.js"
# Returns: /vercel/next.js

# Database client
python scripts/context7_client.py search "MongoDB"
# Returns: /mongodb/docs

# UI library
python scripts/context7_client.py search "shadcn"
# Returns: /shadcn/ui
```

## Fetching Documentation

Use `scripts/context7_client.py docs` with resolved library ID.

**Basic fetch:**
```bash
python scripts/context7_client.py docs vercel/next.js
```

**With topic filter:**
```bash
python scripts/context7_client.py docs vercel/next.js --topic routing
```

**With token limit:**
```bash
python scripts/context7_client.py docs vercel/next.js --tokens 3000
```

**Specific version:**
```bash
python scripts/context7_client.py docs vercel/next.js/v15.1.8
```

**Combined parameters:**
```bash
python scripts/context7_client.py docs vercel/next.js --topic "app router" --tokens 2000
```

## Parameters

### Library ID Format
- **Standard:** `/org/project` (e.g., `/vercel/next.js`)
- **Versioned:** `/org/project/version` (e.g., `/vercel/next.js/v15.1.8`)
- **Leading slash optional:** Script handles both `vercel/next.js` and `/vercel/next.js`

### Optional Filters
- **`--topic`**: Focus on specific subject (e.g., "routing", "hooks", "authentication")
- **`--tokens`**: Limit documentation size (default: 5000)
  - Use lower values (1000-2000) for focused queries
  - Use higher values (5000-10000) for comprehensive references

### Output Formats
- **Default**: Formatted markdown documentation
- **`--json`**: Raw JSON for programmatic parsing

## Error Handling

**Common errors:**

1. **"Context7 API key required"**
   - Set CONTEXT7_API_KEY environment variable

2. **"Authentication failed"**
   - Verify API key is correct
   - Check key hasn't been revoked

3. **"Library not found"**
   - Verify library ID is correct
   - Try searching first to confirm ID

4. **"Rate limited. Retry after X seconds"**
   - Wait specified duration
   - Consider implementing exponential backoff

5. **Network errors**
   - Check internet connectivity
   - Verify Context7 API is accessible

## Usage Examples

**Example 1: Next.js App Router documentation**
```bash
# Search for Next.js
python scripts/context7_client.py search "Next.js"

# Fetch App Router docs
python scripts/context7_client.py docs vercel/next.js --topic "app router"
```

**Example 2: React hooks with token limit**
```bash
# Direct fetch (known ID)
python scripts/context7_client.py docs facebook/react --topic hooks --tokens 2000
```

**Example 3: Specific library version**
```bash
# Search for library
python scripts/context7_client.py search "Tailwind CSS"

# Fetch specific version docs
python scripts/context7_client.py docs tailwindlabs/tailwindcss/v3.4.0
```

## Integration Tips

**For code generation:**
1. Search for library if ID unknown
2. Fetch docs with relevant topic filter
3. Use documentation to generate accurate, up-to-date code
4. Consider token limits based on scope

**For setup/configuration:**
1. Fetch docs without topic filter for comprehensive guide
2. Use higher token limit (5000+) for full instructions
3. Look for "getting started" or "installation" sections

**For API references:**
1. Use topic filter for specific API sections
2. Moderate token limits (2000-3000) for focused references
3. Fetch multiple topics separately if needed

## Token Efficiency

**Progressive disclosure vs MCP:**
- **MCP**: All tools always in context (~2k tokens)
- **This skill**:
  - Metadata: ~100 words (always)
  - SKILL.md: <5k words (when triggered)
  - Scripts: Executed without loading to context
  - References: Loaded only when needed

**Best practices:**
- Use topic filters to get focused docs
- Adjust token limits based on query scope
- Cache results when appropriate
- Only invoke skill when documentation is actually needed

## Resources

### scripts/context7_client.py
Python client for Context7 API with CLI interface. Handles authentication, search, and documentation fetching. Can be executed directly without loading to context.

### references/api_details.md
Detailed API reference including endpoints, authentication, rate limits, and error codes. Load into context if deeper API understanding is needed for debugging or advanced usage.
