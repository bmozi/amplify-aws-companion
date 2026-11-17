# SAP-C02 task 1.3 knowledge review

The three individual points in the transitional [SAP-C02 resilience task](https://docs.aws.amazon.com/aws-certification/latest/solutions-architect-professional-02/solutions-architect-professional-02-domain1.html#solutions-architect-professional-02-domain1-task3) have **partial authored teaching and assessment mappings**, checked 2026-10-19. This is not SAP-C03 coverage, an AWS recovery result or learner mastery.

| Knowledge point | Teaching and changed-case evidence | Remaining evidence |
| --- | --- | --- |
| 1. RTO and RPO | Unit 07 treats useful-service time and recoverable accepted data separately; the regional incident and 20-minute strategy case require both judgments. | Selected workload start/end and data-state measurements; independent learner attempt. |
| 2. Disaster recovery strategies | Unit 07 compares backup/restore, pilot light, warm standby, active/active and DRS for a supported inherited server. The professional packet changes server reconstruction time, readiness and costs. | Supported source and target review, DRS or chosen strategy configuration, full-path drill and cost measurement. |
| 3. Backup and restoration | Unit 07 distinguishes an online copy from a historical point; local SQLite reconciliation and the corrupted-order case require restore, replay and external-effect checks. | Selected AWS restore, validated recovered business state and measured duration. |

The [professional recovery packet](../../examples/regional-recovery/README.md#professional-recovery-choice) and [assessor](../../examples/regional-recovery/ASSESSOR.md#professional-recovery-choice-reasoning) are fictional design assessments. Existing local labs test only their stated models. Independent technical and learner reviews remain pending.
