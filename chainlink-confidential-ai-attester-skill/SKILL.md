---
name: chainlink-confidential-ai-attester-skill
description: "Chainlink Confidential AI Attester: submit private documents to an LLM inside an AWS Nitro Enclave and get back a cryptographically attested result — raw documents never leave the TEE. Use for these hackathon scenarios: (1) undercollateralized DeFi lending — upload a bank statement, get an attested approved/denied JSON decision without exposing financials on-chain; (2) accredited investor verification — check SEC Rule 501 qualification from brokerage statements privately; (3) KYC/AML screening — analyse ID docs and transaction history inside a TEE, return a pass/fail with flags; (4) proof of reserves — verify custodian balance reports against claimed reserves; (5) any use case where an AI must read sensitive user documents and the result needs a cryptographic proof of what model ran on what data. Trigger on: private inference, attested AI, TEE inference, confidential AI, or undercollateralized lending / KYC / accredited investor mentioned alongside document analysis."
license: MIT
compatibility: Designed for AI agents that implement https://agentskills.io/specification, including Claude Code, Cursor Composer, and Codex-style workflows.
allowed-tools: Read WebFetch Write Edit Bash
metadata:
  version: "0.0.1"
---

# Chainlink Confidential AI Attester

Runs LLM inference inside Trusted Execution Environment (TEE). Documents go in, LLM analysis comes out — the raw documents are never stored or exposed.

**Beta product for the EthGlobal NYC hackathon.** Get an API key at the **Chainlink booth** or via the **#partner-chainlink channel in the EthGlobal Discord**.

Playground UI: `https://confidential-ai-dev-preview.cldev.cloud/playground` — easiest way to try it. Everything there maps 1:1 to the API calls below.

---

## Workflow 1 — Submit: `POST /v1/inference`

Auth: `Authorization: Bearer $API_KEY` — always use an env var, never hardcode.

Request shape:
```json
{
  "model": "gemma4",
  "system_prompt": "",
  "prompt": "...",
  "resources": [{ "filename": "doc.pdf", "content_type": "application/pdf", "content_base64": "<base64>" }],
  "cre_callback": { "url": "https://..." }
}
```

- `cre_callback` is optional — omit it and poll instead.
- Models: `gemma4` (images/general, default), `qwen3.6` (long text).
- Prefer PNG over PDF for demos — PDF preprocessing can take up to 5 minutes.

Response: `202 Accepted` → `{ "id": "...", "status": "queued" }` — save the `id`.

For curl examples and multi-language snippets → [references/code-examples.md](references/code-examples.md)  
For full request/response spec, error codes, resource types → [references/api-reference.md](references/api-reference.md)

---

## Workflow 2 — Poll: `GET /v1/inference/{id}`

Poll every 2–5 s until `status` is `completed` or `failed`.

Key fields on completion: `output` (LLM text), `usage`, `completed_at`.

For error symptoms → [references/troubleshooting.md](references/troubleshooting.md)

---

## Writing Prompts That Work

Always enforce JSON output with two layers:
1. **System prompt** — keep the default unless you have a specific reason to change it.
2. **User prompt** — binary question + exact JSON schema to return

For per-use-case prompt templates (lending, KYC, accredited investor, proof of reserves) → [references/prompts.md](references/prompts.md)
