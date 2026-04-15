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
  EVMClientCapability,
  CronCapability,
  handler,
  Runner,
  type Runtime,
} from "@chainlink/cre-sdk"
import {
  parseAbi,
  encodeFunctionData,
  decodeFunctionResult,
} from "viem"

type Config = {
  schedule: string
  contractAddress: string
  chainSelectorName: string
}

const abi = parseAbi([
  "function latestRoundData() external view returns (uint80 roundId, int256 answer, uint256 startedAt, uint256 updatedAt, uint80 answeredInRound)",
])

const LAST_FINALIZED_BLOCK_NUMBER = 0n

const onCronTrigger = (runtime: Runtime<Config>): string => {
  const evmClient = new EVMClientCapability()

  const callData = encodeFunctionData({
    abi,
    functionName: "latestRoundData",
  })

  const result = evmClient
    .callContract(runtime, {
      toAddress: runtime.config.contractAddress,
      chainSelectorName: runtime.config.chainSelectorName,
      callMsg: {
        data: callData,
        blockNumber: LAST_FINALIZED_BLOCK_NUMBER,
      },
    })
    .result()

  const decoded = decodeFunctionResult({
    abi,
    functionName: "latestRoundData",
    data: result.data as `0x${string}`,
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
    "math/big"
    "github.com/smartcontractkit/cre-sdk-go/cre"
    "github.com/smartcontractkit/cre-sdk-go/capabilities/scheduler/cron"
    "my-project/contracts/evm/src/abi"
)

type Config struct {
    Schedule          string `json:"schedule"`
    ContractAddress   string `json:"contractAddress"`
    ChainSelectorName string `json:"chainSelectorName"`
}

type Result struct {
    Price string `json:"price"`
}

func onCronTrigger(config *Config, runtime cre.Runtime, trigger *cron.Payload) (*Result, error) {
    evmClient := runtime.EVMClient()

    binding := abi.NewAggregatorV3Interface(
        config.ContractAddress,
        config.ChainSelectorName,
        evmClient,
    )

    result, err := binding.LatestRoundData(big.NewInt(-3)).Await()
    if err != nil {
        return nil, err
    }

    return &Result{Price: result.Answer.String()}, nil
}

func InitWorkflow(config *Config) []cre.HandlerDefinition {
    return []cre.HandlerDefinition{
        cre.Handler(cron.Trigger(cron.Config{Schedule: config.Schedule}), onCronTrigger),
    }
}
```

### Block Number Options

| Value | Description |
|-------|-------------|
| `0n` / `big.NewInt(0)` | Last finalized block (default, recommended) |
| `-1n` / `big.NewInt(-1)` | Latest known block (not finalized) |
| `-2n` / `big.NewInt(-2)` | Safe block |
| `-3n` / `big.NewInt(-3)` | Pending block |
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
2. **Generate a signed report** using `runtime.report()`
3. **Submit the report** using `evmClient.writeReport()`

### TypeScript: Encoding Single Values

```typescript
import { encodeAbiParameters, parseAbiParameters } from "viem"

const encoded = encodeAbiParameters(
  parseAbiParameters("uint256 price"),
  [42000000000n]
)
```

### TypeScript: Encoding Structs

```typescript
const encoded = encodeAbiParameters(
  parseAbiParameters("(uint256 price, uint256 timestamp)"),
  [{ price: 42000000000n, timestamp: BigInt(Math.floor(Date.now() / 1000)) }]
)
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
  EVMClientCapability,
  CronCapability,
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
  const evmClient = new EVMClientCapability()

  const encoded = encodeAbiParameters(
    parseAbiParameters("uint256 price"),
    [42000000000n]
  )

  const signedReport = runtime.report(encoded)

  const txResult = evmClient
    .writeReport(runtime, {
      toAddress: runtime.config.consumerAddress,
      chainSelectorName: runtime.config.chainSelectorName,
      report: signedReport,
      gasLimit: 500000n,
    })
    .result()

  runtime.log(`TX hash: ${txResult.txHash}`)
  runtime.log(`TX status: ${txResult.txStatus}`)

  return txResult.txHash
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
    "math/big"
    "github.com/ethereum/go-ethereum/accounts/abi"
    "github.com/smartcontractkit/cre-sdk-go/cre"
    "github.com/smartcontractkit/cre-sdk-go/capabilities/scheduler/cron"
)

type Config struct {
    Schedule          string `json:"schedule"`
    ConsumerAddress   string `json:"consumerAddress"`
    ChainSelectorName string `json:"chainSelectorName"`
}

func onCronTrigger(config *Config, runtime cre.Runtime, trigger *cron.Payload) (*string, error) {
    evmClient := runtime.EVMClient()

    uint256Type, _ := abi.NewType("uint256", "", nil)
    args := abi.Arguments{{Type: uint256Type}}
    encoded, err := args.Pack(big.NewInt(42000000000))
    if err != nil {
        return nil, err
    }

    signedReport := runtime.Report(encoded)

    txResult, err := evmClient.WriteReport(cre.WriteReportConfig{
        ToAddress:         config.ConsumerAddress,
        ChainSelectorName: config.ChainSelectorName,
        Report:            signedReport,
        GasLimit:          big.NewInt(500000),
    }).Await()
    if err != nil {
        return nil, err
    }

    result := txResult.TxHash
    return &result, nil
}

func InitWorkflow(config *Config) []cre.HandlerDefinition {
    return []cre.HandlerDefinition{
        cre.Handler(cron.Trigger(cron.Config{Schedule: config.Schedule}), onCronTrigger),
    }
}
```

### TxStatus Values

| Status | Description |
|--------|-------------|
| `Success` | Transaction confirmed and successful |
| `Reverted` | Transaction was reverted on chain |
| `Pending` | Transaction is pending confirmation |
| `FatalError` | Unrecoverable error |

### Gas Configuration

Default gas limit is 500,000. Override per-write with the `gasLimit` parameter.

## Go Binding Generation

Generate type-safe Go bindings from Solidity ABI files:

```bash
cre generate-bindings --abi-dir contracts/evm/src/abi --pkg abi --output contracts/evm/src/abi
```

Place ABI JSON files in the `contracts/evm/src/abi/` directory:

```
contracts/evm/src/abi/
├── AggregatorV3Interface.json
└── MyContract.json
```

Generated bindings provide type-safe methods that return `Promise` objects:

```go
binding := abi.NewMyContract(address, chainSelector, evmClient)
result, err := binding.MyMethod(arg1, arg2).Await()
```

## Consumer Contracts

### Overview

A consumer contract receives data written by a CRE workflow. It must implement the `IReceiver` interface to accept reports from the `KeystoneForwarder`.

### IReceiver Interface

```solidity
interface IReceiver {
    function onReport(bytes calldata metadata, bytes calldata report) external;
}
```

### ReceiverTemplate

Use the `ReceiverTemplate` base contract for easier implementation:

```solidity
// SPDX-License-Identifier: MIT
pragma solidity 0.8.24;

import {ReceiverTemplate} from "@chainlink/cre-contracts/src/ReceiverTemplate.sol";

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

### Key Points

- The `onlyForwarder` modifier restricts calls to the `KeystoneForwarder` contract
- The constructor takes the `KeystoneForwarder` address as a parameter
- The `report` bytes are ABI-encoded, matching what `runtime.report()` produces
- The `metadata` bytes contain workflow and DON information

### Deployment

Deploy consumer contracts to the same chain as specified in your `workflow.yaml` or `config.json`. Pass the `KeystoneForwarder` address for the target network to the constructor.

## KeystoneForwarder Addresses

The `KeystoneForwarder` is the onchain entry point that validates CRE-signed reports and forwards them to consumer contracts.

### Testnet

| Network | Address |
|---------|---------|
| Ethereum Sepolia | `0x2cfC062B1B5c97a73BC7Ad4E67d1cd416e4DE71b` |
| Arbitrum Sepolia | `0x2cfC062B1B5c97a73BC7Ad4E67d1cd416e4DE71b` |
| Base Sepolia | `0x2cfC062B1B5c97a73BC7Ad4E67d1cd416e4DE71b` |

For a full up-to-date list, check the forwarder addresses page in the official documentation.

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

- Onchain read (TypeScript): `https://docs.chain.link/cre/guides/workflow/using-evm-client/onchain-read-ts`
- Onchain read (Go): `https://docs.chain.link/cre/guides/workflow/using-evm-client/onchain-read-go`
- Onchain write: `https://docs.chain.link/cre/guides/workflow/using-evm-client/onchain-write/writing-data-onchain`
- Consumer contracts: `https://docs.chain.link/cre/guides/workflow/using-evm-client/onchain-write/consumer-contracts`
- Forwarder addresses: `https://docs.chain.link/cre/reference/forwarder-addresses`
