# Relational capacity reasoning: assessor notes

Keep this file away from a first-attempt learner packet.

- **Large reads:** 1,200 operations/s and `(1,000 × 128 + 200 × 16) ÷ 1024 = 128.125 MiB/s`. Only the fictional throughput ceiling is crossed. More IOPS alone does not address that arithmetic comparison. It still does not prove a real storage bottleneck.
- **Small busy reads:** 2,800 operations/s and 10.9375 MiB/s. Neither fictional ceiling is crossed. That does not establish low latency: pool waits, locks, CPU, query plans, bursts and other work are unobserved.
- **Many tiny reads:** 3,200 operations/s and 12.5 MiB/s. Only the fictional IOPS ceiling is crossed. More throughput alone does not address that arithmetic comparison.
- **Exact boundary:** A window with 1,000 reads/s at 64 KiB and 2,000 writes/s at 32 KiB reaches exactly 3,000 operations/s and 125 MiB/s. It is not *above* either stated ceiling, but it leaves no modeled headroom. This is still not a safe configuration recommendation.
- **Changed read size:** 1,000 reads/s at 32 KiB plus 200 writes/s at 16 KiB stays at 1,200 operations/s and becomes 34.375 MiB/s. Neither fictional ceiling is crossed.
- **More clients, same completed I/O:** The calculator's totals are unchanged. Concurrency, pool waiting, transactions or latency may change; new evidence is required.
- **Same I/O, more lock wait:** Storage arithmetic is unchanged. Inspect lock owners, blocked statements, transaction duration and customer impact before proposing a storage change.
- **950 ms request:** The stipulated 900 ms pool wait dominates the 20 ms SQL execution. The remaining 30 ms is not assigned by this trace. Investigate connection allocation, active borrowers, pinning, timeouts and rollout overlap first; do not claim the database query is the primary wait from these numbers.

An adequate answer states units, distinguishes arithmetic from observation, and names a test that could falsify its proposed bottleneck. A fluent recommendation to resize RDS without the selected workload, available metrics, actual limits, pricing and rollback is incomplete. No independent learner has attempted these cases.
