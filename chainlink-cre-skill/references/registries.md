# Registries

## Contents

- Choose a registry
- Registry selection in config
- Onchain registry
- Private registry
- Lifecycle per registry
- Secrets per registry
- Verify the active registry
- Quotas and access
- Not a confidentiality boundary
- Sources

Use for registry choice, onchain vs private differences, per-target registry routing, and registry-specific lifecycle or secret behavior. Command syntax belongs to [cli-reference.md](cli-reference.md); approval gates belong to [operations.md](operations.md).

## Choose a registry

CRE publishes workflows to one of two registries. The choice is per target, not per project.

| | Onchain registry | Private registry |
|---|---|---|
| Registration | Ethereum Mainnet transaction | Chainlink-hosted off-chain registry |
| Authorization | Linked wallet key | CRE login session or `CRE_API_KEY` |
| Needs `CRE_ETH_PRIVATE_KEY` | Yes | No |
| Needs `project.yaml` RPC URL | Yes | No |
| Gas cost | Yes (mainnet) | None |
| Workflow owner | Linked wallet address | Organization owner address |
| Availability | General | Private registry beta; organization must be enabled |
| Confidentiality | None | None — see below |

`private` is a supported registry selector, not a placeholder ID. Never invent a registry ID; read the real ones from `cre registry list`.

## Registry selection in config

Each target declares its registry under `user-workflow`:

```yaml
# <workflow>/workflow.yaml
production:
  user-workflow:
    workflow-name: my-workflow-production
    deployment-registry: "private"      # or an ID from cre registry list
  workflow-artifacts:
    workflow-path: "./main.ts"
    config-path: "./config.production.json"
    secrets-path: "./secrets.yaml"
```

Rules:

- `deployment-registry` is required for registry-bound deploy, activate, pause, update, and delete. Omitting it does not mean "whatever the workflow already uses"; treat an unknown registry as a verification gap, not an invite to guess.
- One `workflow.yaml` may mix registries: target A onchain, target B private.
- `init`, `deploy`, broadcast, and every lifecycle command route by the `--target` selected at call time.
- Existing deployed workflows cannot be moved between registries; deploy the workflow again under the other registry.

## Onchain registry

- Prerequisites: CRE Early Access (`cre account access`), browser `cre login` or a user-supplied `CRE_API_KEY`, a linked funded wallet (`cre account link-key --target <target>`), an RPC URL for each chain in `project.yaml`, and uploaded Vault DON secrets when used.
- The CLI consumes the wallet key from `CRE_ETH_PRIVATE_KEY`; the agent never reads it.
- The workflow owner is the linked wallet, which is also the address consumer contracts must authorize for onchain writes.
- `cre account unlink-key` deletes the workflows associated with that key.

## Private registry

- Prerequisites: CRE CLI v1.15.0+, an authenticated session, and a private registry enabled for the organization (`cre registry list` shows an entry with `Type: off-chain`).
- No linked wallet key, no `CRE_ETH_PRIVATE_KEY`, no RPC URL in `project.yaml`, and no gas.
- Registered workflows are active immediately after deploy.
- The workflow owner is the organization owner address, which matches **Organization address** in the CRE platform and the `ownerAddress` field of `cre workflow list --registry private --output json`.
- Consumer contracts that accept onchain writes from this workflow authorize the organization owner address, not a linked key.
- Private registry is beta; default quota is three workflows per organization.

## Lifecycle per registry

Deploy registers a paused workflow on the onchain registry, which then needs activate. A private-registry deploy is registered active immediately. Pause stops triggers but retains the deployment; delete removes it permanently.

Deletion specifics:

- `cre workflow delete` deletes **all workflow versions matching the given name and owner address**, not a single version. Re-using a workflow name therefore risks removing records the caller did not intend; confirm the name and owner before deleting, and prefer `cre workflow list --include-deleted` to see prior versions of that name.
- On the private registry the CLI shows the workflow details and prompts the operator to type the workflow name; `--yes` skips that prompt and `--unsigned` returns a raw transaction instead of sending it.
- Deleted workflows stay hidden from `cre workflow list` unless `--include-deleted` is passed.

Registry routing applies to every lifecycle command:

```bash
cre workflow activate <dir> --target <target>
cre workflow pause <dir> --target <target>
cre workflow update <dir> --target <target>
cre workflow delete <dir> --target <target>
```

## Secrets per registry

Onchain registry secrets are authorized through the linked wallet key. Private registry secrets are authorized through a browser OAuth (PKCE) flow, so add `--secrets-auth=browser`:

```bash
cre secrets create <workflow-dir> --target <target> --secrets-auth=browser
cre secrets update <workflow-dir> --target <target> --secrets-auth=browser
cre secrets list --target <target> --secrets-auth=browser
```

`--secrets-auth` defaults to `onchain` (wallet key); `browser` uses account credentials for the private registry. Do not pass a `workflow-owner-address` or wallet flag for the private registry path.

## Verify the active registry

```bash
cre registry list                                        # IDs, labels, types, onchain addresses
cre workflow list --registry private --output json        # ownerAddress per workflow
cre workflow get <dir> --target <target>                  # health + latest execution
cre workflow get <dir> --target <target> --all-registries  # ignore the configured registry
```

`cre workflow get` scopes resolution to the workflow's configured `deployment-registry` by default; `--all-registries` is the escape hatch when the configured registry looks wrong.

If a lifecycle command behaves as though a wallet is missing, or the workflow is absent from `cre workflow list`, check `deployment-registry` for the selected target before anything else.

## Quotas and access

Registry quotas cover deployed workflows per organization (private registry defaults to three), binary size, linked keys, secrets, trigger frequency, and concurrency. Private registry access is a beta enrollment separate from general deploy access. Fetch current limits from `https://docs.chain.link/cre/service-quotas.md` rather than guessing.

## Not a confidentiality boundary

The private registry is a private, centralized control plane for workflow management. It does not make workflow execution confidential: the binary and logic remain DON-visible, and only values concluded through TEE execution are confidential. For confidential execution use [confidential-workflows.md](confidential-workflows.md).

## Sources

- https://docs.chain.link/cre/guides/operations/deploying-workflows.md
- https://docs.chain.link/cre/guides/operations/deploying-to-onchain-registry.md
- https://docs.chain.link/cre/guides/operations/deploying-to-private-registry-ts.md
- https://docs.chain.link/cre/reference/cli/registry.md
- https://docs.chain.link/cre/service-quotas.md
