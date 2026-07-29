# Operations

Use this file when the user asks about deploying, monitoring, activating, pausing, updating, or deleting workflows, or about multi-sig wallets.

## Trigger Conditions

- "How do I deploy my CRE workflow?"
- "How do I monitor a deployed workflow?"
- "How do I update a workflow?"
- "How do I pause or delete a workflow?"

For simulation, see simulation.md. Do not use for workflow code patterns (see workflow-patterns.md), CLI command syntax (see cli-reference.md), or first-time setup (see getting-started.md).

## Workflow Lifecycle

```
Init -> Simulate -> Deploy -> Activate -> (Running)
                                  |
                              Pause -> Update -> Activate
                                  |
                              Delete
```

## Simulation

For simulation details including per-trigger-type examples, expected output, common errors, and the `--broadcast` flag, see simulation.md.

Quick reference:

```bash
cre workflow simulate <workflow-dir> --target <target-name>
```

Always include `--target`. For `cre workflow simulate` only, the CLI can also prompt for HTTP request body (**`--http-payload`**), EVM log source (**`--evm-tx-hash`**, **`--evm-event-index`**), or which handler to run; use **`--non-interactive`** with **`--trigger-index`** when you need zero prompts. See simulation.md and cli-reference.md.

## Deployment

### Prerequisites

1. **Early Access approval**: Deployment requires approval for the CRE Early Access program. After logging in, request access with `cre account access`; it reports the organization's status and prompts for a use-case description when access is not enabled.
2. **Authentication**: Run `cre login`; it opens a browser where the user completes the interactive sign-in (password, plus 2FA if enabled), then the agent continues
3. **Linked wallet**: Run `cre account link-key --target <target>` to link a funded wallet
4. **Funded wallet**: Wallet needs ETH on the target chain for gas fees
5. **Secrets uploaded**: If the workflow uses secrets, run `cre secrets create` first

Deployment and workflow management are testnet-only for agent execution. Refuse mainnet deployment, activation, update, pause, delete, and secrets operations.

### Deploy Command

```bash
cre workflow deploy <workflow-dir> --target <target-name>
```

Example:

```bash
cre workflow deploy my-workflow --target staging-settings
```

Always include `--target` on lifecycle commands:

```bash
cre workflow deploy <workflow-dir> --target <target-name>
cre workflow activate <workflow-dir> --target <target-name>
cre workflow update <workflow-dir> --target <target-name>
cre workflow pause <workflow-dir> --target <target-name>
cre workflow delete <workflow-dir> --target <target-name>
cre secrets create <workflow-dir> --target <target-name>
```

## Approval Protocol

Before any deployment, activation, update, pause, deletion, or secrets upload/delete operation, present a preflight summary:

```text
Proposed workflow operation:
- Action: deploy / activate / update / pause / delete / upload secrets / delete secrets
- Network type: testnet
- Target: <target name from workflow.yaml>
- Chain(s): <chain selector name(s) involved>
- Workflow name: <workflow name>
- Secrets: <yes/no, list secret names if yes>
- Consumer contract: <address if applicable>
- Expected effect: <what will happen>

Do you want me to execute this?
```

End the preflight with a direct approval question.

Require a second explicit confirmation immediately before executing any testnet action that:

1. deploys a workflow (`cre workflow deploy`)
2. activates a workflow (`cre workflow activate`)
3. deletes a workflow (`cre workflow delete`)
4. uploads or deletes secrets (`cre secrets create`, `cre secrets delete`)

Do not treat the user's original intent as the second confirmation. Ask again right before the side-effecting command.

### What Deployment Does

1. Compiles workflow code to WebAssembly
2. Uploads the WASM binary, config, and secrets reference to the CRE platform
3. Registers the workflow with the DON
4. The workflow starts in a **paused** state

### Activating After Deployment

```bash
cre workflow activate <workflow-dir> --target <target-name>
```

## Secret Custody And Opaque Transfer

The agent never learns a secret's value. The agent may still move an existing secret from one user-controlled store to another when the value remains opaque throughout.

That transfer is permitted only when the user explicitly authorized that specific transfer and all of the following hold:

