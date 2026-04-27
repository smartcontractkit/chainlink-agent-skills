# WebSocket SDK Workflows

Use this file when the user wants real-time Data Streams reports over WebSocket, including High Availability mode.

## Default Path

1. Prefer the official SDK for Go, Rust, or TypeScript.
2. Keep Data Streams credentials server-side.
3. Decode reports with the official report decoder for the schema version.
4. Backfill missed reports with REST if the application needs a complete time series.
5. Expose metrics or logs for connection state, reconnects, and deduplication when generating long-running services.

For default WebSocket endpoint domains, read [public-endpoints-and-addresses.md](public-endpoints-and-addresses.md). Keep endpoints configurable because HA support and environment availability can change.

## Standard Streaming

Standard streaming is appropriate for:

- development and testnet prototypes
- simple backend consumers
- cases where occasional reconnects can be tolerated

Expected generated flow:

1. build SDK client config from environment variables
2. subscribe to one or more feed IDs
3. handle report events or blocking reads
4. decode the full report
5. store or forward the decoded data
6. close the stream cleanly on shutdown

Minimal Go stream:

```go
// Function-body fragment. Required imports: context, fmt, os,
// github.com/smartcontractkit/data-streams-sdk/go, and
// github.com/smartcontractkit/data-streams-sdk/go/feed.
feedID := &feed.ID{}
if err := feedID.FromString(os.Getenv("DATA_STREAMS_FEED_ID")); err != nil {
	panic(err)
}

client, err := streams.New(streams.Config{
	ApiKey:    os.Getenv("DATA_STREAMS_API_KEY"),
	ApiSecret: os.Getenv("DATA_STREAMS_USER_SECRET"),
	RestURL:   os.Getenv("DATA_STREAMS_REST_URL"),
	WsURL:     os.Getenv("DATA_STREAMS_WS_URL"),
	WsHA:      false,
})
if err != nil {
	panic(err)
}

ctx := context.Background()
stream, err := client.Stream(ctx, []feed.ID{*feedID})
if err != nil {
	panic(err)
}
defer stream.Close()

report, err := stream.Read(ctx)
if err != nil {
	panic(err)
}
fmt.Println(report.FeedID, report.ObservationsTimestamp)
```

Minimal Rust stream:

```rust
// Function-body fragment. Required imports: ID, Config, Stream.
let feed_id = ID::from_hex_str(&std::env::var("DATA_STREAMS_FEED_ID")?)?;
let config = Config::new(
    std::env::var("DATA_STREAMS_API_KEY")?,
    std::env::var("DATA_STREAMS_USER_SECRET")?,
    std::env::var("DATA_STREAMS_REST_URL")?,
    std::env::var("DATA_STREAMS_WS_URL")?,
)
.build()?;

let mut stream = Stream::new(&config, vec![feed_id]).await?;
stream.listen().await?;
let response = stream.read().await?;
println!(
    "{} {}",
    response.report.feed_id.to_hex_string(),
    response.report.observations_timestamp
);
stream.close().await?;
```

Minimal TypeScript stream:

```typescript
import { createClient } from "@chainlink/data-streams-sdk";

const client = createClient({
  apiKey: process.env.DATA_STREAMS_API_KEY!,
  userSecret: process.env.DATA_STREAMS_USER_SECRET!,
  endpoint: process.env.DATA_STREAMS_REST_URL!,
  wsEndpoint: process.env.DATA_STREAMS_WS_URL!,
  haMode: false,
});

const stream = client.createStream([process.env.DATA_STREAMS_FEED_ID!]);
stream.on("report", report => {
  console.log(report.feedID, report.observationsTimestamp);
});
stream.on("error", error => {
  console.error(error.message);
});
await stream.connect();
```

## High Availability Mode

HA mode is appropriate for production-style consumers that need lower risk of report gaps.

