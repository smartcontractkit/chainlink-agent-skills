# Operations

Use this file when the user asks about simulating, deploying, monitoring, activating, pausing, updating, or deleting workflows, or about multi-sig wallets.

## Trigger Conditions

- "How do I deploy my CRE workflow?"
- "How do I monitor a deployed workflow?"
- "How do I update a workflow?"
- "How do I pause or delete a workflow?"

Do not use for workflow code patterns (see workflow-patterns.md), CLI command syntax (see cli-reference.md), or first-time setup (see getting-started.md).

## Workflow Lifecycle

```
Init -> Simulate -> Deploy -> Activate -> (Running)
                                  |
                              Pause -> Update -> Activate
                                  |
                              Delete
```

## Simulation

### Running a Simulation

```bash
cre workflow simulate <workflow-dir> --target <target-name>
```

Example:

```bash
cre workflow simulate my-workflow --target staging-settings
```

### What Simulation Does

1. Compiles workflow code to WebAssembly
2. Runs the workflow locally using the specified target configuration
3. Simulates trigger events
4. Executes capability calls against real endpoints (RPC, HTTP APIs)
5. Displays output including user logs and the workflow result

### Simulation vs Deployment

| Aspect | Simulation | Deployment |
|--------|-----------|------------|
| Execution | Local machine | DON nodes |
| Consensus | Single node (no aggregation) | Multi-node with consensus |
| Gas costs | None | Real gas costs |
| Secrets | From `.env` / environment | From Vault DON |
| RPC calls | Direct to RPC endpoint | Via DON EVM client |

### Testing HTTP Triggers

For HTTP-triggered workflows, simulation starts a local HTTP server:

```bash
cre workflow simulate my-workflow --target staging-settings
```

Then in another terminal:

```bash
curl -X POST http://localhost:8080/trigger \
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

## Deployment

### Prerequisites

1. **Early Access approval**: Deployment requires being approved for the CRE Early Access program
2. **Authentication**: Run `cre login` and complete 2FA
3. **Linked wallet**: Run `cre account link-key --target <target>` to link a funded wallet
4. **Funded wallet**: Wallet needs ETH on the target chain for gas fees
5. **Secrets uploaded**: If the workflow uses secrets, run `cre secrets create` first

### Deploy Command

```bash
cre workflow deploy <workflow-dir> --target <target-name>
```

Example:

```bash
cre workflow deploy my-workflow --target production-settings
```

### What Deployment Does

1. Compiles workflow code to WebAssembly
2. Uploads the WASM binary, config, and secrets reference to the CRE platform
3. Registers the workflow with the DON
4. The workflow starts in a **paused** state

### Activating After Deployment

```bash
cre workflow activate <workflow-dir> --target <target-name>
```

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

- Deploying workflows: `https://docs.chain.link/cre/guides/workflow/deploying-a-workflow`
- Service quotas: `https://docs.chain.link/cre/reference/service-quotas`
