# SAP-C02 task 2.2 knowledge review

The five knowledge points in the transitional [official business-continuity task](https://docs.aws.amazon.com/aws-certification/latest/solutions-architect-professional-02/solutions-architect-professional-02-domain2.html#solutions-architect-professional-02-domain2-task2) have **partial** teaching and assessment mappings, checked October 19, 2026. These do not establish SAP-C03 coverage, AWS recovery or learner mastery.

| Point | Teaching and changed-case evidence | Still needed |
| --- | --- | --- |
| 1. Global infrastructure | Unit 07 explains AZ versus Region failure boundaries; case 3 changes prepared capacity and target time. | Selected placement, eligibility and tested disruption. |
| 2. Networking and routing | Unit 07 separates DNS, target health and writer authority; cases 1 and 4 reject a healthy route to stale or conflicting data. | Selected Route 53/network configuration, client cache and return-path tests. |
| 3. RTO/RPO | Unit 07 separates useful-service time from accepted-work loss; cases 1 and 3 require both calculations. | Measured full application interruption and recovered confirmed records. |
| 4. DR scenarios | Unit 07 compares backup/restore, pilot light, warm standby and active/active; case 3 changes prepared capacity. | Selected strategy cost, implementation and full-path drill. |
| 5. AWS DR solutions | Unit 07 and cases 2 and 6 distinguish cross-Region copy, target key, restore job and business validation. | Selected resource/Region/permission checks, restore, cleanup and billing evidence. |

The [six-case packet](../../examples/business-continuity-path/README.md) and [assessor reasoning](../../examples/business-continuity-path/ASSESSOR.md) are fictional design work. The existing local recovery labs prove only their own models. Independent technical and learner review remains pending.
