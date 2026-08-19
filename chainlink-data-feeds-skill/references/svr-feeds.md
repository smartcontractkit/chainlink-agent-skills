# SVR Feeds (Smart Value Recapture)

## Trigger Conditions

Read this file when:
- The user asks about Smart Value Recapture or SVR feeds
- The user mentions OEV (oracle-extractable value) or MEV recapture
- The user wants to integrate SVR feeds into a DeFi protocol
- The user is a searcher wanting to participate in SVR auctions

## SVR Architecture

SVR extends standard Chainlink Price Feeds to recapture oracle-extractable value — primarily non-toxic liquidation-related MEV — via an optional private transmission route and auction.

### How it works

1. **Dual transmission**: Each price update is sent through two paths:
   - Standard Aggregator: transmitted via the public mempool (normal path)
   - SVR Aggregator: transmitted via a private channel (e.g., Flashbots MEV-Share on Ethereum, Atlas on Base/Arbitrum/BNB Chain)

2. **Auction**: Searchers bid to backrun the oracle update with a liquidation. The builder selects the highest bid and bundles the liquidation in the same block.

3. **Fail-safe**: If the private route fails or times out, the SVR feed reverts to the Standard Feed price after a configurable delay.

4. **Revenue split**: Recaptured OEV is split between the integrating protocol and the Chainlink Network. The split may change over time.

### Supported auction systems by network

- **Ethereum Mainnet**: Flashbots MEV-Share
- **Base, Arbitrum, BNB Chain**: Atlas

## Protocol Integration

Integrating SVR feeds is minimal — the interface is identical to standard Price Feeds. The only difference is the feed address.

### Steps

1. Fill out the Chainlink compatibility form (required before integration).
2. Find the SVR feed address on the Feed Addresses page — filter for "SVR" feeds.
3. Read the feed using AggregatorV3Interface with the SVR address instead of the standard address.


All standard validation applies: staleness checks, bounds checks, L2 sequencer checks (if on L2).

### Validated consumer

```solidity
import {AggregatorV3Interface} from
    "@chainlink/contracts/src/v0.8/shared/interfaces/AggregatorV3Interface.sol";

contract SVRConsumer {
    AggregatorV3Interface public immutable svrFeed;
    uint256 public immutable maxAge;
    int256 public immutable minPrice;
    int256 public immutable maxPrice;

    constructor(address proxy, uint256 age, int256 min, int256 max) {
        require(proxy != address(0) && age != 0, "Invalid config");
        require(min > 0 && max > min, "Invalid bounds");
        svrFeed = AggregatorV3Interface(proxy);
        maxAge = age;
        minPrice = min;
        maxPrice = max;
    }

    function latestPrice() external view returns (int256, uint8) {
        (, int256 answer,, uint256 updatedAt,) =
            svrFeed.latestRoundData();
        require(updatedAt != 0 && updatedAt <= block.timestamp, "Invalid round");
        require(block.timestamp - updatedAt <= maxAge, "Stale price");
        require(answer >= minPrice && answer <= maxPrice, "Price out of bounds");
        return (answer, svrFeed.decimals());
    }
}
```

Set `maxAge` from the feed heartbeat and configure asset-specific bounds. On an L2, perform the sequencer check before this read and enforce the 3600-second recovery grace period.

### Risks to communicate

- SVR introduces a delay (private route auction adds latency vs standard public mempool)
- Liquidation competition still exists — searchers compete in the auction
- MEV is not eliminated, only partially recaptured
- Recapture rates are dynamic and may vary

## Searcher Onboarding — Ethereum (MEV-Share)

### Flow

1. **Monitor** the Flashbots MEV-Share private mempool for SVR price update transactions.
2. **Filter** pending tx events by the `forward()` function selector `0x6fadcf72`.
3. **Decode** the nested calldata: `forward(address to, bytes callData)` contains an encoded `transmitSecondary(bytes32[3] reportContext, bytes report, bytes32[] rs, bytes32[] ss, bytes32 rawVs)` call.
4. **Extract** the updated feed address and median price from the report bytes: decode to `(uint32 observationsTimestamp, bytes32 observers, int192[] observations, int192 juelsPerFeeCoin)`.
5. **Construct** a liquidation transaction to backrun the price update in the same bundle.
6. **Submit** the bundle to MEV-Share with your bid.

### Key details

- Price updates come from multiple forwarder contracts (per Node Operator Proxy) — updates may originate from different addresses.
- MEV-Share can emit single-transaction events or bundle events; bundle txs are in ascending nonce order.
- Searcher submits liquidation tx in same bundle as price update; highest bid wins.
- Contact: svr@chain.link

## Searcher Onboarding — Atlas (Base, Arbitrum, BNB Chain)

### Flow

1. **Connect** to the SVR bid endpoint WebSocket: `wss://svr-bid-endpoint.chain.link/ws/solver`
2. **Receive** user operations (oracle updates) as EIP-712 messages.
3. **Simulate** solver operations locally — failed sims never hit chain.
4. **Sign** the required payloads: EIP-191 message format `<auctionID>:<userOperationHash>:<solverOperationFrom>` (colon-delimited).
5. **Submit** the solution. The final bundled transaction is submitted by Chainlink oracles, not the searcher.

### Key details

- Bond native tokens with Atlas contracts for gas reimbursement: Base/Arbitrum 0.1 ETH, BNB Chain 1 BNB.
- The gas price is chosen by the Chainlink oracle and provided at auction start. Solver must sign gasPrice exactly equal to provided value.
- Do not exceed `SolverGasLimit` (query via `DappControl.getSolverGasLimit`).
- Set WebSocket read/write buffers > 10KB and implement auto-reconnect.
- Listen to the **aggregator** address for price reports, not the proxy. Get aggregator via `proxy.aggregator()`.
- Use Aave-SVR feeds for Aave and SVR feeds for other protocols.
- Contact: svr@chain.link

## Freshness Rules

1. SVR feed addresses and supported networks may change — fetch the address page when the user asks for a specific SVR feed address.
2. Auction mechanics and Atlas contract addresses may be updated — fetch the searcher onboarding page when the user needs current operational details.
3. The integration pattern (AggregatorV3Interface with SVR address) is stable and can be used from this file directly.

