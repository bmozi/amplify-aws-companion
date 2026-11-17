# Individual skill review for DOP-C02 task 3.1

Internal editorial review, October 19, 2026. The current [official Domain 3 task page](https://docs.aws.amazon.com/aws-certification/latest/devops-engineer-professional-02/devops-engineer-professional-02-domain3.html) lists five applied skills for implementing highly available solutions. Each maps to Unit 07's [high-availability decision lesson](../../reader/BOOK-LOCATORS.md#book-382878fd78726415) and a matching changed-condition prompt in the [DOP-C02 resilience design route](../../examples/resilience-path-review/README.md#dop-c02-task-31-resilience-design-route). All evidence is synthetic and design-only; every skill remains partial.

## Skill 01 — Translate business requirements into technical resiliency needs

The teaching starts with a customer promise and separates service-level agreement, application SLO, data correctness, allowable interruption and data-loss tolerance. The 99.9%-over-30-days arithmetic makes the requirement concrete without presenting fictional uptime as a measured or guaranteed result. Route case 1 changes the tolerance for a confirmed booking and asks what design question changes.

**Remaining:** independent learner transfer; stakeholder-approved objective; service-specific SLA review; measured customer behavior under a named failure.

## Skill 02 — Identify and remediate single points of failure

The manuscript asks the reader to follow the entire customer and recovery path: application, state, identity, keys, network, routing, quotas, deployment artifacts, external services and operator access. Route case 2 requires the reader to remove a supposed duplicate and explain what stops working. This checks dependency reasoning rather than rewarding a count of application instances.

**Remaining:** inspect an actual selected workload, rank and repair a real dependency, then test that the customer journey survives the chosen failure. The case does not establish any AWS control.

## Skill 03 — Enable cross-Region solutions where available

The lesson requires a service/feature/Region support check before treating the second location as an option. Route case 3 asks the reader to choose S3, DynamoDB or RDS data behavior, then account for lag, keys, permissions, quota, authority, promotion and cost. Organization-dependent deployment remains outside this exercise.

**Remaining:** verify the exact current service feature and Region, use an approved non-root identity, verify the account plan, and meet the account owner's chosen estimated-run ceiling and credit reserve, and test controlled propagation/recovery/cleanup. There is no live implementation evidence.

## Skill 04 — Configure load balancing to support cross-AZ services

Unit 07 explains that AZ-spread targets, health checks and surviving capacity have separate roles; its earlier resilience section also documents the ALB all-targets-unhealthy fail-open nuance. Route case 4 changes from one AZ failing to all targets reporting unhealthy and requires an admission/overload response.

**Remaining:** verify the chosen load-balancer configuration and cross-zone behavior, then test failure routing, health-check scope, customer acceptance and cost. No load balancer was configured or exercised in this work.

## Skill 05 — Configure applications and related services for multiple AZs and Regions

The lesson connects traffic movement to data authority, in-flight writes, stale DNS, capacity, identity, keys and external dependencies. Route case 5 combines a write in progress, 90-second data lag, cached clients and reduced standby quota, then asks for a staged failover and separate failback.

**Remaining:** deploy the selected service topology, verify component support and effective access, run controlled failure/failback tests, measure business RTO/RPO and customer outcomes, and reconcile attributable spend. No live topology or learner result exists.

## Overall scope

The figure, prose and cases improve objective-level curriculum evidence. They do not claim the five AWS implementation skills are complete. The `wgu` AWS session recorded in prior evidence was expired; this turn did not attempt AWS authentication or inspect account state. Independent technical review and learner assessment remain pending.
