# Distributed compute knowledge review

Internal editorial review, October 18, 2026. Checked all six knowledge bullets for [SAA-C03 Domain 3 task 3.2](https://docs.aws.amazon.com/aws-certification/latest/solutions-architect-associate-03/solutions-architect-associate-03-domain3.html#solutions-architect-associate-03-domain3-task2) against the retained official guide and current teaching. All six source-bullet digests match the accepted inventory. Each now has an individual **partial** teaching and assessment mapping; task-level assignment and knowledge mapping do not establish implementation or exam readiness.

| Ordinal | Teaching and assessment evidence | What remains missing |
| --- | --- | --- |
| 01 — Compute services | Unit 14 compares AWS Batch, EMR, Glue and simpler workers by the shape and ownership of the job; case prompts change runtime, data handling and parallel work. | Broader service/mode eligibility, selected Region pricing, measured runtime and recovery, learner assessment. |
| 02 — Distributed placement | Unit 02 distinguishes regional, edge and on-premises/Outposts placement by request path, authoritative data, network dependency and failure. Five cases change latency and connectivity. | Exact current service/runtime support, account/Region eligibility, measured latency, and what continues during failure. |
| 03 — Queuing and messaging | Unit 02 distinguishes holding a task for a worker, publishing to independent subscribers and routing events. Queue-recovery and event-reconciliation cases test duplicate, retry and durable-completion boundaries. | Selected AWS service-mode configuration, ordering/retention/replay guarantees, authorization, full costs and independent learner assessment. |
| 04 — Scaling capability | Unit 02 teaches target capacity, queue backlog, horizontal/vertical scaling, bottlenecks and hibernation; existing cases change duration, dependency capacity and restart behavior. | Installed controls, representative traffic, failover/scale-in timing and complete cost. |
| 05 — Serverless patterns | Unit 02 compares bounded event functions with container tasks and host-controlled EC2 using runtime, duration, state, scaling and responsibility. | Current mode/Region compatibility and price, representative performance, concurrency, downstream capacity and recovery tests. |
| 06 — Container orchestration | Unit 15 compares ECS/EKS responsibilities and makes scheduling, readiness, upgrades and remaining customer work visible. The design worksheet changes team capability, platform needs and failure expectations. | Selected ECS/EKS configuration, network/storage/identity, upgrades, workload recovery, regional cost and cleanup; local Docker evidence is not orchestration proof. |

These mappings reuse distinct existing teaching for each objective. Several cases are design-only, and local queue, SQLite or Docker behavior does not demonstrate an AWS-managed service. The retained official guide was checked by source hash, not refreshed from AWS during this review.

All six entries remain partial. Independent technical review, live service behavior and learner results remain pending.
