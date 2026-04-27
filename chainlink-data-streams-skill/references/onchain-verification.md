# Onchain Verification

Use this file when the user wants smart contracts or programs that verify Data Streams reports onchain, or when reviewing code that consumes verified reports.

## Safety Boundary

Code generation and review are allowed. Any deployment, transaction submission, verifier configuration, or other onchain write requires the skill's approval protocol and second confirmation rule. Mainnet writes are refused.

## Contents

- EVM
- Minimal Solidity Verification Pattern
- Chainlink Local Mock Testing
- Public Verifier Address Fallback
- Solana
- Minimal Solana Anchor CPI Pattern
- Stellar
- Review Checklist
- Refusal Template

## EVM

Official sources:

- `https://docs.chain.link/data-streams/reference/data-streams-api/onchain-verification`
- `https://docs.chain.link/data-streams/tutorials/evm-onchain-report-verification`
- `https://docs.chain.link/data-streams/supported-networks`
- `https://github.com/smartcontractkit/chainlink-local`
- `https://www.npmjs.com/package/@chainlink/local`

Expected pattern:

1. fetch current verifier proxy address for the target network from official docs
2. accept a `full_report` payload retrieved from Data Streams
3. estimate or handle verification fees using the documented verifier/fee manager flow
4. call the verifier proxy `verify` path documented by Chainlink
5. decode the returned verifier response for the target report schema
6. validate freshness, market status, ripcord, or other schema-specific risk signals before using the value
7. use Chainlink Local for local mock tests before moving verification code to a testnet

Generated Solidity should be minimal, explicit, and conservative. Do not bake in stale verifier addresses unless the user requested a specific network and live docs were checked.

For public verifier proxy/program IDs, read [public-endpoints-and-addresses.md](public-endpoints-and-addresses.md). Treat that table as an offline fallback, not as permission to skip live verification before deployment or transactions.

### Minimal Solidity Verification Pattern

Use this as a compact EVM shape for schema v3 examples. For other schemas, replace `ReportV3` with the exact struct from `references/report-schemas.md` or the current official docs.

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import {Common} from "@chainlink/contracts/src/v0.8/llo-feeds/libraries/Common.sol";
import {IERC20} from "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import {SafeERC20} from "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";

interface IVerifierProxy {
    function verify(
        bytes calldata payload,
        bytes calldata parameterPayload
    ) external payable returns (bytes memory verifierResponse);

    function s_feeManager() external view returns (address);
}

interface IFeeManager {
    function getFeeAndReward(
        address subscriber,
        bytes memory unverifiedReport,
        address quoteAddress
    ) external returns (Common.Asset memory fee, Common.Asset memory reward, uint256 discount);

    function i_linkAddress() external view returns (address);
    function i_rewardManager() external view returns (address);
}

