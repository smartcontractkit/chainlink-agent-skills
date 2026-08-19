# ACE Platform and Beta Scope

Read for ACE Platform/private Beta, product UI or managed API, Policy/Identity/Reporting Manager, Coordinator/Reporting API, auditors, audit trails, networks/mainnet readiness, managed registration/indexing, externally deployed contract visibility, custom managed capabilities, credentials, or product limitations.

## Authority and Boundary

Current product sources:
- Overview: `https://docs.chain.link/ace.md`
- Beta: `https://docs.chain.link/ace/beta-scope.md`
- Networks: `https://docs.chain.link/ace/supported-networks.md`
- Coordinator: `https://docs.chain.link/ace/reference/api/coordinator.md`
- Reporting API/concept: `https://docs.chain.link/ace/reference/api/reporting.md`, `https://docs.chain.link/ace/concepts/reporting.md`

Verify live docs before definitive claims about availability, networks, mainnet, APIs, or Beta limitations.

| Surface | Authority and scope |
| --- | --- |
| OSS/self-deployed contracts | `smartcontractkit/chainlink-ace`; users deploy/extend under BUSL/commercial licensing, security review, and their own infrastructure |
| Managed ACE Platform | `docs.chain.link/ace`; managed UI/APIs subject to access, provisioning, supported networks, private-Beta scope, and product limitations |

Never infer managed support from a repository capability, or infer that a managed Beta limitation prevents OSS evaluation/self-deployment.

## Beta Defaults

As documented April 28, 2026:
- The Platform is private Beta and requires access/provisioning; the Beta scope describes it as testnet-only.
- Supported contract types, attestation-only credentials, self-deployed contract visibility, custom policies/extractors, signing model, and contract upgradeability are scoped or limited areas.
- Do not claim managed mainnet readiness or UI/API support for custom policies, custom extractors, custom fraud-score configuration, or custom Credential Data Validator logic unless current docs do.
- For production/mainnet, lead with the managed limitation. Then distinguish self-deployed OSS evaluation, which still needs BUSL/commercial-license review, audits, operational ownership, legal/compliance review, and deployment approval.

## Managed Surfaces

- **Policy Manager (UI + API):** configure/deploy compliance rules.
- **Identity Manager (UI + API):** manage CCIDs, identities, credential registries/types, issuers, and credentials.
- **Reporting Manager (API):** query policy-run history, transactions, and onchain compliance state.

### Coordinator API

Privileged write/control-plane API for supported management operations:
- delegated signing-wallet creation where supported;
- PolicyEngine deployment/configuration on supported networks;
- policy-library instance creation and parameters;
- target registration and function-selector protection attachment;
- extractor management;
- identity/credential registry creation;
- CCID and wallet mapping registration;
- credential-type definition, credential issuance/management, and trusted-issuer management.

It changes ACE resources and is not the auditor evidence API.

### Reporting API

Read-only audit/monitoring plane for **Transactions, Policies, Targets, and Identities**. Use `as_of` or equivalent point-in-time fields when exposed to show state at a transaction/cutoff. For audit evidence, reconcile its records with onchain logs, deployed addresses, policy snapshots, credential-issuer records, and governance/admin history.

## External Deployments

Do not assume Foundry/self-deployed contracts automatically appear in Platform UI. Visibility generally depends on managed registration, provisioning, or indexing. Check Beta docs or the team's Chainlink contact for external registration, indexing behavior, and required metadata.

## Credential Modes

OSS Cross-Chain Identity supports credential registries and Credential Data Validator patterns. Managed credentials are product-scoped: cite the current official ACE Beta docs at `https://docs.chain.link/ace/beta-scope` before stating attestation-only or any other Beta limit, and do not promise custom data-validator behavior through UI/API. When contrasting the modes, require production OSS BUSL/commercial-license and counsel review, trusted-issuer controls, and credential expiry/revocation handling; separate what OSS contracts can implement from what managed Beta exposes.
