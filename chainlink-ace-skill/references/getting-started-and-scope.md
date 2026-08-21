# Getting Started and Scope

Read for what ACE is, use-case fit, starting from the repository, production/license scope, custom components or mainnet feasibility, and OSS-versus-managed capability questions.

## What ACE Is

Chainlink Automated Compliance Engine core contracts are a modular EVM toolkit separating application business logic from enforcement:
- Policy Management enforces rules through `PolicyProtected`, `PolicyEngine`, policies, extractors, and mappers.
- Cross-Chain Identity links addresses to CCIDs and credentials for onchain KYC, AML, accreditation, or custom requirements.

Source: `https://github.com/smartcontractkit/chainlink-ace`; package `@chainlink/ace`; BUSL-1.1; Foundry, pnpm, Solidity.

## Choose Components

| Need | Use |
| --- | --- |
| Dynamic rules; add/remove/reorder without changing business logic; access, pause, limit, reserve, or custom policy/extractor/mapper | Policy Management |
| KYC, AML, accreditation, cross-chain address identity, multiple trusted issuers, custom credential types | Cross-Chain Identity |
| Regulated ERC-20 or ERC-3643/T-REX reference integration | Token examples |

## Managed Versus Self-Deployed

| Intent | Authority |
| --- | --- |
| Self-deploy audited contracts from the repository | OSS references in this skill |
| Managed Platform/UI, Coordinator API, Reporting API, or Beta access | [platform-and-beta.md](platform-and-beta.md) plus live `docs.chain.link/ace` |

Do not merge these scopes. Repository support for custom policies or Credential Data Validators does not prove managed Beta support; a managed testnet limitation does not by itself prohibit OSS evaluation under its license and security requirements.

## Fit

ACE fits when the protected contract is EVM-based; the team can integrate `PolicyProtected`, `PolicyProtectedUpgradeable`, or `IPolicyProtected`; deploy/administer PolicyEngine; model rules with built-in/custom policies; audit policies, extractors, mappers, and chains; and review production licensing.

Treat policy order as a security property: `Allowed` skips every later policy, so restrictive checks must precede intentional bypasses.

Plan additional design when:
- the contract is non-upgradeable or near the 24KB bytecode limit;
- rules depend on external systems, signatures, complex context, or non-standard calldata requiring a custom extractor;
- raw contracts need operational indexing, dashboards, or admin tooling;
- the team expects managed visibility for self-deployed contracts, because registration/indexing is freshness-sensitive product scope.

## License Guidance

The repository uses BUSL-1.1. Do not infer specific permissions or a license-change date: for production, cite the current repository `LICENSE` and `chainlink-ace-License-grants`, contact Chainlink about a production/commercial license, and require counsel to review the terms. Do not provide legal advice.

Every repository-scope answer must link `https://github.com/smartcontractkit/chainlink-ace`, cite the current `LICENSE` and `chainlink-ace-License-grants`, and name `README.md` and `getting_started/GETTING_STARTED.md` as starting points.
