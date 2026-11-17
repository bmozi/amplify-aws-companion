# Assessor notes: one green balance, eight different decisions

Open after the learner writes a first response. These notes are authored reasoning, not an AWS bill, calibrated exam key or live credit decision.

**A — candidate for separate live review.** The fictional checks are all marked reviewed, so the local classifier has no stated blocker and calculates USD 3 above the reserve. A real operator still needs current account identity and plan state, actual per-credit applicability and expiration, selected-service/Region rates, accurate workload quantities, effective role permissions, resource inventory and later cleanup/billing receipts. The toy booleans are supplied assumptions, not evidence that those real checks happened.

**B — hold.** The plan balance does not list the applicable products of each individual credit. Inspect enabled status, amount, expiration, named products and terms for the selected meters. Do not add the individual amounts to the aggregate plan balance as if they are separate money.

**C — hold.** The Free plan limits access to some services and offerings. A credit balance is not a service-access grant. Verify the exact proposed feature and Region under the current plan before budgeting it.

**D — hold.** The run must end before the Free-plan expiration, and any relevant credit must last through it as well. A plan expiration or credit expiration at the planned end is not a comfortable margin; this toy gate refuses equality. A planned end still does not remove cloud resources automatically.

**E — hold.** The same account-wide snapshot is not an atomic reservation. Inventory active experiments and retained resources, then reprice the combined exposure. The workflow's concurrency key controls that workflow's overlapping invocations only; it cannot see local or unrelated AWS work.

**F — hold.** The project requires a scoped non-root execution identity. Correct arithmetic cannot narrow a root session. Keep owner inspection separate from deployment authority.

**G — hold.** The deterministic calculation is `77 − 3 − 75 = −1` USD of headroom. No favorable interpretation of credit applicability repairs the violated reserve. A dated account balance could also change before a later run.

**H — hold.** Stopping the application or disabling the GitHub publisher does not prove that Hosting files, backend resources, logs, snapshots or other retained resources were removed. Name an owner, deadline, target inventory, verification method and later billing reconciliation.

A strong answer can explain **which boundary is unknown**, not merely repeat “check costs.” Maya's chosen spending limit and reserve are fixture inputs, not AWS policy or enforced billing caps. The [official account-plan guide](https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/free-tier-plans.html) and [GetCredits API](https://docs.aws.amazon.com/aws-cost-management/latest/APIReference/API_billing_GetCredits.html) support the mechanism questions. Do not turn this small synthetic packet into certification-readiness evidence.
