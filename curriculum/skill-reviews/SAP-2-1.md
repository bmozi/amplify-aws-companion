# SAP-C02 task 2.1 skill review

The four individual skills in the transitional [SAP-C02 deployment-strategy task](https://docs.aws.amazon.com/aws-certification/latest/solutions-architect-professional-02/solutions-architect-professional-02-domain2.html#solutions-architect-professional-02-domain2-task1) have **partial design-focused mappings**, checked 2026-10-19. No managed deployment or reader outcome is claimed.

| Skill | Teaching and assessment evidence | Missing evidence |
| --- | --- | --- |
| 1. Choose upgrade path | Unit 03 and case 1 compare adding scoped server-side work to an existing web path with a whole-service migration. | Selected application/credential/queue integration and workload fit. |
| 2. Select deployment/rollback | Unit 03 and cases 2, 4 and 5 distinguish controller, infrastructure preview, traffic recovery, old-code compatibility and completed effects. | Selected cloud controller, alarms, IAM, live traffic/data recovery and cleanup. |
| 3. Adopt managed services | Unit 03 compares Amplify Hosting, ECS Express Mode, EC2 and ECS Fargate by chores AWS takes over and chores retained; App Runner is an existing-customer case only. Cases 3 and 6 change runtime/long-request behavior. | Actual supported runtime/platform, performance, cost, patch and operational checks. |
| 4. Delegate complex tasks | The managed source/image and deployment cases require exact artifact and authority handoffs plus residual customer ownership. | Live service execution, scoped roles, trust, failure path and customer acceptance. |

The [six-case packet](../../examples/professional-deployment-choice/README.md) has separate [assessor notes](../../examples/professional-deployment-choice/ASSESSOR.md). The local canary and schema exercises are meaningful bounded checks, not AWS platform emulation. Independent technical and learner reviews remain pending.
