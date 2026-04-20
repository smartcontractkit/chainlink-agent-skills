# Concepts

Use this file when the user asks about consensus computing, finality levels, non-determinism pitfalls, or the TypeScript WASM runtime.

## Trigger Conditions

- "How does CRE consensus work?"
- "What finality levels are available?"
- "Why does my workflow fail with non-determinism errors?"
- "How does the TypeScript WASM runtime work?"

Do not use for specific capability usage (see evm-client.md, http-client.md), workflow code patterns (see workflow-patterns.md), or CLI commands (see cli-reference.md).

## Consensus Computing

### Overview

CRE workflows run on a Decentralized Oracle Network (DON) consisting of multiple independent nodes. For a workflow result to be accepted, nodes must reach consensus (agreement) on the output.

### How It Works

1. A trigger event fires (cron tick, HTTP request, EVM log)
2. Each node in the DON executes the workflow independently
3. For capability calls (HTTP, EVM), results from individual nodes are aggregated
4. The aggregated result is used in subsequent workflow steps
5. The final output must achieve BFT (Byzantine Fault Tolerance) consensus

### Execution Modes

#### DON Mode (Default)

- Code runs on all nodes simultaneously
- All operations must be deterministic
- External data is fetched via capabilities with consensus aggregation
- `runtime.now()`, `runtime.Rand()` provide consensus-safe values

#### Node Mode

- Code runs on each node independently inside `runInNodeMode`
- Can perform non-deterministic operations (HTTP fetches, secret access)
- Results are aggregated afterward using the specified consensus method
- Used for operations that inherently produce different results per node

### Aggregation Methods

| Method | Description | Use Case |
|--------|-------------|----------|
| `median` | Takes the median of numeric values across nodes | Prices, quantities, timestamps |
| `identical` | Requires all nodes to return the exact same value | Strings, booleans, addresses, hashes |
| `mode` | Takes the most common value across nodes | Categorical data, status codes |

### BFT Threshold

Consensus requires agreement from a supermajority of nodes (typically 2f+1 out of 3f+1 nodes, where f is the maximum number of faulty nodes). If consensus cannot be reached, the workflow execution fails for that trigger event.

## Finality Levels

When reading from the blockchain, CRE supports different finality guarantees:

| Level | Block Number Value | Description | Risk |
|-------|-------------------|-------------|------|
| Finalized | `0n` / `big.NewInt(0)` | Block is finalized and irreversible | Lowest |
| Safe | `-2n` / `big.NewInt(-2)` | Block is safe from reorgs (L2 specific) | Low |
| Latest | `-1n` / `big.NewInt(-1)` | Most recent known block | Medium (subject to reorg) |
| Pending | `-3n` / `big.NewInt(-3)` | Pending block (includes mempool txs) | Highest |

### Recommendations

- Use **Finalized** (`0n`) for high-value operations and writes based on read data
- Use **Latest** (`-1n`) for time-sensitive reads where slight reorg risk is acceptable
- Avoid **Pending** in production workflows

### Chain-Specific Behavior

Finality semantics vary by chain:
- **Ethereum**: Finalized = ~15 minutes behind head; Safe = ~6 minutes
- **L2s (Arbitrum, Base, Optimism)**: Finality depends on L1 confirmation; Safe varies by chain
- Always check the target chain's finality characteristics

## Non-Determinism Pitfalls

### Why Non-Determinism Matters

In DON mode, all nodes must produce the same result. Non-deterministic code causes consensus failures because different nodes produce different outputs.

### Common Pitfalls in Go

#### Map Iteration Order

Go maps have random iteration order. Never iterate over a map directly when order affects the output:

```go
// WRONG: map iteration order is non-deterministic
for k, v := range myMap {
    result += fmt.Sprintf("%s=%s,", k, v)
}

// CORRECT: sort keys first
keys := make([]string, 0, len(myMap))
for k := range myMap {
    keys = append(keys, k)
}
sort.Strings(keys)
for _, k := range keys {
    result += fmt.Sprintf("%s=%s,", k, myMap[k])
}
```

#### System Clock

```go
// WRONG: different on each node
now := time.Now()

// CORRECT: consensus-derived time
now := runtime.Now()
```

#### Random Numbers

```go
// WRONG: different on each node
n := rand.Intn(100)

// CORRECT: consensus-safe random
r, _ := runtime.Rand()
n := r.Intn(100)
```

#### Goroutines and Channels

Do not use goroutines or channels in DON mode. CRE workflows are single-threaded. Goroutines introduce non-deterministic scheduling.

### Common Pitfalls in TypeScript

#### System Clock

```typescript
// WRONG: different on each node
const now = Date.now()
const date = new Date()

// CORRECT: consensus-derived time
const now = runtime.now()
```

