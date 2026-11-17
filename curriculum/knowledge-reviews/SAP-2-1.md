# SAP-C02 task 2.1 knowledge review

The four individual points in the transitional [SAP-C02 deployment-strategy task](https://docs.aws.amazon.com/aws-certification/latest/solutions-architect-professional-02/solutions-architect-professional-02-domain2.html#solutions-architect-professional-02-domain2-task1) have **partial authored teaching and assessment mappings**, checked 2026-10-19. This is not SAP-C03 coverage, cloud deployment or learner mastery.

| Knowledge point | Teaching and changed-case evidence | Missing evidence |
| --- | --- | --- |
| 1. IaC | Unit 09 distinguishes intent, state and observed resource; Unit 03's change contract treats an infrastructure preview as one gate. The case changes a stateful CloudFormation resource. | Actual selected plan/change set, permissions, rollback and drift evidence. |
| 2. CI/CD | Unit 03 develops source/build/test/delivery/deployment and existing local artifact/canary checks. The packet tests a new feature and failed canary. | Actual source connection, pipeline, tested artifact promotion and customer result. |
| 3. Change management | Unit 03 and the packet name deadline, approver, stop, prior state, data compatibility and completed-effect reconciliation. | Executed controlled change, independent approval and measured failure/recovery behavior. |
| 4. Configuration management | Unit 03 distinguishes application settings, AppConfig behavior and deployment artifacts; the packet changes a managed runtime and its data contract. | Selected AppConfig/Systems Manager configuration, effective consumers and failure test. |

The [six-case packet](../../examples/professional-deployment-choice/README.md) and [assessor](../../examples/professional-deployment-choice/ASSESSOR.md) are fictional. Existing local canary and schema labs cover only their stated behavior. Independent technical and learner reviews remain pending.
