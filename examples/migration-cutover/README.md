# Migration requires matching meaning, not just matching counts

Run `python3 examples/migration-cutover/lab.py` from the repository root. It creates temporary SQLite databases and a local selection file, then removes them. It requires Python's standard library and makes no AWS calls.

The old schema stores decimal amount strings. The new schema stores integer cents. Predict the results:

1. A faulty converter drops fractional dollars. Row counts match, but business reconciliation blocks selection of that copy.
2. The corrected converter preserves cents. A new source order arrives after copying, so reconciliation still blocks selection.
3. With fixture writes paused, the known missing order is copied. All IDs and amounts match; the local pointer selects the target.
4. A new order is written only to the target. Comparing against the old source now shows that simple rollback would hide that order.

The program also rejects fractional-cent, negative and non-finite amounts under its deliberately narrow schema rule. The financial values are synthetic teaching fixtures, not accounting advice or a production monetary model.

The selection file models a cutover decision; no application traffic, DNS or network connection changes. Writes are sequential and explicitly paused during reconciliation. There is no CDC, conflict resolution, live concurrency or reverse replication. In a real system, validation and switching must account for writes arriving between those steps.

## Catch a write between reconciliation and selection

Run `python3 examples/migration-cutover/write_gap.py` from the repository root. It uses only the Python standard library and temporary SQLite files. First predict the final location of order `late` in two runs:

1. **Unsafe check then switch:** the selector verifies matching stores and pauses. Another thread commits `late` to the old source. The selector still points to the target, which lacks that committed order.
2. **One-process gate:** every fixture writer and the selector share one lock. The selector checks and changes the selected store while holding it. A writer that starts during that interval then reads the new selection and commits `late` to the target.

