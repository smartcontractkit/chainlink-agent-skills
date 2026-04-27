# Public Endpoints And Addresses

Use this file when the user needs public Chainlink Data Streams endpoint defaults or supported-network verifier proxy/program IDs.

These details are public developer integration data. Keep credentials secret and keep endpoint/address values configurable in generated projects.

## Freshness Boundary

Endpoint domains and verifier addresses are public, but they are still live deployment facts. Before production deployment, any transaction, or any user-facing claim that an address is current, fetch the official docs again:

- `https://docs.chain.link/data-streams/reference/data-streams-api/interface-api`
- `https://docs.chain.link/data-streams/reference/data-streams-api/interface-ws`
- `https://docs.chain.link/data-streams/supported-networks`
- `https://github.com/smartcontractkit/documentation/blob/main/src/features/feeds/data/StreamsNetworksData.ts`

If docs fetching fails, tell the user which URL could not be verified and say that this table is the offline fallback. This table was checked against the public Chainlink docs repository on 2026-04-27 at commit `d3e2464b68546a899c015c438241a788a17a79ea`.

Do not treat any mainnet address below as approval to deploy, configure, submit, or otherwise perform a mainnet write. Mainnet writes are refused by this skill.

## API Endpoint Defaults

| Surface | Testnet | Mainnet |
|---|---|---|
| REST API | `https://api.testnet-dataengine.chain.link` | `https://api.dataengine.chain.link` |
| WebSocket API | `wss://ws.testnet-dataengine.chain.link` | `wss://ws.dataengine.chain.link` |
| Candlestick API | `https://priceapi.testnet-dataengine.chain.link` | `https://priceapi.dataengine.chain.link` |

REST paths:

- latest report: `/api/v1/reports/latest?feedID=<feedID>`
- timestamp lookup: `/api/v1/reports?feedID=<feedID>&timestamp=<unixTimestamp>`
- bulk timestamp lookup: `/api/v1/reports/bulk?feedIDs=<feedID1>,<feedID2>&timestamp=<unixTimestamp>`
- paginated history: `/api/v1/reports/page?feedID=<feedID>&startTimestamp=<unixTimestamp>&limit=<limit>`

WebSocket path:

- stream reports: `/api/v1/ws?feedIDs=<feedID1>,<feedID2>`

Recommended environment variables:

```text
DATA_STREAMS_REST_URL=https://api.testnet-dataengine.chain.link
DATA_STREAMS_WS_URL=wss://ws.testnet-dataengine.chain.link
DATA_STREAMS_CANDLESTICK_URL=https://priceapi.testnet-dataengine.chain.link
```

Switch these to mainnet only when the user explicitly targets mainnet read paths. This does not change the skill's mainnet-write refusal.

## Verifier Proxy And Program Fallbacks

All Data Streams report types share the verifier address for a supported network unless the current docs say otherwise.

For Solana, the address column is the verifier program ID and the note includes the access controller. For Canton, Chainlink issues party-specific `VerifierConfig` contract IDs, so there is no reusable verifier proxy address.

