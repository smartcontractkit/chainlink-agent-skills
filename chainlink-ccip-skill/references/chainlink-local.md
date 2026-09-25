# Chainlink Local

Use only for Chainlink CCIP EVM local simulation/tests or forked environments. Within an already-activated CCIP skill, a local simulator test request in an established Hardhat or Foundry repository is sufficient CCIP intent: do not ask which Chainlink product; activate Chainlink Local's no-fork CCIP simulator (`CCIPLocalSimulator`) and use that established framework. Otherwise, bare ambiguous Chainlink Local mentions remain subject to the main ownership gate. Always name CCIP and the no-fork `CCIPLocalSimulator`. Preserve the repository's established or explicitly requested framework exactly: Hardhat stays Hardhat and Foundry stays Foundry; otherwise default to Foundry. Hardhat 3 runs Solidity (`.t.sol`, forge-std) tests natively; that is the default for Hardhat 3 repositories, and JS/TS tests are only for repositories whose tests are already JS/TS or on explicit request. When the user requests coverage, tests, or files, output the actual runnable artifacts in that framework—not a plan, mapping, completion summary, or example from the other framework. For an existing or referenced repository/contract, inspect the actual source before writing its test; if the source is not accessible or pasted, ask for its contract path/source and test path instead of inventing contract names, constructors, methods, events, getters, or allowlist APIs. Answer no-fork-vs-fork questions directly.

Official guides: overview `https://docs.chain.link/chainlink-local.md`; Foundry no-fork `https://docs.chain.link/chainlink-local/build/ccip/foundry/local-simulator.md`; Foundry fork `.../foundry/local-simulator-fork.md`; Hardhat no-fork `.../hardhat/local-simulator.md`; Hardhat fork `.../hardhat/local-simulator-fork.md`. Types: `CCIPLocalSimulator`, `CCIPLocalSimulatorFork`, and the JS fork interface for Hardhat.

## Setup

Chainlink Local V3 (`v0.3.0` and above) targets `@chainlink/contracts-ccip` 2.0; 0.2.x targets 1.6.

Foundry:

```bash
forge install smartcontractkit/chainlink-local@v<version>
```

```text
@chainlink/local/=lib/chainlink-local/
@chainlink/contracts-ccip/=lib/chainlink-ccip/chains/evm/
@chainlink/contracts/=lib/chainlink-evm/contracts/
@openzeppelin/contracts@4.8.3/=lib/openzeppelin-contracts-4.8.3/contracts/
@openzeppelin/contracts@5.3.0/=lib/openzeppelin-contracts-5.3.0/contracts/
```

Use `solc >= 0.8.24` and `evm_version = "cancun"`: deployed CCIP 2.0 contracts use Cancun opcodes, and fork tests or scripts on `paris` fail with `EvmError: NotActivated`. Fork tests need Foundry >= 1.5.1.

```solidity
import {CCIPLocalSimulator} from "@chainlink/local/src/ccip/CCIPLocalSimulator.sol";
```

Hardhat 3 (Solidity tests, Node.js 22):

```bash
npm install --save-dev hardhat@^3 @chainlink/local@<version> "@openzeppelin/contracts-4.8.3@npm:@openzeppelin/contracts@4.8.3" "@openzeppelin/contracts-5.3.0@npm:@openzeppelin/contracts@5.3.0" "forge-std@github:foundry-rs/forge-std#v1.9.4"
```

`@chainlink/local` pulls in `@chainlink/contracts-ccip` and `@chainlink/contracts`. Root `remappings.txt`:

```text
@openzeppelin/contracts@4.8.3/=node_modules/@openzeppelin/contracts-4.8.3/
@openzeppelin/contracts@5.3.0/=node_modules/@openzeppelin/contracts-5.3.0/
forge-std/=node_modules/forge-std/src/
```