contract DataStreamsVerifier {
    using SafeERC20 for IERC20;

    error UnsupportedReportVersion(uint16 version);
    error StaleReport(uint32 expiresAt);

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
    int192 public lastPrice;

    constructor(address verifierProxyAddress) {
        verifierProxy = IVerifierProxy(verifierProxyAddress);
    }

    function verifyV3(bytes calldata fullReport) external returns (ReportV3 memory report) {
        (, bytes memory reportData) = abi.decode(fullReport, (bytes32[3], bytes));
        uint16 reportVersion = _reportVersion(reportData);
        if (reportVersion != 3) revert UnsupportedReportVersion(reportVersion);

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

        bytes memory verifiedReport = verifierProxy.verify(fullReport, parameterPayload);
        report = abi.decode(verifiedReport, (ReportV3));
        if (report.expiresAt < block.timestamp) revert StaleReport(report.expiresAt);

        lastPrice = report.price;
    }

    function _reportVersion(bytes memory reportData) private pure returns (uint16) {
        return (uint16(uint8(reportData[0])) << 8) | uint16(uint8(reportData[1]));
    }
}
```

Notes:

- The `fullReport` input is the full payload returned by Streams Direct, not only the inner report data.
- `s_feeManager() == address(0)` means the contract should call `verify()` with an empty `parameterPayload`.
- If a fee manager exists, quote the fee, approve the reward manager, and pass `abi.encode(feeToken)`.
- Extend the version check and decoded struct only for schemas the contract explicitly supports.
- A function that stores decoded values is a state-changing transaction. Mainnet writes are refused by this skill, and testnet writes require the approval protocol and second confirmation rule.

### Chainlink Local Mock Testing

Use Chainlink Local when the user wants local tests for EVM Data Streams verification. Package-sourced Data Streams mocks are available in `@chainlink/local` and the `smartcontractkit/chainlink-local` repository even when the official Data Streams docs do not yet show these examples.

Known package APIs to verify before generating production-grade snippets:

- `@chainlink/local/src/data-streams/DataStreamsLocalSimulator.sol`
- `@chainlink/local/src/data-streams/MockReportGenerator.sol`
- `@chainlink/local/scripts/data-streams/MockReportGenerator`
- `DataStreamsLocalSimulator.configuration()`
- `DataStreamsLocalSimulator.requestLinkFromFaucet(address,uint256)`
- `DataStreamsLocalSimulator.enableOffChainBilling()`
- `DataStreamsLocalSimulator.enableOnChainBilling()`
- `MockReportGenerator.generateReportV2()`, `generateReportV3()`, and `generateReportV4()`
- `MockReportGenerator.updateFees(uint192,uint192)`, `updatePrice(int192)`, and `updatePriceBidAndAsk(int192,int192,int192)`

Foundry local-mode smoke test:

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import {Test} from "forge-std/Test.sol";
import {
    DataStreamsLocalSimulator,
    MockVerifierProxy
} from "@chainlink/local/src/data-streams/DataStreamsLocalSimulator.sol";
import {MockReportGenerator} from "@chainlink/local/src/data-streams/MockReportGenerator.sol";
import {DataStreamsVerifier} from "../src/DataStreamsVerifier.sol";

contract DataStreamsVerifierTest is Test {
    DataStreamsLocalSimulator internal simulator;
    MockReportGenerator internal reportGenerator;
    DataStreamsVerifier internal consumer;

    int192 internal initialPrice = 1000e8;

    function setUp() public {
        simulator = new DataStreamsLocalSimulator();
        (,,, MockVerifierProxy verifierProxy,,) = simulator.configuration();

        reportGenerator = new MockReportGenerator(initialPrice);
        consumer = new DataStreamsVerifier(address(verifierProxy));
    }

    function test_VerifiesReportV3WithOnChainBilling() public {
        reportGenerator.updateFees(1 ether, 0.5 ether);
        (bytes memory signedReport,) = reportGenerator.generateReportV3();

        simulator.requestLinkFromFaucet(address(consumer), 1 ether);

        DataStreamsVerifier.ReportV3 memory report = consumer.verifyV3(signedReport);

        assertEq(report.price, initialPrice);
        assertEq(consumer.lastPrice(), initialPrice);
    }

    function test_VerifiesReportV3WithOffChainBilling() public {
        simulator.enableOffChainBilling();
        (bytes memory signedReport,) = reportGenerator.generateReportV3();

        DataStreamsVerifier.ReportV3 memory report = consumer.verifyV3(signedReport);

        assertEq(report.price, initialPrice);
    }
}
```

Hardhat local-mode smoke test:

```typescript
import { loadFixture } from "@nomicfoundation/hardhat-toolbox/network-helpers";
import { expect } from "chai";
import { ethers } from "hardhat";
import { MockReportGenerator } from "@chainlink/local/scripts/data-streams/MockReportGenerator";

describe("DataStreamsVerifier", function () {
  async function deployFixture() {
    const simulator = await ethers.deployContract("DataStreamsLocalSimulator");
    const config = await simulator.configuration();

    const initialPrice = 1000n * 10n ** 8n;
    const reportGenerator = new MockReportGenerator(initialPrice);

    const consumer = await ethers.deployContract("DataStreamsVerifier", [
      config.mockVerifierProxy_,
    ]);

    return { simulator, consumer, reportGenerator, initialPrice };
  }

  it("verifies a v3 report with on-chain billing", async function () {
    const { simulator, consumer, reportGenerator, initialPrice } =
      await loadFixture(deployFixture);

    reportGenerator.updateFees(ethers.parseEther("1"), ethers.parseEther("0.5"));
    await simulator.requestLinkFromFaucet(consumer.target, ethers.parseEther("1"));

    const { signedReport } = await reportGenerator.generateReportV3();
    await consumer.verifyV3(signedReport);

    expect(await consumer.lastPrice()).to.equal(initialPrice);
  });

  it("verifies a v3 report with off-chain billing", async function () {
    const { simulator, consumer, reportGenerator, initialPrice } =
      await loadFixture(deployFixture);

    await simulator.enableOffChainBilling();

    const { signedReport } = await reportGenerator.generateReportV3();
    await consumer.verifyV3(signedReport);

    expect(await consumer.lastPrice()).to.equal(initialPrice);
  });
});
```

Local testing guidance:

- Use Chainlink Local mocks only for local simulation. Do not treat mock verifier behavior as a production security guarantee.
- The package mock report generator currently focuses on v2, v3, and v4 reports. Use official docs and SDK decoders for newer live schemas.
- The default simulator mode uses on-chain fee handling. `enableOffChainBilling()` removes the fee manager so consumer contracts can exercise the empty-parameter path.
- Hardhat projects need compiled artifacts for Chainlink Local contracts; if `ethers.deployContract("DataStreamsLocalSimulator")` cannot find one, add a small test-only Solidity import file or follow the package's current setup docs.
- If a Chainlink Local API is missing from the installed package, tell the user which package file or URL could not be verified before improvising.

## Solana

Official sources:

