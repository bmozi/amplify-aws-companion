# Connection-budget assessor notes

Provisional internal criteria; these are not observed learner results or AWS settings.

1. Application maximum is 120; adding 60 for other clients/reserve allocates 180 of 240, leaving 60. A maximum does not prove all connections are open or busy.
2. At ten each, 24 processes permit 240 application connections and 300 total. At seven each, 168 plus 60 is 228, leaving 12. Smaller pools can increase waits; lower overlap changes release and recovery behavior. Require representative observations rather than picking the smaller number automatically.
3. The importer contributes another 40: 168 + 40 + 60 = 268, exceeding 240 by 28. Account for deployment and scheduled-job overlap, or explicitly coordinate them. The original calculation was incomplete for this changed operating schedule.
4. Require evidence for cancellation propagation, rollback/completion, and connection release or discard according to the chosen driver. A frontend timeout alone establishes none of these. Verify that a returned pooled connection has appropriate state for its next borrower.
5. At most 60 connections remain before other work/reserves. Useful throughput depends on occupancy, transaction duration, session behavior, query work and downstream resources. Do not infer an immediate-service guarantee or fixed multiplexing ratio from client count.
6. These two stages contribute 920 milliseconds, before any omitted work. Investigate pool occupancy, leaks, transaction duration, competing clients and concurrency. An index can help if slow query work contributes to the contention; the single 20-millisecond observation does not establish that cause.

For transfer, count every client reaching the shared target and examine reconnect storms and network delays. Separate writable databases introduce replication, conflict, routing and authority questions; they do not automatically form one consistent data store. Accept defensible alternatives when they name these boundaries and required tests. No actual proxy, driver cancellation or multi-region behavior was tested here.
