# Assessor notes: booking bulkhead

Give these after the learner predicts the cases. These are fixture results, not AWS measurements.

| Case | Booking interval | Meets end-of-minute-3 promise? | Reports unfinished at minute 3 | Cause |
| --- | --- | --- | ---: | --- |
| Shared two-worker queue, DB capacity two | 4–5 | No | 4 | Both workers and database slots are occupied when booking arrives. |
| One worker per lane, DB capacity two | 1–2 | Yes | 4 | Booking has its own worker and the second database slot. |
| One worker per lane, DB capacity one | 4–5 | No | 4 | The running report holds the only database slot through minute 4. |

Priority is applied only when a running job finishes. It cannot evict report work already in progress. The third result is the counterexample: separate worker names alone do not isolate a shared scarce dependency. The second case also does not make report work disappear; its backlog still needs an owner, retry policy, status promise and cost model. A learner who suggests a bounded report queue, smaller report database hold time, separate read path or additional measured database capacity should identify how to test that choice and its cost/consistency tradeoff.

If booking arrives at minute 0, the model's booking-first tie rule starts it immediately even with shared workers. That changed case passes, but says nothing about a booking arriving after reports have taken both slots. Reject an answer that generalizes from one favorable ordering, claims full cell isolation, assigns a real Lambda concurrency value from this toy scale, or calls the printed result a live failure test.
