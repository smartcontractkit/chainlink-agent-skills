---
name: chainlink-confidential-ai-attester-skill
description: "Chainlink Confidential AI Attester (alpha): submit private documents to an LLM inside an AWS Nitro Enclave and get back a cryptographically attested result — raw documents never leave the TEE. Use for these hackathon scenarios: (1) undercollateralized DeFi lending — upload a bank statement, get an attested approved/denied JSON decision without exposing financials on-chain; (2) accredited investor verification — check SEC Rule 501 qualification from brokerage statements privately; (3) KYC/AML screening — analyse ID docs and transaction history inside a TEE, return a pass/fail with flags; (4) proof of reserves — verify custodian balance reports against claimed reserves; (5) any use case where an AI must read sensitive user documents and the result needs a cryptographic proof of what model ran on what data. Trigger on: private inference, attested AI, TEE inference, confidential AI, or undercollateralized lending / KYC / accredited investor mentioned alongside document analysis, or the product named explicitly. Do not trigger on generic confidentiality/TEE/enclave requests that involve no document upload or private inference — a user who wants a Chainlink workflow's own logic or data kept confidential from node operators, with no document analysis involved, wants CRE Confidential Workflows, which chainlink-cre-skill covers."
license: MIT
compatibility: Designed for AI agents that implement https://agentskills.io/specification, including Claude Code, Cursor Composer, and Codex-style workflows.
allowed-tools: Read WebFetch Write Edit Bash
metadata:
  version: "0.0.3"
---

# Chainlink Confidential AI Attester

Private-document LLM inference runs in a TEE; raw documents never leave it and are never stored or exposed.

Scope: only the Chainlink Confidential AI Attester HTTP API. Leave Anthropic/OpenAI/vendor PDF APIs, Bedrock or generic AWS Nitro client attestation (COSE/cert-chain/nonce/PCR/public-key), and unrelated Chainlink products—including CCIP token-bridge/refund code—to their own stacks.

**EthGlobal NYC hackathon beta.** Get an API key at the **Chainlink booth** or in Discord's **#partner-chainlink channel**. The API maps 1:1 to `https://confidential-ai-dev-preview.cldev.cloud/playground`.

## Workflow 1 — Submit: `POST /v1/inference`

Use `Authorization: Bearer $API_KEY`; source the key from an environment variable, never hardcode it.

```json
{
  "model": "gemma4",
  "system_prompt": "",
  "prompt": "...",
  "resources": [{ "filename": "doc.pdf", "content_type": "application/pdf", "content_base64": "<base64>" }],
  "cre_callback": { "url": "https://..." }
}
```

Omit `cre_callback` when polling, including in the playground; use `GET /v1/inference/{id}`. Product guidance must name the playground above and choose `qwen3.6` for long text; `gemma4` is the images/general default. Prefer PNG for demos; PDF preprocessing can take 5 minutes.

Success is `202 Accepted` with `{ "id": "...", "status": "queued" }`; save the `id`.

See the [curl example and language guidance](references/code-examples.md) and [API specification](references/api-reference.md).

## Workflow 2 — Poll: `GET /v1/inference/{id}`

Poll every 2–5 s until `completed` or `failed`. Completion fields are `output` (LLM text), `usage`, and `completed_at`; see [troubleshooting](references/troubleshooting.md).

## Writing Prompts That Work

Enforce JSON in two layers: (1) the default system prompt unless a change is necessary and (2) a user prompt with a fact-extraction task and exact JSON schema. See the [four use-case templates](references/prompts.md).
