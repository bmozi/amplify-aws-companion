# Replacement-boundary design cases

Read [unit 03](../../reader/BOOK-LOCATORS.md#book-02b8b1e13a935d6d), “Repair the running worker or replace it from the recipe?” These are invented design cases, not deployment observations. No cloud account or installation is needed.

For each case, name the unit being changed, the source of truth, the customer risk, competing remedies and evidence needed before claiming recovery. Keep your first attempt and AI assistance in the [learning record](../../curriculum/LEARNING-RECORD.md). Read [assessor notes](ASSESSOR.md) afterward.

## 1. The repair that disappears

An operator edits a running worker's parser to accept a valid customer name. A replacement from the original image rejects that name again. Another worker was never edited. Explain the disagreement. Propose a reconciliation path that preserves service while testing and distributing the actual correction. What evidence would distinguish a useful repair from a change that merely conceals another defect?

## 2. Same image, different result

Two workers have the same recorded image digest. They read different configuration revisions and connect with different permissions. One applies the promised discount; the other denies database access. A reviewer says, “The image is immutable, so behavior cannot differ.” Refute the claim precisely. List the additional release inputs and observations needed without copying secret values into the record.

## 3. A new worker built from an old promise

Every replacement downloads the newest available parser during startup. Yesterday's and today's workers began from the same base image, but their installed dependency versions differ. Decide whether the replacement procedure establishes reproducibility. Compare a controlled artifact build with dynamic startup installation, including the need to patch later. Do not claim that pinning a vulnerable version makes it safe.

## 4. The upload left on the old worker

The diagram calls workers disposable, but a customer's completed upload exists only on Worker A's local filesystem. The release plan will delete A after B passes a health check. Identify the missing data requirement, a candidate migration/storage approach and the evidence needed before retirement. Explain why a successful HTTP response from B is insufficient.

## 5. Correct code, incompatible recovery

Version B writes invoice amounts using a new representation. The old version A is retained and starts successfully, but interprets those records differently. The team proposes returning traffic to A because the deployment is immutable. Explain the recovery failure and compare retaining a compatible recovery version, staged data changes and an explicitly designed forward repair. Which completed effects still require reconciliation?

## Transfer: emergency maintenance under a hard deadline

The business requires an urgent repair and cannot currently provide overlap capacity. Compare a bounded in-place repair with delaying for a tested replacement. State what business decision and evidence would justify either choice, how the durable recipe is reconciled, and how to prevent the exception becoming an undocumented permanent deployment path. There is no unconditional winner supplied by this scenario.

Ask Codex for an assumption that would reverse your decision. Verify its objection before revising. This assesses reasoning only; real implementation and customer outcomes require separate evidence. Any later live lab needs current account eligibility, a chosen whole-run spending limit and reserve, scoped access and cleanup.
