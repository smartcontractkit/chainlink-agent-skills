# CCIP Tools

Use this file only for tool-first CCIP requests where the user wants to use CCIP CLI, API, or SDK instead of building custom contracts.

## Trigger Conditions

Use this workflow for requests like:

- "Send a CCIP message for me."
- "Bridge USDC from one chain to another using CCIP."
- "Move funds with CCIP without writing contracts."
- "Estimate the fee and prepare the transfer command."

Do not use this workflow when the user clearly wants custom sender or receiver contracts.

## Required Inputs

Collect only the missing inputs needed for the next safe step:

1. source chain
2. destination chain
3. network type
4. recipient address or receiving account
5. token and amount for fund transfers
6. payload for message sends

If the route or network is missing, ask for it and state that the CCIP Directory is the source for the next live route and token check. Do not assume a lane.

## Default Path

1. Use the CCIP API for every live read: message status, message search, lane existence, lane latency, chain and contract configuration. It is the shortest path to a current answer. See [ccip-api.md](ccip-api.md).
2. Use the CCIP CLI as a documentation target for user-run command templates. Do not run CLI commands that sign, broadcast, send, bridge, deploy, approve, or manually execute transactions.
3. Use the CCIP SDK when the user asks for a programmatic integration or a code sample rather than an answer.
4. Route read-only monitoring, querying, searching, lane-latency checks, and message-status workflows to [ccip-monitoring.md](ccip-monitoring.md).
5. Do not switch to contract generation unless the user asks for it or the tool-first path cannot satisfy the goal.

Reference points:
- Machine-readable aggregate of the whole tools reference (fetch this first for
  command, flag, endpoint, or method questions): `https://docs.chain.link/ccip/tools/llms.txt`
- Tools overview: `https://docs.chain.link/ccip/tools/`
- CLI docs: `https://docs.chain.link/ccip/tools/cli/`
- CLI global options, RPC sources, and wallet resolution: `https://docs.chain.link/ccip/tools/cli/configuration`
- CLI troubleshooting: `https://docs.chain.link/ccip/tools/cli/troubleshooting`
- CLI workflow guides: `https://docs.chain.link/ccip/tools/cli/guides/token-transfer-workflow`, `https://docs.chain.link/ccip/tools/cli/guides/data-transfer-workflow`, `https://docs.chain.link/ccip/tools/cli/guides/tokens-and-data-workflow`, `https://docs.chain.link/ccip/tools/cli/guides/debugging-workflow`
- API docs: `https://docs.chain.link/ccip/tools/api/` (base URL `https://api.ccip.chain.link/v2`, schema browser `https://api.ccip.chain.link/docs`)
- SDK docs: `https://docs.chain.link/ccip/tools/sdk/`
- Supported chains and selectors: `https://docs.chain.link/ccip/tools/chains`
- CLI package: `@chainlink/ccip-cli`
- SDK package: `@chainlink/ccip-sdk`
- SDK examples repo: `https://github.com/smartcontractkit/ccip-sdk-examples`

For TypeScript SDK code examples (fee estimation, token transfers, messaging, status checks), see [ccip-sdk-examples.md](ccip-sdk-examples.md).

## CLI Surface

Install: `npm install -g @chainlink/ccip-cli`. Full flag tables live in
`https://docs.chain.link/ccip/tools/llms.txt`; fetch it instead of guessing a flag.

| Command | Aliases | Effect | Notes |
|---|---|---|---|
| `show <tx-hash-or-id>` | - | read | Full request detail. `--log-index`, `--wait` |
| `search messages [sender]` | `msgs` | read | `--sender`, `--receiver`, `--source`, `--dest`, `--manual-exec-only`, `--limit` (`0` = all). Requires API access |
| `lane-latency <source> <dest>` | `laneLatency`, `latency` | read | Trimmed-median delivery latency. `--block-confirmations`. Requires API access |
| `lane` | `get-lane` | read | OnRamp and OffRamp config for a lane. `--source`, `--dest`, `--router` all required |
| `get-supported-tokens` | `getSupportedTokens` | read | `--network` and `--address` required; `--token`, `--fee-tokens`, `--only-fee-tokens` |
| `token` | - | read | Token or native balance. `--network`, `--holder` required; `--token` |
| `parse <data>` | `parse-bytes`, `parse-data` | read | Decode revert reasons, errors, call data, or event data |
| `send` | - | **write** | User-run only. `--router` is the source-chain router. `--only-get-fee` and `--only-estimate` print and exit without broadcasting |
| `manual-exec <tx-hash-or-id>` | `manualExec` | **write** | User-run only. `--only-estimate` prints the gas estimate and exits |

Global options apply to every command: `--rpcs`/`--rpc`, `--rpcs-file` (default
`./.env`), `--format pretty|log|json`, `--verbose`, `--page`, `--api <url>` or
`--no-api` for RPC-only mode, `--canton-config`, `--indexer`. Environment
equivalents: `RPC_*`, `CCIP_FORMAT`, `CCIP_VERBOSE`, `CCIP_PAGE`, `CCIP_API`.

Always add `--format json` when the output will be parsed rather than read.

### Wallet auto-detection

