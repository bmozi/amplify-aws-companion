# A locked copy still needs a usable restore

Maya's repair shop has three kinds of recoverable data: signed reports in S3, a VM disk snapshot, and database backups held in an AWS Backup vault. An attacker gains an operator identity and tries to erase the evidence. The team proposes one word—*immutable*—for all three. Your job is to name **exactly what is locked, for how long, who can alter that decision, and how the business will restore a clean, decryptable version**.

This paper lab supports [SAP-C03 skill 4.3.4](https://docs.aws.amazon.com/aws-certification/latest/solutions-architect-professional-03/solutions-architect-professional-03-domain4.html). It requires no account, resource or credits. Read the [data-protection lesson](../../reader/BOOK-LOCATORS.md#book-4f6cf1453aa8c153) and [recovery lesson](../../reader/BOOK-LOCATORS.md#book-20703bba15f79b2d), then answer before opening [the assessor](ASSESSOR.md).

The [chapter diagram](../../book/figures/locked-version-to-customer.svg) follows one report from a protected version to a usable customer read. Its arrows are checks to perform, not evidence that a restore happened. If the first ordinary key read returns “not found,” ask whether a delete marker is masking a retained version before declaring that the report is gone.

| Protect this | Candidate control | Protected unit | Important separate dependency |
| --- | --- | --- | --- |
| Signed S3 report | S3 Object Lock | An **object version**, with retention or legal hold | Correct version selection, KMS key and readable application path |
| VM recovery point | EBS snapshot lock | A **snapshot** for its lock duration | Volume creation, instance/application restore and keys |
| Managed backup | AWS Backup Vault Lock | Recovery points in a **vault**, under their backup lifecycles | Vault access, restore role, target environment and keys |

The table is a route to the questions, not an assertion that all three are appropriate for the same record. Check AWS's current [S3 Object Lock](https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lock.html), [EBS snapshot lock](https://docs.aws.amazon.com/ebs/latest/userguide/snapshot-lock.html), and [Backup Vault Lock](https://docs.aws.amazon.com/aws-backup/latest/devguide/vault-lock.html) documentation for exact behavior before any real change.

## Six decisions under attack and recovery

For each case, record **asset and version; threat; lock mode and retention owner; attacker action and expected observation; restore action and acceptance test; cost/cleanup consequence**.

1. **Hidden report:** The attacker issues an ordinary delete against the key of a protected S3 report. A new delete marker can make the current-key read look absent even while an older protected version remains. How does the responder find the intended version, verify it, and restore customer access without claiming Object Lock prevented every visible deletion? What happens if its KMS key is unavailable?
2. **Powerful operator:** A user with special governance-bypass permission wants to shorten a report's retention, while another user tries to delete a version protected in compliance mode. State the different authority checks. Would a legal hold change the first case? Do not treat an IAM `Deny` printed on paper as a live denial test.
3. **Frozen snapshot:** A locked EBS snapshot remains present. The VM cannot boot because the target image, instance configuration and KMS grant were not recorded. Distinguish proof that a snapshot was retained from proof that Maya can serve bookings. Include a clean-data and malware check before reconnecting the restored VM.
4. **Vault mode:** The team wants a Backup Vault Lock. Compare governance mode with compliance mode after the grace period. Name what must be approved **before** irreversible retention takes effect: lifecycle, minimum/maximum bounds, recovery owner, restore key access, storage growth, account closure consequences and an exit plan. Do not turn on compliance mode in a learning account.
5. **Wrong backup:** The attacker encrypted a database on Monday. Tuesday's backup succeeded and is locked. What evidence identifies a clean pre-attack recovery point, and how will a restored booking be checked against independent business records? A successful restore job does not make corrupted content correct.
6. **Second account or Region:** The team proposes copying protected recovery data to a separately governed location. Draw the source and destination principals, vaults/buckets, keys, retention settings, data-location rule, copy receipt, restore role and cost meters. A cross-account copy is a different authority boundary, not an automatic escape from bad key management.

## The acceptance record

An answer passes this *design* exercise only if it distinguishes the protected unit and mode, includes a denied destructive action **and** a successful restore of the intended clean version, states who may change or remove a governance lock, and calculates retention cost only after obtaining current quantities and rates. Record the untested cloud steps. Locking can preserve damaged data and impose long-running storage charges; test the recovery path before selecting a compliance-mode retention that cannot be shortened.

Ask Codex to play the attacker and then the restore operator. Make it identify a still-possible loss of access, a version-selection error, a key failure and an unpriced retention obligation. Require it to cite the current primary documentation above. Never provide real credentials, customer records or keys to the prompt. This exercise does not establish ransomware resistance, legal compliance or a measured restore time.
