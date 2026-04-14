# Chainlink Local

Use this file only for CCIP local simulation, local contract tests, or forked-environment testing.

## Trigger Conditions

Use this workflow for requests like:

- "Add local CCIP tests for these contracts."
- "Simulate this CCIP flow locally before testnet."
- "Use Chainlink Local in this Foundry project."
- "This is a Hardhat repo. Add CCIP local simulator tests."
- "Run this in a forked environment first."

Do not use this workflow for live-network execution, message monitoring, or basic contract generation without a local-testing goal.

## Default Path

1. Prefer Chainlink Local for local simulation and local contract tests.
2. Prefer the no-fork local simulator first.
3. Use the current repo framework when it is already clearly Foundry or Hardhat.
4. If the repo is not already committed to a framework and the user does not ask for one, default to Foundry.
5. Use forked environments only when the user needs higher realism or specifically asks for a forked-network workflow.

## Official References

Start from these official docs:

- Overview: `https://docs.chain.link/chainlink-local`
- Foundry local simulator: `https://docs.chain.link/chainlink-local/build/ccip/foundry/local-simulator`
- Foundry forked environments: `https://docs.chain.link/chainlink-local/build/ccip/foundry/local-simulator-fork`
- Hardhat local simulator: `https://docs.chain.link/chainlink-local/build/ccip/hardhat/local-simulator`
- Hardhat forked environments: `https://docs.chain.link/chainlink-local/build/ccip/hardhat/local-simulator-fork`

Core simulator types:

- `CCIPLocalSimulator`
- `CCIPLocalSimulatorFork`
- `CCIPLocalSimulatorFork JS` - for Hardhat users who want a JavaScript interface to the forked simulator

## Setup Guidance

### Common package

Use the official local package:

- npm or yarn: `@chainlink/local`

### Foundry

Use the official Foundry install path:

```bash
forge install smartcontractkit/chainlink-local
```

Add the remapping:

```text
@chainlink/local/=lib/chainlink-local/
```

Import the simulator from the local package:

```solidity
import {CCIPLocalSimulator} from "@chainlink/local/src/ccip/CCIPLocalSimulator.sol";
```

### Hardhat

Use the existing Hardhat repo if the project is already Hardhat or the user explicitly wants Hardhat.

Install the package:

```bash
npm install @chainlink/local
```

Prefer the starter-kit structure from the official docs when the user wants the quickest working path.

## Foundry No-Fork Example

