# Backup and lifecycle assessor notes

Open after saving the first answer and changed-case revision. Internal criteria, not independent learner validation or live AWS evidence.

## Case 1

- Versioning can help recover an overwritten or ordinarily deleted version, but it does not by itself establish a separate security, account, Region, retention or restore boundary. Each property depends on configuration and access controls.
- Replication can support a separate-location design, but the student must consider whether the unwanted change or deletion also reaches that destination and identify the needed recovery point and failure assumptions.
- AWS Backup for S3 requires versioning. The answer should state the required retention and recovery-point behavior and check current service limits and configuration before implementation.
- Validation includes opening or hashing the recovered bytes against trusted evidence and reconciling the photo to the correct customer and booking. A successful restore job alone does not prove business correctness.
- Estimate retained versions, backup storage, request and restore work, transfer, retention duration, monitoring and any applicable retrieval or early-deletion costs using current regional prices. No dollar answer is supported by this fictional prompt.
- The missing RTO, RPO, retention and spend ceiling are decision inputs; the learner must ask for them rather than invent them.

## Case 2

- In a versioning-enabled bucket, expiration of the current version generally creates a delete marker; the prior version can remain as a noncurrent version and continue to consume storage. A separate noncurrent-version expiration policy is needed if the business has decided those versions should be permanently removed.
- Lifecycle is not an exact authorization deadline. Enforce a customer-visible access cutoff through the application's authorization path, separately from storage cleanup.
- Review the existing population because old objects may already qualify when a rule is added. Confirm filters, age basis, current/noncurrent scope, minimum retention, recovery needs, legal or business requirements, and the effect on backup recovery points.
- S3 Lifecycle behavior and billing details can change; check current AWS documentation and regional prices before implementation. Do not claim that a tabletop answer or local test proves cloud rule behavior.

## Case 3

- Do not treat versioning as a complete independent backup. It can help recover prior object versions, but permissions, malicious deletion, account/Region failure, business record correctness and restore procedure still matter.
- If AWS Backup for S3 is selected, check the current prerequisite and configuration: S3 Versioning must be enabled. Include every retained object version and lifecycle interaction in the cost estimate; a recovery point may include objects already scheduled to expire. Define a restore destination and test who can perform and validate it.
- Choose the archive tier from the eight-hour access promise, not the word “archive.” Glacier Flexible Retrieval typically offers standard restores in hours; Glacier Deep Archive may take longer than this case allows. These are service guidance expectations, not a guarantee for a particular incident. Check current behavior before a real design.
- Include storage, backup/recovery-point, request, retrieval, restore, transition and minimum-duration charges. Many small objects can add per-object overhead. Do not name a lowest-cost design without object counts, size distribution, expected restore size/frequency, current Region and prices.
- State the missing deletion-protection requirement and recovery authority explicitly. If administrators must not be able to shorten retention, investigate supported vault/object-lock controls and the impact on required recovery; do not claim immutability from the word “backup.”
- A restore job passing does not prove that each report belongs to the correct inspection. Reconcile identifiers and hashes or business fields against an independent source before reopening access. No actual seven-year retention, legal compliance, RPO, RTO or cost result follows from this fictional case.

## Case 4

- Treat each requirement as a separate rule question: exact prefix/tag scope, transition for current versions, possible transition for noncurrent versions, current-version expiration, noncurrent-version expiration and any delete-marker or incomplete-upload cleanup. The bucket has one lifecycle configuration containing rules; do not assume an added rule is isolated from other lifecycle rules.
- A lifecycle transition changes the storage class. It does not prove that the report is protected from deletion or that the business can meet an audit restore request. Confirm that the chosen class and restore process can fit the 12-hour promise with current guidance and an operational margin.
- In a versioned bucket, current expiration generally adds a delete marker. It does not delete the older version. If versions must be retained for five years, decide how transition and permanent noncurrent expiration apply to each version. Noncurrent age starts when a successor version is created, not when the original version was first uploaded.
- S3 Lifecycle may act on already-old matching objects after the rule is enabled. Inventory current and noncurrent versions first. Check transition ordering and minimum-duration charges; many small objects may not transition by default, and per-object transition charges can outweigh storage savings. Verify current behavior and filtering rules.
- Do not put legally held objects in an ordinary expiration scope and assume the tag filter can express every exclusion. Define an enforceable object classification and handling process, then check current S3 filter capabilities. Keep actual regulatory interpretation with the owner and counsel.
- Compare stored bytes/versions, requests, transition and retrieval charges, restored-copy duration, monitoring and operator effort using current regional prices. The case has no AWS rate or exact lifecycle configuration.
