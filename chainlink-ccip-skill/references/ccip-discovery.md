# CCIP Discovery

Use this file only for CCIP route connectivity checks, network classification, or supported-token discovery.

## Trigger Conditions

Use this workflow for requests like:

- "Are these two chains connected by CCIP?"
- "Is this route testnet or mainnet?"
- "Which tokens are supported on this route?"
- "Does this chain have CCIP lanes?"
- "Can I bridge this token across this route?"

Do not use this workflow for message status, lane-performance monitoring, direct send execution, or contract generation.

## Default Path

1. Prefer the CCIP Directory as the primary source of truth for route existence, network classification, and supported tokens. The directory covers both EVM and non-EVM chains (Solana, Aptos lanes appear in the directory).
2. For a machine-readable answer, query the CCIP API instead of parsing directory pages: `GET https://api.ccip.chain.link/v2/lanes` (filter by `sourceChainSelector`, `destChainSelector`, `environment`) for lane inventory, and `GET /v2/chains` or `GET /v2/chains/{selector}` for supported networks, chain families, and CCIP deployment identifiers, including which router is `isActive`. The `/v2` prefix is required. Chain selectors are uint64 sent as strings. See [ccip-api.md](ccip-api.md) for parameters and response shapes, and `https://docs.chain.link/ccip/tools/chains` for a browsable list of names and selectors.
3. Use CLI `get-supported-tokens` only as an additional check when the user has concrete router or network context and command-line output would help. It needs `--network` and `--address`, accepts `--token`, `--fee-tokens`, and `--only-fee-tokens`, and supports non-EVM chains natively. Add `--format json` when the output will be parsed.
4. Use CCIP Tools documentation only when the request depends on current tool behavior rather than the directory itself.
5. If the user is actually asking about current lane performance instead of route existence, route to [ccip-monitoring.md](ccip-monitoring.md).

Reference points:

- Mainnet directory: `https://docs.chain.link/ccip/directory/mainnet`
- Testnet directory: `https://docs.chain.link/ccip/directory/testnet`
- Supported chains and selectors: `https://docs.chain.link/ccip/tools/chains`
- API endpoint parameters and CLI flags: `https://docs.chain.link/ccip/tools/llms.txt`
- CLI docs: `https://docs.chain.link/ccip/tools/cli/`

## Discovery Workflow

### Route existence

1. Determine whether the user is asking about mainnet or testnet. If they do not say, ask.
2. Use the matching CCIP Directory page first.
3. Confirm whether both chains appear and whether a lane exists between them.
4. Explain the answer in direct route terms rather than only restating chain counts.
5. If the user asks only whether a route exists and whether it is mainnet or testnet, answer only those points and cite the source. Do not volunteer token lists, lane counts, selectors, addresses, CLI commands, or performance details.

### Network classification

1. If the user gives a route, classify it as mainnet or testnet using the CCIP Directory.
2. If the user gives only chain names, clarify whether they mean the production or test network when that is ambiguous.
3. Do not infer that a chain pair is testnet or mainnet only from naming patterns when the directory can confirm it directly.

### Token support

1. Use the CCIP Directory first for supported-token discovery on a route.
2. If the user has a router or pool context and wants command-level verification, use CLI `get-supported-tokens` as an additional path.
3. Distinguish clearly between:
   - route exists but token unsupported
   - route missing entirely
   - token exists elsewhere but not on the requested route

## Freshness Rules

1. Treat the CCIP Directory as the source of truth for current route and token availability.
2. Re-check the directory for live route and token questions instead of relying on cached assumptions.
3. Do not hardcode current lane counts, token counts, or route availability.
4. If CLI output and the directory disagree, prefer the directory and say so.

## Refusal Rules

1. Keep discovery flows read-only.
2. Refuse to imply that discovery confirms current lane performance; route that question to monitoring instead.
3. Refuse to guess route or token support when the directory does not confirm it.

