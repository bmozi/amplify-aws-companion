# Assessor guide — read after the first submission

These are internal teaching rubrics, not validated psychometric instruments. No learner has been scored yet. Use the independent trial protocol in `curriculum/REVIEW-PROTOCOL.md`; distinguish author/model review from independent human evidence.

## Operations expected evidence

At second 120: six accepted, three completed, three unfinished. Five jobs have had their full 60-second allowance; two completed on time, while three are late or missing. The sixth is unfinished but not yet due. At second 200: all six are complete, but only two met the original deadline. Eventual completion does not repair historical latency compliance.

Dependency 503 responses and the separate direct probe support a dependency-availability explanation more strongly than a backend-release regression. The pack says the backend revision did not change and the frontend change was a label. These facts weaken the proposed rollback explanation but do not establish the dependency's root cause. No evidence establishes that the operator's action caused recovery.

Increasing concurrency can amplify load on a failing dependency. A good response preserves durable work, keeps retries/concurrency bounded, investigates the dependency and checks the customer outcome. It need not name one mandatory mitigation; reward a justified bounded choice with stop conditions. Rollback should follow evidence of a relevant regression, not mere temporal proximity.

The follow-up has six unique assignment receipts. The duplicate delivery for r3 references its existing receipt; within this fixture there is no second recorded business effect. This does not prove an external service can never duplicate an effect.

For the timeout variation, the candidate should distinguish lost response from failed effect, reuse a stable operation identity and reconcile with authoritative dependency receipts. Blindly retrying with a new identity is insufficient.

Score each of these six dimensions from 0 to 2: arithmetic/cohort reasoning, evidence versus hypothesis, safe mitigation, recovery/duplicate reasoning, customer communication, changed-failure response. Zero means absent or contradicted, one means partly correct with a material omission, two means correct with stated limits. A provisional internal target is at least 10/12 with no zero in safe mitigation or changed-failure response. This threshold is an editorial teaching choice, not a validated measure of job or exam readiness. Record the evidence behind every score.

## Architecture expected evidence

The stated volume is 44,000 requests per month. If every request has one 5 MB photo using decimal units, new photo bytes are 220,000 MB, or 220 GB, per month before versions, copies or outputs. The brief does not establish steady-state storage because retention is unspecified. Do not penalize a consistently explained binary interpretation; do require clear units.

Accept multiple designs when they satisfy the stated requirements and explain tradeoffs. A strong pooled proposal includes trusted tenant context across queries, caches, files, exports and workers, not merely a tenant field. A strong dedicated-resource proposal addresses provisioning, updates, drift, recovery and fixed per-tenant overhead. Neither topology automatically establishes legal compliance.

The request receipt must follow durable acceptance. Completion, idempotency and dependency failure handling must be explicit. The file path must distinguish uploaded from approved. The change card requires more than reusing the immediate last-seat lab: expiring holds and external payment effects need additional state and reconciliation rules.

Score eight dimensions from 0 to 2: requirements/units, alternatives/tradeoffs, identity/tenant boundaries, durable workflow/correctness, recovery/operations, cost/cleanup, delivery/ownership, change-card adaptation. Use the same 0/1/2 meaning above. A provisional internal target is at least 13/16 with no zero in tenant boundaries, workflow correctness or change-card adaptation. Record deficiencies and request a targeted revision; a passing paper design still needs implementation evidence.

## Review record

Capture participant pseudonym, experience, consent, source revision, first-attempt time, assistance, scores with cited response passages, material mistakes, revision and transfer outcome. Do not collect credentials or unnecessary personal data. Retain an uncoached first answer separately from a corrected answer. Report disagreements between assessors rather than averaging them into false certainty.
