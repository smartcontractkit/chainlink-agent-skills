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
