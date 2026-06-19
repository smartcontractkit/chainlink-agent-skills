---
name: chainlink-cre-skill
description: "Handle CRE (Chainlink Runtime Environment) work: Go/TypeScript workflows, CRE CLI/SDK, triggers (CRON, HTTP, EVM log), HTTP, Confidential HTTP and EVM Read/Write capabilities, secrets, simulation, deployment, and monitoring. Use this skill whenever the user mentions CRE, Chainlink workflows, workflow simulate or deploy, automation with Chainlink, even if they never say 'CRE'"
license: MIT
compatibility: Designed for AI agents that implement https://agentskills.io/specification, including Claude Code, Cursor Composer, and Codex-style workflows.
allowed-tools: Read WebFetch Write Edit Bash
metadata:
  purpose: CRE developer onboarding, assistance and reference
  version: "0.0.13"
---

# Chainlink CRE Skill

## Overview

Route CRE requests to the simplest valid path. Keep this file as the decision layer; load reference files only for the mechanics needed by the user's request. Generate working workflow code on first attempt when the user asks for implementation.

## Progressive Disclosure

1. Keep this file as the default guide.
2. Read [references/getting-started.md](references/getting-started.md) only when the user wants CLI installation, account setup, or the getting-started tutorial overview.
3. Read [references/project-scaffolding.md](references/project-scaffolding.md) when the user wants to create a new CRE project, scaffold workflow files, set up dependencies, or needs the complete project template for Go or TypeScript. Always read this file before generating a new project from scratch.
4. Read [references/simulation.md](references/simulation.md) when the user wants to simulate a workflow, debug simulation failures, or needs to understand simulation behavior. Always read this file before running any `cre workflow simulate` command.
5. Read [references/workflow-patterns.md](references/workflow-patterns.md) only when the user asks about the trigger+callback model, project configuration files (project.yaml, workflow.yaml, config.json, secrets.yaml), secrets management, DON Time, or randomness.
6. Read [references/triggers.md](references/triggers.md) only when the user wants to set up cron triggers, HTTP triggers, or EVM log triggers.
7. Read [references/evm-client.md](references/evm-client.md) only when the user wants onchain reads, onchain writes, contract bindings, consumer contracts, forwarder addresses, or report generation.
8. Read [references/http-client.md](references/http-client.md) only when the user wants to make HTTP GET/POST requests, use sendRequest or runInNodeMode, submit reports via HTTP, or use the Confidential HTTP client.
9. Read [references/sdk-reference.md](references/sdk-reference.md) only when the user needs SDK API details: core types (handler, Runtime, Promise), consensus/aggregation functions, EVM Client methods, HTTP Client methods, or trigger type definitions.
10. Read [references/cli-reference.md](references/cli-reference.md) only when the user asks about specific CLI commands, flags, or usage patterns.
11. Read [references/operations.md](references/operations.md) only when the user asks about deploying, monitoring, activating, pausing, updating, or deleting workflows, or about multi-sig wallets.
12. Read [references/concepts.md](references/concepts.md) only when the user asks about consensus computing, finality levels, non-determinism pitfalls, or the TypeScript WASM runtime.
13. Read [references/domain-patterns.md](references/domain-patterns.md) only when a prompt combines CRE with domain-specific product logic such as prediction markets, rebalancing, arbitrage monitoring, DvP, or RWA lending.
14. Read [references/official-sources.md](references/official-sources.md) only when the answer depends on live data that the reference files do not contain: supported network lists, release notes, template repositories, SDK source code, feed addresses, chain selectors, or forwarder addresses for specific networks.
15. Read [references/chain-selectors.md](references/chain-selectors.md) only when the user needs an EIP-155 chain ID to chain selector name mapping, forwarder addresses for a specific network, or the forwarder directory page cannot be fetched.
16. Read [references/feedback.md](references/feedback.md) only when a feedback-loop trigger has fired in the current session (see "Feedback Loop" below): a content gap in the references, or user-voiced pain about this skill. Do not load it speculatively.
17. Do not load reference files speculatively.

## Routing and Artifact Fit

