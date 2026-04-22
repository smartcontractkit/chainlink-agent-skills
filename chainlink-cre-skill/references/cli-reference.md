# CLI Reference

Use this file when the user asks about specific CLI commands, flags, or usage patterns.

## Trigger Conditions

- "What CRE CLI commands are available?"
- "How do I deploy a workflow?"
- "How do I manage secrets with the CLI?"
- "What flags does `cre workflow simulate` accept?"

Do not use for workflow code patterns (see workflow-patterns.md), getting started tutorial (see getting-started.md), or detailed deployment operations (see operations.md). For simulation details, see simulation.md.

## Non-Interactive Usage

When running CRE CLI commands from an automated agent or script, always provide all required flags explicitly. Several commands display interactive prompts when flags are omitted, which blocks automated execution.

Key rules:
- **Always pass `--target`** on every `cre workflow` and `cre secrets` command. Omitting it triggers a "Select a target" interactive prompt.
- **Always pass `--non-interactive`** with `cre init` plus the required flags (`--project-name`, `--template`). Without `--non-interactive`, the command prompts for input.

## Global Flags

| Flag | Description |
|------|-------------|
| `--help`, `-h` | Show help for any command |
| `--version`, `-v` | Show CLI version |

## Authentication Commands

### `cre login`

Authenticate with the CRE platform. Opens a browser for interactive login with 2FA.

```bash
cre login
```

### `cre logout`

End the current authentication session.

```bash
cre logout
```

### `cre whoami`

Display current authentication status and account details.

```bash
cre whoami
```

Output includes email, organization ID, and linked keys.

## Project Commands

### `cre init`

Initialize a new CRE project. Supports both interactive and non-interactive modes.

```bash
cre init [flags]
```

| Flag | Description | Required with `--non-interactive` |
|------|-------------|-----------------------------------|
| `--non-interactive` | Fail instead of prompting (for CI/CD and agents) | Yes (prevents interactive prompts) |
| `-p, --project-name` | Name for the new project | Yes (when creating a new project) |
| `-w, --workflow-name` | Name for the new workflow | No |
| `-t, --template` | Template name (e.g., `hello-world-ts`, `hello-world-go`) | No (but recommended) |
| `--rpc-url` | RPC endpoint, format: `chain-name=url` (repeatable) | Depends on template |
| `--refresh` | Bypass template cache and fetch from GitHub | No |

Always use `--non-interactive` when running as an agent to prevent the CLI from waiting for input.

Non-interactive example:

```bash
cre init \
  --non-interactive \
  --project-name my-project \
  --workflow-name my-workflow \
  --template hello-world-ts
```

Interactive example (only when a human is present):

```bash
cre init
```

Interactive prompts: project name, language (Go/TypeScript), template, workflow name.

See project-scaffolding.md for complete project creation guidance.

### `cre generate-bindings`

Generate type-safe Go bindings from Solidity ABI files.

```bash
cre generate-bindings --abi-dir <path> --pkg <package-name> --output <output-path>
```

| Flag | Description | Example |
|------|-------------|---------|
| `--abi-dir` | Directory containing ABI JSON files | `contracts/evm/src/abi` |
| `--pkg` | Go package name for generated code | `abi` |
| `--output` | Output directory for generated files | `contracts/evm/src/abi` |

## Workflow Commands

### `cre workflow simulate`

Compile and simulate a workflow locally. For detailed simulation guidance, see simulation.md.

```bash
cre workflow simulate <workflow-dir> --target <target-name>
```

