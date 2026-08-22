# Chainlink Developer Agent Skills

Official Repo for Chainlink coding skills. Each skill follows the [Agent Skills specification](https://agentskills.io/specification).

## Available Skills

| Skill                                                         | Description                                                                                           |
| ------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------- |
| [chainlink-cre-skill](chainlink-cre-skill/)                   | CRE onboarding, workflow generation, CLI/SDK help, and runtime operations                             |
| [chainlink-ccip-skill](chainlink-ccip-skill/)                 | CCIP sends, contracts, local testing, monitoring, discovery, and CCT workflows                        |
| [chainlink-data-feeds-skill](chainlink-data-feeds-skill/)     | Data Feeds contracts, multi-chain Data Feeds integration                                              |
| [chainlink-data-streams-skill](chainlink-data-streams-skill/) | Data Streams REST/WebSocket SDKs, report decoding, on-chain verification, and real-time frontend apps |
| [chainlink-ace-skill](chainlink-ace-skill/)                   | ACE core contracts, Policy Management, Cross-Chain Identity, and compliance token examples            |
| [chainlink-vrf-skill](chainlink-vrf-skill/)                   | VRF v2.5 subscription and direct-funding consumers, migration from V2, billing, and network addresses |

## Install

### Cursor Marketplace

These skills are published as Cursor plugins. Install from the [Cursor Marketplace](https://cursor.com/marketplace) (search for "Chainlink") or install individual plugins after listing:

| Plugin | Description |
| ------ | ----------- |
| chainlink-cre-skill | CRE workflows, CLI/SDK, triggers, simulation, deployment |
| chainlink-ccip-skill | CCIP cross-chain transfers, messaging, contracts, CCT |
| chainlink-data-feeds-skill | Data Feeds integration across EVM and non-EVM chains |
| chainlink-data-streams-skill | Data Streams SDKs, report decoding, WebSocket HA |
| chainlink-ace-skill | ACE compliance, policies, Cross-Chain Identity |
| chainlink-vrf-skill | VRF v2.5 consumers, billing, network addresses |

**Test locally before publishing:** symlink a plugin into Cursor's local plugins folder, then reload the window:

```bash
ln -s "$(pwd)/chainlink-cre-skill" ~/.cursor/plugins/local/chainlink-cre-skill
```

**Submit for listing:** open [cursor.com/marketplace/publish](https://cursor.com/marketplace/publish) and submit `https://github.com/smartcontractkit/chainlink-agent-skills`. Cursor manually reviews every plugin before it appears in the marketplace.

### Open skills CLI

Use [vercel's CLI for the open skills ecosystem](https://github.com/vercel-labs/skills#readme). Project-level installation is the default.

```bash
npx skills add smartcontractkit/chainlink-agent-skills
```

<p align="center">
<img width="75%" alt="npx skills add smartcontractkit/chainlink-agent-skills" src="https://github.com/user-attachments/assets/2f4fbecb-be53-47d6-9f5a-7cb32979eb72" />
</p>

But if you want to install globally (at the user level) then add the `-g` flag.

Note the use of `--skill` to specify which specific skill to install.

```bash
npx skills add smartcontractkit/chainlink-agent-skills --skill chainlink-cre-skill -g
npx skills add smartcontractkit/chainlink-agent-skills --skill chainlink-ccip-skill -g
npx skills add smartcontractkit/chainlink-agent-skills --skill chainlink-data-feeds-skill -g
npx skills add smartcontractkit/chainlink-agent-skills --skill chainlink-data-streams-skill -g
npx skills add smartcontractkit/chainlink-agent-skills --skill chainlink-ace-skill -g
npx skills add smartcontractkit/chainlink-agent-skills --skill chainlink-vrf-skill -g
```

## Use

When your agent supports Agent Skills, it will discover and activate these skills based on the task. **However** we recommend that you explicitly invoke the skill in your agent chat sessions as follows:


```text
Using /chainlink-data-feeds-skill, /chainlink-cre-skill, and /chainlink-ccip-skill, 
build a tokenized fund project that:

- delivers data (NAV, yields and ESG attestations) securely on-chain
- mints fund tokens representing shares in a tokenized investment fund
- uses Chainlink Proof of Reserve by CRE for real-time verification of reserved assets
- can be traded and settled seamlessly across multiple public and private chains
- has a clean, modern UI dashboard

Create a development plan. Include steps for testing on testnets. 
Make sure README has instructions on how to run local CRE simulations and 
how to monitor status of cross-chain transfers using the CCIP CLI.

Any questions before you start?
```
