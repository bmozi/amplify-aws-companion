# Assessor notes: migration portfolio

These are authored reference judgments for the fictional packet, not observed learner responses or a live AWS migration. Give credit for a different defensible strategy when its dependencies, owner, cost scope and acceptance evidence are explicit.

## Baseline reasoning

| Workload | Provisional choice and wave boundary | Evidence that changes the decision |
| --- | --- | --- |
| A. Booking portal | Rehost or replatform are candidates, but **no wave date** until identity fallback, payment retry, schema/data reconciliation, 5-minute interruption and 30-minute recovery are tested. A refactor is possible only with added scope and time. | Observed identity and webhook paths, vendor/license fit, rollback after new payments, rehearsal timings and business-owner acceptance. |
| B. Nightly report | Replatforming its data path may fit, but moving before A requires a tested read route to the authoritative old database and exact totals. Group it with A if the data contract cannot bridge versions. | Real table/column use, permissions, reconciliation, schedule and source/target compatibility. |
| C. Drawing archive | Transfer then retire the old share only after inventory, readable representative files, retention and retrieval checks. Its strategy may be replatform for storage, but “retire” applies to the old server only after user acceptance. | Actual access pattern, small-file/request costs, transfer time, metadata/permission behavior and retrieval target. |
| D. Controller | Retain the on-site component now while assessing vendor replacement or repurchase before support ends. A cloud-only plan would contradict the observed physical interface. | Vendor-supported alternatives, safety-label workflow, support date and recovery plan. |

An acceptable tracker can be Migration Hub or a maintained project record. It must name data sources, owner, stale-status handling and decision use. A dashboard's completion marker cannot prove business acceptance.

The simple 12-month arithmetic is A: current `$12,000`, candidate `$7,800 + $2,000 + $1,000 = $10,800`; B: current `$3,360`, candidate `$2,160 + $600 + $280 = $3,040`; C: current `$2,880`, candidate `$1,320 + $900 + $240 = $2,460`. The modeled differences are `$1,200`, `$320` and `$420`. These are **incomplete** directional comparisons. Do not sum them into a purchase recommendation: the $500/month shared identity service has no allocation or retirement decision; candidate rows omit multiple costs, and D has unknown costs. An explicit allocation would still need to reconcile with the whole portfolio and any retained identity use. Promotional credits affect cash timing, not resource TCO.

## Changed-fact reasoning

- A 90-second webhook retry and a 5-minute interruption allowance are different limits. Test webhook idempotency, replay and external payment reconciliation; do not promise rollback by switching a URL after new target payments.
- The identity-service deadline creates a program dependency. Decide and test its replacement or compatibility path before assigning A's date. July is not quiet for the online channel.
- B's undocumented table invalidates the earlier “documented contract” assumption. Discover and reconcile that table before moving B separately or alongside A.
- C's 15-minute retrieval promise may invalidate a low-cost archival assumption. Re-price eligible storage/retrieval, validate access through the real user path and consider keeping a faster copy if retention permits. Do not invent an AWS tier or current rate from this packet.

## Provisional scoring guide

Score each dimension 0–2: **inventory confidence** (owners and observed/unknown facts), **strategy** (per-workload 7R plus tradeoff), **wave safety** (dependencies, capacity, rehearsal, acceptance), **TCO** (period, arithmetic, omitted/shared costs), and **changed-case revision** (invalidated assumptions and a new evidence gate). Ten points are possible. A mathematically correct answer that gives A a date despite the unknown identity path cannot earn full wave-safety credit. No score in this document represents an actual learner result.
