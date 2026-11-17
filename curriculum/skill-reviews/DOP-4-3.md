# Individual skill review for DOP-C02 task 4.3

Editorial review, October 18, 2026. The [current official Domain 4 page](https://docs.aws.amazon.com/aws-certification/latest/devops-engineer-professional-02/devops-engineer-professional-02-domain4.html) lists seven applied skills. Unit 08 supplies an illustrated control-loop lesson, one synthetic incident, a local policy lab and an original changed-condition assessment. Each skill is mapped individually and remains partial.

## Skill 01 — Configure solutions for auto scaling

The [service-specific scaling section](../../reader/BOOK-LOCATORS.md#book-5ebc7c97d935ded0) separates EC2 Auto Scaling groups, ECS services, ECS capacity providers, DynamoDB provisioned throughput, RDS storage autoscaling, and EKS workload/node layers. The linked scaling-policy model supports deeper backlog and capacity math.

**Remaining:** test an approved bounded service-specific policy with current limits and prices, actual scale evidence, downstream checks and cleanup. No policy is configured.

## Skill 02 — Create custom metrics and filters, alarms and notifications

The [alarm section](../../reader/BOOK-LOCATORS.md#book-6b65c05b82ba922c) distinguishes a measured input, alarm evaluation, state transition, SNS/Lambda destination and execution result. It asks readers to test missing data and repeated state separately.

**Remaining:** publish or select a scoped metric, verify the metric filter and dimensions, create a bounded alarm, test transition and notification permissions, observe actual delivery and record current cost. No CloudWatch resource changed.

## Skill 03 — Configure S3 events to process log files and deliver them

The [event-delivery section](../../reader/BOOK-LOCATORS.md#book-ea22a4995fe6369b) teaches S3 notification filtering, duplicate-safe object/version work, output-loop prevention, IAM, content classification and destination separation. The local lab checks repeated version delivery and an output prefix.

**Remaining:** validate an authorized isolated bucket, event destination policy, actual Lambda/queue invocation, duplicate/failure behavior, output and cleanup under current prices. No log files were moved in AWS.

## Skill 04 — Configure EventBridge event patterns for notifications

The same event section explains source/type/detail pattern matching, target permissions, retries, dead-letter handling, replay and feature-specific defaults. The lab applies a limited exact-field predicate to two fictional events.

**Remaining:** verify a real event schema, pattern matches and near-misses, role/resource policy, target delivery, configured retries/DLQ, monitoring and current cost. No event bus or rule was created.

## Skill 05 — Install and configure SSM Agent and CloudWatch Agent

The [agent distinction](../../reader/BOOK-LOCATORS.md#book-218e632ab96c8b22) teaches that SSM Agent supports node management while CloudWatch Agent collects selected host/application telemetry. Systems Manager can help manage installation/configuration, but agent presence alone does not prove metrics or logs are arriving.

**Remaining:** select an isolated supported node, verify agent version and SSM registration, apply a least-privilege instance role and explicit metric/log configuration, and test delivery, network failures and cost. No agent was installed or checked.

## Skill 06 — Configure AWS Config remediation

The [drift-remediation section](../../reader/BOOK-LOCATORS.md#book-218e632ab96c8b22) distinguishes evaluation evidence from runtime health and covers SSM Automation, freshness, resource scope, roles, parameters, manual-first rollout, bounded retries, cost and verification. The local lab tests explicit allowlist/freshness/action gates.

**Remaining:** implement a read-only or manual case first, verify rule scope and recorder, inspect current configuration, then validate least-privilege SSM Automation and retry behavior on a disposable isolated target. Organization/account-wide rules remain design-only.

## Skill 07 — Configure Route 53 and ALB health checks

The [health-check section](../../reader/BOOK-LOCATORS.md#book-ad2c765d6dd201aa) separates ALB target group state from Route 53 endpoint and DNS health, and both from customer business outcomes. It teaches the all-targets-unhealthy ALB fail-open behavior and DNS caching considerations.

**Remaining:** configure and test a safe endpoint, verify thresholds, reachability, traffic consequence and DNS behavior, and record charges. No DNS record, ALB or health check was created.

## Scope

The [fictional E21 packet](../../curriculum/EXERCISES.md#e21) integrates all seven design choices; the [local lab](../../examples/monitoring-automation/README.md) tests only a small subset of local routing and stop rules. Neither emulates or configures AWS. Current official source links are embedded in Unit 08. Independent technical review and learner transfer evidence remain pending; no certification readiness is claimed.