Current docs describe HA as using multiple simultaneous WebSocket connections with origin discovery, automatic failover, report deduplication, and per-connection monitoring. The TypeScript SDK docs currently state HA mode is mainnet-only, so verify current docs before enabling it in generated code.

Expected HA behavior:

- enable the SDK's HA option for the target language
- deduplicate reports before storage or downstream publishing
- track accepted, received, deduplicated, reconnect, and active-connection metrics when the SDK exposes them
- backfill with REST after reconnects if gaps matter

Minimal Go HA stream:

```go
feedID := &feed.ID{}
if err := feedID.FromString(os.Getenv("DATA_STREAMS_FEED_ID")); err != nil {
	panic(err)
}

client, err := streams.New(streams.Config{
	ApiKey:    os.Getenv("DATA_STREAMS_API_KEY"),
	ApiSecret: os.Getenv("DATA_STREAMS_USER_SECRET"),
	RestURL:   os.Getenv("DATA_STREAMS_REST_URL"),
	WsURL:     os.Getenv("DATA_STREAMS_WS_URL"),
	WsHA:      true,
})
if err != nil {
	panic(err)
}

stream, err := client.Stream(context.Background(), []feed.ID{*feedID})
if err != nil {
	panic(err)
}
defer stream.Close()

report, err := stream.Read(context.Background())
if err != nil {
	panic(err)
}
fmt.Println(report.FeedID, stream.Stats())
```

Minimal Rust HA stream:

```rust
use chainlink_data_streams_sdk::config::WebSocketHighAvailability;

let feed_id = ID::from_hex_str(&std::env::var("DATA_STREAMS_FEED_ID")?)?;
let config = Config::new(
    std::env::var("DATA_STREAMS_API_KEY")?,
    std::env::var("DATA_STREAMS_USER_SECRET")?,
    std::env::var("DATA_STREAMS_REST_URL")?,
    std::env::var("DATA_STREAMS_WS_URL")?,
)
.with_ws_ha(WebSocketHighAvailability::Enabled)
.build()?;

let mut stream = Stream::new(&config, vec![feed_id]).await?;
stream.listen().await?;
let response = stream.read().await?;
println!("{} {:?}", response.report.feed_id.to_hex_string(), stream.get_stats());
stream.close().await?;
```

Minimal TypeScript HA stream:

```typescript
const client = createClient({
  apiKey: process.env.DATA_STREAMS_API_KEY!,
  userSecret: process.env.DATA_STREAMS_USER_SECRET!,
  endpoint: process.env.DATA_STREAMS_REST_URL!,
  wsEndpoint: process.env.DATA_STREAMS_WS_URL!,
  haMode: true,
});

const stream = client.createStream([process.env.DATA_STREAMS_FEED_ID!], {
  maxReconnectAttempts: 10,
  reconnectInterval: 3000,
});

stream.on("report", report => console.log(report.feedID, report.observationsTimestamp));
stream.on("error", error => console.error(error.message));
await stream.connect();
```

## Language Notes

Go:
- `Config` includes REST URL, WebSocket URL, `WsHA`, reconnect settings, debug logging, and optional HTTP inspection.
- `Stream` exposes read, stats, and close behavior.

Rust:
- Use `chainlink-data-streams-sdk` for stream clients.
- Use `chainlink-data-streams-report` for decoding.
- The SDK repository includes examples for simple WebSocket streams and multiple streams in HA mode.

TypeScript:
- Use `@chainlink/data-streams-sdk`.
- Create streams from feed IDs and listen for report/error events.
- Use `haMode: true` only after verifying the target environment supports it.

## Failure Handling

Generated services should handle:

- authentication failures
- feed entitlement failures
- disconnects and reconnects
- duplicate reports in HA mode
- decode mismatch
- process shutdown

Avoid browser-direct WebSocket connections to Data Streams unless the docs explicitly support a safe browser credential model. Use a backend proxy for browser UIs.
