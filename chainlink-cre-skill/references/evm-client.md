# EVM Client

Use this file when the user wants onchain reads, onchain writes, contract bindings, consumer contracts, forwarder addresses, or report generation.

## Trigger Conditions

- "How do I read from a smart contract?"
- "How do I write data onchain?"
- "How do I generate contract bindings?"
- "How do I set up a consumer contract?"
- "What is the KeystoneForwarder?"

Do not use for HTTP requests (see http-client.md), trigger configuration (see triggers.md), or general workflow patterns (see workflow-patterns.md).

## Onchain Reads

### TypeScript

```typescript
import {
  EVMClient,
  CronCapability,
  encodeCallMsg,
  getNetwork,
  bytesToHex,
  LAST_FINALIZED_BLOCK_NUMBER,
  handler,
  Runner,
  type Runtime,
} from "@chainlink/cre-sdk"
import {
  type Address,
  parseAbi,
  encodeFunctionData,
  decodeFunctionResult,
  zeroAddress,
} from "viem"

type Config = {
  schedule: string
  contractAddress: string
  chainSelectorName: string
}

const abi = parseAbi([
  "function latestRoundData() external view returns (uint80 roundId, int256 answer, uint256 startedAt, uint256 updatedAt, uint80 answeredInRound)",
])

const onCronTrigger = (runtime: Runtime<Config>): string => {
  // The chain selector goes in the constructor, so you need one client per chain.
  const network = getNetwork({
    chainFamily: "evm",
    chainSelectorName: runtime.config.chainSelectorName,
  })
  if (!network) {
    throw new Error(`Unknown chain selector name: ${runtime.config.chainSelectorName}`)
  }

  const evmClient = new EVMClient(network.chainSelector.selector)

  const callData = encodeFunctionData({
    abi,
    functionName: "latestRoundData",
  })

  const result = evmClient
    .callContract(runtime, {
      call: encodeCallMsg({
        from: zeroAddress,
        to: runtime.config.contractAddress as Address,
        data: callData,
      }),
      blockNumber: LAST_FINALIZED_BLOCK_NUMBER,
    })
    .result()

  const decoded = decodeFunctionResult({
    abi,
    functionName: "latestRoundData",
    data: bytesToHex(result.data),
  })

  const [roundId, answer, startedAt, updatedAt, answeredInRound] = decoded
  runtime.log(`Price: ${answer.toString()}`)

  return answer.toString()
}

const initWorkflow = (config: Config) => {
  const cron = new CronCapability()
  return [handler(cron.trigger({ schedule: config.schedule }), onCronTrigger)]
}

export async function main() {
  const runner = await Runner.newRunner<Config>()
  await runner.run(initWorkflow)
}
```

### Go (with Generated Bindings)

```go
package main

import (
    "fmt"
    "log/slog"
    "math/big"

    "my-project/contracts/evm/src/generated/storage"

    "github.com/ethereum/go-ethereum/common"
    "github.com/smartcontractkit/cre-sdk-go/capabilities/blockchain/evm"
    "github.com/smartcontractkit/cre-sdk-go/capabilities/scheduler/cron"
    "github.com/smartcontractkit/cre-sdk-go/cre"
    "github.com/smartcontractkit/cre-sdk-go/cre/wasm"
)

type Config struct {
    Schedule        string `json:"schedule"`
    ContractAddress string `json:"contractAddress"`
    ChainSelector   uint64 `json:"chainSelector"`
}

type Result struct {
    Value string `json:"value"`
}

func onCronTrigger(config *Config, runtime cre.Runtime, trigger *cron.Payload) (*Result, error) {
    evmClient := &evm.Client{ChainSelector: config.ChainSelector}
    contractAddress := common.HexToAddress(config.ContractAddress)

    binding, err := storage.NewStorage(evmClient, contractAddress, nil)
    if err != nil {
        return nil, fmt.Errorf("create Storage binding: %w", err)
    }

    value, err := binding.Get(runtime, big.NewInt(-3)).Await()
    if err != nil {
        return nil, fmt.Errorf("read storage value: %w", err)
    }

    return &Result{Value: value.String()}, nil
}

func InitWorkflow(config *Config, logger *slog.Logger, secretsProvider cre.SecretsProvider) (cre.Workflow[*Config], error) {
    return cre.Workflow[*Config]{
        cre.Handler(
            cron.Trigger(&cron.Config{Schedule: config.Schedule}),
            onCronTrigger,
        ),
    }, nil
}

func main() {
    wasm.NewRunner(cre.ParseJSON[Config]).Run(InitWorkflow)
}
```