- The source and destination are systems the user identified and controls.
- Transport is encrypted.
- The value never appears in agent-visible output, in command arguments, in logs, in shell history, in files the agent reads, or in repository content.
- The agent neither inspects nor retains the value.
- The operation complies with system and developer policy and stays within the scope the user authorized.

User authorization never licenses reading, printing, or logging a secret value.

### Safe

```bash
# Safe: .env contains only the 1Password reference; op injects the value.
MY_API_KEY_VAR=op://my-vault/my-item/api-key
op run --env-file ../.env -- cre secrets create <workflow-dir> --target <target-name>

# Safe: CRE reads MY_API_KEY_VAR from the environment the user provisioned.
cre secrets create <workflow-dir> --target <target-name>

# Safe: the destination consumes the value from stdin without agent-visible output.
op read op://my-vault/my-item/api-key | some-store set MY_API_KEY --stdin

# Safe: the user completes the required browser sign-in.
cre login
```

### Unsafe

```bash
# Unsafe: reading a secret file exposes its contents to the agent.
cat .env

# Unsafe: printing a secret exposes it in output and logs.
echo "$CRE_ETH_PRIVATE_KEY"

# Unsafe: a literal secret argument enters shell history and the process list.
some-store set MY_API_KEY --value '<literal-secret-value>'

# Unsafe: writing a real value into secrets.yaml, config.json, a README, or a test fixture exposes and retains it.
printf 'MY_API_KEY: %s\n' "$MY_API_KEY_VAR" > secrets.yaml

# Unsafe: encoding or hashing is still exposure when the result is printed.
printf '%s' "$MY_API_KEY_VAR" | base64
printf '%s' "$MY_API_KEY_VAR" | shasum -a 256

# Unsafe: asking the user to paste a secret into chat exposes it to the agent.
printf '%s\n' 'Paste MY_API_KEY into chat so I can forward it.'
```

The safe list is not exhaustive. An unlisted mechanism is acceptable only when it satisfies every condition above; when it cannot, decline that mechanism and offer a compliant one rather than refusing the user's whole request.

## Monitoring

### Viewing Workflow Status

```bash
cre workflow show <workflow-dir> --target <target-name>
```

Shows:
- Workflow name and ID
- Current status (active, paused, error)
- Deployment timestamp
- Associated wallet key

### Listing All Workflows

```bash
cre workflow list --target <target-name>
```

### Logs

Workflow logs (from `runtime.log()` / `runtime.Logger().Info()`) are available through the CRE platform dashboard.

## Updating Workflows

### Update Command

```bash
cre workflow update <workflow-dir> --target <target-name>
```

### What Gets Updated

- Workflow code (recompiled to WASM)
- Configuration file
- Secrets reference

### Update Process

1. Pause the workflow (if active): `cre workflow pause <dir> --target <target>`
2. Update secrets if changed: `cre secrets update <dir> --target <target>`
3. Deploy the update: `cre workflow update <dir> --target <target>`
4. Re-activate: `cre workflow activate <dir> --target <target>`

## Pausing Workflows

```bash
cre workflow pause <workflow-dir> --target <target-name>
```

A paused workflow stops receiving trigger events but retains its deployment. It can be re-activated.

## Deleting Workflows

```bash
cre workflow delete <workflow-dir> --target <target-name>
```

This is permanent. The workflow is removed from the DON and cannot be recovered.

## Multi-Sig Wallet Support

CRE supports multi-sig wallets for workflow management. The organization owner configures multi-sig settings through the platform.

Key considerations:
- Multi-sig transactions require multiple approvals before execution
- The `cre account link-key` command links the multi-sig address
- All deployment and management operations go through the multi-sig approval flow
- Timeout for multi-sig operations may be longer than standard single-key operations

## Service Quotas

CRE has service quotas that limit:
- Maximum number of deployed workflows per organization
- Maximum workflow binary size
- Maximum number of linked keys per organization (currently 2)
- Maximum number of secrets per workflow
- Rate limits on trigger frequency

Check the service quotas documentation for current limits.

## Official Documentation

- Deploying workflows: `https://docs.chain.link/cre/guides/operations/deploying-workflows.md`
- Service quotas: `hhttps://docs.chain.link/cre/service-quotas.md`
