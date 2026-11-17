# Queue recovery: predict the next delivery and the business effect

Original cloud-free cases for [the durable-request lesson](../../reader/BOOK-LOCATORS.md#book-0b7eb9d1bab09ff9). Write your answer before opening [assessor reasoning](ASSESSOR.md). No queue is created or modified. These cases do not extend the Moto suite's executable scope.

For each, separate what the queue can report from what the business knows, identify the next evidence and state a replay or stop condition.

1. **Slow work:** In the lesson's fictional 30-second visibility sequence, A still runs when B receives the same job at second 31. Someone claims the queue has granted B exclusive permission to make a new appointment. Explain the mistake and the role of stable supplier identity. Does a longer timeout prove that no duplicate effect can occur?
2. **Crash before processing:** A message reaches the configured receive threshold, but a worker repeatedly crashes after receipt and before calling the supplier. Explain why the threshold does not count completed business attempts. What evidence distinguishes this from a supplier that accepted work but lost its response?
3. **The wrong correction:** A message lacks a required schema field. An operator proposes resending the same payload and increasing all worker permissions. Describe the diagnosis and approval needed before replay. What if the payload is valid but the intended operation is explicitly unauthorized?
4. **Retention clock:** A standard-queue message was originally enqueued 20 hours ago and moved to a DLQ one hour ago. The DLQ retention is 24 hours. Under the documented original-enqueue expiry rule, what nominal time remains? Would the answer be the same for a FIFO message whose enqueue timestamp reset at the move? The times are fictional; assume no other retention or redrive changes.
5. **Empty does not mean completed:** After a replay, the DLQ is empty. The accepted-work ledger still lists two unfinished requests, and the supplier outcome for one is unknown. Write a bounded recovery statement. List what must be reconciled before declaring the customer's request completed.

Then add fresh production-like work to the paper design. Identify a replay rate/stop policy that protects it, but do not invent a safe numeric rate without workload evidence. Explain what a later authorized cloud test would need to observe that these cases cannot establish.

## Change the number of responsibilities

These additional cases are design-only; the executable below does not simulate SNS or independent subscriptions.

6. **Two applications, one queue.** The scheduler and auditor both require every accepted request. Someone connects both to one work queue and adds more workers when audit records are missing. Explain why this changes capacity without establishing two independent deliveries. Draw the proposed topic, queues and workers; name the completion record for each responsibility.
7. **A misleading healthy result.** J1, J2 and J3 have appointment results. Audit contains J1 and J3 only, and the scheduling queue is empty. State what is known about J2 and whether replaying appointment creation is justified. Identify the evidence and scope needed for an audit-only recovery or a common replay route.
8. **A filter hides required work.** Audit must cover all accepted requests, but its subscription selects only urgent requests. An ordinary request has no audit result and no inspected failed-queue entry. Explain the possible configuration cause, why an empty failed queue is insufficient, and what must supply the omitted event after a reviewed correction. Do not assume a filter update automatically replays history.

## Route by event contents

9. **Different destinations.** A repair application emits appointment and invoice events. Only invoices above a declared amount must reach a finance integration; every accepted request must still reach audit. Compare a shared work queue, a topic with appropriate subscription filtering, and event-bus rules. Draw the selected paths and identify where each obligation is recorded. Then make the finance target unavailable and later change the amount threshold. What must be configured or reconciled before claiming delivery and historical completeness? Do not assume that changing a routing rule replays old events.

Save your first answer before reading the [routing assessor](ASSESSOR.md#routing-case). This is a design comparison; the executable below does not simulate EventBridge, SNS or their retry policies.

## Run the lost-response experiment

A repair shop asks a supplier to book an appointment. The supplier books it, but the reply never reaches the shop. The shop now knows less than the supplier: “I did not get a reply” cannot tell it whether the appointment exists.

From the repository root, run:

```sh
python3 examples/queue-recovery/lab.py
```

Only Python's standard library is needed. The exercise creates a temporary SQLite database, uses no credentials or network, and removes the database afterward. Before running, predict the number of supplier effects in each case:

| Case | What changes | Expected observation |
| --- | --- | --- |
| Unsafe retry | A new operation ID is assigned to each delivery | Two bookings for the same appointment |
| Stable retry | The original business operation ID survives a lost reply | One booking for that request; the retry returns its existing receipt |
| Conflicting retry | The same ID is reused for a different appointment | Rejected; existing effects unchanged |
| Failure before the call | Three scripted deliveries encounter a worker crash | Three receives but zero supplier calls |
| Empty failed-work list | Transport entries are cleared | The business request remains unfinished |
| Reviewed recovery | The injected worker failure is removed | A supplier receipt is obtained before the ledger marks completion |

The program intentionally retains the two unsafe bookings while testing separate safe requests. Its final total of four rows includes those two bad effects plus one each for requests B and C. A passing exercise proves that the negative control detected the duplicate; it does not undo the duplicate or make that unsafe approach acceptable.

```text
Worker sends request B → supplier commits booking + receipt
                               ↓
                         response is lost
                               ↓
Worker knows “unknown” → retry original B → existing receipt
```

The supplier contract does the important work here. Its operation ID is unique, the booking and receipt commit together, and reuse with different appointment details fails. Merely adding an ID to a payload cannot force an unrelated supplier to honor it. In a real integration, verify the supplier's scope, retention period, behavior on conflicting reuse and recovery/query capability. If it cannot provide these guarantees, an unknown outcome may require reconciliation or human investigation before another effect is attempted.

The worker's local state and the supplier's database are deliberately separate. A database transaction in our application cannot roll back an appointment already created in another system. The injected failure happens **after** the supplier commits, so retry handling must account for a real recorded effect rather than assuming failure means nothing happened.

**Evidence boundary:** the supplier is a fictional sequential SQLite implementation. The delivery list is an authored fixture, not SQS polling or automatic redrive. No visibility timer, receipt-handle behavior, concurrent workers, Lambda batch handling, retention expiry, tenant authorization or provider outage is tested. These checks do not extend the Moto suite or establish live AWS behavior. The paper cases above still require separate explanations.

Ask Codex to explain the exact commit point and trace why the unsafe case has two effects. Then ask it what changes if the supplier forgets old operation IDs before our retry arrives. A useful answer identifies the missing evidence and does not promise that a stable key alone prevents duplicates forever.
