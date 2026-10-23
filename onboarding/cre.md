Help me get set up with Chainlink CRE (Chainlink Runtime Environment). I'm starting from an empty directory with nothing CRE-related installed. Do the following, in order, and don't skip verification steps:

1. Install the Chainlink CRE agent skill into this project directory (not globally): "npx skills add smartcontractkit/chainlink-agent-skills --skill chainlink-cre-skill". Then load it and treat it and the official CRE template repos as the source of truth for everything that follows: CLI commands, flags, project structure, code, and minimum toolchain versions. Don't invent APIs, addresses, or flags, and don't rely on memorized version numbers.

2. Install the CRE CLI for my OS following the skill's install instructions, then confirm it works with "cre version". If it's already installed, run "cre update" to make sure it's current.

3. Get me logged in. Run "cre whoami" to check. If I'm not logged in, first determine whether my browser can complete the login callback ("http://localhost:53682/callback") on the machine running the CLI. It may not if you're running in a remote sandbox, container, or SSH session. If it can't, tell me and stop: I can instead set "CRE_API_KEY" in the environment that launches you (requires Early Access; never ask me to paste it into chat). Otherwise run "cre login" — it will open a browser. If I don't have a CRE account yet, tell me I can create one from that same sign-in page. You can't do the password/2FA part, so tell me exactly what to do in the browser, then WAIT for me to say I'm done — do not move on, keep this same session going. "cre login" terminates after 500 seconds, so keep track of your progress while waiting, and if the command exits or expires before I confirm, restart it and tell me. Once I confirm, verify with "cre whoami" and show me the output. If it fails, help me retry before continuing.

4. Verify the toolchain for my chosen language (from Step 5) against the skill's documented minimum versions (Bun for TypeScript, Go for Go), and install/upgrade if missing. Tell me clearly if anything's missing before we continue.

5. Ask me what to build, all in ONE batched message:
   - Language: TypeScript (recommended, most common) or Go. Assume TypeScript if I don't care.
   - Path: fastest path (a starter workflow I can simulate in ~5 minutes), or do I already have a use case?
   - Only if I choose my own use case: which chain(s), data source(s), and trigger type (cron, HTTP, EVM log) I want. If I want a use case but don't have one, offer these areas so I can pick: DeFi Vault Operations (scheduled/event-driven reads + transactions), Tokenized Asset Operations (stablecoin/RWA reserves, compliance, distributions), Custom Oracles & Data Feeds (anomaly detection, pause/reroute), Cross-Chain Coordination (read any chain, write via CCIP), Prediction Markets (resolve markets from Chainlink feeds or external data with signed reports), or something else I describe.

   If I pick the fastest path, ask nothing further: go straight to Step 6 with the hello-world template for my language. Otherwise, ask follow-ups only for genuinely blocking ambiguity (trigger type, network, capability). Don't write code until those are resolved.

6. Scaffold and prove it works:
   - Scaffold with "cre init" using its non-interactive flags and the template matching my language (check "cre templates list --json" if unsure). If the template needs RPC URLs, use a well-known public endpoint unless I give you one.
   - Finish setup (dependencies, WASM tooling) exactly as the skill describes.
   - If I chose my own use case, implement the workflow on top of the scaffold: my trigger, data sources, and any onchain reads/writes, following the skill's patterns.
   - Run "cre workflow simulate <workflow-dir> --target staging-settings --non-interactive --trigger-index 0" (use the index of the handler you want to run if my workflow has more than one) and iterate until it passes. Done means: I see the simulation output including my workflow's log line. Show it to me.

7. After the simulation works, suggest relevant next steps based on what I built: if I took the fastest path, offer to evolve the starter toward one of the use-case areas above (fetch offchain data, read/write onchain) so it doesn't end at hello-world. Then explain that deployment requires CRE Early Access approval, and walk me through requesting it with "cre account access" (verify its exact usage with "cre account access --help" first). Do NOT deploy, activate, or upload anything.
