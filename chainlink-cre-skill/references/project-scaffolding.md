# Project Scaffolding

Read this file before creating any CRE project. Use `cre init`; never hand-write a project tree, config, or starter files unless the command is unavailable or fails. For generated file meanings and SDK patterns, see [workflow-patterns.md](workflow-patterns.md).

## Execution vs. answer artifacts

When the environment provides filesystem/shell tools and the user asks to set up a project (new or existing) and run a simulation, actually run `cre init`, install dependencies, and run the simulation with those tools; report the real command output, generated paths, and simulation result. Do not write an unattended script and a hand-off checklist while claiming the setup is done — that is not execution.

When no execution tool is available, give the exact `cre init`/install/simulate commands and the file contents they will produce, but label the response as unverified: state plainly that nothing was run in this turn and that the user must run the listed commands themselves. Either way, never answer a "did it work" question with an unearned "yes," and never close with a vague "you run this" hand-off after implying the work is finished. If a runnable example is missing non-sensitive values that do not create a security or deployment decision, use clearly labeled safe sample values instead of returning only an outline or questions. Keep sensitive, account-scoped, deployment, and irreversible values as real prerequisites; never invent them.

**No-tools, from-scratch TypeScript contract:** When execution tools are unavailable and the user requests a new TypeScript starter, prominently state “Nothing was run in this turn,” then show this sequence in order: (1) `cre init --non-interactive --project-name my-project --deployment-registry "$CRE_DEPLOYMENT_REGISTRY_ID" --workflow-name my-workflow --template hello-world-ts`, with `CRE_DEPLOYMENT_REGISTRY_ID` supplied from the user's authenticated `cre registry list`; (2) from the newly generated `my-project/my-workflow`, `bun install`; (3) `bunx cre-setup`; (4) back at the generated project root, `workflow_name=my-workflow; workflow_dir="$PWD/$workflow_name"; target_name="$(grep -m1 -E '^[A-Za-z0-9_.-]+:[[:space:]]*$' "$workflow_dir/workflow.yaml" | sed 's/:.*//')"; : "${target_name:?No target key found in generated workflow.yaml}"`; and (5) `cre workflow simulate "$workflow_name" --target "$target_name" --non-interactive --trigger-index 0`. This is creation-only: never inspect, reference, or reuse an existing directory, and never claim that initialization, installation, setup, or simulation succeeded. Keep account IDs, credentials, and addresses as prerequisites, never samples.

## Prerequisites

- Authenticated CRE CLI (`cre login`; the user completes browser authentication)
- Go 1.25.3+ for Go workflows
- Bun 1.2.21+ for TypeScript workflows
- A funded Sepolia account only when simulation broadcasts or deployment needs gas
- An authenticated deployment-registry ID from `cre registry list`; IDs are account/organization scoped, so never guess one

## Non-interactive initialization

Agents always supply `--non-interactive`, `--project-name`, `--deployment-registry`, and a template. Omitting the registry can still prompt.

An unattended initialization wrapper must fail fast and validate every externally supplied value that `cre init` consumes:

```bash
#!/usr/bin/env bash
set -euo pipefail
: "${CRE_DEPLOYMENT_REGISTRY_ID:?Set an ID from cre registry list}"
```

Use the validated registry ID in `--deployment-registry "$CRE_DEPLOYMENT_REGISTRY_ID"`.

```bash
cre init \
  --non-interactive \
  --project-name my-project \
  --deployment-registry "$CRE_DEPLOYMENT_REGISTRY_ID" \
  --workflow-name my-workflow \
  --template hello-world-ts
```