### Block Number Options

#### TypeScript

| Value | Description |
|-------|-------------|
| `0n` | Last finalized block (default, recommended) |
| `-1n` | Latest known block (not finalized) |
| `-2n` | Safe block |
| `-3n` | Pending block |
| Positive value | Specific block number |

#### Go

**Generated bindings (`binding.Method(runtime, ..., blockNumber)`)**

| Value | Description |
|-------|-------------|
| `big.NewInt(-3)` | Finalized block (recommended for production) |
| `big.NewInt(-2)` | Latest known block |
| `nil` | Finalized block (default) |
| Positive value | Specific block number |

Generated read methods substitute `bindings.FinalizedBlockNumber` when `blockNumber` is `nil`.

**Low-level `evm.Client` calls (`CallContract`, `BalanceAt`, `HeaderByNumber` — `BlockNumber *pb.BigInt`)**

| Value | Description |
|-------|-------------|
| `nil` or `-2` | Latest known block (default) |
| `-3` | Finalized block |
| Positive value | Specific block number |

### ABI Encoding/Decoding (TypeScript)

Use `viem` for all ABI encoding/decoding:

```typescript
import { parseAbi, encodeFunctionData, decodeFunctionResult } from "viem"

const abi = parseAbi(["function balanceOf(address owner) view returns (uint256)"])

const callData = encodeFunctionData({
  abi,
  functionName: "balanceOf",
  args: ["0x1234..."],
})

const decoded = decodeFunctionResult({
  abi,
  functionName: "balanceOf",
  data: result.data as `0x${string}`,
})
```

Use `bigint` (not `number`) for all Solidity integer types to avoid precision loss.

## Onchain Writes

### Writing Data Workflow

1. **ABI-encode** the data you want to write
2. **Generate a signed report** using `runtime.report()` in TypeScript (`runtime.GenerateReport()` in Go)
3. **Submit the report** using `evmClient.writeReport()` in TypeScript (a generated `WriteReportFrom<StructName>` helper or `evmClient.WriteReport()` in Go)

### TypeScript: Encoding Single Values

```typescript
import { encodeAbiParameters, parseAbiParameters } from "viem"

const encoded = encodeAbiParameters(
  parseAbiParameters("uint256 price"),
  [42000000000n]
)
```

### TypeScript: Encoding Structs

Report timestamps must derive from DON Time (`runtime.now()`), never the local JavaScript clock (`Date.now()`/`new Date()`), which is non-deterministic across DON nodes. See [workflow-patterns.md](workflow-patterns.md) for the DON Time source of truth.

```typescript
import {
  CronCapability,
  handler,
  type Runtime,
} from "@chainlink/cre-sdk"
import { encodeAbiParameters, parseAbiParameters } from "viem"

type Config = {
  schedule: string
}

const onCronTrigger = (runtime: Runtime<Config>): string => {
  const price = 42000000000n
  // DON Time is consensus-derived; convert ms -> seconds, then to bigint for ABI encoding
  const timestamp = BigInt(Math.floor(runtime.now().getTime() / 1000))

  const encoded = encodeAbiParameters(
    parseAbiParameters("(uint256 price, uint256 timestamp)"),
    [{ price, timestamp }]
  )
  return encoded
}

const initWorkflow = (config: Config) => {
  const cron = new CronCapability()
  return [handler(cron.trigger({ schedule: config.schedule }), onCronTrigger)]
}
```

### TypeScript: Encoding Arrays

```typescript
const encoded = encodeAbiParameters(
  parseAbiParameters("uint256[]"),
  [[1n, 2n, 3n]]
)
```

### TypeScript: Full Write Flow

