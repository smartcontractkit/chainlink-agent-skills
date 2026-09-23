# ACE API Usage

Read to call or generate code for the managed ACE Coordinator, Evaluation (MVP), or Reporting APIs: choosing an API, auth, endpoints, request/response shapes, pagination, errors, and curl/SDK sketches. Scope, Beta limits, and audit guardrails: [platform-and-beta.md](platform-and-beta.md).

**Verified against** the official OpenAPI specs Coordinator `0.1.0`, Reporting `1.0.0`, Evaluation `0.1.0`, and `https://docs.chain.link/ace/reference/apis.md`. Specs are Beta and change: re-fetch the relevant spec before relying on a path, field, or enum, say when you verified it, and name any drift from this file. Only use endpoints and fields present in the spec; do not extrapolate from the UI or OSS contracts.

| Spec | URL |
| --- | --- |
| Coordinator | `https://docs.chain.link/api/ace/coordinator/openapi.json` |
| Evaluation (MVP) | `https://docs.chain.link/api/ace/evaluation/openapi.json` |
| Reporting | `https://docs.chain.link/api/ace/reporting/openapi.json` |
| Offchain permits guide | `https://docs.chain.link/ace/guides/policy-manager/offchain-policies/request-offchain-permits.md` |

## Which API When

| Need | API | Base URL | Access |
| --- | --- | --- | --- |
| Create/update/archive engines, policies, targets, protections, extractors, registries, identities, credentials, wallets | Coordinator | `https://ace.api.chain.link/v1` | read-write control plane |
| Get a permit for a function protected by a managed offchain risk policy (TRM wallet risk) | Evaluation (MVP) | `https://ace.api.chain.link/v1/evaluation` | read-write runtime |
| Audit/monitor: policy runs, point-in-time policy/target/identity state, permits, registry usage | Reporting | `https://ace.api.chain.link/v1/reporting` | read-only evidence |

Coordinator reads (`GET`) show managed configuration, not audit evidence; use Reporting for evidence and reconcile it onchain. Evaluation is MVP: tell the user to contact their Chainlink representative before integrating.

## Auth and Key Handling

All three: header `Authorization: Apikey <API_KEY>`. The key is created in the Chainlink App (`https://app.chain.link`) and grants org-wide read-write access to ACE resources, including through read-only-looking scripts.
- Never ask for, accept, echo, or store the key in chat, code, client-side bundles, or agent-readable files. Reference `$ACE_API_KEY` from the user's environment or secret manager; if a key is pasted, tell the user to rotate it and do not use it.
- Server-side only; never call these APIs from a browser.
- Generate curl/SDK code freely. Run only read-only calls (`GET`), and only when the user has already configured the key outside the agent's view.
- Coordinator `POST`/`PUT`/`PATCH`/`DELETE` and Evaluation `POST /evaluate` are user-run artifacts: show the ACE preflight from `SKILL.md`, get explicit approval, and let the user run them. Coordinator writes can deploy or reconfigure onchain contracts.

## Coordinator API (`/v1`)

Most resources: `POST` create, `GET` list, `GET /{id}`, `PUT` update, `PATCH` archive (body `{"status": ...}`; returns `202`). IDs are UUIDs; `chain_selector` is a string.

