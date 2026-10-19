# Chain Selectors

## Contents

- Trigger Conditions
- EIP-155 Chain ID to CRE Chain Selector Name Mapping
- Forwarder Addresses
- Freshness Note

Use this file when the user needs an EIP-155 chain ID to chain selector name mapping, forwarder addresses for a specific network, or the forwarder directory page cannot be fetched.

## Trigger Conditions

- "What chain selector name do I use for Arbitrum Sepolia?"
- "What's the chain ID for this CRE chain selector?"
- "What forwarder address do I use on Base Sepolia?"

Do not use for workflow code patterns (see workflow-patterns.md) or operational concerns (see operations.md).

## EIP-155 Chain ID to CRE Chain Selector Name Mapping

The CRE chain selector name is the value for `project.yaml` and the EVM client. Chain IDs match that name in `smartcontractkit/chain-selectors`. For a network that is not in these tables, fetch the official forwarder directory before you use a name or an address.

Ethereum Hoodi Testnet uses CRE name `ethereum-hoodi-testnet`. chain-selectors names chain id 560048 `ethereum-testnet-hoodi`. Use the CRE name in workflow config and EVM client code.

### Mainnets

| Network             | EIP-155 Chain ID | CRE Chain Selector Name         |
| ------------------- | ---------------- | ------------------------------- |
| ADI Mainnet         | 36900            | `adi-mainnet`                   |
| Arbitrum One        | 42161            | `ethereum-mainnet-arbitrum-1`   |
| Avalanche           | 43114            | `avalanche-mainnet`             |
| Base                | 8453             | `ethereum-mainnet-base-1`       |
| BNB Smart Chain     | 56               | `binance_smart_chain-mainnet`   |
| Celo                | 42220            | `celo-mainnet`                  |
| Ethereum Mainnet    | 1                | `ethereum-mainnet`              |
| Gnosis Chain        | 100              | `gnosis_chain-mainnet`          |
| Hyperliquid Mainnet | 999              | `hyperliquid-mainnet`           |
| Ink                 | 57073            | `ethereum-mainnet-ink-1`        |
| Jovay Mainnet       | 5734951          | `jovay-mainnet`                 |
| Linea               | 59144            | `ethereum-mainnet-linea-1`      |
| Mantle              | 5000             | `ethereum-mainnet-mantle-1`     |
| MegaETH             | 4326             | `megaeth-mainnet`               |
| Monad               | 143              | `monad-mainnet`                 |
| OP Mainnet          | 10               | `ethereum-mainnet-optimism-1`   |
| Pharos Mainnet      | 1672             | `pharos-mainnet`                |
| Plasma              | 9745             | `plasma-mainnet`                |
| Polygon             | 137              | `polygon-mainnet`               |
| Scroll              | 534352           | `ethereum-mainnet-scroll-1`     |
| Sonic               | 146              | `sonic-mainnet`                 |
| World Chain         | 480              | `ethereum-mainnet-worldchain-1` |
| XLayer Mainnet      | 196              | `ethereum-mainnet-xlayer-1`     |
| ZKSync Era          | 324              | `ethereum-mainnet-zksync-1`     |

### Testnets

