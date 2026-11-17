# Individual knowledge review for DOP-C02 task 4.3

Editorial review, October 18, 2026. The [current official Domain 4 page](https://docs.aws.amazon.com/aws-certification/latest/devops-engineer-professional-02/devops-engineer-professional-02-domain4.html) lists four knowledge areas for automation and complex event management. Unit 08 teaches these as different control loops in one fictional service. The companion lab uses local fixtures only. All four mappings are partial.

## 01 — Event-driven asynchronous design patterns

Unit 08 separates an S3 object notification from an EventBridge content pattern and explains asynchronous delivery, duplicate-safe work, output-prefix loop prevention, target permissions, retries, dead-letter destinations and replay ownership. It links to official documentation for S3 delivery, S3 sequencer ordering and product-specific EventBridge retry behavior. The local packet checks one repeated object version, output filtering and an exact selected-field event pattern.

**Still required:** implement an approved S3/EventBridge path, demonstrate actual duplicate/failure handling and destination delivery, inspect IAM/resource policies, measure latency and current costs, and obtain independent technical and learner review. The lab does not simulate AWS delivery.

## 02 — Auto scaling capabilities across AWS services

Unit 08 distinguishes EC2 instance count, ECS desired task count, ECS EC2 capacity-provider instances, DynamoDB provisioned throughput, RDS storage and EKS pod/worker layers. It teaches metric fit, per-capacity demand, warmup, bounds, quotas, downstream bottlenecks and maximum cost. Existing scaling examples provide deeper workload math. No scaling policy was deployed.

**Still required:** choose one bounded service-specific case, confirm current Region/service availability and pricing, gather representative workload data, configure only an approved isolated target, observe scale-out/in and downstream impact, and verify cleanup. Organization-wide and production scaling remain design-only.

## 03 — Alert notification and action capabilities

Unit 08 separates metric evaluation, alarm state transitions, configured actions, target permission, execution result and customer-outcome verification. It discusses SNS, Lambda and supported EC2 recovery/action choices, missing data, duplicate-safe actions and stop conditions. The local test distinguishes a transition into `ALARM` from a repeated state.

**Still required:** configure an approved metric/filter, alarm and destination; check least-privilege invocation and topic access; induce bounded positive, negative and missing-data cases; record actual notification and response results and current cost. No alarm or notification service was used.

## 04 — Service health checks

Unit 08 distinguishes ALB target health from Route 53 endpoint checks and DNS failover, then connects each to (but separates it from) customer completion evidence. It includes ALB's all-targets-unhealthy fail-open edge case and Route 53's external/resolver timing boundary. No live endpoint or DNS record was checked.

**Still required:** select safe synthetic targets, verify configured health paths, thresholds, security-group reachability, health state and resulting routing, then record DNS/cache and customer-path behavior. A health response does not establish business completion.

## Limits

The individual mappings do not establish current service behavior for every feature, successful AWS configuration, cost, an account’s credit balance, independent technical review, learner understanding or exam readiness. A future live lab requires a scoped non-root identity, a reviewed whole-run estimate within the account owner's chosen ceiling, a verified account-appropriate credit reserve, explicit cleanup inventory and no organization-wide resources.
