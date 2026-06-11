# Chainlink Confidential AI — API Reference

## Base URL

```
https://confidential-ai-dev-preview.cldev.cloud
```

Auth on every request: `Authorization: Bearer $API_KEY`

---

## POST /v1/inference

Submit an inference request.

**Request body:**

```json
{
  "model": "gemma4",
  "system_prompt": "optional — defaults to the standard helpful-assistant prompt if omitted",
  "prompt": "required",
  "resources": [
    {
      "filename": "statement.pdf",
      "content_type": "application/pdf",
      "content_base64": "<base64>"
    },
    {
      "url": "https://example.com/report.html",
      "method": "GET",
      "headers": {}
    }
  ],
  "cre_callback": { "url": "https://your-server.example.com/callback" }
}
```

- `resources` — optional, up to 10 items. Two variants:
  - **Base64 upload**: `filename` + `content_type` + `content_base64`. Use for sensitive documents — never publicly hosted.
  - **URL fetch**: `url` + `method` + optional `headers`. The server fetches it server-side at inference time.
- `cre_callback` — optional. When the request reaches a terminal state, the server POSTs `{"input": <full status object>}` to the URL once (10 s timeout, no retries, best-effort).

**Response: 202 Accepted**

```json
{ "id": "019ea785-...", "status": "queued" }
```

---

## GET /v1/inference/{id}

Poll for status and result.

**Response (completed):**

```json
{
  "id": "019ea785-...",
  "status": "completed",
  "model": "gemma4",
  "system_prompt": "...",
  "prompt": "...",
  "output": "LLM response text",
  "usage": { "prompt_tokens": 1898, "completion_tokens": 1531 },
  "resource_summaries": [],
  "created_at": "2026-06-07T17:26:19Z",
  "started_at": "2026-06-07T17:26:19Z",
  "completed_at": "2026-06-07T17:27:43Z"
}
```

When `status` is `failed`, the `error` field is populated instead of `output`.

**Status values:**

| Status | Meaning |
|--------|---------|
| `queued` | Waiting for a worker |
| `preparing-resources` | Fetching or preprocessing resources |
| `processing` | LLM is running |
| `completed` | Done — `output` is populated |
| `failed` | Error — check `error` field |

Poll every 2–5 seconds until `completed` or `failed`.

---

## GET /v1/models

Returns the list of available models. No request body.

---

## Available Models

| Model | Best for |
|-------|----------|
| `gemma4` | Images, screenshots, general use (default) |
| `qwen3.6` | Long text documents, high token count |

---

## Error Codes

| HTTP status | Meaning |
|-------------|---------|
| `400` | Malformed body or unsupported model |
| `401` | Missing or invalid `Authorization` header |
| `429` | Too many concurrent requests for this API key |
| `503` | Server at capacity or in maintenance — retry with backoff |
