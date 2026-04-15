# CLI Reference

Use this file when the user asks about specific CLI commands, flags, or usage patterns.

## Trigger Conditions

- "What CRE CLI commands are available?"
- "How do I deploy a workflow?"
- "How do I manage secrets with the CLI?"
- "What flags does `cre workflow simulate` accept?"

Do not use for workflow code patterns (see workflow-patterns.md), getting started tutorial (see getting-started.md), or detailed deployment operations (see operations.md).

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

Initialize a new CRE project interactively.

```bash
cre init
```

Interactive prompts:
- Project name
- Language (Go / TypeScript)
- Template (Helloworld, etc.)
- Workflow name

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

Compile and simulate a workflow locally.

```bash
cre workflow simulate <workflow-dir> --target <target-name>
```

| Flag | Description | Default |
|------|-------------|---------|
| `--target` | Target configuration to use | Required |
| `--timeout` | Simulation timeout | `30s` |

Example:

```bash
cre workflow simulate my-workflow --target staging-settings
```

### `cre workflow deploy`

Deploy a workflow to the CRE network.

```bash
cre workflow deploy <workflow-dir> --target <target-name>
```

| Flag | Description |
|------|-------------|
| `--target` | Target configuration to use |

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