#### Promise.race / Promise.any

```typescript
// WRONG: winner is non-deterministic
const result = await Promise.race([fetch1(), fetch2()])

// CORRECT: fetch sequentially or use sendRequest with aggregation
const result1 = httpClient.sendRequest(runtime, fetch1, agg)(url1).result()
const result2 = httpClient.sendRequest(runtime, fetch2, agg)(url2).result()
```

#### Unordered Object Keys

Object key order in JavaScript is mostly deterministic for string keys, but avoid relying on insertion order for mixed key types (numeric + string).

#### Math.random()

```typescript
// WRONG: non-deterministic
const n = Math.random()

// There is no runtime.rand() in TypeScript yet
// Use deterministic logic or compute randomness in Go workflows
```

### Safe Patterns

| Operation | Safe Alternative |
|-----------|-----------------|
| Current time | `runtime.now()` / `runtime.Now()` |
| Random numbers | `runtime.Rand()` (Go only) |
| Map iteration | Sort keys first |
| External HTTP | Use `sendRequest` or `runInNodeMode` with aggregation |
| Secrets | `runtime.getSecret()` / `runtime.GetSecret()` |

## TypeScript WASM Runtime

### Overview

TypeScript CRE workflows compile to WebAssembly (WASM) via a two-stage process:

1. **TypeScript -> JavaScript**: Transpiled by Bun
2. **JavaScript -> WASM**: Compiled by Javy (which embeds QuickJS)

### QuickJS Engine

The WASM runtime uses QuickJS, a lightweight JavaScript engine. Key differences from V8/Node.js:

- **No async/await at top level**: The WASM environment is synchronous. The `.result()` pattern replaces `await`.
- **No Node.js APIs**: No `fs`, `path`, `crypto`, `process`, etc.
- **No Web APIs**: No `setTimeout`, `setInterval`, `XMLHttpRequest`, `WebSocket`
- **Limited `fetch`**: The `fetch` function is provided by the CRE runtime, not by the browser or Node.js. It is synchronous within the WASM context.

### The .result() Pattern Explained

Standard JavaScript:

```javascript
const response = await fetch(url)
const data = await response.json()
```

CRE TypeScript:

```typescript
const response = fetch(url)
const data = response.json()
```

In the CRE WASM environment, `fetch` and capability calls appear synchronous. The `.result()` method on capability objects explicitly waits for consensus resolution:

```typescript
const data = httpClient.sendRequest(runtime, fetchFn, agg)(url).result()
```

### Memory and Size Limits

- WASM binary size is limited (check service quotas)
- Memory is limited within the WASM sandbox
- Large data processing should be done offchain or via HTTP APIs

### Supported npm Packages

Packages that are pure JavaScript and don't rely on Node.js APIs or native modules generally work. Before adding any third-party npm package to a CRE TypeScript workflow, verify it does not depend on unsupported Node.js APIs.

**Unsupported Node.js APIs in QuickJS:**
`fs`, `path`, `crypto`, `process`, `http`, `https`, `net`, `stream`, `child_process`, `os`, `worker_threads`, `cluster`, `dgram`, `dns`, `tls`, `vm`, `zlib`, `readline`, `events` (Node.js-specific EventEmitter), `util` (Node.js-specific features like `promisify`), `buffer` (Node.js Buffer; use `ArrayBuffer`/`Uint8Array` instead)

**How to check compatibility:**
1. Review the package's `package.json` for Node.js-specific dependencies
2. Check if the package imports any of the unsupported APIs listed above
3. Consult the QuickJS Node.js compatibility reference: https://sebastianwessel.github.io/quickjs/docs/module-resolution/node-compatibility.html
4. Test with `cre workflow simulate` to confirm the package works in the WASM runtime

**Known compatible packages:**
- `zod` (schema validation)
- `viem` (Ethereum ABI encoding/decoding, type utilities)

**Known incompatible packages:**
- `ethers` (depends on Node.js `crypto`)
- `axios` (depends on Node.js `http`/`https`)
- `node-fetch` (depends on Node.js `http`/`stream`)
- `ws` (depends on Node.js `net`/`http`)
- `dotenv` (depends on Node.js `fs`/`path`)
- Any package requiring native/N-API modules

### Debugging

- Use `runtime.log()` for logging; output appears in simulation
- Schema validation errors from `zod` provide detailed messages
- Compilation errors appear during the `cre workflow simulate` step

## Official Documentation

- Consensus computing: `https://docs.chain.link/cre/concepts/consensus-computing`
- Finality: `https://docs.chain.link/cre/concepts/finality`
- Non-determinism: `https://docs.chain.link/cre/concepts/non-determinism`