```typescript
import {
  EVMClient,
  CronCapability,
  getNetwork,
  prepareReportRequest,
  bytesToHex,
  TxStatus,
  handler,
  Runner,
  type Runtime,
} from "@chainlink/cre-sdk"
import { encodeAbiParameters, parseAbiParameters } from "viem"

type Config = {
  schedule: string
  consumerAddress: string
  chainSelectorName: string
}

const onCronTrigger = (runtime: Runtime<Config>): string => {
  const network = getNetwork({
    chainFamily: "evm",
    chainSelectorName: runtime.config.chainSelectorName,
  })
  if (!network) {
    throw new Error(`Unknown chain selector name: ${runtime.config.chainSelectorName}`)
  }

  const evmClient = new EVMClient(network.chainSelector.selector)

  const encoded = encodeAbiParameters(
    parseAbiParameters("uint256 price"),
    [42000000000n]
  )

  // runtime.report returns a lazy handle; resolve it with .result()
  const signedReport = runtime.report(prepareReportRequest(encoded)).result()

  const txResult = evmClient
    .writeReport(runtime, {
      receiver: runtime.config.consumerAddress,
      report: signedReport,
      gasConfig: { gasLimit: "500000" },
    })
    .result()

  if (txResult.txStatus !== TxStatus.SUCCESS) {
    throw new Error(`Write failed: ${txResult.errorMessage || txResult.txStatus}`)
  }

  const txHash = bytesToHex(txResult.txHash ?? new Uint8Array(32))
  runtime.log(`TX hash: ${txHash}`)

  return txHash
}

const initWorkflow = (config: Config) => {
  const cron = new CronCapability()
  return [handler(cron.trigger({ schedule: config.schedule }), onCronTrigger)]
}

export async function main() {
  const runner = await Runner.newRunner<Config>()
  await runner.run(initWorkflow)
}
```

### Go: Full Write Flow

```go
package main

import (
    "fmt"
    "log/slog"
    "math/big"

    calculator_consumer "my-project/contracts/evm/src/generated/calculator_consumer"

    "github.com/ethereum/go-ethereum/accounts/abi"
    "github.com/ethereum/go-ethereum/common"
    "github.com/smartcontractkit/cre-sdk-go/capabilities/blockchain/evm"
    "github.com/smartcontractkit/cre-sdk-go/capabilities/scheduler/cron"
    "github.com/smartcontractkit/cre-sdk-go/cre"
    "github.com/smartcontractkit/cre-sdk-go/cre/wasm"
)

type Config struct {
    Schedule        string `json:"schedule"`
    ConsumerAddress string `json:"consumerAddress"`
    ChainSelector   uint64 `json:"chainSelector"`
    GasLimit        uint64 `json:"gasLimit"`
}

func onCronTrigger(config *Config, runtime cre.Runtime, trigger *cron.Payload) (*string, error) {
    evmClient := &evm.Client{ChainSelector: config.ChainSelector}
    consumerAddress := common.HexToAddress(config.ConsumerAddress)

    consumerContract, err := calculator_consumer.NewCalculatorConsumer(evmClient, consumerAddress, nil)
    if err != nil {
        return nil, fmt.Errorf("create CalculatorConsumer binding: %w", err)
    }

    gasConfig := &evm.GasConfig{GasLimit: config.GasLimit}
    writePromise := consumerContract.WriteReportFromCalculatorResult(runtime, calculator_consumer.CalculatorResult{
        OffchainValue: big.NewInt(20000000000),
        OnchainValue:  big.NewInt(22000000000),
        FinalResult:   big.NewInt(42000000000),
    }, gasConfig)

    resp, err := writePromise.Await()
    if err != nil {
        return nil, fmt.Errorf("write generated report: %w", err)
    }

    txHash := common.BytesToHash(resp.TxHash).Hex()
    return &txHash, nil
}

func writeReportExplicit(runtime cre.Runtime, evmClient *evm.Client, consumerAddress common.Address, gasLimit uint64) (string, error) {
    uint256Type, err := abi.NewType("uint256", "", nil)
    if err != nil {
        return "", fmt.Errorf("create uint256 ABI type: %w", err)
    }
    args := abi.Arguments{{Type: uint256Type}}
    encoded, err := args.Pack(big.NewInt(42000000000))
    if err != nil {
        return "", fmt.Errorf("encode report payload: %w", err)
    }

    report, err := runtime.GenerateReport(&cre.ReportRequest{
        EncodedPayload: encoded,
        EncoderName:    "evm",
        SigningAlgo:    "ecdsa",
        HashingAlgo:    "keccak256",
    }).Await()
    if err != nil {
        return "", fmt.Errorf("generate report: %w", err)
    }

    resp, err := evmClient.WriteReport(runtime, &evm.WriteCreReportRequest{
        Receiver:  consumerAddress.Bytes(),
        Report:    report,
        GasConfig: &evm.GasConfig{GasLimit: gasLimit},
    }).Await()
    if err != nil {
        return "", fmt.Errorf("write report: %w", err)
    }

    return common.BytesToHash(resp.TxHash).Hex(), nil
}

func InitWorkflow(config *Config, logger *slog.Logger, secretsProvider cre.SecretsProvider) (cre.Workflow[*Config], error) {
    return cre.Workflow[*Config]{
        cre.Handler(
            cron.Trigger(&cron.Config{Schedule: config.Schedule}),
            onCronTrigger,
        ),
    }, nil
}

func main() {
    wasm.NewRunner(cre.ParseJSON[Config]).Run(InitWorkflow)
}
```

