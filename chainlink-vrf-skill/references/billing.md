# VRF v2.5 Billing

## Premiums and Timing

Ethereum mainnet charges a **20% LINK premium** or **24% native-payment premium** above base gas cost. Other networks may differ; verify the live values at https://docs.chain.link/vrf/v2-5/billing.md.

| Method | When charged | Callback gas charged |
|---|---|---|
| Subscription | After fulfillment | Actual gas consumed |
| Direct funding | Upfront when `requestRandomWords` is called; insufficient consumer balance reverts | Full configured limit, even if less is used |

Ask which asset the user prefers and default to LINK. A subscription request selects it with `ExtraArgsV1({nativePayment: false})` for LINK or `true` for native. A direct-funded consumer calls `requestRandomness` for LINK or `requestRandomnessPayInNative` for native. Fund the matching balance before requesting.

## Cost Formulas

Subscription:

```text
total gas cost = gas_price × (verification_gas + callback_gas_used)
total request cost = total gas cost × ((100 + premium%) / 100)
```

Direct funding:

```text
total gas cost = gas_price × (coordinator_overhead + callback_gas_limit + wrapper_overhead + (per_word_overhead × num_words))
total request cost = (coordinator_flat_fee + total gas cost) × ((100 + wrapper_premium%) / 100)
```

Subscriptions bill actual `callback_gas_used`; direct funding bills the configured `callback_gas_limit`. `coordinator_flat_fee` is denominated in millionths of LINK. Estimate with the target network's current gas lane, exchange rate, flat fee, and overheads rather than reusing mainnet values.

## Ethereum Mainnet Overheads

| Component | LINK | Native (ETH) |
|---|---:|---:|
| Coordinator overhead | 112,000 gas | 90,000 gas |
| Wrapper overhead | 13,400 gas | 13,400 gas |
| Per-word overhead | 435 gas/word | 435 gas/word |
| Premium | 20% | 24% |

These are Ethereum mainnet values. Testnets and other networks differ; verify https://docs.chain.link/vrf/v2-5/supported-networks.md before estimating.

## Funding and Withdrawal

Fund a subscription with ERC-677 LINK via the UI at https://vrf.chain.link or:

```solidity
LINK.transferAndCall(coordinatorAddress, linkAmount, abi.encode(subscriptionId));
```

Fund it with the native coin via:

```solidity
coordinator.fundSubscriptionWithNative{value: amount}(subscriptionId);
```

Cancel and withdraw LINK with `coordinator.cancelSubscription(subscriptionId, receivingAddress)`. Use the VRF UI to withdraw excess without cancellation. A direct-funded consumer instead receives LINK/native funds at its own address and exposes application-controlled withdrawals.

## PegSwap on Polygon and BNB Chain

LINK arriving from the canonical **Polygon** or **BNB Chain** bridge is ERC-20, not the ERC-677 LINK required for VRF funding. Convert bridge-sourced LINK to native ERC-677 LINK at https://pegswap.chain.link before funding a subscription or direct-funded consumer. LINK bought directly on those chains is already ERC-677 and does not need conversion.
