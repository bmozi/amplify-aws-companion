# Retry-budget assessor reasoning

The all-failing two-layer path makes `3 × 3 = 9` supplier calls. One inner three-call sequence takes `2 + 1 + 2 + 2 + 2 = 9` seconds: three two-second calls and one- and two-second waits. Three such sequences plus one- and two-second outer waits take `9 + 1 + 9 + 2 + 9 = 30` seconds. At the exercise's invented USD 0.001 per supplier call, 100 requests cause 900 calls and USD 0.900 of that one modeled meter. They produce zero completed repairs. Cost per completed repair is **undefined**, not zero or USD 0.001.

One three-call worker sequence takes nine seconds, produces 300 calls for 100 all-failing requests and a USD 0.300 modeled subtotal. It still completes **zero** repairs. The shared three-call limit also stops at nine seconds despite both retry-capable layers. This is a lower failed-work subtotal, not proof of availability, overall lower cost or customer success.

If call three succeeds, three bounded calls complete the modeled request at nine seconds; forbidding every retry would lose that successful case. A permanent permission denial stops after one call and two seconds; retrying it under the same unchanged authority cannot fix the permission boundary. With an eight-second deadline, a third two-second call after the waits would finish at nine seconds, so the model stops after two calls at five seconds, before the unnecessary wait. A real deadline must account for network and upstream processing as well as the downstream call.

Do not award a safe-retry claim for a lost reply after an external effect. The model counts attempts only and has no durable operation IDs, supplier lookup, idempotency, concurrency, customer receipt or actual bill. A strong answer names the provider's replay/lookup contract and an evidence owner, and leaves the result unresolved when that contract is absent. It also notices that SDK, queue and workflow retries can add layers beyond the two shown here.

This deterministic local calculation is not a resilience benchmark, AWS cost estimate or live test.

## Jitter follow-up

An adequate answer separates retry-start concentration, total work, customer outcome and the deadline. For the default seed the peak bucket falls from 20 to 12, total calls rise from 60 to 80, and successful operations remain zero by construction. Do not award a claim of improved AWS reliability, lower costs, safe replay or measured capacity. The deadline includes each call's duration; the initial request is included in the four-call allowance. Identical random draws preserve synchronization. A different seed can change this example's concentration, so a single favorable sample is not a guarantee.

Transfer question: a payment service times out after it may have charged the customer. Would adding full jitter make a second charge request safe? No: delay does not settle the unknown external effect. Require an operation identity and the provider's replay/status contract before considering another attempt. A reader who explains only the backoff arithmetic has not yet demonstrated that safety boundary.
