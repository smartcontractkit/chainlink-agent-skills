---
name: chainlink-data-streams-skill
description: "Help developers build with Chainlink Data Streams, including credentials guidance, report decoding, REST and WebSocket report retrieval with official Go/Rust/TypeScript SDKs, High Availability streaming, on-chain report verification, real-time frontend displays, report schema guidance, SQLite persistence, and timestamp lookback. Use this skill whenever the user mentions Chainlink Data Streams, Streams Direct, Data Streams reports, report schemas, report decoding, data-streams-sdk, or real-time low-latency market data from Chainlink."
license: MIT
compatibility: Designed for AI agents that implement https://agentskills.io/specification, including Claude Code, Cursor Composer, and Codex-style workflows.
allowed-tools: Read WebFetch Write Edit Bash
metadata:
  purpose: Chainlink Data Streams developer assistance and reference
  version: "0.0.1"
  mcp-server: "@upstash/context7-mcp"
---

# Chainlink Data Streams Skill

## Overview

Route Data Streams requests to the simplest valid path while keeping credentials, billing information, and on-chain side effects tightly controlled.

## Status

This initial scaffold establishes the skill identity and repository structure. Curated references, routing rules, safety guardrails, and evals are added in the following implementation steps.
