# Assessor notes: migration mechanisms

These judgments are authored against the fictional facts; no migration tool, network, directory, organization or AWS account was configured. Different architectures can earn credit when they establish the same source/target fit and business acceptance.

## Baseline decision

| Lane | Defensible candidate or hold | Evidence gate |
| --- | --- | --- |
| Archive | DataSync is a candidate for a supported NFS-to-target pairing, but five days at the stated spare bandwidth is impossible even ideally. Investigate a later date, a measured larger path, reduced **owner-approved** scope or eligible physical-transfer route. Snow Family devices cannot be newly ordered. | Inventory and final changes, pairing/agent, sustained rate, metadata/permissions, application read, retained copy and retirement sign-off. |
| Partner SFTP | Transfer Family may supply a continuing protocol endpoint to supported AWS storage. Do not use it as the archive or database migration answer. | Partner authentication, endpoint reachability, per-user path, uploaded-file acceptance, recurring endpoint/storage/transfer cost. |
| Booking VM | AWS Transform MGN is a rehost candidate, subject to source and agent/connector support, staging, target launch, network, license and test. It preserves much of the server; it does not turn the app into a managed platform. | Representative launch and customer path, operating/security duties, replication cost and clean target shutdown after tests. |
| PostgreSQL | An engine-native copy/restore may fit a write freeze and supported target. DMS full load plus CDC is a candidate if exact endpoints, keys and logs support it and the downtime budget requires ongoing changes. DMS Schema Conversion addresses schema/code for a supported engine change, not rows or semantics. DataSync copying database files is not a transaction-consistent migration plan. | Source and target versions, consistent snapshot or log point, objects/rows, independent business totals, application journeys, final write boundary, target-only writes and backup. |
| Network/DNS | A staged hybrid path needs source-to-target **and return** routes, DNS resolution, encryption and failure tests. VPN is an encrypted internet path; Direct Connect is dedicated but not encrypted by default. DNS switching is separate from connectivity and database writer authority. | Address and route plan, tunnel/circuit readiness, measured throughput, TLS/IPsec/MACsec design, cached names and customer request tests. |
| Staff identity | Existing directory continuity or a planned directory/federation change must be tested before decommissioning old access. A cutover-morning IAM Identity Center source switch risks losing assignments/roles. | Staff sign-in, access denial, application identity mapping, emergency operator recovery and any KMS/resource-policy references. |

For the 8 TiB archive, the exact ideal time at 80 Mbit/s is `10.180663 days`, and the ideal five-day requirement is about `162.891 Mbit/s`. A valid calculation may round differently but must not call a 1 Gbit/s bound a measured transfer. The exercise's `unproven` verdict means “mathematically possible under perfect use,” not “feasible.” Add scan, protocol, retries, verification, source deltas and final cutover before promising a window. S3 Transfer Acceleration might improve a compatible long-distance client-to-S3 path, but it cannot create more outbound office bandwidth or solve live database consistency.

In the single-account learning sandbox, scoped roles, private state, monitoring and explicit spending gates are relevant. Control Tower requires an organization/landing-zone estate and can create continuing resources and costs; no organization is warranted just to score this paper case. In a real multi-account enterprise, compare Organizations policy/billing and Control Tower account governance against existing accounts, logging/security account ownership, migration role boundaries, audit and funding. These are design decisions, not instructions to enable them here.

## Changed-fact reasoning

- A measured 1 Gbit/s over 20 days removes the **ideal-bandwidth** contradiction. It does not prove scan or final-delta time, permissions, destination reads, or source retirement. A continuing archive write requires a change-capture or last-write boundary.
- No source agent invalidates the MGN proposal **as written**. Check current supported agentless/connector modes and policy before selecting another route; do not assert every VM has an agentless path. A rebuild/replatform or exception may become the better choice.
- PostgreSQL-to-MySQL adds data types, extensions, stored procedures, collation, rounding, queries, drivers and transaction behavior to schema/code assessment. The business may reject the engine change and retain PostgreSQL; no tool makes semantics equivalent by naming a target.
- Lost Identity Center assignments/roles block operator recovery. Restore or pre-provision reviewed access and test break-glass plus normal staff journeys before changing authoritative traffic. Do not rely on a user who can no longer sign in to repair their own access.
- A funded multi-account enterprise must name management, log/security, migration and production owners, organization mode, policy scope, landing-zone prerequisites and ongoing cost. This paper case does not deploy an enterprise environment.

## Provisional assessment guide

Score each dimension 0–2: mechanism/source fit; arithmetic and deadline honesty; database/application cutover and rollback; network/identity/security path; governance and whole-life cost; changed-case revision. Twelve points are possible. A service-name list without source/target evidence or a five-day promise over the 80 Mbit/s link earns no full mechanism/deadline credit. No score represents an actual learner result.
