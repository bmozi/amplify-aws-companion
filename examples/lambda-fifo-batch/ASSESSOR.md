# Answer guide: which envelopes need another attempt?

Read this after making your predictions in the [exercise](README.md). These answers describe `lab.py` and its injected callback, not observations from AWS.

## Follow the first failure

Assume the callback raises `ValueError` at the named record, before making its intended change. Records arrive as A, B and C.

| Callback result | Attempted records | Returned identifiers | Not attempted |
| --- | --- | --- | --- |
| A fails | A | A, B, C | B, C |
| B fails | A, B | B, C | C |
| C fails | A, B, C | C | None |
| All succeed | A, B, C | None | None |

The handler stops immediately when it catches `ValueError`. Its response includes the record that raised the error and the remaining records. It does not claim that the remaining records were attempted. If an unexpected `RuntimeError` escapes instead, this local call raises an exception; it does not produce a successful response with an empty failure list.

An answer that returns only B in the middle-failure case loses track of C, which was never opened. An answer that attempts C after B fails contradicts this model's stop rule. Neither answer should receive credit merely for producing correctly shaped JSON.

## A failed return does not erase a completed action

For the changed case, the first callback appends A, appends B, then raises `ValueError`. The list is now `[A, B]`. The response still names B and C for retry. There is no rollback instruction anywhere in `handle`.

Manually call the handler with B and C again, this time using a callback that appends successfully. The list becomes `[A, B, B, C]`. The second response has no failed identifiers. That empty list tells you the second local call returned successfully; it does not prove that B's business action happened only once.

This is why the time of failure matters. A process can lose its successful reply after changing something. Retrying the request may then repeat the change. The example intentionally provides no durable receipt, transaction or duplicate-prevention mechanism. A real design would need to define the business operation's identity, coordinate the change with its completion evidence, and test failure between those steps. A Python list cannot establish those properties across processes or crashes.

## Explain the limit before proposing the next test

A useful learner answer identifies the attempted sequence, the returned sequence and the surviving side effect separately. It proposes a failure after the change but before the reply, then asks how another attempt can recognize the same business operation. It does not claim that FIFO ordering alone prevents duplicate business effects, or that this local handler configured a queue or event-source mapping.

For an AI-assisted review, give Codex your original prediction and the observed list. Ask it to point to the exact line that would undo or deduplicate the append. There is none. Keep its explanation separate from your own answer, and compare any proposed AWS implementation with the official sources linked in the exercise. No independent learner results have been collected for this guide.
