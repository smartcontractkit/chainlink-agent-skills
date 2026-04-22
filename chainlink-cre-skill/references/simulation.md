# Simulation

Use this file when the user wants to simulate a CRE workflow, debug simulation failures, or understand simulation behavior.

## Trigger Conditions

- "How do I simulate my CRE workflow?"
- "My simulation is failing"
- "How do I test my workflow locally?"
- "How does simulation differ from deployment?"

Do not use for project creation (see project-scaffolding.md), deployment operations (see operations.md), or workflow code patterns (see workflow-patterns.md).

## Non-Interactive Rule

Pass every value the CLI would otherwise ask for. Missing flags cause interactive prompts or a blocked terminal, which stops agents that cannot type into the prompt.

### Target selection

ALWAYS pass `--target <target-name>` on `cre workflow simulate`. Omitting it makes the CLI ask you to pick a target (for example `staging-settings` vs `production-settings`).

```bash
cre workflow simulate my-workflow --target staging-settings
```

NEVER run without `--target`:

```bash
cre workflow simulate my-workflow
```

### HTTP trigger: request body

If the workflow has an **HTTP trigger** and the CLI needs a body (or you use `--non-interactive`), pass **`--http-payload`**: a JSON string, or a path to a JSON file. Paths are resolved relative to the directory from which you run the command.

### EVM log trigger: onchain event

If the workflow has an **EVM log trigger** and the CLI needs a concrete event (or you use `--non-interactive`), pass **`--evm-tx-hash`** with the transaction hash (`0x...`) that contains the log. Use **`--evm-event-index`** (0-based) when that transaction emitted more than one relevant log and you need a specific index.

### Multi-handler workflows and `--non-interactive`

Use **`--non-interactive`** when the process must not answer any follow-up questions. With `--non-interactive`, the CLI requires **`--trigger-index`**: the 0-based index of the handler to run (first handler is `0`, second is `1`, and so on). Combine **`--target`**, **`--non-interactive`**, **`--trigger-index`**, and the HTTP or EVM flags that match the selected handler.

Examples (see also `https://docs.chain.link/cre/reference/cli/workflow`):

```bash
cre workflow simulate my-workflow \
  --non-interactive \
  --trigger-index 0 \
  --http-payload '{"key":"value"}' \
  --target staging-settings
```

```bash
cre workflow simulate my-workflow \
  --non-interactive \
  --trigger-index 1 \
  --evm-tx-hash 0x420721d7d00130a03c5b525b2dbfd42550906ddb3075e8377f9bb5d1a5992f8e \
  --evm-event-index 0 \
  --target staging-settings
```

A **cron-only** workflow with a single handler often needs only `--target`. If the CLI still asks which handler to run, add `--non-interactive --trigger-index 0`. Run `cre workflow simulate --help` on the installed CLI to confirm flag names for that version.

## Running a Simulation

### Basic Command

```bash
cre workflow simulate <workflow-dir> --target <target-name>
```

| Flag | Description | When required |
|------|-------------|---------------|
| `--target` | Target configuration from `workflow.yaml` | Always (omitting prompts for target) |
| `--non-interactive` | No prompts; you must supply handler index and trigger inputs | Automation and CI |
| `--trigger-index` | 0-based handler index | With `--non-interactive` |
| `--http-payload` | JSON string or path to JSON file for HTTP trigger body | HTTP trigger when a body is required or with `--non-interactive` |
| `--evm-tx-hash` | Transaction hash `0x...` containing the log | EVM log trigger when a tx is required or with `--non-interactive` |
| `--evm-event-index` | 0-based log index inside the transaction | When the tx has multiple events and you must pick one |
| `--timeout` | Simulation timeout | No (default: 30s) |
| `--broadcast` | Real onchain writes (MockKeystoneForwarder) | No |
| `--limits` | Production limits profile or file | No |
| `--skip-type-checks` | Skip TypeScript typecheck | No |

### What Simulation Does

1. Compiles workflow code to WebAssembly
2. Runs the workflow locally using the specified target configuration
3. Simulates trigger events (fires each trigger once)
4. Executes capability calls against real endpoints (RPC, HTTP APIs)
5. Displays output including user logs and the workflow result

### Run Directory

Always run simulation from the **project root directory** (the directory containing `project.yaml`), not from within the workflow subdirectory.

```bash
cd my-project
cre workflow simulate my-workflow --target staging-settings
```

## Simulation by Trigger Type

### Cron Trigger

The simulator fires the cron trigger once immediately without waiting for the schedule.

```bash
cre workflow simulate my-workflow --target staging-settings
```

Expected output:

```
Workflow compiled
[SIMULATION] Simulator Initialized
[SIMULATION] Running trigger trigger=cron-trigger@1.0.0
[USER LOG] Hello world! Workflow triggered.
Workflow Simulation Result:
 "Hello world!"
[SIMULATION] Execution finished signal received
```

### HTTP Trigger

**Interactive (human can use two terminals):** the simulator starts a local HTTP server on port 8080. Send a request from a separate terminal to trigger the workflow.

Terminal 1 (start simulation):

```bash
cre workflow simulate my-workflow --target staging-settings
```

Output:

```
Workflow compiled
[SIMULATION] Simulator Initialized
[SIMULATION] HTTP trigger server started on :8080
[SIMULATION] Waiting for HTTP request...
```

Terminal 2 (send trigger request):

