# A fast answer can be an old answer

Run from the repository root with ordinary Python 3:

```sh
python3 examples/cache-consistency/lab.py
```

No dependencies, credentials, network or AWS resources are needed. The script creates a temporary SQLite database, uses an in-memory cache and removes the database after execution. Time values are injected integers; it does not wait ten seconds or measure latency. Do not use Python optimization, which disables assertions.

Predict each result before running it:

1. Reading the same cached record twice avoids the second database read. Another tenant with the same item name gets a separate entry.
2. After the last seat is reserved, the cached display still says one seat. A second reservation is denied by a conditional database update.
3. At the exact expiry time, the cache reloads the new record.
4. A reader fetches an old record and pauses. A writer updates the source and invalidates the cache. The reader then inserts its old result. Deleting the cache after writing did not prevent stale repopulation.
5. A later expiry refreshes that entry in this schedule. A missing source record creates no successful cache entry.

The assertions deliberately require the stale observations in cases 2 and 4: they reproduce the weakness, rather than pretending to fix distributed cache invalidation. The business invariant is separate: only the authoritative conditional write can consume a seat, and it never lets the count fall below zero. This is not a complete booking API; request idempotency, authentication, payment and crash recovery are out of scope.

The store uses real SQLite statements and transactions. The cache and pause/resume schedule are local teaching code, not ElastiCache, Redis, Valkey, RDS replication or a threaded concurrency benchmark. Tuple keys illustrate tenant namespacing, not authentication. The injected schedule shows one possible interleaving; it does not establish all possible races are handled.

Read [the database read-path lesson](../../reader/BOOK-LOCATORS.md#book-8d7fd952f0661828). As a negative control, remove the cache expiry condition in a disposable copy: the boundary assertion must fail. Separately remove `AND seats>0`: the database constraint should reject the invalid decrement, exposing the lost conditional-admission behavior. Do not weaken checks to make either broken copy pass.
