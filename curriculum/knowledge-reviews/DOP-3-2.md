# Individual knowledge review for DOP-C02 task 3.2

Internal editorial review, October 19, 2026; knowledge 04 evidence updated October 25. The [current official Domain 3 task page](https://docs.aws.amazon.com/aws-certification/latest/devops-engineer-professional-02/devops-engineer-professional-02-domain3.html) lists four knowledge areas for scaling solutions to business requirements. On October 19, the current official Markdown was fetched and all four source-bullet hashes matched the accepted inventory. Each item links to an explanation and changed-condition assessment. Coverage remains **partial**: local arithmetic and Kubernetes observations are not AWS throughput evidence or independent learner review.

## 01 — Appropriate metrics for scaling services

Unit 02's [scaling lesson](../../reader/BOOK-LOCATORS.md#book-4c46e3da6524fef5) distinguishes customer symptoms (completion, latency, errors), resource saturation, incoming request rate and queue age/backlog per worker. It explains how target tracking can turn an appropriate metric into a capacity change and why a healthy signal must account for startup and downstream bounds. The standard-library [scaling-policy model](../../examples/scaling-policy-model/README.md) reproduces a backlog-per-task target calculation and a separate database bottleneck case.

**Still required:** select and verify real CloudWatch metrics and statistic periods, test missing/late data and scaling delay, measure the selected workload, validate quotas and cost, and conduct independent learner assessment.

## 02 — Loosely coupled and distributed architectures

The lesson uses a durable queue as a waiting room when a customer can receive an “accepted, still working” state. It connects decoupling to stable job identity, bounded retries, poison handling, queue age and downstream protection. It stresses that a queue absorbs timing differences but does not add compute or supplier/database capacity. The DOP design route changes outage, retry and arrival assumptions.

**Still required:** verify end-to-end dispatch, duplicate handling, visibility/redelivery, back-pressure, failure recovery, measured delay and operating cost for a selected AWS service. Local formula checks do not test SQS or distributed delivery.

## 03 — Serverless architectures

Unit 02 differentiates a short API Gateway/Lambda request path from an asynchronous Lambda queue consumer and names execution time, concurrency, data and downstream boundaries. The assessment requires a safe relationship between event-source maximum concurrency, Lambda reserved concurrency and database connection limits, and asks what must be checked for the selected mode.

**Still required:** verify current Region/service eligibility, configuration semantics, permissions, retries, invocation limits, dependency protection, actual customer behavior and current full-path cost. No serverless capacity setting was changed or tested.

## 04 — Container platforms

The Unit 02 and Unit 15 lessons compare ECS on Fargate, ECS on EC2 and EKS by application requirements and operating responsibility. They distinguish Pod/task replicas from cluster/node capacity and require a concrete Kubernetes need before choosing EKS. The [local Kubernetes exercise](../../examples/kubernetes-reality/README.md) observes two ready Pods serving the wrong synthetic booking, a corrected rollout serving the expected value, and an oversized Pod that cannot be scheduled on a local node. Unit 15's container migration/release work and the DOP route support changed-case assessment.

**Still required:** deploy a selected AWS service only after cost review and identity prerequisites, then verify image/task/cluster configuration, scaling, health, drain, IAM, regional capacity, recovery and customer outcomes. A Rancher Desktop run does not establish ECS or EKS behavior.

## Limits

Four individual mappings do not close task 3.2, its five skills, all AWS scalability options or certification coverage. The local Kubernetes lab creates and removes only workstation resources; neither it nor the arithmetic model makes an AWS call or calculates an account-specific price. Independent technical review, real AWS service behavior and learner transfer remain open.
