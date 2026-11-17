# SAP-C02 task 2.5 knowledge review

The four knowledge points in the transitional [official performance task](https://docs.aws.amazon.com/aws-certification/latest/solutions-architect-professional-02/solutions-architect-professional-02-domain2.html#solutions-architect-professional-02-domain2-task5) have **partial** teaching and assessment mappings, checked October 19, 2026. This is not SAP-C03 coverage or a cloud benchmark.

| Point | Teaching and changed-case evidence | Still needed |
| --- | --- | --- |
| 1. Monitoring | Unit 02 distinguishes pressure signals from activity; the review packet changes CPU, connection wait and p99 customer time. | Representative per-stage and customer telemetry under peak/failure load. |
| 2. Storage | Unit 20 chooses object, file or block from the access contract; the packet changes a legacy POSIX writer to object publication. | Selected service interface, correctness, throughput, latency and price. |
| 3. Instance families | Unit 02 and existing family cases connect observed CPU, memory, disk and network pressure to candidates; the packet changes the bottleneck. | Selected Region/runtime compatibility and bounded A/B benchmark. |
| 4. Purpose-built databases | Unit 25 begins with transactional, analytical and search access; the packet preserves authoritative last-slot admission. | Selected service feature, lag, security, migration, cost and workload results. |

The [nine-case review](../../examples/professional-performance-path/README.md) and [assessor](../../examples/professional-performance-path/ASSESSOR.md) are fictional. Cases 1–7 supply the task 2.5 evidence above; the later global-delivery and placement cases support the separate task 3.3 review. The [cold-cache lab](../../examples/cold-cache-burst/README.md) tests controlled local concurrency only. Independent technical and learner review remains pending.
