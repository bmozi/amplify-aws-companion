# SAP-C02 task 1.3 skill review

All four skills in the transitional [SAP-C02 resilience task](https://docs.aws.amazon.com/aws-certification/latest/solutions-architect-professional-02/solutions-architect-professional-02-domain1.html#solutions-architect-professional-02-domain1-task3) have **partial design-focused mappings**, checked 2026-10-19. No live AWS recovery or independent learner performance is claimed.

| Skill | Teaching and assessment evidence | Missing evidence |
| --- | --- | --- |
| 1. Design DR from RTO/RPO | Unit 07 turns the business clocks into an acceptance contract; the regional tabletop makes the confirmed-but-missing order decisive. | Measured selected-workload objectives and recovery result. |
| 2. Implement automatic recovery | Unit 07 separates automation steps from promotion authority; the local deterministic gate rejects incomplete reconciliation and an unfenced writer. | AWS implementation, service-specific health and failover behavior, safe abort and live drill. |
| 3. Develop scale-up/scale-out architecture | Unit 07 and the packet compare fictional 16-minute vertical replacement with six-minute added workers, AZ loss and a changed database limit. | Real scaling, placement, quotas, health, warm-up, customer load and cost measurement. |
| 4. Design backup/restoration | Unit 07's backup policy, local restore/reconciliation and historical corruption case cover point selection, replay and business checks. | Selected AWS backup configuration, restore evidence and whole-application recovery time. |

The [professional recovery packet](../../examples/regional-recovery/README.md#professional-recovery-choice) has separate [assessor reasoning](../../examples/regional-recovery/ASSESSOR.md#professional-recovery-choice-reasoning). Its inputs are fictional; local gate behavior is not AWS failover. Independent technical and learner reviews remain pending.
