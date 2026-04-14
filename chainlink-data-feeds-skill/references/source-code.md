# Source Code References

Use this file only when debugging interface mismatches, verifying function signatures, or the user needs to inspect actual contract source code on GitHub.

## Trigger Conditions

Read this file when:
- The user gets a compilation error related to interface mismatches
- The user wants to inspect the actual proxy or aggregator implementation
- The user needs to verify a function signature or return type against deployed code
- The user wants working example contracts to reference

## smartcontractkit/documentation — Example Contracts

### EVM Solidity Consumers

- `public/samples/DataFeeds/DataConsumerV3.sol` — Basic price feed consumer via AggregatorV3Interface
- `public/samples/DataFeeds/DataConsumerWithSequencerCheck.sol` — Consumer with L2 sequencer uptime check
- `public/samples/DataFeeds/PriceConverter.sol` — Library for converting ETH amounts using price feeds
- `public/samples/DataFeeds/HistoricalDataConsumer.sol` — Reading historical round data
- `public/samples/DataFeeds/ReserveConsumerV3.sol` — Proof of Reserve feed consumer
- `public/samples/DataFeeds/ENSConsumer.sol` — Resolving feed addresses via ENS

### Off-Chain Readers

- `public/samples/DataFeeds/PriceConsumerV3.js` — ethers.js price feed reader
- `public/samples/DataFeeds/PriceConsumerV3Ethers.js` — ethers.js alternative example
- `public/samples/DataFeeds/PriceConsumerV3.py` — Python web3.py reader
- `public/samples/DataFeeds/HistoricalDataConsumer.js` — JavaScript historical data reader
- `public/samples/DataFeeds/HistoricalDataConsumer.py` — Python historical data reader
- `public/samples/DataFeeds/ENSConsumer.js` — JavaScript ENS resolver

### MVR Examples

- `public/samples/DataFeeds/MVR/MVRDataConsumer.sol` — Solidity MVR bundle consumer

### SVR Searcher Examples

- `public/samples/DataFeeds/SVR/broadcaster.go` — Go SVR searcher broadcaster
- `public/samples/DataFeeds/SVR/broadcaster.ts` — TypeScript SVR broadcaster
- `public/samples/DataFeeds/SVR/decoder.go` — Go SVR event decoder
- `public/samples/DataFeeds/SVR/decoder.ts` — TypeScript SVR decoder
- `public/samples/DataFeeds/SVR/listener.go` — Go SVR event listener
- `public/samples/DataFeeds/SVR/listener.ts` — TypeScript SVR listener
- `public/samples/DataFeeds/SVR/bundle-bid.json` — SVR bundle bid payload schema
- `public/samples/DataFeeds/SVR/bundle-transaction-event.json` — SVR bundle transaction event schema
- `public/samples/DataFeeds/SVR/single-transaction-event.json` — SVR single transaction event schema
- `public/samples/DataFeeds/SVR/decoding-abi.json` — ABI for decoding SVR transaction data

### Solana Examples

- `public/samples/Solana/PriceFeeds/on-chain-read.rs` — Rust on-chain reader (native)
- `public/samples/Solana/PriceFeeds/on-chain-read-anchor.rs` — Rust on-chain reader (Anchor)
- `public/samples/Solana/PriceFeeds/off-chain-read.js` — JavaScript off-chain reader
- `public/samples/Solana/PriceFeeds/off-chain-read.ts` — TypeScript off-chain reader

Base URL: `https://github.com/smartcontractkit/documentation/blob/main/`

## smartcontractkit/chainlink-evm — Contract Source Code

### v0.6 — Legacy Price Feed Contracts (widely deployed)

- `contracts/src/v0.6/data-feeds/AggregatorProxy.sol` — Core proxy that delegates reads to an upgradeable aggregator
- `contracts/src/v0.6/data-feeds/EACAggregatorProxy.sol` — Extended access-controlled proxy (most commonly deployed)
- `contracts/src/v0.6/data-feeds/interfaces/AggregatorV3Interface.sol` — The canonical interface for reading price feeds
- `contracts/src/v0.6/data-feeds/interfaces/AggregatorV2V3Interface.sol` — Combined V2+V3 interface (used for L2 sequencer feeds)
- `contracts/src/v0.6/data-feeds/interfaces/AggregatorInterface.sol` — Legacy V2 interface (latestAnswer, latestTimestamp)

### v0.8 — MVR / Bundle Feed Contracts (newer)

- `contracts/src/v0.8/data-feeds/BundleAggregatorProxy.sol` — Proxy for MVR bundle feeds
- `contracts/src/v0.8/data-feeds/DataFeedsCache.sol` — Caching layer for data feeds
- `contracts/src/v0.8/data-feeds/interfaces/IBundleAggregatorProxy.sol` — Interface for MVR bundle proxy
- `contracts/src/v0.8/data-feeds/interfaces/IBundleAggregator.sol` — Underlying MVR bundle aggregator interface
- `contracts/src/v0.8/data-feeds/interfaces/ICommonAggregator.sol` — Common interface shared across feed types

Base URL: `https://github.com/smartcontractkit/chainlink-evm/blob/develop/`

## When to Fetch Source Code

1. **Interface mismatch error** — Fetch the specific interface file to verify the function signature matches what the user is calling.
2. **Proxy behavior question** — Fetch AggregatorProxy.sol or EACAggregatorProxy.sol to explain delegation behavior.
3. **Working example needed** — Fetch the specific example file from the documentation repo. Only fetch the one file needed — do not browse directories.
4. **MVR contract internals** — Fetch BundleAggregatorProxy.sol or IBundleAggregatorProxy.sol for bundle-specific behavior.
