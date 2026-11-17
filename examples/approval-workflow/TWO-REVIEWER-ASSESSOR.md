# Two-reviewer policy — assessor guidance

This is an original design rationale under the fictional policy, not implementation evidence or a validated compliance control.

A suitable record design binds each review to action ID/revision, the reviewed action digest, authenticated reviewer identity, decision time and expiry. Enforce uniqueness for a person's approval on that revision. Keep requester identity on the action. Keep eligibility evidence and its policy/version context auditable. An execution record needs stable operation identity and a defined admitted state; the receipt later records observed execution outcome.

1. A repeated submission can recover A's recorded decision, but cannot become a second person's approval. A unique review identity and atomic handling must agree with the count query.
2. A's normal reviewer eligibility does not override this action's requester exclusion. The supplied pair therefore does not qualify. Check that exclusion at the enforcement boundary, not only by hiding a button.
3. Neither revision has two matching approvals. Do not combine A's authorization for one target with B's for another. A digest comparison only helps if it covers all consequential fields.
4. The reviews remain historical evidence, but the current eligibility condition fails. Require a valid replacement review or a revised action under the stated policy. Do not rewrite B's earlier approval as though it never happened.
5. Admission is rejected at the deadline. The rule is current time strictly before expiry. A real design must name the trusted clock and handle its supported precision; client-supplied time is not authoritative.
6. With an appropriate shared transaction, cancellation first prevents admission. Admission first means cancellation cannot claim that dispatch was prevented without checking the actual execution stage. The design may add a later cancellation protocol, but that is another mechanism. An external eligibility service introduces a separate freshness/race boundary that must remain explicit.
7. Approval is authority, not an execution receipt. Use the provider's supported operation identity/status path and preserve an unresolved state if the outcome cannot be established. Do not issue a fresh operation merely because the first reply is missing.
8. C must make a real decision on the concrete action under the policy. Relabeling B's history forges a review relationship. Preserve B's record and add C's actual review, then recompute current eligibility and matching scope at admission.

The positive case must include actual stored matching reviews from two distinct non-requesters and a single admission result. A proposal that checks the approvals outside the admission transaction, then blindly changes state, still needs a stale-state defense. In the external-authority alternative, a dated observation alone does not establish immediate revocation consistency. Accept a clearly bounded policy or mark that stronger requirement unresolved; do not reward an unsupported distributed-atomicity claim.

Review policy fidelity, record binding, identity provenance, duplicate handling, changing authority, timing, cancellation and external-effect uncertainty separately. A correct count is insufficient when the wrong people or revision supplied it. Require the learner to explain one advantage and one limitation of each storage alternative. A complete authenticated two-reviewer workflow requires separate implementation and testing. The separate local admission drill now demonstrates a bounded transactional subset; its README distinguishes tested cases from the external-authority and publication requirements.

## Waiting-mechanism rationale

1. Request Response progresses after the service response; an acceptance response need not mean completion. A supported `.sync` integration waits for the integrated job's completion. Verify the specific service and task behavior, then separately check the business result.
2. Express supports Request Response integrations, not the callback pattern. A supported Standard callback integration is a candidate for that waiting requirement. The business application must still authenticate and authorize the review before returning the task token through the appropriate AWS operation.
3. Stopping the workflow is not proof of stopping the integrated job. AWS describes cancellation of `.sync` work as best effort; permissions or service failures can prevent it. Inspect the downstream job and its resource lifecycle, then reconcile usage. Do not label an uncertain or ongoing operation cancelled merely because the parent workflow stopped.

Source for these three service distinctions: [AWS integration patterns](https://docs.aws.amazon.com/step-functions/latest/dg/connect-to-resource.html), checked October 18, 2026. No orchestration deployment, callback or downstream cancellation was tested by this exercise.