Complete test showing EOA-to-EOA token transfer with LINK fee payment. Based on the official [CCIP Foundry Starter Kit](https://github.com/smartcontractkit/ccip-starter-kit-foundry).

```solidity
// SPDX-License-Identifier: MIT
pragma solidity 0.8.24;

import {Test} from "forge-std/Test.sol";
import {CCIPLocalSimulator, IRouterClient, LinkToken, BurnMintERC677Helper} from
    "@chainlink/local/src/ccip/CCIPLocalSimulator.sol";
import {Client} from "@chainlink/contracts-ccip/contracts/libraries/Client.sol";

contract CCIPLocalTest is Test {
    CCIPLocalSimulator public ccipLocalSimulator;
    uint64 public destinationChainSelector;
    IRouterClient public router;
    LinkToken public linkToken;
    BurnMintERC677Helper public ccipBnMToken;

    address alice;
    address bob;

    function setUp() public {
        ccipLocalSimulator = new CCIPLocalSimulator();

        (
            uint64 chainSelector,
            IRouterClient sourceRouter,
            ,
            ,
            LinkToken link,
            BurnMintERC677Helper ccipBnM,
        ) = ccipLocalSimulator.configuration();

        destinationChainSelector = chainSelector;
        router = sourceRouter;
        linkToken = link;
        ccipBnMToken = ccipBnM;

        alice = makeAddr("alice");
        bob = makeAddr("bob");
    }

    function test_transferTokensPayFeesInLink() public {
        ccipBnMToken.drip(alice);
        uint256 amountToSend = 100;

        uint256 balanceOfAliceBefore = ccipBnMToken.balanceOf(alice);
        uint256 balanceOfBobBefore = ccipBnMToken.balanceOf(bob);

        vm.startPrank(alice);
        ccipLocalSimulator.requestLinkFromFaucet(alice, 5 ether);

        ccipBnMToken.approve(address(router), amountToSend);

        Client.EVMTokenAmount[] memory tokensToSend = new Client.EVMTokenAmount[](1);
        tokensToSend[0] = Client.EVMTokenAmount({token: address(ccipBnMToken), amount: amountToSend});

        Client.EVM2AnyMessage memory message = Client.EVM2AnyMessage({
            receiver: abi.encode(bob),
            data: "",
            tokenAmounts: tokensToSend,
            extraArgs: Client._argsToBytes(Client.EVMExtraArgsV1({gasLimit: 0})),
            feeToken: address(linkToken)
        });

        uint256 fees = router.getFee(destinationChainSelector, message);
        linkToken.approve(address(router), fees);
        router.ccipSend(destinationChainSelector, message);

        vm.stopPrank();

        assertEq(ccipBnMToken.balanceOf(alice), balanceOfAliceBefore - amountToSend);
        assertEq(ccipBnMToken.balanceOf(bob), balanceOfBobBefore + amountToSend);
    }

    function test_transferTokensPayFeesInNative() public {
        ccipBnMToken.drip(alice);
        uint256 amountToSend = 100;

        uint256 balanceOfAliceBefore = ccipBnMToken.balanceOf(alice);
        uint256 balanceOfBobBefore = ccipBnMToken.balanceOf(bob);

        vm.startPrank(alice);
        deal(alice, 5 ether);

        ccipBnMToken.approve(address(router), amountToSend);

        Client.EVMTokenAmount[] memory tokensToSend = new Client.EVMTokenAmount[](1);
        tokensToSend[0] = Client.EVMTokenAmount({token: address(ccipBnMToken), amount: amountToSend});

        Client.EVM2AnyMessage memory message = Client.EVM2AnyMessage({
            receiver: abi.encode(bob),
            data: "",
            tokenAmounts: tokensToSend,
            extraArgs: Client._argsToBytes(Client.EVMExtraArgsV1({gasLimit: 0})),
            feeToken: address(0)
        });

        uint256 fees = router.getFee(destinationChainSelector, message);
        router.ccipSend{value: fees}(destinationChainSelector, message);

        vm.stopPrank();

        assertEq(ccipBnMToken.balanceOf(alice), balanceOfAliceBefore - amountToSend);
        assertEq(ccipBnMToken.balanceOf(bob), balanceOfBobBefore + amountToSend);
    }
}
```

Run with:

```bash
forge test --match-contract CCIPLocalTest
```

Key patterns: `CCIPLocalSimulator` provides all pre-deployed addresses via `configuration()`. Use `requestLinkFromFaucet` for LINK, `drip` for test tokens. Fees paid via LINK require `approve` to router; native fees use `{value: fees}`.

## Hardhat No-Fork Example

Equivalent test in Hardhat using the `@chainlink/local` npm package:

```javascript
const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("CCIP Local Simulator", function () {
  let ccipSimulator, router, linkToken, ccipBnM;
  let chainSelector;
  let alice, bob;

  beforeEach(async function () {
    [alice, bob] = await ethers.getSigners();

    const CCIPLocalSimulator = await ethers.getContractFactory("CCIPLocalSimulator");
    ccipSimulator = await CCIPLocalSimulator.deploy();

    const config = await ccipSimulator.configuration();
    chainSelector = config.chainSelector_;
    router = await ethers.getContractAt("IRouterClient", config.sourceRouter_);
    linkToken = await ethers.getContractAt("LinkToken", config.linkToken_);
    ccipBnM = await ethers.getContractAt("BurnMintERC677Helper", config.ccipBnM_);
  });

  it("should transfer tokens paying fees in native", async function () {
    await ccipBnM.drip(alice.address);
    const amountToSend = 100;

    const balanceBefore = await ccipBnM.balanceOf(bob.address);

    await ccipBnM.connect(alice).approve(await router.getAddress(), amountToSend);

    const message = {
      receiver: ethers.AbiCoder.defaultAbiCoder().encode(["address"], [bob.address]),
      data: "0x",
      tokenAmounts: [{ token: await ccipBnM.getAddress(), amount: amountToSend }],
      extraArgs: "0x",
      feeToken: ethers.ZeroAddress,
    };

    const fees = await router.getFee(chainSelector, message);
    await router.connect(alice).ccipSend(chainSelector, message, { value: fees });

    const balanceAfter = await ccipBnM.balanceOf(bob.address);
    expect(balanceAfter - balanceBefore).to.equal(amountToSend);
  });
});
```

## Starter Kits

For the quickest working setup:

- Foundry: `https://github.com/smartcontractkit/ccip-starter-kit-foundry`
- Hardhat: `https://github.com/smartcontractkit/ccip-starter-kit-hardhat`

## Local Testing Workflow

### No-fork local simulator

This is the default path.

1. Start with the official local simulator guide for the current framework.
2. Use the simulator to obtain local router, LINK, token, and chain-selector configuration via `configuration()`.
3. Write or update tests for the specific CCIP path the user cares about.
4. Keep the first test small and reproducible.
5. Move to forked environments only after the no-fork path is working or when the user explicitly needs the fork.

### Forked environments

Use forked environments only when the user needs to test against realistic chain state or current deployed contracts.

1. Confirm that the user actually needs a fork.
2. Keep the fork scope narrow.
3. Use the official forked-environment guide for the current framework.
4. Compare config details from `ccipLocalSimulatorFork.getNetworkDetails(block.chainid);` against the CCIP Directory.
5. If the simulator details differ from the CCIP Directory, treat the CCIP Directory as the source of truth.
6. When fork-network details are missing or need correction, configure them explicitly with `setNetworkDetails(...)` using CCIP Directory values.
7. Do not introduce fork complexity when the no-fork simulator already answers the question.

## Scope

Chainlink Local is EVM-only. There is no local simulator for Solana, Aptos, Sui, or TON. For non-EVM CCIP testing, deploy directly to testnet.

## What To Test First

Prioritize:

1. sender and receiver happy path
2. token-only transfer path
3. data-only message path
4. receiver validation and revert behavior
5. defensive receiver behavior when token-plus-data flows can fail
6. forked-network detail alignment against the CCIP Directory when forks are used

## Security and Design Rules

1. Local simulation is not a reason to relax security defaults in generated contracts.
2. Preserve the same router, chain, sender, and access-control checks the contract should have outside local tests.
3. If the local test exposes a risky receiver pattern, suggest the defensive programmable-token-transfer example.
4. Keep test setup simple enough that a developer can rerun it quickly.
5. In fork tests, prefer verified CCIP Directory values over simulator defaults when they differ.