`cre init` does not accept `--target`; it generates `workflow.yaml` with more than one target block by default — the built-in templates ship a `staging-settings` target (used throughout this skill's own examples) plus at least one more, such as `production`, each with its own target config JSON (for example `config.staging.json` and `config.production.json`). Never hand-pick or guess one of these names and never leave a `<placeholder>` in a command; derive the target programmatically from the generated file in the same run, immediately after `cre init`:

```bash
workflow_dir="$project_root/$workflow_name"
target_name="$(grep -m1 -E '^[A-Za-z0-9_.-]+:[[:space:]]*$' "$workflow_dir/workflow.yaml" | sed 's/:.*//')"
: "${target_name:?No target key found in generated workflow.yaml}"
```

This reads the file's first top-level key — the target name itself, not a field literally called `target:` — because `workflow.yaml` has no such field. Use `$target_name` directly in the following simulate command; never stop the script to ask the user to copy it in by hand:

```bash
cre workflow simulate "$workflow_name" --target "$target_name" --non-interactive --trigger-index 0
```

An unattended wrapper must not require or default `CRE_TARGET` before `cre init`; the authoritative `workflow.yaml` does not exist yet, so that is a circular prerequisite. Initialize first, then read and assign the generated target before simulation in the same run.

When a shared value (schedule, RPC, or other invariant) must stay identical across environments, enumerate every top-level target the same way and write the value into each one's referenced config file — never only the first:

```bash
mapfile -t all_targets < <(grep -E '^[A-Za-z0-9_.-]+:[[:space:]]*$' "$workflow_dir/workflow.yaml" | sed 's/:.*//')
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

For every non-hello-world workflow, replace or remove the generic template's default README, tutorial comments, sample handler/config/secrets, and unused dependencies before the first simulation. Never simulate the untouched template or present that run as validation of the requested workflow, and do not leave hello-world material beside the custom workflow.

If an answer mentions `--broadcast`, deployment, update, or activation, it must explicitly state the prerequisites: CRE Early Access, browser-completed login, a linked funded wallet for the target, uploaded Vault DON secrets when used, and a successful non-broadcast simulation.

## After initialization

TypeScript dependencies and WASM tooling must be installed from the generated workflow directory:

```bash
project_root="$(cd my-project && pwd)"
cd "$project_root/my-workflow"
bun install
bunx cre-setup
cd "$project_root"
```

`postinstall` may already run `cre-setup`; run it explicitly when install output does not confirm that. For Go, `cre init` creates `go.mod`; from the project root run `GOFLAGS=-mod=mod go mod tidy` if needed. If the module proxy stalls, retry with `GOPROXY=direct go mod tidy -v`; private-module environments may additionally need `GONOSUMCHECK=github.com/smartcontractkit/* GONOSUMDB=github.com/smartcontractkit/*`.

For Go, preserve the import paths and WASM runner emitted by the installed `hello-world-go` template; do not replace them from memory. When a complete `main.go` replacement is required, copy those exact version-matched imports and runner from the generated file, then change only the workflow-specific handler and configuration.

The block above is one automated shell sequence: capture `project_root` immediately after `cre init`, before entering any workflow or dependency subdirectory, and return to it before simulation. Never run `cd my-project` from inside `my-project/my-workflow`; that looks for a nonexistent nested project. Read [simulation.md](simulation.md) before using its canonical command.

## Generated configuration

Do not replace generated files with guessed examples or vague “generated files” placeholders; when the user asks for the full structure, show the concrete tree produced by `cre init`. Preserve the selected target across:

- root `project.yaml`: shared target/RPC configuration
- workflow `workflow.yaml`: workflow name, entry/config/secrets paths per target
- target config JSON: runtime values (`runtime.config` in TypeScript; handler config parameter in Go)
- root `secrets.yaml`: secret IDs mapped to environment-variable names, never secret values

The default templates generate at least two targets (`staging-settings` and `production`); a requested schedule or other invariant must be written into every target's referenced config file, not only the one used for simulation — enumerate all targets as shown above rather than updating just the first match. Go's `go.mod` remains at the project root, never inside the workflow directory.

Keep `.env`, WASM output, and dependency/build directories out of version control. Never read secret-bearing `.env` or wallet files; authorized tools may consume them opaquely as described in [operations.md](operations.md).

## QuickJS/WASM fit

TypeScript compiles through Javy/QuickJS rather than Node.js. Use pure-JS packages only; `@chainlink/cre-sdk`, `zod`, and `viem` are compatible. `ethers`, `axios`, `node-fetch`, `ws`, `dotenv`, native/N-API modules, and packages importing Node built-ins are incompatible. No `fs`, `path`, `crypto`, `process`, `http`, `https`, `net`, `stream`, `child_process`, `os`, `worker_threads`, `cluster`, `dgram`, `dns`, `tls`, `vm`, `zlib`, `readline`, Node `events`/`util`/`buffer`, timers, or Node `fetch`.

Use `Uint8Array`/`ArrayBuffer` rather than `Buffer`, CRE HTTP capability APIs rather than Node networking, `runtime.getSecret({ id }).result().value` rather than `process.env`, and deterministic logic (or Go `runtime.Rand()`) rather than Node crypto randomness. [concepts.md](concepts.md) owns the runtime model and compatibility details.

## Sources

- https://docs.chain.link/cre/reference/cli/project-setup-ts.md
- https://docs.chain.link/cre/reference/cli/project-setup-go.md
- https://github.com/smartcontractkit/cre-templates
