# A backup can open successfully and still contain the wrong business data

Run `python3 examples/recovery-reconciliation/lab.py` from the repository root. Python's standard library is sufficient. No AWS account or external service is used; all temporary databases are removed afterward.

Predict which recovery copy should be accepted:

| Copy | Database opens | Three orders present | Amounts match confirmed orders |
| --- | --- | --- | --- |
| Newer damaged copy | Yes | Yes | No |
| Older copy | Yes | No | The two present orders match |

The newer copy has an altered amount. Its database integrity check and row count both pass, but reconciliation rejects it. The older copy is restored separately and compared with an independent synthetic ledger of confirmed orders. One missing order is replayed; all IDs and amounts then match and the total is 4,400 cents. The original database is not overwritten.

The fictional backup recovery point is second 60, the last confirmed write is at second 180 and the incident is at second 240. Backup-only exposure spans 180 seconds before the incident and contains one missing confirmed write. Those timestamps are an authored scenario. The separately measured local duration covers copy and validation work only; it excludes detection, approvals, AWS restore and application reconnection.

The command also compares an invented three-order candidate with the same **count and 4,400-cent total** as the ledger, but with `order-X` in place of `order-3`. Predict the result before running it: reconciliation reports one missing and one unexpected identity, so the candidate is rejected. Then remove the independent ledger from the scenario: explain why the missing order can no longer be reconstructed with confidence. Never silently invent a record to make counts match.

Ask Codex to challenge the recovery evidence: what does the checksum, row count, business reconciliation and timing each establish? Complete E14 and read [the recovery unit](../../reader/BOOK-LOCATORS.md#book-20703bba15f79b2d). This lab does not emulate AWS backup, encryption, IAM, region failure or traffic cutover.

## A maintained copy follows an accidental deletion

The same command also runs a separate four-order scenario. It uses real SQLite full-copy refreshes, not engine replication or CDC. Predict these states before reading the output:

| Copy | Order 2, accidentally deleted | Order 4, confirmed after historical copy |
| --- | --- | --- |
| Writer after mistake | Missing | Present |
| Maintained read copy after refresh | Missing | Present |
| Retained historical copy | Present | Missing |
| Separately restored candidate after ledger replay | Present | Present |

The complete restored candidate has four exact IDs/amounts and totals 4,900 cents. The original scenario above still totals 4,400 cents; these are separate datasets and outcomes. The program checks the read copy before and after a controlled refresh, verifies the copied deletion, preserves the historical copy and leaves the damaged writer unchanged. Connections are explicitly closed before the temporary directory is removed.

For transfer, suppose the deletion was a legitimate cancellation. Explain why blindly replaying the old booking would now be wrong. If the independent confirmation ledger is lost or incomplete, identify which claims can no longer be established. Do not manufacture missing orders or treat agreement between two damaged copies as independent reconciliation.

This is a sequential local state demonstration. It does not test replica endpoints, replication ordering, network lag, managed backup retention, point-in-time service restore or application cutover. The fixture's intact historical copy is not evidence of immutable or separately authorized backup storage.

## Restore one shop without reversing another shop's work

Run `python3 examples/recovery-reconciliation/tenant_lab.py`. This second exercise uses only Python's standard library and temporary SQLite databases. It supports the [architecture decision lesson](../../reader/BOOK-LOCATORS.md#book-aadca742bfb00b8e).

A historical copy contains order 1 for shops A and B. After the copy, shop B changes its order amount and adds order 2. Shop A also adds order 2, then accidentally loses order 1. Predict the consequences of replacing the whole live database with the old copy: it would recover A1 but lose both new orders and reverse B1's legitimate change. The drill demonstrates this on a separate unsafe copy, leaving its live fixture intact.

Restoring only A's historical rows is also insufficient: that would lose A2. The fixture supplies a complete, trusted confirmation ledger so we can reconstruct the intended A records. In this program the ledger is captured before damage for a controlled comparison. It is **not** an independently secured audit system or a mechanism that discovers missing business history. If the ledger were incomplete, the desired state would be unknown; do not run destructive replacement from an incomplete candidate.

| Check | Observable result |
| --- | --- |
| Interrupt the repair after deleting A's rows inside a transaction | Rollback preserves every original row |
| Include B's row in A's candidate | Reject before changing any row |
| Change A2 after preparing the plan | Reject the stale plan; preserve the newer amount |
| Reconcile the new amount, review a fresh plan and apply it | A contains orders 1 and 2 at 100 and 175 cents; B still contains 250 and 300 cents |
| Repeat the successful repair | Exact tenant/ID/amount tuples remain unchanged |

The repair checks the target tenant's observed state and replaces only that tenant's rows in one SQLite transaction. Both shops deliberately use the same local order IDs; an ID without a tenant is insufficient. A write transaction encloses the precondition check and replacement. The stale update in this drill is deliberately ordered before that transaction; this is not a concurrent-writer stress test. Comparing row state also cannot detect a value that changed and later changed back, or an external effect absent from the table. A real recovery plan needs an appropriate revision/authority mechanism and explicit handling of those effects.

The table is intentionally simple. There are no foreign keys, triggers, photo objects, authentication, notifications or application connections to redirect. Do not copy the delete-and-reinsert technique into a richer schema without designing its dependencies and semantics. A database rollback cannot undo a message already sent to a technician.

Ask Codex to review the output against the invariants: A is repaired to the reviewed state, B is unchanged, stale plans and mixed-tenant candidates are refused, and an interrupted transaction leaves no partial repair. Then explain which invariants require additional evidence when files and external assignments are introduced. Passing this local lab does not demonstrate AWS tenant isolation, point-in-time recovery, recovery-time objectives or production cutover.
