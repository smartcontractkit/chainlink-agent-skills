# Frontend and Storage

Use this for real-time UI, candlesticks, local report history, or SQLite. Keep every credential in backend environment variables: SDK stream → decode/optionally verify → optionally store raw+decoded report → publish sanitized data by WebSocket/SSE/HTTP → render. Browsers receive sanitized data only; never connect them to Streams directly.

## Charts

For live prices, show latest price, bid/ask, raw timestamp, and connection state from backend-decoded reports. For candles, prefer the Candlestick API for official OHLC history; aggregate reports only when local candles are requested or that API is unavailable. It provides history, row/column response formats, symbol/group discovery, and streaming price updates. Take its endpoint from [public-endpoints-and-addresses.md](public-endpoints-and-addresses.md), fetch current parameter docs, and use the repo's existing chart stack (or a fitting library such as Lightweight Charts/Recharts).

## SQLite

Use only when local persistence was requested. Default shape:

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

Adjust fields to the schema/language. Preserve `full_report` for re-decoding after SDK upgrades. Use prepared statements, idempotent inserts for reconnect/HA duplicates, integer timestamps, strings for precision-sensitive decoded values, and lowercase-hex feed IDs unless the SDK requires case. WAL suits long-running collectors when safe for the app.

## Timestamp Lookback

For a price at Unix timestamp X: use the REST API/SDK timestamp lookup, decode it, optionally insert it, and return raw timestamp fields plus the decoded value. Do not substitute local SQLite data when official history was requested unless local-only behavior is explicit.
