# SAP-C02 task 1.4 knowledge review

All three knowledge points in the transitional [SAP-C02 multi-account task](https://docs.aws.amazon.com/aws-certification/latest/solutions-architect-professional-02/solutions-architect-professional-02-domain1.html#solutions-architect-professional-02-domain1-task4) have **partial authored teaching and assessment mappings**, checked 2026-10-19. This is not SAP-C03 coverage, a deployed Organization or learner mastery.

| Knowledge point | Teaching and changed-case evidence | Missing evidence |
| --- | --- | --- |
| 1. Organizations and Control Tower | Unit 16 separates hierarchy, account creation, landing-zone baseline, guardrails and governance ownership. A07 and the six-case packet change the account split and member lifecycle. | Suitable organization environment, actual control/enrollment/access behavior and learner trial. |
| 2. Multi-account event notifications | Unit 16 illustrates a selected EventBridge sender-to-receiver path and separates it from an organization CloudTrail audit trail. The packet changes target permission, rule match, Region and omitted audit selector. | Live bus policy, target delivery/failure/DLQ, recipient and trail read evidence. |
| 3. Resource sharing | Unit 16 uses a supported RAM shared-subnet candidate, separates resource use from account administration and checks OU/Region/exit conditions. | Current selected resource support, live share/permissions/network/customer tests and learner trial. |

The [paper packet](../../examples/multi-account-paths/README.md) and [assessor](../../examples/multi-account-paths/ASSESSOR.md) are fictional. Existing local onboarding and audit-join labs test their own synthetic inputs, not these AWS integrations. Independent technical and learner reviews remain pending.
