# A hold can expire while payment succeeds elsewhere

Use [the reservation-lifecycle lesson](../../reader/BOOK-LOCATORS.md#book-ffe5a37f32aa3433) for the prerequisites, worked explanation and limits.

Run `python3 examples/reservation-holds/lab.py` from the repository root, without `-O`. The standard library uses an in-memory SQLite database for the initial sequence, then temporary file databases for independent connections in the contention exercises. Connections close and the temporary directory is removed afterward. No account, network, payment provider or real charge is involved. All times and successful-capture events are authored fixtures.

Predict this sequence before running:

| Fictional time | Operation | Expected business state |
| --- | --- | --- |
| 0 | Alice obtains the only capacity under hold A, expiring at 10 | A is held; no free capacity |
| 9 | Bob requests hold B | Full |
| 10 | Bob tries again; expired holds are reconciled transactionally | A expires; B obtains capacity |
| 11 | A trusted fixture reports successful payment capture for A | Refund pending; B keeps its hold |
| 12 | The same payment event is replayed | Same outcome; no duplicate compensation row |
| 12 | B's own payment succeeds | B confirmed |
| 14 | A second distinct successful capture is reported for B | Extra capture needs compensation; no second reservation |
| 100 | Expiration runs again | B remains confirmed; capacity is not released again |

Equality counts as expired in this model. Expiration updates only rows still `HELD`; the number of actual transitions controls how much capacity is returned. Hold acquisition and expiration share a database transaction. A late capture records its business disposition and pending compensation atomically. Reusing a payment ID for a different hold is rejected. Reusing an expired hold ID does not silently allocate a new hold.

`REFUND_PENDING` is a recorded obligation, not evidence that a refund occurred. The hold fixture has no provider API, authenticated webhook, amount/currency validation or customer communication. The separate compensation exercise below uses an authored local provider simulator. The cancellation policy below applies only to held capacity. Inputs are trusted synthetic events. An unknown hold is rejected for separate investigation rather than treated as a verified refundable payment. Production reconciliation must preserve and resolve such events.

The original scenario uses one connection and a controlled sequential schedule. The additional cases below exercise actual local connection contention. Neither establishes DynamoDB behavior or concurrent correctness across cloud workers. The fixture uses caller-supplied time for reproducibility; a real design needs a trusted time policy and explicit treatment of delayed events. It decides eligibility when the capture result is processed, not at a claimed earlier provider timestamp. Different business rules require a different reviewed state machine.

For a negative control, copy the script temporarily and remove the state filter from expiration. Repeated expiration must not pass the capacity invariant. Then design a cancellation racing with confirmation, and a refund request whose response is lost. Explain which durable identities and reconciliation observations prevent double capacity release or duplicate compensation effects.

Ask Codex to trace each state change and identify the exact point where the database transaction stops protecting the external world. Require it to distinguish payment confirmation, reservation confirmation and completed compensation. Keep predictions and unaided explanations before reading the implementation; no learner assessment has yet been performed.

## Two callers act on the same hold

The script also checks both serial orders and an actual overlapping attempt by two threads with separate SQLite connections to a temporary file. A barrier releases the callers together; database write locking determines the winner, so the printed winner can vary. No sleep selects the result.

If cancellation commits first, it releases the held capacity once; the later successful-capture event records refund pending. If confirmation commits first, cancellation returns the confirmed state and leaves capacity occupied. This chosen policy requires a separate business procedure to cancel an already confirmed booking; it does not invent one. Repeating cancellation changes neither result.

The transaction starts with `BEGIN IMMEDIATE` before reading the payment ledger or hold state. For this SQLite fixture, that serializes the competing writers before they make their decisions. A second contention case sends the same capture ID from two connections: both return confirmed, but inspection finds one payment row, one confirmed hold and no compensation obligation. A unique key alone would reject a duplicate insert; the locked read/decision path also lets the later caller return the stored outcome. This is a database-specific implementation, not portable SQL isolation guidance.

A negative control that removes the held-state predicate from cancellation must fail the capture-first case. Both serial orders are checked deliberately because one simultaneous run does not guarantee that the scheduler exercises both outcomes. These bounded cases do not establish starvation freedom, performance under load, process-crash recovery, distributed locking or provider-event authenticity.

## Restart after the separate ledger recorded success

Run a second exercise:

```sh
python3 examples/reservation-holds/compensation_lab.py
```

It creates two temporary SQLite files: the application holds/compensation database and a separate provider-simulator ledger. A child worker submits a stable operation ID derived from the payment ID. The simulator commits one record. The child then exits deliberately with code 23 before updating the application's pending obligation. The parent reopens both databases and verifies this disagreement: provider record present, local work still pending.

A new child retries with the same operation ID. The authored simulator returns the already-recorded outcome, and the worker marks the local row `SIMULATED_DONE`. Inspection proves one provider record remains. Another run does nothing, and reuse of the operation ID for a different payment is rejected. All connections close and the temporary directory is removed. This is an actual process exit and restart around persisted local files, not a network-disconnection test.

The simulator's idempotency contract is deliberately part of the fixture. A real provider may have different key scope, expiration, payload matching, authentication and reconciliation APIs. Verify those rules; do not infer them from this code. If a provider cannot establish the outcome, keep the obligation unresolved and use a reviewed investigation path. A new random ID on every attempt would describe a new operation instead of a retry.

`SIMULATED_DONE` means the local model recorded its effect, not that a customer received money. The worker has no concurrent job leasing, retry scheduler, permanent-error handling, amount/currency rules or notification delivery. The fixture's original payment outcome remains `REFUND_PENDING`; compensation state is a separate record, so a customer-facing projection must reconcile the two before claiming completion.

For a negative control, remove the simulator's lookup of an existing operation in a temporary copy. Its unique key will reject the retried insert, and the worker-restart success check must fail. Uniqueness prevents a second row, but a useful idempotent interface must also let the caller recover the prior outcome. Ask Codex to explain that distinction and identify the provider facts still needed before adapting this design.
