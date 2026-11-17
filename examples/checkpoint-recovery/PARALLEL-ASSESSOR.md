# Parallel checkpoint assessor notes

Keep this separate from a learner's first attempt. The fixture is a local ordered-file model and makes no cloud or customer claim.

## Expected reasoning

Before worker 2 is repaired, completion records exist for positions 1 and 3 and the ledger has sales A and C (4,000 cents). Position 2 is missing. The safe contiguous frontier is **1**. A marker of **3** incorrectly means “everything through 3 is done.” A restart that begins after 3 never revisits sale B.

In the safe run, restart processes position 2 and recognizes 3 as already complete. The final ledger has A, B and C (6,000 cents) and progress 3. A learner should explain why the per-position completion record makes replay of 3 harmless in this fixture and why it does not establish exactly-once delivery from a real stream.

In the changed case where 2 repeatedly fails, advancing through 3 needs a chosen, durable exception policy, an exact failed record identity, an accountable repair owner, and a way to reconcile the eventual business result. Simply recording “3 was last seen” is insufficient. A decision to quarantine 2 is a business and operating policy, not an arithmetic trick. The local exercise has no quarantine path; a correct answer may keep the marker at 1 while defining what must be built.

## Evidence boundaries to enforce

- Two overlapping local processes and one SQLite database per run are observed. Distributed ownership, leases, failover, and source ordering are not.
- The effects and local progress are committed in one database transaction. The separate-commit crash windows live in `lab.py`; neither fixture proves an external side effect can be made atomic with a stream checkpoint.
- These trusted fixture rows are not authenticated producer events or Kinesis sequence numbers.
- A numeric total is insufficient on its own; compare the identity set and exact source positions.
- No independent learner attempt, AWS ingestion, customer outcome, or billing evidence is recorded.
