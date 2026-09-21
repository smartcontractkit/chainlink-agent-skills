# Official Sources

Use only when embedded references lack a live or version-sensitive fact. Find every indexed destination in [assets/cre-docs-index.md](../assets/cre-docs-index.md), fetch the smallest matching page, and do not load full-text dumps when a focused page exists.

## Source map

| Need | Official destination |
|---|---|
| Docs home, account, install | `https://docs.chain.link/cre.md`; `/cre/account.md`; `/cre/getting-started/cli-installation.md` |
| CLI commands and flags | `/cre/reference/cli.md` and its `/reference/cli/*` pages |
| TypeScript/Go SDK signatures | `/cre/reference/sdk/overview-ts.md`, `/overview-go.md`, then the capability-specific SDK page |
| Project configuration | `/cre/reference/project-configuration-ts.md` or `-go.md` |
| Supported networks | `/cre/supported-networks-ts.md` or `-go.md` |
| Forwarders | `/cre/guides/workflow/using-evm-client/forwarder-directory-ts.md` or `-go.md` |
| Consensus, finality, determinism | `/cre/concepts/*` |
| Confidential Workflows/access | `/cre/concepts/confidential-workflows`; `/cre/account/confidential-workflows-access` |
| Templates | `https://github.com/smartcontractkit/cre-templates` |
| SDK/CLI source | `https://github.com/smartcontractkit/cre-sdk-typescript`, `/cre-sdk-go`, `/cre-cli` under `smartcontractkit` |
| Releases/quotas | `/cre/release-notes.md`; `/cre/service-quotas.md` |

Use official sources for networks, numeric/name selectors, forwarders, feed proxies, flags, SDK signatures, contract requirements, release behavior, and quotas. Cite verified live constants; if verification is impossible, mark the value for verification before deployment rather than guessing.
