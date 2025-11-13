# Context7 API Reference

## Authentication

All requests require bearer token authentication:

```
Authorization: Bearer CONTEXT7_API_KEY
```

Obtain API key from: <https://context7.com/dashboard>

## Endpoints

### 1. Search/Resolve Library ID

**Endpoint:** `GET https://context7.com/api/v1/search`

**Parameters:**

- `q` (required): Library name to search

**Response Format:**

```json
{
  "results": [
    {
      "title": "Library Name",
      "id": "/org/project",
      "description": "Library description",
      "trustScore": "High|Medium|Low",
      "codeSnippets": 1234
    }
  ],
  "error": "Optional error message"
}
```

### 2. Fetch Documentation

**Endpoint:** `GET https://context7.com/api/v1/{org}/{project}/{version}`

**Path Parameters:**

- `org/project` (required): Library identifier (e.g., `vercel/next.js`)
- `version` (optional): Specific version (e.g., `v15.1.8`)

**Query Parameters:**

- `topic` (optional): Filter by topic (e.g., "routing", "hooks")
- `tokens` (optional): Limit documentation size (default: 5000)

**Response Format:**

```json
{
  "content": "Documentation content in markdown format",
  "library": "Library metadata",
  "version": "Version information"
}
```

## Rate Limiting

**Limits:**

- Unauthenticated: Low limits
- Authenticated: Plan-based limits

**Rate Limit Error (429):**

```json
{
  "error": "Too many requests",
  "status": 429,
  "retryAfterSeconds": 60
}
```

## HTTP Status Codes

- **200**: Success
- **401**: Authentication failed - check API key
- **404**: Library not found - verify library ID
- **429**: Rate limited - retry after specified delay
- **500**: Server error - retry and contact support

## Best Practices

1. **Library ID Resolution:** Always search first to get exact library ID unless user provides exact format
2. **Token Limits:** Use `tokens` parameter to control context usage
3. **Topic Filtering:** Use `topic` parameter to get focused documentation
4. **Error Handling:** Implement retry logic for rate limits and server errors
5. **Caching:** Cache results when appropriate to reduce API calls