The binding generator creates a `WriteReportFrom<StructName>` helper named after each ABI input struct. That helper performs the ABI encoding, `runtime.GenerateReport()`, and `evmClient.WriteReport()` steps for you.

### TxStatus Values

| Go | TypeScript | Description |
|----|------------|-------------|
| `evm.TxStatus_TX_STATUS_SUCCESS` | `TxStatus.SUCCESS` | Transaction confirmed and successful |
| `evm.TxStatus_TX_STATUS_REVERTED` | `TxStatus.REVERTED` | Transaction was reverted onchain |
| `evm.TxStatus_TX_STATUS_FATAL` | `TxStatus.FATAL` | Transaction failed with an unrecoverable error |

### Gas Configuration

In Go, pass `&evm.GasConfig{GasLimit: <uint64>}` to the write call, or pass `nil` to accept the default. In TypeScript, set the per-write limit with `gasConfig.gasLimit`.

## Go Binding Generation

Place raw ABI arrays (`*.abi`) or compiled contract artifacts (`*.json`) in `contracts/evm/src/abi/`, then generate the bindings:

```bash
cre generate-bindings evm
```

Generated Go packages land under `contracts/evm/src/generated/`. Constructors return the binding and an error, and generated read methods take the runtime first:

```go
evmClient := &evm.Client{ChainSelector: config.ChainSelector}
address := common.HexToAddress(config.ContractAddress)
binding, err := my_contract.NewMyContract(evmClient, address, nil)
if err != nil {
    return nil, fmt.Errorf("create MyContract binding: %w", err)
}
result, err := binding.MyMethod(runtime, my_contract.MyMethodInput{
    Arg1: arg1,
    Arg2: arg2,
}, big.NewInt(-3)).Await()
```

Methods with no ABI inputs omit the `args` parameter entirely.

## Consumer Contracts

### Overview

A consumer contract receives data written by a CRE workflow. It must implement the `IReceiver` interface to accept reports from the `KeystoneForwarder`.

### IReceiver Interface

The `IReceiver` interface is the minimal contract a consumer must satisfy:

```solidity
interface IReceiver {
    function onReport(bytes calldata metadata, bytes calldata report) external;
}
```

Parameters:
- `metadata`: Contains workflow ID, DON ID, and execution metadata. Use this for access control or audit logging if needed.
- `report`: ABI-encoded payload matching what `runtime.report()` produces in the workflow code.

### Direct IReceiver Implementation

If you need full control over access control, implement `IReceiver` directly:

```solidity
// SPDX-License-Identifier: MIT
pragma solidity 0.8.24;

import {IReceiver} from "./interfaces/IReceiver.sol";

contract MyConsumer is IReceiver {
    address public immutable forwarder;
    uint256 public lastPrice;
    uint256 public lastTimestamp;

    error UnauthorizedForwarder(address caller);

    constructor(address _forwarder) {
        forwarder = _forwarder;
    }

    function onReport(bytes calldata metadata, bytes calldata report) external {
        if (msg.sender != forwarder) revert UnauthorizedForwarder(msg.sender);

        (uint256 price, uint256 timestamp) = abi.decode(report, (uint256, uint256));
        lastPrice = price;
        lastTimestamp = timestamp;
    }
}
```

### ReceiverTemplate (Recommended)

Use the `ReceiverTemplate` base contract for easier implementation. It provides the `onlyForwarder` modifier and handles forwarder address validation:

