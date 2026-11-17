# A cold cache can multiply source work

Run from the repository root with ordinary Python 3:

```bash
python3 examples/cold-cache-burst/lab.py
```

This is a cloud-free companion to [the database read-path lesson](../../reader/BOOK-LOCATORS.md#book-b2320aadd4a275a7). It uses Python threads and a held synthetic source to force known concurrent schedules. It calls no AWS service, opens no network connection and measures no real database latency, throughput, ElastiCache behavior or dollars. The key is a fictional tenant/repair identifier, not an authentication mechanism.

Predict the three observations before running:

1. Eight callers start together on an empty naive cache. The source is deliberately held until all eight have entered it. How many reads occur?
2. Eight callers start together on an empty cache with a per-key shared in-flight result. The source is held until seven callers are waiting on the first. How many reads occur? What would happen if two different keys were loaded or if the app had eight separate processes?
3. The shared source read fails. What do the waiting callers see? Is a failed value cached? Can a later request retry after the source recovers?

The lab asserts eight, one and one failed shared read followed by a successful second read, respectively. It fails if a waiter hangs or if failure is treated as a successful cache entry. The synchronization controls the schedule rather than relying on a tiny sleep to “probably” expose a race.

This code is a teaching example, not a production cache. It has no TTL, invalidation protocol, per-caller authorization, eviction, cancellation policy, bounded waiter count, distributed coordination or observed service latency. Use the separate [cache-consistency lab](../cache-consistency/README.md) to see stale display and a delayed reader refill a cleared cache. Use the [scaling model](../scaling-policy-model/README.md) to reason about a shared downstream ceiling. Together they show different failure modes; none proves a selected AWS cache or database can survive a real burst.

For a changed case, the repair summary becomes tenant-private and one technician loses access while a shared load is in flight. Decide where authorization must occur and whether an already-waiting caller can still receive the value. Then the source is available but its concurrency limit is four while the application runs in six processes. Explain why this process-local coalescing cannot guarantee at most four source calls across the fleet. Ask Codex for an admission, timeout and fallback plan, then label every assumption and evidence gap.