```bash
curl -X POST http://localhost:8080/trigger \
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

After the curl request, Terminal 1 shows the workflow execution result.

**Non-interactive (agents, CI):** pass the same JSON with **`--http-payload`**, and use **`--non-interactive`** with **`--trigger-index`** when the CLI would otherwise prompt for a body or for which handler to run. See the [Non-Interactive Rule](#non-interactive-rule) section.

### EVM Log Trigger

**Default:** the simulator can monitor the chain for matching log events using the RPC endpoint from `project.yaml`. The run may need a long **`--timeout`** because it waits for a matching event.

```bash
cre workflow simulate my-workflow --target staging-settings --timeout 120s
```

**Non-interactive (agents, CI):** pass **`--evm-tx-hash`** (and **`--evm-event-index`** if needed) so the CLI does not ask for a transaction. Use **`--non-interactive`** and **`--trigger-index`** as in the [Non-Interactive Rule](#non-interactive-rule) section.

### Multi-Trigger Workflows

In typical interactive use, the simulator can step through multiple handlers: cron may fire first, HTTP may start a local server, EVM log may monitor the chain, depending on CLI version and prompts.

For **automation**, select one handler per run with **`--non-interactive`**, **`--target`**, **`--trigger-index`**, and the HTTP or EVM flags for that handler. To exercise another handler, run simulate again with a different **`--trigger-index`** and the right **`--http-payload`** or **`--evm-tx-hash`**.

```bash
cre workflow simulate my-workflow --target staging-settings
```

See [Non-Interactive Rule](#non-interactive-rule) for the full flag set.

## Simulation vs Deployment

| Aspect | Simulation | Deployment |
|--------|-----------|------------|
| Execution | Local machine | DON nodes |
| Consensus | Single node (no aggregation) | Multi-node with consensus |
| Gas costs | None | Real gas costs |
| Secrets | From `.env` / environment | From Vault DON |
| RPC calls | Direct to RPC endpoint | Via DON EVM client |
| Onchain writes | Via MockKeystoneForwarder (with `--broadcast`) | Via KeystoneForwarder |

## Onchain Write Simulation (--broadcast)

To test onchain writes during simulation, use the `--broadcast` flag. This deploys a MockKeystoneForwarder and executes the write transaction on a real testnet.

```bash
cre workflow simulate my-workflow --target staging-settings --broadcast
```

This requires:
- A funded wallet (private key in `.env`)
- The consumer contract's forwarder address set to the MockKeystoneForwarder for the target chain (see chain-selectors.md for addresses)

## Common Errors and Fixes

### "Select a target" interactive prompt

**Cause**: `--target` flag was omitted.

**Fix**: Always include `--target`:

```bash
cre workflow simulate my-workflow --target staging-settings
```

### Prompts for HTTP body, EVM transaction hash, or trigger index

**Cause**: The CLI needs input for an HTTP payload, an EVM log (tx hash and optional log index), or which handler to run in a multi-handler workflow, and no flag was passed.

**Fix**: Add **`--http-payload`**, **`--evm-tx-hash`** / **`--evm-event-index`**, and for fully non-interactive runs **`--non-interactive`** with **`--trigger-index`**, as in the [Non-Interactive Rule](#non-interactive-rule) section.

### Compilation error: "cannot find module"

**Cause**: Dependencies not installed.

**Fix (TypeScript)**:

```bash
cd my-workflow
bun install
bunx cre-setup
cd ..
```

If `postinstall` already ran `cre-setup`, `bunx cre-setup` is redundant but safe. See project-scaffolding.md for why `cre-setup` must complete before leaving the workflow directory.

**Fix (Go)**:

```bash
GOFLAGS=-mod=mod go mod tidy
```

### "secret not found" error

**Cause**: Secret declared in `secrets.yaml` but not present in `.env` or environment, OR the env var name is a substring of the secret name (known bug in CRE CLI v1.1.0).

**Fix**: Ensure the `.env` file contains the environment variable referenced in `secrets.yaml`. If the env var name is a prefix of the secret name, rename the env var to avoid the substring conflict (e.g., add a `_VAR` suffix).

### "workflow-path not found" error

**Cause**: Running simulation from the wrong directory, or `workflow.yaml` has an incorrect `workflow-path`.

**Fix**: Run from the project root (where `project.yaml` is). Verify `workflow-path` in `workflow.yaml` points to the correct entry file relative to the workflow directory.

### TypeScript: "X is not defined" (process, Buffer, crypto)

**Cause**: Code or a dependency uses Node.js APIs that are not available in the QuickJS WASM runtime.

**Fix**: Replace Node.js APIs with CRE equivalents:
- `process.env.X` -> `runtime.getSecret("X")`
- `Buffer.from(...)` -> `new Uint8Array(...)`
- `crypto.randomBytes(...)` -> not available; use deterministic logic or Go workflows for randomness
- See project-scaffolding.md for the full list of unsupported APIs

### Go: "go mod tidy" hangs

**Cause**: Module proxy is slow or the CRE SDK module requires special access.

**Fix**: Try direct mode with a timeout:

```bash
GOPROXY=direct go mod tidy -v
```

If the module is in a private repository:

```bash
GONOSUMCHECK=github.com/smartcontractkit/* GONOSUMDB=github.com/smartcontractkit/* GOPROXY=direct go mod tidy
```

### Simulation timeout

**Cause**: Default timeout (30s) may be too short for EVM log triggers or slow RPC endpoints.

**Fix**: Increase the timeout:

```bash
cre workflow simulate my-workflow --target staging-settings --timeout 120s
```

## Official Documentation

- Simulation guide: `https://docs.chain.link/cre/getting-started/overview`
- Deploying workflows: `https://docs.chain.link/cre/guides/workflow/deploying-a-workflow`
