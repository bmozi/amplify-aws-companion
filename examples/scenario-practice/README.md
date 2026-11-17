# Original scenario practice: explain the constraint

These authored, fictional questions support [the scenario-reasoning lesson](../../reader/BOOK-LOCATORS.md#book-f4cbabaed002683d). They are not AWS questions, recalled exam content or a calibrated mock exam. No AWS deployment, notification or spending is involved.

Before reading [the assessor notes](ASSESSOR.md), record your selected answer(s), the requirement that decides, your confidence and any assistance. Then answer the changed case. No score from this three-question set predicts certification success.

## Case 1 — Select one: the next incident observation

Two application versions call the same supplier. Both show elevated elapsed time. A release occurred just before the symptom. No comparison of request mix or dependency timings has been collected. The question asks for the next read-only observation most directly useful for distinguishing a new-version regression from a shared supplier slowdown.

A. Remove supplier timeouts from both versions.
B. Compare equivalent request traces from both versions, including time at the supplier boundary.
C. Declare the release causal because it happened first.
D. Increase both versions' concurrency tenfold.

**Change:** Only the new version remains slow for equivalent requests, and its supplier timings are normal. What hypothesis becomes stronger, and what is still missing before claiming a root cause?

## Case 2 — Select two: accept a tenant repair

A reviewed repair should reconstruct shop A's orders from a stipulated complete, trusted ledger while preserving shop B's current orders. The fixture contains only one table with tenant, order ID and amount; there are no triggers, external effects or dependent tables. Which TWO observations directly verify the required resulting row state?

A. The repair command exits successfully.
B. A's exact tenant/ID/amount tuples equal the reviewed ledger, with no missing or extra rows.
C. B's exact tenant/ID/amount tuples equal its pre-repair snapshot.
D. The total row count matches the combined count before the incident.
E. The database process responds to a health request.

**Change:** A separate provider may already have sent a technician. Explain why the selected pair no longer establishes the entire recovery outcome, even if both observations still pass.

## Case 3 — Select one: obey the environment constraint

A learner uses a personal trial account. The exercise explicitly prohibits creating an Organization or enabling an organization-dependent environment. The goal is to compare account-grouping and policy-boundary designs, not to prove live enforcement. Which activity meets this exercise's scope?

A. Create the Organization, then remove it after drawing the diagram.
B. Use a broadly privileged script because automation makes the change temporary.
C. Produce a fictional account tree, trace stated policy assumptions and label enforcement as untested.
D. Claim that a passing local policy exercise verifies the account's live access.

**Change:** An authorized organizational sandbox becomes available later. List the identity, targets, policy behavior, recovery and cost evidence needed for a separate live test. The change card does not supply authorization to use any real account.

After reviewing the rationale, record one specific misconception to address and a different scenario you can explain without assistance. Keep implementation evidence separate from answer selection.
