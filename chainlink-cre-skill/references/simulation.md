# Simulation

Always read this file before any `cre workflow simulate`. Run from the project root containing `project.yaml`.

## Canonical command and flags

This file owns the command shape:

```bash
cre workflow simulate <workflow-dir> --target <target-name>
```

`--target` is mandatory; omission prompts for a target. Supply every value the CLI would otherwise request:

| Flag | Use |
|---|---|
| `--target` | target from `workflow.yaml`; always |
| `--non-interactive` | forbid prompts |
| `--trigger-index` | 0-based handler; required with non-interactive mode |
| `--http-payload` | HTTP JSON string or JSON-file path (relative to the run directory) |
| `--evm-tx-hash` | transaction containing the selected log |
| `--evm-event-index` | 0-based log index when needed |
| `--evm-receipt-timeout` | receipt wait only, not overall timeout; CLI-version dependent |
| `--broadcast` | real testnet transaction via `MockKeystoneForwarder` |
| `--limits` | `default`, limits-file path, or `none` |
| `--skip-type-checks` | skip TypeScript checking |

There is no generic overall `--timeout`; confirm version-specific flags with `cre workflow simulate --help`.

Fully non-interactive examples:

```bash
cre workflow simulate my-workflow --target staging-settings \
  --non-interactive --trigger-index 0 \
  --http-payload '{"key":"value"}'
```

```bash
cre workflow simulate my-workflow --target staging-settings \
  --non-interactive --trigger-index 1 \
  --evm-tx-hash 0x... --evm-event-index 0
```

A single cron handler often needs only `--target`; add `--non-interactive --trigger-index 0` if selection still prompts. Exercise each handler in a separate non-interactive run.

## Receiver-free handler-0 simulation

Use the CRE CLI—not a source-level harness—when handler 0 must run before a receiver contract exists. Define [project-scaffolding.md](project-scaffolding.md)'s matching `local-simulation` targets in `project.yaml` and `workflow.yaml`; the workflow target uses the supported literal `deployment-registry: "private"`, never a guessed account-scoped registry ID, `local-simulation-only`, or a fake receiver.

Run this exact command from the project root:

```bash
cre workflow simulate <workflow> --target local-simulation --non-interactive --trigger-index 0
```

Keep `--broadcast` absent. This path still requires CRE CLI login, but it does not require an account-scoped registry ID or deployed receiver.

The selected config must set `mode: "local-simulation"` and a decimal-string `samplePreviousPrice`. Handler 0 must:

1. perform the same real configured HTTP capability fetches as production;
2. apply the same response/status checks, strict decimal validation and scaling, `bigint` bounds, and consensus aggregation;
3. validate and scale `samplePreviousPrice` by the same rules and run the normal changed-price/threshold decision; and
4. log and return a clearly labeled local result such as `{ mode: "local-simulation", currentPrice, previousPrice, changed, wouldWrite }`, with integer values stringified.

After step 4 the local branch returns. It must not validate or invent a receiver, construct a CRE report or `EVMClient`, call a Forwarder, accept a signer, or expose another write path. Do not replace real HTTP observations with injected fixtures or duplicate the handler in a local script.

Every non-local branch is production: reject unknown modes; require a configured, well-formed, nonzero receiver; retain CRE report creation and Forwarder delivery for each changed-price write; resolve every capability with `.result()`; and fail closed on validation, report, delivery, or missing-transaction-hash errors.

The local target is simulation-only. Never select it for `--broadcast`, deploy, update, activate, or another lifecycle command, and never allow a production target/config to set `mode: "local-simulation"`. Even if a user mistakenly appends `--broadcast`, the handler's early return must leave no report, EVM client, or transaction to send.

## Behavior by trigger

Simulation compiles to WASM, loads the selected target, fires/accepts a local trigger, calls real configured HTTP/RPC endpoints, and prints user logs/result. It is a local dry run by default and does not reproduce every deployed DON behavior.

- **Cron:** fires once immediately; it does not wait for the schedule.
- **HTTP:** interactive mode starts a local server on port 8080 and waits for a request; agents/CI should use `--http-payload`.
- **EVM log:** may monitor configured RPC for a match; deterministic runs provide `--evm-tx-hash`, optional `--evm-event-index`, and a handler index.
- **Multiple handlers:** interactive behavior varies by CLI; automation always selects one handler per run.

| | Simulation | Deployment |
|---|---|---|
| Execution/consensus | local simulator | DON, multi-node consensus |
| Gas | none unless broadcast | real |
| Secrets | environment/`.env` consumed by CLI | Vault DON |
| RPC | configured endpoint | DON EVM capability |
| Writes | `MockKeystoneForwarder` with `--broadcast` | `KeystoneForwarder` |

Without `--broadcast`, simulation does not send a transaction and must remain the default first check. Never fabricate a zero transaction hash for this dry-run path or for a successful write whose response omitted `txHash`.

## Broadcast writes

```bash
cre workflow simulate my-workflow --target staging-settings --broadcast
```

This sends a real testnet transaction and requires a funded wallet available opaquely to the CLI; repeated writes on Base Sepolia require Base Sepolia test ETH. The consumer must trust the target chain's `MockKeystoneForwarder`, not its production forwarder; selector/forwarder values are canonical in [chain-selectors.md](chain-selectors.md) and must be refreshed from its official source before live use. Apply the user's authorization and never inspect key files.

## Focused failures

| Symptom | Cause / fix |
|---|---|
| `Select a target` | add `--target` |
| prompts for body/tx/handler | add matching payload flags plus `--non-interactive --trigger-index` |
| module not found (TS) | in generated workflow: `bun install`, then `bunx cre-setup`; see scaffolding |
| Go dependency stall | from project root try `GOPROXY=direct go mod tidy -v`; private-module environment may need `GONOSUMCHECK`/`GONOSUMDB` |
| `secret not found` | referenced environment variable is unavailable, or the CRE CLI v1.1.0 secret-name substring bug applies; see workflow patterns |
| `workflow-path not found` | run from project root and check the generated `workflow.yaml` relative path |
| `process`/`Buffer`/`crypto` undefined | Node API reached QuickJS; replace with CRE/typed-array/deterministic equivalents |
| apparent hang | EVM log wait or slow RPC; provide tx hash, event index, handler index, and target |

For HTTP interactive testing, a present human may run the simulator and send a JSON POST to `http://localhost:8080/trigger` from another terminal. Agents should prefer `--http-payload`.

## Sources

- https://docs.chain.link/cre/guides/operations/simulating-workflows.md
- https://docs.chain.link/cre/reference/cli/workflow.md
