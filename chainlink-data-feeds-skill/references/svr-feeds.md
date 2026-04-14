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

```solidity
// Same interface as standard price feeds — only the address changes
AggregatorV3Interface internal svrPriceFeed;

constructor(address _svrFeedAddress) {
    svrPriceFeed = AggregatorV3Interface(_svrFeedAddress);
}

function getLatestPrice() public view returns (int256) {
    (, int256 price, , uint256 updatedAt, ) = svrPriceFeed.latestRoundData();
    require(block.timestamp - updatedAt <= STALENESS_THRESHOLD, "Stale price");
    require(price > 0, "Invalid price");
    return price;
}
```

All standard validation applies: staleness checks, bounds checks, L2 sequencer checks (if on L2).

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

## Triggering Tests

- "I want to integrate SVR feeds into my lending protocol"
- "How do I participate in Chainlink SVR auctions as a searcher?"
- "What's the difference between SVR and regular price feeds?"

## Functional Tests

1. Protocol integration response uses AggregatorV3Interface with the SVR feed address.
2. Response explains that SVR is identical to standard feeds except for the address and the addition of MEV recapture.
3. Searcher onboarding response distinguishes between Ethereum (MEV-Share) and Atlas (Base/Arbitrum/BNB) paths.
4. Response mentions the compatibility form requirement before integration.

## Eval Checks

1. Consumer code uses standard AggregatorV3Interface — not a custom SVR interface.
2. Staleness and bounds validation included in generated code.
3. Searcher guidance includes correct WebSocket endpoint and signing format.
4. Risks (delay, competition, dynamic rates) are mentioned for protocol integration.
5. Correct auction system identified for the user's target network.

## A/B Prompt Pack

- "Set up SVR price feeds for my Aave fork on Ethereum mainnet"
- "I'm a searcher and I want to bid on Chainlink SVR auctions on Base"
- "What do I need to change in my existing price feed consumer to use SVR?"
