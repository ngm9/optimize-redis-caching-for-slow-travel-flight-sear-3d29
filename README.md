# Task Overview

Utkrusht runs a travel search API for partner companies. The `/api/travel/flights/search` endpoint is heavily used to search flights by origin, destination, and date. Although Redis is already integrated for caching, this endpoint still shows high latency under concurrent traffic. Cache lookups are slow because cache keys include a timestamp suffix and are discovered using SCAN-style pattern matching instead of direct lookups, and cached search results never expire, causing memory bloat over time.

In addition, the `/api/travel/price-alerts` endpoint stores every price alert in a single Redis String key as a growing JSON array. As the number of alerts grows, each write reads and rewrites the entire array, leading to slow writes and unnecessary serialization overhead. A startup cache pre-warming routine also populates Redis for a list of popular searches but performs each SET operation individually without pipelining, making bulk initialization slower than necessary on larger datasets.

Your task is to analyze and optimize the existing Redis usage in this application. You must preserve the overall behaviour of the API while improving key patterns, TTL strategy, data structures, and connection usage so that flight search and price alert operations are significantly faster and more robust under load.

## Helpful Tips

- Start by calling the existing endpoints under light and moderate load (e.g., using curl, HTTP clients, or simple load-test tools) to observe baseline response times for `/api/travel/flights/search` and `/api/travel/price-alerts`.
- Inspect Redis keys and values to understand how data is currently stored. Use commands like:
  - `KEYS flights_search:*` (for exploration only, not in production)
  - `SCAN 0 MATCH flights_search:* COUNT 100`
  - `TYPE <key>` and `MEMORY USAGE <key>`
- Use `INFO stats`, `INFO keyspace`, and `INFO commandstats` to see basic cache hit/miss behaviour, number of keys, and command usage.
- Run `MONITOR` or `SLOWLOG GET` in Redis to see which Redis commands are being called most frequently and which ones are slow.
- Look for patterns such as:
  - Keys that look almost unique per request (e.g., containing timestamps) leading to very low cache hit rates.
  - Keys without meaningful TTLs, causing unbounded growth in Redis memory usage.
  - Large values that are read and written repeatedly (e.g., a single JSON array of many alerts) which increase serialization overhead.
- Review how the cache warm-up logic is implemented. Check if it sends one command at a time to Redis rather than batching operations.
- Examine the Redis client configuration (connection pool size, decode_responses, timeouts) to understand whether it is tuned appropriately for concurrent traffic.
- When testing improvements, compare before/after:
  - Average and p95 latency for the flight search endpoint.
  - Redis key counts and memory usage for cached searches and alerts.
  - The number of Redis commands executed per request.
- Use incremental changes and test after each change so you can clearly see which optimizations have the biggest impact.

## Redis Access

- Host: `localhost (127.0.0.1)`
- Port: `6379`
- Database: `0`

Redis is bound to `127.0.0.1` on the droplet for security and is only accessible from within the droplet itself (via SSH).

SSH into the droplet and connect using `redis-cli` directly:

```bash
redis-cli -h 127.0.0.1 -p 6379
```

Or access Redis via the running container:

```bash
docker exec -it <container_name> redis-cli
```

Useful commands for analysis:

- `INFO` – inspect server status, memory, and keyspace information.
- `INFO stats` and `INFO keyspace` – understand key counts and operation statistics.
- `SLOWLOG GET 10` – check recent slow commands.
- `MONITOR` – view live command traffic (use carefully as it can be verbose).
- `SCAN 0 MATCH flights_search:* COUNT 100` – explore current cache key patterns.
- `GET price_alerts` and `MEMORY USAGE price_alerts` – inspect how alerts are stored.

Use these tools to verify the impact of your optimizations on key patterns, TTLs, memory usage, and command distribution.

## Objectives

- Improve the performance of the `/api/travel/flights/search` endpoint by optimizing Redis key design and lookup strategy so that cache lookups no longer depend on SCAN-based searches across timestamp-suffixed keys.
- Introduce an effective TTL and expiration strategy for cached flight search results so that popular queries benefit from high cache hit rates while Redis memory usage remains under control.
- Reduce the cost of storing and updating price alerts by replacing the current single large JSON String pattern with a more scalable structure and access pattern that avoids full-array reads and rewrites on each write.
- Optimize bulk cache warm-up operations so that they no longer perform one command per Redis round-trip for each popular search and instead use more efficient interaction patterns.
- Ensure that the Redis client configuration and connection usage are appropriate for concurrent requests, avoiding unnecessary connection overhead and bottlenecks.
- Maintain functional parity for all existing endpoints while improving latency, cache hit rate, and stability under moderate concurrent load.

## How to Verify

- Measure baseline latency for `/api/travel/flights/search` with repeated identical queries (same origin, destination, and date). After optimization, the second and subsequent requests for the same parameters should become noticeably faster and show fewer costly backend computations.
- Inspect Redis keys before and after your changes:
  - Verify that cache keys for flight searches use a predictable, low-cardinality pattern without timestamp components that change on every call.
  - Check that outdated or unused search results eventually expire and disappear from Redis.
- Confirm that you can still retrieve and create price alerts via `/api/travel/price-alerts`, but that Redis no longer stores all alerts in a single large JSON String that grows indefinitely.
- During cache warm-up, monitor Redis with `MONITOR` or `SLOWLOG GET` to ensure bulk initialization uses fewer round-trips compared to the original implementation.
- Use Redis `INFO memory` and `INFO keyspace` to compare key counts and memory usage before and after optimization, ensuring that they remain stable or grow more slowly under typical usage.
- Compare the number of Redis commands executed per request using `MONITOR` or `INFO commandstats` and verify that the optimized implementation issues fewer expensive commands (e.g., fewer SCAN operations and large GET/SET of huge values).
