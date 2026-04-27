# REST SDK Workflows

Use this file when the user wants Go, Rust, or TypeScript code to fetch Data Streams reports through REST, including latest reports, timestamp lookups, bulk lookups, or paginated history.

## Default Path

1. Prefer the official SDK for the requested language.
2. Ask one focused question if the user has not provided language, environment, or feed IDs and the answer depends on them.
3. Use placeholders for credentials and keep endpoint values configurable. If the user asks for public defaults, use [public-endpoints-and-addresses.md](public-endpoints-and-addresses.md).
4. Keep generated code secret-safe and runnable.
5. Add a short note about onchain verification when the report will secure value.

## Official SDKs

Go:
- Package: `github.com/smartcontractkit/data-streams-sdk/go`
- Client methods include feed listing, latest report, timestamp report lookup, paginated reports, and streams.
- Report decoding uses the report packages under the SDK repository.

Rust:
- Crates: `chainlink-data-streams-sdk` and `chainlink-data-streams-report`
- Supports REST and WebSocket clients.
- Use `chainlink_data_streams_report` decoders for full reports.

TypeScript:
- Package: `@chainlink/data-streams-sdk`
- Supports REST, real-time streaming, automatic report decoding, and metrics.
- Requires Node.js and TypeScript versions compatible with the current SDK docs.

Always check the SDK repository for current package versions and method names before generating production-ready code.

## Public REST Endpoint Defaults

For default REST endpoint domains, read [public-endpoints-and-addresses.md](public-endpoints-and-addresses.md). The local fallback is useful for prototypes and examples, but production code should still keep endpoints in environment variables.

## REST Use Cases

### Latest report

Use when the user wants the newest report for a feed ID.

Expected implementation:

1. configure SDK client with API key, user secret, REST URL, and WebSocket URL if required by the SDK config
2. call the language-specific latest-report method
3. decode the full report with the matching schema decoder
4. print or return feed ID, observations timestamp, valid-from timestamp, and decoded fields

Minimal Go client:

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
	feedID := &feed.ID{}
	if err := feedID.FromString(os.Getenv("DATA_STREAMS_FEED_ID")); err != nil {
		panic(err)
	}

	client, err := streams.New(streams.Config{
		ApiKey:    os.Getenv("DATA_STREAMS_API_KEY"),
		ApiSecret: os.Getenv("DATA_STREAMS_USER_SECRET"),
		RestURL:   os.Getenv("DATA_STREAMS_REST_URL"),
		WsURL:     os.Getenv("DATA_STREAMS_WS_URL"),
	})
	if err != nil {
		panic(err)
	}

	report, err := client.GetLatestReport(context.Background(), *feedID)
	if err != nil {
		panic(err)
	}
	fmt.Println(report.FeedID, report.ObservationsTimestamp, report.ValidFromTimestamp)
}
```

Minimal Rust client:

```rust
use chainlink_data_streams_report::feed_id::ID;
use chainlink_data_streams_sdk::client::Client;
use chainlink_data_streams_sdk::config::Config;
use std::{env, error::Error};

#[tokio::main]
async fn main() -> Result<(), Box<dyn Error>> {
    let feed_id = ID::from_hex_str(&env::var("DATA_STREAMS_FEED_ID")?)?;
    let config = Config::new(
        env::var("DATA_STREAMS_API_KEY")?,
        env::var("DATA_STREAMS_USER_SECRET")?,
        env::var("DATA_STREAMS_REST_URL")?,
        env::var("DATA_STREAMS_WS_URL")?,
    )
    .build()?;

    let client = Client::new(config)?;
    let response = client.get_latest_report(feed_id).await?;
    let report = response.report;
    println!(
        "{} {} {}",
        report.feed_id.to_hex_string(),
        report.observations_timestamp,
        report.valid_from_timestamp
    );
    Ok(())
}
```

Minimal TypeScript client:

```typescript
import { createClient } from "@chainlink/data-streams-sdk";

const client = createClient({
  apiKey: process.env.DATA_STREAMS_API_KEY!,
  userSecret: process.env.DATA_STREAMS_USER_SECRET!,
  endpoint: process.env.DATA_STREAMS_REST_URL!,
  wsEndpoint: process.env.DATA_STREAMS_WS_URL!,
});

const report = await client.getLatestReport(process.env.DATA_STREAMS_FEED_ID!);
console.log(report.feedID, report.observationsTimestamp, report.validFromTimestamp);
```

### Timestamp lookback

Use when the user asks for the price at a UNIX timestamp.

Expected implementation:

1. accept a UNIX timestamp in seconds unless the docs say otherwise for the endpoint
2. call the REST endpoint or SDK method for a report at that timestamp
3. handle "not found" or nearest-report behavior exactly as the official docs define it
4. decode and return both raw timestamps and human-readable time

Do not invent nearest-neighbor semantics. Fetch the REST API docs if the exact behavior matters.

### Bulk and paginated reports

Use bulk lookup when the user supplies multiple feed IDs for the same timestamp. Use paginated history when the user needs sequential reports for one stream starting at a timestamp.

Persist `nextPageTS` or equivalent pagination cursors when building data collectors.

## Error Handling

Generated REST code should handle:

- missing credentials
- unauthorized or insufficient feed permissions
- timestamp/signature errors
- unknown feed IDs
- retryable 5xx responses
- decode mismatch when a feed uses a different schema than expected

Keep retry logic simple unless the user asks for production hardening.
