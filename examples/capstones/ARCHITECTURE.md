# Architecture review: one foundation, two businesses

This original design exercise is cloud-free. It does not establish deployment readiness, regulatory compliance or certification readiness. Read the business brief, write your decision, then consult the assessor guide.

Prepare with [the worked architecture decision lesson](../../reader/BOOK-LOCATORS.md#book-aadca742bfb00b8e), then write your own decision before consulting the assessor guide.

## Fixed fictional requirements

A provider serves 20 repair shops with 10 staff members each. Each shop receives 100 requests per business day. A request has metadata and may include one photo up to 5 MB. Shops must not read one another's information. A customer receives an acceptance receipt immediately after durable receipt; technician assignment may take up to five minutes. A duplicated submission must not create a second assignment. Two operators maintain the platform. The provider's illustrative operating budget is USD 300 per month, not a statement of AWS pricing or approval to spend in any account.

Assume 22 business days per month. Calculate the implied request count and worst-case new photo volume, explicitly choosing decimal MB or binary MiB. Do not assume that storage volume is the whole bill or that every request includes a photo. Define retention before calculating steady-state stored volume.

## Required submission

Draw the user/data path and the deployment/administration path separately. Mark tenant boundaries, durable acceptance, asynchronous completion, file review, retries and failure handling. Label every managed resource's infrastructure owner.

Compare two feasible designs: a shared application with tenant-scoped data and a design that dedicates selected resources to each shop. You may choose a mixed approach. Explain the consequences for isolation, noisy neighbors, recovery, deployment, cost and the two-person operating team. Do not award your preferred option every advantage; identify one condition that would make the alternative better.

Create an acceptance matrix covering allowed access, forbidden cross-tenant access, duplicate submission, an unavailable scheduling dependency, a stuck file review and recovery of a confirmed request. State which companion local examples support reasoning and which cloud checks are still needed.

Produce a cost model with quantities, dated regional prices or explicitly missing prices, omitted items and a workload bound. The fictional USD 300 business scenario is not a lab spending authorization; a live experiment needs its own account-specific limit and credit reserve. No resources should be deployed for this assessment.

Write a release and rollback approach that accounts for schema changes. Include one observable customer outcome, a missing-telemetry decision, a cleanup boundary and an operator handoff. Finish with unresolved requirements rather than silently inventing them.

## Review-board change card

A new customer is a training provider selling 30 seats per class. Multiple people may buy the last seat at once. Payment confirmation can arrive late or repeat. Explain which foundations remain useful and which correctness rules must change. Include capacity enforcement, expiring holds, payment reconciliation and refund/cancellation ownership as requirements; the existing immediate-reservation lab does not implement all of them.

Then the provider requests tenant-specific restoration without rolling back the other tenants. Revisit the storage isolation choice. Compare the operational cost of your revised design with the cost of more complex selective recovery.

Ask Codex to play a reviewer who asks one question at a time. Require it to identify unsupported assumptions and the evidence that would resolve them. Preserve your initial decision, the questions and your revisions. A persuasive defense is not a substitute for implementing and verifying the selected design.
