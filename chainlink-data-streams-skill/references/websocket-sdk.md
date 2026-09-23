# WebSocket SDK Workflows

Use this for Go, Rust, or TypeScript real-time streams, including HA. Generate with the official SDK, server-side environment credentials, matching decoder, and configurable [endpoints](public-endpoints-and-addresses.md). Default an omitted language to TypeScript; deliver the streamer rather than only asking.

## One Stream Lifecycle

Every generated streamer must implement this lifecycle; HA adds origin discovery, simultaneous connections, failover, deduplication, and per-connection monitoring:

1. Build config from `DATA_STREAMS_API_KEY`, `DATA_STREAMS_USER_SECRET`, `DATA_STREAMS_REST_URL`, and `DATA_STREAMS_WS_URL`.
2. Parse one or more feed IDs; select standard or verified-supported HA mode.
3. Connect/listen, read report events, and decode `full_report` with its official schema decoder.
4. Deduplicate before storage/publishing; log/measure connection state, accepted, received, deduplicated, reconnect, and active-connection counts when exposed.
5. After each reconnect, REST-backfill from last accepted `observationsTimestamp` via [paginated history](rest-sdk.md) (`/api/v1/reports/page` cursor); never infer gaps from live timestamp jumps.
6. On authentication, entitlement, disconnect, decode, or process-shutdown events, handle the error and close cleanly.

Canonical TypeScript lifecycle (standard by default; set `DATA_STREAMS_HA=true` only after the checks below):

```typescript
import { createClient } from "@chainlink/data-streams-sdk";

const haMode = process.env.DATA_STREAMS_HA === "true";
const client = createClient({
  apiKey: process.env.DATA_STREAMS_API_KEY!,
  userSecret: process.env.DATA_STREAMS_USER_SECRET!,
  endpoint: process.env.DATA_STREAMS_REST_URL!,
  wsEndpoint: process.env.DATA_STREAMS_WS_URL!,
  haMode,
});
const stream = client.createStream([process.env.DATA_STREAMS_FEED_ID!]);
stream.on("report", report => {
  console.log(report.feedID, report.observationsTimestamp);
});
stream.on("error", error => console.error(error.message));
await stream.connect();
```

## Language and HA Deltas

Verify current SDK methods and the target environment before generation or enabling HA. Treat TypeScript HA's documented mainnet-only note as a freshness-sensitive caveat to re-check, not a hard fact.

| Language | SDK and standard lifecycle | HA option and metrics |
|---|---|---|
| Go | `github.com/smartcontractkit/data-streams-sdk/go`; `streams.New(Config)` → `client.Stream(ctx, []feed.ID)` → `stream.Read(ctx)` → `stream.Close()` | `WsHA: true` (`false` for standard); `Config` also has reconnect, debug, and optional HTTP-inspection settings; inspect `stream.Stats()` |
| Rust | `chainlink-data-streams-sdk` client plus `chainlink-data-streams-report` decoder; `Stream::new(&config, vec![feed_id])` → `listen().await` → `read().await` → `close().await` | `.with_ws_ha(WebSocketHighAvailability::Enabled)`; inspect `stream.get_stats()`; repository examples cover simple and multi-stream HA |
| TypeScript | `@chainlink/data-streams-sdk`; `createClient` → `createStream(feedIDs)` → report/error listeners → `connect()` | `haMode: true` (`false` for standard); re-check the documented network caveat; use exposed metrics/events |

Go config fields are `ApiKey`, `ApiSecret`, `RestURL`, `WsURL`, and `WsHA`; parse IDs with `feed.ID.FromString`. Rust uses `Config::new(apiKey, secret, restURL, wsURL).build()` and `ID::from_hex_str`. TypeScript config uses `apiKey`, `userSecret`, `endpoint`, `wsEndpoint`, and `haMode`.

Never connect from a browser; proxy sanitized reports from a credentialed backend.
