# SAP-C02 task 2.5 skill review

The five skills in the transitional [official performance task](https://docs.aws.amazon.com/aws-certification/latest/solutions-architect-professional-02/solutions-architect-professional-02-domain2.html#solutions-architect-professional-02-domain2-task5) have **partial** design and local evidence mappings, checked October 19, 2026. No selected AWS workload performance has been measured.

| Skill | Teaching and changed-case evidence | Still needed |
| --- | --- | --- |
| 1. Large-scale paths | Unit 02 follows booking, photo and reporting stages; the packet asks for the limiting stage under changed arrivals. | Complete selected workload and failure-path measurements. |
| 2. Elasticity | Unit 02 links scaling signal to customer promise; the packet changes CPU, database wait and queue deadline. | Actual policy, metric freshness, warm-up, guard and cost. |
| 3. Cache/buffer/replica | Unit 21 and the new local burst demonstrate duplicate cold reads, in-process coalescing and failed-load retry; cases change replica freshness and durable photo buffering. | Distributed coordination, selected cache/queue/replica behavior and customer results. |
| 4. Purpose-built choice | Unit 25 and changed transaction/report/search cases require access semantics and comparative tests. | Selected regional service, compatibility, performance, migration and price. |
| 5. Rightsizing | Unit 02 and the bounded A/B case separate memory, CPU, network and disk hypotheses. | Representative selected instance benchmark, failure headroom and whole cost. |

The [packet](../../examples/professional-performance-path/README.md) and [assessor](../../examples/professional-performance-path/ASSESSOR.md) have no independent learner outcome. The local concurrency drill is not ElastiCache or a database benchmark; the AWS account and trial credits were untouched.
