# Count business events, not delivery attempts

Run from the repository root with Python 3, without optimization:

```sh
python3 examples/event-reconciliation/lab.py
```

No dependencies, credentials, network calls or retained files are needed. SQLite runs in memory. Before running, predict whether a $20 sale that happened in minute one but arrives in minute three should change minute one's report. Then predict what redelivering a $10 sale should do.

The drill begins with a provisional $10 first-minute report. A late $20 sale changes it to $30. A $5 event at exactly second 60 belongs to the second minute, using half-open intervals `[start, end)`. Replaying all three events in reverse order leaves the total at $35. Eleven delivery attempts produce three accepted events, four duplicates, one identity conflict and three quarantined payloads. Rejected payloads never contribute to totals.

The `events` composite primary key `(producer, id)` and canonical payload prevent a repeated identifier from silently changing money. A separate `deliveries` table retains every attempt and its outcome. Report queries aggregate accepted events by occurrence time. An independent **synthetic** producer manifest exposes the missing event before it arrives; matching that fixture is not proof a real source reported everything.

The first run uses one default fixture producer, one currency and sequential local calls. Time and producer identity are trusted inputs. It rejects timestamps beyond the arrival time; real clock skew requires an explicit tolerance policy. It does not authenticate producers, implement stream checkpoints, test concurrent consumers, simulate AWS, persist across a real process restart, correct accepted events, or measure Athena costs. Retaining arbitrary raw payloads in production also requires privacy and retention rules.

## Two shops can both issue event 42

Run the second pass after predicting how two shops' `42` records should be counted:

```sh
python3 examples/event-reconciliation/producer_lab.py
```

Shop A contributes 1,000 cents and shop B contributes 2,000. Their trusted producer labels are passed separately from the payload. The key and duplicate lookup use `(producer, id)`. A scoped expected manifest catches shop B's missing event after only A arrives; comparing only the set of IDs incorrectly appears complete because both sets contain `42`.

After B arrives, the ledger contains two events totaling 3,000 cents. Replaying both unchanged produces two duplicates. Changing A's amount creates a conflict, and adding an unexpected producer field inside the body is quarantined. The exact original accepted rows remain unchanged. Empty or non-string producer context is rejected before ledger access. Both in-memory databases are explicitly closed.

The output also demonstrates the limit: an arbitrary nonempty producer label is accepted in a separate fixture database. This function does **not** authenticate the caller or check membership. A real ingestion boundary must supply trusted scope; a browser-provided label would invalidate that assumption. The aggregate `report` function intentionally totals all producers for this operator exercise; it is not a customer-scoped API or a tested tenant authorization boundary.

Explain `unscoped_manifest_false_complete` and `scoped_manifest_detected_missing_shop_b` before asking Codex to interpret them. Then describe the enforcing component that would be needed to reject an impostor in a real system. Do not relabel this check as an authentication test.

Independent challenge: design a refund event referring to the original producer/event pair without overwriting the original sale. Decide whether a producer can correct another producer's event and where that authority is enforced. Define expected totals and replay behavior before changing code. The current lab does not implement refunds or persistent schema migration.

Ask Codex: “Review this event contract and accounting query. Find a sequence of valid deliveries that yields a wrong total. Separate source omissions, duplicates, conflicting IDs and late arrival. Propose tests before edits. Do not deploy AWS resources.” Verify its counterexample manually.

Read [the lesson](../../reader/BOOK-LOCATORS.md#book-f0f0044d800d44b9). Local passing assertions do not establish source completeness, distributed exactly-once effects or live AWS behavior.
