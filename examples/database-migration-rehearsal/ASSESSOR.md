# Assessor notes — database migration rehearsal

Strong answers first ask whether the engine change is justified. For the stated PostGIS, stored-procedure and behavior constraints, moving location while preserving the engine is the safer initial comparison; converting to MySQL requires an explicit benefit and separate compatibility/rewrite evidence. The new Region is also unapproved and must be checked for exact engine version, extension and feature support.

Keep schema conversion, full data load/CDC and cutover distinct. DMS Schema Conversion can assess/convert supported schema objects but does not move table data. DMS full load moves existing data; CDC may move changes for supported paths. DMS validation has endpoint and key limitations, consumes resources and does not verify application semantics. Confirm these details for the exact source/target versions and migration path.

The missing primary-key tables need an explicit validation strategy. Row counts, checksums or samples can supplement row-level checks but do not necessarily prove exact equivalence. The exercise's independent invoice totals and ordered product-code tests catch semantic drift that simple counts may miss. Tests should cover duplicates, nulls, rounding, collations, extensions, procedures, concurrent writes, retries and target-only writes.

Cutover needs a controlled final-sync/write gate, defined acceptance, client/credential switch and named rollback trigger. A safe rollback must address transactions accepted only by the target. Do not accept “switch DNS back” if data diverged or writes continued in both locations. Retain the source according to approved policy until the owner accepts the target and rollback window expires.

Costs include temporary double-running, transfer, replication, validation workload, backups, logs, rehearsals and operator effort. The migration estimate differs from the post-cutover run rate. No migration, AWS resources, measured duration, quote or learner outcome is part of this paper exercise.

## Four-booking reconciliation

Both copies have four rows and total 40000 cents. Those two checks pass while the copy is wrong. B104 is missing and B105 is unexpected. B102 changes from 8000 to 5000 cents. B103 changes from 5000 to 8000 cents and from cancelled to confirmed. Comparing by customer would conceal the identity substitution for Dee; identity is part of the stated contract.

The source confirmed total is 35000 cents; the candidate target confirmed total is 40000 cents. That business check catches a problem, but still does not identify every discrepancy. Require both the identity/field reconciliation and the independently specified business checks. Cutover is held because exact preservation was required. Rebalancing amounts until a total matches would leave incorrect bookings in place.

After the repaired cutover, B106 is an accepted target-only transaction. Switching clients to the old source would make it disappear from the application's active record unless it is preserved and reconciled. A sound answer controls writes and captures the target's accepted changes; uses a rehearsed, approved reconciliation method; handles duplicate application and retries by stable identity; verifies records and business invariants; and opens only the selected writer after the gate passes. A manual correction is not automatically safe merely because there is one illustrated booking: real dependencies and other accepted changes must be accounted for.

If preservation and verification cannot fit the deadline, escalate the conflict between availability and data preservation to the named decision owner. The exercise does not supply permission to lose a confirmed booking, assume an untested reverse-replication path or promise a recovery time. Accept alternative plans that satisfy the same explicit invariants and explain their dependencies.
