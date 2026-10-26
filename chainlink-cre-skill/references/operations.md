# Operations

Use for deploy, activate, update, pause, delete, secrets writes, monitoring, or multisig. Simulation mechanics belong to [simulation.md](simulation.md); registry choice and per-registry behavior belong to [registries.md](registries.md).

## Boundary and lifecycle

Default lifecycle: init → simulate → deploy → activate (onchain only; private-registry deploys are active immediately) → pause/update/reactivate or delete. Agent execution is testnet-only: refuse mainnet deploy, activate, update, pause, delete, and secrets operations.

Prerequisites depend on the target's registry, which `workflow.yaml` sets per target under `user-workflow.deployment-registry`:

- Both registries: CRE Early Access (`cre account access`), browser-completed `cre login` or a user-supplied `CRE_API_KEY`, and uploaded Vault DON secrets when required.
- Onchain registry only: a linked funded wallet (`cre account link-key --target <target>`) and an RPC URL in `project.yaml`; the CLI consumes the key from `CRE_ETH_PRIVATE_KEY`.
- Private registry: no linked key, no `CRE_ETH_PRIVATE_KEY`, no RPC URL, and no gas. Deploy is authorized by the login session and the organization must have the private registry enabled (`cre registry list`).

Never state the onchain prerequisites for a private-registry target, and never infer the registry: if the target does not declare one, stop and verify. Deployment compiles WASM, uploads binary/config/secret references, registers with the registry, and starts paused on the onchain registry — a private-registry deploy is registered active immediately.

```bash
cre workflow deploy <dir> --target <target>
cre workflow activate <dir> --target <target>
cre workflow pause <dir> --target <target>
cre workflow update <dir> --target <target>
cre workflow delete <dir> --target <target>
cre secrets create <dir> --target <target>
cre secrets update <dir> --target <target>
cre secrets delete <dir> --target <target>
cre secrets list --target <target>
```

Every accepted command includes `--target`, and every lifecycle command routes to the registry declared by that target's `user-workflow.deployment-registry` — never assume the onchain registry. Simulate before deploy and again before an update; simulation defaults to non-broadcast. Deletion is permanent and removes **every version matching the workflow name and owner**, so confirm the name and owner before deleting; pause retains the deployment but stops triggers (missed triggers are not queued); deleted workflows are only visible with `cre workflow list --include-deleted`. The private registry prompts the operator to type the workflow name before deleting, and `--yes` skips that prompt. A typical update simulates the candidate, pauses, updates secrets if needed, updates code/config, then reactivates.

## Approval protocol

Before **every** testnet deploy, activate, update, pause, delete, or secrets create/update/delete, show:

```text
Proposed workflow operation:
- Action: <action>
- Network type: testnet
- Target: <target from workflow.yaml>
- Registry: <registry id from user-workflow.deployment-registry>
- Chain(s): <chain selector names>
- Workflow name: <name>
- Secrets: <yes/no; names only>
- Consumer contract: <address, if any>
- Expected effect: <effect>

Do you want me to execute this?
```

Do not infer approval from the original request. Immediately before `workflow deploy`, `workflow activate`, `workflow delete`, `secrets create`, or `secrets delete`, require a **second explicit confirmation**. Never expose secret values in either prompt. For a private-registry target, state that no wallet or gas is involved instead of listing onchain prerequisites.

## Secret custody and opaque transfer

The agent never learns a secret value. A user may explicitly authorize moving an existing secret between user-controlled systems only when source/destination are identified and controlled by the user, transport is encrypted, the value never enters agent-visible output, arguments, logs, shell history, repository content, or files the agent reads, the agent neither inspects nor retains it, and policy/scope permit the operation. Authorization never permits reading, printing, or logging. If any condition fails, decline that mechanism and offer an opaque one.

Safe patterns (references or tool-to-tool streams; no value becomes visible):

```dotenv
MY_API_KEY_REF=op://my-vault/my-item/api-key
```

```bash
cre secrets create <dir> --target <target>
op read op://my-vault/my-item/api-key | some-store set MY_API_KEY --stdin
cre login
```

Unsafe patterns (agent access, logs/history, or retained plaintext):

```bash
cat .env
cat secrets.yaml
echo "$CRE_ETH_PRIVATE_KEY"
some-store set MY_API_KEY --value '<literal-secret>'
printf 'MY_API_KEY: %s\n' "$MY_API_KEY" > secrets.yaml
printf '%s' "$MY_API_KEY" | base64
printf '%s' "$MY_API_KEY" | shasum -a 256
```

Also unsafe: reading keystores/wallet files, asking the user to paste a secret, or placing real values in config, README, tests, command arguments, or repository files. Encoding/hashing printed output is still exposure. The safe list is illustrative; an unlisted mechanism must satisfy every opaque-transfer condition.

## Monitoring and status

```bash
cre workflow show <dir> --target <target>
cre workflow get <dir> --target <target>
cre workflow list --target <target> --output json
cre workflow list --target <target> --registry private
```

`show` includes workflow name/ID, status, deployment time, and owner — the linked wallet key on the onchain registry, the organization owner address on the private registry. `get` prints the owner for a workflow configured in `workflow.yaml`. Runtime logs (`runtime.log()` / `runtime.Logger().Info()`) and execution history/metrics are available through the CRE dashboard; never log secrets or confidential payloads.

## Multisig and quotas

The organization owner configures multisig. `cre account link-key` links its address; lifecycle actions produce/enter the multisig approval flow and may take longer because multiple approvals are required.

Quotas cover deployed workflows, binary size, linked keys (currently two per organization), secrets, trigger frequency, memory/execution, and concurrency. Fetch current limits from `https://docs.chain.link/cre/service-quotas.md` rather than guessing. Private-registry workflows count against a separate registry quota (three per organization by default); see [registries.md](registries.md).

## Sources

- https://docs.chain.link/cre/guides/operations/deploying-workflows.md
- https://docs.chain.link/cre/guides/operations/deploying-to-onchain-registry.md
- https://docs.chain.link/cre/guides/operations/deploying-to-private-registry-ts.md
- https://docs.chain.link/cre/guides/operations/activating-pausing-workflows.md
- https://docs.chain.link/cre/guides/operations/updating-deployed-workflows.md
- https://docs.chain.link/cre/guides/operations/deleting-workflows.md
- https://docs.chain.link/cre/guides/operations/using-multisig-wallets.md