```solidity
// SPDX-License-Identifier: MIT
pragma solidity 0.8.24;

import {ReceiverTemplate} from "./interfaces/ReceiverTemplate.sol";

contract MyConsumer is ReceiverTemplate {
    uint256 public lastPrice;

    constructor(address forwarderAddress)
        ReceiverTemplate(forwarderAddress)
    {}

    function onReport(bytes calldata metadata, bytes calldata report)
        external
        override
        onlyForwarder
    {
        (uint256 price) = abi.decode(report, (uint256));
        lastPrice = price;
    }
}
```

### Best Practices

- Always validate `msg.sender` against the `KeystoneForwarder` address (use `ReceiverTemplate` or check manually)
- Keep `onReport` gas-efficient; the workflow's `gasLimit` must cover the full execution
- Use `abi.decode` with the exact types matching your workflow's `encodeAbiParameters` call
- Emit events in `onReport` for offchain indexing and monitoring
- Store the forwarder address as `immutable` to save gas

### Key Points

- The `onlyForwarder` modifier restricts calls to the `KeystoneForwarder` contract
- The constructor takes the `KeystoneForwarder` address as a parameter
- The `report` bytes are ABI-encoded, matching what `runtime.report()` produces
- The `metadata` bytes contain workflow and DON information

### Deployment

Deploy consumer contracts to the same chain as specified in your `workflow.yaml` or `config.json`. Pass the `KeystoneForwarder` address for the target network to the constructor. Use the simulation forwarder address (`MockKeystoneForwarder`) during local development and the production forwarder address (`KeystoneForwarder`) when deploying. See [references/chain-selectors.md](chain-selectors.md) for addresses per network.

### Using CRE with Foundry

The CRE receiver contracts (`IReceiver`, `IERC165`, `ReceiverTemplate`) are not published as a Forge-installable package. Copy them from the official docs into your project's `src/interfaces/` directory, then install OpenZeppelin for the `Ownable` dependency used by `ReceiverTemplate`:

```bash
forge install OpenZeppelin/openzeppelin-contracts
```

Add the remapping in `foundry.toml`:

```toml
[profile.default]
remappings = [
    "@openzeppelin/=lib/openzeppelin-contracts/",
]
```

Project structure:

```
contracts/
├── foundry.toml
├── src/
│   ├── interfaces/
│   │   ├── IERC165.sol
│   │   ├── IReceiver.sol
│   │   └── ReceiverTemplate.sol
│   └── MyConsumer.sol
└── test/
    └── MyConsumer.t.sol
```

Import from the local path in your consumer:

```solidity
import {ReceiverTemplate} from "./interfaces/ReceiverTemplate.sol";
```

Get the contract source code from the official docs page: `https://docs.chain.link/cre/guides/workflow/using-evm-client/onchain-write/building-consumer-contracts.md` or open them directly in Remix from the links on that page.

Example test:

```solidity
// SPDX-License-Identifier: MIT
pragma solidity 0.8.24;

import {Test} from "forge-std/Test.sol";
import {MyConsumer} from "../src/MyConsumer.sol";

contract MyConsumerTest is Test {
    MyConsumer public consumer;
    address public forwarder = address(0xF0);

    function setUp() public {
        consumer = new MyConsumer(forwarder);
    }

    function test_onReport_storesPrice() public {
        uint256 price = 42000000000;
        bytes memory report = abi.encode(price);
        bytes memory metadata = "";

        vm.prank(forwarder);
        consumer.onReport(metadata, report);

        assertEq(consumer.lastPrice(), price);
    }

    function test_onReport_revertsIfNotForwarder() public {
        bytes memory report = abi.encode(uint256(1));
        bytes memory metadata = "";

        vm.expectRevert();
        consumer.onReport(metadata, report);
    }
}
```

Run tests:

```bash
forge test
```

### Using CRE with Hardhat

The CRE receiver contracts are not published as an npm package. Copy `IReceiver.sol`, `IERC165.sol`, and `ReceiverTemplate.sol` from the official docs into your project's `contracts/interfaces/` directory, then install OpenZeppelin:

```bash
npm install @openzeppelin/contracts
```

Project structure:

```
├── contracts/
│   ├── interfaces/
│   │   ├── IERC165.sol
│   │   ├── IReceiver.sol
│   │   └── ReceiverTemplate.sol
│   └── MyConsumer.sol
├── test/
│   └── MyConsumer.test.ts
└── hardhat.config.ts
```

