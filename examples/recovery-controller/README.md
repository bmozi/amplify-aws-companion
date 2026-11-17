# Decide when recovery is safe

Read [Unit 24's recovery-tool lesson](../../reader/BOOK-LOCATORS.md#book-5885d1c9d7f5b123), then answer before opening the [assessor notes](ASSESSOR.md). This is an invented architecture exercise. It needs no AWS account and creates no resource.

Maya promises that a confirmed booking will not be silently lost. The primary Region stops accepting new bookings. The standby endpoint returns HTTP 200, but its data is ninety seconds behind, its applied worker quota supports only half of peak demand, and booking B-8417 returned a timeout just before the failure. The team has no evidence whether B-8417 committed. Some customers retain cached DNS answers. The only available operator has permission to view dashboards but has not yet been granted recovery execution permissions.

Draw five boxes: **assessment**, **controlled experiment**, **decision**, **execution**, and **customer verification**. Put the first two in a planned, normal-operation preparation phase and the remaining three in the active-incident phase. Do not propose beginning fault injection during Maya's outage. For each box, write its owner, input, output and one thing it cannot prove. Place Resilience Hub, FIS, ARC routing control and Systems Manager Automation where each might help. You may leave a box without an AWS product. Explain why a healthy endpoint, an estimated RTO or a completed runbook cannot alone satisfy the booking promise.

Run the existing [local recovery gate](../recovery-automation/README.md) after drawing your boxes. It accepts declared evidence flags; it does not measure AWS state. From the repository root, this short experiment changes one fact at a time without editing the lab:

```bash
PYTHONPATH=examples/recovery-automation python3 - <<'PY'
from dataclasses import replace
from gate import decide, example_cases

base = replace(dict(example_cases())['unreconciled business records'], policy_allows_automatic_cutover=False)
for label, evidence in (
    ('missing booking receipt', base),
    ('approval alone', replace(base, human_approval_received=True)),
    ('receipt present, capacity missing', replace(base, business_records_reconciled=True, survivor_capacity_proved=False)),
):
    result, reasons = decide(evidence)
    print(label, result, reasons)
    assert result == 'NO_GO'
PY
```

Explain why approval alone cannot change the result and what measured capacity or explicit degraded-service policy would justify a new evaluation. A `True` flag is an assertion supplied to the local model, not an AWS observation. Keep the three results and the evidence you would seek in your learning record.

Write an ordered recovery decision record. Include the authoritative writer, B-8417 reconciliation, allowed data-loss decision, standby quota and degraded-capacity policy, operator identity, traffic change, stale-DNS observation, post-change correct reads and new booking completion. State which missing evidence **holds** the traffic change. Include a human approval before any irreversible or customer-affecting step; the approver needs the decision evidence, not just a button.

## Change the conditions

1. A teammate proposes enrolling a new account as an **ARC readiness-check customer**. Check the [current AWS availability note](https://docs.aws.amazon.com/r53recovery/latest/dg/recovery-readiness.html). Rewrite the plan without that feature. Say how you would independently verify capacity, quota, routing and customer behavior. Do not turn an unavailable feature into an account-setup task.
2. The FIS stop alarm fires and the experiment ends, but B-8417 remains uncertain and the backlog grows. Identify what the stop proves and which recovery steps still remain. Would you widen traffic now?
3. A runbook requests approval to flip a routing control, but the operator can only view dashboards and the old writer may still be active. Decide whether to approve. Identify the scoped execution permission and fencing evidence that must exist first. Explain why granting a broad administrator role solely to finish the drill would fail the design review.

Ask Codex to challenge one proposed decision using the cited AWS service documentation and the fictional case facts. Have it list unsupported claims separately from missing evidence. Retain your first answer and assisted revision. An AI response or this packet is not proof of a live recovery or independent learner mastery.
