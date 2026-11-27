# CCIP Discovery

Use only for route connectivity, mainnet/testnet classification, or supported-token discovery—not status, performance, send execution, or contracts. A discovery-only prompt stays read-only and loads only this workflow and the current CCIP API; never answer it with contract imports, package installation, remappings, or project setup.

## Sources and workflow

The CCIP API (`https://api.ccip.chain.link/v2`) is the default and authoritative source for route existence/classification, token availability, and verifiers across EVM and non-EVM families. The CCIP Directory is being deprecated and merged into the CCIP Explorer, which is powered by the same API.

- Routes: `GET /v2/lanes` with `sourceChainSelector`, `destChainSelector`, `environment`.
- Tokens: `GET /v2/tokens` (filters `chainSelector`, `remoteChainSelector`, `symbol`, `address`, `environment`), `GET /v2/tokens/{chainSelector}/{tokenAddress}` for the pool and per-remote-chain `status`, `GET /v2/tokens/groups/{groupId}` for members and directed connections.
- Verifiers: `GET /v2/verifiers`. Chains and routers: `GET /v2/chains[/{selector}]`.

`/v2` is required, selectors are `uint64` strings, and active routers have `isActive`. Full schemas: [ccip-api.md](ccip-api.md). Names/selectors: `https://docs.chain.link/ccip/tools/chains`. Fallback only while the pages exist or the API is unavailable: `https://docs.chain.link/ccip/directory/mainnet`, `/testnet`.

`ccip-cli get-supported-tokens` is an optional command-level check when router/network context exists. It requires `--network`, `--address`; accepts `--token`, `--fee-tokens`, `--only-fee-tokens`; supports non-EVM; use `--format json` for parsing. Current flags: `https://docs.chain.link/ccip/tools/llms.txt` and `https://docs.chain.link/ccip/tools/cli/`.

1. Establish mainnet or testnet; ask once if absent.
2. Query `/v2/lanes` for the direct lane and confirm both chains via `/v2/chains`; a returned lane's `status` is the route state.
3. Until that live API check succeeds, never answer “yes” or otherwise assert support and then qualify it as unverified; say that live support cannot be verified here, then try the matching Directory page as a fallback and name it. An inconclusive or unavailable source is not evidence of support.
4. For token questions, distinguish: lane with unsupported token; missing lane; token supported only elsewhere.
5. If the user asks only route existence/environment, answer only the facts the current source verified—do not add token lists, counts, selectors, addresses, commands, or performance.
6. Never infer environment from names when the API can confirm it. Use CLI only as an additional check.
7. Route latency/performance to [monitoring](ccip-monitoring.md).

`GET /v2/tokens` defaults to `reviewedOnly=true`, which hides tokens not yet reviewed. A token missing from the default list is not proof it is unsupported: re-query with `reviewedOnly=false` (or by `address`) before answering. Report a hit with `isReviewed: false` as indexed but unreviewed, with its `remoteChains` `status`; never present it as reviewed or recommend it.

Re-check live questions; do not hardcode counts or availability. If CLI and API disagree, prefer the API and say so. If the API and the Directory fallback disagree, prefer the API and say so. Discovery is read-only and neither proves performance nor licenses guesses when the official source is inconclusive.

Never select or recommend a transfer token unless the user asked for one. Before any token-send handoff, verify both the direct lane and that exact token via the API (`/v2/tokens/{chainSelector}/{tokenAddress}`, remote `status` `CONNECTED`), then require explicit send mode or confirmation; discovery itself stays read-only. On mainnet, provide only sourced reads, with a placeholder-only fee quote or testnet artifact as the closest send alternative—never approval, signing, send, or broadcast steps.