Import from the local path in your consumer:

```solidity
import {ReceiverTemplate} from "./interfaces/ReceiverTemplate.sol";
```

Get the contract source code from the official docs page: `https://docs.chain.link/cre/guides/workflow/using-evm-client/onchain-write/building-consumer-contracts.md`

Example test using Hardhat + ethers:

```typescript
import { expect } from "chai"
import { ethers } from "hardhat"

describe("MyConsumer", function () {
  it("should store price from onReport", async function () {
    const [deployer, forwarder] = await ethers.getSigners()

    const Consumer = await ethers.getContractFactory("MyConsumer")
    const consumer = await Consumer.deploy(forwarder.address)

    const price = ethers.parseUnits("42000", 0)
    const report = ethers.AbiCoder.defaultAbiCoder().encode(["uint256"], [price])
    const metadata = "0x"

    await consumer.connect(forwarder).onReport(metadata, report)

    expect(await consumer.lastPrice()).to.equal(price)
  })

  it("should revert if caller is not forwarder", async function () {
    const [deployer, forwarder, attacker] = await ethers.getSigners()

    const Consumer = await ethers.getContractFactory("MyConsumer")
    const consumer = await Consumer.deploy(forwarder.address)

    const report = ethers.AbiCoder.defaultAbiCoder().encode(["uint256"], [1n])

    await expect(
      consumer.connect(attacker).onReport("0x", report)
    ).to.be.reverted
  })
})
```

Run tests:

```bash
npx hardhat test
```

## KeystoneForwarder Addresses

The `KeystoneForwarder` is the onchain entry point that validates CRE-signed reports and forwards them to consumer contracts.

For the full list of production and simulation forwarder addresses per network, see [references/chain-selectors.md](chain-selectors.md). Common production forwarder addresses for testnets:

| Network | CRE Chain Selector Name | Forwarder Address |
|---------|------------------------|-------------------|
| Ethereum Sepolia | `ethereum-testnet-sepolia` | `0xF8344CFd5c43616a4366C34E3EEE75af79a74482` |
| Arbitrum Sepolia | `ethereum-testnet-sepolia-arbitrum-1` | `0x76c9cf548b4179F8901cda1f8623568b58215E62` |
| Base Sepolia | `ethereum-testnet-sepolia-base-1` | `0xF8344CFd5c43616a4366C34E3EEE75af79a74482` |

Simulation uses different `MockKeystoneForwarder` addresses. Always update the forwarder address in your consumer contract constructor when moving from simulation to production.

## Solidity/TypeScript Type Mappings

| Solidity Type | TypeScript Type | Notes |
|---------------|----------------|-------|
| `uint256`, `int256` | `bigint` | Never use `number` |
| `address` | `` `0x${string}` `` | 20-byte hex string |
| `bytes` | `` `0x${string}` `` | Hex-encoded bytes |
| `bytes32` | `` `0x${string}` `` | 32-byte hex string |
| `bool` | `boolean` | |
| `string` | `string` | |
| `uint8` - `uint128` | `bigint` | Use `bigint` for safety |
| `tuple` | Object | Matches struct fields |
| `array` | Array | Typed arrays |

### Decimal Handling

Use `viem` for safe decimal scaling:

```typescript
import { parseUnits, formatUnits } from "viem"

const oneEth = parseUnits("1.0", 18)
const display = formatUnits(1000000000000000000n, 18)
```

## Official Documentation

- Onchain read (TypeScript): `https://docs.chain.link/cre/guides/workflow/using-evm-client/onchain-read-ts.md`
- Onchain read (Go): `https://docs.chain.link/cre/guides/workflow/using-evm-client/onchain-read-go.md`
- Onchain write: `https://docs.chain.link/cre/guides/workflow/using-evm-client/onchain-write/writing-data-onchain.md`
- Consumer contracts: `https://docs.chain.link/cre/guides/workflow/using-evm-client/onchain-write/building-consumer-contracts.md`
- Forwarder addresses: `https://docs.chain.link/cre/guides/workflow/using-evm-client/forwarder-directory-ts.md`
- Go binding generation: `https://docs.chain.link/cre/guides/workflow/using-evm-client/generating-bindings-go.md`
- Go EVM client SDK reference: `https://docs.chain.link/cre/reference/sdk/evm-client-go.md`
