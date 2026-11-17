# Transfer challenge: a reservation is not always a seat

An original, fictional design assessment for chapter 34. No AWS deployment is required or authorized by this exercise. Complete your first submission before opening [the change card](CHANGE-CARD.md) or [assessor guidance](ASSESSOR.md). The scoring criteria are provisional.

## The business brief

A rental company operates two branches. It has 24 individually numbered carpet cleaners: 12 initially held at each branch. Customers reserve a particular cleaner for a pickup time and a return deadline. Each confirmed reservation identifies one physical asset and one pickup branch. The first release does not support transferring assets between branches.

For this exercise, all times use UTC with minute precision. A rental's planned exclusive-use interval begins at pickup and extends through 60 minutes after its promised return, allowing inspection and cleaning. Represent it as a half-open interval: the start is included and the end is excluded. Two reservations may touch at their boundaries but may not overlap for the same asset. Assume the reservation transaction has authoritative access to all confirmed intervals for that asset; explain how your selected implementation would establish that assumption.

A scheduled interval ending does not prove that the cleaner is physically available. Staff must record its actual return and a passed inspection before the next handover. A failed inspection makes the asset unavailable until an authorized repair/reinspection decision. An already-confirmed later customer must receive an exception workflow, not silently disappear from the schedule. The brief does not promise that every confirmed reservation can be fulfilled under every late return or equipment fault.

Customers may view only their own reservations. Branch staff may operate only on assets and reservations at their authorized branch. A central operations role may coordinate exceptions across both branches. The same customer's repeated request with the same operation key and intent must resolve to the original reservation; changed intent must be rejected or follow an explicit update process. The system must prevent simultaneous overlapping confirmations for one asset.

The company expects 180 reservation attempts per day and retains reservation history for 180 days for this fictional exercise. This is a business-supplied training assumption, not a legal retention rule. Payments, deposits, tax and damage billing are outside this release. There is no supplied monthly AWS budget or measured peak workload. Record those as missing inputs; do not invent prices or assume daily average is peak demand.

## Required first submission

1. Write the invariant in ordinary language, then write the interval-overlap rule. Work through a 09:00 pickup, 11:00 return and 60-minute turnaround. Decide whether a second 12:00 pickup conflicts. Repeat with 11:59. State the date and time basis so the answer does not silently depend on local daylight-saving changes.
2. Draw separate paths for booking and physical handover. Mark authority, durable state, concurrent conflict checks, retries and the point where an unavailable asset becomes an operator/customer exception. A booking receipt and permission to hand over a machine must not be the same unchecked flag.
3. Compare at least two bounded implementations: serialized admission for each asset versus a transaction that enforces conflicting-interval exclusion. Explain consistency, contention, failure recovery and operational complexity. A unique asset ID alone does not enforce a time-range rule. Select one and name evidence needed to prove it.
4. List what can be reused from this book and what must change. Classify each as unchanged foundation, configuration within a validated range, new business rule, or unresolved requirement. Include identity, retries, stock, temporal conflicts, physical inspection, recovery and cost.
5. Supply an acceptance matrix with at least these cases: simultaneous overlapping requests; boundary-touching intervals; a retry after a lost reply; a late return; failed inspection; unauthorized staff at the other branch; and restored scheduling data whose real-world asset condition has since changed. Include expected state, allowed/denied action and evidence to collect.
6. Write a cost/discovery and operating handoff. Calculate an upper bound on retained attempt records if all 180 daily attempts were stored for the full 180 days. Explain why that is neither confirmed reservations nor a storage-byte estimate. Identify missing peak, payload, audit, backup, notification and service-price inputs. Describe rollback, retained-data handling and cleanup for a later bounded lab.

Use the [business-context worksheet](../architecture/business-context.md) as a record structure, not as the completed answer. Save the first design before opening the change card. A design may remain provisional where the brief lacks facts, but it must not quietly violate a stated rule.

## Use AI without surrendering the transfer test

First write your invariants, examples and preferred design unaided. Then give Codex the fictional brief and your draft, and ask it to find a counterexample to each claimed safety rule. Require it to separate a code-level race, a missing business decision and an unverified service claim. Keep both versions and explain which suggestions you accepted and why.

Do not provide customer data or credentials. Keep cloud tools and provisioning disabled for this assessment. Any later AWS experiment needs current service research, a scoped identity, a whole-run estimate within the account owner's chosen limit, an owner-chosen credit reserve, and a cleanup plan. A persuasive diagram or AI-generated policy is not deployment evidence.


## After your design attempt inspect one local implementation

Save your unaided submission and change-card amendment first. Then run:

```sh
python3 examples/business-transfer/lab.py
```

This follow-up uses standard-library Python and a temporary SQLite database. No installation or AWS account is needed. It implements a small part of the original brief, not the cross-branch/offline change card or a complete rental application.

Predict these results before looking at the assertions:

| Step | Expected observation | Reason |
| --- | --- | --- |
| Repeat the original key and input | Same booking ID | Retry identity survives a repeated attempt |
| Reuse that key with changed return time | Rejected without changing records | The key cannot silently acquire a different meaning |
| Request pickup at 11:59 after a 09:00–11:00 rental | Conflict | The first interval includes turnaround through 12:00 |
| Request pickup at 12:00 | Confirmation permitted | Half-open intervals touch without overlapping |
| Release two overlapping requests concurrently | One confirmation | Conflict check and insert share a SQLite write transaction |
| Other branch's staff attempts handover | Denial with unchanged records | Trusted fixture branch scope is enforced |
| Noon arrives while the cleaner remains out | Handover blocked; later booking retained | The schedule cannot establish physical availability |
| Return recorded without inspection, or inspection fails | Handover blocked | Return and readiness are separate states |
| Return and successful inspection recorded for another cleaner | Next eligible handover succeeds | The safety check has a positive control |

The last negative control evaluates an unsafe calendar-only rule. It would authorize the blocked cleaner because the booked time has arrived. The guarded operation refuses. No second physical handover is performed by either path; all conditions are fictional records.

Open `reserve` in `lab.py`. `BEGIN IMMEDIATE` serializes database writers before checking interval overlap and inserting the booking. This deliberately locks more broadly than one asset, trading concurrency for a small inspectable example. The separate connections and barrier release exercise actual local contention, but do not enumerate every possible schedule or prove an AWS database implementation. Scaling this policy requires a supported atomic admission design, not removing the transaction because it looks slow.

Open `handover` next. In one transaction it checks the trusted staff fixture's branch, booking state and time, and recorded asset condition before changing both records. A blocked handover leaves the later booking intact. The program reports `exception_required`; it does not implement customer notification, replacement selection or an operator case queue. Those remain required design work.

A conditional state transition rejects the illustrated stale inspection update after a failure, but this is not a general offline-event ordering protocol. Repeated state names, version history, recalls, authenticated devices and cross-branch custody need more than that check. There is no real authentication, customer status API, multi-day/time-zone calendar, cancellation, deposit, restore process or physical inspection. Staff/owner labels and UTC-minute values are trusted fixtures. The temporary file is removed after the run.

Ask Codex to trace one invariant from your first design to this code and one requirement this implementation omits. Explain why a passing local test supports only the tested mechanism. Preserve your original design rather than replacing its unknowns with the example's convenient assumptions.
