# SAP-C02 task 1.2 skill review

All four skills in the transitional [SAP-C02 task 1.2](https://docs.aws.amazon.com/aws-certification/latest/solutions-architect-professional-02/solutions-architect-professional-02-domain1.html#solutions-architect-professional-02-domain1-task2) now have **partial design-focused mappings**, checked 2026-10-19. No AWS security control or learner performance is claimed.

| Skill | Teaching and assessment evidence | Missing evidence |
| --- | --- | --- |
| 1. Evaluate cross-account access | Unit 16 compares a direct data-account role with an application role requiring owner S3 and KMS grants. The packet asks for intended and forbidden object outcomes. | Effective policy simulation or live allowed/denied access with exact principals and resources. |
| 2. Integrate a third-party identity provider | Unit 16 distinguishes SAML sign-in, SCIM user/group provisioning, account assignment and remaining sessions. The packet includes missing assignment and departure cases. | Real federation, provisioning/offboarding, session lifetime and recovery-access testing. |
| 3. Deploy at-rest and in-transit encryption strategies | Unit 16 and Unit 19 trace TLS/ACM, S3 stored bytes, KMS key use, object approval and a denied adjacent version. | Selected service/certificate configuration, key policy, TLS negotiation, decrypt and restore behavior. |
| 4. Develop centralized security notifications and auditing | Unit 16 and Unit 31 distinguish trail source selection and delivery, Access Analyzer policy findings, Security Hub CSPM coverage and owner notification. The packet adds missing-data-event and stale-finding variations. | Organization trail, actual event selection/delivery, alert recipient and failure-route tests, cost/retention evidence. |

The organization-dependent design stays paper-only in this course. The linked local drills use synthetic facts and do not evaluate the actual AWS services. Independent technical and learner review and SAP-C03 remapping remain pending.
