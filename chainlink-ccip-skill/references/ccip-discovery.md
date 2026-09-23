# CCIP Discovery

Use only for route connectivity, mainnet/testnet classification, or supported-token discovery—not status, performance, send execution, or contracts. A discovery-only prompt stays read-only and loads only this workflow and the matching current CCIP Directory; never answer it with contract imports, package installation, remappings, or project setup.

## Sources and workflow

The CCIP Directory is primary for route existence/classification and token availability across EVM and non-EVM families:

- `https://docs.chain.link/ccip/directory/mainnet`
- `https://docs.chain.link/ccip/directory/testnet`

For machine-readable lane/network/active-contract facts use `GET https://api.ccip.chain.link/v2/lanes` with `sourceChainSelector`, `destChainSelector`, `environment`, and `GET /v2/chains[/{selector}]`; `/v2` is required, selectors are `uint64` strings, and active routers have `isActive`. Full schemas: [ccip-api.md](ccip-api.md). Names/selectors: `https://docs.chain.link/ccip/tools/chains`.

`ccip-cli get-supported-tokens` is an optional command-level check when router/network context exists. It requires `--network`, `--address`; accepts `--token`, `--fee-tokens`, `--only-fee-tokens`; supports non-EVM; use `--format json` for parsing. Current flags: `https://docs.chain.link/ccip/tools/llms.txt` and `https://docs.chain.link/ccip/tools/cli/`.

1. Establish mainnet or testnet; ask once if absent.
2. Check the matching current Directory and confirm both chains plus their direct lane before answering whether the route is supported.
3. Until that official current check succeeds, never answer “yes” or otherwise assert support and then qualify it as unverified; say that live support cannot be verified here and name the matching Directory URL. An inconclusive or unavailable source is not evidence of support.
4. For token questions, distinguish: lane with unsupported token; missing lane; token supported only elsewhere.
5. If the user asks only route existence/environment, answer only the facts the current source verified—do not add token lists, counts, selectors, addresses, commands, or performance.
6. Never infer environment from names when the Directory can confirm it. Use CLI only as an additional check.
7. Route latency/performance to [monitoring](ccip-monitoring.md).

Re-check live questions; do not hardcode counts or availability. The Directory, not the lanes API, is the sole route/token authority; the API reports inventory/status only. If CLI and Directory disagree, prefer Directory and say so. Discovery is read-only and neither proves performance nor licenses guesses when the official source is inconclusive.

Never select or recommend a transfer token unless the user asked for one. Before any token-send handoff, verify both the direct lane and that exact token in the matching Directory, then require explicit send mode or confirmation; discovery itself stays read-only. On mainnet, provide only sourced reads, with a placeholder-only fee quote or testnet artifact as the closest send alternative—never approval, signing, send, or broadcast steps.
