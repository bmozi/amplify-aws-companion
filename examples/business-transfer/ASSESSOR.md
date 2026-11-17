# Assessor guidance: business transfer

Original reasoning and provisional rubric for the fictional rental brief. Multiple designs can be defensible. Score the requirement-to-evidence reasoning, not the number of AWS service names. This guide is not a validated exam.

## Core reasoning

For a proposed interval `[s1, e1)` and existing interval `[s2, e2)`, overlap exists when `s1 < e2` and `s2 < e1`. Require positive interval duration and a defined timestamp representation. The 09:00–11:00 rental occupies the planned asset interval through 12:00. Another interval starting at 12:00 does not overlap; one starting at 11:59 does. This scheduling calculation does not authorize physical handover without actual return and inspection evidence.

A capacity counter of 24 is insufficient: it ignores asset identity, branch and time. A unique asset identifier identifies the machine but cannot by itself prohibit overlapping reservations. A design must make the conflict check and confirmation indivisible relative to competing admissions. Serialized per-asset admission can provide an understandable authority boundary, but must address duplicate delivery, failed workers and avoiding two active authorities. A database transaction needs an actual documented exclusion/locking strategy; a plain read followed by an insert can race. Do not award correctness merely because a candidate mentions “transaction.” Selected AWS implementation behavior still requires service research and tests.

The initial future booking decision and the later handover decision use different evidence. A cleaner that has not returned or has failed inspection cannot become available solely because wall-clock time advanced. A later reservation remains a promise requiring explicit exception handling. Restoring a pre-damage database copy cannot repair the machine or revoke a handover that already happened. Reconcile confirmed reservations, actual custody, inspections and any completed external actions before resuming.

Customer-scoped retry identity and current authorization remain shared foundations. Branch membership, asset operation scope and customer visibility must be enforced on each relevant operation. A role name in a diagram is not an authorization test. The changed flow must not grant unrelated branches access to customer records merely because an asset moves.

The retention arithmetic is `180 attempts/day × 180 days = 32,400 attempt records` under the stated full-retention assumption. It is not a count of successful reservations. No byte volume is calculable until record sizes and additional data are defined. A cost estimate must include its missing facts; a practice-run limit is not the hypothetical business's monthly budget.

## Changed-context reasoning

Cross-branch return invalidates the fixed-location assumption. Transport time is necessary but not sufficient for availability: physical receipt and any recall/inspection constraints also matter. A 90-minute elapsed timer cannot establish arrival. Existing reservations may require an alternative machine, transport that actually meets the deadline, or a customer/operator exception. The brief does not guarantee a feasible replacement.

Offline events need authenticated provenance, stable event identity and defined ordering/version rules. Deduplicating repeated bytes does not determine whether an old state change is still applicable. An earlier passed inspection arriving after a later recall must not automatically overwrite the recall. State transitions must account for the business's actual ordering and authority; device wall clocks alone have not been established as authoritative. The brief does not authorize offline booking or handover, so a candidate cannot assume either as a convenience.

A thoughtful design records unresolved custody rather than inventing certainty. Explain how reconciliation resolves it, who may make that decision and what evidence is preserved. A stale source restore or a delayed event can be internally consistent while wrong about physical reality.

## Provisional scoring: five dimensions, four points each

| Dimension | Evidence for four points | Examples of reduced evidence |
| --- | --- | --- |
| Business rules and arithmetic | Correct interval boundary, positive duration, physical availability distinction and retained-attempt arithmetic | Treats turnaround as proof of actual return, or counts attempts as confirmed rentals |
| Authority and concurrency | Concrete enforcement strategy, customer/branch restrictions, retry behavior and concurrent conflict test | Lists IAM/database products without proving the target rule |
| Alternatives and transfer | Compares two bounded approaches; distinguishes reusable foundation from changed invariant and unknowns | Renames seats to cleaners or assumes a global stock count is enough |
| Failure, recovery and operations | Late return, inspection failure, lost reply, restore and customer exception paths with owners and expected evidence | Only happy-path diagram, or assumes restore reverses physical events |
| Change-card adaptation and evidence | Custody acknowledgement, stale-event/recall handling, preserved first draft, justified amendment and bounded cost/test plan | Only increases turnaround time or silently authorizes offline handover |

Use three points for mostly supported reasoning with one material omission; two for a plausible approach with major unverified steps; one for relevant vocabulary without a coherent mechanism; zero for absent or contradictory reasoning. Record the specific missing evidence, not just the number.

An internal practice target is at least 16/20 with no zero dimension. It is not an empirically calibrated passing standard. Regardless of total, a design that knowingly permits overlapping confirmations, unauthorized cross-customer reads, or handover without required physical evidence needs revision. Do not let strength in prose average away a violated mandatory rule.

For a real learner review, retain the unaided first submission, AI-assisted revision, change-card amendment, assessor notes and unresolved questions. Record what the learner could explain and demonstrate independently. This repository currently supplies the task and authored criteria, not those learner results or an implemented rental platform.


## Separate executable follow-up evidence

The optional local lab, linked after the design task, checks interval boundaries, stable-key replay/conflict, competing SQLite admissions, branch-fixture denial, recorded return/inspection gates and a calendar-only negative control. It supplies one bounded implementation to examine after the learner attempt. It does not implement the change card, authenticated staff/customer access, a complete exception workflow, real physical events or restoration. Its serialized database writer is an explicit operating tradeoff. Do not grade a copied implementation as independent transfer or infer a real machine's condition from its fixture row.
