# Chainlink Local

Use only for Chainlink CCIP EVM local simulation/tests or forked environments. Within an already-activated CCIP skill, a local simulator test request in an established Hardhat or Foundry repository is sufficient CCIP intent: do not ask which Chainlink product; activate Chainlink Local's no-fork CCIP simulator (`CCIPLocalSimulator`) and use that established framework. Otherwise, bare ambiguous Chainlink Local mentions remain subject to the main ownership gate. Always name CCIP and the no-fork `CCIPLocalSimulator`. Preserve the repository's established or explicitly requested framework exactly: Hardhat stays Hardhat and Foundry stays Foundry; otherwise default to Foundry. When the user requests coverage, tests, or files, output the actual runnable artifacts in that framework—not a plan, mapping, completion summary, or example from the other framework. For an existing or referenced repository/contract, inspect the actual source before writing its test; if the source is not accessible or pasted, ask for its contract path/source and test path instead of inventing contract names, constructors, methods, events, getters, or allowlist APIs. Answer no-fork-vs-fork questions directly.

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

Complete EOA→EOA CCIP-BnM transfer paying fees in LINK for Foundry requests or the no-framework default, based on `https://github.com/smartcontractkit/ccip-starter-kit-foundry`. Never return this Solidity/Foundry floor for a Hardhat request:

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

The floor above sends straight through the router so it stays runnable with no other contracts. When the user has their own token-transfer sender contract, deploy and call through that contract instead of calling `router.ccipSend` directly from the test, so the test actually exercises the user's contract:

```solidity
sender = new TokenSender(address(sourceRouter), address(link)); // the user's actual sender contract
sender.allowlistDestinationChain(destinationChainSelector, true);
ccipBnMToken.drip(address(sender));
simulator.requestLinkFromFaucet(address(sender), 5 ether);

sender.transferTokens(destinationChainSelector, bob, address(ccipBnMToken), amount); // through the user's contract, not the router
```

Fund and call the deployed sender/receiver contracts, never the router, whenever the request targets an existing or generated contract. A token-transfer test must send at least one nonzero token amount and assert token balances or the receiver's complete accounting; an empty `tokenAmounts` array tests data-only delivery and never satisfies it. Exercise receiver success and failure through `CCIPLocalSimulator` delivery—never impersonate the router or call `ccipReceive` directly.

## Hardhat mapping

For a Hardhat request, output an actual runnable JavaScript or TypeScript test based on the official Hardhat guide/starter; never return the Foundry example above or this mapping alone. Use `const config = await simulator.configuration()` and map:

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
