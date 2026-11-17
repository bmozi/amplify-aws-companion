# Assessor reasoning: a late old schema writer

Keep this file out of the learner's first attempt. The exercise is a local SQLite model; no learner or AWS outcome has been observed.

The first clean comparison is true for the instant it ran. It is not a lock, a writer inventory or a future guarantee. The old connection later changes only `email`, leaving `contact_email` stale. Reconciliation must run again, but repeating it without controlling later writes leaves the same race.

The local guard changes the phase and checks the row at the actual write. The old connection's earlier read of `expanded` does not override the database's current `fenced` phase. Its update fails without changing the row. The compatible writer changes both fields in one statement and succeeds. Two statements inside one transaction fail at the first immediate trigger check; atomic rollback protects the row but does not make the request successful.

Accept an answer that proposes a different engine-supported guard if it explains how the guard is enforced at the authoritative write and how it is tested against every writer. Do not require a SQLite trigger as a universal AWS prescription. Look for the operational cost of the guard: old customer requests can fail until routed away or upgraded. A correct release decision names a writer inventory, phase sequencing, customer-path checks, database-specific locking/DDL and recovery evidence. A green process check or CodeDeploy application rollback does not establish data compatibility.

For transfer, change the old writer to a scheduled export job or a direct administrative tool. Ask where it writes and what evidence would prove it was disabled or made compatible. If the participant proposes removing `email`, ask which old readers and rollback revision still reference it. Score first-attempt reasoning and any Codex-assisted revision separately; this authored key has not been calibrated with independent learners.
