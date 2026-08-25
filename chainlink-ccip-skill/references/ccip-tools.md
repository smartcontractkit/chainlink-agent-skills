# CCIP Tools

Use for tool-first CLI/API/SDK requests without custom contracts. Contract requests use [contracts](ccip-contracts.md); live reads use [API](ccip-api.md); monitoring uses [monitoring](ccip-monitoring.md); TypeScript uses [SDK examples](ccip-sdk-examples.md).

## Inputs and path

For every send/bridge/fee request, name CCIP and require a current CCIP Directory check before support claims or send preparation. Track every required field — the complete source→destination route, token/amount, and recipient — and ask one focused question for the single most useful missing field at a time, naming in that same question any other required field still outstanding (for example, asking for the amount while noting the recipient address is still needed too) so collection never silently stops after only one field. State as soon as collection starts, even before every field is known, that any resulting send or bridge artifact is only ever prepared for the user's own wallet to sign and broadcast — this skill never signs or sends. Prefer API live reads, CLI user-run templates, and SDK integrations. Do not switch to contracts unless requested or necessary.
If a named testnet source has only a destination chain name, propose its matching testnet, warn that testnet assets cannot move to that mainnet, and give the user-run next step before asking confirmation.

Fetch `https://docs.chain.link/ccip/tools/llms.txt` before asserting commands, flags, endpoints, or methods. Other sources: tools `https://docs.chain.link/ccip/tools/`; CLI `.../tools/cli/`; configuration `.../cli/configuration`; troubleshooting `.../cli/troubleshooting`; workflow guides under `.../cli/guides/{token-transfer-workflow,data-transfer-workflow,tokens-and-data-workflow,debugging-workflow}`; API `.../tools/api/` with HTTPS base `api.ccip.chain.link/v2` and schema `https://api.ccip.chain.link/docs`; SDK `.../tools/sdk/`; names/selectors `.../tools/chains`; packages `@chainlink/ccip-cli`, `@chainlink/ccip-sdk`; examples `https://github.com/smartcontractkit/ccip-sdk-examples`.

## CLI surface

Install: `npm install -g @chainlink/ccip-cli`.

| Command | Alias | Effect and required facts |
|---|---|---|
| `show <tx-or-id>` | — | read; `--log-index`, `--wait` |
| `search messages [sender]` | `msgs` | read; sender/receiver/source/dest; `--limit 0` means all; API required |
| `lane-latency <source> <dest>` | `laneLatency`, `latency` | read; `--block-confirmations`; API required |
| `lane` | `get-lane` | read; `--source`, `--dest`, `--router` required |
| `get-supported-tokens` | `getSupportedTokens` | read; `--network`, `--address` required; optional `--token`, `--fee-tokens`, `--only-fee-tokens` |
| `token` | — | read; `--network`, `--holder` required; optional `--token` |
| `parse <data>` | `parse-bytes`, `parse-data` | read; decode revert/error/call/event data |
| `send` | — | **write/user-run**; source `--router`; `--only-get-fee`, `--only-estimate` print then exit |

Globals: `--rpcs`/`--rpc`, `--rpcs-file` (default `./.env`), `--format pretty|log|json`, `--verbose`, `--page`, `--api <url>`/`--no-api`, `--canton-config`, `--indexer`; environment equivalents `RPC_*`, `CCIP_FORMAT`, `CCIP_VERBOSE`, `CCIP_PAGE`, `CCIP_API`. Use JSON for parsed output.

```bash
ccip-cli show <tx-hash-or-message-id> --format json
ccip-cli lane-latency ethereum-mainnet arbitrum-mainnet --format json
ccip-cli get-supported-tokens --network ethereum-mainnet --address <router>
```

### Signer hazard

Without `--wallet`, the CLI resolves `PRIVATE_KEY`, then `USER_KEY`, then `OWNER_KEY`, then scans `--rpcs-file` (default `.env`). Thus even fee-only `send` can encounter a signer:

1. Never run `send` from agent tools, never read/write `.env` or keys, and never put a private key, signing secret, or placeholder for either on a command line. User-run execution must use wallet-controlled signing without exposing signing material to the agent.
2. Prefer signerless SDK `chain.getFee(...)` for a live fee; fall back to a user-run `send --only-get-fee`/`--only-estimate` only if no signerless path covers it.
3. [Non-EVM](ccip-non-evm.md) exclusively owns the family support matrix, Solana/Aptos send templates, family flags, and Canton requirements.

## Send/bridge workflow

For tokens, verify route and token in the current Directory; for data, verify the route. Then estimate the fee, emit the main preflight, and provide the actual requested testnet-only CCIP CLI command, SDK code, or unsigned transaction artifact—not a plan or completion summary. Every write artifact must repeat exactly: “This skill never signs or sends. You must sign and broadcast from your own wallet.” For any mainnet write artifact, emit no command or transaction and say exactly: “I refuse mainnet write artifacts; testnet only.”

The complete safest path does not end at broadcast: always include post-transfer message/status monitoring through the CCIP API or CLI. After the user broadcasts, have them pass the transaction hash or message ID to `ccip-cli show <tx-hash-or-message-id> --wait --format json` or use the equivalent CCIP API message lookup, then explain the resulting success or failure status. This monitoring guidance is required, not conditional on a separate follow-up request.

For testnets, suggest faucet/tutorial **CCIP-BnM** when no token is specified; LINK/WETH exist only on some routes. Never assume support.

If the user asks only for a fee and no safe live read exists, give: (1) fee must come from the router, (2) minimal user-run fee-only command or SDK read, (3) ask for the result. Stop before preflight, internals, addresses, or send command.

Current routes/tokens come from the Directory; commands from CLI docs; integrations from SDK docs. See [the main boundary](../SKILL.md#boundary-and-preflight).
