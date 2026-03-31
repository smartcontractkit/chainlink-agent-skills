# CRE Prediction Market Demo Repository

## Overview

- https://github.com/smartcontractkit/cre-gcp-prediction-market-demo/blob/main/README.md — full demo overview: AI-powered prediction market with CRE, Gemini AI, Firebase, architecture diagrams, step-by-step guide

## CRE Workflow

- https://github.com/smartcontractkit/cre-gcp-prediction-market-demo/tree/main/cre-workflow — CRE workflow project root (project.yaml, secrets.yaml)
- https://github.com/smartcontractkit/cre-gcp-prediction-market-demo/blob/main/cre-workflow/README.md — workflow setup and deployment guide
- https://github.com/smartcontractkit/cre-gcp-prediction-market-demo/blob/main/cre-workflow/project.yaml — CRE project configuration (RPC endpoints, targets)
- https://github.com/smartcontractkit/cre-gcp-prediction-market-demo/blob/main/cre-workflow/secrets.yaml — secrets configuration template
- https://github.com/smartcontractkit/cre-gcp-prediction-market-demo/blob/main/cre-workflow/prediction-market-demo/main.ts — main workflow logic: EVM log trigger, Gemini AI call, Firebase write, onchain settlement
- https://github.com/smartcontractkit/cre-gcp-prediction-market-demo/blob/main/cre-workflow/prediction-market-demo/evm.ts — EVM client setup and onchain write logic
- https://github.com/smartcontractkit/cre-gcp-prediction-market-demo/blob/main/cre-workflow/prediction-market-demo/gemini.ts — Gemini AI integration for outcome determination
- https://github.com/smartcontractkit/cre-gcp-prediction-market-demo/blob/main/cre-workflow/prediction-market-demo/firebase.ts — Firestore data persistence integration
- https://github.com/smartcontractkit/cre-gcp-prediction-market-demo/blob/main/cre-workflow/prediction-market-demo/types.ts — TypeScript type definitions for workflow data
- https://github.com/smartcontractkit/cre-gcp-prediction-market-demo/blob/main/cre-workflow/prediction-market-demo/workflow.yaml — workflow YAML configuration
- https://github.com/smartcontractkit/cre-gcp-prediction-market-demo/blob/main/cre-workflow/prediction-market-demo/config.json — workflow config (market addresses, chain selectors, gas limits)
- https://github.com/smartcontractkit/cre-gcp-prediction-market-demo/blob/main/cre-workflow/prediction-market-demo/package.json — workflow package dependencies

## Smart Contracts

- https://github.com/smartcontractkit/cre-gcp-prediction-market-demo/tree/main/contracts — Foundry project with Solidity contracts and tests
- https://github.com/smartcontractkit/cre-gcp-prediction-market-demo/blob/main/contracts/src/SimpleMarket.sol — prediction market smart contract with CRE receiver integration
- https://github.com/smartcontractkit/cre-gcp-prediction-market-demo/tree/main/contracts/src/interfaces — contract interfaces including ReceiverTemplate
- https://github.com/smartcontractkit/cre-gcp-prediction-market-demo/blob/main/contracts/test/SimpleMarket.t.sol — contract test suite
- https://github.com/smartcontractkit/cre-gcp-prediction-market-demo/blob/main/contracts/README.md — contracts README
- https://github.com/smartcontractkit/cre-gcp-prediction-market-demo/tree/main/contracts/script — deployment and interaction scripts (deploy, create market, predict, settle, claim)

## Frontend

- https://github.com/smartcontractkit/cre-gcp-prediction-market-demo/tree/main/frontend — Next.js frontend for viewing settlement history from Firestore
- https://github.com/smartcontractkit/cre-gcp-prediction-market-demo/blob/main/frontend/README.md — frontend setup instructions

## Setup

- https://github.com/smartcontractkit/cre-gcp-prediction-market-demo/blob/main/firebase-setup.md — Firebase/Firestore configuration guide
