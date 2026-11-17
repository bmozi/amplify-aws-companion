# Recovery gate assessor notes

Use these notes after you have explained each case in your own words. The cases are synthetic. A sound answer names evidence, its source and freshness; it does not treat the model's Boolean values as real verification.

1. **Missing reconciliation receipt:** do not cut over. A successful restore or HTTP 200 cannot establish that every confirmed booking and its value survived. Obtain a trustworthy reconciliation result or document an explicit degraded/read-only business decision.
2. **Unfenced old writer:** do not cut over writes. Changing a DNS record does not prove that all old clients or workers stopped writing. Establish and test an application-appropriate fencing mechanism and resolve writes already in flight.
3. **Recovery operator signs in through the failed Region:** recovery access is not ready. Prove an independent, authorized operator path under the intended outage, including its identity, key and network dependencies.
4. **Stale observer:** the last green state is historical evidence, not current health. Stop or wait for an independent fresh signal. Define the observation-age limit and missing-data response before the exercise.
5. **Approval required:** wait for the named approval bound to this candidate, action and evidence. Approval is not a substitute for any failed technical gate.
6. **Only half of demand can be served:** block the normal full-service cutover unless the business has approved a tested degraded mode that deliberately sheds or queues specified work while protecting correctness. Include the degraded service's acceptance test and recovery time.

The model's automatic path is intentionally narrow. It says only that every supplied Boolean passed and the supplied policy permits automation. It cannot prove the booleans came from trustworthy, independent, current checks. In real recovery automation, validate those checks, the runbook role's exact permissions, each action's side effects, retry/idempotency behavior, operator escape path, notification, audit trail, and the procedure for stopping safely.