- `https://docs.chain.link/data-streams/tutorials/solana-onchain-report-verification`
- `https://docs.chain.link/data-streams/tutorials/solana-offchain-report-verification`

Expected pattern:

1. use the onchain integration when the Solana program itself must verify reports
2. use CPI to the Chainlink verifier program as described in the official tutorial
3. keep account lists and verifier program IDs sourced from current docs
4. use the offchain Rust SDK path when client-side verification is sufficient

### Minimal Solana Anchor CPI Pattern

Use this as a compact onchain Solana shape. Keep the exact verifier program ID, account addresses, report crate version, and schema module sourced from current docs before generating production code.

Relevant dependencies from the official tutorial shape:

```toml
[dependencies]
anchor-lang = "0.31.0"
chainlink_solana_data_streams = { git = "https://github.com/smartcontractkit/chainlink-data-streams-solana" }
chainlink-data-streams-report = "1.0.3"
```

Program snippet for a v3 report:

```rust
use anchor_lang::prelude::*;
use anchor_lang::solana_program::{
    instruction::Instruction,
    program::{get_return_data, invoke},
};
use chainlink_data_streams_report::report::v3::ReportDataV3;
use chainlink_solana_data_streams::VerifierInstructions;

declare_id!("<YOUR_PROGRAM_ID>");

#[program]
pub mod data_streams_consumer {
    use super::*;

    pub fn verify_v3(ctx: Context<VerifyReport>, signed_report: Vec<u8>) -> Result<()> {
        let verifier_program_id = ctx.accounts.verifier_program_id.key();
        let verifier_account = ctx.accounts.verifier_account.key();
        let access_controller = ctx.accounts.access_controller.key();
        let user = ctx.accounts.user.key();
        let config_account = ctx.accounts.config_account.key();

        let verify_ix: Instruction = VerifierInstructions::verify(
            &verifier_program_id,
            &verifier_account,
            &access_controller,
            &user,
            &config_account,
            signed_report,
        );

        invoke(
            &verify_ix,
            &[
                ctx.accounts.verifier_account.to_account_info(),
                ctx.accounts.access_controller.to_account_info(),
                ctx.accounts.user.to_account_info(),
                ctx.accounts.config_account.to_account_info(),
            ],
        )?;

        let (_, verified_bytes) = get_return_data().ok_or(DataStreamsError::NoReportData)?;
        let report = ReportDataV3::decode(&verified_bytes)
            .map_err(|_| error!(DataStreamsError::InvalidReportData))?;

        let now = Clock::get()?.unix_timestamp;
        require!(
            i64::from(report.expires_at) >= now,
            DataStreamsError::ExpiredReport
        );

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
    /// CHECK: PDA derived from the signed report and validated by the verifier program.
    pub config_account: UncheckedAccount<'info>,
    /// CHECK: current Chainlink Data Streams verifier program ID for the target cluster.
    pub verifier_program_id: AccountInfo<'info>,
}

#[error_code]
pub enum DataStreamsError {
    #[msg("No verified report data was returned by the verifier program")]
    NoReportData,
    #[msg("The verified report bytes did not match the expected report schema")]
    InvalidReportData,
    #[msg("The verified report is expired")]
    ExpiredReport,
}
```

Solana notes:

- The `VerifierInstructions::verify` helper handles verifier PDA computation; do not hand-roll PDA derivation unless the official SDK no longer supports the needed path.
- The client must pass the signed report payload and all accounts expected by the current verifier tutorial. Fetch current account requirements before generating a complete client.
- Rust crate fields are snake_case and can differ from Solidity struct field names. For example, the Solana v3 decoder currently exposes `benchmark_price`, while the EVM tutorial's v3 ABI example uses `price`.
- For v8 or other schemas, switch the import and decoder, for example `chainlink_data_streams_report::report::v8::ReportDataV8`, then adjust field access and risk checks.
- Deploying or invoking this program on devnet changes state and requires the skill approval protocol. Mainnet writes are refused.

Do not translate EVM verifier assumptions into Solana account or CPI code.

## Stellar

Official source:

- `https://docs.chain.link/data-streams/tutorials/stellar-onchain-report-verification`

Expected pattern:

1. generate Soroban/Rust code from the official Stellar tutorial shape
2. fetch current verifier contract details from docs
3. keep report parsing and verifier calls separate from business logic
4. surface any required network setup or contract IDs as placeholders unless live docs were checked

Do not apply EVM or Solana verifier APIs to Stellar.

## Review Checklist

When generating or reviewing verification code, check:

- current verifier address/program/contract source was consulted
- report bytes are passed exactly as required by the verifier
- decoded schema matches the feed/report version
- stale or expired reports are rejected
- application-specific risk fields are handled
- only testnet writes are considered, and only after two confirmations
- no private key, mnemonic, or API secret is embedded in source

## Refusal Template

For mainnet write requests:

```text
I cannot execute or help automate a mainnet state-changing action. I can generate or review the code, explain the verification flow, or help run read-only checks.
```
