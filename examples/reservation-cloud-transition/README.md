# A03 to expiring holds: a cloud design review

This is an architecture review of a **partial experimental source path**, not a deployed timed enrollment service. First run [A03's Moto tests](../../architectures/reliable-workflows/README.md) and the [local hold exercise](../reservation-holds/README.md). Read `architectures/reliable-workflows/src/domain.py` beside the tests, then write your answers before reading [assessor reasoning](ASSESSOR.md). Use invented people and payments only.

Maya's workshop has one seat. A03's original action confirms it in one DynamoDB transaction. The new product request says: “Hold a seat for ten minutes while a separate payment provider responds. If the customer does not complete payment, let someone else have it.” That sentence changes the data contract. An A03 `CONFIRMED` row cannot simply gain a TTL attribute and become a hold. The source now has separate hold actions and two **manual** expiry-discovery paths, and a default-off Scheduler candidate, but no payment provider or live timed-service evidence; evaluate those gaps as part of the exercise.

## Draw the state and authority first

Draw the path from verified customer identity through the hold API, authoritative capacity/hold records, provider event receiver, compensation obligation and customer status view. For every arrow, name the actor allowed to write it. The existing A03 `actor` field is only a trusted lab label; it is not customer authentication. Make the course, customer, hold ID, payment attempt ID and provider event ID different identifiers. Say which can be retried and which can be reused for a new purchase.

Choose and defend an expiry rule. For this exercise, `now >= expires_at` makes a still-held seat ineligible for confirmation. The timestamp must come from a trusted service-side policy, not a browser field or an event's claimed creation time. Record where that clock is sampled and what can happen between sampling, sending a write and committing it. An exact real-time cutoff across a remote service is a stronger claim than a successful conditional database write alone can prove.

Compare two bounded designs: (a) keep immediate confirmation and take payment afterward, with an explicit unpaid-seat policy; (b) introduce `HELD`, `CONFIRMED`, `EXPIRED` and `CANCELLED` states with capacity release and a late-payment compensation path. Pick one for Maya's stated ten-minute promise and identify the business fact that could reverse your choice.

## Produce a transaction worksheet

Complete this table for **acquire, confirm, expire, cancel, duplicate event and late capture**. Include the exact old state required, the capacity change, the durable result, the external effect, and the observation needed after an ambiguous timeout. A conditional write must protect the state being changed; a read followed by an unconditional write does not do that.

| Operation | State condition to define | Capacity change to justify | Ambiguous-response question |
| --- | --- | --- | --- |
| Acquire | No prior hold under this stable request identity; capacity available | Consume once | Did the first request commit? |
| Confirm | Still `HELD` and eligible under the chosen time policy | None; held seat is already counted | Did confirmation commit before retry? |
| Expire | Still `HELD`; deadline reached under the chosen policy | Return exactly one | Did another worker already release it? |
| Cancel | Still `HELD` under this exercise's cancellation policy | Return exactly one | Did confirmation win the race? |
| Duplicate capture | Same provider event/attempt and payload | None | Which earlier outcome was recorded? |
| Late capture | Expired/cancelled hold; valid provider evidence | None | Is compensation pending, attempted or confirmed? |

On a proposed DynamoDB implementation, place the hold-state transition and capacity adjustment in one conditional transaction. Do not put two actions for the same item in one `TransactWriteItems` request. Show what happens when the condition fails: reread the authoritative state and distinguish a business rejection, a successful earlier retry and an unresolved service error. Specify how workers discover expired holds without assuming that background TTL deletion occurs at the exact deadline. Preserve enough history to recognize duplicate events after housekeeping; deleting the only identity record can make a repeat look new.

## Changed cases to answer

1. Alice's hold expires at second 10. Bob is rejected at 9, succeeds at 10, and Alice's provider reports a capture at 11. What may be shown to each customer, and what obligation remains?
2. Two expiry workers read the same `HELD` row. Both try to release it. Which condition prevents the capacity count rising twice? What do they do after an uncertain response?
3. Cancellation races with confirmation. Work both commit orders. Which operation may return capacity, and what must the loser observe?
4. A provider sends the same capture ID twice, then sends a distinct successful capture for the same hold. Why are those different cases? Name the durable key and pending obligation.
5. An expired DynamoDB item remains in the table past its TTL timestamp. Does that keep the seat unavailable? Conversely, if TTL deletes the sole hold record, what retry evidence disappears?
6. A Lambda samples `now=9.999`, then its transaction commits after second 10. Its condition compares `expires_at` with that sampled value. What did the transaction prove, and what did it **not** prove about the wall-clock promise? Propose a reviewed acceptance margin or a stronger time-authority design before claiming exact cutoff behavior.
7. The refund worker sends a request and loses the reply. What provider-specific idempotency/reconciliation evidence is needed before trying again or telling the customer the refund completed?
8. The manual sweep's first page evaluates five unrelated records and returns zero matches plus a cursor. A second worker releases the due hold after a later page is read but before its conditional write. What should the operator do with the first cursor, and what may the later page report? Explain why a completed pass may need another pass and why filtering does not make unrelated reads free.
9. The `query_due` index returns only keys for up to five due holds, but a hold created just before the query is absent from that page and a completed hold still appears. What may the index prove? Why does the worker reread the base item and retain a conditional transaction? How will you discover pre-index holds without `due_partition`, and what extra index write/storage costs belong in the estimate?
10. Sixteen holds are due. The manually invoked `query_due_tick` handles at most three five-entry pages. Its first call reports `page_limit_reached=true`; its second reaches the visible index end. Then inject a failure while processing page two of a fresh seven-hold run. Which holds may already have been released, what should the caller see, and why is a whole-pass retry safe? Distinguish the hold deadline, a proposed recurring tick and the separate two-hour lab stop. Design a bounded Scheduler delivery/failure route and whole-run cost review, but do not describe it as installed or as an exact deadline guarantee.

Submit a one-page architecture decision, the six-row transaction worksheet, two competing timelines, a failure/observation table, and a cost/cleanup inventory. Compare each proposed condition with the current source; mark missing pieces, including opt-in scheduling and failure observation, index lag/reconciliation, provider evidence and exact-deadline semantics. Count scan or index-query pages, base reads, index writes/storage, transactional reads/writes, repeated attempts, logs, retained history, queue/workflow use and provider fees where applicable. Price a future whole run for the selected Region and account before proposing AWS execution; this packet authorizes none. A live lab needs a scoped non-root identity, account-appropriate spending and credit-reserve limits, and teardown and billing evidence. Do not put real payments or customer data in the lab.

Ask Codex to challenge your proposed transaction with a second expiry worker and a late provider event. Require it to identify the **specific condition and durable key** that blocks each duplicate effect. Check the answer against the local fixture and current AWS documentation rather than accepting a confident diagram.

AWS references: [DynamoDB transaction actions and limits](https://docs.aws.amazon.com/amazondynamodb/latest/APIReference/API_TransactWriteItems.html), [transaction isolation and reads](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/transaction-apis.html), [TTL timing](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/TTL.html), [working with expired items](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/ttl-expired-items.html).
