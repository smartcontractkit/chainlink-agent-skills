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

Solana feeds are OCR account data read through `chainlink_solana`, not external-chain dependencies. They are available on Mainnet and Devnet (not Testnet); congestion can slow updates.

### On-Chain Reading (Rust / Anchor)

Use the Chainlink Solana SDK v2; validate the account and round before using the value:

```rust
use anchor_lang::{prelude::*, solana_program::pubkey};
use chainlink_solana::v2::read_feed_v2;

const FEED_OWNER: Pubkey =
    pubkey!("HEvSKofvBgfaexv23kMabbYqxasxU3mQ4ibBMEmJWHny");
const MAX_AGE: i64 = 3_600; // replace with this feed's heartbeat + buffer

pub fn read_sol_usd(ctx: Context<ReadSolUsd>) -> Result<()> {
    let account = &ctx.accounts.feed;
    let data = account.try_borrow_data()?;
    let feed = read_feed_v2(data, account.owner.to_bytes())
        .map_err(|_| error!(FeedError::InvalidFeed))?;

    require!(feed.description().starts_with(b"SOL / USD"), FeedError::WrongFeed);
    let round = feed.latest_round_data()
        .ok_or(error!(FeedError::StaleOrIncomplete))?;
    let updated_at = round.timestamp as i64;
    let answer = round.answer;
    let decimals = feed.decimals();
    let now = Clock::get()?.unix_timestamp;

    require!(answer > 0, FeedError::InvalidPrice);
    require!(
        updated_at > 0
            && updated_at <= now
            && now.saturating_sub(updated_at) <= MAX_AGE,
        FeedError::StaleOrIncomplete
    );
    msg!("SOL/USD raw price: {}; decimals: {}", answer, decimals);
    Ok(())
}

#[derive(Accounts)]
pub struct ReadSolUsd<'info> {
    /// CHECK: owner and SDK decoding are checked before use.
    #[account(owner = FEED_OWNER)]
    pub feed: UncheckedAccount<'info>,
}

#[error_code]
pub enum FeedError { InvalidFeed, WrongFeed, InvalidPrice, StaleOrIncomplete }
```

`FEED_OWNER` is the OCR2 program, not a feed address. Pass the verified SOL/USD feed account and confirm the current owner, account, identity, and heartbeat in official docs.

### Off-Chain Validation

Validate a decoded SDK round before it drives application logic:

```javascript
function validateRound(round, decimals, now, maxAge) {
  const answer = BigInt(round.answer.toString());
  const updatedAt = Number(round.timestamp);
  if (answer <= 0n) throw new Error("invalid price");
  if (!updatedAt || updatedAt > now || now - updatedAt > maxAge)
    throw new Error("stale or incomplete round");
  return { answer, decimals }; // raw integer
}
```

First verify the feed account's OCR2 owner and description/identity, and obtain `decimals()` at runtime. Never decode the account layout yourself.


## Aptos

### Architecture

Aptos uses a **single Chainlink price feed contract** that serves multiple feeds. Developers query by passing feed ID(s), unlike EVM where each feed has its own contract address.

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

### On-Chain Model

Onchain consumers are Cairo contracts that call the Starknet aggregator proxy; unlike read-only `starkli`/`sncast` calls, deployment requires a funded Starknet account. The official `chainlink-starknet/examples/contracts/aggregator_consumer/` example covers Sepolia and local Devnet RS.

## Tron

### Architecture

Tron uses Solidity-compatible smart contracts with AggregatorV3Interface — similar to EVM chains. Deploy with TronBox.


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


Test feed addresses (Nile testnet):
- BTC/USD: `TD3hrfAtPcnkLSsRh4UTgjXBo6KyRfT1AR`
- ETH/USD: `TYaLVmqGzz33ghKEMTdC64dUnde5LZc6Y3`

Note: Tron uses base58 addresses, not hex.

## Freshness Rules

1. Integration patterns (SDK versions, CLI commands, code patterns) are stable within major versions — use this file directly.
2. Feed addresses, program IDs, and RPC endpoints may change — fetch the chain-specific docs page for current values when the user needs a specific address.
3. Package/dependency versions may update — verify against the docs page if the user reports compilation errors with versions in this file.

