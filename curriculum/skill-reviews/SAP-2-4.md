# SAP-C02 task 2.4 skill review

The six skills in the transitional [official reliability task](https://docs.aws.amazon.com/aws-certification/latest/solutions-architect-professional-02/solutions-architect-professional-02-domain2.html#solutions-architect-professional-02-domain2-task4) have **partial design-focused mappings**, checked October 19, 2026. The implementation and operations verbs in the official task remain unproved in AWS.

| Skill | Teaching and changed-case evidence | Still needed |
| --- | --- | --- |
| 1. Design availability | Unit 07 turns the 600-request peak and one-AZ loss into survivor capacity and business checks. | Selected workload load/failure test. |
| 2. Design for failure | The switches lesson and packet change data corruption, DNS cache, quota and shared dependency. | Actual selected failover and recovery measurements. |
| 3. Implement loose coupling | The booking/photo case requires durable acceptance, retry identity, status and dead-letter handling. | Cloud queue/outbox implementation and failure tests. |
| 4. Operate failover | The managed database, ALB and operator-access case rejects green-status-only closure. | Live runbook, roles, failover/failback and customer evidence. |
| 5. Use managed services | The lesson distinguishes managed routing, data and queue chores from application correctness. | Chosen services' configured scope, failure behavior and current cost. |
| 6. Implement DNS policy | The new DNS lesson compares simple, weighted, latency, geolocation and failover by business question. | Selected Route 53 record/health configuration, cached-client and end-to-end tests. |

The [packet](../../examples/professional-reliability-path/README.md) and [assessor](../../examples/professional-reliability-path/ASSESSOR.md) have no independent learner result. No AWS resource or trial credit was used.
