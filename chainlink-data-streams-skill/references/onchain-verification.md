# Onchain Verification

Use this file when the user wants smart contracts or programs that verify Data Streams reports onchain, or when reviewing code that consumes verified reports.

## Safety Boundary

Code generation and review are allowed. Any deployment, transaction submission, verifier configuration, or other onchain write requires the skill's approval protocol and second confirmation rule. Mainnet writes are refused.

## EVM

Official sources:

- `https://docs.chain.link/data-streams/reference/data-streams-api/onchain-verification`
- `https://docs.chain.link/data-streams/tutorials/evm-onchain-report-verification`

Expected pattern:

1. fetch current verifier proxy address for the target network from official docs
2. accept a `full_report` payload retrieved from Data Streams
3. estimate or handle verification fees using the documented verifier/fee manager flow
4. call the verifier proxy `verify` path documented by Chainlink
5. decode the returned verifier response for the target report schema
6. validate freshness, market status, ripcord, or other schema-specific risk signals before using the value

Generated Solidity should be minimal, explicit, and conservative. Do not bake in stale verifier addresses unless the user requested a specific network and live docs were checked.

## Solana

Official sources:

- `https://docs.chain.link/data-streams/tutorials/solana-onchain-report-verification`
- `https://docs.chain.link/data-streams/tutorials/solana-offchain-report-verification`

Expected pattern:

1. use the onchain integration when the Solana program itself must verify reports
2. use CPI to the Chainlink verifier program as described in the official tutorial
3. keep account lists and verifier program IDs sourced from current docs
4. use the offchain Rust SDK path when client-side verification is sufficient

Do not translate EVM verifier assumptions into Solana account or CPI code.

## Stellar

Official source:

- `https://docs.chain.link/data-streams/tutorials/stellar-onchain-report-verification`

Expected pattern:

1. generate Soroban/Rust code from the official Stellar tutorial shape
2. fetch current verifier contract details from docs
3. keep report parsing and verifier calls separate from business logic
4. surface any required network setup or contract IDs as placeholders unless live docs were checked

Do not apply EVM or Solana verifier APIs to Stellar.

## Review Checklist

When generating or reviewing verification code, check:

- current verifier address/program/contract source was consulted
- report bytes are passed exactly as required by the verifier
- decoded schema matches the feed/report version
- stale or expired reports are rejected
- application-specific risk fields are handled
- only testnet writes are considered, and only after two confirmations
- no private key, mnemonic, or API secret is embedded in source

## Refusal Template

For mainnet write requests:

```text
I cannot execute or help automate a mainnet state-changing action. I can generate or review the code, explain the verification flow, or help run read-only checks.
```
