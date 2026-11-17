# SAP-C02 task 1.2 knowledge review

The four individual mappings below are **partial authored teaching and assessment evidence** for the transitional [SAP-C02 security-controls task](https://docs.aws.amazon.com/aws-certification/latest/solutions-architect-professional-02/solutions-architect-professional-02-domain1.html#solutions-architect-professional-02-domain1-task2), checked 2026-10-19. They do not establish SAP-C03 coverage, AWS enforcement or reader mastery.

| Knowledge point | Teaching and assessment evidence | Missing evidence |
| --- | --- | --- |
| 1. IAM and IAM Identity Center | Unit 16 follows an external employee through federation, account assignment, role and protected export, while separating customer sign-in. The design packet changes a group assignment and departure. | No external directory, Identity Center, role session, assignment or offboarding was observed. |
| 2. Route tables, security groups and network ACLs | The integrated lesson and packet separate next hop, resource/subnet traffic gates and HTTP/record-level denial. Unit 31 gives the more detailed packet and return-path model. | No actual route, filter, packet or effective application policy was checked. |
| 3. KMS keys and ACM certificates | The lesson separates cross-account key-policy/IAM decisions, TLS endpoint identity and stored-object permission. Unit 19 develops the exact-version export; the packet changes key permission and tests adjacent denial. | No certificate, key operation, service integration or recovery decrypt was tested. |
| 4. Security, identity and compliance tools | The lesson distinguishes a selected CloudTrail data event, IAM Access Analyzer policy finding and Security Hub CSPM scoped control result. Unit 31 develops service roles; the packet tests missing/stale coverage. | No live finding, trail event/delivery, central policy, alert or investigation was observed. |

The [packet](../../examples/professional-security-design/README.md) links existing local permission, synthetic audit-join and control-matrix drills. Their supplied inputs cannot validate AWS IAM or service coverage. Independent technical and learner reviews remain pending.
