# Official Sources

Use this file when the answer depends on current Data Streams facts such as available schemas, deprecated streams, endpoints, SDK APIs, verifier addresses, or supported networks.

## Freshness Policy

1. Do not hardcode live Data Streams facts such as current feed IDs, endpoint availability, schema deprecation status, verifier addresses, supported networks, or SDK method names.
2. Re-check official sources whenever the user needs a current feed, current schema status, current endpoint, current SDK behavior, or current verifier deployment.
3. Distinguish stable concepts from live configuration data.
4. If a live source conflicts with cached assumptions, prefer the live source and say so.
5. Cite the exact official source used for freshness-sensitive answers.

## Source Map

### Data Streams Docs

URLs:
- `https://docs.chain.link/data-streams`
- `https://docs.chain.link/data-streams/llms-full.txt`

Use for:
- architecture and concepts
- Standard API vs Streams Trade implementation
- developer responsibilities and best practices
- pointers to tutorials, API references, and report schemas

Do not use as the only source for:
- current SDK method names
- current schema deprecation status
- current verifier proxy addresses

### Credentials and Authentication

URLs:
- `https://docs.chain.link/data-streams/reference/data-streams-api/authentication`
- `https://chain.link/contact?ref_id=datastreams`

Use for:
- explaining the official process to request Data Streams access
- REST and WebSocket authentication requirements
- HMAC header generation only when the user is not using an SDK

### Report Schemas and Deprecation

URLs:
- `https://docs.chain.link/data-streams/reference/report-schema-overview`
- `https://docs.chain.link/data-streams/deprecating-streams`

Use for:
- available stream categories and report schema versions
- current field names and field meanings
- deprecated stream or schema guidance

### REST and WebSocket API

URLs:
- `https://docs.chain.link/data-streams/reference/data-streams-api/interface-api`
- `https://docs.chain.link/data-streams/reference/data-streams-api/interface-ws`

Use for:
- REST endpoints for latest reports, timestamp lookups, bulk report queries, and paginated report history
- WebSocket subscription parameters, payloads, and errors
- testnet and mainnet endpoint domains

### SDKs

URLs:
- `https://github.com/smartcontractkit/data-streams-sdk`
- `https://github.com/smartcontractkit/data-streams-sdk/tree/main/go`
- `https://github.com/smartcontractkit/data-streams-sdk/tree/main/rust`
- `https://github.com/smartcontractkit/data-streams-sdk/tree/main/typescript`

Use for:
- official Go, Rust, and TypeScript SDK APIs
- examples for fetching, decoding, streaming, HA mode, and metrics
- package names and language-specific setup

### Onchain Verification

URLs:
- `https://docs.chain.link/data-streams/reference/data-streams-api/onchain-verification`
- `https://docs.chain.link/data-streams/tutorials/evm-onchain-report-verification`
- `https://docs.chain.link/data-streams/tutorials/solana-onchain-report-verification`
- `https://docs.chain.link/data-streams/tutorials/solana-offchain-report-verification`
- `https://docs.chain.link/data-streams/tutorials/stellar-onchain-report-verification`

Use for:
- verifier interfaces and current addresses
- EVM, Solana, and Stellar verification flows
- code generation and review for verification contracts/programs

### Frontend and Candlestick Data

URLs:
- `https://docs.chain.link/data-streams/reference/candlestick-api`

Use for:
- OHLC history endpoints
- supported symbol and group discovery
- live price updates for frontend charting

### Billing

URLs:
- `https://docs.chain.link/data-streams/billing`
- `https://chain.link/contact?ref_id=datastreams`

Use only to redirect users to official Chainlink contact channels. Do not expose, infer, or summarize private billing details.

## Practical Selection Rules

1. For credentials or auth setup, start with the authentication page and prefer SDK-managed auth.
2. For report decoding or schema properties, start with the report schema overview, then the language SDK docs.
3. For REST latest/timestamp/history work, use the REST API docs plus the target language SDK.
4. For WebSocket or HA work, use the WebSocket docs plus the target language SDK.
5. For onchain verification, use the chain-specific verification tutorial and fetch current verifier addresses.
6. For candlestick charts, use the Candlestick API docs and keep Data Streams credentials server-side.
7. For billing questions, do not speculate. Direct the user to Chainlink.

## Documentation Fetching

1. If WebFetch, a browser tool, or an MCP server can retrieve docs, use it before answering freshness-sensitive questions.
2. If Context7 (`@upstash/context7-mcp`) is available, use it as a fallback for `docs.chain.link` and SDK documentation.
3. If all fetch methods fail, explicitly tell the user which URL could not be verified and use only the embedded reference files as a floor.
