# Frontend and Storage

Use this for real-time UI, candlesticks, local report history, or SQLite. Keep every credential in backend environment variables: SDK stream → decode/optionally verify → optionally store raw+decoded report → publish sanitized data by WebSocket/SSE/HTTP → render. Browsers receive sanitized data only; never connect them to Streams directly.

## Charts

For live prices, show latest price, bid/ask, raw timestamp, and connection state from backend-decoded reports. For candles, prefer the Candlestick API for official OHLC history; aggregate reports only when local candles are requested or that API is unavailable. It provides history, row/column response formats, symbol/group discovery, and streaming price updates. Take its endpoint from [public-endpoints-and-addresses.md](public-endpoints-and-addresses.md), fetch current parameter docs, and use the repo's existing chart stack (or a fitting library such as Lightweight Charts/Recharts). Generated production code must cite `https://docs.chain.link/data-streams/reference/candlestick-api` and state its parameter-check status and date: claim verified only after a successful live check; if the official page cannot be fetched, label parameters unverified as of that date and do not claim validation.

Candlestick server contract (require a configurable upstream base URL whose parsed scheme is exactly `https:` before any request or credential is sent; never use cleartext remote authentication. Live-verify current parameters—including unit-bearing resolution/window bounds—response/error shapes, and availability before generating calls):

| Role | Stable route |
|---|---|
| Exchange form-encoded login/password for the response envelope `d.access_token` plus `d.expiration`; clients must parse the nested `d` object | `POST /api/v1/authorize` |
| Discover groups | `GET /api/v1/groups` |
| Discover symbols, optionally filtered by `group` | `GET /api/v1/symbol_info` |
| Fetch column-formatted history; require `symbol`, `resolution`, `from`, and `to` (`from`/`to` are inclusive Unix timestamps) | `GET /api/v1/history` |
| Fetch row-formatted history; require `symbol`, `resolution`, `from`, and `to` (`from`/`to` are inclusive Unix timestamps) | `GET /api/v1/history/rows` |
| Receive live trade updates and separate heartbeat objects; require one query filter, `symbol` or `feedId`, with comma-separated values; unfiltered requests are invalid. In a trade, `f` is the message type (`t` means trade), `i` the symbol, `fid` the feed ID, `p` the latest price, `t` the Unix timestamp, and `s` the trade size (currently `1`). The currently documented five-second heartbeat cadence is freshness-sensitive and must be rechecked | `GET /api/v1/streaming`: HTTP chunked JSON; explicitly not WebSocket |

Application policy: keep login, password, JWT, and all upstream credentials/authorization in server-side environment values. Never put the API key, password, JWT, or upstream authorization headers in browser/frontend code. Parse authorization results from the nested `d` object as `d.access_token` and `d.expiration`; never read those fields from the top level. History requests must use a server-owned `CANDLESTICK_RESOLUTION` whose exact unit-bearing value was live-verified (for example `1m` or `5m` when currently supported); reject bare numerals such as `5`. Register the downstream browser subscriber before starting the upstream stream. Generated complete-workflow answers must include a concrete browser-facing backend route/handler plus its downstream subscriber/fan-out implementation over SSE, WebSocket, or HTTP using only sanitized objects; an upstream client/callback or prose next step alone is incomplete even though upstream `/api/v1/streaming` is HTTP chunked.

Canonical Node 20 TypeScript example. Source: `https://docs.chain.link/data-streams/reference/candlestick-api`. The endpoint parameters, limits, availability, heartbeat cadence, and volume support below are **unverified as of 2026-08-25** because no live check was performed. Set the HTTPS-only `CANDLESTICK_BASE_URL`, `CANDLESTICK_LOGIN`, `CANDLESTICK_PASSWORD`, and a live-verified unit-bearing server-owned `CANDLESTICK_RESOLUTION`; the optional limits have safe defaults. Package/run note: save this as `server.ts`, declare the sole development dependency with `npm install --save-dev tsx`, then use the one startup command `npx tsx server.ts`.

