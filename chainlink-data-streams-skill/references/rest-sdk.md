# REST SDK Workflows

Use this for Go, Rust, or TypeScript latest reports, timestamp lookups, bulk lookup, pagination, and backfill. Prefer official SDKs; keep credentials/endpoints in environment variables, use public defaults only from [public-endpoints-and-addresses.md](public-endpoints-and-addresses.md), decode with the matching schema, and preserve `full_report`. Check current package versions and methods at `https://github.com/smartcontractkit/data-streams-sdk`.

## SDK Map

| Language | Package | Client/decoder notes |
|---|---|---|
| Go | `github.com/smartcontractkit/data-streams-sdk/go` | Feed listing, latest, timestamp, pagination, and streams; report packages hold decoders. |
| Rust | `chainlink-data-streams-sdk`; `chainlink-data-streams-report` | REST/WebSocket client plus full-report decoders. |
| TypeScript | `@chainlink/data-streams-sdk` | REST, streaming, automatic decoding, metrics; use currently supported Node.js/TypeScript. |

## Canonical Latest-Report Shape

This runnable Go example shows the shared lifecycle. Rust uses `Config::new(key, secret, restURL, wsURL).build()`, `Client::new(config)`, and `client.get_latest_report(feed_id).await`; TypeScript uses `createClient({apiKey,userSecret,endpoint,wsEndpoint})` and `client.getLatestReport(feedID)`.

```go
package main

import (
    "context"
    "fmt"
    "os"

    streams "github.com/smartcontractkit/data-streams-sdk/go"
    "github.com/smartcontractkit/data-streams-sdk/go/feed"
)

func main() {
    id := &feed.ID{}
    if err := id.FromString(os.Getenv("DATA_STREAMS_FEED_ID")); err != nil { panic(err) }
    client, err := streams.New(streams.Config{
        ApiKey: os.Getenv("DATA_STREAMS_API_KEY"),
        ApiSecret: os.Getenv("DATA_STREAMS_USER_SECRET"),
        RestURL: os.Getenv("DATA_STREAMS_REST_URL"),
        WsURL: os.Getenv("DATA_STREAMS_WS_URL"),
    })
    if err != nil { panic(err) }
    report, err := client.GetLatestReport(context.Background(), *id)
    if err != nil { panic(err) }
    fmt.Println(report.FeedID, report.ObservationsTimestamp, report.ValidFromTimestamp)
}
```

For generated code: validate missing credentials/feed IDs; distinguish unauthorized/entitlement, clock/signature, unknown-feed, retryable 5xx, and schema/decode errors; keep retries simple unless production hardening is requested. Mention onchain verification when reports secure value.

## Use Cases

### Latest

Call the language's latest-report method, decode the full report with its schema decoder, and return feed ID, observations/valid-from timestamps, and decoded values.

### Timestamp lookback

Accept Unix seconds unless current endpoint docs specify otherwise. Call the timestamp report method/endpoint, decode, and return raw timestamps plus human-readable time. Handle not-found or nearest-report behavior exactly as official docs define it—never invent nearest-neighbor semantics.

### Bulk and pagination

Bulk lookup is for multiple feed IDs at one timestamp. Paginated history is for sequential reports from one feed/start time. Persist `nextPageTS` or the language-equivalent cursor in collectors; use this flow for REST backfill after stream reconnects.

Ask only for a missing language, environment, or feed ID required for the next step. If exact behavior matters, consult the REST API docs before generating production code.
