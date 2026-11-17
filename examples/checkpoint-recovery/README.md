# Restart after saving only half the story

Run `python3 examples/checkpoint-recovery/lab.py` from the repository root without Python optimization. It uses the standard library, temporary local files and short-lived child processes. It makes no network calls. Each child has a 15-second timeout. All fixture files are removed when the parent exits normally or handles an exception.

Read [the checkpoint lesson](../../reader/BOOK-LOCATORS.md#book-fef63383f1ae7f1b). Predict both failure windows before running. The source contains two fictional sales: `sale-a` for 1000 cents and `sale-b` for 2000 cents. Progress and destination effects live in separate SQLite databases, so there is no single transaction spanning them.

| Worker sequence | State immediately after forced exit | State after restart |
| --- | --- | --- |
| Save progress, then exit before saving the effect | Position 1; empty ledger; total 0 | Position 2; only sale-b; total 2000, so sale-a is lost from processing |
| Save the effect, then exit before saving progress | Position 0; sale-a recorded; total 1000 | Replays sale-a safely, processes sale-b; position 2; total 3000 |

The early-progress case intentionally demonstrates a defect. A successful exit on its later run does not repair the missing sale. The correct expected source set is known separately, so a progress marker at the end cannot masquerade as a complete business result.

The second sequence commits the destination's identity receipt and counter update in one SQLite transaction. On replay, the same ID and payload return `duplicate` without incrementing the counter. Different content under the same ID is an error. The worker then records progress separately. This does not eliminate redelivery; it makes the demonstrated destination effect safe to repeat.

The parent actually launches a new Python process, requests `os._exit(73)` at the specified boundary, checks the child's exit code and opens the persisted databases to inspect intermediate state. It starts another process for recovery. This is more evidence than calling an in-memory function twice, but it is still a local process failure, not a machine power loss or distributed service outage.

The drill also restarts after completion, appends a producer duplicate at a new source position, and appends conflicting content. The duplicate advances progress without changing the total. The conflict leaves progress at the prior position and the ledger unchanged. The source file is a trusted fixture; integer positions are not actual Kinesis sequence numbers. No source authentication, shard ownership, retention expiry, parallel consumer coordination or external side-effect protocol is implemented.

The `--worker`, `--strategy` and `--fault` options are internal harness controls for the prepared temporary directory, not a general stream consumer CLI. Do not point them at an unrelated folder. The example is not a production ingestion daemon.

## Explain a changed result

1. Remove the duplicate guard and keep the replay. Predict whether the total should remain 3000. The acceptance checks must fail; a green test would not be observing the effect boundary.
2. Send sale-a again at a different source position. Explain why deduplicating only by position misses a producer retry.
3. Put the identity receipt and counter in separate commits. Identify a new failure window and describe the intermediate state a new test must inspect.
4. Replace the counter update with an email. Explain why the SQLite transaction cannot atomically commit delivery by an external service.
5. Let two consumers advance one shared progress marker. Identify the ownership and ordering assumptions the sequential lab no longer proves.

Ask Codex to predict the ledger, total and progress at each stop before executing the lab. Compare its predictions with actual output, then require it to name the missing cloud evidence. No AWS costs or learner-mastery claims follow from these local results.

## Let later work finish while an earlier record is missing

The first lab processes records sequentially. This continuation uses three ordered fictional sales and two overlapping local worker processes. Worker 2 reaches a controlled stall, worker 3 commits, and worker 2 exits before its effect. Predict the saved progress and ledger before running:

```sh
python3 examples/checkpoint-recovery/parallel_lab.py
```

The **contiguous-frontier** version stores completion for positions 1 and 3 but keeps progress at 1. On restart it processes sale B at position 2, recognizes position 3 as already complete, and finishes with all three sales totaling 6,000 cents. The deliberately wrong **highest-finished** version moves progress to 3 when position 3 commits. Restart begins after 3, leaving sale B missing and the total at 4,000 cents. The script checks those persisted states and removes its temporary files.

The fixture's effect, per-position completion and local progress live in one SQLite database and commit together. This isolates the *gap in ordered progress*; the earlier lab is still needed to study separate effect/checkpoint commits. The process coordination is deterministic on one workstation. It does not implement distributed ownership, Kinesis shard leases, source authentication, retention handling or an external payment.

Changed case: position 3 succeeds, position 2 fails repeatedly and requires human repair. May a checkpoint advance through 3? Explain what durable evidence and owner would justify any quarantine policy before progressing, and how a later repair would enter the report. Ask Codex to distinguish the highest observed completion from the highest **uninterrupted** completion, then point to the actual rows rather than assuming the marker is truthful. Facilitator criteria are in [separate assessor notes](PARALLEL-ASSESSOR.md).
