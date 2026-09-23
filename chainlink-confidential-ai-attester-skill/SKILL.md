---
name: chainlink-confidential-ai-attester-skill
description: "What it does: Chainlink Confidential AI Attester (alpha) runs an LLM inside AWS Nitro Enclave/TEE over private documents and returns the model result; raw documents do not leave TEE. When to use: trigger on private inference, attested AI, TEE inference, confidential AI, or sensitive-document analysis, including lending, accredited-investor, KYC/AML, and proof-of-reserves. Key capabilities: submit document resources, choose model, request structured JSON, poll completion, and use the result without exposing source documents onchain. Do not use for generic TEE/enclave work without document inference; use CRE Confidential Workflows for confidential Chainlink workflow logic. Do not trigger on generic confidentiality/TEE/enclave requests that involve no document upload or private inference — a user who wants a Chainlink workflow's own logic or data kept confidential from node operators, with no document analysis involved, wants CRE Confidential Workflows, which chainlink-cre-skill covers."
license: MIT
compatibility: Designed for AI agents that implement https://agentskills.io/specification, including Claude Code, Cursor Composer, and Codex-style workflows.
allowed-tools: Read WebFetch Write Edit Bash
metadata:
  version: "0.0.3"
---

# Chainlink Confidential AI Attester

Private-document LLM inference runs in a service-managed TEE; raw documents never leave it and are never stored or exposed.

Scope: only the Chainlink Confidential AI Attester document-inference HTTP API. Data Feeds, CCIP, AI architecture or zkML, Anthropic or other vendor PDF APIs, and AWS Nitro/Bedrock attestation stay with their owning product or vendor; do not introduce Attester. For any request outside Attester document inference, state that this capability does not apply, route to the owning capability, and do not provide any Attester API or playground procedure.

**EthGlobal NYC hackathon beta.** Get an API key at the **Chainlink booth** or in Discord's **#partner-chainlink channel**. The playground at `https://confidential-ai-dev-preview.cldev.cloud/playground` and the HTTP API are two access paths to the same Attester service, not separate privacy options.

## Workflow 1 — Submit: `POST /v1/inference`

Use `Authorization: Bearer $API_KEY`; load the key from an environment variable or injected secret store, never hardcode it or place its literal or expanded value in command-line arguments. Set the service URL in `BASE_URL` (or an equivalent environment variable) and use it in every command or code sample; never inline the service base.

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

## Verification Boundary and EVM Delivery

The Attester API does not expose an independently verifiable Chainlink signature or TEE attestation document. Hashing response fields can detect a later change to those fields, but a response hash is neither an independently verifiable Chainlink signature nor a TEE attestation and does not prove that inference ran in an enclave.

For EVM delivery, validate a completed result and its required JSON schema, create a CRE-native report, and deliver that report through the Chainlink Forwarder. Treat failed or non-JSON output as failure and create no report. Do not use a generic EIP-712 signer or application private key to present Attester output as confidential-compute proof.

Every signed-summary or verify-later answer must state one credential rule: `API_KEY` comes from an environment variable or injected secret store, never a CLI argument.

## Writing Prompts That Work

Enforce JSON in two layers: (1) the default system prompt unless a change is necessary and (2) a user prompt with a fact-extraction task and exact JSON schema. Emit the requested `system_prompt`, user `prompt`, and schema in full; never replace them with a summary. See the [four use-case templates](references/prompts.md).

## Choose the Privacy Approach

| Option | Use when | Tradeoff |
|--------|----------|----------|
| Attester | You want managed document inference inside the service's Nitro Enclave | Fastest integration, but the current API provides no independently verifiable Chainlink or TEE signature |
| Local model | Data must remain on a controlled device with no external inference call | You operate the model and hardware; locality alone provides no remote attestation |
| Self-hosted confidential compute | You need infrastructure control and can operate a TEE and its attestation verification | Most control and potential for independent attestation, with the highest operational burden |
| Redaction or tokenization | The task can work on minimized or substituted data before any external call | Simplest data minimization, but may reduce utility and does not eliminate re-identification risk |

The playground and API are interfaces to one Attester service; choose between them for interaction style, not as distinct privacy architectures.
