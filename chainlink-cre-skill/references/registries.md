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

- `deployment-registry` is optional in the CLI: when omitted, the target resolves to the public onchain registry (`onchain:ethereum-mainnet`), not to "whatever the workflow already uses". Set it explicitly in every generated or edited target, and treat an unknown registry as a verification gap, not an invite to guess.
- One `workflow.yaml` may mix registries: target A onchain, target B private.
- `init`, `deploy`, broadcast, and every lifecycle command route by the `--target` selected at call time.
- The docs describe no migration of an existing deployment between registries. Do not promise one; deploying under another registry is a separate registration with that registry's owner.

## Onchain registry

- Prerequisites: CRE Early Access (`cre account access`), browser `cre login` or a user-supplied `CRE_API_KEY`, a linked funded wallet (`cre account link-key --target <target>`), an RPC URL for each chain in `project.yaml`, and uploaded Vault DON secrets when used.
- The CLI consumes the wallet key from `CRE_ETH_PRIVATE_KEY`; the agent never reads it.
- The workflow owner is the linked wallet, which is also the address consumer contracts must authorize for onchain writes.
- `cre account unlink-key` irreversibly deletes all workflows registered under that address.

## Private registry

- Prerequisites: CRE CLI v1.15.0+, an authenticated session (`cre login` or `CRE_API_KEY`), `cre whoami` showing Deploy Access `Enabled`, and a private registry enabled for the organization (`cre registry list` shows an entry with `Type: off-chain`).
- No linked wallet key, no `CRE_ETH_PRIVATE_KEY`, no RPC URL in `project.yaml`, and no gas.
- Registered workflows are active immediately after deploy.
- The workflow owner is the organization owner address, which the CLI labels "(derived)". It matches **Organization address** in the CRE platform and the `ownerAddress` field of `cre workflow list --registry private --output json`.
- Consumer contracts that accept onchain writes from this workflow authorize the organization owner address, not a linked key — for example, pass it to `setExpectedAuthor()` on a `ReceiverTemplate` consumer.
- CI needs only `CRE_API_KEY` (no private key or RPC URL): `cre workflow deploy <dir> --target <target> --yes --non-interactive`.
- Private registry is beta; default quota is three workflows per organization.

## Lifecycle per registry

Deploy registers a paused workflow on the onchain registry, which then needs activate. A private-registry deploy is registered active immediately. Pause stops triggers but retains the deployment; delete removes it permanently.

Deletion specifics:

- `cre workflow delete` deletes **all workflow versions matching the given name and owner address**, not a single version. Re-using a workflow name therefore risks removing records the caller did not intend; confirm the name and owner before deleting, and prefer `cre workflow list --include-deleted` to see prior versions of that name.
- On the private registry the CLI shows the workflow details and prompts the operator to type the workflow name; `--yes` skips that prompt. `--unsigned` (return a raw transaction for multisig signing) applies only to the onchain registry; the private registry has no transaction.
- Deleted workflows stay hidden from `cre workflow list` unless `--include-deleted` is passed.

Registry routing applies to every lifecycle command:

```bash
cre workflow deploy <dir> --target <target>     # also updates: same name redeploys
cre workflow activate <dir> --target <target>
cre workflow pause <dir> --target <target>
cre workflow delete <dir> --target <target>
```

There is no `cre workflow update`. Redeploying the same name replaces the previous deployment in that registry, keeps its active/paused status, and produces a new workflow ID.

## Secrets per registry

Onchain registry secrets are authorized through the linked wallet key. Private registry secrets are authorized through a browser OAuth (PKCE) flow, so add `--secrets-auth=browser`:

```bash
cre secrets create <secrets-file> --target <target> --secrets-auth=browser
cre secrets update <secrets-file> --target <target> --secrets-auth=browser
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

Registry quotas cover deployed workflows per organization (private registry defaults to three; onchain allows one linked key with three workflows per key), binary size, secrets, trigger frequency, and concurrency, and may change before general availability. Private registry is beta: request access through the deploy access process (`cre account access`) or a Chainlink contact, then confirm with `cre registry list`. Fetch current limits from `https://docs.chain.link/cre/service-quotas.md` rather than guessing.

## Not a confidentiality boundary

The private registry is a private, centralized control plane for workflow management. It does not make workflow execution confidential: a private-registry workflow still runs on the public DON and uses the same public HTTP trigger gateway. Confidential execution works with either registry; for it use [confidential-workflows.md](confidential-workflows.md).

## Sources

- https://docs.chain.link/cre/guides/operations/deploying-workflows.md
- https://docs.chain.link/cre/guides/operations/deploying-to-onchain-registry.md
- https://docs.chain.link/cre/guides/operations/deploying-to-private-registry-ts.md
- https://docs.chain.link/cre/reference/cli/registry.md
- https://docs.chain.link/cre/service-quotas.md