```ts
import { createServer, type IncomingMessage, type ServerResponse } from "node:http";
type Auth = { token: string; expiration: number }; type Filter = { key: string; query: string };
type Candle = { time: number; open: number; high: number; low: number; close: number; volume?: number | null }; type Trade = { type: "trade"; symbol: string; feedId: string; price: number; timestamp: number; size: number }; type Heartbeat = { type: "heartbeat"; timestamp: number }; type DTO = Trade | Heartbeat;
type Attempt = { controller: AbortController; validated: () => void; close: () => void };
type Session = { filter: Filter; subscribers: Set<ServerResponse>; stop: AbortController; startedAt: number;
  attempts: number; authRetriesUsed: number; token?: Auth; active?: Attempt; reader?: ReadableStreamDefaultReader<Uint8Array>;
  delay?: ReturnType<typeof setTimeout>; ended?: boolean };
class TerminalAuth extends Error {} class Unsubscribed extends Error {}
const sessions = new Map<string, Session>(), WATCHDOG = 15_000, MAX_ATTEMPTS = 5, MAX_ELAPSED = 120_000, MAX_DELAY = 5_000;
const MAX_FRAME = 64 * 1024, MAX_RESIDUAL = 64 * 1024;
declare function strictFilter(p: URLSearchParams): Filter; // exactly one validated symbol or feedId
declare function validateAuth(x: unknown): Auth; // strict s="ok", d.access_token + d.expiration
declare function validateGroups(x: unknown): { groups: string[] }; // strict s="ok", d.groups[].id
declare function validateSymbols(x: unknown): { symbols: { symbol: string; currency: string; baseCurrency: string }[] };
declare function validateHistory(x: unknown): { candles: Candle[] }; declare function validateRows(x: unknown): { candles: Candle[] };
// History: equal finite t/o/h/l/c; v=[] or equally aligned with every value finite. Rows: exactly six finite values before volume normalization.
declare function validateTrade(x: unknown, f: Filter): Trade; declare function validateHeartbeat(x: unknown): Heartbeat;
// Trade is exact f/i/fid/p/t/s and matches f; heartbeat is exact and projected to a semantic DTO.
function upstreamUrl(path: string): URL {
  const base = new URL(process.env.CANDLESTICK_BASE_URL ?? ""); if (base.protocol !== "https:") throw Error("HTTPS upstream required"); return new URL(path, base);
}
declare function requireLiveVerifiedResolution(x: string | undefined): string; // unit-bearing current value; rejects bare numerals
declare function authorizeRequest(url: URL, signal: AbortSignal): Promise<Response>; // authorize fetch must set redirect:"error"; never follow credential-bearing redirects; fetch and body share signal
declare function serveSanitizedRest(req: IncomingMessage, res: ServerResponse, resolution: string): Promise<void>; declare function genericRouteError(res: ServerResponse, error: unknown): void; // sanitized 4xx/5xx
declare function linkedController(parent: AbortSignal): AbortController; declare function abortableDelay(s: Session, ms: number): Promise<void>;
function startAttempt(s: Session): Attempt {
  const controller = linkedController(s.stop.signal); // unsubscribe aborts the active attempt
  let watchdog = setTimeout(() => controller.abort(Error("timeout")), WATCHDOG);
  const validated = () => { clearTimeout(watchdog); watchdog = setTimeout(() => controller.abort(Error("timeout")), WATCHDOG); };
  const a: Attempt = { controller, validated, close: () => {
    clearTimeout(watchdog); if (s.active === a) s.active = undefined; if (!controller.signal.aborted) controller.abort();
  } };
  s.active = a; return a; // watchdog already runs before auth, headers, or reads
}
async function authorize(a: Attempt): Promise<Auth> {
  const response = await authorizeRequest(upstreamUrl("/api/v1/authorize"), a.controller.signal);
  const auth = validateAuth(await response.json()); // same Attempt watchdog remains armed through the complete body read and validation
  a.validated(); return auth; // reset only after complete auth JSON validates
}
async function reauthorizeOnce<T>(s: Session, a: Attempt, retry: () => Promise<T>): Promise<T> {
  if (s.authRetriesUsed >= 1) throw new TerminalAuth();
  s.authRetriesUsed += 1; // session-global and incremented before refresh
  try { s.token = await authorize(a); } catch { if (s.stop.signal.aborted) throw new Unsubscribed(); throw new TerminalAuth(); }
  return retry(); // interrupted request runs exactly once
}
async function consume(response: Response, s: Session, a: Attempt): Promise<void> {
  if (!response.body) throw Error("missing body");
  const reader = response.body.getReader(), decoder = new TextDecoder("utf-8", { fatal: true }); s.reader = reader; let pending = "";
  try { for (;;) {
    const chunk = await reader.read(); if (chunk.done) break;
    pending += decoder.decode(chunk.value, { stream: true });
    const lines = pending.split("\n"); pending = lines.pop()!; // remove complete frames before applying independent limits
    for (const framed of lines) {
      const line = framed.endsWith("\r") ? framed.slice(0, -1) : framed;
      if (line.length > MAX_FRAME) throw Error("oversized frame"); if (!line) continue; // each frame, never the coalesced chunk
      const raw: unknown = JSON.parse(line), heartbeat = !!raw && typeof raw === "object" && "heartbeat" in raw;
      const message = heartbeat ? validateHeartbeat(raw) : validateTrade(raw, s.filter);
      a.validated(); fanOut(s, message); // complete validated JSON only
    }
    if (pending.length > MAX_RESIDUAL) throw Error("oversized partial frame"); // only the residual partial frame
  } pending += decoder.decode(); if (pending.length > MAX_RESIDUAL) throw Error("oversized partial frame");
    if (pending.trim()) throw Error("partial final frame");
  } finally { if (s.reader === reader) s.reader = undefined; reader.releaseLock(); }
}
function fanOut(s: Session, dto: DTO): void {
  const clean: DTO = dto.type === "trade" ? { type: "trade", symbol: dto.symbol, feedId: dto.feedId, price: dto.price, timestamp: dto.timestamp, size: dto.size } : { type: "heartbeat", timestamp: dto.timestamp };
  const frame = `event: ${clean.type}\ndata: ${JSON.stringify(clean)}\n\n`; // semantic allowlist, never raw upstream JSON
  for (const res of s.subscribers) if (!res.destroyed && !res.writableEnded) res.write(frame);
}
function finish(s: Session, failed: boolean): void {
  if (s.ended) return; s.ended = true; clearTimeout(s.delay); void s.reader?.cancel().catch(() => {}); s.reader = undefined;
  s.active?.controller.abort(new Unsubscribed()); s.active?.close(); if (!s.stop.signal.aborted) s.stop.abort(new Unsubscribed());
  if (sessions.get(s.filter.key) === s) sessions.delete(s.filter.key);
  for (const r of s.subscribers) { if (failed && !r.writableEnded)
    r.write('event: end\ndata: {"error":"upstream unavailable"}\n\n'); if (!r.writableEnded) r.end(); }
  s.subscribers.clear();
}
async function runSession(s: Session): Promise<void> {
  let failed = false;
  try {
    let a = startAttempt(s); s.token = await authorize(a); // same bounded attempt continues into first stream
    while (!s.stop.signal.aborted && s.subscribers.size) {
      try {
        const open = () => { const u = upstreamUrl("/api/v1/streaming");
          u.search = s.filter.query; return fetch(u, { headers: { authorization: `Bearer ${s.token!.token}` },
            signal: a.controller.signal }); }; // HTTPS filtered authenticated HTTP chunks—not WebSocket
        let r = s.token!.expiration <= Date.now() / 1000 + 5 ? await reauthorizeOnce(s, a, open) : await open();
        if (r.status === 401) { await r.body?.cancel(); r = await reauthorizeOnce(s, a, open); }
        if (r.status === 401) throw new TerminalAuth(); if (!r.ok) throw Error("transport");
        await consume(r, s, a); // clean EOF is retryable
      } catch (e) {
        if (s.stop.signal.aborted || e instanceof Unsubscribed) throw new Unsubscribed();
        if (e instanceof TerminalAuth) throw e; // only auth/unsubscribe bypass the reconnect budget
        // Read, decode, parse, validation, frame-limit, timeout, HTTP, and EOF failures retry below.
      } finally { void s.reader?.cancel().catch(() => {}); s.reader = undefined; a.close(); }
      s.attempts += 1; // one nonresetting session counter and startedAt budget across every transport failure
      const remaining = MAX_ELAPSED - (Date.now() - s.startedAt);
      if (s.attempts >= MAX_ATTEMPTS || remaining <= 0) throw Error("reconnect budget exhausted");
      await abortableDelay(s, Math.min(250 * 2 ** (s.attempts - 1), MAX_DELAY, remaining)); a = startAttempt(s);
    }
  } catch (e) { failed = !(e instanceof Unsubscribed); } finally { finish(s, failed); }
}
function serveLive(req: IncomingMessage, res: ServerResponse, p: URLSearchParams): void {
  const filter = strictFilter(p); // rejects unfiltered, mixed, repeated, or invalid filters
  res.writeHead(200, { "content-type": "text/event-stream" }); res.write(": connected\n\n");
  let s = sessions.get(filter.key), start = false;
  if (!s) { s = { filter, subscribers: new Set(), stop: new AbortController(), startedAt: Date.now(),
    attempts: 0, authRetriesUsed: 0 }; sessions.set(filter.key, s); start = true; }
  s.subscribers.add(res); if (start) void runSession(s); // subscriber exists before upstream starts
  req.once("close", () => { s!.subscribers.delete(res); if (!s!.subscribers.size) finish(s!, false); });
}
async function route(req: IncomingMessage, res: ServerResponse): Promise<void> {
  const url = new URL(req.url ?? "/", "http://server.invalid");
  if (req.method === "GET" && url.pathname === "/candles/live") return serveLive(req, res, url.searchParams);
  await serveSanitizedRest(req, res, requireLiveVerifiedResolution(process.env.CANDLESTICK_RESOLUTION)); // exact validators; generic errors only
}
createServer((req, res) => void route(req, res).catch(e => genericRouteError(res, e)))
  .listen(Number(process.env.PORT ?? 3000), "127.0.0.1");
```