| Network                     | EIP-155 Chain ID | CRE Chain Selector Name                 |
| --------------------------- | ---------------- | --------------------------------------- |
| ADI Testnet                 | 99999            | `adi-testnet`                           |
| Apechain Curtis             | 33111            | `apechain-testnet-curtis`               |
| Arc Testnet                 | 5042002          | `arc-testnet`                           |
| Arbitrum Sepolia            | 421614           | `ethereum-testnet-sepolia-arbitrum-1`   |
| Avalanche Fuji              | 43113            | `avalanche-testnet-fuji`                |
| Base Sepolia                | 84532            | `ethereum-testnet-sepolia-base-1`       |
| BSC Testnet                 | 97               | `binance_smart_chain-testnet`           |
| Celo Sepolia                | 11142220         | `celo-sepolia`                          |
| Cronos Testnet              | 338              | `cronos-testnet`                        |
| Ethereum Hoodi Testnet      | 560048           | `ethereum-hoodi-testnet`                |
| Ethereum Sepolia            | 11155111         | `ethereum-testnet-sepolia`              |
| Gnosis Chiado               | 10200            | `gnosis_chain-testnet-chiado`           |
| Hyperliquid Testnet         | 998              | `hyperliquid-testnet`                   |
| Ink Sepolia                 | 763373           | `ink-testnet-sepolia`                   |
| Jovay Testnet               | 2019775          | `jovay-testnet`                         |
| Linea Sepolia               | 59141            | `ethereum-testnet-sepolia-linea-1`      |
| Mantle Sepolia              | 5003             | `ethereum-testnet-sepolia-mantle-1`     |
| MegaETH Testnet 2           | 6343             | `megaeth-testnet-2`                     |
| Monad Testnet               | 10143            | `monad-testnet`                         |
| OP Sepolia                  | 11155420         | `ethereum-testnet-sepolia-optimism-1`   |
| Pharos Atlantic Testnet     | 688689           | `pharos-atlantic-testnet`               |
| Plasma Testnet              | 9746             | `plasma-testnet`                        |
| Polygon Amoy                | 80002            | `polygon-testnet-amoy`                  |
| Robinhood Testnet           | 46630            | `robinhood-testnet`                     |
| Scroll Sepolia (deprecated) | 534351           | `ethereum-testnet-sepolia-scroll-1`     |
| Sonic Testnet               | 14601            | `sonic-testnet`                         |
| Stable Testnet              | 2201             | `stable-testnet`                        |
| TAC Testnet                 | 2391             | `tac-testnet`                           |
| T-REX Testnet (deprecated)  | 364301           | `t-rex-testnet`                         |
| Unichain Sepolia            | 1301             | `ethereum-testnet-sepolia-unichain-1`   |
| World Chain Sepolia         | 4801             | `ethereum-testnet-sepolia-worldchain-1` |
| XLayer Testnet              | 1952             | `xlayer-testnet`                        |
| ZKSync Era Sepolia          | 300              | `ethereum-testnet-sepolia-zksync-1`     |

## Forwarder Addresses

### Production Forwarders (KeystoneForwarder)

Used by deployed workflows. Configure these in consumer contract constructors for production.

### Mainnets

| Network             | CRE Chain Selector Name         | Forwarder Address                            |
| ------------------- | ------------------------------- | -------------------------------------------- |
| ADI Mainnet         | `adi-mainnet`                   | `0x76c9cf548b4179F8901cda1f8623568b58215E62` |
| Arbitrum One        | `ethereum-mainnet-arbitrum-1`   | `0xF8344CFd5c43616a4366C34E3EEE75af79a74482` |
| Avalanche           | `avalanche-mainnet`             | `0x76c9cf548b4179F8901cda1f8623568b58215E62` |
| Base                | `ethereum-mainnet-base-1`       | `0xF8344CFd5c43616a4366C34E3EEE75af79a74482` |
| BNB Smart Chain     | `binance_smart_chain-mainnet`   | `0x76c9cf548b4179F8901cda1f8623568b58215E62` |
| Celo                | `celo-mainnet`                  | `0x98B8335d29Aca40840Ed8426dA1A0aAa8677d8D1` |
| Ethereum Mainnet    | `ethereum-mainnet`              | `0x0b93082D9b3C7C97fAcd250082899BAcf3af3885` |
| Gnosis Chain        | `gnosis_chain-mainnet`          | `0x9eF6468C5f37b976E57d52054c693269479A784d` |
| Hyperliquid Mainnet | `hyperliquid-mainnet`           | `0x9eF6468C5f37b976E57d52054c693269479A784d` |
| Ink                 | `ethereum-mainnet-ink-1`        | `0x9eF6468C5f37b976E57d52054c693269479A784d` |
| Jovay Mainnet       | `jovay-mainnet`                 | `0x76c9cf548b4179F8901cda1f8623568b58215E62` |
| Linea               | `ethereum-mainnet-linea-1`      | `0x9eF6468C5f37b976E57d52054c693269479A784d` |
| Mantle              | `ethereum-mainnet-mantle-1`     | `0xB9F79d863261869B234c481D1f9A7af84AeAd192` |
| MegaETH             | `megaeth-mainnet`               | `0x7BCcaFBD064cB3658476066Cc33ceE3F3414c04c` |
| Monad               | `monad-mainnet`                 | `0x76c9cf548b4179F8901cda1f8623568b58215E62` |
| OP Mainnet          | `ethereum-mainnet-optimism-1`   | `0xF8344CFd5c43616a4366C34E3EEE75af79a74482` |
| Pharos Mainnet      | `pharos-mainnet`                | `0x76c9cf548b4179F8901cda1f8623568b58215E62` |
| Plasma              | `plasma-mainnet`                | `0x7BCcaFBD064cB3658476066Cc33ceE3F3414c04c` |
| Polygon             | `polygon-mainnet`               | `0x76c9cf548b4179F8901cda1f8623568b58215E62` |
| Scroll              | `ethereum-mainnet-scroll-1`     | `0x98B8335d29Aca40840Ed8426dA1A0aAa8677d8D1` |
| Sonic               | `sonic-mainnet`                 | `0x98B8335d29Aca40840Ed8426dA1A0aAa8677d8D1` |
| World Chain         | `ethereum-mainnet-worldchain-1` | `0x98B8335d29Aca40840Ed8426dA1A0aAa8677d8D1` |
| XLayer Mainnet      | `ethereum-mainnet-xlayer-1`     | `0x76c9cf548b4179F8901cda1f8623568b58215E62` |
| ZKSync Era          | `ethereum-mainnet-zksync-1`     | `0x76c9cf548b4179F8901cda1f8623568b58215E62` |

