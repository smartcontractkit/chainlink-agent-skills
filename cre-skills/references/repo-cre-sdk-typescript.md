# CRE TypeScript SDK Repository

## Overview

- https://github.com/smartcontractkit/cre-sdk-typescript/blob/main/README.md — monorepo overview: CRE TypeScript SDK, examples, Javy WASM plugin
- https://github.com/smartcontractkit/cre-sdk-typescript/blob/main/PUBLISHING.md — package publishing guide
- https://github.com/smartcontractkit/cre-sdk-typescript/blob/main/turbo.json — turborepo build configuration

## Core SDK

- https://github.com/smartcontractkit/cre-sdk-typescript/tree/main/packages/cre-sdk — main CRE SDK package (types, capabilities, consensus, EVM/HTTP clients)
- https://github.com/smartcontractkit/cre-sdk-typescript/blob/main/packages/cre-sdk/README.md — SDK package README with API details and build instructions
- https://github.com/smartcontractkit/cre-sdk-typescript/blob/main/packages/cre-sdk/src/index.ts — SDK main entry point and public exports
- https://github.com/smartcontractkit/cre-sdk-typescript/tree/main/packages/cre-sdk/src/sdk — core SDK implementation (runtime, workflow, types, report, errors)
- https://github.com/smartcontractkit/cre-sdk-typescript/blob/main/packages/cre-sdk/src/sdk/workflow.ts — workflow definition and orchestration
- https://github.com/smartcontractkit/cre-sdk-typescript/blob/main/packages/cre-sdk/src/sdk/runtime.ts — SDK runtime implementation
- https://github.com/smartcontractkit/cre-sdk-typescript/blob/main/packages/cre-sdk/src/sdk/report.ts — report generation for onchain writes
- https://github.com/smartcontractkit/cre-sdk-typescript/tree/main/packages/cre-sdk/src/sdk/types — SDK type definitions
- https://github.com/smartcontractkit/cre-sdk-typescript/tree/main/packages/cre-sdk/src/generated/capabilities — generated capability type definitions
- https://github.com/smartcontractkit/cre-sdk-typescript/tree/main/packages/cre-sdk/src/generated-sdk/capabilities — generated SDK capability wrappers
- https://github.com/smartcontractkit/cre-sdk-typescript/tree/main/packages/cre-sdk/src/generated/chain-selectors — generated chain selector constants

## HTTP Trigger Package

- https://github.com/smartcontractkit/cre-sdk-typescript/tree/main/packages/cre-http-trigger — HTTP trigger testing package
- https://github.com/smartcontractkit/cre-sdk-typescript/blob/main/packages/cre-http-trigger/README.md — HTTP trigger package README
- https://github.com/smartcontractkit/cre-sdk-typescript/blob/main/packages/cre-http-trigger/src/index.ts — HTTP trigger entry point

## SDK Examples

- https://github.com/smartcontractkit/cre-sdk-typescript/tree/main/packages/cre-sdk-examples — example workflows and patterns
- https://github.com/smartcontractkit/cre-sdk-typescript/blob/main/packages/cre-sdk-examples/README.md — examples README with usage instructions
- https://github.com/smartcontractkit/cre-sdk-typescript/tree/main/packages/cre-sdk-examples/src/workflows/hello-world — hello world example (index.ts, config.json, workflow.yaml)
- https://github.com/smartcontractkit/cre-sdk-typescript/tree/main/packages/cre-sdk-examples/src/workflows/http-fetch — HTTP fetch example workflow
- https://github.com/smartcontractkit/cre-sdk-typescript/tree/main/packages/cre-sdk-examples/src/workflows/http-confidential-fetch — confidential HTTP fetch example
- https://github.com/smartcontractkit/cre-sdk-typescript/tree/main/packages/cre-sdk-examples/src/workflows/http-confidential-fetch-with-secrets — confidential HTTP fetch with secrets
- https://github.com/smartcontractkit/cre-sdk-typescript/tree/main/packages/cre-sdk-examples/src/workflows/on-chain — on-chain read example workflow
- https://github.com/smartcontractkit/cre-sdk-typescript/tree/main/packages/cre-sdk-examples/src/workflows/on-chain-write — on-chain write example workflow
- https://github.com/smartcontractkit/cre-sdk-typescript/tree/main/packages/cre-sdk-examples/src/workflows/log-trigger — log trigger example workflow
- https://github.com/smartcontractkit/cre-sdk-typescript/tree/main/packages/cre-sdk-examples/src/workflows/proof-of-reserve — proof of reserve example workflow
- https://github.com/smartcontractkit/cre-sdk-typescript/tree/main/packages/cre-sdk-examples/src/workflows/secrets — secrets usage example workflow
- https://github.com/smartcontractkit/cre-sdk-typescript/tree/main/packages/cre-sdk-examples/src/workflows/star-wars — star wars API example workflow

## Javy Plugin

- https://github.com/smartcontractkit/cre-sdk-typescript/tree/main/packages/cre-sdk-javy-plugin — WASM/Javy compilation plugin for TypeScript workflows
- https://github.com/smartcontractkit/cre-sdk-typescript/blob/main/packages/cre-sdk-javy-plugin/README.md — Javy plugin README

## Scripts

- https://github.com/smartcontractkit/cre-sdk-typescript/tree/main/scripts/e2e — end-to-end simulation scripts (hello-world, log-trigger, star-wars)
- https://github.com/smartcontractkit/cre-sdk-typescript/blob/main/scripts/full-checks.sh — full build and lint checks script
