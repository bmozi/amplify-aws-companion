# Individual-skill review: SAA-C03 task 3.3

Internal editorial review, updated October 19, 2026. The [official task](https://docs.aws.amazon.com/aws-certification/latest/solutions-architect-associate-03/solutions-architect-associate-03-domain3.html#solutions-architect-associate-03-domain3-task3) contains five skills. All five now have individual **partial** teaching and assessment links. The new [read-promise lesson](../../reader/BOOK-LOCATORS.md#book-00750a33d2735e31), [figure](../../book/figures/database-read-promises.svg), [seven cases](../../examples/database-read-architecture/README.md) and [assessor](../../examples/database-read-architecture/ASSESSOR.md) deepen skills 01–02. IDs use editorial ordinal positions.

## Skill 01 — Configure a read replica for the business read

The Unit 21 lesson and cases 1–3 distinguish a manually created asynchronous RDS DB-instance read replica from the non-readable Multi-AZ DB instance standby and the different Multi-AZ DB cluster. The assessment requires actual eligible-read routing, lag/freshness evidence, correct writer path and failure behavior. The local [recovery-copy](../../examples/recovery-reconciliation/README.md) fixture illustrates copy lag and wrong-change propagation, not database-engine replication. Selected engine/Region support, actual replica, encryption/network/permissions, endpoint routing, measured lag, cost, teardown and independent learner review remain open. This is partial design evidence, not the official implementation skill completed.

## Skill 02 — Design the database around competing read and write promises

The new lesson separates immediate booking confirmation, one-minute-lag reports and reusable descriptions; cases 4–6 change query cost, pooled connections, reader failure and recovery source. The existing query-plan, pool, capacity, cache and recovery labs test local pieces. An extra reader does not expand the writer's commit capacity or repair an inefficient query. Selected AWS topology, representative read/write workload and correctness, failure redistribution, availability, full cost and independent learner review remain open.

## Skill 03 — Select an engine against actual compatibility needs

An existing PostgreSQL application uses PostGIS and stored procedures. Its owner requests a hosting migration, but the proposed target is MySQL because both use SQL. Explain the scope change, nominate a managed PostgreSQL candidate and alternative, and identify compatibility evidence needed for acceptance. Then suppose an invoice-total test differs despite matching row counts.

Look for exact version/extension/procedure/driver requirements, a distinction between engine conversion and hosting migration, independently expected business results and a measured operating/cost comparison. Teaching: unit 25, “The engine and the managed service are separate decisions.” Cases 1 and 6 in the database-selection review provide original assessment prompts. No PostgreSQL/MySQL compatibility run or AWS engine comparison was performed.

## Skill 04 — Select a database type from access and correctness requirements

A high-volume device-status service has specified keyed reads and updates. Recommend a candidate and one credible alternative. Change the requirement to frequent unplanned relationship queries, then add a last-seat invariant. Explain which changes affect the decision and why transactions do not uniquely identify SQL.

Look for access patterns, skew, authoritative state, flexibility, service-specific transaction boundaries, explicit reversal conditions and avoiding unsupported latency claims. Teaching: unit 25, “Relational and key-based designs organize the work differently.” Cases 2–5 supply changed requirements and assessment reasoning. This is a source-grounded design review, not a configured cloud database or measured comparison.

The [in-memory authority lesson](../../reader/BOOK-LOCATORS.md#book-1a9c241595d0995a) and cases 7–9 add a current service-selection boundary: an ordinary display cache can be rebuilt from its ledger, while a selected durable in-memory primary must defend its acknowledged-write and restore promise. The [local journal lab](../../examples/in-memory-authority/README.md) then compares record-before-ack with ack-before-record, an old snapshot and a worker replacement using real SQLite commits. Eligible node-based ElastiCache for Valkey synchronous and asynchronous durability and MemoryDB are compared as configurations with different consequences; the learner must check exact version, Region, replica freshness, recovery and whole cost. This remains partial: the local ordering result is not a selected AWS implementation or a performance measurement.

## Skill 05 — Integrate caching against requirements

A class listing shows one seat after another customer has booked it. The team says a ten-second TTL guarantees every answer is at most ten seconds old and deleting the cache after a database update prevents all stale results. Draw a counterexample involving a paused reader. Decide where the booking rule must be enforced. Then remove the cache during a busy period and explain the new source-load risk.

Look for: cache-insertion time versus source-observation time, stale repopulation after invalidation, authoritative conditional writes, freshness per operation, tenant/representation keys, authorization and bounded cache-miss load. A version number without an atomic ordering protocol is insufficient. The source-load example changes from 1,000 to 10,000 reads when the fictional hit rate falls from 90 percent to zero; it is not measured traffic.

Teaching: [database read paths](../../reader/BOOK-LOCATORS.md#book-8d7fd952f0661828). Evidence: [local lab](../../examples/cache-consistency/README.md), including real SQLite conditional writes and deterministic replay of the stale-result schedule. The in-memory cache and simulated time are not an ElastiCache deployment. No actual distributed invalidation, cache outage load test, replica-lag measurement or independent learner assessment was performed.

## Knowledge review and remaining work

This task's database-service/engine selection, read replication, capacity, connections, caching and infrastructure topics still need selected AWS implementation and measured comparative evidence. Unit 21 now connects the read promises to topology and negative cases; Unit 25 adds engine/type selection decisions. All five skills have partial individual assessments, not complete task coverage or real replica configuration. Engine compatibility and performance still need representative tests.

The current remedy addresses a material teaching gap: cache names and TTL alone did not explain stale repopulation or the distinction between display and authoritative admission. Learners should predict the lab outcomes unaided and explain a changed case. That assessment has not been run with independent readers.
