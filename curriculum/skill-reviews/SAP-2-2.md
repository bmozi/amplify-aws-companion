# SAP-C02 task 2.2 skill review

The six skills in the transitional [official business-continuity task](https://docs.aws.amazon.com/aws-certification/latest/solutions-architect-professional-02/solutions-architect-professional-02-domain2.html#solutions-architect-professional-02-domain2-task2) have **partial design-focused mappings**, checked October 19, 2026. The word “configure” in the official task is not satisfied by the paper exercise.

| Skill | Teaching and changed-case evidence | Still needed |
| --- | --- | --- |
| 1. Configure DR | Unit 07's full-chain plan and destination-key case specify components and owners. | Selected cloud configuration and controlled cutover. |
| 2. Configure replication | The replication/authority lesson and stale, corrupted and dual-writer cases test reasoning. | Actual selected data service, lag, promotion and conflict behavior. |
| 3. Test DR | The rehearsal lesson and passing-restore-job case separate resource from customer recovery; existing local gate is bounded. | AWS full-path drill and measured RTO/RPO. |
| 4. Automate affordable backups | The copy/restore chain and key/cost cases require schedule, destination, retention and validation. | Configured plan, complete current price, real restore and cleanup. |
| 5. Design availability | The failure-boundary lesson and standby/capacity cases expose missing dependencies. | Selected application/network/data failure and customer acceptance evidence. |
| 6. Central monitoring | The new monitoring chain names copy age, lag, restore, target capacity and customer outcome. | Effective signals, alarm delivery, responder action and recovery observation. |

The [packet](../../examples/business-continuity-path/README.md) and [assessor](../../examples/business-continuity-path/ASSESSOR.md) have not been tried by independent learners. No AWS account was used.
