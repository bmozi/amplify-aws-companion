# Keep rollback compatible with the current data

Run `python3 examples/schema-compatibility/lab.py` from the repository root, without `-O`. This standard-library exercise changes a real in-memory SQLite schema and closes the connection afterward. It creates no files, network listeners or AWS resources. Addresses use the fictional `.test` domain; nothing is sent.

Predict each stage:

1. The old application reads `email`. Adding nullable `contact_email` preserves the old reader. A compatibility reader uses the new value when present and falls back to the old field.
2. Backfill copies the old values. An old-only writer then changes `email`. The compatibility reader returns a stale value because the new field is already populated. Reconciliation finds the mismatch.
3. The fixture retires old-only writes, repeats reconciliation and uses a writer that updates both fields in one transaction. An injected failure between updates rolls the whole transaction back.
4. Table replacement removes `email`. A new-only reader succeeds, but both the original reader and the fallback reader fail because their SQL still references the removed column.

The fourth stage is especially important: `COALESCE` cannot rescue a query referencing a column that no longer exists. Deploy and verify the new-only readers before removing that column. The fixture calls the separate query explicitly to expose the compatibility boundary; it does not orchestrate a live rollout.

This sequential schedule assumes control of every writer. It does not prove that a production fleet, scheduled job or rollback version has stopped old-only writes. Reconciliation is an observation, not an atomic promise that no subsequent write can invalidate it. A real plan needs writer fencing or a supported synchronization design, online migration/locking analysis, engine-specific DDL review, backups and tested recovery. Updating two fields in one database transaction is not a distributed dual-write solution.

For a negative control, use a temporary copy and omit the second field update in `compatible_write`. The complete old/new equality assertion should fail. Then explain why restoring an old binary after contraction is not a valid application rollback. Restoring an old database backup would be a separate recovery action that must account for writes since that backup.

Ask Codex to list every reader and writer that depends on either field, including exports, background work and old deployment artifacts. Require references to actual queries or configuration. Its list is a review aid, not evidence that the inventory is complete. The exercise does not perform an AWS database migration.

## Catch the writer that arrives after the clean check

Run `python3 examples/schema-compatibility/overlap_lab.py` from the repository root, without `-O`. It opens two independent SQLite connections to one temporary file and removes that file when finished. First predict what happens if the new application checks that `email` and `contact_email` match, but an old worker updates only `email` a moment later. The output shows that the earlier clean check was true **and** the later row disagreed. Neither observation cancels the other.

The second pass reconciles the row, then changes a phase flag while holding SQLite's write lock. A database trigger checks the current phase on every row update: after the fence, an old-only update fails even though the old connection had read the earlier phase. A compatible update sets both fields in one SQL statement and succeeds. The old reader can still read during this expanded phase, but its write path now fails. Redirect or retire old write traffic before using that fence in a customer system; this fixture does not demonstrate an uninterrupted release.

This is a deliberately small **check-at-write** model. Its temporary database is one reachable authority and SQLite serializes its writes. A real RDS or other migration needs an inventory of every application, scheduled job and direct writer; a reviewed engine-specific constraint/trigger or other enforcement plan; lock and DDL behavior; transaction and failover testing; scoped permissions; recovery; and customer-visible checks. A trigger can also add latency or reject a legitimate update if its rule is wrong. The local gate does not prove any AWS service behavior or authorize changing a live schema. Do not contract the old column until every remaining read path and rollback candidate is compatible with that removal.

Changed case: the compatibility writer updates `email` and `contact_email` in **two statements inside one transaction**. Predict what the immediate trigger does after the first statement, then compare with the single-statement write in the fixture. Attempt a transfer case before opening the [assessor reasoning](OVERLAP-ASSESSOR.md). Ask Codex to propose a release sequence and list the evidence needed to prove no old-only writer remains. Check whether it confuses a passing reconciliation query with a durable write barrier, or assumes that CodeDeploy rollback reverses database data. AWS describes [CodeDeploy rollback as redeploying a prior application revision](https://docs.aws.amazon.com/codedeploy/latest/userguide/deployments-rollback-and-redeploy.html); it is not a database restore. Before any separately reviewed cloud experiment, choose a whole-run limit and reserve for your own account.