In `hardhat.config.ts` set `solidity: { version: "0.8.24", settings: { evmVersion: "cancun" } }`. Put `.t.sol` files in `test/` and run `npx hardhat test solidity`.

## Full Solidity no-fork floor (Foundry and Hardhat 3)

Complete EOA→EOA CCIP-BnM transfer paying fees in LINK for Foundry and Hardhat 3 requests or the no-framework default. It runs unchanged with `forge test` or `npx hardhat test solidity`. Return it for Hardhat 2 or JS/TS-only repositories only if they also want Solidity tests:

```solidity
// SPDX-License-Identifier: MIT
pragma solidity 0.8.24;

import {Test} from "forge-std/Test.sol";
import {CCIPLocalSimulator, IRouterClient, LinkToken, BurnMintERC677Helper} from
    "@chainlink/local/src/ccip/CCIPLocalSimulator.sol";
import {Client} from "@chainlink/contracts-ccip/contracts/libraries/Client.sol";
import {ExtraArgsCodec} from "@chainlink/contracts-ccip/contracts/libraries/ExtraArgsCodec.sol";
import {FinalityCodec} from "@chainlink/contracts-ccip/contracts/libraries/FinalityCodec.sol";

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
            extraArgs: ExtraArgsCodec._getBasicEncodedExtraArgsV3(0, FinalityCodec.WAIT_FOR_FINALITY_FLAG),
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

Run: `forge test --match-contract CCIPLocalTest` (Foundry) or `npx hardhat test solidity test/CCIPLocal.t.sol` (Hardhat 3). `configuration()` supplies predeployed contracts; `requestLinkFromFaucet` supplies LINK and `drip` supplies test tokens. LINK fees require router approval; native fees instead use `feeToken: address(0)` and `router.ccipSend{value: fees}(...)`.

The floor above sends straight through the router so it stays runnable with no other contracts. When the user has their own token-transfer sender contract, deploy and call through that contract instead of calling `router.ccipSend` directly from the test, so the test actually exercises the user's contract:

```solidity
sender = new TokenSender(address(sourceRouter), address(link)); // the user's actual sender contract
sender.allowlistDestinationChain(destinationChainSelector, true);
ccipBnMToken.drip(address(sender));
simulator.requestLinkFromFaucet(address(sender), 5 ether);

sender.transferTokens(destinationChainSelector, bob, address(ccipBnMToken), amount); // through the user's contract, not the router
```

Fast Transfers in local mode (V3 `CCIPLocalRouter`): delivery is synchronous, so block confirmations are not simulated, and pools and CCVs are not simulated. The requested finality is still checked against the receiver's `getCCVsAndFinalityConfig`. A rejected Fast Transfer reverts `FinalityCodec.InvalidRequestedFinality(requested, allowed)` directly from `ccipSend`, not wrapped in `ReceiverError`. Token-only transfers skip the check. Test the receiver's opt-in, floor, and non-allowlisted-sender cases; test pool finality floors on a fork or in pool unit tests ([CCT](ccip-cct.md#pool-tests)).

Fund and call the deployed sender/receiver contracts, never the router, whenever the request targets an existing or generated contract. A token-transfer test must send at least one nonzero token amount and assert token balances or the receiver's complete accounting; an empty `tokenAmounts` array tests data-only delivery and never satisfies it. Exercise receiver success and failure through `CCIPLocalSimulator` delivery. A receiver revert during simulator delivery exposes the outer `ReceiverError`, so assert that wrapper there; assert exact inner receiver errors separately with direct guard tests, using a minimal harness or authenticated-router context when the guard lies behind router authentication. Direct non-router calls must still prove router authentication; never impersonate the router merely to bypass it.

## Hardhat JS/TS mapping

Only for a repository whose tests are already JavaScript/TypeScript, or on explicit request: output an actual runnable test based on the official Hardhat guide/starter, never this mapping alone. V3 JS helpers need Hardhat 3, ESM, and `@nomicfoundation/hardhat-ethers`; Hardhat 2 JS/TS projects stay on Chainlink Local 0.2.x (CCIP 1.6). Use `const config = await simulator.configuration()` and map:

| Field | Hardhat use |
|---|---|
| `config.chainSelector_` | destination selector |
| `config.sourceRouter_` | `ethers.getContractAt("IRouterClient", ...)` |
| `config.linkToken_` | `ethers.getContractAt("LinkToken", ...)` |
| `config.ccipBnM_` | `ethers.getContractAt("BurnMintERC677Helper", ...)` |

Full runnable starter: `https://github.com/smartcontractkit/ccip-starter-kit-hardhat`.

