# Individual skill review for DOP-C02 task 3.3

Internal editorial review, October 18, 2026. The [current official Domain 3 task page](https://docs.aws.amazon.com/aws-certification/latest/devops-engineer-professional-02/devops-engineer-professional-02-domain3.html) lists three applied skills for automated recovery. Unit 07, the regional recovery tabletop, the resilience path review and the local recovery gate now provide distinct prompts for each skill. Coverage remains partial and design-focused.

## Skill 01 — Test failover of Multi-AZ and multi-Region workloads

The [regional recovery exercise](../../examples/regional-recovery/README.md) makes learners decide whether to reopen, what remains unknown, how to handle a late write, and why failback is another migration. Unit 07 distinguishes AZ-level recovery from regional recovery, explains routing versus data authority, and requires customer acceptance evidence. The bounded resilience exercise keeps the fault, observer and recovery-operator paths distinct.

**Remaining:** no failover test has been run against RDS, Aurora, Route 53, CloudFront or another AWS workload. Service-specific behavior, live timing, data correctness, client reconnection and cost remain unverified.

## Skill 02 — Identify and implement cross-Region AWS Backup and recovery strategies

The new lesson and [recovery automation gate lab](../../examples/recovery-automation/README.md) ask the learner to choose and validate a candidate recovery point, check keys and dependencies, reconcile business data, fence old writers, prove capacity, and decide whether policy allows automated or human-approved cutover. AWS Backup and Systems Manager references ground the design in current primary documentation. The code is deterministic local policy logic only.

**Remaining:** no AWS Backup cross-Region copy, S3 recovery point, Systems Manager recovery runbook or resource-specific restore test was implemented. Organization-dependent cross-account variants remain design-only. Real role scope, supported resource/Region, encryption, price and cleanup require a separately bounded authorized plan.

## Skill 03 — Configure a load balancer to recover from backend failure

Unit 07's resilience-switch section differentiates target health from application correctness and names Application Load Balancer fail-open behavior when all registered targets are unhealthy. The new automation lesson puts the routing decision after data, authority and capacity gates; the [resilience path review](../../examples/resilience-path-review/README.md) changes target-health evidence and requires a safe degraded mode.

**Remaining:** no load balancer was configured or failed over. Target group health behavior, registered targets, cross-AZ capacity, request outcomes and any Region transition must be validated against a selected live configuration and current service behavior.

## Scope

The design cases and local gate are not an exam calibration, AWS emulator, deployment, measured recovery or learner result. Independent technical review and learner testing remain pending. Do not claim full certification coverage from this objective-level mapping.