### Testnets

| Network                     | CRE Chain Selector Name                 | Forwarder Address                            |
| --------------------------- | --------------------------------------- | -------------------------------------------- |
| ADI Testnet                 | `adi-testnet`                           | `0x76c9cf548b4179F8901cda1f8623568b58215E62` |
| Apechain Curtis             | `apechain-testnet-curtis`               | `0x76c9cf548b4179F8901cda1f8623568b58215E62` |
| Arc Testnet                 | `arc-testnet`                           | `0x76c9cf548b4179F8901cda1f8623568b58215E62` |
| Arbitrum Sepolia            | `ethereum-testnet-sepolia-arbitrum-1`   | `0x76c9cf548b4179F8901cda1f8623568b58215E62` |
| Avalanche Fuji              | `avalanche-testnet-fuji`                | `0x76c9cf548b4179F8901cda1f8623568b58215E62` |
| Base Sepolia                | `ethereum-testnet-sepolia-base-1`       | `0xF8344CFd5c43616a4366C34E3EEE75af79a74482` |
| BSC Testnet                 | `binance_smart_chain-testnet`           | `0x76c9cf548b4179F8901cda1f8623568b58215E62` |
| Celo Sepolia                | `celo-sepolia`                          | `0x9eF6468C5f37b976E57d52054c693269479A784d` |
| Cronos Testnet              | `cronos-testnet`                        | `0x9eF6468C5f37b976E57d52054c693269479A784d` |
| Ethereum Hoodi Testnet      | `ethereum-hoodi-testnet`                | `0x76c9cf548b4179F8901cda1f8623568b58215E62` |
| Ethereum Sepolia            | `ethereum-testnet-sepolia`              | `0xF8344CFd5c43616a4366C34E3EEE75af79a74482` |
| Gnosis Chiado               | `gnosis_chain-testnet-chiado`           | `0x0b93082D9b3C7C97fAcd250082899BAcf3af3885` |
| Hyperliquid Testnet         | `hyperliquid-testnet`                   | `0x76c9cf548b4179F8901cda1f8623568b58215E62` |
| Ink Sepolia                 | `ink-testnet-sepolia`                   | `0x76c9cf548b4179F8901cda1f8623568b58215E62` |
| Jovay Testnet               | `jovay-testnet`                         | `0x76c9cf548b4179F8901cda1f8623568b58215E62` |
| Linea Sepolia               | `ethereum-testnet-sepolia-linea-1`      | `0x76c9cf548b4179F8901cda1f8623568b58215E62` |
| Mantle Sepolia              | `ethereum-testnet-sepolia-mantle-1`     | `0xB9F79d863261869B234c481D1f9A7af84AeAd192` |
| MegaETH Testnet 2           | `megaeth-testnet-2`                     | `0x9eF6468C5f37b976E57d52054c693269479A784d` |
| Monad Testnet               | `monad-testnet`                         | `0xF8344CFd5c43616a4366C34E3EEE75af79a74482` |
| OP Sepolia                  | `ethereum-testnet-sepolia-optimism-1`   | `0x76c9cf548b4179F8901cda1f8623568b58215E62` |
| Pharos Atlantic Testnet     | `pharos-atlantic-testnet`               | `0x76c9cf548b4179F8901cda1f8623568b58215E62` |
| Plasma Testnet              | `plasma-testnet`                        | `0x76c9cf548b4179F8901cda1f8623568b58215E62` |
| Polygon Amoy                | `polygon-testnet-amoy`                  | `0x76c9cf548b4179F8901cda1f8623568b58215E62` |
| Robinhood Testnet           | `robinhood-testnet`                     | `0x8E6E6A1f2B2D4dF503bfd67951CF28F27BF3AF19` |
| Scroll Sepolia (deprecated) | `ethereum-testnet-sepolia-scroll-1`     | `0x98B8335d29Aca40840Ed8426dA1A0aAa8677d8D1` |
| Sonic Testnet               | `sonic-testnet`                         | `0x98B8335d29Aca40840Ed8426dA1A0aAa8677d8D1` |
| Stable Testnet              | `stable-testnet`                        | `0x701d026D1c85BA1DCbc3EEbe3636D646D88a0Aae` |
| TAC Testnet                 | `tac-testnet`                           | `0x7BCcaFBD064cB3658476066Cc33ceE3F3414c04c` |
| T-REX Testnet (deprecated)  | `t-rex-testnet`                         | `0x8E6E6A1f2B2D4dF503bfd67951CF28F27BF3AF19` |
| Unichain Sepolia            | `ethereum-testnet-sepolia-unichain-1`   | `0x98B8335d29Aca40840Ed8426dA1A0aAa8677d8D1` |
| World Chain Sepolia         | `ethereum-testnet-sepolia-worldchain-1` | `0x76c9cf548b4179F8901cda1f8623568b58215E62` |
| XLayer Testnet              | `xlayer-testnet`                        | `0x9eF6468C5f37b976E57d52054c693269479A784d` |
| ZKSync Era Sepolia          | `ethereum-testnet-sepolia-zksync-1`     | `0x76c9cf548b4179F8901cda1f8623568b58215E62` |

