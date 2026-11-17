# SAP-C02 task 3.2 knowledge review

Internal editorial review, October 19, 2026, against the transitional [official security-improvement task](https://docs.aws.amazon.com/aws-certification/latest/solutions-architect-professional-02/solutions-architect-professional-02-domain3.html#solutions-architect-professional-02-domain3-task2). The seven concepts have **partial** authored teaching and changed-case assessment. They are not SAP-C03 coverage, legal advice or selected AWS-control evidence.

| Point | Teaching and changed-case evidence | Still needed |
| --- | --- | --- |
| 1. Retention, sensitivity and requirements | Unit 19 classifies every derived copy and separates owner-approved retention from a made-up legal period; packet cases 1 and 6 change embedded content and restored deletion. | Actual data inventory, applicable requirement review and effective lifecycle/hold controls. |
| 2. Automated monitoring and remediation | Unit 31 separates detection, evaluation, action and customer-safe result; packet case 7 reveals tag-wide blast radius from a test-bucket Config result. | Selected rule scope, freshness, action policy, failure and rollback evidence. |
| 3. Secret management | Unit 31 and the local two-worker overlap round distinguish supplier, store, consumers, cache and retirement; packet case 4 changes the lagging worker. | Chosen AWS store/rotation strategy, target integration, concurrent refresh and real revocation. |
| 4. Least privilege | Unit 31 and packet case 2 require exact object/key/session access plus neighboring denials and alternate-role review. | Effective IAM, resource/key policy and live allow/deny tests. |
| 5. Security services | Unit 31 distinguishes Inspector, Config, GuardDuty, Macie and Security Hub/CSPM by observation and scope; the packet changes missing data-event and finding evidence. | Actual service enablement, supported-resource/Region coverage, current price and finding disposition. |
| 6. Patching practices | Unit 31 distinguishes managed host baseline, next image and application dependency; packet case 5 changes their status separately. | Selected node/image/dependency repair, compatibility, staged rollout and customer check. |
| 7. Backup methods | Unit 19 and packet decision 6 require historical key access, confirmed booking, deletion reconciliation and customer route. | Selected timed, decryptable restore, RTO/RPO and retained-copy cost. |

The [packet](../../examples/security-improvement/README.md) and [assessor](../../examples/security-improvement/ASSESSOR.md) are fictional. The [local credential drill](../../examples/credential-rotation/README.md) tests only synthetic sequential HTTP behavior; it does not configure Secrets Manager. Independent technical and learner review remain pending.
