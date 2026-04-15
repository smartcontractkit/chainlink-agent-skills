---
name: chainlink-cre-skill
description: "Enable developers to learn and use Chainlink Runtime Environment (CRE) quickly by referencing filtered CRE docs. Trigger when user wants onboarding, CRE workflow generation (in TypeScript or Golang or other supported languages), workflow guidance, CRE CLI and/or SDK help, runtime operations advice, or capability selection"
license: MIT
compatibility: Designed for AI agents that implement https://agentskills.io/specification, including Claude Code, Cursor Composer, and Codex-style workflows.
allowed-tools: Read WebFetch Write Edit Bash
metadata:
  purpose: CRE developer onboarding, assistance and reference
  version: "0.0.3"
---

# Chainlink CRE Skill

## Overview

Route CRE requests to the simplest valid path. Generate working workflow code on first attempt when possible. Fetch documentation only when a specific gap blocks progress.

## Progressive Disclosure

1. Keep this file as the default guide.
2. Read [references/getting-started.md](references/getting-started.md) only when the user wants CLI installation, account setup, project initialization, or the getting-started tutorial walkthrough.
3. Read [references/workflow-patterns.md](references/workflow-patterns.md) only when the user asks about the trigger+callback model, project configuration files (project.yaml, workflow.yaml, config.json, secrets.yaml), secrets management, DON Time, or randomness.
4. Read [references/triggers.md](references/triggers.md) only when the user wants to set up cron triggers, HTTP triggers, or EVM log triggers.
5. Read [references/evm-client.md](references/evm-client.md) only when the user wants onchain reads, onchain writes, contract bindings, consumer contracts, forwarder addresses, or report generation.
6. Read [references/http-client.md](references/http-client.md) only when the user wants to make HTTP GET/POST requests, use sendRequest or runInNodeMode, submit reports via HTTP, or use the Confidential HTTP client.
7. Read [references/sdk-reference.md](references/sdk-reference.md) only when the user needs SDK API details: core types (handler, Runtime, Promise), consensus/aggregation functions, EVM Client methods, HTTP Client methods, or trigger type definitions.
8. Read [references/cli-reference.md](references/cli-reference.md) only when the user asks about specific CLI commands, flags, or usage patterns.
9. Read [references/operations.md](references/operations.md) only when the user asks about simulating, deploying, monitoring, activating, pausing, updating, or deleting workflows, or about multi-sig wallets.
10. Read [references/concepts.md](references/concepts.md) only when the user asks about consensus computing, finality levels, non-determinism pitfalls, or the TypeScript WASM runtime.
11. Read [references/official-sources.md](references/official-sources.md) only when the answer depends on live data that the reference files do not contain: supported network lists, release notes, template repositories, SDK source code, or forwarder addresses for specific networks.
12. Do not load reference files speculatively.

## Routing

1. Use getting-started.md as the default for onboarding, CLI setup, and first-project questions.
2. For workflow generation tasks, use workflow-patterns.md for project structure, then the relevant capability reference (triggers.md, evm-client.md, http-client.md) for the specific capabilities needed.
3. For SDK API questions, route to sdk-reference.md.
4. For CLI command questions, route to cli-reference.md.
5. For operational concerns (deploy, simulate, monitor), route to operations.md.
6. For conceptual questions (consensus, determinism, WASM), route to concepts.md.
7. Ask one focused question if the language (Go vs TypeScript), trigger type, or capability is unclear.
8. Proceed without asking for read-only work: explanations, code generation, debugging.

## Safety Defaults

These are non-negotiable in generated workflow code.

1. Always use `runtime.Now()` (Go) or `runtime.now()` (TypeScript) for timestamps. Never use `time.Now()`, `Date.now()`, or any local system clock in DON mode.
2. Always use `runtime.Rand()` (Go) for randomness. Never use Go's `math/rand` global functions or `crypto/rand` in DON mode.
3. Always use `runtime.GetSecret()` (Go) or `runtime.getSecret()` (TypeScript) for secrets. Never hardcode API keys, private keys, or credentials.
4. Avoid non-deterministic patterns in DON mode: unsorted map iteration in Go, `Promise.race()`/`Promise.any()` in TypeScript, and unordered object iteration.
5. Always use consensus aggregation (median, identical, field-based) when fetching external data via HTTP or running code in node mode.
6. Default to simulation (`cre workflow simulate`) before deployment. Only provide deployment steps if the user explicitly requests it.
7. Remind users that deployment requires Early Access approval, a funded wallet, and a linked key.
8. Use `bigint` (not `number`) for all Solidity integer types in TypeScript to avoid precision loss.
9. Use `parseUnits()`/`formatUnits()` from viem for safe decimal scaling in TypeScript.

## Workflow Generation Checklist

Follow these steps when generating or scaffolding a new workflow (not just answering questions):

1. Confirm whether the user wants Go or TypeScript. Ask directly if not clear from context.
2. If the workflow involves HTTP requests, ask whether they want regular HTTP or Confidential HTTP. Explain the difference briefly: regular HTTP is the default; Confidential HTTP provides privacy-preserving requests via enclave execution with secret injection and optional response encryption (experimental, simulation only).
3. Generate the complete workflow structure immediately from knowledge and reference files. Mark specific uncertainties inline (e.g., `// NEED: exact chain selector name`).
4. Include simulation commands. Ask the user to run `cre workflow simulate`. Then iterate: error means fetch the specific doc for that error, fix, re-run.
5. One fetch per gap. Never fetch speculatively to prevent hypothetical errors.

## Documentation Access

This skill contains embedded reference content for all core CRE topics. Whether the model needs to fetch external URLs depends on what information is missing.

1. For integration patterns, code generation, and conceptual questions, use the embedded reference files directly. Most questions need zero fetches.
2. If a specific detail is missing from the reference files (e.g., a forwarder address for a new network, or a recently added CLI flag), check [references/official-sources.md](references/official-sources.md) for the correct URL to fetch.
3. If WebFetch is available, use it. If it returns less than ~1000 chars of useful content, fall back to `curl -s -L -A "Mozilla/5.0 ..." "<url>"`. If both fail, report the URL to the user.
4. Keep fetches proportional: 0-1 is normal, 2-3 is a ceiling. Most questions need no fetches.

## Working Rules

1. Generate working code from knowledge and reference files first. Fetch only when a specific detail is missing.
2. Keep answers proportional: a simple trigger setup question gets a code block and brief explanation, not a full tutorial.
3. Generate code only when code is actually needed.
4. Keep unsupported or out-of-scope features out of the answer rather than speculating.
5. Many topics have separate Go and TypeScript pages. Ask the user which language they're using if unclear, or address both.

## Known Issues

### Secret name/env var substring conflict (CRE CLI v1.1.0)

**Problem:** Secret resolution fails with "secret not found" if the env var name in `secrets.yaml` is a substring or prefix of the secret name (the YAML key). For example, secret name `GEMINI_API_KEY_SECRET` with env var `GEMINI_API_KEY` fails because `GEMINI_API_KEY` is a prefix of `GEMINI_API_KEY_SECRET`.

**Workaround:** Ensure the env var name is never a substring/prefix of the secret name. Use a suffix like `_VAR` on the env var (e.g., `GEMINI_API_KEY_VAR`).
