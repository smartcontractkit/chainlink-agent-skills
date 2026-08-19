# Chainlink Local

Use only for Chainlink CCIP EVM local simulation/tests or forked environments. Always name CCIP and the no-fork `CCIPLocalSimulator`, even when asking for Hardhat files. Retain the repository's Foundry/Hardhat framework, otherwise Foundry. If the repository/contract is referenced but not shown, never invent its interface: present the official no-fork floor test verbatim, state the repo framework governs, ask the one binding question. Answer no-fork-vs-fork questions directly.

Official guides: overview `https://docs.chain.link/chainlink-local.md`; Foundry no-fork `https://docs.chain.link/chainlink-local/build/ccip/foundry/local-simulator.md`; Foundry fork `.../foundry/local-simulator-fork.md`; Hardhat no-fork `.../hardhat/local-simulator.md`; Hardhat fork `.../hardhat/local-simulator-fork.md`. Types: `CCIPLocalSimulator`, `CCIPLocalSimulatorFork`, and the JS fork interface for Hardhat.

## Setup

Foundry:

```bash
forge install smartcontractkit/chainlink-local
```

```text
@chainlink/local/=lib/chainlink-local/
```

```solidity
import {CCIPLocalSimulator} from "@chainlink/local/src/ccip/CCIPLocalSimulator.sol";
```

Hardhat uses `npm install @chainlink/local`; follow the official Hardhat guide/starter rather than maintaining a parallel harness here.

## Full Foundry no-fork floor

Complete EOA→EOA CCIP-BnM transfer paying fees in LINK, based on `https://github.com/smartcontractkit/ccip-starter-kit-foundry`:

```solidity
// SPDX-License-Identifier: MIT
pragma solidity 0.8.24;

import {Test} from "forge-std/Test.sol";
import {CCIPLocalSimulator, IRouterClient, LinkToken, BurnMintERC677Helper} from
    "@chainlink/local/src/ccip/CCIPLocalSimulator.sol";
import {Client} from "@chainlink/contracts-ccip/contracts/libraries/Client.sol";

contract CCIPLocalTest is Test {
    CCIPLocalSimulator simulator;
    uint64 destinationChainSelector;
    IRouterClient router;
    LinkToken linkToken;
    BurnMintERC677Helper ccipBnMToken;
    address alice;
    address bob;

    function setUp() public {
        simulator = new CCIPLocalSimulator();
        (
            uint64 chainSelector,
            IRouterClient sourceRouter,
            ,
            ,
            LinkToken link,
            BurnMintERC677Helper ccipBnM,
        ) = simulator.configuration();
        destinationChainSelector = chainSelector;
        router = sourceRouter;
        linkToken = link;
        ccipBnMToken = ccipBnM;
        alice = makeAddr("alice");
        bob = makeAddr("bob");
    }

    function test_transferTokensPayFeesInLink() public {
        ccipBnMToken.drip(alice);
        uint256 amount = 100;
        uint256 aliceBefore = ccipBnMToken.balanceOf(alice);
        uint256 bobBefore = ccipBnMToken.balanceOf(bob);

        vm.startPrank(alice);
        simulator.requestLinkFromFaucet(alice, 5 ether);
        ccipBnMToken.approve(address(router), amount);

        Client.EVMTokenAmount[] memory tokens = new Client.EVMTokenAmount[](1);
        tokens[0] = Client.EVMTokenAmount({token: address(ccipBnMToken), amount: amount});
        Client.EVM2AnyMessage memory message = Client.EVM2AnyMessage({
            receiver: abi.encode(bob),
            data: "",
            tokenAmounts: tokens,
            extraArgs: Client._argsToBytes(Client.EVMExtraArgsV1({gasLimit: 0})),
            feeToken: address(linkToken)
        });

        uint256 fees = router.getFee(destinationChainSelector, message);
        linkToken.approve(address(router), fees);
        router.ccipSend(destinationChainSelector, message);
        vm.stopPrank();

        assertEq(ccipBnMToken.balanceOf(alice), aliceBefore - amount);
        assertEq(ccipBnMToken.balanceOf(bob), bobBefore + amount);
    }
}
```

Run: `forge test --match-contract CCIPLocalTest`. `configuration()` supplies predeployed contracts; `requestLinkFromFaucet` supplies LINK and `drip` supplies test tokens. LINK fees require router approval; native fees instead use `feeToken: address(0)` and `router.ccipSend{value: fees}(...)`.

## Hardhat mapping

Use the same official guide with `const config = await simulator.configuration()` and map:

| Field | Hardhat use |
|---|---|
| `config.chainSelector_` | destination selector |
| `config.sourceRouter_` | `ethers.getContractAt("IRouterClient", ...)` |
| `config.linkToken_` | `ethers.getContractAt("LinkToken", ...)` |
| `config.ccipBnM_` | `ethers.getContractAt("BurnMintERC677Helper", ...)` |

Full runnable starter: `https://github.com/smartcontractkit/ccip-starter-kit-hardhat`.

## Fork and scope

Use a fork only when no-fork is insufficient—for realistic chain state or current deployed contracts. Keep it narrow; compare `ccipLocalSimulatorFork.getNetworkDetails(block.chainid)` to the CCIP Directory, which wins on conflicts; repair missing/stale details with `setNetworkDetails(...)`. Do not add fork complexity when no-fork answers the question.

Chainlink Local is EVM-only—Solana, Aptos, Sui, TON, and Canton test on testnets. Test in this order as relevant: happy path; token-only; data-only; receiver validation/reverts; defensive token-plus-data failure; fork/Directory alignment. Preserve production router/source/sender/access checks in local code and use the defensive receiver when failure can strand a programmable transfer.