For browser-facing REST routes, accept only the currently documented official response envelopes unless current official docs state a changed shape and that shape is live-verified:
Before parsing any of these discovery/history bodies, require the top-level response status `s` to equal `"ok"`; this HTTP response-status field is distinct from the numeric streaming-trade `s` field, which is trade size.

- `/groups` reads `d.groups` and projects `{groups: string[]}` from `d.groups[].id`.
- `/symbol_info` reads the top-level `symbol`, `currency`, and `base-currency` arrays—not arrays nested under `d`—and projects `{symbols: {symbol, currency, baseCurrency}[]}` by zipping equal-length arrays.
- `/history` reads the top-level `t/o/h/l/c/v` columns—not columns nested under `d`—and projects `{candles: {time, open, high, low, close, volume?}[]}` from equal-length finite `t/o/h/l/c` arrays plus `v` that is either empty (unsupported) or the same length with every value finite.
- `/history/rows` reads the top-level `candles` array—not `d.candles`—and projects `{candles: {time, open, high, low, close, volume?}[]}` only after requiring every row to contain exactly six finite values `[time, open, high, low, close, volume]`; validate the sixth value even when a `0` placeholder is normalized away.

Reject alternate or nested response envelopes unless current official docs state a changed shape and that shape is live-verified. Validated server-derived candle fields may also be projected after reading the route's official envelope. Normalize every browser candle so unavailable volume—including the current row-format sixth-position `0` placeholder—is omitted or `null`; otherwise include only a validated, currently supported volume value. Live-verify actual group/symbol availability. The `v`/volume field and sixth row position are documented, but current volume support and values are freshness-sensitive and must be rechecked live. Never forward raw upstream REST JSON.