The first run is a controlled failure, not an accidental test flake. The second establishes only this cooperative in-process rule. A different service, an old mobile client, a scheduled job or an operator with direct database access could ignore it. Name how a real design would stop or account for **every** old-side writer, and which observation would reveal a missed path. Compare a write pause with CDC and a final captured position; neither is implemented here. The [assessor reasoning](ASSESSOR.md#write-gap-assessor-reasoning) keeps the observed stores separate from a production claim.

### Move the gate into one authoritative database

A Python lock belongs to one process. The [database-epoch drill](db_epoch_lab.py) instead puts an `epoch` (a change number) beside the selected store in **one temporary SQLite database**. Two separate connections observe it. Predict where order `late` lands in each path, then run:

```sh
python3 examples/migration-cutover/db_epoch_lab.py
python3 -m unittest discover -s examples/migration-cutover -p 'test_db_epoch_lab.py' -v
```

In the unsafe path, a comparison finishes, a source writer commits `late`, and the selector changes the route afterward. The selected new store lacks that order. In the controlled path, the selector compares and advances the epoch inside one SQLite write transaction. A writer carrying the old epoch waits for that transaction and is refused after the change; a writer using the new epoch writes to the selected new store. The six tests also prove that divergence blocks selection and that a direct old-store insert can bypass the **application** rule after the switch. See the [assessor](ASSESSOR.md#database-epoch-assessor-reasoning) after writing your own explanation.

The stronger boundary works here because route and both store copies live in one SQLite file and participating writers check the epoch **in the same transaction as their write**. The program does not grant or restrict database privileges, capture independent changes, span two databases, settle outside effects, switch DNS or call AWS. An epoch read before a separately committed business write is not the same protection. For a real migration, identify the authoritative write point and every bypass path; choose and test a supported fence or write pause and a final captured change position. Ask Codex to draw a direct old-store writer absent from the diagram and explain what would reveal its order.

Independent challenge: add a currency field and a tax rule without changing historical totals. State which values are copied unchanged and which are recalculated, and why. Then extend the reverse replay for a changed order while preserving both versions and requiring a human conflict decision. Do not delete an order merely to make the comparison pass.

Ask Codex to identify where a row-count check would falsely pass and what evidence the rollback decision needs. Read [the migration lesson](../../reader/BOOK-LOCATORS.md#book-9fb6047993bd4d40) and complete E19.

## Follow a customer through the switch

The first drill changes a local pointer but never sends an application request. This second drill binds a tiny HTTP server to `127.0.0.1`, creates temporary SQLite stores, and lets the same visitor route read whichever store the pointer selects:

```sh
python3 examples/migration-cutover/visitor.py
```

Predict the statuses before running it. A late order on the old source blocks the first cutover attempt. Once the target catches up, `GET /orders/d` returns 200 from the target. The visitor then receives `201` for a new order `e` committed only to the target. A guarded fallback leaves the route on target; a deliberately forced fallback to the old source makes `GET /orders/e` return 404. Returning to the target makes that same order visible. The toy replay then copies `e` back, reconciles both stores and allows the guarded local return; `GET /orders/e` returns 200 from the old source. Compare this path with [the illustrated authority boundary](../../book/figures/migration-return-boundary.svg) and the [assessor reasoning](ASSESSOR.md#customer-route-assessor-reasoning).

This is an intentionally sequential loopback demonstration with a trusted local selection file. A 201 here means the local SQLite write committed before the toy server replied; it is not a claim about a real payment, notification or distributed customer promise. The forced fallback is a negative control, not a recovery recommendation. The server and databases are removed after the run. No DNS, CDC, independent writers, external effect or cloud service is tested.

For transfer, imagine that order `e` also triggered an email and a payment authorization. Which observations would you need before choosing **hold on target**, **repair forward** or **synchronize back**? Ask Codex to list the missing receipts and to separate a request acknowledgment from a completed outside effect. Keep your own first answer and check the model's claims against the recorded local observations.

## Replay before returning

Run `python3 examples/migration-cutover/reverse_lab.py`, then `python3 -m unittest discover -s examples/migration-cutover -p 'test_*.py' -v`. Predict three outcomes before looking at the output: an interruption after one source insert, a complete replay of target-only orders `e` and `f` followed by the same replay again, and an old-source `e` with a different amount. In which cases may the local pointer select the source?

The interruption rolls back the source transaction, so the pointer stays on target. The complete replay inserts two rows, its retry inserts zero, and comparison lets the local guard select the source. The conflict raises an error without overwriting `e`; source selection is refused. Read the [assessor reasoning](ASSESSOR.md#reverse-replay-assessor-reasoning) after recording your prediction. Then change the case: one order was edited on the target, one was deleted, and an external payment authorization has an uncertain receipt. Explain why this insert-only drill cannot decide those outcomes. Identify the writer fence, independently captured change position, effect receipts, reconciliation, owner and tested customer path a real return would need.

This replay is one SQLite transaction on the old store after a static read of the target. There is no atomic transaction across the two stores and no guard that stops another writer between comparison and selection. The test demonstrates a local data rule, not safe AWS or customer rollback.

## Carry the outside effect receipt

Now order `e` also has a fictional 250-cent **authorization request** in a separate provider store. Predict whether matching order databases alone permit the old route to serve customers. Run from the repository root:

```sh
python3 examples/migration-cutover/effect_return_lab.py
python3 -m unittest discover -s examples/migration-cutover -p 'test_effect_return_lab.py' -v
```

The provider fixture commits an authorization and loses its reply. The new application therefore records an unknown outcome. A matching lookup changes that local record to confirmed, but the old application still lacks its operation receipt, so the local return guard stays on target. Copying the exact confirmed receipt to the old record lets the sequential fixture pass. A repeat copies nothing. A changed provider amount or conflicting old-side receipt stops the return. The [two-lane figure](../../book/figures/migration-two-receipts.svg) and [assessor reasoning](ASSESSOR.md#outside-effect-assessor-reasoning) show which observation supports each claim.

For a changed case, the provider lookup is unavailable for an hour while customers keep submitting orders. Write the operator's hold/repair-forward/return decision and the observation that could later change it. Then suppose the old application ignores the copied operation ID and issues a fresh authorization. Explain why the fixture's matching rows would no longer protect the customer. Ask Codex to identify which receipt is a local assertion, which comes from the pretend provider, and what a real provider contract must establish. Check its answer against the files before accepting it.

This uses three sequential temporary SQLite stores. It has no real payment, email, authenticated provider receipt, independent writer fence, concurrent traffic, DNS, AWS resource or customer recovery evidence. A provider authorization is not a charge or refund. A selected real API needs its own idempotency, lookup, retention, reversal and effect semantics reviewed before use.

## Replay an edit and a removal without erasing their history

The insert-only return above cannot carry a changed order or a deletion. Think of a notebook: crossing out an entry tells the next reader more than tearing out its page. This lab records each target change with its expected old revision and value; a removed order remains as a **tombstone** (a marked, non-serving row) so a stale copy cannot silently create the same ID again. Predict the old store and pointer after an interrupted replay, a complete replay, and an identical retry. Then run:

```sh
python3 examples/migration-cutover/versioned_return_lab.py
python3 -m unittest discover -s examples/migration-cutover -p 'test_versioned_return_lab.py' -v
```

The target fixture changes `e` from 250 to 300 cents, marks `f` deleted, and creates `g` at 425 cents. An injected crash after two changes rolls back the entire old-store transaction and leaves the pointer on target. A complete replay applies three changes; an identical retry applies zero. The local return guard compares both materialized rows **and** the change journal, including the `f` tombstone. The focused tests also alter the old value without raising its revision, make a stale independent old-side write, physically remove the tombstone, and corrupt a journal entry. Each stops replay or return without overwriting the conflicting evidence. See the [separate assessor](ASSESSOR.md#versioned-change-assessor-reasoning) after your first prediction.

Changed case: the target updates `e` again after this program reads its journal but before the pointer changes. Explain why the earlier match can expire. Identify the real writer-fence or final captured change position, the independent reconciliation and the customer read that would be required. Then add an email sent for deleted `f`: what separate outside-effect record is needed, and why does the tombstone alone not retract the email? Ask Codex to challenge your plan and classify each observation as fixture data, independently confirmed effect or customer result.

This fixture **supplies** the change journal; it does not implement or validate CDC, schema conversion, source authority, cross-store atomicity, concurrent writer fencing, external effects, DNS or AWS. The guard is sequential and can be invalidated by another writer immediately after its comparison. It teaches a necessary data distinction, not a production return procedure. It uses only temporary local SQLite files and no credits.

## Choose the transfer and access model

These six additional cases are design-only and do not modify the local drill. For each, state the business outcome, candidate, rejected alternative, missing observation, cost drivers and cleanup/operating owner. Read [assessor notes](ASSESSOR.md) after answering.

1. A shop will retire its NFS server after moving a selected drawing collection to supported AWS storage. Compare a transfer task with operating a continuing gateway. Identify the final write boundary and evidence needed before retirement.
2. A legacy application must continue using an SMB share while its data resides in S3. Explain why a one-time copy alone does not provide that access path, and which gateway compatibility/outage assumptions need testing.
3. A task verifies every file in its supplied manifest. The manifest omitted the archive directory the business needed. What succeeded, what failed, and which independent inventory would reveal the difference?
4. An application has written through a gateway while the WAN is disconnected. An operator wants to remove the gateway because the write returned successfully. Name the persistence and recovery evidence needed before removal.
5. Two gateways write the same files; someone promises that refreshing both caches guarantees coordinated edits and full offline access. Separate the two unsupported claims and propose a safer ownership/test plan.
6. An active database's files are copied without an application-consistent boundary. Their transfer checksums match. Decide what this establishes and what is needed before opening the target application.

Transfer: the retirement project becomes recurring daily delivery to an analytical dataset. Reconsider scheduling, source changes/deletions, independent manifests, destination publication, access, failures and total cost. A repeated transfer is not automatically a transactional replication protocol. This exercise contains no live transfer benchmark or learner assessment.

## Choose the lowest-cost valid transfer

A repair business must copy 6 TiB and one million files from an office file server into S3 within ten days. The office internet circuit is 200 Mbit/s, but employees share it. The business expects changes during the copy and requires integrity evidence before it retires the source.

Compare a direct supported client transfer with AWS DataSync. For both, list the source/network, service or agent, destination request/storage, verification, retry, operator, overlap and cleanup costs. Show which figures need current regional prices and which need measurement or an office contract. Calculate the ideal transfer-time lower bound at 200 Mbit/s, then explain why it is not a completion promise. Decide whether a continuing Storage Gateway belongs in the comparison; state what ongoing file-access requirement would make that option valid.

Do not invent AWS rates. If the available evidence cannot establish which option costs less, say what quote, price input or measurement would settle the choice. A valid answer must first meet the ten-day business window and correctness requirement; a cheaper design that cannot do so is not the winner.
