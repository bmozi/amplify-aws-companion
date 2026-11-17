# SAP-C02 task 2.4 knowledge review

The six knowledge points in the transitional [official reliability task](https://docs.aws.amazon.com/aws-certification/latest/solutions-architect-professional-02/solutions-architect-professional-02-domain2.html#solutions-architect-professional-02-domain2-task4) have **partial** teaching and assessment mappings, checked October 19, 2026. They do not establish SAP-C03 coverage or actual AWS availability.

| Point | Teaching and changed-case evidence | Still needed |
| --- | --- | --- |
| 1. Global infrastructure | Unit 07 distinguishes AZ and Region failure boundaries; cases change the failed location and DNS answer. | Selected placement and observed service/data behavior. |
| 2. Storage and replication | Unit 07 separates online copy from historical restore; the corrupt-copy case requires supported replay and business reconciliation. | Selected data-service replication and tested restore. |
| 3. Multi-AZ/Multi-Region | Unit 07's survivor-capacity arithmetic and the packet change AZ loss, Region loss, cached clients and writer authority. | Complete selected deployment, failure drill and cost. |
| 4. Auto scaling | Unit 07 and Unit 22 separate requested workers, quota, placement, health and useful capacity. | Target-account applied limits and measured scale-up/failure. |
| 5. Integration | Unit 07's bounded-work discussion and the photo-queue case distinguish durable booking acceptance from later work. | Selected queue/outbox/status and retry implementation. |
| 6. Quotas | Unit 22 gives scope and units; the launch case separates permitted count, physical availability and role permission. | Current selected quota/usage and real launch/ready evidence. |

Cases 1–7 of the [now nine-case packet](../../examples/professional-reliability-path/README.md) and its [assessor](../../examples/professional-reliability-path/ASSESSOR.md) supply the task 2.4 evidence above. Cases 8–9 and the local growth screen support the separate task 3.4 review. Existing local queue, scaling and recovery fixtures have narrower scopes. Independent technical and learner review remains pending.