| Path | Purpose | Required create body |
| --- | --- | --- |
| `GET /networks`, `/networks/{chain_selector}` | supported networks | — |
| `GET /organizations/me` | caller's org | — |
| `GET/POST /wallets` | CRE Connect wallets | `wallets` |
| `/policy-engines` | PolicyEngine instances | `name`, `onchain_policy_engines` |
| `/policy-implementations` | library + custom implementations | `name`, `description`, `policy_config_schema` |
| `/policies` | onchain or offchain policy instances (`policy_kind`) | onchain: `name`, `policy_implementation_id`, `policy_engine_id` |
| `PATCH /policies/{id}/configs` | JSON-patch config | — |
| `PUT /policies/{id}/config` | offchain config (redeploys workflow) | `config` |
| `/policies/{id}/protections` | offchain protections (`GET`, `DELETE`) | — |
| `/policies/{id}/targets/{target_id}/access-grants` | cross-org evaluation access | `grantee_org_id` |
| `/targets` | protected contracts | `title`, `policy_engine_id` |
| `POST /targets/{id}/merge` | merge targets | `source_target_ids` |
| `/targets/{id}/protections` | attach policy to selector | `function_signature`, `policy_instance_id` |
| `/extractors` | calldata extractors | `name`, `supported_function_signatures`, `outputs` |
| `/data-validators` (+ `PATCH /{id}/configs`) | credential-data validators | `name`, `data_validator_implementation_id` |
| `/registries` (+ `/{id}/access-grants`) | identity + credential registries | `name`, `description` |
| `/identities`, `POST /identities/batch` | CCIDs and wallet mapping | `title`, `entity_id`, `registry_id`, `onchain_identities` |
| `/credential-types` | credential types | `registry_id`, `title`, `credential_type` |
| `/credentials` | issued credentials | `credential_type_id`, `identity_id` |

The system policy engine (`type: "system"`) is reserved for registry protection; its targets/policies cannot be created or changed. Archive is rejected while dependants are active (e.g., engine with policies, policy with protections).

**Pagination:** `page` (≥1, default 1), `page_size` (1–100, default 10); response has `page`, `total`, `total_pages` plus the resource array (e.g., `policy_engines`). `include_onchains=true` adds per-chain deployments.
**Errors:** `{"error": "...", "message": "..."}`; `error` ∈ `Bad request`, `Unauthorized`, `Forbidden`, `Not found`, `Already exists` (`409`), `Method not allowed`, `Internal error`.

## Evaluation API (`/v1/evaluation`, MVP)

