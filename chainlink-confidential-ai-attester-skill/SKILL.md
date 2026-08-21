---
name: chainlink-confidential-ai-attester-skill
description: "What it does: Chainlink Confidential AI Attester (alpha) sends private documents to an LLM inside an AWS Nitro Enclave and returns a cryptographically attested result; raw documents never leave the TEE. When to use it: use for Chainlink Confidential AI Attester, private inference, attested AI, TEE inference, confidential AI, or sensitive-document analysis needing proof of the model result—such as undercollateralized lending, accredited-investor verification, KYC/AML, or proof of reserves. Key capabilities: submit document resources to the HTTP API, choose the model, require structured JSON output, poll for completion, and use the attested result without exposing source documents on-chain. Do not use for generic TEE/enclave work without document inference; use CRE Confidential Workflows for confidential Chainlink workflow logic."
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
