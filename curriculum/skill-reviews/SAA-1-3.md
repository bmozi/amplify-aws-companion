# Individual-skill review: SAA-C03 task 1.3

Internal editorial review, October 18, 2026. The [official task](https://docs.aws.amazon.com/aws-certification/latest/solutions-architect-associate-03/solutions-architect-associate-03-domain1.html#solutions-architect-associate-03-domain1-task3) lists seven skills. The IDs are our positional identifiers; short labels below paraphrase the objectives. Each remains partial. The new [data-protection unit](../../reader/BOOK-LOCATORS.md#book-4f6cf1453aa8c153) supplies missing explanations, not a deployed control or a compliance opinion.

## Seven changed-case prompts

### Skill 01 — Translate obligations into controls

Maya's fictional retention periods appear in the lesson. A learner proposes reusing them for a medical business because the storage is encrypted. Explain what information is missing and propose a requirement-to-control evidence record.

Look for: no inference that fictional periods are legal requirements; accountable business owners, data categories, actual obligations, configuration and operating evidence. Service selection alone is not proof. The manuscript gives a method but no real regulated-workload assessment or control framework implementation.

### Skill 02 — Protect stored data

An encrypted object is downloaded by an authorized worker, which prints the content in a diagnostic log. Explain what storage encryption did protect, what it did not, and how envelope encryption relates the content key to its protecting key.

Look for: plaintext boundaries and copy inventory; separation of key types; supported service/library use rather than homemade cryptography. The diagram is conceptual. There is no new service encryption configuration, cryptographic lab or measured key-operation evidence.

### Skill 03 — Protect data connections

The browser uses HTTPS to the entry service, which opens another connection to the application. A valid certificate is shown, but one customer receives another customer's invoice. Identify three separate questions to investigate.

Look for: security of each connection, server identity/certificate validation and application record authorization. A browser padlock proves none of the full application's authorization policy. The [TLS boundaries lab](../../examples/tls-boundaries/README.md) now checks actual local trust and hostname rejection, a successful connection and a separate application denial. Its actor header is deliberately not real authentication. AWS endpoint configuration, certificate renewal and actual identity enforcement remain absent.

### Skill 04 — Authorize key use

An operator can fetch an object but decryption fails. A teammate proposes attaching a broad IAM allow. Identify the key, Region, caller, key policy, applicable IAM/grant path and service integration before deciding a remedy.

Look for: object access and key use as separate requirements; key policy participation rather than a universal rule that any IAM allow works; administrative versus runtime authority. The [two-door policy packet](../../examples/key-use-policy/README.md) now supplies bounded fictional S3 role and KMS key policy specimens, a vertical request-path figure, six changed cases and a static source-shape check. The learner must explain version-specific versus unversioned reads, `kms:ViaService`, encryption context and the S3 Bucket Key change. This remains partial: no IAM evaluator, actual positive/negative request, key state, independent reviewer or learner result was observed.

### Skill 05 — Protect recoverable copies

A restore creates a database successfully, but its application cannot decrypt the records. A replica also contains yesterday's mistaken changes. Explain why neither observation proves business recovery.

Look for: key/identity/configuration dependencies; a replica can propagate unwanted changes; actual application reads and reconciliation against accepted records. Unit 7 and the local restore lab provide bounded restore/reconciliation evidence. AWS encrypted backup, replication and timed recovery remain untested.

### Skill 06 — Govern access and lifecycle

A customer record is removed from the live application but remains in an export and a backup. A later restore makes it visible again. Draw the copy inventory and a reconciliation step before access resumes. Then add a hold on one object version.

Look for: explicit copy/retention requirements, a protected deletion/hold ledger and access distinct from retention. Unit 10's local file lifecycle checks do not enforce S3 lifecycle or Object Lock. No production deletion guarantee, regulated retention or locked-object cleanup has been demonstrated.

### Skill 07 — Maintain keys and certificates

A plaintext data key leaks. The team rotates KMS material and declares the existing content safe. Separately, an imported certificate approaches expiry while another regional certificate renews. Explain the two mistaken assumptions and name the next evidence needed.

Look for: key-material rotation does not re-encrypt data or remediate a compromised data key; replacement-key migration differs from rotation; imported certificates lack ACM managed renewal; regional resources and deployed endpoints require separate checks. The [local two-endpoint TLS exercise](../../examples/certificate-endpoint-change/README.md) demonstrates one path presenting a replacement and the other retaining the old certificate despite a fictional inventory claim. It also rejects a wrong hostname under the practice CA. This does not demonstrate KMS rotation, ACM renewal, real service association or customer-path verification in AWS.

**Changed case:** Both inventory records report success, but a validated client still sees the old certificate at east and that certificate expires tonight. Name the stop condition, the specific association or deployment owner to investigate, and the client-side observation needed to lift the hold. Then change the case so west presents the new certificate under the wrong hostname. Explain why an unverified TLS connection would be a false repair. Run the local lab only after predicting those outcomes.

## Staged recovery extension

Complete the [encrypted recovery packets](../../examples/encrypted-recovery/README.md) before opening their separate assessor notes. They extend skills 04–07 with old-export key dependencies, a different recovery caller, cancelled deletion leaving a disabled key, and deletion-ledger reconciliation. The changed rotation case asks whether retaining the same logical key changes the decision. This is fictional evidence interpretation, not a KMS execution or restore result; existing partial dispositions remain unchanged.

## Knowledge-list check and disposition

The task's four knowledge areas cover governance/access, recovery, classification/retention and encryption/key management. Unit 19 adds a coherent data inventory and protection lifecycle; units 7 and 10 provide recovery and file-state foundations. Detailed service-specific controls, classification/discovery implementation and complete key policies remain incomplete. A separate [partial knowledge review](../knowledge-reviews/SAA-1-3.md) now maps all four knowledge entries as partial, with classification teaching and implementation gaps explicit.

The previous manuscript contained recommendations to encrypt but lacked substantive key lifecycle and renewal reasoning. Added unit 19 with two text diagrams, original scenarios and primary-source references. Seven evidence rows now point to exact teaching sections and these prompts. All remain partial; no certification coverage, compliance, independent technical assessment or learner success is inferred.

For assessment, withhold these rationales until the learner supplies an explanation. Change one constraint and ask which conclusion changes and why. Record the actual response and evidence gaps rather than converting this authored answer guide into a passing score.
