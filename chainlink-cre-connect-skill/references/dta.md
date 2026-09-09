# DTA Extension

Read this file only when the user is integrating Digital Transfer Agent contracts through CRE Connect.

## Boundary

The DTA extension packages CRE Connect integration for DTA Request Management and Request Settlement contracts. It does not replace the DTA technical standard. Use the standard for roles, contract architecture, request lifecycle, and payment/settlement models:

`https://docs.chain.link/dta-technical-standard.md`

Use a core ABI-backed CRE Connect watcher instead when the contracts are not DTA.

## Published Extension Shape

The public source describes three surfaces:

- typed Operation builders for the DTA contracts' public actions
- decoded typed values plus one event decode dispatcher
- a service-backed watcher bundle that owns the relevant ABIs

The service name shown in the source is `dta.v2`. Contract ABI versions (`v1`, `v2`, and so on) are separate from the extension package's semantic version; the published CRE Connect material focuses on DTA v2.

The source is conceptual and publishes no package path, import, function signature, endpoint, or client construction. Require the provisioned extension/client documentation before writing runnable integration code.

## Operation Families

| Family | Scope |
| --- | --- |
| Subscriptions and redemptions | Requests, optional ERC-20 approval, distributor processing, and completion. |
| Fund and distributor management | Fund-admin onboarding, fund-token registration/enabling, distributor registration, and token-level authorization/revocation. |
| Cross-DTA settlement | Peer-DTA allow/disallow and settlement-contract ownership changes. |
| Operational | CCIP gas-limit configuration and token withdrawals from Request Management or Request Settlement. |

Every built action still follows the core CRE Connect rules: sign the Operation, submit through the provisioned product interface, and consume the resulting verifiable events. Extension-built and raw calls can share one Operation when they must be atomic; separate them when independent partial success is required.

## Watchers and Events

Provisioning conceptually requires a chain, DTA contract address, and selected event names. The published examples include:

- `SubscriptionRequested`
- `RedemptionRequested`
- `DistributorRequestProcessing`
- `DistributorRequestProcessed`

CRE Connect owns the DTA ABI for service-backed watchers. The application receives the standard verifiable envelope, verifies it locally, then decodes the DTA payload with the provisioned extension. Apply confidence/finality independently of proof verification before side effects.

## Integration Checklist

1. Confirm the deployed DTA contract version and choose the matching extension ABI version.
2. Identify Request Management versus Request Settlement roles and addresses from the DTA deployment.
3. Select only the needed operation family and events.
4. Obtain the provisioned client/extension types instead of guessing names.
5. Apply the core Operation preflight, asset/allowance checks, atomicity rule, event verification, and finality rule.

## Sources

- `https://docs.chain.link/crec/concepts/extensions.md`
- `https://docs.chain.link/crec/extensions.md`
- `https://docs.chain.link/crec/extensions/dta.md`
- `https://docs.chain.link/dta-technical-standard.md`