| Method/path | Body or result |
| --- | --- |
| `POST /evaluate` | req: `caller_address`, `subject`, `function_signature` (canonical, e.g. `transfer(address,uint256)`), `parameters` (object), `chain_selector` (string), `unique_evaluation_id`; optional `permit_parameters` (0x 32-byte ABI words, in the protection's `extractor_output_ids` order; `transfer` = `[from, to, amount]`) → `{permit_id, status}` |
| `GET /evaluate/{permitId}` | `{permit_id, status, reason, workflow_execution_id, expires_at}` |

Status: `evaluating` → `approving` → `ready`; terminal `ready | rejected | error`. Submit the protected tx only at `ready`, from `caller_address`, with args that extract to the same `permit_parameters` (no permit bytes are added). `rejected`: no permit; read `reason`, do not retry blindly. `error`: after fixing, wait ≥60 s and use a new `unique_evaluation_id`. `unique_evaluation_id` is the idempotency key: retry a lost response with the same ID; never reuse it for a different intent. Poll ~5 s. `expires_at` is currently normally `null`. Encode words with an ABI library, not string concatenation. Errors: `{error, message}`; `404` if the permit belongs to another org.

## Reporting API (`/v1/reporting`, read-only)

| Path | Required | Notable filters |
| --- | --- | --- |
| `GET /policies` | `as_of` | `policy_engine_address`, `owner`, `chain_selector`, `include_policy_details` |
| `GET /policies/{chain_selector}/{address}` | `as_of` | `include_policy_details` |
| `GET /policies/{chain_selector}/{address}/versions/{version}` | — | — |
| `GET /targets`, `/targets/{chain_selector}/{address}` | `as_of` | `policy_engine_address`, `chain_selector`, `include_policy_details` |
| `GET /identities`, `/identities/{ccid}` | `as_of` | `address`, `identity_registry`, `credential_registry`, `credential_type_id`, `include_credential_details` |
| `GET /transactions`, `/transactions/{chain_selector}/{tx_hash}` | — | `from`, `to`, `from_address`, `to_address`, `target_contract_address`, `function_selector`, `policy_address`, `policy_engine_address`, `sort` |
| `GET /permits` | — | `chain_selector`, `policy_address`, `permit_id`, `from`, `to` |
| `GET /registry-usage/events` | `registry_type`, `chain_selector`, `registry_address` | `ccid`, `from`, `to` |

`as_of`, `from`, `to` are ISO 8601 date-times; `from`/`to` are inclusive bounds on block timestamp. Transactions `sort`: `chain_selector,-block_number` (default) or `chain_selector,block_number`. Each transaction has `policy_runs[].on_chain` with `target_contract_address`, `engine_address`, `method.selector`, `policies`, `params`, `context`, `engine_default_behavior`, `target_default_behavior`, `extractor_address`. Empty filters return `200` with `[]`, not `404`.

**Pagination:** `page_size` (1–100, default 20) + `page_token`; continue with `next_page_token` until it is `null`.
**Errors:** `{"message", "code", "request_id"}` (`code` e.g. `BAD_REQUEST`, `NOT_FOUND`); quote `request_id` to support.

Do not mix schemes: Coordinator is page-number based with `{error, message}`; Reporting is token based with `{message, code, request_id}`.

## Sketches

Placeholders stay placeholders; the user fills IDs and runs writes.

```bash
# 1. List policy engines (read-only)
curl -s "https://ace.api.chain.link/v1/policy-engines?page=1&page_size=50&include_onchains=true" \
  -H "Authorization: Apikey $ACE_API_KEY"
```

```bash
# 2. Create policy, then protect a selector (USER-RUN writes; preflight first)
curl -s -X POST https://ace.api.chain.link/v1/policies \
  -H "Authorization: Apikey $ACE_API_KEY" -H "Content-Type: application/json" \
  -d '{"policy_kind":"onchain","name":"<NAME>","policy_implementation_id":"<IMPL_ID>",
       "policy_engine_id":"<ENGINE_ID>","onchain_policies":[{"chain_selector":"<CHAIN_SELECTOR>","initial_config":{}}]}'
curl -s -X POST https://ace.api.chain.link/v1/targets/<TARGET_ID>/protections \
  -H "Authorization: Apikey $ACE_API_KEY" -H "Content-Type: application/json" \
  -d '{"function_signature":"transfer(address,uint256)","policy_instance_id":"<POLICY_ID>",
       "desired_position":1,"onchain_target_protections":[{"chain_selector":"<CHAIN_SELECTOR>"}]}'
```

```bash
# 3. Evaluate -> poll -> submit (MVP; POST is user-run)
B=https://ace.api.chain.link/v1/evaluation
PID=$(curl -s -X POST $B/evaluate -H "Authorization: Apikey $ACE_API_KEY" -H "Content-Type: application/json" \
  -d '{"caller_address":"<FROM>","subject":"<FROM>","function_signature":"transfer(address,uint256)",
       "parameters":{"to":"<TO>","amount":"<AMOUNT>"},"permit_parameters":["<FROM_WORD>","<TO_WORD>","<AMOUNT_WORD>"],
       "chain_selector":"<CHAIN_SELECTOR>","unique_evaluation_id":"<STABLE_UUID>"}' | jq -r .permit_id)
while :; do S=$(curl -s $B/evaluate/$PID -H "Authorization: Apikey $ACE_API_KEY" | jq -r .status)
  case $S in ready) break;; rejected|error) echo "$S"; exit 1;; esac; sleep 5; done
# only now: user signs and sends transfer(<TO>, <AMOUNT>) from <FROM>
```

```bash
# 4. Transactions for a target in a window, all pages (read-only)
R=https://ace.api.chain.link/v1/reporting; T=""
while :; do J=$(curl -s -G $R/transactions -H "Authorization: Apikey $ACE_API_KEY" \
  --data-urlencode "chain_selector=<CHAIN_SELECTOR>" --data-urlencode "target_contract_address=<TARGET>" \
  --data-urlencode "from=<FROM_ISO8601>" --data-urlencode "to=<TO_ISO8601>" \
  --data-urlencode "page_size=100" ${T:+--data-urlencode "page_token=$T"})
  echo "$J" | jq -c '.transactions[]'; T=$(echo "$J" | jq -r '.next_page_token // empty'); [ -z "$T" ] && break; done
```

For a cutoff snapshot, call `GET /policies`, `/targets`, `/identities` with the same `as_of`, then reconcile against onchain logs and state.