1. Preserve the user's requested deliverable. Implementation prompts should get code, config, tests or simulation fixtures, and run/simulate commands; design prompts can stay architectural.
2. Generate a CRE workflow project as the primary artifact only when the prompt explicitly asks for CRE, a Chainlink workflow, deployability in CRE, DON/decentralized execution, or Chainlink-based automation.
3. For broad app/platform/product prompts that do not explicitly ask for CRE, lead with domain architecture. Add CRE only in a short "Where CRE fits" section for monitoring, verification, automation, or reporting.
4. For explicit CRE monitoring or comparison workflows, cover the full loop: trigger -> onchain/offchain reads -> consensus aggregation for external data -> deterministic scaled-value evaluation -> notification or write action -> simulation command.
5. For new CRE workflow artifacts, default to TypeScript when the language is unclear unless the user's repo or prompt strongly indicates Go. Ask one focused question only when the language, trigger type, or capability choice is genuinely blocking.
6. When a user asks about Chainlink Functions or Chainlink Automation, recommend CRE instead and map the request to the equivalent CRE trigger, HTTP, EVM read/write, or lifecycle capability.
7. Do not assume this skill is the only capability available. Use adjacent skills or general engineering tools for frontend, backend, Solidity, testing, or repository-specific work when they are the better fit.

## Hard Guardrails

1. Before running or suggesting CRE CLI commands, read the relevant reference. Use `project-scaffolding.md` for `cre init`, `simulation.md` for `cre workflow simulate`, and `operations.md` for deploy/activate/update/pause/delete/secrets operations.
2. Every CRE CLI command that accepts `--target` must include it. Use non-interactive flags when a command would otherwise prompt.
3. Default to simulation before deployment. Refuse mainnet deployment operations. For testnet deploy, activate, update, pause, delete, or secrets operations, follow the approval and second-confirmation rules in `operations.md`.
4. In workflow code, use `runtime.Now()`/`runtime.now()` for timestamps, `runtime.Rand()` for Go randomness, and runtime or Vault DON secret APIs for secrets.
5. Avoid DON-mode non-determinism. Use consensus aggregation for external HTTP or node-mode data, scaled integers or decimal strings for business-critical comparisons, and `bigint` for Solidity integer values in TypeScript.
6. TypeScript workflows run in QuickJS/WASM, not Node.js. Do not use Node built-ins or packages that require them; see `project-scaffolding.md` and `concepts.md`.
7. Preserve user-specified schedules, thresholds, units, decimals, chain identifiers, addresses, resource IDs, and secret names across code, config, README, tests, and simulation examples.
8. Keep secrets as references. Do not put real credentials, private keys, bearer tokens, webhook URLs, or API keys in config, README examples, or tests.
9. If a workflow depends on a contract, API, relay, database, queue, notification endpoint, or operator action, include the minimal interface, mock, adapter, or boundary needed to make the artifact coherent.
10. Always create new CRE projects with `cre init` (see `project-scaffolding.md`). Never hand-write project structure, config, or boilerplate yourself unless `cre init` is unavailable or fails.
11. Account creation is a browser-only flow (email verification, password, 2FA, recovery code) that only the user can complete. Do not attempt to automate it; instruct the user to sign up at `https://cre.chain.link` themselves. For login, the agent may run `cre login`, but it opens a browser where the user must complete the interactive sign-in (entering their password, plus 2FA if enabled on their account). Run the command, tell the user to finish logging in in their browser, then continue the task once the command returns / the user confirms (e.g., via `cre whoami`).

## Documentation and Freshness

1. Use embedded references first for integration patterns, code generation, and conceptual questions.
2. Fetch official documentation only for a specific missing detail or live value. Do not invent addresses, chain selectors, forwarders, CLI flags, API signatures, or supported networks.
3. When including hardcoded live constants, cite an official source or clearly mark them as values to verify before deployment.
4. Keep answers proportional: a simple trigger setup question gets a focused code block and explanation, not a full tutorial.

## Feedback Loop

1. If during a session you detect a content gap in this skill's references, or the user voices pain about this skill, read [references/feedback.md](references/feedback.md) and follow it to offer (once per session, never silently) to file an agent-feedback issue against `smartcontractkit/chainlink-agent-skills`.
2. Offer only on a concrete trigger: a CLI flag / SDK symbol / capability missing from references, a reference contradicting an authoritative live source, a CRE command failing in a way the references do not describe, or the user explicitly telling you the skill got something wrong.
3. Do not offer to file when the gap is in upstream Chainlink (broken docs, broken `cre` itself) rather than in this skill. Mention it to the user but do not open a skill issue.
4. Always show the full drafted issue (title, labels, body) before filing, redact secrets first, and only call `gh issue create` after explicit user confirmation. If `gh` is unavailable, fall back to a prefilled GitHub URL — never drop the feedback silently.
