# CRE Go SDK Repository

## Overview

- https://github.com/smartcontractkit/cre-sdk-go/blob/main/README.md — repo overview: Go SDK setup and capability update commands
- https://github.com/smartcontractkit/cre-sdk-go/blob/main/go.mod — Go module definition and dependencies
- https://github.com/smartcontractkit/cre-sdk-go/blob/main/go.md — Go SDK documentation and usage guide
- https://github.com/smartcontractkit/cre-sdk-go/blob/main/Makefile — build targets including proto generation and capability updates

## Core SDK

- https://github.com/smartcontractkit/cre-sdk-go/tree/main/cre — core CRE package (workflow, runtime, triggers, consensus, promises)
- https://github.com/smartcontractkit/cre-sdk-go/blob/main/cre/workflow.go — workflow definition entry point
- https://github.com/smartcontractkit/cre-sdk-go/blob/main/cre/runtime.go — runtime interface (Now, Rand, GetSecret, Log)
- https://github.com/smartcontractkit/cre-sdk-go/blob/main/cre/consensus_aggregators.go — consensus aggregation functions (median, mode, etc.)
- https://github.com/smartcontractkit/cre-sdk-go/blob/main/cre/trigger.go — trigger registration and types
- https://github.com/smartcontractkit/cre-sdk-go/blob/main/cre/report.go — report generation for onchain writes
- https://github.com/smartcontractkit/cre-sdk-go/blob/main/cre/promise.go — promise type for async capability calls
- https://github.com/smartcontractkit/cre-sdk-go/blob/main/cre/runner.go — workflow runner entry point
- https://github.com/smartcontractkit/cre-sdk-go/blob/main/cre/execution_handler.go — execution handler logic
- https://github.com/smartcontractkit/cre-sdk-go/blob/main/cre/parsers.go — input/output parsers
- https://github.com/smartcontractkit/cre-sdk-go/blob/main/cre/const.go — SDK constants

## WASM Runtime

- https://github.com/smartcontractkit/cre-sdk-go/tree/main/cre/wasm — WASM (wasip1) runtime, runner, and writer implementations

## Capabilities

- https://github.com/smartcontractkit/cre-sdk-go/tree/main/capabilities/blockchain/evm — EVM client capability (read/write smart contracts)
- https://github.com/smartcontractkit/cre-sdk-go/tree/main/capabilities/blockchain/solana — Solana client capability
- https://github.com/smartcontractkit/cre-sdk-go/tree/main/capabilities/networking/http — HTTP client capability
- https://github.com/smartcontractkit/cre-sdk-go/tree/main/capabilities/networking/confidentialhttp — confidential HTTP capability (secrets in requests)
- https://github.com/smartcontractkit/cre-sdk-go/tree/main/capabilities/scheduler/cron — cron trigger capability

## Code Generation

- https://github.com/smartcontractkit/cre-sdk-go/tree/main/generator/protoc-gen-cre — protobuf code generator for CRE capability bindings
- https://github.com/smartcontractkit/cre-sdk-go/tree/main/cmd/newcapability — CLI tool to scaffold new capabilities from templates

## Test Utilities

- https://github.com/smartcontractkit/cre-sdk-go/tree/main/cre/testutils — test runtime and mock utilities
- https://github.com/smartcontractkit/cre-sdk-go/tree/main/standard_tests — standard WASM integration tests (secrets, logging, triggers, errors, time, random, mode switch)
- https://github.com/smartcontractkit/cre-sdk-go/tree/main/internal_testing/capabilities — internal test capabilities (basic action, trigger, consensus, node action)
- https://github.com/smartcontractkit/cre-sdk-go/tree/main/internal/test_workflow — internal test workflow examples
