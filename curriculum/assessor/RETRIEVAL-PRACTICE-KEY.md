# Cumulative retrieval reasoning guide

Read after preserving the [participant attempt](../RETRIEVAL-PRACTICE.md). These are authored feedback criteria, not independent learner observations or calibrated scores. Accept other designs when they satisfy the stated contract and explain their evidence.

## R1 — Acceptance, retry and capacity

The matched record supports accepted work, not an assigned appointment. Preserve the operation identity and reconcile status before creating a new operation. More workers are justified only if worker capacity limits the path; downstream throttling can make them harmful. If the record no longer matches the customer, acceptance for this request becomes unknown. Remediation: Chapters 1, 5 and 19. Ask the learner to name the missing correlation fields rather than merely say “check logs.”

## R2 — Destinations and authority

Hold private-note testing against the unintended production destination. Identify the actual Auth, Data and other relevant targets; correct the outputs/build and inspect the served artifact before testing again. An empty list does not prove a denied direct read. Declared sharing of a disposable test backend may be acceptable with explicit participants, data scope, effects and cleanup ownership; a preview URL alone proves no isolation. Remediation: Chapters 6, 8 and 10. A response that changes only the displayed environment label misses the defect.

## R3 — Freshness and atomic admission

Confirmation needs a read/result path consistent with the promised committed booking. The reporting replica can be appropriate within its allowed lag, with lag and fallback observed. A cache adds a freshness contract; speed alone does not repair stale confirmation. The authoritative write must enforce the last-slot rule atomically under contention. Two fresh reads can both precede conflicting writes. Remediation: Chapters 5, 12 and 13. Ask which transaction or conditional decision rejects the loser.

## R4 — Mitigation and recoverability

Use evidence of the changed path to judge rollback, including artifacts, configuration, callers and data compatibility. Restore addresses a different state-loss/corruption problem and needs usable data, keys, roles, capacity and reconciliation. Neither action follows from a green endpoint. Define stop conditions and verify an authorized customer outcome and unfinished work afterward. Old clients can keep issuing incompatible writes even after a frontend rollback. Remediation: Chapters 14–18. Do not award causal certainty from timing alone.

## R5 — Authority and uncertain effects

Reconcile the existing provider operation under authorized lookup access; an expired approval cannot authorize a new payment. Do not treat an unchanged report as proof that the effect did not happen. Reuse the bound operation identity according to the provider's idempotency/lookup contract, distinguish pending from confirmed and avoid a fresh ID that duplicates the payment. Coordinate competing workers with a shared authoritative claim/transition and handle a crash around the external effect. Remediation: Chapters 19, 20, 23 and 24. A local transaction cannot make a provider exactly-once.

## R6 — Independent readiness boundaries

Network reachability, current document authorization and overlapping capacity/quota are separate checks. Hold cutover if a hard boundary lacks evidence or the transition exceeds quota. Rebuilding an index does not establish current caller permission, current source/version, correct filtering or safe answer release. Test allowed and denied paths with current trusted identity, and reconcile the migration before changing authority. Remediation: Chapters 27–31. Reward specific observations over a generic checklist.

## R7 — Hard constraints before preferences

B is the only candidate meeting the supplied 10-minute RTO; both meet the RPO. Seek representative recovery evidence, dependencies, authority, capacity and full cost before making a live promise. A preference score cannot compensate for violating a mandatory requirement. At a 60-minute RTO both supplied candidates become eligible; compare cost, operational work, failure assumptions and other requirements again. Do not infer that A is automatically preferred from monthly cost alone. Remediation: Chapters 2, 17 and 32.

## Feedback record

For each attempt, cite the learner's words or diagram for the mechanism, controlling requirement, rejected alternative and changed-condition response. Record assistance and prior exposure. Keep the first response, feedback and subsequent transfer separate. A facilitator may use these criteria to identify misconceptions, but must not invent results or label self/AI feedback as independent review.
