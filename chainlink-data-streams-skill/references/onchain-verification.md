# Onchain Verification

Use this for EVM, Solana, or Stellar verification code/review and Chainlink Local simulation. The safety and non-custodial protocol live in [SKILL.md](../SKILL.md): code, review, local tests, and user-run artifacts are allowed; the agent refuses mainnet writes.

Always fetch current verifier deployments and requirements from the chain tutorial. Validate the matching schema, freshness/expiration, market status, ripcord, and application risk signals before consuming value.

## EVM

Sources:

- `https://docs.chain.link/data-streams/reference/data-streams-api/onchain-verification.md`
- `https://docs.chain.link/data-streams/tutorials/evm-onchain-report-verification.md`
- `https://docs.chain.link/data-streams/supported-networks.md`

Flow: obtain the current network verifier proxy; pass the full Streams Direct `full_report`; quote/handle fees; call `IVerifierProxy.verify`; decode the schema-specific response; enforce risk checks. Generated deployment code/preflights use a verifier-address constructor parameter/placeholder plus supported-networks URL; never copy table addresses.

### Canonical Solidity verification shape (v3)

For another schema, use its exact struct from [report-schemas.md](report-schemas.md).

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import {Common} from "@chainlink/contracts/src/v0.8/llo-feeds/libraries/Common.sol";
import {IERC20} from "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import {SafeERC20} from "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";

interface IVerifierProxy {
    function verify(bytes calldata payload, bytes calldata parameterPayload)
        external payable returns (bytes memory verifierResponse);
    function s_feeManager() external view returns (address);
}
interface IFeeManager {
    function getFeeAndReward(address subscriber, bytes memory unverifiedReport, address quoteAddress)
        external returns (Common.Asset memory fee, Common.Asset memory reward, uint256 discount);
    function i_linkAddress() external view returns (address);
    function i_rewardManager() external view returns (address);
}

