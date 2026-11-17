# Assessor notes — database engine selection

For the stated move, preserving PostgreSQL is the strongest initial candidate because PostGIS, stored procedures and a fixed driver are explicit compatibility requirements and no business goal justifies conversion. RDS for PostgreSQL and Aurora PostgreSQL may both be evaluated as managed-service candidates, but verify the exact engine version, extension support, driver, procedures, privileges and operational fit. Neither candidate is declared a winner without version/Region checks and a workload comparison.

MySQL experience can lower training risk, but does not translate PostgreSQL behavior. A MySQL conversion needs a stated business benefit and evidence that the application, queries, data values, operational scripts, recovery and deploy/rollback behavior remain correct. SQL compatibility alone is not an acceptance test. Include collation, timezone and decimal edge cases because records can retain their row count while business meaning changes.

Candidates should compare like-for-like behavior and load, state what is unknown, and name a fact that would reverse the recommendation. Separate the database engine from the managed service. Review the exact feature/version/Region documentation; AWS schema conversion assessment does not migrate the data or guarantee application semantics. Cost discussion should include capacity, storage, backup retention, replicas, licensing where relevant, data movement, operational work and migration overlap; no price conclusion is supported by this worksheet.

Codex may help locate SQL and draft test cases, but its proposed equivalences require source and expected-result review. No AWS target was created, no migration or benchmark ran, and no independent learner review is established.