When `--wallet` is omitted, the CLI resolves a signer from `PRIVATE_KEY`, then
`USER_KEY`, then `OWNER_KEY`, and then by scanning `--rpcs-file` (default
`./.env`). A `send` or `manual-exec` invocation can therefore broadcast with no
wallet argument present in the command. Because of that:

1. Never run `send` or `manual-exec` from the agent runtime, including "just to estimate".
2. Never read, print, or write `./.env`, and never ask the user for key material.
3. For fee or gas numbers, give the user `send --only-get-fee` or `send --only-estimate` and let them run it.

### Read-only command templates

```bash
ccip-cli show <tx-hash-or-message-id> --format json
ccip-cli search messages --sender <address> --manual-exec-only --format json
ccip-cli lane-latency ethereum-mainnet arbitrum-mainnet --format json
ccip-cli lane --source ethereum-mainnet --dest arbitrum-mainnet --router <router>
ccip-cli get-supported-tokens --network ethereum-mainnet --address <router>
ccip-cli token --network ethereum-mainnet --holder <address> --token <token>
```

## Multi-Chain Support

The SDK, CLI, and API support multiple blockchain families:

| Chain Family | SDK/CLI Status |
|-------------|---------------|
| EVM | Full support |
| Solana (SVM) | Full support |
| Aptos | Full support |
| Sui | Partial (manual execution only) |
| TON | Partial (no token pool/registry queries) |
| Canton | Supported; requires `--canton-config`, and `--indexer` for CCV verifications |

Per-command family support is listed on each CLI command page and in
`https://docs.chain.link/ccip/tools/llms.txt`. Re-verify the partial rows above
before telling a user a family cannot do something.

For non-EVM-specific workflow guidance (SDK chain classes, CLI options, wallet setup, tutorials), see [ccip-non-evm.md](ccip-non-evm.md).

### Non-EVM CLI Command Templates

These are user-run templates. The agent may help fill placeholders from public, non-secret inputs, but must not run commands that would sign or broadcast transactions.

```bash
# User-run: send from Solana to EVM
ccip-cli send \
  --source solana-devnet \
  --dest ethereum-testnet-sepolia \
  --router <solana-router> \
  --receiver 0xYourEVMAddress \
  --transfer-tokens <token>=0.001

# User-run: send from Aptos to EVM
ccip-cli send \
  --source aptos-testnet \
  --dest ethereum-testnet-sepolia \
  --router <aptos-router> \
  --receiver 0xYourEVMAddress \
  --transfer-tokens <token>=0.001

# Read-only: track any message (works for all chain families)
ccip-cli show <tx-hash-or-message-id> --wait

# Read-only: check lane latency
ccip-cli lane-latency solana-devnet ethereum-testnet-sepolia
```

## Testnet Tokens

For testnet flows, the standard test token is **CCIP-BnM** (burn-and-mint). It is the token provided by the Chainlink faucet and used in official CCIP tutorials. When the user is working on a testnet and has not specified a token, suggest CCIP-BnM as the default. LINK and WETH are also available on some testnet routes but CCIP-BnM is the most common starting point.

## Send and Bridge Workflow

### For token transfers

1. Verify that the route exists and the token is supported on that route.
2. Estimate the fee before preparing the user-run artifact.
3. Present the non-custodial preflight package from the main skill file.
4. Provide a command template, unsigned transaction data, or integration code for the user to run in their own wallet-controlled environment.
5. Do not execute the transfer, sign a transaction, broadcast a transaction, or read wallet material.
6. If the user wants follow-up tracking after they execute it, route that request to [ccip-monitoring.md](ccip-monitoring.md).

### For data-only message sends

1. Verify that the route exists.
2. Estimate the fee before preparing the user-run artifact.
3. Present the non-custodial preflight package from the main skill file.
4. Provide a command template, unsigned transaction data, or integration code for the user to run in their own wallet-controlled environment.
5. Do not execute the send, sign a transaction, broadcast a transaction, or read wallet material.
6. If the user wants follow-up tracking after they execute it, route that request to [ccip-monitoring.md](ccip-monitoring.md).

### Fee-first requests

When the user asks for the fee before a send and no safe live fee read is available, do not invent a numeric value. Give only:

1. a brief statement that the fee must be read from the router
2. the minimal user-run fee-only CLI command or SDK read
3. a request for the returned value if the user wants help interpreting it

Stop there. Do not add the full preflight, lane internals, addresses, or the eventual send command until the fee is known.

## Freshness Rules

1. Read [official-sources.md](official-sources.md) before answering route or token questions.
2. Use the CCIP Directory for route and token availability.
3. Use CLI docs for user-run command behavior.
4. Use SDK docs for programmatic integration behavior.
5. Do not hardcode live routes, lane counts, router assumptions, or token support.

## Refusal Rules

1. Refuse every mainnet write workflow, including preparation of commands, unsigned transactions, code, or other user-run artifacts for a mainnet write. Read-only mainnet lookups remain allowed.
2. Refuse to prepare a write artifact if the route, network, recipient, or transfer details are still ambiguous.
3. Refuse to execute, sign, broadcast, deploy, approve, bridge, transfer, or manually execute any on-chain transaction from agent tools.
4. Refuse to read wallet credential files, signing-material files, keystores, or secret environment files.
5. If the user asks for unsupported behavior, explain the limit and offer the closest safe alternative.
