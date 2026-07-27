# Chainlink Data Feeds Foundry Starter Kit Template

Use this template when a user asks for a working Data Feeds project, a Foundry starter kit, or a runnable example. It is based on the Chainlink Foundry Starter Kit `PriceFeedConsumer.sol` pattern and adds the skill's required validation: round completion, staleness, positive answer checks, and runtime decimals access.

## Files

```text
foundry.toml
remappings.txt
src/PriceFeedConsumer.sol
script/PriceFeedConsumer.s.sol
test/PriceFeedConsumer.t.sol
test/mocks/MockV3Aggregator.sol
```

## Dependencies

For a fresh Foundry project, install these dependencies before running the template:

```sh
forge install foundry-rs/forge-std
forge install smartcontractkit/chainlink-evm@contracts-v1.5.0
```

The included `remappings.txt` expects Chainlink contracts under `lib/chainlink-evm/` and forge-std under `lib/forge-std/`.

## Default Network

The deploy script defaults to Sepolia ETH/USD:

```text
0x694AA1769357215DE4FAC081bf1f309aDC325306
```

Tell users to verify feed addresses against the official Chainlink docs before deploying. For L2 networks, add a Sequencer Uptime Feed check before production use.

## Commands

```sh
forge test
forge script script/PriceFeedConsumer.s.sol:DeployPriceFeedConsumer --rpc-url $SEPOLIA_RPC_URL --private-key $PRIVATE_KEY --broadcast
```

Example code is unaudited and should be reviewed before production use.

## Adapt This Template

The template is a complete, compiling reference. Two layers behave differently when you adapt it.

**Must be preserved exactly** — these are safety requirements, not style choices:

- The `AggregatorV3Interface` import path and the `latestRoundData()` destructuring, written exactly
  as `(, int256 price,, uint256 updatedAt,) = priceFeed.latestRoundData();`. Every tuple element must
  be declared in the destructuring. Assigning into a named return or other pre-existing variable
  while declaring another element inline is a syntax error, not a style preference.
- The round-completion check (`updatedAt == 0`), the staleness check against a threshold, and the
  positive-answer check. Every read path that returns or derives a price must pass through all three.
- Reading `decimals()` from the feed at runtime. Never hardcode a decimal count.
- Feed addresses and the dependency pins in `remappings.txt`. Copy these from the template or the
  official docs rather than retyping them; a mistyped address literal fails EIP-55 checksum
  validation and will not compile.
- On L2 networks (Arbitrum, Optimism, Base, Scroll, and similar) an L2 Sequencer Uptime Feed check
  with a grace period, added before any price is trusted. The template targets Sepolia and does not
  include one.
- Never using `answeredInRound` for freshness. The field is deprecated.

**Replace to fit the user's use case** — these are illustrative, not prescriptive:

- The `PriceFeedConsumer` contract name and file names.
- `getLatestPrice()` returning a raw `int256`, plus `getDecimals()` and `getPriceFeed()`. If the
  application needs a derived value (a collateral ratio, a quote, a converted amount), expose that
  and keep the raw read internal rather than shipping both surfaces.
- The immutable-vs-settable choice for the feed address.
- The deploy script's mock-vs-live branch and the test names.

**Tune, do not copy** — the template's values are placeholders:

- `stalenessThreshold` (template: `3600`). Look up the target feed's actual heartbeat, state it, and
  derive the threshold from it as heartbeat plus a buffer. Heartbeats differ per feed and per chain,
  and many are well under an hour. A threshold shorter than the heartbeat reverts during normal
  operation; leaving the template's hour in place on a 20-minute feed silently widens the staleness
  window.
- The mock's `DECIMALS` (`8`) and `INITIAL_ANSWER`. These match ETH/USD; other feeds differ.

When the derived value does arithmetic on the price, scale by the feed's runtime `decimals()` rather
than assuming 8, and order the operations so multiplication precedes division.

Errors carrying parameters (`StalePrice(uint256)`, `InvalidPrice(int256)`) must be asserted in tests
with `abi.encodeWithSelector(...)`. A bare `vm.expectRevert(Err.selector)` does not match a revert
payload that includes encoded arguments.
