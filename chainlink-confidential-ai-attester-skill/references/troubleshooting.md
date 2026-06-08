# Chainlink Confidential AI — Troubleshooting

## File Format Decision Tree

Choose the resource format based on what you have:

```
What file do you have?
│
├── PNG / JPG image
│   → Upload as base64, content_type: "image/png" or "image/jpeg"
│   → preprocess: false (or omit)
│   → Fastest path. Recommended for demos and first tests.
│
├── HTML file
│   → Upload as base64, content_type: "text/html"
│   → preprocess: false (or omit)
│   → Fast. Good for rendered financial statements saved from a browser.
│
├── PDF
│   ├── Simple or printable PDF (can be rendered as image)
│   │   → Convert to PNG first (see commands below), resubmit as image/png
│   └── Must use PDF (conversion not possible)
│       → Allow up to 5 minutes for Docling preprocessing
│       → If timeout → convert to PNG and resubmit
│
└── URL (publicly accessible)
    → Use the url resource field: { "url": "https://...", "method": "GET" }
    → Must be reachable by the enclave server
    → If the URL returns 4xx → switch to base64 upload
```

## Error Reference Table

| Symptom | Likely cause | Fix |
|---------|-------------|-----|
| `status: failed`, error contains `context deadline exceeded` | PDF preprocessing (Docling) timed out | Convert the PDF to PNG using `qlmanage -t -s 2400 -o /tmp/ file.pdf` and resubmit as `image/png` with `preprocess: false` |
| `status: failed`, error contains `resource returned status 4xx` | URL resource is not publicly accessible | Switch to base64 upload instead of a URL resource |
| `status: failed`, error contains `resource returned status 5xx` | Remote server error when fetching URL resource | Check the URL is reachable, retry, or switch to base64 upload |
| `401` HTTP response | Missing or invalid `Authorization` header | Verify `Authorization: Bearer <API_KEY>` is present and the key is correct |
| `429 per_key_limit` | Too many concurrent in-flight requests for this API key | Wait for current requests to complete before submitting new ones |
| `503 queue_full` | Server at capacity | Retry with exponential backoff: wait 5s, 10s, 20s, etc. |
| `503 maintenance_mode` | Planned maintenance | Wait and retry |
| LLM output is "I cannot determine this without more information..." | Prompt is too open-ended and the model is refusing | Add "Assess based on available evidence only — do not refuse due to missing documents" before the JSON schema in the user prompt |
| LLM output is prose, not JSON | Prompt does not enforce JSON format | Add "Respond with ONLY a valid JSON object" to the user prompt and include the exact JSON schema |
| LLM wraps JSON in markdown code fences (` ```json ... ``` `) | Prompt instructions not strong enough | Add "Do not include markdown formatting, code fences, or any text outside the JSON object" |
| `output` field is missing from a `completed` response | Unexpected — should not happen on success | Check `error` field, log the full response, retry the request |

---

## Slow Requests

Most requests complete in 10–60 seconds. The following add significant latency:

| Cause | Expected extra time |
|-------|-------------------|
| `preprocess: true` on a PDF | 2–5 minutes |
| Large images (> 5 MB) | 30–90 seconds for upload + tokenization |
| `qwen3.6` with very long documents | Up to several minutes |
| Server queue backlog | Variable — check `status: preparing-resources` vs `processing` |

If a request is stuck on `preparing-resources` for more than 5 minutes, it is likely a preprocessing timeout. Cancel the request and resubmit with PNG.

