# Node API

Inspect one configured node with `GET` until evidence supports a conclusion, relevant sources are exhausted, access blocks progress, or the user stops. Never mutate the node.

## Preferred client

Use the bundled standard-library client before ad hoc code. From the skill root:

```text
python3 scripts/node_api.py [--config PATH] [--env-file PATH] snapshot
python3 scripts/node_api.py [--config PATH] [--env-file PATH] get /v2/jobs [--all-pages]
```

The default is `<skill-root>/config.yaml`; `--config` selects another fixed-schema file. `--env-file` overlays the environment and, if config is absent, can provide `CHAINLINK_API_URL`, `CHAINLINK_API_KEY`, and `CHAINLINK_API_SECRET`. Never print that file.

Start with `snapshot` for compact statuses/counts across broad useful reads. Use `get` for a sanitized endpoint body when the summary lacks needed evidence. Paths must be root-relative. `--all-pages` follows same-origin next links without an arbitrary overall page budget and stops on an absent or repeated cursor.

The client writes sanitized JSON to stdout; errors go to stderr and exit nonzero. It recursively redacts credential-like keys and secret-like TOML assignments. Report only relevant fields.

Use raw/manual reads only if Python is unavailable or a necessary GET route/content type is unsupported. Keep the same origin, identity, redaction, and pagination stops, and never expose request credentials. `snapshot` is not an allowlist; `get` and the fallback preserve broad GET access.

## Authentication and responses

Join routes to `node_api.url`. Resolve each one-key `env` or `file` credential reference only for a request, then send its value as `X-API-KEY` or `X-API-SECRET`. Never ask for, display, or log resolved values.

Authenticated `/v2` routes accept those headers or the node's `clsession`; `/debug/vars` is session-only. Authentication failure normally returns `401`.

Most `/v2` controllers return JSON:API with resources in `data`. `/v2/ping` and `/v2/build_info` return ordinary JSON; health and profiling routes use native content types. Paginated collections accept positive `size` and `page`, defaulting to `25` and `1`; invalid values return `422`. Responses may include `meta.count`, `links.next`, and `links.prev`. Jobs and pipeline runs default to size `1000`.

Interpret the actual status and endpoint body. Common statuses are `200`, `401`, `404`, and `422`. Public readiness is bodyless `200` or `503`; `/readyz` is `200` or `503`, and `/health` is `200` or `207`.

## Built-in static GET routes

Use any relevant path allowed by the configured account.

| Group | Paths |
|---|---|
| Config | `/v2/config`, `/v2/config/v2` |
| Bridges and external initiators | `/v2/bridge_types`, `/v2/bridge_types/:BridgeName`, `/v2/external_initiators` |
| Transactions and attempts | `/v2/tx_attempts`, `/v2/tx_attempts/evm`, `/v2/transactions`, `/v2/transactions/:TxHash`, `/v2/transactions/evm`, `/v2/transactions/evm/:TxHash` |
| Key metadata | `/v2/keys/{csa,eth,evm,ocr,ocr2,p2p,solana,cosmos,starknet,aptos,stellar,tron,sui,ton,vrf,workflow,dkgrecipient}` |
| Jobs, pipelines, and runs | `/v2/jobs`, `/v2/jobs/:ID`, `/v2/pipeline/runs`, `/v2/jobs/:ID/runs`, `/v2/jobs/:ID/runs/:runID` |
| Features and log settings | `/v2/features`, `/v2/log` |
| Chains, nodes, and forwarders | `/v2/chains`, `/v2/chains/:network`, `/v2/chains/:network/:ID`, `/v2/chains/:network/:ID/nodes`, `/v2/nodes`, `/v2/nodes/:network`, `/v2/nodes/evm/forwarders` |
| Build and reachability | `/v2/build_info`, `/v2/ping` |
| Authenticated profiling | `/v2/debug/pprof/`, `/v2/debug/pprof/{cmdline,profile,symbol,trace,allocs,block,goroutine,heap,mutex,threadcreate}` |
| Session-only debug | `/debug/vars` |
| Public health and discovery | `/public-readyz`, `/readyz`, `/health`, `/health.txt`, `/discovery`, `/plugins/:name/metrics`, `/plugins/:name/debug/pprof/*profile` |
| Account and ancestry reads | `/v2/enroll_webauthn`, `/v2/users`, `/v2/find_lca` |

`/v2/find_lca` requires `run` or higher; `/v2/users` requires `admin`. Other authenticated GET registrations above have no explicit role middleware. `/v2/enroll_webauthn` begins enrollment and is rarely diagnostic.

Authentication providers can add runtime routes. Use them only when authenticated, `GET`, relevant, and permitted.

## Sensitive operational data

Bridges and external initiators can return URLs and tokens. Config, chain, and node responses can contain TOML. Jobs and runs can contain pipeline source, inputs, outputs, errors, results, and specs. Transaction attempts can contain signed raw transaction hex.

Inspect these only as needed. Never quote tokens, credential-bearing config, credentials found in job/run data, or raw signed transactions.
