# smartcontractkit/chainlink-evm — Data Feeds Contract Source Code

## v0.6 — Legacy Price Feed Contracts (widely used)

- https://github.com/smartcontractkit/chainlink-evm/blob/develop/contracts/src/v0.6/data-feeds/AggregatorProxy.sol — Core aggregator proxy contract that delegates reads to an upgradeable aggregator
- https://github.com/smartcontractkit/chainlink-evm/blob/develop/contracts/src/v0.6/data-feeds/EACAggregatorProxy.sol — Extended access-controlled aggregator proxy (most commonly deployed proxy type)
- https://github.com/smartcontractkit/chainlink-evm/blob/develop/contracts/src/v0.6/data-feeds/Owned.sol — Ownership management base contract used by proxies
- https://github.com/smartcontractkit/chainlink-evm/blob/develop/contracts/src/v0.6/data-feeds/interfaces/AggregatorV3Interface.sol — The canonical interface for reading price feeds (decimals, description, getRoundData, latestRoundData, version)
- https://github.com/smartcontractkit/chainlink-evm/blob/develop/contracts/src/v0.6/data-feeds/interfaces/AggregatorV2V3Interface.sol — Combined V2+V3 interface extending both legacy and current methods
- https://github.com/smartcontractkit/chainlink-evm/blob/develop/contracts/src/v0.6/data-feeds/interfaces/AggregatorInterface.sol — Legacy V2 aggregator interface (latestAnswer, latestTimestamp, latestRound)
- https://github.com/smartcontractkit/chainlink-evm/blob/develop/contracts/src/v0.6/data-feeds/interfaces/AccessControllerInterface.sol — Access controller interface for restricting feed reads

## v0.8 — MVR / Bundle Feed Contracts (newer)

- https://github.com/smartcontractkit/chainlink-evm/blob/develop/contracts/src/v0.8/data-feeds/BundleAggregatorProxy.sol — Proxy contract for Multiple-Variable Response (MVR) bundle feeds
- https://github.com/smartcontractkit/chainlink-evm/blob/develop/contracts/src/v0.8/data-feeds/DataFeedsCache.sol — Caching layer for data feeds
- https://github.com/smartcontractkit/chainlink-evm/blob/develop/contracts/src/v0.8/data-feeds/interfaces/IBundleAggregatorProxy.sol — Interface for MVR bundle proxy (latestBundle, bundleDecimals, latestBundleTimestamp)
- https://github.com/smartcontractkit/chainlink-evm/blob/develop/contracts/src/v0.8/data-feeds/interfaces/IBundleAggregator.sol — Interface for the underlying MVR bundle aggregator
- https://github.com/smartcontractkit/chainlink-evm/blob/develop/contracts/src/v0.8/data-feeds/interfaces/IBundleBaseAggregator.sol — Base interface shared by bundle aggregators
- https://github.com/smartcontractkit/chainlink-evm/blob/develop/contracts/src/v0.8/data-feeds/interfaces/ICommonAggregator.sol — Common aggregator interface shared across feed types
- https://github.com/smartcontractkit/chainlink-evm/blob/develop/contracts/src/v0.8/data-feeds/interfaces/IDataFeedsCache.sol — Interface for the data feeds caching layer
- https://github.com/smartcontractkit/chainlink-evm/blob/develop/contracts/src/v0.8/data-feeds/interfaces/IDecimalAggregator.sol — Interface for decimal-aware aggregators
- https://github.com/smartcontractkit/chainlink-evm/blob/develop/contracts/src/v0.8/data-feeds/interfaces/ITokenRecover.sol — Interface for recovering stuck tokens from feed contracts
