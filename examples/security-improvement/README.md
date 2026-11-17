# Repair the protection path, not just the finding count

Maya's repair business stores customer photos, lets a supplier worker fetch approved jobs, and runs one inherited EC2 import host. A scanner reports a package finding on the host. A former supplier still has a role assignment. Last month's encrypted export uses an older key. The team proposes turning on automatic remediation and calls the system protected. Work through this fictional [SAP-C02 task 3.2](https://docs.aws.amazon.com/aws-certification/latest/solutions-architect-professional-02/solutions-architect-professional-02-domain3.html#solutions-architect-professional-02-domain3-task2) design packet before reading the [assessor](ASSESSOR.md). It is not an AWS control test or legal-retention determination.

Read [Unit 31's security improvement loop](../../reader/BOOK-LOCATORS.md#book-d6d08244f1004bcc) and the [data-protection diagram](../../book/figures/data-protection-boundaries.svg). Run the [local credential rotation](../credential-rotation/README.md) round for one concrete consumer/target boundary. The other sources below are exercise facts, not account observations.

## Supplied facts and uncertainties

| Fact in the exercise | What remains unknown |
| --- | --- |
| Customer photo P17 is restricted. A public guide was combined with it into a report draft; the downloadable PDF still contains the original image. | Which other thumbnails, caches, exports and AI summaries contain P17; approved legal retention and any hold. |
| The application checks the customer on its normal photo route. A supplier role can read `photos/*` and decrypt with a broad key policy. The supplier needs only one approved export version. | All effective policies, conditions, alternative routes and recent access evidence. |
| A synthetic audit export includes supplier role assumption, S3 object reads and a database write, but lacks one Region and some S3 data events. | Whether a missing row means no operation or an unobserved operation; which user/session maps to the write. |
| The import host's Inspector finding names a vulnerable OS package. Patch Manager's last compliant scan is 18 days old. The next machine image and an application dependency also contain separately versioned components. | Whether a patch is approved, installed and compatible; whether the host is enrolled and the newer image/dependency are affected. |
| A Config evaluation says a test bucket is noncompliant. An automatic Systems Manager remediation proposal would modify every bucket with a matching tag. | Evaluation freshness, exact target set, exception owners, action permissions and rollback behavior. |
| The supplier accepts credential A. The store has A and two workers cache it. The supplier can accept A and B during a transition. | The selected AWS secret store, rotation strategy, provider contract, worker refresh timing and ability to revoke a compromised value immediately. |
| Current writes decrypt with key B; last month's retained encrypted export needs key A. The backup catalog lists a nightly copy. | Whether key A is usable by the restore identity, whether the copy decrypts, which confirmed bookings it contains and how deleted records are reconciled. |

## Seven decisions to write down

For each decision, name the **risk, owner, exact scope, first read-only check, proposed change, negative control, stop/rollback condition, evidence after change and cost driver**. Label every statement observed, inferred, unknown or proposed.

1. **Data lifetime:** Inventory every copy of P17. Propose who may approve a public release version, what content must be removed, how retention and holds are determined, and how a restore avoids republishing a deleted record. Do not invent a statutory period.
2. **Least privilege and layers:** Narrow the supplier to one approved export version and the required decrypt operation. Trace its workforce/service principal, S3 authorization, KMS authorization, network/TLS path and application owner check. State an allowed read and adjacent denied reads; explain why a valid TLS connection or a bucket policy alone cannot prove the full result.
3. **Traceability and findings:** Choose the missing CloudTrail/account/Region/data-event observations and correlation fields needed to connect a supplier session to an object read. Decide what the Inspector finding and 18-day-old Patch Manager status each establish. An empty result from an uncovered source is not clearance.
4. **Credentials:** Propose an A-to-B sequence with a supplier overlap, store publication, both-worker positive checks, expiry/refresh and old-A negative check. If B fails at the supplier, state where the change stops. Compare this generic provider contract with a selected AWS Secrets Manager rotation strategy before promising no interruption.
5. **Patches and vulnerabilities:** Separate host OS patch, next image, application dependency and service configuration. Choose a small wave, compatibility/customer test, maintenance owner and revert path. Decide whether the finding warrants an immediate automatic fleet-wide install.
6. **Backup and restore:** Name the encrypted export, backup, key permissions, retention/hold state, last confirmed booking and deleted-record ledger. Rehearse a decryptable restore and customer-level correctness check in an isolated destination; define RPO/RTO clocks and cleanup.
7. **Bounded remediation:** Decide whether the stale test-bucket Config result justifies any action. If using automatic remediation later, fence exact resource IDs and accounts/Regions, test one target, prove repeatability, record outcome and stop on uncertain ownership. Distinguish recorded evaluation, action invocation, successful mutation and customer-safe state.

## Change one fact at a time

1. The public report's visible page hides the address, but its embedded image still contains it. Does the release decision change?
2. The supplier's S3 allow is narrowed, but its role can still decrypt unrelated keys and assume a second broad role. Which denial remains unproved?
3. The missing S3 data events are enabled only today. Can tomorrow's trail reconstruct last week's reads? What current question can it answer?
4. B is accepted by the supplier, but one worker never refreshes A before A is retired. Which positive test fails? How does an urgent compromise change the availability tradeoff?
5. The host shows patch compliant today, but the next image still contains the old package and the application dependency remains vulnerable. What must be repaired separately?
6. The backup decrypts, but the restore resurrects a photo whose deletion was approved yesterday. What must happen before customers regain access?
7. The Config result applies to a test bucket, while the tag-based repair matches a production archive under legal hold. What should the automation do?

## Use AI as a reviewer

Ask Codex to make a seven-row evidence table, flag every inference that crosses an account, Region, resource, version or time boundary, and propose the smallest read-only check that would change the decision. Give it only these fictional facts. Compare service behavior with current AWS primary documentation and verify local lab output yourself. Do not let it approve a retention rule, change an IAM policy, rotate a real credential or run remediation.

This packet creates no AWS resources. Any future selected live test needs a scoped non-root identity, confirmed service eligibility and regional price, an estimate within the account owner's chosen run limit, a chosen credit reserve, exact resource/cleanup inventory and later billing reconciliation. Organization-dependent controls stay design-only here.