### Simulation Forwarders (MockKeystoneForwarder)

Used with `cre workflow simulate --broadcast`. Use these only during local development and testing.

ADI Mainnet has a production forwarder and no simulation row on the directory page. Fetch that page, or run `cre workflow supported-chains` after `cre login`, before a broadcast simulation on ADI Mainnet.

### Mainnets

| Network             | CRE Chain Selector Name         | Mock Forwarder Address                       |
| ------------------- | ------------------------------- | -------------------------------------------- |
| Arbitrum One        | `ethereum-mainnet-arbitrum-1`   | `0xd770499057619c9a76205fd4168161cf94abc532` |
| Avalanche           | `avalanche-mainnet`             | `0xdc21e279934ff6721cadfdd112dafb3261f09a2c` |
| Base                | `ethereum-mainnet-base-1`       | `0x5e342a8438b4f5d39e72875fcee6f76b39cce548` |
| BNB Smart Chain     | `binance_smart_chain-mainnet`   | `0x6f3239bbb26e98961e1115aba83f8a282e5508c8` |
| Celo                | `celo-mainnet`                  | `0x6E9EE680ef59ef64Aa8C7371279c27E496b5eDc1` |
| Ethereum Mainnet    | `ethereum-mainnet`              | `0xa3d1ad4ac559a6575a114998affb2fb2ec97a7d9` |
| Gnosis Chain        | `gnosis_chain-mainnet`          | `0x6E9EE680ef59ef64Aa8C7371279c27E496b5eDc1` |
| Hyperliquid Mainnet | `hyperliquid-mainnet`           | `0x6E9EE680ef59ef64Aa8C7371279c27E496b5eDc1` |
| Ink                 | `ethereum-mainnet-ink-1`        | `0x6E9EE680ef59ef64Aa8C7371279c27E496b5eDc1` |
| Jovay Mainnet       | `jovay-mainnet`                 | `0x2B3068C4B288A2CD1f8B3613b8f33ef7cEecadC4` |
| Linea               | `ethereum-mainnet-linea-1`      | `0x6E9EE680ef59ef64Aa8C7371279c27E496b5eDc1` |
| Mantle              | `ethereum-mainnet-mantle-1`     | `0x6E9EE680ef59ef64Aa8C7371279c27E496b5eDc1` |
| MegaETH             | `megaeth-mainnet`               | `0x6E9EE680ef59ef64Aa8C7371279c27E496b5eDc1` |
| Monad               | `monad-mainnet`                 | `0x9eF6468C5f37b976E57d52054c693269479A784d` |
| OP Mainnet          | `ethereum-mainnet-optimism-1`   | `0x9119a1501550ed94a3f2794038ed9258337afa18` |
| Pharos Mainnet      | `pharos-mainnet`                | `0x2B3068C4B288A2CD1f8B3613b8f33ef7cEecadC4` |
| Plasma              | `plasma-mainnet`                | `0x6E9EE680ef59ef64Aa8C7371279c27E496b5eDc1` |
| Polygon             | `polygon-mainnet`               | `0xf458d621885e29a5003ea9bbba5280d54e19b1ce` |
| Scroll              | `ethereum-mainnet-scroll-1`     | `0x6E9EE680ef59ef64Aa8C7371279c27E496b5eDc1` |
| Sonic               | `sonic-mainnet`                 | `0x6E9EE680ef59ef64Aa8C7371279c27E496b5eDc1` |
| World Chain         | `ethereum-mainnet-worldchain-1` | `0x6E9EE680ef59ef64Aa8C7371279c27E496b5eDc1` |
| XLayer Mainnet      | `ethereum-mainnet-xlayer-1`     | `0x2B3068C4B288A2CD1f8B3613b8f33ef7cEecadC4` |
| ZKSync Era          | `ethereum-mainnet-zksync-1`     | `0x6E9EE680ef59ef64Aa8C7371279c27E496b5eDc1` |