contract DataStreamsVerifier {
    using SafeERC20 for IERC20;
    error Unauthorized();
    error InvalidAddress();
    error MalformedReport();
    error UnsupportedReportVersion(uint16 version);
    error UnexpectedFeed(bytes32 actualFeedId);
    error ReportNotYetValid(uint32 validFromTimestamp);
    error FutureReport(uint32 observationsTimestamp);
    error StaleReport(uint32 observationsTimestamp);
    error ExpiredReport(uint32 expiresAt);
    error Replay(uint32 observationsTimestamp, uint32 lastObservationsTimestamp);
    error InvalidPriceRange(int192 bid, int192 price, int192 ask);

    struct ReportV3 {
        bytes32 feedId;
        uint32 validFromTimestamp;
        uint32 observationsTimestamp;
        uint192 nativeFee;
        uint192 linkFee;
        uint32 expiresAt;
        int192 price;
        int192 bid;
        int192 ask;
    }

    IVerifierProxy public immutable verifierProxy;
    address public immutable authorizedUpdater;
    bytes32 public immutable expectedFeedId;
    uint32 public immutable maxReportAge;
    uint32 public lastObservationsTimestamp;
    int192 public lastPrice;

    constructor(address proxy, address updater, bytes32 feedId, uint32 reportMaxAge) {
        if (proxy == address(0) || proxy.code.length == 0 ||
            updater == address(0)) revert InvalidAddress();
        verifierProxy = IVerifierProxy(proxy);
        authorizedUpdater = updater;
        expectedFeedId = feedId;
        maxReportAge = reportMaxAge;
    }

    function verifyV3(bytes calldata fullReport) external returns (ReportV3 memory report) {
        if (msg.sender != authorizedUpdater) revert Unauthorized();
        (, bytes memory reportData) = abi.decode(fullReport, (bytes32[3], bytes));
        if (reportData.length < 2) revert MalformedReport();
        uint16 version = (uint16(uint8(reportData[0])) << 8) | uint16(uint8(reportData[1]));
        if (version != 3) revert UnsupportedReportVersion(version);

        bytes memory parameterPayload;
        address feeManagerAddress = verifierProxy.s_feeManager();
        if (feeManagerAddress != address(0)) {
            IFeeManager feeManager = IFeeManager(feeManagerAddress);
            address feeToken = feeManager.i_linkAddress();
            (Common.Asset memory fee,,) =
                feeManager.getFeeAndReward(address(this), reportData, feeToken);
            IERC20(feeToken).safeIncreaseAllowance(feeManager.i_rewardManager(), fee.amount);
            parameterPayload = abi.encode(feeToken);
        }

        bytes memory verified = verifierProxy.verify(fullReport, parameterPayload);
        report = abi.decode(verified, (ReportV3));

        uint256 timestamp = block.timestamp;
        if (report.feedId != expectedFeedId) revert UnexpectedFeed(report.feedId);
        if (report.validFromTimestamp > timestamp) {
            revert ReportNotYetValid(report.validFromTimestamp);
        }
        if (report.observationsTimestamp > timestamp) {
            revert FutureReport(report.observationsTimestamp);
        }
        if (uint256(report.observationsTimestamp) + maxReportAge < timestamp) {
            revert StaleReport(report.observationsTimestamp);
        }
        if (report.expiresAt < timestamp) revert ExpiredReport(report.expiresAt);
        if (report.observationsTimestamp <= lastObservationsTimestamp) {
            revert Replay(report.observationsTimestamp, lastObservationsTimestamp);
        }
        if (report.bid > report.price || report.price > report.ask) {
            revert InvalidPriceRange(report.bid, report.price, report.ask);
        }

        // Commit replay protection before any application-specific external interaction.
        lastObservationsTimestamp = report.observationsTimestamp;
        lastPrice = report.price;
    }
}
```

`fullReport` is the complete Streams Direct payload. A zero fee manager requires empty `parameterPayload`; otherwise quote/approve LINK as shown. Set `expectedFeedId` and `maxReportAge` from application policy at deployment. The canonical consumer rejects a report until `validFromTimestamp`, rejects future or over-age observations, treats `expiresAt < block.timestamp` as expired, and accepts observation timestamps only when they strictly increase. It commits `lastObservationsTimestamp` after every validation and before any application-specific external interaction; do not move that update later when extending the consumer. For another schema, retain the same feed, time, replay, and schema-specific risk checks. Storing is a write under [SKILL.md](../SKILL.md).

### Required compile and guard tests

For a complete latest-report dashboard/service that asks for verification status, emitting only an `unverified` label is incomplete: include the local canonical verifier and focused mock test. Missing live network or verifier values must remain explicit configuration/constructor placeholders and must not block writing or compiling those local files.

Write the canonical contract and focused test as the smallest complete runnable files in the generated project, then compile them against the project's installed Chainlink Contracts and OpenZeppelin versions; do not leave pseudocode imports, pasted-only excerpts, or undeclared test paths. Construct the contract with `(verifierProxy, authorizedUpdater, expectedFeedId, maxReportAge)`. Use a local verifier stub that returns ABI-encoded `ReportV3` values for guard tests, while keeping the Chainlink Local fee-path cases below.

Run one focused suite with the project's runner on a local, in-process network only: `forge build && forge test --match-contract DataStreamsVerifierTest` or `npx hardhat compile && npx hardhat test --network hardhat test/DataStreamsVerifier.test.ts`. The suite must prove:

- a fresh, currently valid report for `expectedFeedId` succeeds and advances both stored fields;
- an expired report and an observation older than `maxReportAge` revert; `expiresAt == block.timestamp` and `observationsTimestamp + maxReportAge == block.timestamp` remain valid, while each one-second-older case reverts;
- a future `validFromTimestamp`, a future `observationsTimestamp`, and a different `feedId` each revert;
- replaying the accepted report or submitting an older observation timestamp reverts, and rejected calls leave `lastObservationsTimestamp` and `lastPrice` unchanged;
- `bid <= price <= ask`, the v3 version check, and ABI decoding remain enforced; and
- both zero-fee-manager and LINK-fee paths still pass the exact payload and expected `parameterPayload` to `verify`.

## Chainlink Local Simulator

Sources: `https://github.com/smartcontractkit/chainlink-local`, `https://www.npmjs.com/package/@chainlink/local`, and current package source. Mocks are local simulation, not a production-security guarantee. Confirm the installed version before using:

- `@chainlink/local/src/data-streams/DataStreamsLocalSimulator.sol`
- `@chainlink/local/src/data-streams/MockReportGenerator.sol`
- `@chainlink/local/scripts/data-streams/MockReportGenerator`
- `DataStreamsLocalSimulator.configuration()` and `requestLinkFromFaucet(address,uint256)`
- `enableOffChainBilling()` and `enableOnChainBilling()`
- `MockReportGenerator.generateReportV2()`, `generateReportV3()`, `generateReportV4()`
- `updateFees(uint192,uint192)`, `updatePrice(int192)`, `updatePriceBidAndAsk(int192,int192,int192)`

### Runner-neutral smoke matrix

Foundry and Hardhat exercise the same sequence; use their native deployment/assert APIs rather than duplicating the test.

| Case | Arrange | Act | Assert |
|---|---|---|---|
| Onchain billing (default) | Deploy `DataStreamsLocalSimulator`; read `configuration()` for `MockVerifierProxy`; create `MockReportGenerator(1000e8)` and the consumer; `updateFees(1 ether, 0.5 ether)`; generate v3; `requestLinkFromFaucet(consumer, 1 ether)` | `consumer.verifyV3(signedReport)` | returned/stored price is `1000e8` |
| Offchain billing | Same setup; call `enableOffChainBilling()`; generate v3 | `consumer.verifyV3(signedReport)` | price is `1000e8`, exercising empty `parameterPayload` |

