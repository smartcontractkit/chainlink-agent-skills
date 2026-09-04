# Official Sources

Use this map for current endpoints, feeds, schemas/deprecation, SDK APIs, verifier deployments, or supported networks. Follow [SKILL.md](../SKILL.md)'s five-line freshness policy: live source beats cached assumptions; distinguish stable concepts from deployment data and cite the exact source checked.

## Source Map

### Concepts and architecture

- `https://docs.chain.link/data-streams.md`
- `https://docs.chain.link/data-streams/llms-full.txt`

Use for architecture, Standard API vs Streams Trade, responsibilities/best practices, and tutorial/API/schema pointers—not alone for current SDK methods, deprecation, or verifier addresses.

### Access and authentication

- `https://docs.chain.link/data-streams/reference/data-streams-api/authentication.md`
- `https://chain.link/contact?ref_id=datastreams`

Use for access requests and REST/WebSocket HMAC only when not using an SDK. Local details: [credentials-and-auth.md](credentials-and-auth.md).

### Schemas and deprecation

- `https://docs.chain.link/data-streams/reference/report-schema-overview.md`
- `https://docs.chain.link/data-streams/deprecating-streams.md`

Use for stream categories, fields/meanings, current schema availability, and deprecation. Then check the language SDK decoder; local catalog: [report-schemas.md](report-schemas.md).

### REST and WebSocket APIs

- `https://docs.chain.link/data-streams/reference/data-streams-api/interface-api.md`
- `https://docs.chain.link/data-streams/reference/data-streams-api/interface-ws.md`

Use for latest/timestamp/bulk/history endpoints; subscription parameters, payloads, and errors; and testnet/mainnet domains. Offline defaults: [public-endpoints-and-addresses.md](public-endpoints-and-addresses.md).

### SDKs

- `https://github.com/smartcontractkit/data-streams-sdk`
- `https://github.com/smartcontractkit/data-streams-sdk/tree/main/go`
- `https://github.com/smartcontractkit/data-streams-sdk/tree/main/rust`
- `https://github.com/smartcontractkit/data-streams-sdk/tree/main/typescript`

Use for current Go/Rust/TypeScript packages, methods, versions, fetch/decode/stream/HA examples, and metrics.

### Onchain verification

- `https://docs.chain.link/data-streams/reference/data-streams-api/onchain-verification.md`
- `https://docs.chain.link/data-streams/tutorials/evm-onchain-report-verification.md`
- `https://docs.chain.link/data-streams/supported-networks.md`
- `https://github.com/smartcontractkit/documentation/blob/main/src/features/feeds/data/StreamsNetworksData.ts`
- `https://docs.chain.link/data-streams/tutorials/solana-onchain-report-verification.md`
- `https://docs.chain.link/data-streams/tutorials/solana-offchain-report-verification.md`
- `https://docs.chain.link/data-streams/tutorials/stellar-onchain-report-verification.md`

Use the chain-specific tutorial for verifier interfaces, flows, code review/generation, and current deployments. Offline address fallback: [public-endpoints-and-addresses.md](public-endpoints-and-addresses.md); canonical examples: [onchain-verification.md](onchain-verification.md).

### Chainlink Local tests

- `https://github.com/smartcontractkit/chainlink-local`
- `https://www.npmjs.com/package/@chainlink/local`
- `https://github.com/smartcontractkit/chainlink-local/releases`

Use for local Foundry/Hardhat/Remix simulator tests and current package source. Re-check versions/APIs; the package includes Data Streams simulator/fork, mock report generator/verifier/proxy/fee manager, and billing modes. Exact APIs and smoke matrix: [onchain-verification.md](onchain-verification.md).

### Candlesticks

- `https://docs.chain.link/data-streams/reference/candlestick-api.md`

Use for OHLC history, symbols/groups, and live chart updates; keep credentials server-side.

### Billing

- `https://docs.chain.link/data-streams/billing.md`
- `https://chain.link/contact?ref_id=datastreams`

Redirect to Chainlink; do not infer or summarize private billing details.

## Selection

Start with authentication for access/auth; schema overview then SDK for decoding; REST or WebSocket interface plus SDK for retrieval/HA; chain tutorial plus current deployment data for verification; Candlestick docs for charts. Use local endpoint/address tables only as fallbacks. If retrieval fails, name the URL and use embedded references only as a floor; Context7 (`@upstash/context7-mcp`) is the fallback fetcher.
