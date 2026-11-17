# Artifact retention: which spare parts still matter?

Original fictional design assessment for the [container lifecycle lesson](../../reader/BOOK-LOCATORS.md#book-09e7b02918edc26d). No AWS calls, deletion or spending occurs. Record a decision, missing evidence, accountable owner and review condition for each case before reading the assessor notes.

## 1. The quiet recovery image

Image B serves customers. A proposed age rule selects A, which was pushed six weeks ago. A is the only image with a recorded successful recovery test against the current schema. Neither its current vulnerability status nor its present retrieval permissions has been checked. Can the team delete A now? Can it call A a proven safe recovery target today? Separate those two questions.

## 2. The reassuring running process

The preview selects the image used by a long-running worker. The worker still responds correctly. Its replacement starts by pulling from the registry. Explain why current health is insufficient deletion evidence. Specify how to check the replacement path without deleting the only required copy as an experiment.

## 3. The old image with a new problem

A current advisory affects retained image A. Someone proposes either deleting every old image immediately or approving A forever because it once passed a recovery test. Offer a third plan that separates investigation evidence, execution permission, a repaired compatible recovery target and the retirement decision. The scenario supplies no exploit reachability result, patch test or complete affected population.

## 4. The cleanup preview is accurate

A preview correctly marks every image selected by the proposed rules, including two digests referenced by approved recovery records. The engineer calls the policy successful because the selected count matches their prediction. Explain which test passed and which business requirement failed. Identify what must be rechecked after a policy or tagging change; do not assume a particular label overrides every rule.

## 5. The archive alternative

The team proposes moving the recovery image to a cheaper storage mode. Its recovery objective requires a usable service within ten minutes. Retrieval time, minimum retention, permissions and current pricing are unknown. Write the evidence required before accepting this alternative. A cost-saving claim and a recovery-time claim need different evidence.

## Transfer

Replace container images with a ZIP website and its build receipt. Which retention questions stay the same, and which ECR policy mechanics can no longer be assumed? Include backend compatibility and the deployed website's identity in your answer. Keep source retention separate from retention of the exact tested build.

Save your first answers, then ask Codex for an uninspected dependency and revise explicitly. Compare with [assessor reasoning](ASSESSOR.md). This exercise does not implement an ECR policy.
