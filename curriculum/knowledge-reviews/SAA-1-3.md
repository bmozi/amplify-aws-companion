# Individual knowledge review for SAA-C03 task 1.3

Internal editorial review, October 18, 2026. This records partial evidence for all four knowledge entries: access/governance, recovery, retention/classification and encryption/key management. Ordinals are our inventory positions, not AWS-issued objective IDs or scores. [Official domain source](https://docs.aws.amazon.com/aws-certification/latest/solutions-architect-associate-03/solutions-architect-associate-03-domain1.html#solutions-architect-associate-03-domain1-task3).

Fetched and parsed the official domain Markdown: task 1.3 contains four knowledge entries and seven skills. Ordinal 02 matches the accepted bullet SHA-256 `9e4ac0ae401f7a0067abe89959df05f8feeabd1f825b77cbd469e209f573d96e`. The fetched domain SHA-256 is `d810efd72bb4de4aaea8c5f8f80318653cd8c22b82f9531065a053deaf058962`; source retained at `artifacts/curriculum-research/saa-data-recovery-review-source.md`. A subsequent source fetch for the other three entries matched the same domain digest; retained at `artifacts/curriculum-research/saa-data-security-review-source.md`. Their individual digests and evidence follow below.

## Ordinal 02 — recovery teaching

[Unit 19](../../reader/BOOK-LOCATORS.md#book-a5e58766cd2ee7ee) follows an earlier encrypted export through its original key, recovery identity, supported reader and record reconciliation. It separates a successful current application read from evidence about an older recovery path. Its service-grounded retained-data-key example explains why a working component does not necessarily demonstrate that a replacement can start. The following recovery criteria require intended and denied customer reads before reopening access.

This supports data-recovery reasoning from a security perspective. It is narrower than a full encrypted-backup implementation. The export example explicitly defines its key type and application-level package; it does not imply that every AWS backup service uses the same encryption arrangement.

[Unit 07](../../reader/BOOK-LOCATORS.md#book-20703bba15f79b2d) adds business recovery targets, reconciliation and routing/write-authority decisions. Existing local restore exercises supply bounded SQLite behavior; this new mapping does not rerun them or treat their results as KMS verification. The author recorded a bounded browser-layout review of [Unit 19](../../reader/BOOK-LOCATORS.md#book-4f6cf1453aa8c153) in an owner-only log. That review does not establish reader understanding or a successful restore.

## Assessment and changed facts

The [encrypted recovery exercise](../../examples/encrypted-recovery/README.md) supplies four sequential packets and [separate assessor criteria](../../examples/encrypted-recovery/ASSESSOR.md):

- A working current reader uses a different key from an older retained export. Learners must reject recent success and quiet usage as sufficient retirement evidence.
- The recovery caller can fetch the package but cannot use its key. Learners must investigate the actual authorization path without inventing the responsible policy statement.
- Cancelled deletion leaves the key disabled. Learners must distinguish preservation, usability and demonstrated recovery.
- A readable export contains subsequently deleted records. Learners must reconcile before reopening access, rather than declaring the record count sufficient.

The final transfer changes replacement of a key into rotation within the same logical key. The reader must revise the dependency analysis while preserving the requirement for an actual recovery read. Answers should identify the supplied observation, the inference it supports, the uncertainty and the next discriminating evidence. Merely naming KMS or backups is insufficient.

## Remaining evidence

Coverage remains partial. Missing implementation includes selected AWS backup/export integration, protected recovery metadata, reviewed positive/negative key requests under the intended identity, fresh recovery-reader behavior, reconciliation enforcement, application cutover and measured business recovery against agreed targets. Cross-Region and cross-account recovery require their own design and permission evidence; the single-Region example does not cover them. Cost and retention assumptions also need workload-specific validation.

Independent learner answers and assessor calibration have not been collected. This review maps authored teaching and assessment; it does not award a passing result, imply complete certification preparation or increase the seven implementation-skill dispositions. Any future live experiment needs a scoped identity, current plan and credit review, and a whole-run estimate against spending and reserve limits chosen for the account. No cloud execution is needed for this review.


## Ordinal 01 — access decisions and accountable ownership

Bullet SHA-256: `eff16480fa8b4bc9204a8ab374528406dc694cb95386811499bf22951ec4fe55`.

Unit 19's “Turn a requirement into observable evidence” assigns intended readers and purposes to specific information, calls for an owner/control/test/evidence record, and inventories secondary copies. “Permission to fetch bytes is not permission to decrypt them” separates storage permission from key use and key administration. These explain different enforcement boundaries instead of treating encryption as permission to disclose.

The [skill-review prompts](../skill-reviews/SAA-1-3.md) test the reasoning through skills 01, 03 and 04: reusing fictional requirements for a different business, releasing another customer's invoice over valid HTTPS, and a failed decrypt despite object access. The existing rationales require the actual business owner, enforcing component and evidence. They must be withheld until the learner answers. The [TLS lab](../../examples/tls-boundaries/README.md) offers bounded local connection and synthetic record-denial behavior; its actor header is not authentication.

This is partial governance knowledge. Missing work includes a worked access-review lifecycle, role changes and revocation, exception approval/expiry, separation of reviewer and operator duties, verified identity integration and real data-owner decisions. None of the local fixtures proves an organization's governance process or compliance. A learner assessment should change the case so the technician's assignment ends while an old download link remains available; require identification of every surviving access route rather than a vague promise to remove the user.

## Ordinal 03 — retention evidence and classification gaps

Bullet SHA-256: `d382c1d5f3c4df1b4aef58905e987117f1a35fbdcbd7b9492342b22e57b7957b`.

Unit 19 distinguishes photos, invoices and diagnostic events by intended use, reader and fictional retention rule. “Retention and recovery can pull in different directions” extends the copy inventory through exports, backups, holds and reconciliation after restore. Skill-review prompt 06 and encrypted-recovery packet 4 require a decision about deleted records reappearing after restoration. This supports retention reasoning, including why a deletion of the current record is insufficient evidence about all copies.

The subsequent “Give the information a handling rule” addition supplies a fictional three-category scheme, explicit handling/audience rules, unresolved classification, derived-report restrictions and version-specific public release approval. Its [staged assessment](../../examples/data-classification/README.md) and separate assessor notes change preview, attachment, metadata and release-version facts. This addresses the previously identified absence of a worked scheme. Business-owner validation, actual classification/discovery, enforcement, redaction quality and learner evidence remain missing; the combined objective remains partial.

For a changed-case assessment, mix a public repair guide and a customer's private repair photo into one report. Ask whether the public source makes the combined report public, who decides, which recipients may receive it and how its copies inherit handling decisions. A sound answer identifies missing business classification rules and avoids deriving sensitivity solely from file extension, encryption or a service label. This additional authored prompt has not been trialed with learners.

## Ordinal 04 — encryption mechanisms and key lifecycle

Bullet SHA-256: `d57ccf8b2ef750d5ca339c79f464d7be9e1e2879b174510f4d086fc7a5e4c84a`.

Unit 19 explains TLS endpoints, plaintext boundaries, envelope encryption, storage/key authorization, logical-key replacement versus material rotation, certificate renewal and recovery dependencies. Its cryptographic migration section adds client/server compatibility and observed-negotiation questions without claiming deployed post-quantum protection.

Skill-review prompts 02, 04 and 07 test logged plaintext, failed key use, leaked data keys and certificate-renewal assumptions. The [cryptographic migration exercise](../../examples/crypto-migration/README.md) changes evidence about clients and intermediaries and challenges a proposed validation shortcut. The encrypted-recovery transfer case changes replacement of a logical key into rotation within it. Together these test distinctions beyond memorizing a service name; all assessor criteria remain provisional.

The local TLS fixture establishes only its reported connection outcomes. KMS key creation/policy/rotation, real service encryption configuration, customer authorization, managed certificate renewal and post-quantum negotiation remain unimplemented or unverified here. A full key-management lesson still needs a selected integration with operational ownership, failure recovery, cost and positive/negative access evidence. Do not add implementation coverage because this knowledge review now links the existing explanations.
