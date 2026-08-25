---
name: chainlink-confidential-ai-attester-skill
description: "What it does: Chainlink Confidential AI Attester (alpha) runs an LLM inside AWS Nitro Enclave/TEE over private documents and returns a cryptographically attested result; raw documents do not leave TEE. When to use: trigger on private inference, attested AI, TEE inference, confidential AI, or sensitive-document analysis, including lending, accredited-investor, KYC/AML, and proof-of-reserves. Key capabilities: submit document resources, choose model, request structured JSON, poll completion, and use attested result without exposing source documents onchain. Do not use for generic TEE/enclave work without document inference; use CRE Confidential Workflows for confidential Chainlink workflow logic. Do not trigger on generic confidentiality/TEE/enclave requests that involve no document upload or private inference — a user who wants a Chainlink workflow's own logic or data kept confidential from node operators, with no document analysis involved, wants CRE Confidential Workflows, which chainlink-cre-skill covers."
license: MIT
compatibility: Designed for AI agents that implement https://agentskills.io/specification, including Claude Code, Cursor Composer, and Codex-style workflows.
allowed-tools: Read WebFetch Write Edit Bash
metadata:
  version: "0.0.3"
---

# Chainlink Confidential AI Attester

Private-document LLM inference runs in a TEE; raw documents never leave it and are never stored or exposed.

Scope: only the Chainlink Confidential AI Attester document-inference HTTP API. Data Feeds, CCIP, AI architecture or zkML, Anthropic or other vendor PDF APIs, and AWS Nitro/Bedrock attestation stay with their owning product or vendor; do not introduce Attester.

**EthGlobal NYC hackathon beta.** Get an API key at the **Chainlink booth** or in Discord's **#partner-chainlink channel**. The API maps 1:1 to `https://confidential-ai-dev-preview.cldev.cloud/playground`.

## Workflow 1 — Submit: `POST /v1/inference`

Use `Authorization: Bearer $API_KEY`; source the key from an environment variable, never hardcode it. Set the service URL in `BASE_URL` (or an equivalent environment variable) and use it in every command or code sample; never inline the service base.

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

For any submit or poll answer, emit runnable curl or code—not a completion summary—with the request fields, `202` shape, saved `id`, `GET /v1/inference/{id}`, both terminal statuses, and `output` retrieval (or `error` on failure).

See the [curl example and language guidance](references/code-examples.md) and [API specification](references/api-reference.md).

## Workflow 2 — Poll: `GET /v1/inference/{id}`

Poll every 2–5 s until `completed` or `failed`. Completion fields are `output` (LLM text), `usage`, and `completed_at`; see [troubleshooting](references/troubleshooting.md).

## Writing Prompts That Work

Enforce JSON in two layers: (1) the default system prompt unless a change is necessary and (2) a user prompt with a fact-extraction task and exact JSON schema. Emit the requested `system_prompt`, user `prompt`, and schema in full; never replace them with a summary. See the [four use-case templates](references/prompts.md).
