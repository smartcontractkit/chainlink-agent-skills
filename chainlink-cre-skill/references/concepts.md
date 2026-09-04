# Concepts

Use for consensus, finality, determinism, or TypeScript QuickJS/WASM. Capability mechanics live in their own references.

## Consensus and execution modes

A trigger runs the workflow independently on DON nodes; capability/node-mode results are aggregated, and the final output needs BFT agreement (typically `2f+1` of `3f+1`). DON mode must be deterministic. Node mode (`runInNodeMode`) permits per-node I/O/computation, then aggregates the results.

| Aggregation | Meaning | Typical use |
|---|---|---|
| median | middle numeric observation | prices, quantities, timestamps |
| identical | all values agree | strings, booleans, addresses, hashes |
| common prefix/suffix | shared array segment | append-only sequences |
| frequency list | observed values plus counts | categorical results |
| ignore | omit field | node-local noise |

There is no TypeScript `mode` aggregator; use `frequencyList`. Exact SDK constructors are in [sdk-reference.md](sdk-reference.md).

For an HTTP request specifically: each node performs the request independently through an HTTP capability, then CRE aggregates the per-node responses using the rule you choose. If a node returns a materially different response: with **median**, outliers are naturally tolerated as long as enough nodes still produce compatible numeric results; with **identical**, the differing node's value prevents agreement unless the required BFT supermajority still agrees on one exact value; if too many nodes disagree or return incompatible data so the threshold cannot be met, consensus fails and that execution fails for the trigger event rather than producing an untrusted result. Keep post-aggregation workflow logic deterministic, but the disagreement-handling above belongs to the aggregation step itself, not the DON-mode determinism rules below.

## Finality constants

Finality semantics vary by chain. Prefer finalized for high-value reads and decisions that lead to writes; latest trades reorg safety for freshness; avoid pending in production.

TypeScript `EVMClient.callContract` block numbers:

| Value | Level |
|---|---|
| `LAST_FINALIZED_BLOCK_NUMBER` | exported opaque finalized sentinel (default/recommended) |
| `-1n` | latest |
| `-2n` | safe |
| `-3n` | pending |
| positive `bigint` | exact block |

Go generated bindings use `nil` or `big.NewInt(-3)` for finalized and `big.NewInt(-2)` for latest; positive values select an exact block. Low-level Go `CallContract`, `BalanceAt`, and `HeaderByNumber` use `nil`/`-2` for latest and `-3` for finalized. Do not mix the generated-binding and low-level conventions.

Ethereum finalized is roughly 15 minutes behind head and safe roughly 6 minutes; L2 safe/finalized behavior depends on L1 confirmation. Check the target chain rather than assuming these timings.

## Determinism

Use `runtime.now()`/`runtime.Now()` for consensus time and Go `runtime.Rand()` for consensus-safe randomness. TypeScript has no `runtime.rand()`; use deterministic logic or Go. External HTTP/node-mode data must be aggregated.

Avoid in DON mode:

- Go map iteration without sorted keys; goroutines/channels; `time.Now()`; global `math/rand`; `crypto/rand`
- TypeScript `Date.now()`, `new Date()`, `Math.random()`, `Promise.race`, `Promise.any`, or order-dependent mixed numeric/string object keys
- free-form values whose nondeterministic formatting enters consensus

Safe pattern: sort Go keys (`sort.Strings` over the collected map keys before iterating), resolve capability calls in a deterministic order, use scaled integers/decimal strings for business comparisons, and use `bigint` for Solidity integers. The CRE Go SDK core package is `github.com/smartcontractkit/cre-sdk-go/cre` — `runtime cre.Runtime` supplies `Now()`/`Rand()`; never import `chainlink-evm/pkg/cre` or any other path for it. These determinism rules apply only when logic in the DON path actually needs them; do not lead with them when the user's question is about HTTP/capability consensus behavior, which the table above owns.

## TypeScript WASM runtime

Compilation is TypeScript → JavaScript (Bun) → WASM (Javy embedding QuickJS). It is synchronous and sandboxed:

- capability handles resolve with `.result()`, not `await`
- no top-level async capability execution, Node.js APIs, or browser timers/WebSockets/XHR
- CRE-provided HTTP APIs are not Node/browser `fetch`
- WASM binary size and memory are limited; check service quotas and move large processing behind an API

Unsupported Node APIs: `fs`, `path`, `crypto`, `process`, `http`, `https`, `net`, `stream`, `child_process`, `os`, `worker_threads`, `cluster`, `dgram`, `dns`, `tls`, `vm`, `zlib`, `readline`, Node-specific `events`, `util`, and `buffer`. Use `Uint8Array`/`ArrayBuffer`, not `Buffer`.

Pure-JS packages without native modules or Node imports may work. Known compatible: `zod`, `viem`. Known incompatible: `ethers` (Node crypto), `axios` (HTTP), `node-fetch`, `ws`, `dotenv`, and native/N-API modules. Inspect dependency imports and confirm in simulation; compatibility reference: `https://sebastianwessel.github.io/quickjs/docs/module-resolution/node-compatibility.html`.

Response/capability code appears synchronous:

```typescript
const response = httpClient.sendRequest(runtime, fetchFn, aggregation)(url).result()
const body = json(response)
```

Use `runtime.log()` only for non-sensitive diagnostics. Compilation/schema failures appear during simulation.

## Sources

- https://docs.chain.link/cre/concepts/consensus-computing.md
- https://docs.chain.link/cre/concepts/finality-ts.md
- https://docs.chain.link/cre/concepts/finality-go.md
- https://docs.chain.link/cre/concepts/non-determinism-ts.md
- https://docs.chain.link/cre/concepts/non-determinism-go.md
- https://docs.chain.link/cre/concepts/typescript-wasm-runtime.md
