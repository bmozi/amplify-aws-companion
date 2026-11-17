# SAP-C02 task 1.4 skill review

All three skills in the transitional [SAP-C02 multi-account task](https://docs.aws.amazon.com/aws-certification/latest/solutions-architect-professional-02/solutions-architect-professional-02-domain1.html#solutions-architect-professional-02-domain1-task4) have **partial design-focused mappings**, checked 2026-10-19. No Organization, member account, resource share, event bus, trail or learner result is claimed.

| Skill | Teaching and assessment evidence | Missing evidence |
| --- | --- | --- |
| 1. Evaluate account structure | Unit 16 compares one, two and purpose-specific accounts; the packet requires each added boundary to justify its operations and cost. | Real workload/account requirements, effective access, suitable sandbox and independent learner transfer. |
| 2. Recommend central logging and notifications | Unit 16's three-path diagram and packet distinguish audit retention, selected operational event, delivery failure and recipient. | Scoped organization trail and selected data-event delivery; bus, DLQ and recipient checks. |
| 3. Develop a governance model | Unit 16 and the existing governance review cover onboarding, OU inheritance, baseline, delegation, share membership and retirement; new cases test a division exit. | Actual policy/control behavior, staged changes, emergency recovery and cost evidence in a suitable environment. |

The [paper packet](../../examples/multi-account-paths/README.md) has separate [assessor reasoning](../../examples/multi-account-paths/ASSESSOR.md). Organization-dependent work remains design-only here; live claims require a suitable, separately authorized environment.
