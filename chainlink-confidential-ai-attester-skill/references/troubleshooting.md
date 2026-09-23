# Chainlink Confidential AI — Troubleshooting

## File Format

| Format | Action |
|--------|--------|
| PNG/JPG | Base64 upload as `image/png` or `image/jpeg`; set `preprocess: false` (or omit). Fastest and recommended for demos. |
| HTML | Base64 upload as `text/html`; set `preprocess: false` (or omit). Fast and suitable for browser-saved statements. |
| PDF | Convert printable PDFs to PNG. Otherwise allow up to 5 minutes for Docling preprocessing; on timeout, convert and resubmit as PNG. |
| Public URL | Use `{ "url": "https://...", "method": "GET" }`; it must be enclave-reachable. On 4xx, use base64 upload. |

## Error Reference Table

| Symptom | Action |
|---------|--------|
| Docling `context deadline exceeded` | Convert with `qlmanage -t -s 2400 -o /tmp/ file.pdf`; resubmit as `image/png` with `preprocess: false`. |
| URL resource 4xx | Switch to base64 upload. |
| URL resource 5xx | Check reachability, retry, or switch to base64 upload. |
| `401` | Supply a valid `Authorization: Bearer <API_KEY>` header. |
| `429 per_key_limit` | Wait for in-flight requests to complete. |
| `503 queue_full` | Retry with exponential backoff: 5s, 10s, 20s, etc. |
| `503 maintenance_mode` | Wait and retry. |
| Refusal for insufficient information | Before the JSON schema add: "Assess based on available evidence only — do not refuse due to missing documents". |
| Prose instead of JSON | Require "Respond with ONLY a valid JSON object" and include the exact schema. |
| JSON in markdown fences | Require "Do not include markdown formatting, code fences, or any text outside the JSON object". |
| Missing `output` on `completed` | Check `error`, log the full response, and retry. |

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

