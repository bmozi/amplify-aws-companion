# Assessor: when a green delivery chart deserves a hold

Use this after attempting the six [changed cases](README.md#one-chart-four-receipts). The answer is about evidence for a human decision, not a recommendation to change staffing.

1. Hold. Two of three eligible orders are confirmed on time, so the order-level fraction is **2/3**. **1/2** describes a different numerator or denominator and must not inherit the same label.
2. Hold. A source change at 08:30 is later than the 08:20 import. Even if the chart's current number happens to match a later calculation, this imported copy has not established that it contains the newer fact.
3. Hold. Equal dollar totals do not identify the orders. Compare the exact `(shop, order ID)` set with a separately prepared expectation; the missing and duplicated identities are material even when their amounts cancel.
4. Hold. The Shop B identity violates the supplied Shop A scope. The local allowlist is a negative control for this fixture, not a real user permission test.
5. Show **no defined rate** and the count of zero qualifying orders. Dividing by zero cannot justify either 0% or 100%.
6. No. Test the actual reader role and rule data, then separately test source, sharing and export paths. A dashboard filter and a local list are not effective-access evidence.

For the original two cases, the local program returns `hold_for_investigation` for the 09:00 chart and `ready_for_human_review` after the missing outcome and fictional import are updated. Both retain `staffing_action_taken: false` and `aws_called: false`. A passing local result means only that the *supplied* fixture claims are internally consistent. In a real operation, preserve the query, source-to-import lineage, actual reader identity, business definition and manager's recorded decision before treating a dashboard as operational evidence.