## Fork and scope

Use a fork only when no-fork is insufficient—for realistic chain state or current deployed contracts. Keep it narrow; compare `ccipLocalSimulatorFork.getNetworkDetails(block.chainid)` to the CCIP Directory, which wins on conflicts; repair missing/stale details with `setNetworkDetails(...)`. Do not add fork complexity when no-fork answers the question.

Fork (V3 `CCIPLocalSimulatorFork`), with `evm_version = "cancun"`:

- `vm.makePersistent(address(simulator))` after deploying it; fork with RPC URLs from env placeholders, never hard-coded endpoints.
- A 2.0 lane can use a different router than `getNetworkDetails(...).routerAddress`: send through `getCCIPV2RouterAddress(block.chainid)`; if it returns `address(0)`, set the lane's router from the Directory/API with `setCCIPV2RouterAddress(chainId, router)`. Deploy receivers with the destination's 2.0 router.
- `switchChainAndRouteMessage(forkId)` runs the real OffRamp with simulated CCV attestations. Failures (receiver revert, finality or CCV rejection) are logged, not reverted, so assert destination state (for example the received message ID) rather than `expectRevert`.
- Pool finality floors are enforced on a fork; read the live pool's `getAllowedFinalityConfig()` instead of hard-coding it.
- Hardhat 3 JS: `getCCIPMessages(connection, receipt)` then `routeMessage(connection, routerAddresses, sent)`, which throws on failure; the caller supplies all addresses.

Chainlink Local is EVM-only—Solana, Aptos, Sui, TON, and Canton test on testnets. Test in this order as relevant: happy path; token-only; data-only; receiver validation/reverts; defensive token-plus-data failure; fork/Directory alignment. Preserve production router/source/sender/access checks in local code. Every generated Foundry token-plus-data deliverable must use the complete defensive receiver from [Solidity examples](ccip-solidity-examples.md), never a small, passive, happy-path-only, or abridged receiver: preserve router authentication, pair-bound source/sender and token authorization, try/catch, complete failed-message plus reason/state persistence and read access, owner-only recovery, unknown/resolved rejection, all-token recovery, and failure/recovery events.

Generated sender/receiver examples require focused rejection and recovery coverage: non-owner and disallowed-destination sender calls; insufficient and correctly paid LINK fees, including `forceApprove`, `ccipSend`, and events on success; non-router, disallowed-source, disallowed-sender, and malformed receiver messages. Isolate insufficient LINK by first funding the sender with the full transfer-token amount and satisfying its setup/approval prerequisites, then withholding only the LINK fee—a token-transfer failure is not evidence of the fee guard. In simulator rejection tests assert the observable outer `ReceiverError`, and assert exact inner receiver errors in separate direct guard or harness tests. Force processing failure; assert persisted failure reason/state and the complete message (ID, source selector, sender, data, and every destination token amount); then cover owner-only recovery, unknown/already-resolved rejection, exact all-token transfers, resolved state, and events. The deliverable is incomplete until the focused `forge test` suite passes; run it, fix the generated contracts or tests, and rerun before presenting them. Scripts/tests must default to no broadcast, reject mainnet writes, and require explicit testnet send mode or confirmation; keep any mainnet alternative read-only, such as a placeholder-only fee quote.
