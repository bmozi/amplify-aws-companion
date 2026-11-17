# Individual skill review for DOP-C02 task 3.2

Internal editorial review, October 19, 2026; skill 03 evidence updated October 25. The [current official Domain 3 task page](https://docs.aws.amazon.com/aws-certification/latest/devops-engineer-professional-02/devops-engineer-professional-02-domain3.html) lists five applied skills. Each maps to Unit 02's [scaling lesson](../../reader/BOOK-LOCATORS.md#book-4c46e3da6524fef5) and a separate prompt in the [DOP-C02 scaling design route](../../examples/scaling-policy-model/README.md#dop-c02-task-32-scaling-design-route). Coverage is partial; the container skill now has a separate local Kubernetes observation in addition to the arithmetic model.

## Skill 01 — Identify and remediate scaling issues

The reader compares p95 latency, errors, CPU and database wait to identify where useful completion is constrained. The local model calculates a queue target, then demonstrates that doubling worker capacity does not change a separately limited database ceiling. The scenario asks for the observation that would change the diagnosis.

**Remaining:** gather representative system traces/metrics, isolate the actual limiting resource, make a scoped repair and measure customer completion before and after. The model has no AWS metrics or workload variation.

## Skill 02 — Identify and implement appropriate auto scaling, load balancing and caching solutions

Unit 02 links scaling to an appropriate target signal and bounded capacity. The design cases distinguish task scaling from load balancing and from caching. The cache case changes a tenant-specific key and requires the learner to protect authorization and response isolation. Existing Unit 05 and Unit 11 material provide deeper network and tenant context.

**Remaining:** choose exact AWS policy/load balancer/cache settings; verify fresh and missing metric behavior, target health, cache keys/invalidation, customer denial boundaries, regional cost and rollback. No component was configured or tested.

## Skill 03 — Deploy container-based applications (for example, ECS, EKS)

Unit 02 and Unit 15 compare ECS/Fargate, ECS/EC2 and EKS responsibilities; the case starts with a long-running custom-library worker and adds a Kubernetes-specific requirement as a changed fact. The container-release exercise covers image identity, state, readiness, a known business result and drain. Its local deadline continuation measures one short request finishing after SIGTERM and one longer request being interrupted by a forced kill. The [local Kubernetes exercise](../../examples/kubernetes-reality/README.md) then deploys two ready Pods behind a Service on Rancher Desktop, observes a wrong booking response, rolls out corrected configuration, and records a separate Pod Pending for insufficient local CPU. These are local process and cluster observations, not a deployed ECS/EKS release or durable-work recovery.

**Remaining:** deploy a selected AWS platform and image only in an authorized bounded environment; verify cloud permission paths, ingress, scaling, representative load, actual stop timing, client and durable-work recovery, complete cost and cleanup. The local exercise does not test EKS or ECS, and organization-dependent variants remain design-only.

## Skill 04 — Deploy workloads in multiple Regions for global scalability

The lesson starts with geographic latency and keeps global reads, static edge content and authoritative writes separate. The case asks whether edge caching, regional reads, cells or data partitioning match the actual constraint and requires data authority and failback reasoning. AWS guidance is linked in the lesson.

**Remaining:** choose supported regional features and a data ownership model, then validate routing, quotas, access, replication/failure, customer behavior, latency and full cross-Region cost. This remains design-only in the personal trial; no Region or Organization was created.

## Skill 05 — Configure serverless applications (for example, API Gateway, Lambda, Fargate)

The lesson maps a short API request to API Gateway/Lambda and work that can wait to a durable queue with a Lambda or Fargate consumer. The design case asks for timeout, concurrency, retry, queue, database and cost boundaries; current AWS Lambda documentation links inform the event-source limits to recheck.

**Remaining:** verify current selected-mode and Region support, APIs, IAM, concurrency, redrive, dependency behavior, customer completion and cost. No API Gateway, Lambda event source or Fargate service was deployed in this update.

## Scope

The five prompts are authored design cases, not a calibrated exam or learner result. The local scaling model tests small arithmetic and invalid inputs; it does not emulate AWS. The Rancher Desktop case observes local Kubernetes behavior only. No AWS account identity, Free plan, credit balance, price or resource was checked or changed for this update. Independent technical review and learner assessment remain pending.
