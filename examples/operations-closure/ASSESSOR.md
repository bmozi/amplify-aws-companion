# Assessor notes — two incident finish lines

These are answer criteria for invented records, not independent learner scores or AWS evidence. Read after making your own predictions.

1. **Healthy baseline:** Both distinct recent probes succeed; the single stipulated accepted booking has a completion record; the alarm is `OK`; the owner is named; and the failed first delivery has a later acknowledged retry for the *same* transition. Customer recovery and operations handoff both pass the local rule. The three delivery attempts represent two unique transitions.
2. **Green alarm, unfinished booking:** Customer recovery fails because accepted work remains incomplete. Handoff fails with it. Check the exact booking's durable state and any external effect; do not use the alarm's state as the receipt.
3. **Stale or repeated probe:** Two old results are not fresh evidence. Two records for one run are not two independent observations. Check a new request through the affected journey and its resulting business state.
4. **Wrong scope:** A successful probe in another Region cannot close this Region's customer impact. Compare exact account, Region, journey and observation interval.
5. **Missing work row:** The supplied intake set and work export disagree. Even an empty pending count is then untrustworthy. Locate the missing request or prove the intake population is different; do not subtract unrelated counters.
6. **Failed notification:** Customer recovery can pass while the operations handoff stays open. Preserve the failed transition, identify its owner, inspect the route and verify an appropriate retry or alternate notification. The fixture's boolean is not a human receipt.
7. **New alarm transition:** A second `ALARM` transition with a new ID is not a duplicate of the first. It needs its own delivery accounting. Do not deduplicate by a broad incident label that hides a fresh failure.
8. **No owner or alarm still active:** The customer checks can pass while operations still has work. State both facts, the owner gap and the reason the alarm remains active before handoff.

The threshold choices, trusted intake set and simplified in-memory event IDs make this a decision exercise. It cannot verify AWS collection, notification delivery, authorized remediation, actual customer recovery or root cause.
