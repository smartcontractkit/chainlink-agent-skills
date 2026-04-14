# Multi-Chain Data Feeds (Solana, Aptos, StarkNet, Tron)

## Trigger Conditions

Read this file when:
- The user wants to read Chainlink Data Feeds on a non-EVM chain
- The user mentions Solana, Aptos, StarkNet, or Tron in a data feeds context
- The user asks about Move, Cairo, Anchor, or TronBox in a data feeds context

For EVM chain integrations, use `reading-price-feeds.md` instead.

## Chain Selection

| Chain | Language | Framework | Feed Model |
|-------|----------|-----------|------------|
| Solana | Rust | Anchor / native Solana | Account-based; use `chainlink_solana` SDK |
| Aptos | Move | Aptos CLI | Single contract queried by feed ID |
| StarkNet | Cairo | Starknet Foundry / Starkli | Cairo contracts on Starknet Sepolia |
| Tron | Solidity | TronBox | Similar to EVM; uses AggregatorV3Interface |

## Solana

### Architecture

- Feeds use Offchain Reporting (OCR); no dependency on Ethereum or external chains.
- Solana model: programs (logic) + accounts (data) — state and logic are separate.
- Price Feeds available on Solana **Mainnet** and **Devnet**. Testnet is not supported.
- High network congestion may reduce feed update frequency.

### On-Chain Reading (Rust / Anchor)

Use the Chainlink Solana SDK v2 for direct account reads (preferred over deprecated v1 CPI approach):

```toml
# Cargo.toml
[dependencies]
chainlink_solana = "2.0.8"
anchor-lang = "0.31.1"  # if using Anchor
```

```rust
use chainlink_solana::v2::read_feed_v2;

// OCR2 Data Feeds program ID (Devnet/Mainnet owner)
const FEED_OWNER: &str = "HEvSKofvBgfaexv23kMabbYqxasxU3mQ4ibBMEmJWHny";

// Read the feed account data
let feed = read_feed_v2(feed_account_data, feed_owner_pubkey_bytes)?;
let answer = feed.latest_round_data();
let description = feed.description();  // e.g., "SOL / USD"
let decimals = feed.decimals();
```

Do not depend on feed account memory layout — always use the SDK consumer library.

### Off-Chain Reading (JavaScript / TypeScript)

```bash
npm install @chainlink/solana-sdk @project-serum/anchor
```

```javascript
const { OCR2Feed } = require("@chainlink/solana-sdk");
const anchor = require("@project-serum/anchor");

// Set environment: ANCHOR_PROVIDER_URL=https://api.devnet.solana.com
//                  ANCHOR_WALLET=./id.json
const CHAINLINK_PROGRAM_ID = "cjg3oHmg9uuPsP8D6g29NWvhySJkdYdAo9D25PRbKXJ";

const provider = anchor.AnchorProvider.env();
const dataFeed = await OCR2Feed.load(CHAINLINK_PROGRAM_ID, provider);

// Subscribe to round updates
dataFeed.onRound(feedAddress, (event) => {
    console.log("Price:", event.answer.toNumber());
});
```

A wallet file is required even for read-only operations (Anchor requirement): `solana-keygen new --outfile ./id.json` (no SOL needed for reads).

### Starter Kit

```bash
git clone https://github.com/smartcontractkit/solana-starter-kit
cd solana-starter-kit && yarn install
node read-data.js
```

## Aptos

### Architecture

Aptos uses a **single Chainlink price feed contract** that serves multiple feeds. Developers query by passing feed ID(s), unlike EVM where each feed has its own contract address.

### Setup

```bash
aptos init --network=testnet --assume-yes
aptos move init --name aptos-data-feeds
```

Configure `Move.toml`:
```toml
[addresses]
sender = "<your-address>"
data_feeds = "0xf1099f...fdd3"   # testnet
platform = "0x516e77...c99"       # testnet
move_stdlib = "0x1"
aptos_std = "0x1"
```

Download Chainlink packages:
```bash
aptos move download --account <platform_addr> --package ChainlinkPlatform
aptos move download --account <datafeeds_addr> --package ChainlinkDataFeeds
```

Update `ChainlinkDataFeeds/Move.toml` to point ChainlinkPlatform dependency to local path.

### Reading a Feed (Move)

```move
use data_feeds::router::get_benchmarks;

public entry fun fetch_price(account: &signer, feed_id: vector<u8>) {
    let billing_data = vector::empty<u8>();
    let feed_ids = vector::singleton(feed_id);
    let benchmarks = get_benchmarks(account, feed_ids, billing_data);

    let benchmark = vector::borrow(&benchmarks, 0);
    let price = get_benchmark_value(benchmark);
    let timestamp = get_benchmark_timestamp(benchmark);
    // Store or use price and timestamp
}
```

Example BTC/USD testnet feed ID: `0x01a0b4d920000332000000000000000000000000000000000000000000000000`

### Deploy and Run

```bash
aptos move publish --skip-fetch-latest-git-deps
aptos move run --function-id '<ADDR>::MyOracleContractTest::fetch_price' --args hex:<feed_id>
```

Fund for gas: `aptos account fund-with-faucet --account <ADDR> --amount 100000000` (1 APT = 100M Octas).

