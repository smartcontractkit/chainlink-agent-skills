# Data Feeds Documentation Delta Cache

Topic-indexed facts absent from the curated references, which remain the workflow and safety owners. Treat addresses, versions, endpoints, network lists, and parameters as cached; verify the linked official source.

## Contract and aggregator inspection

Sources: [Data Feeds overview](https://docs.chain.link/data-feeds.md), [index](https://docs.chain.link/data-feeds/index.md), [API reference](https://docs.chain.link/data-feeds/api-reference.md), [full-text fallback](https://docs.chain.link/data-feeds/llms-full.txt).

- A proxy can expose the current underlying aggregator address. Block explorers and verified ABIs can then show aggregator owner, configuration, transmissions, and implementation-specific methods. Do not turn inspection into a consumer dependency: application reads still go through the proxy so aggregator upgrades do not break the application.
- Aggregator implementations vary by feed and network. Call `typeAndVersion()` and inspect the verified source/configuration before reasoning about internals; do not assume every aggregator is `AccessControlledOffchainAggregator`.
- `AccessControlledOffchainAggregator` metadata may include `LINK`, `owner`, `billingAccessController`, `requesterAccessController`, `checkEnabled`, `minAnswer`, and `maxAnswer`. The min/max answer fields are largely unused on many feeds, so applications need their own appropriate circuit breakers rather than relying on those fields.
- Additional inspection methods can include `getBilling()`, `getConfig()`, `latestConfigDetails()`, `latestTransmissionDetails()`, `transmitters()`, and `hasAccess(address,bytes)`. These are aggregator/configuration tools, not substitutes for `AggregatorV3Interface` consumer reads.
- Legacy aggregator getters such as `getAnswer`, `getTimestamp`, `latestAnswer`, `latestRound`, and `latestTimestamp` are deprecated. Prefer the proxy's V3 round methods.
- `@chainlink/contracts` is the EVM interface package. The exact source paths and samples live in [official-sources.md](../references/official-sources.md); fetch a single file rather than browsing an entire repository.

## ENS feed discovery

Source: [ENS integration](https://docs.chain.link/data-feeds/ens.md).

- Feed names use `<base>-<quote>.data.eth`, for example `eth-usd.data.eth` and `btc-usd.data.eth`.
- Subdomains distinguish roles: `proxy.<name>` resolves the stable consumer proxy, `aggregator.<name>` the current underlying aggregator, and `proposed.<name>` a proposed aggregator. Consumers should normally resolve/use the proxy.
- Cached Ethereum Mainnet Chainlink resolver for `data.eth`: `0x122eb74f9d0F1a5ed587F43D120C1c2BbDb9360B`. Verify it before use.
- Resolver `AddrChanged` events announce address changes. Filter the indexed node with the ENS namehash of the full subdomain, such as `aggregator.eth-usd.data.eth`.
- Reverse lookup is not supported. JavaScript can use `web3.eth.ens.getAddress("eth-usd.data.eth")`; Solidity callers resolve a `bytes32` node through the ENS registry/resolver. Any copied Solidity example is unaudited and requires review.

## Feed selection and market-data quality

Sources: [Price Feeds](https://docs.chain.link/data-feeds/price-feeds.md), [selecting feeds](https://docs.chain.link/data-feeds/selecting-data-feeds.md), [developer responsibilities](https://docs.chain.link/data-feeds/developer-responsibilities.md), [data sources](https://docs.chain.link/data-feeds/data-sources.md).

- Official selection categories are **Low**, **Medium**, **High**, and **Very High Market Pricing Risk**, plus **New Token**, **Custom**, and **Deprecating**. A category informs diligence; it does not replace application-specific risk parameters.
- Medium-risk drivers include low or inconsistent liquidity, large venue spreads, concentration on one exchange, cross-rate exposure, migrations or market events, provider dispersion, and changing source availability.
- High-risk feeds have heightened medium-risk factors and can be candidates for deprecation. Very-high-risk conditions include extreme volatility, hacks, bridge failures, delistings, severe liquidity loss, and other exceptional events.
- New Token feeds have limited history. Custom feeds need extra scrutiny and can represent an onchain single source, Proof of Reserve, an exchange rate rather than a market price, technical metrics, TVL, or a custom index.
- Price Feeds normally aggregate multiple sources through independent node operators, but exceptions include single-source feeds and calculated values. Confirm the sourcing model for the exact feed rather than assuming decentralization from the product name.
- Most crypto price, crypto state price, forex, precious-metals, US-oil, and US-equity feeds use at least three vendors/aggregators. UK and Euro ETF data can use two or more vendors and be delayed by 15 minutes. Data Link long-tail crypto can be a single aggregator source.
- Market integrity risks include spoofing, ramping, bear raids, cross-market manipulation, wash trading, and frontrunning. Low-liquidity assets are more vulnerable. The integrator owns monitoring, code/dependency audit, end-user disclosure, circuit breakers, and contingency behavior.
- Watch the Chainlink changelog and the Discord notification channel for classification and deprecation changes. Current classifications and sources belong to the live selection page.

## Registry and deprecation deltas

Sources: [contract registry](https://docs.chain.link/data-feeds/contract-registry.md), [deprecating feeds](https://docs.chain.link/data-feeds/deprecating-feeds.md), [price address directory](https://docs.chain.link/data-feeds/price-feeds/addresses.md).

- `IFlags.getFlag(proxy) == true` means the proxy is currently listed as official and active for that network. Inactive feeds are removed; the registry is maintained as deployments change.
- Each network has a different Flags contract. Never copy an address from another network or infer it from a proxy. Fetch the live table before constructing a registry call.
- Deprecation candidates include feeds with little/no usage or no viable economic-sustainability path. Data-quality monitoring stops two weeks before the published deprecation date.
- The live table fields include network, pair, deprecation date, deviation, heartbeat seconds, decimals, aggregator address, asset name/type, and market hours. Use it before mainnet launch and during ongoing monitoring.
- Officially documented feeds are reviewed; community/custom deployments can have additional risks. Registry status and documentation listing do not remove the integrator's diligence obligations.

## MVR proxy administration and client deltas

Sources: [MVR API](https://docs.chain.link/data-feeds/mvr-feeds/api-reference.md), [guide index](https://docs.chain.link/data-feeds/mvr-feeds/guides.md), [Solidity](https://docs.chain.link/data-feeds/mvr-feeds/guides/evm-solidity.md), [ethers v5](https://docs.chain.link/data-feeds/mvr-feeds/guides/ethersjs.md), [viem](https://docs.chain.link/data-feeds/mvr-feeds/guides/viem.md).

- `IBundleAggregatorProxy` combines bundle reads with common aggregator metadata and keeps consumers compatible across aggregator changes when they remain on the proxy.
- Administrative/view functions can include `aggregator()`, `proposedAggregator()`, and `confirmAggregator(address)`. They describe proxy upgrade state; ordinary consumers use the bundle read trio documented in `mvr-feeds.md`.
- The guide hub separates onchain Solidity, offchain ethers v5, and offchain viem paths. Ethers v6 differs from the cached v5 guide. Prefer the caller's installed client and the schema-neutral sequence in the curated reference.
- Ethers v5 uses `ethers.utils.defaultAbiCoder.decode` and `ethers.utils.formatUnits`; viem uses `decodeAbiParameters`, `readContract`, and `formatUnits`. Both need `RPC_URL`, a proxy address, the exact documented schema, per-field decimals, and a heartbeat-derived staleness threshold.
- A decimals array should align with the schema length. Numeric values can be kept raw to avoid Solidity truncation; booleans and other nonnumeric fields are not scaled.
- Examples in the official guides are unaudited and not production-ready without feed-specific validation, access/risk design, and review.

## SmartData, Proof of Reserve, and self-managed deltas

Sources: [SmartData](https://docs.chain.link/data-feeds/smartdata.md), [SmartData addresses](https://docs.chain.link/data-feeds/smartdata/addresses.md), [self-managed feeds](https://docs.chain.link/data-feeds/self-managed-feeds.md).

- Proof of Reserve answers can be quantities such as ounces or token counts, not prices. Interpret the feed description, units, decimals, and source model before using the answer in collateral logic.
- Offchain reserve data can come from custodians, fund administrators, auditors, asset managers, regulated appraisers, or other approved sources; cross-chain PoR can read onchain reserves from the asset-holding chain.
- Wallet-address-manager configuration differs across feeds and chains. A self-reporting manager can include addresses whose ownership is not cryptographically verified; an issuer could inflate reported reserves with addresses it does not control. Inspect each feed's address-page disclosure.
- Chainlink Labs disclaims responsibility for the accuracy of self-reported reserves. Treat issuer reporting and address ownership as trust assumptions and perform independent data-quality/issuer-risk analysis.
- A self-managed feed's third-party publication path has no Chainlink Labs monitoring for heartbeat or deviation compliance, end-to-end latency, write correctness, or publication SLA. Addresses come from the chain/operator rather than the public catalog.
- The self-managed architecture uses a CRE workflow to read Chainlink Data Streams and write a standard Data Feeds proxy. A familiar consumer interface does not imply Chainlink-operated publication.

## Solana deltas

Sources: [Solana overview](https://docs.chain.link/data-feeds/solana.md), [onchain v2 guide](https://docs.chain.link/data-feeds/solana/using-data-feeds-solana.md), [offchain guide](https://docs.chain.link/data-feeds/solana/using-data-feeds-off-chain.md).

- Programs contain logic and accounts contain feed state. Programs are stateless; local program tests are possible, but live Chainlink feeds require a supported onchain cluster. Price Feeds are on Mainnet and Devnet, not Solana Testnet.
- Cached OCR2 feed owner/program ID for v2 direct account validation: `HEvSKofvBgfaexv23kMabbYqxasxU3mQ4ibBMEmJWHny`. Cached offchain Data Feeds Store Program ID: `cjg3oHmg9uuPsP8D6g29NWvhySJkdYdAo9D25PRbKXJ`. Verify both before use.
- `chainlink_solana::v2::read_feed_v2(feed_data_bytes, feed_owner_pubkey_bytes)` returns a parsed feed exposing `latest_round_data()`, `description()`, and `decimals()`. V2 direct account reads replace the deprecated v1 CPI pattern and reduce compute use.
- Cached dependencies are `chainlink_solana = "2.0.8"` and, for Anchor, `anchor-lang = "0.31.1"`. Package versions can move.
- Offchain clients use `OCR2Feed.load(programId, provider)` and `onRound(feedAddress, listener)`. Cached packages are `@chainlink/solana-sdk` and `@project-serum/anchor`; the old guide states Node.js 14 or later.
- Anchor requires `ANCHOR_PROVIDER_URL` and `ANCHOR_WALLET` even for read-only calls. A wallet file needs no lamports for reads, but it is still a credential: do not expose, solicit, or commit wallet/private-key material.
- Network congestion can reduce update frequency. Monitor Solana status and validate feed freshness rather than treating expected cadence as guaranteed.

## Aptos deltas

Source: [Aptos guide](https://docs.chain.link/data-feeds/aptos.md).

- `data_feeds::router::get_benchmarks(account, feed_ids, billing_data)` accepts a vector of feed IDs and returns `vector<Benchmark>`; extract values with `get_benchmark_value` and timestamps with `get_benchmark_timestamp`.
- The reference's BTC/USD testnet feed ID is cached. The Chainlink platform and data-feeds package addresses are also network-specific; retrieve their complete live values from the guide rather than using shortened examples.
- A Move module can store `PriceData` under the signer and expose a `#[view] get_price_data(account_address)` accessor. This persistence pattern is optional; it is not required for a one-shot router read.
- Publishing or invoking an entry function consumes gas in Octas (`1 APT = 100,000,000 Octas`). Read model and feed identity remain router-plus-feed-ID, not one contract address per pair.

## Starknet deltas

Sources: [Starknet overview](https://docs.chain.link/data-feeds/starknet.md), [Foundry hub](https://docs.chain.link/data-feeds/starknet/tutorials/snfoundry.md), [offchain read](https://docs.chain.link/data-feeds/starknet/tutorials/snfoundry/read-data.md), [consumer](https://docs.chain.link/data-feeds/starknet/tutorials/snfoundry/consumer-contract.md), [Devnet RS](https://docs.chain.link/data-feeds/starknet/tutorials/snfoundry/sn-devnet-rs.md).

- `latest_round_data` returns hex-encoded fields in this order: `round_id`, `answer`, `block_num`, `started_at`, `updated_at`. Timestamps are Unix seconds. Decode by position; do not apply the EVM five-tuple ordering.
- Cached Starknet Sepolia ETH/USD proxy: `0x228128e84cdfc51003505dd5733729e57f7d1f7e54da679474e73db4ecaad44`. RPC provider documentation: [Alchemy supported chains](https://www.alchemy.com/docs/reference/node-supported-chains).
- `starkli call` and `sncast call` can read without an account. A deployed Cairo consumer requires a funded account. The tutorial hub separates read-only, deployed-consumer, and Docker-based Devnet RS flows.
- Cached tutorial versions are Starknet Foundry `0.21.0` and Scarb `2.6.4`; verify current compatibility before following repository scripts.
- ETH/USD cached examples use 8 decimals, but consumers still obtain/confirm precision for the selected feed rather than generalizing that value.

## SVR searcher protocol deltas

Sources: [SVR](https://docs.chain.link/data-feeds/svr-feeds.md), [Ethereum searchers](https://docs.chain.link/data-feeds/svr-feeds/searcher-onboarding-ethereum.md), [Atlas searchers](https://docs.chain.link/data-feeds/svr-feeds/searcher-onboarding-atlas.md).

- Ethereum events can be single-transaction or bundle events; bundle transactions are nonce-ordered. Updates originate from multiple forwarders, one per Node Operator Proxy, so a searcher cannot pin one sender address.
- The nested report decode is `(uint32 observationsTimestamp, bytes32 observers, int192[] observations, int192 juelsPerFeeCoin)`; searchers derive the median observation after decoding `forward` and `transmitSecondary` calldata.
- Atlas represents the oracle update and liquidation as EIP-712 user/solver operations bundled atomically without depending on block builders. The WebSocket JSON-RPC subscription uses method `solver_subscribe` with `userOperations`.
- The solver must simulate locally, sign the exact oracle-provided `gasPrice`, stay within `DappControl.getSolverGasLimit()`, maintain adequate bond for gas reimbursement, use buffers above 10 KB, and reconnect automatically.
- Atlas documentation covers Aave, Compound, and Venus integrations. Listen to the current aggregator, not proxy, for price reports; resolve it from `proxy.aggregator()` and verify live contract/feed addresses.
- Searcher examples and JSON schemas are indexed by exact path in `official-sources.md`. Operational endpoints, contracts, supported protocols, bonds, and auction mechanics can change; fetch the onboarding page before running a solver.

## Tokenized equity deltas

Sources: [tokenized equity](https://docs.chain.link/data-feeds/tokenized-equity-feeds.md), [Ondo](https://docs.chain.link/data-feeds/tokenized-equity-feeds/ondo.md), [providers](https://docs.chain.link/data-feeds/tokenized-equity-feeds/providers.md).

- A tokenized-equity feed prices the issuer's token instrument, not necessarily the raw underlying equity. Issuer methodology can incorporate total-return multipliers, dividends, and corporate actions.
- Provider coverage and quality are strongest during the regular US session and thinner pre-market, post-market, and overnight. Session-aware smoothing can reduce brief illiquid spikes but can lag legitimate rapid moves. Halts are not explicitly flagged.
- Ondo Total Return Value is `Underlying Equity Market Price × sValue`; `sValue` comes from `SyntheticSharesOracle`. Changes at or below 1% per 24 hours apply automatically; larger changes require a scheduled pause and manual confirmation.
- A corporate-action pause is scheduled at least 24 hours in advance; at pause time the feed freezes at its last known good token price until alignment is confirmed and the feed is unpaused. The configured minimum pause duration is at least 10 minutes.
- The provider directory records provider, feed type, calculation, corporate-action handling, documentation, and issuer contact. Provider behavior is not interchangeable. Contact `datafeeds@chain.link` and set protocol risk parameters before integration.

## Tron deltas

Source: [Tron guide](https://docs.chain.link/data-feeds/tron.md).

- Tron uses Solidity-compatible `AggregatorV3Interface`, but account/contract addresses are base58. Nile examples in the curated reference are not EVM hex addresses.
- The official `DataFeedReader.sol` shape exposes latest round data, latest price, decimals, and description. Its offchain TronWeb reader formats `BigInt` answers with runtime decimals and prints round/timestamp metadata.
- Deployment examples use TronBox and a Nile-only account. Never request, expose, paste into chat, or commit `PRIVATE_KEY_NILE`; keep secrets in the user's local environment and never use a production key for a tutorial.
- Cached tooling in the source expects Node.js 20+ and TronBox 3.3+ (the captured example reported TronBox 4.2.0 / Solidity 0.8.23). Tool versions are setup details, not part of the read model, and must be rechecked if compilation fails.

## Source retention ledger

Every source from the former per-URL dump was reviewed. Sources with no remaining delta are represented by their curated fact owner rather than repeated payloads:

| Sources | Curated owner / retained delta |
|---|---|
| `data-feeds.md`, `index.md`, `api-reference.md`, `llms-full.txt` | Contract inspection above; basic proxy/interface facts in `reading-price-feeds.md` |
| `getting-started.md`, `using-data-feeds.md` | Runnable consumer/readers in `reading-price-feeds.md` and starter kit |
| `historical-data.md` | Historical encoding and caveats in `reading-price-feeds.md` |
| `l2-sequencer-feeds.md` | Canonical consumer in `reading-price-feeds.md`; mechanics in `feed-operations.md` |
| `contract-registry.md`, `deprecating-feeds.md` | `feed-operations.md`; operational deltas above |
| `data-sources.md`, `developer-responsibilities.md`, `self-managed-feeds.md` | `feed-operations.md`; selection/trust deltas above |
| `feed-types.md`, `rates-feeds.md`, `smartdata.md` | `feed-types.md`; SmartData deltas above |
| `price-feeds.md`, `price-feeds/addresses.md`, `selecting-data-feeds.md` | `reading-price-feeds.md`, `official-sources.md`, and selection deltas above |
| `mvr-feeds.md`, its API, hub, Solidity, ethers, and viem guides | `mvr-feeds.md`; proxy/client deltas above |
| `svr-feeds.md` and both searcher guides | `svr-feeds.md`; protocol deltas above |
| `solana.md` and both Solana guides | `multi-chain.md`; Solana deltas above |
| `aptos.md` | `multi-chain.md`; Aptos deltas above |
| `starknet.md` and four Foundry/tutorial pages | `multi-chain.md`; Starknet deltas above |
| `tron.md` | `multi-chain.md`; Tron client/security deltas above |
| Tokenized equity overview, Ondo, and providers | `feed-types.md`; issuer-operation deltas above |
| Price, SmartData, rate/volatility, and U.S. macro address pages | `official-sources.md`; no stale address table duplicated here |
| `ens.md` | ENS delta above |
