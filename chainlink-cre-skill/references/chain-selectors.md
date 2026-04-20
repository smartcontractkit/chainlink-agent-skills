# Chain Selectors

Use this file when the user needs an EIP-155 chain ID to chain selector name mapping, forwarder addresses for a specific network, or the forwarder directory page cannot be fetched.

## Trigger Conditions

- "What chain selector name do I use for Arbitrum Sepolia?"
- "What's the chain ID for this CRE chain selector?"
- "What forwarder address do I use on Base Sepolia?"

Do not use for workflow code patterns (see workflow-patterns.md) or operational concerns (see operations.md).

## EIP-155 Chain ID to CRE Chain Selector Name Mapping

### Testnets

| Network | EIP-155 Chain ID | CRE Chain Selector Name |
|---------|-----------------|------------------------|
| Apechain Curtis | 33111 | `apechain-testnet-curtis` |
| Arc Testnet | 1883 | `arc-testnet` |
| Arbitrum Sepolia | 421614 | `ethereum-testnet-sepolia-arbitrum-1` |
| Avalanche Fuji | 43113 | `avalanche-testnet-fuji` |
| Base Sepolia | 84532 | `ethereum-testnet-sepolia-base-1` |
| BSC Testnet | 97 | `binance_smart_chain-testnet` |
| Cronos Testnet | 338 | `cronos-testnet` |
| Ethereum Sepolia | 11155111 | `ethereum-testnet-sepolia` |
| Gnosis Chiado | 10200 | `gnosis-chain-testnet-chiado` |
| Hyperliquid Testnet | 998 | `hyperliquid-testnet` |
| Ink Sepolia | 763373 | `ink-testnet-sepolia` |
| Linea Sepolia | 59141 | `ethereum-testnet-sepolia-linea-1` |
| Mantle Sepolia | 5003 | `ethereum-testnet-sepolia-mantle-1` |
| OP Sepolia | 11155420 | `ethereum-testnet-sepolia-optimism-1` |
| Polygon Amoy | 80002 | `polygon-testnet-amoy` |
| Scroll Sepolia | 534351 | `ethereum-testnet-sepolia-scroll-1` |
| Sonic Testnet | 64165 | `sonic-testnet` |
| Unichain Sepolia | 1301 | `ethereum-testnet-sepolia-unichain-1` |
| World Chain Sepolia | 4801 | `ethereum-testnet-sepolia-worldchain-1` |
| XLayer Testnet | 195 | `xlayer-testnet` |
| ZKSync Era Sepolia | 300 | `ethereum-testnet-sepolia-zksync-1` |

## Forwarder Addresses

### Production Forwarders (KeystoneForwarder)

Used by deployed workflows. Configure these in consumer contract constructors for production.

| Network | CRE Chain Selector Name | Forwarder Address |
|---------|------------------------|-------------------|
| Apechain Curtis | `apechain-testnet-curtis` | `0x76c9cf548b4179F8901cda1f8623568b58215E62` |
| Arbitrum Sepolia | `ethereum-testnet-sepolia-arbitrum-1` | `0x76c9cf548b4179F8901cda1f8623568b58215E62` |
| Avalanche Fuji | `avalanche-testnet-fuji` | `0x76c9cf548b4179F8901cda1f8623568b58215E62` |
| Base Sepolia | `ethereum-testnet-sepolia-base-1` | `0xF8344CFd5c43616a4366C34E3EEE75af79a74482` |
| BSC Testnet | `binance_smart_chain-testnet` | `0x76c9cf548b4179F8901cda1f8623568b58215E62` |
| Cronos Testnet | `cronos-testnet` | `0x9eF6468C5f37b976E57d52054c693269479A784d` |
| Ethereum Sepolia | `ethereum-testnet-sepolia` | `0xF8344CFd5c43616a4366C34E3EEE75af79a74482` |
| Gnosis Chiado | `gnosis-chain-testnet-chiado` | `0x0b93082D9b3C7C97fAcd250082899BAcf3af3885` |
| Hyperliquid Testnet | `hyperliquid-testnet` | `0x76c9cf548b4179F8901cda1f8623568b58215E62` |
| Ink Sepolia | `ink-testnet-sepolia` | `0x76c9cf548b4179F8901cda1f8623568b58215E62` |
| Linea Sepolia | `ethereum-testnet-sepolia-linea-1` | `0x76c9cf548b4179F8901cda1f8623568b58215E62` |
| Mantle Sepolia | `ethereum-testnet-sepolia-mantle-1` | `0xB9F79d863261869B234c481D1f9A7af84AeAd192` |
| OP Sepolia | `ethereum-testnet-sepolia-optimism-1` | `0x76c9cf548b4179F8901cda1f8623568b58215E62` |
| Polygon Amoy | `polygon-testnet-amoy` | `0x76c9cf548b4179F8901cda1f8623568b58215E62` |
| Scroll Sepolia | `ethereum-testnet-sepolia-scroll-1` | `0x98B8335d29Aca40840Ed8426dA1A0aAa8677d8D1` |
| Sonic Testnet | `sonic-testnet` | `0x98B8335d29Aca40840Ed8426dA1A0aAa8677d8D1` |
| Unichain Sepolia | `ethereum-testnet-sepolia-unichain-1` | `0x98B8335d29Aca40840Ed8426dA1A0aAa8677d8D1` |
| World Chain Sepolia | `ethereum-testnet-sepolia-worldchain-1` | `0x76c9cf548b4179F8901cda1f8623568b58215E62` |
| XLayer Testnet | `xlayer-testnet` | `0x9eF6468C5f37b976E57d52054c693269479A784d` |
| ZKSync Era Sepolia | `ethereum-testnet-sepolia-zksync-1` | `0x76c9cf548b4179F8901cda1f8623568b58215E62` |

### Simulation Forwarders (MockKeystoneForwarder)

Used with `cre workflow simulate --broadcast`. Use these only during local development and testing.

| Network | CRE Chain Selector Name | Mock Forwarder Address |
|---------|------------------------|----------------------|
| Arbitrum Sepolia | `ethereum-testnet-sepolia-arbitrum-1` | `0xd41263567ddfead91504199b8c6c87371e83ca5d` |
| Avalanche Fuji | `avalanche-testnet-fuji` | `0x2e7371a5d032489e4f60216d8d898a4c10805963` |
| Base Sepolia | `ethereum-testnet-sepolia-base-1` | `0x82300bd7c3958625581cc2f77bc6464dcecdf3e5` |
| BSC Testnet | `binance_smart_chain-testnet` | `0xa238e42cb8782808dbb2f37e19859244ec4779b0` |
| Ethereum Sepolia | `ethereum-testnet-sepolia` | `0x15fC6ae953E024d975e77382eEeC56A9101f9F88` |
| OP Sepolia | `ethereum-testnet-sepolia-optimism-1` | `0xa2888380dff3704a8ab6d1cd1a8f69c15fea5ee3` |
| Polygon Amoy | `polygon-testnet-amoy` | `0x3675a5eb2286a3f87e8278fc66edf458a2e3bb74` |

For networks not listed above, the common mock forwarder address is `0x6E9EE680ef59ef64Aa8C7371279c27E496b5eDc1`.

## Freshness Note

This data was sourced from the official forwarder directory at `https://docs.chain.link/cre/guides/workflow/using-evm-client/forwarder-directory-ts`. If addresses seem outdated, fetch that page for the latest values.
