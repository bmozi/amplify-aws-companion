# SAP-C02 task 3.2 skill review

Internal editorial review, October 19, 2026, against the transitional [official task](https://docs.aws.amazon.com/aws-certification/latest/solutions-architect-professional-02/solutions-architect-professional-02-domain3.html#solutions-architect-professional-02-domain3-task2). All eight mappings remain **partial**. The guide's verbs “designing and implementing” are not satisfied by the paper packet or local fixture alone.

| Skill | Authored evidence | Remaining implementation or review |
| --- | --- | --- |
| 1. Evaluate secrets/credentials | Unit 31 and packet decision 4 use the tested two-worker generic overlap; a failed new value stops retirement. | Selected Secrets Manager or other supported store, provider contract, real cache/revocation and permissions. |
| 2. Audit least privilege | Packet decision 2 and changed case 2 require positive exact-object read plus adjacent object/key/role denials. | Complete effective policy/context and real allow/deny observations. |
| 3. Review every layer | Unit 31's illustrated request gates plus packet decision 2 trace TLS, application owner, S3 and KMS separately. | Selected topology, endpoint paths and actual enforcement. |
| 4. Review traceability | Packet decision 3 joins principal/session, object, account/Region, event time and observation time; case 3 exposes historical data-event absence. | Trail/selectors, log retention and live event completeness. |
| 5. Prioritize vulnerability response | Packet decision 5 compares finding, affected asset, patch eligibility and fleet blast radius. | Selected threat/impact triage, action permissions, measured remediation and cost. |
| 6. Design and implement patch/update | Packet cases 5–6 separate host, next image and dependency with a small wave and compatibility gate. | Implement and observe node/image/application update and rollback. |
| 7. Design and implement backup | Packet decision 6 and changed case 6 require decryptable retained copy and deletion reconciliation. | Implement selected backup/restore, measure RTO/RPO and customer result. |
| 8. Employ remediation | Packet decision 7 fences resource IDs, repeatability, exceptions and stop ownership. | Authorized selected Config/Systems Manager response with live result and recovery evidence. |

The [reader packet](../../examples/security-improvement/README.md) has separate [author assessor reasoning](../../examples/security-improvement/ASSESSOR.md). No AWS control was configured, no customer record used, and no independent learner attempt observed. Organization-dependent cases stay design-only in this course.
