# A10: one shop fills the shared worker queue

Shop A submits four reports before Shop B submits one. First ignore duration and count the order in which one worker starts jobs; each numbered slot is a dispatch, not a time unit. Run `python3 examples/tenant-fairness/lab.py` from the repository root. Then run `python3 -m unittest discover -s examples/tenant-fairness -p 'test_*.py' -v`.

The FIFO comparison gives Shop B slot 5. The local fair scheduler keeps a separate bounded waiting line for each shop and rotates among nonempty lines, giving Shop B slot 2. Shop A's fifth waiting job is rejected while Shop B can still submit. The code does not silently discard an accepted job; callers must handle rejection with an appropriate retry or customer message. Notice that this fixture counts *waiting jobs*. A real design must separately limit in-flight work and account for retries.

Now give each Shop A report an **assumed** 600-second duration and B's report an assumed one-second duration. One non-preemptive worker starts them in the selected order. Round robin finishes B at virtual second **601**; FIFO finishes B at virtual second **2401**. Moving B to slot 2 removes 1,800 seconds from this invented timeline, yet B still waits ten minutes behind A1. These are arithmetic under stated assumptions, not measured cloud latency or a service-level promise. The lab prints the assumed durations and both start/finish times so the claim can be checked.

This is a scheduling model, not tenant authorization. The `tenant` argument stands for a server-verified value; exposing `submit()` as a public endpoint that accepts an arbitrary shop name would let a caller impersonate another shop or evade its quota. The [tenant access drill](../tenant-isolation/README.md) handles a separate local query/cache boundary. Neither drill verifies Cognito, IAM or a cloud queue.

## Change the case before reading the assessor

1. Change A1 from 600 seconds to 1,200 seconds while keeping A2–A4 at 600. Recompute B's fair and FIFO finish times. What customer promise can no longer be inferred from “slot 2”? Name a control or measurement that would address elapsed wait.
2. Shop B submits its job only after Shop A's first job has started. What is the earliest dispatch slot in this non-preemptive model? Why can the scheduler not undo already-started work?
3. The worker dispatch order is fair, but all reports query one overloaded database. Does the end-to-end response time follow the dispatch order? Where would you measure Shop B's actual outcome?
4. Shop A receives a rejection and retries immediately with a new job ID. Which admission state must be shared across worker instances so the limit is meaningful? What should a retry response say?
5. A signed-in Shop A user sends a request body naming Shop B. What must establish the queue key, and where should the mismatch be rejected?

Compare this per-tenant queue with two alternatives: one global FIFO, and dedicated worker capacity for a customer whose contract requires stronger isolation. The shared fair queue saves dedicated capacity but still shares worker and database failures. Dedicated capacity adds fixed cost and operational work. The right choice depends on measured latency targets, job sizes, tenant count, demand and contract terms—not the word “SaaS.” Read [assessor reasoning](ASSESSOR.md) after writing your own answer.

Ask Codex to propose a counterexample to the statement “round robin guarantees every shop fast reports.” Require a timeline with job lengths, a named bottleneck and a measurable customer outcome. Check its timeline yourself; a plausible AI answer is neither a load test nor a service-level result.

Before an AWS version, choose actual services, estimate the whole bounded run against spending and reserve limits chosen for the account, use a scoped non-root identity and plan cleanup. This local fixture uses no AWS resources or credits.

## Carry a trusted tenant label across a message boundary

The scheduling drill assumes someone has already decided which shop owns a job. The [message-boundary drill](message_boundary.py) tests that earlier decision. Run `python3 examples/tenant-fairness/message_boundary.py`, then the test command at the top of this page. It uses public fixture actors and a temporary SQLite file; it does not send an SQS message.

Alice submits a report request with `request_id=same-id`. The server-side fixture maps Alice to Shop A and writes an accepted request. Bob can use the **same** ID for Shop B without sharing the effect. A supplied `claimed_tenant=shop-b` from Alice is rejected. The returned envelope has `MessageGroupId=shop-a`, chosen from the fixture membership, not copied from her request body. A worker checks that the envelope points to an accepted tenant-scoped request and records one local database effect. Delivering the same envelope twice still records one effect.

| Boundary | What this fixture proves locally | What an AWS design must still prove |
| --- | --- | --- |
| Request to accepted record | Unknown or conflicting fixture identity cannot create a request; a repeated ID with changed content is rejected | Real authentication, membership freshness, request authorization and rate/admission limits |
| Accepted record to message | A reopened process can list pending envelopes after an imagined lost send | An actual outbox publisher, retry policy, SQS send result and poison-message handling |
| Message to database effect | A tampered group or unknown request is rejected; duplicate delivery changes this one SQLite effect only once | Protected worker access, distributed concurrency, external-effect idempotency and reconciliation |

This is a small version of the **outbox problem**. If the application acknowledges a request and then crashes before sending to SQS, the accepted work needs a recoverable record. `pending_envelopes()` shows that record after reopening the database. It is *not* a complete outbox publisher: it has no claim/lease, sent acknowledgement, retry backoff, dead-letter handling or cloud delivery. A real publisher can resend after an uncertain response, so the consumer still needs a stable business idempotency key. [AWS standard queue delivery](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/standard-queues.html).

Work these changed cases before reading the [assessor](MESSAGE-BOUNDARY-ASSESSOR.md):

1. Alice changes the browser field to `shop-b`. Which value must determine the SQS group, and what must reject the mismatch?
2. The accepted database write commits but the process loses the send reply. Which record lets a new process retry? Why could the worker see two deliveries?
3. Alice and Bob both use `same-id`. Which key prevents their reports from colliding?
4. A worker updates SQLite and then emails a report. It crashes after the email and before recording completion. Does this drill prove one email? Design the extra effect/reconciliation boundary.
5. Alice's membership is revoked after acceptance. Should the already accepted report run? State whether this is a user-delegated action or a separately authorized tenant workflow, and identify where that policy is checked.

Ask Codex to change one fact at a time and identify the exact assertion that would fail. Require it to distinguish `MessageGroupId` as SQS scheduling metadata from application authority. The fixture is not a fairness benchmark or evidence of SQS activation. Standard SQS queues may redeliver and reorder messages; `MessageGroupId` on a standard queue does not add FIFO ordering. [AWS fair-queue behavior](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-fair-queues.html), [AWS standard queue delivery](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/standard-queues.html).