## StarkNet

### Architecture

StarkNet is non-EVM; smart contracts use Cairo. Chainlink Data Feeds are deployed as Cairo contracts on Starknet Sepolia.

### Off-Chain Reading (Starkli CLI)

No Starknet account required for reads:

```bash
starkli call \
  0x228128e84cdfc51003505dd5733729e57f7d1f7e54da679474e73db4ecaad44 \
  latest_round_data \
  --rpc https://starknet-sepolia.public.blastapi.io/rpc/v0_7
```

Returns a hex array: `[round_id, answer, block_num, started_at, updated_at]`.

Any Starknet Sepolia RPC provider works (Blast API, Alchemy, Infura).

Example ETH/USD proxy: `0x228128e84cdfc51003505dd5733729e57f7d1f7e54da679474e73db4ecaad44`

### Off-Chain Reading (Starknet Foundry)

```bash
sncast --url <RPC> call \
  --contract-address 0x228128e84cdfc51003505dd5733729e57f7d1f7e54da679474e73db4ecaad44 \
  --function "latest_round_data"
```

### On-Chain Consumer Contract

Requirements: Starknet Foundry v0.21.0, Scarb v2.6.4.

```bash
git clone https://github.com/smartcontractkit/chainlink-starknet.git
cd chainlink-starknet/examples/contracts/aggregator_consumer/
make test  # verify setup
```

Deploy flow:
1. Create OpenZeppelin account: `make create-account`
2. Fund with testnet ETH (Blast Starknet Sepolia Faucet)
3. Deploy account: `make deploy-account`
4. Deploy consumer: `make ac-deploy NETWORK=testnet`
5. Interact: `make ac-set-answer NETWORK=testnet`, `make ac-read-answer NETWORK=testnet`

ETH/USD answers use 8 decimals. Deployed address may print in decimal — convert to hex.

### Local Devnet

Use Starknet Devnet RS (Docker-based local testnet):

```bash
make devnet                              # start devnet container
make add-account                         # import prefunded devnet account
make devnet-deploy                       # deploy mock aggregator + consumer
make agg-read-latest-round NETWORK=devnet
```

## Tron

### Architecture

Tron uses Solidity-compatible smart contracts with AggregatorV3Interface — similar to EVM chains. Deploy with TronBox.

### Setup

```bash
npm install -g tronbox  # >= 3.3
git clone https://github.com/smartcontractkit/smart-contract-examples.git
cd smart-contract-examples/data-feeds/tron/getting-started
cp .env.example .env
# Set PRIVATE_KEY_NILE=<your nile testnet private key>
source .env
```

Get test TRX: use TronLink wallet + `https://nileex.io/join/getJoinPage` for 2000 test TRX.

### Consumer Contract (Solidity on Tron)

The contract uses the same AggregatorV3Interface as EVM:

```solidity
// DataFeedReader.sol
import {AggregatorV3Interface} from "@chainlink/contracts/...";

function getLatestPrice() public view returns (int256) {
    (, int256 price, , , ) = dataFeed.latestRoundData();
    return price;
}
```

### Deploy and Read

```bash
tronbox compile
tronbox migrate --network nile
# Note the deployed contract address from output

# Edit offchain/reader.js with your deployed address
node offchain/reader.js
```

Test feed addresses (Nile testnet):
- BTC/USD: `TD3hrfAtPcnkLSsRh4UTgjXBo6KyRfT1AR`
- ETH/USD: `TYaLVmqGzz33ghKEMTdC64dUnde5LZc6Y3`

Note: Tron uses base58 addresses, not hex.

## Freshness Rules

1. Integration patterns (SDK versions, CLI commands, code patterns) are stable within major versions — use this file directly.
2. Feed addresses, program IDs, and RPC endpoints may change — fetch the chain-specific docs page for current values when the user needs a specific address.
3. Package/dependency versions may update — verify against the docs page if the user reports compilation errors with versions in this file.

## Triggering Tests

- "How do I read a Chainlink price feed on Solana?"
- "I need to integrate price data in my Aptos Move contract"
- "Can I use Chainlink Data Feeds on StarkNet?"
- "Set up a Chainlink data feed consumer on Tron testnet"

## Functional Tests

1. Solana response uses chainlink_solana SDK v2, not deprecated v1 CPI pattern.
2. Aptos response explains the single-contract-with-feed-ID model.
3. StarkNet response distinguishes between off-chain reads (no account) and on-chain consumer (account + deploy).
4. Tron response uses TronBox and base58 addresses.
5. All responses include validation guidance appropriate to the chain.

## Eval Checks

1. Correct chain identified and chain-specific patterns used (not EVM patterns on non-EVM chains).
2. SDK/framework versions match current recommendations.
3. Example feed addresses and program IDs are realistic (not invented).
4. Off-chain vs on-chain reading paths distinguished where applicable.
5. Prerequisites mentioned (CLI tools, wallets, test tokens).

## A/B Prompt Pack

- "Read the SOL/USD price in a Solana Anchor program"
- "I want to fetch BTC/USD on Aptos testnet using Move"
- "Read ETH/USD price from StarkNet using the CLI without deploying anything"
- "Deploy a Chainlink price feed consumer on Tron Nile testnet"