The current mock generator focuses on v2–v4; use official decoders for newer live schemas. Default simulation uses onchain fees. Hardhat needs compiled Chainlink Local artifacts; if `ethers.deployContract("DataStreamsLocalSimulator")` cannot find one, add a test-only Solidity import or follow current package setup. If an API is absent, name the unverified package file/URL rather than improvise.

## Solana

Sources:

- `https://docs.chain.link/data-streams/tutorials/solana-onchain-report-verification.md`
- `https://docs.chain.link/data-streams/tutorials/solana-offchain-report-verification.md`

Use CPI when a program must verify; use the offchain Rust SDK when client verification suffices. Source the verifier program ID, accounts, report crate, and schema module from current docs. Do not import EVM assumptions.

### Canonical Anchor CPI shape (v3)

Tutorial dependency shape:

```toml
[dependencies]
anchor-lang = "0.31.0"
chainlink_solana_data_streams = { git = "https://github.com/smartcontractkit/chainlink-data-streams-solana" }
chainlink-data-streams-report = "1.0.3"
```

```rust
use anchor_lang::prelude::*;
use anchor_lang::solana_program::{instruction::Instruction, program::{get_return_data, invoke}};
use chainlink_data_streams_report::report::v3::ReportDataV3;
use chainlink_solana_data_streams::VerifierInstructions;

declare_id!("<YOUR_PROGRAM_ID>");

#[program]
pub mod data_streams_consumer {
    use super::*;
    pub fn verify_v3(ctx: Context<VerifyReport>, signed_report: Vec<u8>) -> Result<()> {
        let verify_ix: Instruction = VerifierInstructions::verify(
            &ctx.accounts.verifier_program_id.key(),
            &ctx.accounts.verifier_account.key(),
            &ctx.accounts.access_controller.key(),
            &ctx.accounts.user.key(),
            &ctx.accounts.config_account.key(),
            signed_report,
        );
        invoke(&verify_ix, &[
            ctx.accounts.verifier_account.to_account_info(),
            ctx.accounts.access_controller.to_account_info(),
            ctx.accounts.user.to_account_info(),
            ctx.accounts.config_account.to_account_info(),
        ])?;
        let (_, bytes) = get_return_data().ok_or(DataStreamsError::NoReportData)?;
        let report = ReportDataV3::decode(&bytes)
            .map_err(|_| error!(DataStreamsError::InvalidReportData))?;
        require!(i64::from(report.expires_at) >= Clock::get()?.unix_timestamp,
            DataStreamsError::ExpiredReport);
        msg!("feed_id: {}", report.feed_id);
        msg!("observations_timestamp: {}", report.observations_timestamp);
        msg!("benchmark_price: {}", report.benchmark_price);
        msg!("bid: {}", report.bid);
        msg!("ask: {}", report.ask);
        Ok(())
    }
}

#[derive(Accounts)]
pub struct VerifyReport<'info> {
    /// CHECK: validated by the Chainlink verifier program.
    pub verifier_account: AccountInfo<'info>,
    /// CHECK: validated by the Chainlink verifier program.
    pub access_controller: AccountInfo<'info>,
    pub user: Signer<'info>,
    /// CHECK: PDA from the signed report, validated by the verifier program.
    pub config_account: UncheckedAccount<'info>,
    /// CHECK: current verifier program for the target cluster.
    pub verifier_program_id: AccountInfo<'info>,
}

#[error_code]
pub enum DataStreamsError {
    #[msg("No verified report data was returned")] NoReportData,
    #[msg("Verified bytes did not match the schema")] InvalidReportData,
    #[msg("The report is expired")] ExpiredReport,
}
```

`VerifierInstructions::verify` handles verifier PDA computation; do not hand-roll it while supported. The client supplies the signed payload and every current tutorial account. Rust uses snake_case (`benchmark_price`) where EVM may use `price`. For v8, for example, switch to `report::v8::ReportDataV8` and adjust fields/risk checks.

## Stellar

Use the canonical tutorial: `https://docs.chain.link/data-streams/tutorials/stellar-onchain-report-verification.md`. Generate Soroban/Rust from its current shape, fetch the current verifier contract, keep report parsing/verifier calls separate from business logic, and leave network/contract IDs as placeholders unless live docs were checked. Do not apply EVM or Solana APIs.

## Review Checklist

- Current verifier address/program/contract and accounts were checked.
- Exact full report bytes reach the verifier; the decoder matches its schema.
- Freshness/expiration and schema-specific risk signals are enforced.
- Writes are delivered only as user-run artifacts under [SKILL.md](../SKILL.md).
- No key, mnemonic, API secret, or credential is embedded.
