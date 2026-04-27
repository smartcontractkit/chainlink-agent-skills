# Frontend and Storage

Use this file when the user wants a real-time frontend, candlestick chart, local price tracking, or SQLite persistence for Data Streams reports.

## Frontend Architecture

Keep Data Streams credentials out of the browser.

Preferred architecture:

1. backend service connects to Data Streams using the official SDK
2. backend decodes and optionally verifies reports
3. backend stores raw and decoded reports if persistence is needed
4. backend publishes sanitized updates to the frontend over WebSocket, Server-Sent Events, or HTTP polling
5. frontend renders charts from sanitized price/time data

Use direct browser access only if the current official docs provide a safe public-client pattern. Otherwise, refuse to expose credentials in browser code.

## Charting Choices

For a live price display:

- stream decoded reports from the backend
- show latest price, bid/ask, timestamp, and connection status
- preserve raw timestamps so users can audit timing

For candlesticks:

- use the Candlestick API when the user wants official OHLC history
- aggregate local report data only when the user explicitly wants local candles or the Candlestick API is unavailable
- choose a common chart library that fits the repo, such as Lightweight Charts, Recharts, or the existing frontend stack

The Candlestick API exposes history endpoints, row/column response formats, symbol/group discovery, and streaming price updates. Use [public-endpoints-and-addresses.md](public-endpoints-and-addresses.md) for public endpoint defaults, and fetch the docs before relying on exact parameters.

## SQLite Persistence

Default local schema shape:

```sql
CREATE TABLE IF NOT EXISTS reports (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  feed_id TEXT NOT NULL,
  schema_version INTEGER,
  observations_timestamp INTEGER NOT NULL,
  valid_from_timestamp INTEGER,
  expires_at INTEGER,
  full_report TEXT NOT NULL,
  decoded_json TEXT,
  received_at INTEGER NOT NULL,
  source TEXT NOT NULL,
  UNIQUE(feed_id, observations_timestamp, full_report)
);

CREATE INDEX IF NOT EXISTS idx_reports_feed_time
ON reports(feed_id, observations_timestamp);
```

Adjust fields per schema and language. Store `full_report` even when decoded JSON is available so reports can be re-decoded after SDK upgrades.

## Storage Rules

1. Use prepared statements.
2. Use idempotent inserts to tolerate reconnects and HA duplicates.
3. Store feed IDs as lowercase hex strings unless the SDK requires preserving case.
4. Store timestamps as integers.
5. Store decoded values as strings when precision matters.
6. Use WAL mode for long-running collectors when safe for the target app.

## Timestamp Lookback

For "what was the price at UNIX timestamp X?":

1. use the REST API or SDK timestamp lookup
2. decode the returned report
3. optionally insert the report into SQLite
4. return the raw report timestamp fields and the decoded value

Do not fabricate values from local SQLite if the user asked for official Data Streams history unless local-only behavior is explicitly requested.
