# DOP-C02 task 2.3 skill review — automate complex work at scale

Internal curriculum review, October 19, 2026. Each objective has a specific teaching and assessment path and remains partial. The [official task](https://docs.aws.amazon.com/aws-certification/latest/devops-engineer-professional-02/devops-engineer-professional-02-domain2.html) names Systems Manager, AWS Config, Lambda and Step Functions as examples. The current AWS primary references are linked from Unit 16. No AWS account, managed node or workflow was queried or changed.

## Skill 01 — Automate system inventory, configuration and patch management

[Unit 16](../../reader/BOOK-LOCATORS.md#book-b139eca792554b54) separates node inventory from compliance and repair. It teaches fresh evidence, exact target selection, supported-platform checks, reviewed patch baseline, scan before install, canary/pilot/fleet rings, stop conditions and per-node reconciliation. The [fleet-maintenance lab](../../examples/fleet-maintenance/README.md) blocks an unexpected target, duplicate identity, stale inventory and an unmanaged target before its fictional effect boundary.

Partial: no Systems Manager Inventory, association, Quick Setup, patch baseline, maintenance window, organization policy or node was configured; no patch was installed; no reboot, application recovery or current price was measured. A future implementation needs a selected supported OS, account/Region, approved package policy, scoped non-root access, network/enrollment proof, a whole-run estimate within the account owner's chosen ceiling, an appropriate verified credit reserve and teardown/evidence plan.

## Skill 02 — Develop Lambda automation for complex scenarios

Unit 16 explains where an event-triggered Lambda could validate a fleet-change request and why multi-step scan/approval/install/verification may need explicit orchestration. Unit 13 compares Step Functions with Lambda Durable Functions and covers workflow state, retries and authorization boundaries. The lab binds a repeated local request ID to its reviewed target and baseline and rejects reuse for changed input.

Partial: there is no Lambda handler, AWS SDK call, event source, Step Functions state machine, Durable Function, execution role, retry configuration, alarm or deployed integration in this exercise. Local idempotency does not prove an external patch can occur exactly once. A future build must select the orchestration model for actual integration needs, bind credentials and payloads appropriately, test duplicate delivery and partial outcomes, and reconcile node state before retrying an uncertain operation.

## Skill 03 — Automate application software configuration to a desired state

Unit 16 distinguishes AppConfig delivery for application settings from State Manager desired configuration on managed nodes and AWS Config's observation/evaluation role. The figure and lab show the desired baseline and observed node version as separate records. The lesson describes where a maintenance window and canary health check fit before expansion.

Partial: no AppConfig deployment, State Manager association, configuration document, managed-node setup or rollback was executed. A future demonstration needs a harmless setting, test targets, explicit rollback/expiry behavior and customer-facing acceptance evidence. A document declaring desired state does not prove a target received or retained it.

## Skill 04 — Maintain software compliance with Systems Manager

Unit 16 distinguishes a patch scan from installation, a selected baseline from the installed package state, and a compliance result from business application health. It explains why stale or missing inventory is unknown, and why a rate-control stop does not undo work already running. The [local lab](../../examples/fleet-maintenance/README.md) checks the baseline version and retains per-node results.

Partial: no compliance association, patch policy, report destination, operating-system package state or security remediation was observed. The fixture's green result is not a Patch Manager result. Current patch baseline, supported OS/Region, desired timing, exceptions, reboot policy, cost and recovery evidence need verification for any selected live test.

## Assessment boundary

The separate [assessor notes](../../examples/fleet-maintenance/ASSESSOR.md) explain the six changed cases. The lab validates only its deterministic local policy model. It does not establish independent technical review, learner outcome, certification readiness, cloud behavior or book-release readiness.
