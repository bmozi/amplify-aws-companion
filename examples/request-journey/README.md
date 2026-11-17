# Follow one repair request from receipt to result

Maya submits a repair request. The first reply says the shop **received** it. It does not promise that a technician has been booked. When the scheduling worker fails, she can still look up her receipt. After the worker recovers, the same lookup shows that this lab recorded an appointment.

This local exercise joins a loopback HTTP customer path to the existing [A02 domain implementation](../../architectures/reliable-workflows/src/domain.py). It uses Moto's in-memory DynamoDB and SQS emulation. It creates no AWS resources, uses no account credentials and has no cloud bill. Read [Unit 27](../../reader/BOOK-LOCATORS.md#book-0b7eb9d1bab09ff9) first.

```text
synthetic actor -> local POST -> request + pending outbox -> manual dispatcher
       |                    |                         |              |
       |                    v                         v              v
       +----------- local GET status             durable obligation  emulated SQS
                                                                  |
                                                                  v
                                                    emulated worker + appointment row
```

From the repository root, run:

```sh
.venv-labs/bin/python examples/request-journey/lab.py
```

The runner chooses an ephemeral port on `127.0.0.1` and closes the server when finished. The local-only `alice-local-token` and `bob-local-token` strings stand in for identities. They are source-visible fixtures, not secrets or production authentication. The server derives the actor from its token mapping rather than accepting an actor in the request body. This demonstrates the placement of the read boundary; it does not test Cognito, IAM, browser security, session expiry or real customer authorization.

| Observation in the JSON | Meaning |
| --- | --- |
| `accepted` is HTTP 202 and `received_processing` | Intake stored the request and outbox obligation together; simulated scheduling has not completed. |
| `same_retry` reuses the receipt | The same actor, request ID and text describe the same intended work. |
| `accepted_at_epoch` is unchanged on acceptance, retry and outage read | The request stores the first server-sampled acceptance second; retry does not restart the clock. It is not an exact remote commit time or proof that a person was contacted. |
| `changed_retry` is HTTP 409 | One request ID cannot silently become a different repair. |
| `other_actor_denied` is 404; `anonymous_denied` is 401 | The local status route does not reveal Alice's record to Bob or an unknown fixture token. |
| `pending_after_dispatch_gap` is true and `transport_messages` is two | The first send happened, then acknowledgement failed; retry sent a second transport message for one business request. |
| `during_outage` still says `received_processing` | Failure did not erase acceptance or invent an appointment. |
| `at_contact_deadline` is empty; `new_overdue_work` has one item | A manual check of the same Moto table applies the fictional inclusive one-hour rule. |
| `repeat_due_check` is empty; `open_after_lost_check_reply` still has one item | No newly opened item does not mean there is no outstanding work. Read the open worklist independently. |
| `fixture_contact_record` is late; `open_after_contact_record` is empty | A trusted local fixture records first contact at hour four. It removes open work but neither makes nor proves real human contact. |
| `completed` says `appointment_recorded`; `appointment_count` is one | Both messages can be processed, yet the transactional simulated effect occurs once. |

The runner asserts those relationships. It does not measure load, real SQS ordering, actual IAM enforcement, live concurrency or Lambda redrive. The appointment is a record in the same emulated database transaction as DONE. A real supplier call could succeed while its reply is lost; that uncertainty needs a supplier operation key and reconciliation path. This exercise also bypasses a real browser and Amplify hosting. The manual dispatcher and contact checker can leave accepted work pending until an operator invokes them and follows every cursor.

## Look ahead before the one-hour promise

An overdue checker is a rear-view mirror: the one-hour promise is already broken when it first opens work at second 3,601. The [pre-deadline diagram](../../book/figures/contact-before-deadline.svg) adds a separate view at minute 45, while keeping the same immutable acceptance clock. Run the cloud-free continuation:

```sh
python3 examples/request-journey/predeadline_lab.py
python3 -m unittest discover -s examples/request-journey -p 'test_predeadline_lab.py' -v
```

The disposable SQLite drill shows two accepted requests at second 0. At minute 45 both are due soon. A supplied first-contact record for one at exactly second 3,600 meets the *fixture time rule*; the other stays due soon at that instant and overdue one second later. The returned list is a read, not an alert or an operator claim. Its cursor must be followed: a 25-request changed case needs two pages. The `run_watchlist_pass` continuation simulates a worker stopping after page one: no new completion receipt is written. A subsequent walk reaches the terminal cursor and stores its supplied completion time, page count and item count. `sweep_health` marks a missing receipt `unknown` and an old one `stale`; none of these fixture times is authenticated or delivered as an alarm.