Parse and validate complete streaming JSON messages, then project trades from `f/i/fid/p/t/s` to semantic `{type, symbol, feedId, price, timestamp, size}` objects and heartbeat messages from upstream `{heartbeat}` to semantic `{type:"heartbeat", timestamp}` objects before sending them to the browser; never relay raw upstream stream JSON or chunks. Split and remove complete newline-delimited frames before limits: enforce the complete-frame maximum on each frame independently, then bound only the residual partial buffer, so multiple valid coalesced frames never fail an aggregate chunk/buffer limit. Treat malformed/oversized frames and stream decode/read errors as retryable transport failures under the same nonresetting reconnect-attempt and elapsed-time budgets as EOF/timeouts; only authentication and unsubscribe bypass reconnect, and budget exhaustion still fails closed. Treat the first upstream stream connection and every reconnect while subscribers remain as one subscriber-backed stream session. Initialize `let authRetriesUsed = 0` once when that session starts and reset it only after the session ends, never on reconnect. Implement the only auth gate as `async function reauthorizeOnce(retry) { if (authRetriesUsed >= 1) throw terminalAuthError; authRetriesUsed += 1; await authorize(); return retry(); }`: the counter increments before requesting a token, and the interrupted request runs exactly once. Every reactive `401`, proactive JWT-expiry refresh, and reconnect that needs reauthorization must call this same gate; do not add a separate `getValidToken` refresh path that can reauthorize outside it. Terminal auth errors must exit the upstream loop and bypass any generic transport reconnect catch. Keep this auth budget separate from the transport reconnect attempt cap and total-time budget below. Give each upstream stream an `AbortController`, pass its signal to `fetch`, and abort on no-message timeout or unsubscribe before any reconnect. While subscribers remain, reconnect after a bounded delay only within both a configurable attempt cap and total-time budget; stop when either is exhausted, then fail closed instead of looping forever. Set the configurable watchdog timeout from the current, reverified heartbeat cadence. Complete JavaScript/TypeScript answers must declare required dependencies and include a valid build plus run command or a declared runner/start command; never instruct plain `node` to execute a TypeScript file.

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
