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
- **Always pass `--non-interactive`** with `cre init` plus the required flags (`--project-name`, `--deployment-registry`, `--template`). A deployment registry ID is needed for the run to be genuinely non-interactive. Without `--non-interactive`, the command prompts for input.
- **Request JSON output whenever the command supports it** so you can parse results reliably instead of scraping human-formatted text. The flag differs by command:
  - `cre templates list --json`
  - `cre workflow list --output json`
  - `cre workflow supported-chains --output json`

  These are the only commands that currently support JSON output. Note the flag style differs: `templates list` uses the boolean `--json`, while `workflow list` and `workflow supported-chains` use `--output json`. Do not pass `--json` to commands that don't list it (it will error).

## Global Flags

| Flag | Description |
|------|-------------|
| `-h`, `--help` | Show help for any command |
| `-e`, `--env <path>` | Specify the `.env` file path (default: `.env`) |
| `-E`, `--public-env <path>` | Specify the shared, non-sensitive `.env.public` file path |
| `-T`, `--target <name>` | Set the target environment from the project configuration |
| `-R`, `--project-root <path>` | Specify the project root directory |
| `-v`, `--verbose` | Enable debug logging |
| `--non-interactive` | Fail instead of prompting; provide required inputs through flags or environment variables |
## Authentication Commands

### `cre login`

Authenticate with the CRE platform. Opens a browser for interactive login (password, plus 2FA if enabled). The agent can run this command, but the user must complete the browser-based sign-in themselves; the agent continues once the command returns.

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
| `--deployment-registry` | Deployment registry the new project targets | Yes (required to guarantee non-interactive behavior; omitting it can still prompt for registry selection) |
| `-w, --workflow-name` | Name for the new workflow | No |
| `-t, --template` | Template name (e.g., `hello-world-ts`, `hello-world-go`) | No (but recommended) |
| `--rpc-url` | RPC endpoint, format: `chain-name=url` (repeatable) | Depends on template |
| `--refresh` | Bypass template cache and fetch from GitHub | No |

Always use `--non-interactive` when running as an agent to prevent the CLI from waiting for input. Always pass `--deployment-registry <ID>` so the run is genuinely non-interactive; omitting it can still prompt for registry selection. Valid registry IDs are scoped to the logged-in user's account and organization rather than a fixed global list, so use authenticated `cre registry list` to obtain or confirm an available ID instead of hardcoding or guessing.

Non-interactive example:

```bash
cre init \
  --non-interactive \
  --project-name my-project \
  --deployment-registry <your-deployment-registry> \
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
| `--evm-receipt-timeout` | Max wait for an EVM transaction receipt (not an overall simulation timeout); only on CLI versions that expose it | No |
| `--broadcast` | Execute onchain writes via MockKeystoneForwarder | No |
| `--limits` | Production limits: `default`, file path, or `none` | No |
| `--skip-type-checks` | Skip TypeScript typecheck during compile | No |

There is no generic overall simulation `--timeout` flag. Run `cre workflow simulate --help` to list the flags available in the installed CLI version.

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
- Early Access approval (request it with `cre account access`)

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

| Flag | Description |
|------|-------------|
| `--output json` | Print the workflow list as a JSON array to stdout. Use this when running as an agent so the output can be parsed. |
| `--include-deleted` | Include workflows in `DELETED` status |

Agent example (machine-readable output):

```bash
cre workflow list --target <target-name> --output json
```

### `cre workflow show`

Show details of a specific deployed workflow.

```bash
cre workflow show <workflow-dir> --target <target-name>
```

### `cre workflow supported-chains`

List chains and mock forwarder addresses available for your tenant.

```bash
cre workflow supported-chains --target <target-name>
```

| Flag | Description |
|------|-------------|
| `--output json` | Print the supported chains as a JSON array to stdout. Use this when running as an agent so the output can be parsed. |

Agent example (machine-readable output):

```bash
cre workflow supported-chains --target <target-name> --output json
```

## Account Commands

### `cre account access`

Check whether the organization has deployment access. If access is not enabled, submit an Early Access request from the CLI.

```bash
cre account access
```

Requires an authenticated CLI session. Run `cre login` first. The interactive request asks for a brief description of the use case, then confirms that the request was submitted. The Chainlink team follows up by email.

This command has no command-specific flags. The global flags listed above apply.

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

## Templates Commands

### `cre templates list`

List all templates available from the configured repository sources. These can be installed with `cre init`.

```bash
cre templates list
```

| Flag | Description |
|------|-------------|
| `--json` | Output the template list as JSON. Use this when running as an agent so the output can be parsed. |
| `--refresh` | Bypass the cache and fetch fresh data from the source repositories |

Agent example (machine-readable output):

```bash
cre templates list --json
```

### `cre templates add`

Add a template repository source.

```bash
cre templates add <repository-source>
```

### `cre templates remove`

Remove a template repository source.

```bash
cre templates remove <repository-source>
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

- CLI installation: `https://docs.chain.link/cre/getting-started/cli-installation.md`
- CLI reference: `https://docs.chain.link/cre/reference/cli.md`
