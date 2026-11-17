# SAP-C02 task 3.1 knowledge review

Internal editorial review, October 19, 2026, against the transitional [official operational-excellence task](https://docs.aws.amazon.com/aws-certification/latest/solutions-architect-professional-02/solutions-architect-professional-02-domain3.html#solutions-architect-professional-02-domain3-task1). The five points below have **partial** teaching and changed-case assessment evidence. This is neither SAP-C03 remapping nor live operational proof.

| Knowledge point | Teaching and changed-case evidence | Still needed |
| --- | --- | --- |
| 1. Alerting and automatic remediation | Unit 08's controller diagram and whole-loop lesson distinguish alert receipt from safe, bounded repair. Packet cases 3 and 6 change delivery acceptance and automation scope. | Actual alarm/action configuration, target receipt, permissions, failure and cost. |
| 2. Disaster recovery planning | Unit 08 ties restore to correct confirmed bookings, writer authority, capacity and customer route. Packet case 5 invalidates a booted but stale restore. | Timed selected-service restore, RTO/RPO, data reconciliation and independent assessment. |
| 3. Monitoring and logging | Unit 08 connects mature customer outcome to queue, request, dependency and telemetry freshness. Packet case 1 changes the trace population. | Complete selected workload telemetry, access/retention controls and measured cost. |
| 4. CI/CD and deployment strategy | Unit 08 compares limited-wave, rollback and external-effect evidence. Packet cases 2 and 4 challenge release causality and incomplete rollback. | Scoped actual pipeline, compatible schema/data path and observed promotion/recovery. |
| 5. Configuration management | Unit 08 separates versioned application settings, State Manager desired state and AWS Config evaluation. Packet case 6 reveals unmanaged overrides. | Enrolled target inventory, effective values, association/document and permission checks. |

The [packet](../../examples/operational-improvement/README.md) and [assessor](../../examples/operational-improvement/ASSESSOR.md) are fictional authored material. Existing linked local labs cover narrower boundaries and do not establish this integrated AWS path. Independent learner and technical review remain open.