| Network | Environment | Verifier proxy / program ID | Access controller / note |
|---|---|---|---|
| 0G | 0G Aristotle (Mainnet) | `0x673Dd1aA4Dafe735135d00058042D6ee3e85eF81` |  |
| 0G | 0G Galileo (Testnet) | `0x60fAa7faC949aF392DFc858F5d97E3EEfa07E9EB` |  |
| ADI Network | ADI Mainnet | `0x29b289DC5f840762FBF605FF4DF37df18FdA4e7a` |  |
| Apechain | Apechain Mainnet | `0x2e6621e5e3F916d5e512124dD79e06b55E258054` |  |
| Apechain | Apechain Curtis (Testnet) | `0x9D93c410AfDb41E8aEb1BA88B5Ff6DEAa09FF537` |  |
| Aptos | Aptos Mainnet | `0x5e6ee502816abcbe49b5bb670da4a1d5af520db11732e93f19ddd15b4608d01d` |  |
| Aptos | Aptos Testnet | `0x0c68769ae9efe2d02f10bc5baed793cfe0fe780c41e428d087d5d61286448090` |  |
| Arbitrum | Arbitrum Mainnet | `0x478Aa2aC9F6D65F84e09D9185d126c3a17c2a93C` |  |
| Arbitrum | Arbitrum Sepolia | `0x2ff010DEbC1297f19579B4246cad07bd24F2488A` |  |
| Arc | Arc Testnet | `0x72790f9eB82db492a7DDb6d2af22A270Dcc3Db64` |  |
| Avalanche | Avalanche Mainnet | `0x79BAa65505C6682F16F9b2C7F8afEBb1821BE3f6` |  |
| Avalanche | Avalanche Fuji Testnet | `0x2bf612C65f5a4d388E687948bb2CF842FFb8aBB3` |  |
| Base | Base Mainnet | `0xDE1A28D87Afd0f546505B28AB50410A5c3a7387a` |  |
| Base | Base Sepolia | `0x8Ac491b7c118a0cdcF048e0f707247fD8C9575f9` |  |
| Berachain | Berachain Mainnet | `0xC539169910DE08D237Df0d73BcDa9074c787A4a1` |  |
| Berachain | Berachain bArtio Testnet | `0x5A1634A86e9b7BfEf33F0f3f3EA3b1aBBc4CC85F` |  |
| Bitlayer | Bitlayer Mainnet | `0x6FDC15cad4f90a037B7126D7EFff105A9d03D6e7` |  |
| Bitlayer | Bitlayer Testnet | `0x57A97148C1fa50f35F0639f380077017D8893b6b` |  |
| Blast | Blast Mainnet | `0xaB93491064aEE774BE4b8a1cFFe4421F5B124F4e` |  |
| Blast | Blast Sepolia Testnet | `0x141f4278A5D71070Dc09CA276b72809b80F20eF0` |  |
| BNB Chain | BNB Chain Mainnet | `0xF276a4BC8Da323EA3E8c3c195a4E2E7615a898d1` |  |
| BNB Chain | BNB Chain Testnet | `0xF45D6dba93d0dB2C849C280F45e60D6e11b3C4DD` |  |
| Bob | Bob Mainnet | `0xF45D6dba93d0dB2C849C280F45e60D6e11b3C4DD` |  |
| Bob | Bob Sepolia Testnet | `0x60fAa7faC949aF392DFc858F5d97E3EEfa07E9EB` |  |
| Botanix | Botanix Mainnet | `0xC539169910DE08D237Df0d73BcDa9074c787A4a1` |  |
| Botanix | Botanix Testnet | `0xfBFff08fE4169853F7B1b5Ac67eC10dc8806801d` |  |
| Canton | Canton Network | `N/A` | Uses a party-specific VerifierConfig Contract ID issued by Chainlink. |
| Celo | Celo Mainnet | `0x57A97148C1fa50f35F0639f380077017D8893b6b` |  |
| Celo | Celo Testnet Alfajores | `0xfa58eE98c9d56A3e6e903f300BE8C60Bf031808D` |  |
| Ethereum | Ethereum Mainnet | `0x5A1634A86e9b7BfEf33F0f3f3EA3b1aBBc4CC85F` |  |
| Ethereum | Sepolia Testnet | `0x4e9935be37302B9C97Ff4ae6868F1b566ade26d2` |  |
| DogeOS | DogeOS Chikyu Testnet | `0x72790f9eB82db492a7DDb6d2af22A270Dcc3Db64` |  |
| Giwa | Giwa Sepolia | `0x72790f9eB82db492a7DDb6d2af22A270Dcc3Db64` |  |
| Gnosis | Gnosis Mainnet | `0x60fAa7faC949aF392DFc858F5d97E3EEfa07E9EB` |  |
| Gnosis | Gnosis Chiado | `0x60fAa7faC949aF392DFc858F5d97E3EEfa07E9EB` |  |
| Gravity | Gravity Alpha Mainnet | `0x60fAa7faC949aF392DFc858F5d97E3EEfa07E9EB` |  |
| Gravity | Gravity Alpha Testnet Sepolia | `0x60fAa7faC949aF392DFc858F5d97E3EEfa07E9EB` |  |
| HashKey Chain | HashKey Chain Mainnet | `0x3278e7a582B94d82487d4B99b31A511CbAe2Cd54` |  |
| HashKey Chain | HashKey Chain Testnet | `0xE02A72Be64DA496797821f1c4BB500851C286C6c` |  |
| Hedera | Hedera Mainnet | `0x38818Ba0e01E7743F5c001e8Aae095dE56a137db` |  |
| Hedera | Hedera Testnet | `0x57A97148C1fa50f35F0639f380077017D8893b6b` |  |
| HyperEVM | HyperEVM Mainnet | `0x60fAa7faC949aF392DFc858F5d97E3EEfa07E9EB` |  |
| HyperEVM | HyperEVM Testnet | `0x60fAa7faC949aF392DFc858F5d97E3EEfa07E9EB` |  |
| Ink | Ink Mainnet | `0x60fAa7faC949aF392DFc858F5d97E3EEfa07E9EB` |  |
| Ink | Ink Sepolia Testnet | `0x1f27392cC2394d54fFBA83B89C881200b5d5632C` |  |
| Injective | Injective EVM Mainnet | `0x60fAa7faC949aF392DFc858F5d97E3EEfa07E9EB` |  |
| Injective | Injective Testnet | `0x60fAa7faC949aF392DFc858F5d97E3EEfa07E9EB` |  |
| Jovay | Jovay Mainnet | `0xF1Ee15ecca3aD06edF9603a1ea6d19043804522A` |  |
| Jovay | Jovay Sepolia Testnet | `0x60fAa7faC949aF392DFc858F5d97E3EEfa07E9EB` |  |
| Katana | Katana Mainnet | `0x2a644E5AC685112A7Eff0c4d73CD0260546D366F` |  |
| Katana | Katana Testnet (Bokuto) | `0x72790f9eB82db492a7DDb6d2af22A270Dcc3Db64` |  |
| Lens | Lens Mainnet | `0xD9A79903359B4Dedf3a9c26AB47D4a8Fc62A70A2` |  |
| Lens | Lens Testnet | `0x5c0a4924535667ee025dDA78fCb0F213664927d5` |  |
| Linea | Linea Mainnet | `0x60fAa7faC949aF392DFc858F5d97E3EEfa07E9EB` |  |
| Linea | Linea Sepolia Testnet | `0x60fAa7faC949aF392DFc858F5d97E3EEfa07E9EB` |  |
| Mantle | Mantle Mainnet | `0x223752Eb475098e79d10937480DF93864D7EfB83` |  |
| Mantle | Mantle Sepolia Testnet | `0xdc458847982C496E1a5E25D005A332D5a838302B` |  |
| MegaETH | MegaETH Mainnet | `0x60fAa7faC949aF392DFc858F5d97E3EEfa07E9EB` |  |
| MegaETH | MegaETH Testnet | `0xa33c1F0561eECe58ee7b7349D5BE018dd94EC9B6` |  |
| Metis | Metis Andromeda Mainnet | `0xC539169910DE08D237Df0d73BcDa9074c787A4a1` |  |
| Metis | Metis Sepolia Testnet | `0xcFC9A8Efad365B04253575326f6A9bcDD8131Eb7` |  |
| Monad | Monad Mainnet | `0xEd813D895457907399E41D36Ec0bE103E32148c8` |  |
| Monad | Monad Testnet | `0xC539169910DE08D237Df0d73BcDa9074c787A4a1` |  |
| opBNB | opBNB Mainnet | `0x7D543D1a715ED544f7e3Ae9e3b1777BCdA56bF8e` |  |
| opBNB | opBNB Testnet | `0x001225Aca0efe49Dbb48233aB83a9b4d177b581A` |  |
| OP | OP Mainnet | `0xEBA4789A88C89C18f4657ffBF47B13A3abC7EB8D` |  |
| OP | OP Sepolia | `0x5f64394a2Ab3AcE9eCC071568Fc552489a8de7AF` |  |
| Perennial | Perennial Mainnet | `0xC539169910DE08D237Df0d73BcDa9074c787A4a1` |  |
| Perennial | Perennial Testnet | `0xF94Fc3DfD2875AECBEfDA8b7bFA05884fbF1E042` |  |
| Pharos | Pharos Mainnet (Private) | `0xa094978891512268f4a4a4641B8da1A2a3E3BEB7` |  |
| Pharos | Pharos Atlantic Testnet | `0x72790f9eb82db492a7ddb6d2af22a270dcc3db64` |  |
| Polygon | Polygon Mainnet | `0xF276a4BC8Da323EA3E8c3c195a4E2E7615a898d1` |  |
| Polygon | Polygon Amoy Testnet | `0x60fAa7faC949aF392DFc858F5d97E3EEfa07E9EB` |  |
| Plasma | Plasma Mainnet | `0xB4626C56c8d66b09adC57e38a5A15CcCd51BE082` |  |
| Plasma | Plasma Testnet | `0x60fAa7faC949aF392DFc858F5d97E3EEfa07E9EB` |  |
| Robinhood Chain | Robinhood Chain Testnet | `0x72790f9eB82db492a7DDb6d2af22A270Dcc3Db64` |  |
| Ronin | Ronin Mainnet | `0x499Ce6718a50e154B0C69905eEE8D307e5B003cc` |  |
| Ronin | Ronin Saigon Testnet | `0xE02A72Be64DA496797821f1c4BB500851C286C6c` |  |
| Scroll | Scroll Mainnet | `0x37e550C9b35DB56F9c943126F1c2642fcbDF7B51` |  |
| Scroll | Scroll Sepolia Testnet | `0xE17A7C6A7c2eF0Cb859578aa1605f8Bc2434A365` |  |
| Sei | Sei Mainnet | `0x60fAa7faC949aF392DFc858F5d97E3EEfa07E9EB` |  |
| Sei | Sei Testnet | `0x60fAa7faC949aF392DFc858F5d97E3EEfa07E9EB` |  |
| Seismic | Seismic Testnet | `0x72790f9eB82db492a7DDb6d2af22A270Dcc3Db64` |  |
| Shibarium | Shibarium Mainnet | `0xBE9f07f73de2412A9d0Ed64C42De7d9A10C9F28C` |  |
| Shibarium | Shibarium Puppynet | `0xc44eb6c00A0F89D044279cD91Bdfd5f62f752Da3` |  |
| Soneium | Soneium Mainnet | `0x8760535A80Ac5908096B57A094266866f4aA1A8c` |  |
| Soneium | Soneium Minato Testnet | `0x26603bAC5CE09DAE5604700B384658AcA13AD6ae` |  |
| Sonic | Sonic Mainnet | `0xfBFff08fE4169853F7B1b5Ac67eC10dc8806801d` |  |
| Sonic | Sonic Blaze Testnet | `0xfBFff08fE4169853F7B1b5Ac67eC10dc8806801d` |  |
| Solana | Solana Mainnet | `Gt9S41PtjR58CbG9JhJ3J6vxesqrNAswbWYbLNTMZA3c` | access controller: 7mSn5MoBjyRLKoJShgkep8J17ueGG8rYioVAiSg5YWMF |
| Solana | Solana Devnet | `Gt9S41PtjR58CbG9JhJ3J6vxesqrNAswbWYbLNTMZA3c` | access controller: 2k3DsgwBoqrnvXKVvd7jX7aptNxdcRBdcd5HkYsGgbrb |
| Stellar | Stellar Mainnet | `CAKA3NBYPC6OBEUEGNIYGNYG3ES2GPQK736B5SR7ASGUXRDAKXI2JCQI` |  |
| Stellar | Stellar Testnet | `CA7GVHWH4GRHE6GI7MHEKQZAOYO4GE7KRGSU3EOS3HYJRVLX3XEA4ONQ` |  |
| Stable | Stable Mainnet | `0x06034790F8b6c2573B91704BeC6Ab380cB590237` |  |
| Stable | Stable Testnet | `0x72790f9eB82db492a7DDb6d2af22A270Dcc3Db64` |  |
| X Layer | X Layer Mainnet | `0xcE73c8ad08CBDEaCa6078BF0627C8fe0a9a536E7` |  |
| X Layer | X Layer Testnet | `0x72790f9eB82db492a7DDb6d2af22A270Dcc3Db64` |  |
| Taiko | Taiko Alethia (Mainnet) | `0x60fAa7faC949aF392DFc858F5d97E3EEfa07E9EB` |  |
| Taiko | Taiko Hekla (Testnet) | `0xF45D6dba93d0dB2C849C280F45e60D6e11b3C4DD` |  |
| Unichain | Unichain Mainnet | `0x60fAa7faC949aF392DFc858F5d97E3EEfa07E9EB` |  |
| Unichain | Unichain Sepolia Testnet | `0x60fAa7faC949aF392DFc858F5d97E3EEfa07E9EB` |  |
| World Chain | World Chain Mainnet | `0x6733e9106094b0C794e8E0297c96611fF60460Bf` |  |
| World Chain | World Chain Sepolia Testnet | `0xd61ceB4521453F147C58d22879B4ec539331F851` |  |
| ZKSync | ZKSync Era Mainnet | `0xcA64d9D1a9AE4C10E94D0D45af9E878fc64dc207` |  |
| ZKSync | ZKSync Sepolia Testnet | `0xDf37875775d1E777bB413f27de093A62CFF4264b` |  |