Try the second changed case in the tests: insert a request with an earlier deadline after page one. It sorts *behind* the cursor, so the terminal-page receipt says 25 items although a fresh pass finds 26. The receipt proves traversal of those pages, not a simultaneous view of every request. Restart and reconcile against a durable source before relying on it for a deadline promise. This local model does not run a real watchdog, snapshot DynamoDB, or prove timely customer contact.

### Repeat the watchlist from the beginning

Run `python3 predeadline_lab.py` from this directory and inspect `repeat_pass_comparison`. After an interrupted walk and a recovered complete walk, the demonstration inserts one more invented request behind the next walk's first cursor. That first completed pass reports 26 observed IDs; a fresh pass from the beginning reports 27 and lists `arrived-during-repeat-demo` under `repeat_only`. The two receipts have separate supplied completion seconds. The code compares IDs, not just counts: a count could stay at 26 while one request disappears and another arrives.

The result is a *difference to investigate*, not an automatic call or proof of an empty worklist. Run `python3 -m unittest -v test_predeadline_lab.py` to see both the behind-cursor case and the counterexample in which both passes agree but neither becomes a contact or snapshot receipt. Change the fixture so another earlier-deadline request arrives behind the **repeat** cursor. Predict what the comparison misses and which later independent observation should expose it. A live design needs a repeated discovery cadence, durable acceptance source, monitored traversal, responsible operator and separate evidence that Maya was reached before the deadline. An AWS `Scan` must follow every `LastEvaluatedKey`; even strong item reads do not make the whole scan a snapshot. More complete passes add reads and may contend with customer work, so price and measure that path before enabling it. [AWS Scan API](https://docs.aws.amazon.com/amazondynamodb/latest/APIReference/API_Scan.html), [scan performance guidance](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/bp-query-scan.html).

Before opening the [assessor](ASSESSOR.md), change the lead time from fifteen to five minutes. Can an operator who needs ten minutes to investigate and reach Maya meet the promise? Then let the checker stop after page one of 25 while its screen reports no new *overdue* items. Which requests have not been examined, and what independently observed signal would bring that failure to an operator? Now explain why the inserted 26th request can be missed even by a completed pass. Ask Codex to propose a schedule and alert, but require it to keep cursor traversal, current-work reconciliation, operator pickup and customer contact as separate facts. None is deployed here. A selected cloud design must price repeated reads, compute, schedule, alert delivery, logs, retention and cleanup. Choose whole-run spending and reserve limits for the account you will use.

## Claiming an overdue ticket is not contact

Imagine the paper overdue tray has Maya's ticket. Operator A writes their name on it for one minute. That helps the *local* desk avoid two active owners, but it does not call Maya. The [four-fact diagram](../../book/figures/contact-claim-boundary.svg) shows what the desk can and cannot know.

Run the disposable SQLite continuation from the repository root:

```sh
python3 examples/request-journey/operator_lab.py
python3 -m unittest discover -s examples/request-journey -p 'test_operator_lab.py' -v
```

It starts with the separate [contact clock](#check-the-contact-clock): acceptance at second 0, overdue work at 3,601, then a claim at 3,610. The same operator's retry returns the same claim. A rival cannot claim while its short interval is active. A matching first-contact attestation at second 3,650 closes the local open item but remains **late** against the one-hour promise. If that write's reply disappears, repeating the same attestation returns the original record; changing its contact time is refused. In a second request, the claim expires, a replacement gets a newer generation, and the former operator's stale claim cannot clear the work.

The fixture operator IDs and contact times are trusted inputs visible in source. There is no login, phone call, alert, customer acknowledgement, distributed lock or AWS service. The SQLite transaction serializes this one local store; it does not prove multi-host behavior. A claim expires without canceling a human's possible phone call. Before the replacement makes another call, reconcile the earlier operator's notes and customer outcome; keep the request open when those facts are unknown. The local lease is **not** a deadline extension, customer-contact receipt, or budget control. A later cloud design would need scoped operator identity, durable audit, observed notification delivery, missing-reply reconciliation, retention, and selected-service cost and cleanup review. Choose whole-run spending and reserve limits for the account you will use.

Before reading the [assessor](ASSESSOR.md), change two facts: (1) Operator A says they called Maya just before the lease expired, but their write fails after the replacement claims. Does a stale-write rejection prove no call happened? (2) The first attestation succeeds, but its reply disappears and the retry carries a different contact second. Which record remains authoritative, and why must the new timestamp be rejected? Ask Codex for the timeline, then label every statement as local storage, supplied operator claim or observed customer outcome.

## Check the contact clock

The A02 request record keeps its first server-sampled `accepted_at` second. Older records without that field remain unknown; the local HTTP route returns `null` rather than inventing a time. Its private domain methods create first-contact and escalation items in the same emulated DynamoDB table. `check_contact_due` evaluates at most 20 table items per page; a page can have no matching requests and still return `next_cursor`. Follow every cursor, then repeat a pass to catch later or changed work. `read_open_contacts` independently scans for unresolved escalation items; it too can return an empty page with a cursor. The default-off Terraform candidate exposes only those two review methods through a private Lambda, with no installed schedule or contact-record action. A contact time supplied by the local fixture is not evidence that Maya actually heard from anyone. For a simpler view of the same decisions, run the **separate disposable SQLite exercise**:

```sh
python3 examples/request-journey/deadline_lab.py
python3 -m unittest discover -s examples/request-journey -p 'test_deadline_lab.py'
```

This fixture starts Maya's acceptance clock at second 0. A same-ID retry at second 200 keeps that original time. The inclusive one-hour deadline is second 3,600: contact recorded then is on time. At second 3,601, the checker records her request for an operator. A repeated check does not create another item. Imagine the checker printed a new-work slip but the slip fell behind the desk. Its next printout is empty; that does **not** mean the drawer of open work is empty. `read_open_worklist` reads that drawer again, including Maya's item. Contact first recorded at hour four remains late. [The timeline](../../book/figures/contact-deadline-boundary.svg) separates the clock facts.

The checker records at most 20 **newly** overdue items per invocation by default. If more are due, invoke it again until no new records appear. Then read the still-open worklist independently. `read_open_worklist` returns at most 20 open rows per page and a `(accepted_at, request_id)` cursor for the next page; restart from page one after handling a batch. A recorded contact removes the item from the open view while retaining its escalation history. A contact that happened late remains late. The database exists only in this process's memory, so a process exit erases it. The page traversal is not a concurrent or distributed snapshot. This exercise does **not** schedule itself, notify anyone, assign an operator, contact the customer or prove a live AWS deadline. A production design needs durable accepted and contact timestamps, a monitored repeated check, delivery and ownership evidence, and reconciliation after missed checks. Its selected request/index/read, scheduler, alert, log and retention meters belong in the whole-run cost review. Do not infer those controls from the JSON output.

Before reading the assessor, predict this failure: the 3,601-second check commits its escalation row, but its reply disappears. The 3,602-second check returns no *new* rows. Which query still finds Maya? Why would interpreting an empty new-row response as an empty open worklist miss her? Now accept 25 fictional overdue requests and follow both pages of the open worklist. The seven focused tests include those two cases.

Before reading the [assessor](ASSESSOR.md), change the case: contact is recorded at exactly second 3,600; then imagine the checker never runs until hour four. Which customer promise was met in each case? Which operation is merely monitoring? Ask Codex to identify an observation that would distinguish “checker ran” from “person contacted Maya,” and verify the answer against the stored fields.

Try another changed case before reading the [assessor](ASSESSOR.md): Alice submits while the worker is down for four hours. Which A02 items help an operator find her request and overdue work? Which contact facts are only trusted fixture entries, rather than observed customer outcomes? Decide whether a receipt alone is an acceptable customer experience. Then ask Codex to trace the path and propose one failure test; require it to identify what the test cannot prove in live AWS.

For a cloud version, inventory the complete request, queue, scan/read, transactional write, log, retry, schedule, alert and cleanup meters first. A default-off private Lambda candidate now exposes `check_due` and `read_open`, with its own server clock; it has no contact-record action, schedule or customer notification. The guarded runner requires matching `contact_worklist_mode: manual_review`, six positive contact-specific meter rows, a named operator, planned invocation counts, cursor/follow-up procedures and cleanup timing before this opt-in path can be planned. The [contact worksheet](../costs/contact-worklist-worksheet.json) gives those rows but remains pending with blank contact quantities and prices; it is not a selected live-run estimate. Its base and contact rows must be disjoint. Before a live run, choose a whole-run estimate limit and credit reserve appropriate to the account, then verify current prices and credit eligibility. The existing A02/A03 cloud gate remains separate from this zero-cost local exercise.

For a changed case, accept 25 invented requests and let the first due-check reply disappear. Follow every returned cursor on the retry and then read every page of open work. The [private handler tests](../../architectures/reliable-workflows/tests/test_domain.py) exercise those paths through Moto, while [Terraform's mock-provider tests](../../architectures/reliable-workflows/infra/tests/contact_worklist.tftest.hcl) check that the opt-in function has no automatic trigger. Predict what a reader would miss by treating an empty *newly opened* page as an empty worklist, then use the [assessor](ASSESSOR.md) to check your reasoning. Neither test records human contact or sends a notification.

The due checker needs a request key and its acceptance clock, not the repair description. Its DynamoDB scans and follow-up request read use projections so the invented `text` attribute is not returned to this workflow; a local test inspects the responses. The role still has table-level permissions, and projection does not reduce read capacity for the evaluated items. Price the whole scan, including unrelated records and repeats. [AWS Scan capacity and projection](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/Scan.html).
