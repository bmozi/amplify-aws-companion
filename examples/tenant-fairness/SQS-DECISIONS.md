# A10: when the AWS queue is fair, what changes?

Maya's portal eventually serves many repair shops. A few shops send long report jobs, and a quiet shop's job spends too long waiting. The [local round-robin drill](README.md) makes one possible scheduling rule visible: it has a four-job waiting limit per shop and a precise dispatch order. **Amazon SQS fair queues do not promise that rule.** This packet is a design exercise, not an AWS deployment or emulator.

On an SQS **standard** queue, a producer can set `MessageGroupId` to a trusted tenant identifier. AWS says this activates fair-queue behavior for grouped messages. SQS detects disproportionate in-flight count or processing-time share and prioritizes messages from quieter groups. It does not promise our toy's A1, B1, A2 order or slot 2; it does not enforce a per-tenant quota, prevent an already-running slow job or validate that the producer used an authorized tenant ID. A standard queue can still deliver duplicates or out of order. The same field on an SQS **FIFO** queue has ordering semantics; do not infer FIFO from a standard queue's `MessageGroupId`. [AWS fair-queue overview](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-fair-queues.html), [how it works](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-fair-queues-detailed.html), [standard queue behavior](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/standard-queues.html).

| Choice | What it aims to improve | What remains your responsibility |
| --- | --- | --- |
| One standard queue without tenant groups | Simple shared work dispatch | Observe quiet-tenant dwell time under bursts; no fair-queue grouping is supplied. |
| One standard queue with trusted `MessageGroupId` | SQS prioritizes quiet groups when it detects a noisy neighbor | Authorize the group ID, handle duplicates/order, monitor customer completion and price the extra fair-queue request meter. |
| Separate queues or reserved workers | Stronger isolation of selected queue/worker contention | More fixed resources, configuration and cleanup; shared database and downstream limits can still dominate. |
| FIFO when strict per-group ordering is required | Ordered processing within a message group | Different throughput, deduplication and pricing decisions; do not choose it merely for the word “fair.” |

The current A02/A03 message source calls `send_message` **without** `MessageGroupId` and its worksheet prices standard SQS requests. Its one synthetic workflow is not a multi-tenant fair-queue test. Adding group IDs to a future design would change the price review: AWS says relevant sends, receives, deletes and visibility changes on a standard queue are charged at **both standard and fair-queue rates** when a grouped message is involved. The existing USD 0.16 SQS scenario line cannot be reused as the whole fair-queue price. Obtain the current selected-Region fair-queue rate and update the full-run estimate before any live trial. [SQS pricing and metering](https://aws.amazon.com/sqs/pricing/).

## Changed cases to answer first

1. Alice signs in for Shop A but submits JSON with `tenant: "shop-b"`. Which component chooses `MessageGroupId`? What does SQS itself know about Alice's membership?
2. The producer sets `MessageGroupId` for half the messages and omits it for the rest. Why is a quiet-group metric no longer a complete customer view?
3. Shop A sends four jobs before Shop B. Can the local fixture's B-in-slot-2 result be promised by SQS? Name the evidence needed to claim a service improvement instead.
4. A shop requires strict in-shop order and duplicate-safe effects. Compare standard fair queues with FIFO and an idempotent consumer. What is decided by each component?
5. A team adds tenant groups to the A02 queue but keeps only the old standard-request price line. Which new meter must be priced? Compare the revised whole-run estimate with a limit chosen for your account; what information is still needed before a live trial?
6. The quiet-group queue-age metric improves, but Shop B's report still finishes late. Trace the next boundary to inspect and the customer-facing observation to record.

After writing your answers, read [assessor reasoning](SQS-ASSESSOR.md). Ask Codex to find a counterexample to “SQS fair queues guarantee every tenant a fast report.” Require it to separate queue dwell time, worker time, shared data and customer receipt, then verify every claimed AWS property against the official sources. No AWS resource or credit is needed for this paper exercise.