| Flag | Description | Required |
|------|-------------|----------|
| `--target` | Target configuration to use | **Yes** (omitting triggers "Select a target" prompt) |
| `--non-interactive` | Run without prompts; requires `--trigger-index` and trigger inputs | For CI and agents when other prompts would block |
| `--trigger-index` | 0-based handler index to run | **Yes** with `--non-interactive` |
| `--http-payload` | HTTP trigger body: JSON string or path to a JSON file | When an HTTP body is required and not interactive |
| `--evm-tx-hash` | Transaction hash `0x...` for EVM log trigger | When an onchain event must be specified |
| `--evm-event-index` | 0-based log index inside the transaction | When the tx has multiple events |
| `--timeout` | Simulation timeout | No (default: `30s`) |
| `--broadcast` | Execute onchain writes via MockKeystoneForwarder | No |
| `--limits` | Production limits: `default`, file path, or `none` | No |
| `--skip-type-checks` | Skip TypeScript typecheck during compile | No |

**IMPORTANT**: Always include `--target`. If the workflow has HTTP or EVM log handlers, or multiple handlers, the CLI may also prompt for payload, transaction hash, or which handler to run. Pass `--http-payload`, `--evm-tx-hash` / `--evm-event-index`, and for full automation `--non-interactive` with `--trigger-index`. See simulation.md.

Example:

```bash
cre workflow simulate my-workflow --target staging-settings
```

Non-interactive with HTTP:

```bash
cre workflow simulate my-workflow --non-interactive --trigger-index 0 \
  --http-payload '{"key":"value"}' --target staging-settings
```

Non-interactive with EVM log:

```bash
cre workflow simulate my-workflow --non-interactive --trigger-index 1 \
  --evm-tx-hash 0x... --evm-event-index 0 --target staging-settings
```

### `cre workflow deploy`

Deploy a workflow to the CRE network.

```bash
cre workflow deploy <workflow-dir> --target <target-name>
```

| Flag | Description | Required |
|------|-------------|----------|
| `--target` | Target configuration to use | **Yes** |

Prerequisites:
- Logged in (`cre login`)
- Wallet linked (`cre account link-key`)
- Wallet funded with ETH for gas
- Early Access approval

### `cre workflow activate`

Activate a deployed (paused) workflow.

```bash
cre workflow activate <workflow-dir> --target <target-name>
```

### `cre workflow pause`

Pause an active workflow.

```bash
cre workflow pause <workflow-dir> --target <target-name>
```

### `cre workflow delete`

Delete a deployed workflow. This is destructive and permanent.

```bash
cre workflow delete <workflow-dir> --target <target-name>
```

### `cre workflow update`

Update a deployed workflow with new code, config, or secrets references.

```bash
cre workflow update <workflow-dir> --target <target-name>
```

### `cre workflow list`

List all workflows associated with the current account.

```bash
cre workflow list --target <target-name>
```

### `cre workflow show`

Show details of a specific deployed workflow.

```bash
cre workflow show <workflow-dir> --target <target-name>
```

## Account Commands

### `cre account link-key`

Link a wallet key to your organization for workflow deployment.

```bash
cre account link-key --target <target-name>
```

Uses the private key from `CRE_ETH_PRIVATE_KEY` in the `.env` file.

### `cre account list-key`

List all keys linked to your organization.

```bash
cre account list-key
```

### `cre account unlink-key`

Unlink a wallet key. This deletes all workflows associated with that key.

```bash
cre account unlink-key --target <target-name>
```

## Secrets Commands

### `cre secrets create`

Upload secrets for a deployed workflow.

```bash
cre secrets create <workflow-dir> --target <target-name>
```

Reads secret values from `.env` file or environment variables as declared in `secrets.yaml`.

### `cre secrets update`

Update secrets for a deployed workflow.

```bash
cre secrets update <workflow-dir> --target <target-name>
```

### `cre secrets delete`

Delete secrets for a deployed workflow.

```bash
cre secrets delete <workflow-dir> --target <target-name>
```

### `cre secrets list`

List secret namespaces for the current account.

```bash
cre secrets list --target <target-name>
```

## Utility Commands

### `cre update`

Update the CRE CLI to the latest version.

```bash
cre update
```

### `cre version`

Display the current CLI version.

```bash
cre version
```

## Official Documentation

- CLI installation: `https://docs.chain.link/cre/getting-started/cli-installation`
- CLI reference: `https://docs.chain.link/cre/reference/cre-cli`
