# CLI Reference

Use for exact CRE commands and flags. [project-scaffolding.md](project-scaffolding.md) owns the `cre init` flag table; [simulation.md](simulation.md) owns simulate behavior; [operations.md](operations.md) owns side-effect approvals.

## Non-interactive rules

- Pass `--target` on every `cre workflow` and `cre secrets` command that accepts it; omission prompts for a target.
- For `cre init`, pass `--non-interactive --project-name ... --deployment-registry ... --template ...`; a missing registry can still prompt.
- For simulate automation, pass `--non-interactive --trigger-index`, plus the selected trigger's payload flags.
- Machine output exists only as `cre templates list --json`, `cre workflow list --output json`, and `cre workflow supported-chains --output json`; do not invent `--json` for other commands.

## Global flags

| Flag | Meaning |
|---|---|
| `-h, --help` | help |
| `-e, --env <path>` | secret environment file (default `.env`) |
| `-E, --public-env <path>` | shared non-sensitive `.env.public` |
| `-T, --target <name>` | target from project configuration |
| `-R, --project-root <path>` | project root |
| `-v, --verbose` | debug logging |
| `--non-interactive` | fail rather than prompt; all inputs must be supplied |

## Authentication and account

| Command | Effect / important flags |
|---|---|
| `cre login` | opens browser; user completes password/2FA |
| `cre logout` | ends session |
| `cre whoami` | email, organization ID, linked keys |
| `cre account access` | checks/requests Early Access; no command-specific flags |
| `cre account link-key --target <target>` | links key consumed from `CRE_ETH_PRIVATE_KEY` by the CLI |
| `cre account list-key` | lists linked keys |
| `cre account unlink-key --target <target>` | unlinks key and deletes its workflows |

The agent never reads key material. Account creation is browser-only.

## Project and templates

```bash
cre init --non-interactive --project-name my-project \
  --deployment-registry <registry-id> --workflow-name my-workflow \
  --template hello-world-ts
```

All `cre init` flags, required combinations, templates, dependency steps, and registry lookup are canonical in [project-scaffolding.md](project-scaffolding.md).

Generate Go bindings from ABIs/artifacts with:

```bash
cre generate-bindings evm
```

Current project-setup references may also expose the explicit form `cre generate-bindings --abi-dir <path> --pkg <package> --output <path>`; check `cre generate-bindings --help` for the installed CLI before choosing a syntax.

| Command | Flags |
|---|---|
| `cre templates list` | `--json`, `--refresh` |
| `cre templates add <repository-source>` | add source |
| `cre templates remove <repository-source>` | remove source |
| `cre update` | update CLI |
| `cre version` | print version |

## Simulation

[simulation.md](simulation.md) owns the command shape and behavior; this table is a flag index only.

| Flag | Meaning |
|---|---|
| `--target` | required target; omission prompts |
| `--non-interactive` | no prompts |
| `--trigger-index` | 0-based handler; required with non-interactive mode |
| `--http-payload` | HTTP body as JSON or file path |
| `--evm-tx-hash` | transaction containing the EVM log |
| `--evm-event-index` | 0-based log index |
| `--evm-receipt-timeout` | receipt wait, not overall simulation timeout; version-dependent |
| `--broadcast` | execute a real testnet write through `MockKeystoneForwarder` |
| `--limits` | `default`, a limits file, or `none` |
| `--skip-type-checks` | skip TypeScript typecheck |

There is no generic simulation `--timeout`. Read [simulation.md](simulation.md) before running this command.

## Workflow lifecycle

Every command below includes `--target`:

```bash
cre workflow deploy <dir> --target <target>
cre workflow activate <dir> --target <target>
cre workflow pause <dir> --target <target>
cre workflow update <dir> --target <target>
cre workflow delete <dir> --target <target>
cre workflow show <dir> --target <target>
cre workflow list --target <target> --output json
cre workflow supported-chains --target <target> --output json
```

- Deploy prerequisites: login, linked/funded wallet, Early Access, and uploaded secrets when used.
- Deploy registers a paused workflow; activate starts it.
- Delete is permanent.
- `workflow list` also accepts `--include-deleted`.
- `supported-chains` returns tenant chains and mock forwarders.

Refuse mainnet writes and apply [operations.md](operations.md)'s testnet preflight and second confirmations.

## Secrets

All secret commands require a target. The CLI consumes values declared by `secrets.yaml` from its environment without the agent reading them.

```bash
cre secrets create <workflow-dir> --target <target>
cre secrets update <workflow-dir> --target <target>
cre secrets delete <workflow-dir> --target <target>
cre secrets list --target <target>
```

Create uploads; update replaces; delete removes; list shows namespaces. Follow secret custody and approvals in [operations.md](operations.md).

## Sources

- https://docs.chain.link/cre/reference/cli.md
- https://docs.chain.link/cre/reference/cli/workflow.md
- https://docs.chain.link/cre/reference/cli/secrets.md
