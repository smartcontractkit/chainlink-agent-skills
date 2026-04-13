# Official Sources

Use this file only when the answer depends on current CCIP facts that can change over time.

## Freshness Policy

1. Do not hardcode live CCIP facts such as supported routes, token availability, network counts, lane counts, or message status.
2. Re-check official sources whenever the request depends on current routes, current tokens, current tool behavior, or live message tracking.
3. Distinguish between conceptual guidance and live configuration data.
4. If a live source conflicts with cached assumptions, prefer the live source and say so.
5. Cite the exact official source used for freshness-sensitive answers.

## Source Map

### CCIP Docs

URL:
- `https://docs.chain.link/ccip`
- EVM tutorials: `https://docs.chain.link/ccip/tutorials/evm`
- Solana (SVM) tutorials: `https://docs.chain.link/ccip/tutorials/svm`
- Aptos tutorials: `https://docs.chain.link/ccip/tutorials/aptos`

Use for:
- concepts and architecture
- tutorials and implementation guidance (EVM, Solana, Aptos)
- interfaces, contracts, and best practices
- CCT concepts and registration flows (EVM and Solana)
- service limits, billing, and security-oriented documentation

Do not use as the primary source for:
- live message status
- current lane availability
- current token availability

### CCIP Tools

URL:
- `https://docs.chain.link/ccip/tools`
- `https://docs.chain.link/ccip/tools/api/`
- `https://docs.chain.link/ccip/tools/sdk/`
- `https://docs.chain.link/ccip/tools/cli/`

Use for:
- current CLI documentation
- current API documentation
- current SDK documentation
- supported-chain information exposed by the tools reference
- starter projects and tool-oriented examples

Packages:
- CLI: `@chainlink/ccip-cli`
- SDK: `@chainlink/ccip-sdk`

Do not use as the primary source for:
- contract interfaces
- live route inventory
- live message status

### CCIP Directory

URLs:
- `https://docs.chain.link/ccip/directory/mainnet`
- `https://docs.chain.link/ccip/directory/testnet`

Use for:
- whether a route exists on mainnet or testnet
- current network and lane inventory
- current token availability on a route

Do not use for:
- live message execution status
- contract implementation patterns

### CCIP Explorer

URL:
- `https://ccip.chain.link/`

Use for:
- message tracking
- explorer-style lookup
- lane-status surfaces
- current network activity views

Do not use as the primary source for:
- contract authoring guidance
- CLI, API, or SDK usage

### CCIP SDK Examples

URL:
- `https://github.com/smartcontractkit/ccip-sdk-examples`

Use for:
- working multi-chain SDK code examples (EVM, Solana, Aptos)
- Node.js scripts for fee estimation, token transfers, message status
- React/browser bridge applications (EVM-only and multi-chain)
- Hardhat v3 integration with SDK-assisted operations

Do not use as the primary source for:
- contract interfaces or architecture
- live route or message data

## Practical Selection Rules

1. For conceptual or contract questions, start with CCIP Docs.
2. For side-effecting tool workflows, start with the CCIP CLI docs.
3. For monitoring, querying, and message lookup workflows, start with the CCIP API docs.
4. For programmatic integrations, start with the CCIP SDK docs.
5. For working SDK code examples, start with the CCIP SDK Examples repo.
6. For route connectivity or token-availability questions, start with CCIP Directory.
7. For explorer-style message-status questions, use CCIP Explorer.
8. For non-EVM tutorials (Solana, Aptos), start with the chain-specific tutorial sections in CCIP Docs.
9. If the request spans multiple categories, use the smallest number of official sources that fully resolves the question.
