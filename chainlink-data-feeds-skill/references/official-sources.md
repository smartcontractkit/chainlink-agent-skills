# Official Sources

Use live sources only when embedded references lack a current address, deprecation state, network parameter, signature, or implementation detail.

## Freshness and destination matrix

| Need | Official destination | Use |
|---|---|---|
| Concepts, architecture, interfaces, feed types, responsibilities | `https://docs.chain.link/data-feeds.md` | Stable documentation; prefer curated references for ordinary integration |
| Price feed addresses | `https://docs.chain.link/data-feeds/price-feeds/addresses.md` | Network/pair proxy, heartbeat, deviation, decimals |
| SmartData and MVR addresses/schemas | `https://docs.chain.link/data-feeds/smartdata/addresses.md` | Proxy and exact **MVR Bundle Info** field order/types |
| Rate/volatility addresses | `https://docs.chain.link/data-feeds/rates-feeds/addresses.md` | Current network availability and parameters |
| U.S. government macro addresses | `https://docs.chain.link/data-feeds/us-government-macroeconomic/addresses.md` | Current macro feed directory |
| Deprecations | `https://docs.chain.link/data-feeds/deprecating-feeds.md` | Dates, networks, replacement guidance |
| Registry | `https://docs.chain.link/data-feeds/contract-registry.md` | Network `IFlags` address and active official proxies |
| Broad fallback | `https://docs.chain.link/data-feeds/llms-full.txt` | Last resort only; prefer the smallest page above |

Re-check live sources for specific addresses, deprecations, availability, and network configuration. Prefer a conflicting live source over cached data and identify the change. Do not use documentation prose as a substitute for a feed's address/schema table.

## Source and example fetch matrix

Fetch one exact file when debugging an interface mismatch, proxy behavior, signature, return type, or implementation. Use the embedded integration references instead of browsing source for routine answers, and use address pages—not repositories—for live configuration.

### `smartcontractkit/documentation`

Base: `https://github.com/smartcontractkit/documentation/blob/main/`

| Shape | Paths under the base |
|---|---|
| EVM consumers | `public/samples/DataFeeds/DataConsumerV3.sol`; `DataConsumerWithSequencerCheck.sol`; `PriceConverter.sol`; `HistoricalDataConsumer.sol`; `ReserveConsumerV3.sol`; `ENSConsumer.sol` |
| Offchain EVM | `public/samples/DataFeeds/PriceConsumerV3.js`; `PriceConsumerV3Ethers.js`; `PriceConsumerV3.py`; `HistoricalDataConsumer.js`; `HistoricalDataConsumer.py`; `ENSConsumer.js` |
| MVR | `public/samples/DataFeeds/MVR/MVRDataConsumer.sol` |
| SVR searcher code | `public/samples/DataFeeds/SVR/broadcaster.go`; `broadcaster.ts`; `decoder.go`; `decoder.ts`; `listener.go`; `listener.ts` |
| SVR payload/decoding data | `public/samples/DataFeeds/SVR/bundle-bid.json`; `bundle-transaction-event.json`; `single-transaction-event.json`; `decoding-abi.json` |
| Solana readers | `public/samples/Solana/PriceFeeds/on-chain-read.rs`; `on-chain-read-anchor.rs`; `off-chain-read.js`; `off-chain-read.ts` |

Repository directory: `https://github.com/smartcontractkit/documentation/tree/main/public/samples/DataFeeds`

### `smartcontractkit/chainlink-evm`

Base: `https://github.com/smartcontractkit/chainlink-evm/blob/develop/`

| Question | Paths under the base |
|---|---|
| Upgradeable price proxy behavior | `contracts/src/v0.6/data-feeds/AggregatorProxy.sol`; `EACAggregatorProxy.sol` |
| Price/sequencer interfaces | `contracts/src/v0.6/data-feeds/interfaces/AggregatorV3Interface.sol`; `AggregatorV2V3Interface.sol`; legacy `AggregatorInterface.sol` |
| MVR proxy/cache | `contracts/src/v0.8/data-feeds/BundleAggregatorProxy.sol`; `DataFeedsCache.sol` |
| MVR interfaces | `contracts/src/v0.8/data-feeds/interfaces/IBundleAggregatorProxy.sol`; `IBundleAggregator.sol`; `ICommonAggregator.sol` |

Repository directories: legacy `https://github.com/smartcontractkit/chainlink-evm/tree/develop/contracts/src/v0.6/data-feeds`; MVR `https://github.com/smartcontractkit/chainlink-evm/tree/develop/contracts/src/v0.8/data-feeds`.

## Fetch selection

- Interface mismatch: fetch the specific interface and compare its function signature to the caller.
- Proxy delegation: fetch `AggregatorProxy.sol` or `EACAggregatorProxy.sol`; consumers still read the proxy.
- Runnable example: fetch only the matching sample file.
- MVR internals: fetch `BundleAggregatorProxy.sol` or `IBundleAggregatorProxy.sol` after confirming the live schema on SmartData Addresses.
- Unknown live fact: do not guess; name and fetch the smallest URL in the destination matrix.
