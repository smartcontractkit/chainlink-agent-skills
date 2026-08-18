# Project Scaffolding

Read this file before creating any CRE project. Use `cre init`; never hand-write a project tree, config, or starter files unless the command is unavailable or fails. For generated file meanings and SDK patterns, see [workflow-patterns.md](workflow-patterns.md).

## Prerequisites

- Authenticated CRE CLI (`cre login`; the user completes browser authentication)
- Go 1.25.3+ for Go workflows
- Bun 1.2.21+ for TypeScript workflows
- A funded Sepolia account only when simulation broadcasts or deployment needs gas
- An authenticated deployment-registry ID from `cre registry list`; IDs are account/organization scoped, so never guess one

## Non-interactive initialization

Agents always supply `--non-interactive`, `--project-name`, `--deployment-registry`, and a template. Omitting the registry can still prompt.

An unattended wrapper must fail fast and validate every externally supplied value before use:

```bash
#!/usr/bin/env bash
set -euo pipefail
: "${CRE_DEPLOYMENT_REGISTRY_ID:?Set an ID from cre registry list}"
: "${CRE_TARGET:?Set an exact target from workflow.yaml}"
```

Use those validated variables in `--deployment-registry "$CRE_DEPLOYMENT_REGISTRY_ID"` and `--target "$CRE_TARGET"`; do not defer target discovery to an interactive prompt.

```bash
cre init \
  --non-interactive \
  --project-name my-project \
  --deployment-registry "$CRE_DEPLOYMENT_REGISTRY_ID" \
  --workflow-name my-workflow \
  --template hello-world-ts
```

Repeat `--rpc-url chain-name=url` when a template requires RPC configuration. The `cre init` flag table is canonical here:

| Flag | Meaning | Non-interactive use |
|---|---|---|
| `--non-interactive` | Fail rather than prompt | Always |
| `-p, --project-name` | New project name | Required for a new project |
| `--deployment-registry` | Target registry ID | Required to guarantee no prompt |
| `-w, --workflow-name` | Workflow name | Optional; template default otherwise |
| `-t, --template` | Template name | Supply explicitly |
| `--rpc-url` | Repeatable `chain-name=url` RPC | Template-dependent |
| `--refresh` | Bypass template cache and fetch GitHub | Only when fresh templates are needed |

Interactive `cre init` is for a present human only.

## Templates

Built in and available offline:

- `hello-world-ts`
- `hello-world-go`

Registered Confidential Workflow templates:

- `hello-confidential-workflows-ts`
- `hello-confidential-workflows-go`

Discover current registered templates with `cre templates list --json`; `--refresh` bypasses the cache. The advanced confidential examples `ai-audit-firewall`, `automated-liquidation-protection`, and `automated-portfolio-rebalancing` are clone-only, not valid `-t` values; see [confidential-workflows.md](confidential-workflows.md).

## After initialization

TypeScript dependencies and WASM tooling must be installed from the generated workflow directory:

```bash
cd my-project/my-workflow
bun install
bunx cre-setup
```

`postinstall` may already run `cre-setup`; run it explicitly when install output does not confirm that. For Go, `cre init` creates `go.mod`; from the project root run `GOFLAGS=-mod=mod go mod tidy` if needed. If the module proxy stalls, retry with `GOPROXY=direct go mod tidy -v`; private-module environments may additionally need `GONOSUMCHECK=github.com/smartcontractkit/* GONOSUMDB=github.com/smartcontractkit/*`.

Return to the generated project root (the directory containing `project.yaml`) before simulation. Read [simulation.md](simulation.md) before using its canonical command.

## Generated configuration

Do not replace generated files with guessed examples or vague “generated files” placeholders; when the user asks for the full structure, show the concrete tree produced by `cre init`. Preserve the selected target across:

- root `project.yaml`: shared target/RPC configuration
- workflow `workflow.yaml`: workflow name, entry/config/secrets paths per target
- target config JSON: runtime values (`runtime.config` in TypeScript; handler config parameter in Go)
- root `secrets.yaml`: secret IDs mapped to environment-variable names, never secret values

If one schedule or other invariant must be consistent across targets, update every target's referenced config file. Go's `go.mod` remains at the project root, never inside the workflow directory.

Keep `.env`, WASM output, and dependency/build directories out of version control. Never read secret-bearing `.env` or wallet files; authorized tools may consume them opaquely as described in [operations.md](operations.md).

## QuickJS/WASM fit

TypeScript compiles through Javy/QuickJS rather than Node.js. Use pure-JS packages only; `@chainlink/cre-sdk`, `zod`, and `viem` are compatible. `ethers`, `axios`, `node-fetch`, `ws`, `dotenv`, native/N-API modules, and packages importing Node built-ins are incompatible. No `fs`, `path`, `crypto`, `process`, `http`, `https`, `net`, `stream`, `child_process`, `os`, `worker_threads`, `cluster`, `dgram`, `dns`, `tls`, `vm`, `zlib`, `readline`, Node `events`/`util`/`buffer`, timers, or Node `fetch`.

Use `Uint8Array`/`ArrayBuffer` rather than `Buffer`, CRE HTTP capability APIs rather than Node networking, `runtime.getSecret({ id }).result().value` rather than `process.env`, and deterministic logic (or Go `runtime.Rand()`) rather than Node crypto randomness. [concepts.md](concepts.md) owns the runtime model and compatibility details.

## Sources

- https://docs.chain.link/cre/reference/cli/project-setup-ts.md
- https://docs.chain.link/cre/reference/cli/project-setup-go.md
- https://github.com/smartcontractkit/cre-templates