### Testnets

| Network                     | CRE Chain Selector Name                 | Mock Forwarder Address                       |
| --------------------------- | --------------------------------------- | -------------------------------------------- |
| ADI Testnet                 | `adi-testnet`                           | `0x9eF6468C5f37b976E57d52054c693269479A784d` |
| Apechain Curtis             | `apechain-testnet-curtis`               | `0x6E9EE680ef59ef64Aa8C7371279c27E496b5eDc1` |
| Arc Testnet                 | `arc-testnet`                           | `0x6E9EE680ef59ef64Aa8C7371279c27E496b5eDc1` |
| Arbitrum Sepolia            | `ethereum-testnet-sepolia-arbitrum-1`   | `0xd41263567ddfead91504199b8c6c87371e83ca5d` |
| Avalanche Fuji              | `avalanche-testnet-fuji`                | `0x2e7371a5d032489e4f60216d8d898a4c10805963` |
| Base Sepolia                | `ethereum-testnet-sepolia-base-1`       | `0x82300bd7c3958625581cc2f77bc6464dcecdf3e5` |
| BSC Testnet                 | `binance_smart_chain-testnet`           | `0xa238e42cb8782808dbb2f37e19859244ec4779b0` |
| Celo Sepolia                | `celo-sepolia`                          | `0x6E9EE680ef59ef64Aa8C7371279c27E496b5eDc1` |
| Cronos Testnet              | `cronos-testnet`                        | `0x6E9EE680ef59ef64Aa8C7371279c27E496b5eDc1` |
| Ethereum Hoodi Testnet      | `ethereum-hoodi-testnet`                | `0x9eF6468C5f37b976E57d52054c693269479A784d` |
| Ethereum Sepolia            | `ethereum-testnet-sepolia`              | `0x15fC6ae953E024d975e77382eEeC56A9101f9F88` |
| Gnosis Chiado               | `gnosis_chain-testnet-chiado`           | `0x6E9EE680ef59ef64Aa8C7371279c27E496b5eDc1` |
| Hyperliquid Testnet         | `hyperliquid-testnet`                   | `0xB27fA1c28288c50542527F64BCda22C9FbAc24CB` |
| Ink Sepolia                 | `ink-testnet-sepolia`                   | `0x6E9EE680ef59ef64Aa8C7371279c27E496b5eDc1` |
| Jovay Testnet               | `jovay-testnet`                         | `0x6E9EE680ef59ef64Aa8C7371279c27E496b5eDc1` |
| Linea Sepolia               | `ethereum-testnet-sepolia-linea-1`      | `0x6E9EE680ef59ef64Aa8C7371279c27E496b5eDc1` |
| Mantle Sepolia              | `ethereum-testnet-sepolia-mantle-1`     | `0x6E9EE680ef59ef64Aa8C7371279c27E496b5eDc1` |
| MegaETH Testnet 2           | `megaeth-testnet-2`                     | `0x6E9EE680ef59ef64Aa8C7371279c27E496b5eDc1` |
| Monad Testnet               | `monad-testnet`                         | `0xB9F79d863261869B234c481D1f9A7af84AeAd192` |
| OP Sepolia                  | `ethereum-testnet-sepolia-optimism-1`   | `0xa2888380dff3704a8ab6d1cd1a8f69c15fea5ee3` |
| Pharos Atlantic Testnet     | `pharos-atlantic-testnet`               | `0x6E9EE680ef59ef64Aa8C7371279c27E496b5eDc1` |
| Plasma Testnet              | `plasma-testnet`                        | `0x6E9EE680ef59ef64Aa8C7371279c27E496b5eDc1` |
| Polygon Amoy                | `polygon-testnet-amoy`                  | `0x3675a5eb2286a3f87e8278fc66edf458a2e3bb74` |
| Robinhood Testnet           | `robinhood-testnet`                     | `0x0b93082D9b3C7C97fAcd250082899BAcf3af3885` |
| Scroll Sepolia (deprecated) | `ethereum-testnet-sepolia-scroll-1`     | `0x6E9EE680ef59ef64Aa8C7371279c27E496b5eDc1` |
| Sonic Testnet               | `sonic-testnet`                         | `0x6E9EE680ef59ef64Aa8C7371279c27E496b5eDc1` |
| Stable Testnet              | `stable-testnet`                        | `0x9081624a30231767C3093A5F2Ae1C57A4457C88F` |
| TAC Testnet                 | `tac-testnet`                           | `0x6E9EE680ef59ef64Aa8C7371279c27E496b5eDc1` |
| T-REX Testnet (deprecated)  | `t-rex-testnet`                         | `0x53bC8B33F9Fd9cf5323b260CC078967cC3f30297` |
| Unichain Sepolia            | `ethereum-testnet-sepolia-unichain-1`   | `0x6E9EE680ef59ef64Aa8C7371279c27E496b5eDc1` |
| World Chain Sepolia         | `ethereum-testnet-sepolia-worldchain-1` | `0x6E9EE680ef59ef64Aa8C7371279c27E496b5eDc1` |
| XLayer Testnet              | `xlayer-testnet`                        | `0x6E9EE680ef59ef64Aa8C7371279c27E496b5eDc1` |
| ZKSync Era Sepolia          | `ethereum-testnet-sepolia-zksync-1`     | `0x6E9EE680ef59ef64Aa8C7371279c27E496b5eDc1` |

For a network that is not in these tables, fetch the official forwarder directory or run `cre workflow supported-chains` after `cre login`. Do not reuse another network's forwarder. `0x6E9EE680ef59ef64Aa8C7371279c27E496b5eDc1` is the mock forwarder on many networks and the wrong contract on others. Use `MockKeystoneForwarder` for `cre workflow simulate --broadcast`. Use `KeystoneForwarder` for a deployed consumer.

## Freshness Note

This data was sourced from the official forwarder directory at `https://docs.chain.link/cre/guides/workflow/using-evm-client/forwarder-directory-ts.md`. That page says it was last updated on 2026-09-18. Chain availability can also depend on the CRE tenant. If a row is missing or looks outdated, fetch that page.
