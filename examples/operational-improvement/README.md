# Improve the repair service without making the incident worse

Maya's repair-booking service has three problems at once: technicians report late assignments, the team shipped a risky configuration change yesterday, and nobody knows whether the recovery instructions still work. A green process-health check does not answer any of those questions. This fictional packet is a design exercise for the transitional [SAP-C02 task 3.1](https://docs.aws.amazon.com/aws-certification/latest/solutions-architect-professional-02/solutions-architect-professional-02-domain3.html#solutions-architect-professional-02-domain3-task1). It does not configure AWS or prove certification readiness. Write a decision and evidence plan before reading the [assessor notes](ASSESSOR.md).

Read the [operational-improvement lesson](../../reader/BOOK-LOCATORS.md#book-d2dfbc74c642cc4d) and its [controller diagram](../../book/figures/monitoring-automation-paths.svg) first. Use the existing [local request-telemetry](../request-telemetry/README.md), [release](../local-operations/README.md), [monitoring-automation](../monitoring-automation/README.md), and [regional-recovery](../regional-recovery/README.md) exercises as bounded demonstrations of individual links. None is an AWS implementation of this whole case.

## Initial evidence packet

All times and values are invented. The customer promise is: at least 95 of each 100 eligible accepted repairs receive a technician assignment within 30 minutes, measured on a mature cohort. A booking acknowledged to a customer must survive a deployment or worker restart.

| Supplied observation | What it establishes | What is missing |
| --- | --- | --- |
| Yesterday 88 of 100 mature eligible repairs met 30 minutes; the preceding comparable day had 97 of 100. | A stated business measure missed its threshold in this packet. | Per-request causal path, comparable mix, telemetry completeness and current-day outcome. |
| Process health probes returned HTTP 200 throughout. Worker CPU averaged 38%; queue age reached 42 minutes. | The probe endpoint responded and the queue had old work. | Whether the oldest work was eligible, assignment attempts, dependency waits and customer notification. |
| Release R7 began at 14:00. A settings file changed the worker concurrency limit from 8 to 24 at 14:04. Queue age began rising at 13:50. | A change occurred after queue age had already begun rising. | A causal comparison, the effective setting on every worker, database connection pressure and rollback effect. |
| One sampled trace at 14:12 shows 17 seconds waiting for a database connection. Logs record 29 assignment retries, but only 21 have a correlation ID. | A possible bottleneck and a traceability gap exist. | Distribution across requests, duplicate effects and whether retries completed. |
| A CloudWatch alarm design watches queue age. Its proposed action restarts every worker whenever it enters `ALARM`; the notification target has never been exercised. | An automation proposal exists. | Alarm periods, missing-data behavior, delivery receipt, restart safety and recovery evidence. |
| A Systems Manager State Manager association is proposed to keep a host configuration file at the approved version. The team has not listed its managed nodes. | A possible desired-state owner is being considered. | Node enrollment, document, permissions, scope, conflicts with deployment and compliance result. |
| A runbook says “restore the backup and switch traffic.” The last exercise was 11 months ago. | A procedure exists on paper. | A decryptable restore, confirmed-booking reconciliation, writer fencing, surviving capacity, customer route and measured RTO/RPO. |

## Produce one improvement plan

For each decision, write **observation**, **inference**, **unknown**, **proposed action**, **stop condition**, and **proof of customer result**. Name the owner and the first reversible step. A tool name alone is not a plan.

1. **Measure and investigate.** Choose a customer-outcome indicator and the smallest supporting logs, metrics and traces that can separate queue backlog, connection wait and failed assignment. State correlation IDs, time window, retention and who may read the evidence. Explain why CPU and HTTP 200 cannot clear the customer promise.
2. **Improve alerting.** Give the queue-age alarm a denominator or eligibility check, evaluation window, missing-data rule and delivery test. Say who receives the alert, how receipt is observed, and when it escalates. Distinguish alarm transition, target acceptance, operator acknowledgment and customer recovery.
3. **Review deployment.** Compare all-at-once, rolling and blue/green rollout for this stateful worker. Specify the release artifact, configuration, migration compatibility, cohort metric, rollback trigger and what a traffic rollback cannot undo. Decide whether R7 is proven causal from the packet.
4. **Choose automation carefully.** Prioritize a bounded diagnostic or drain action against the proposed restart-every-worker action. Give a per-target scope, retry limit, idempotency rule, maximum duration and human stop owner. Explain how the action could worsen a shared database bottleneck.
5. **Assign configuration ownership.** Decide which setting belongs in versioned application release configuration and which, if any, belongs in a managed-node desired-state association. Explain how to discover target nodes and effective values before using State Manager. Distinguish State Manager from an application setting rollout and from AWS Config's resource-evaluation role.
6. **Exercise recovery.** Define a safe rehearsal that checks backup decryption, correct confirmed bookings, writer authority, capacity, route and customer observation. State the clock start/stop for RTO and the last durable point for RPO. Include a stop condition and cleanup inventory. Do not infer recovery from the existence of a backup or runbook.

## Change one fact and revise only what follows

1. The 14:12 trace is the only request with connection wait; a complete sample of 200 other requests shows fast database acquisition but slow technician-availability lookup. Which hypothesis weakens? Which customer metric still fails?
2. Every worker reports concurrency 24, but a read-only deployment record shows the same value was active two days earlier. Which proposed cause loses support? What still needs a controlled comparison?
3. The notification target rejects the first test message and accepts a retry. The alarm enters `ALARM` once. What delivery and human-response evidence now exists, and what does not?
4. A roll-back to R6 reduces queue age, yet 12 repairs already sent duplicate technician messages. What must be reconciled before saying the incident is over?
5. The restore decrypts and boots, but the restored store lacks the last three confirmed bookings. Which recovery claim fails even if traffic reaches the standby?
6. The State Manager association is scoped to one test node while three production workers have unmanaged local overrides. What is the safer first action? What must not be called compliant?

## AI-assisted review

Ask Codex to challenge your plan as an operator: “For each proposed change, show the exact supplied observation, a competing explanation, the smallest safe discriminating test, the rollback or stop condition, and the customer proof. Label claims that require live AWS evidence.” Check its service-specific suggestions against current AWS documentation. Keep your initial answer and revision so the model's fluency cannot stand in for evidence. Do not provide customer records, deploy resources, or ask the model to execute remediation in this exercise.

Compare your answer with the [assessor](ASSESSOR.md). A later cloud exercise would require a scoped non-root identity, current prices and credit eligibility, an estimated run within the account owner's chosen ceiling, a chosen credit reserve, resource inventory and cleanup. Organization-dependent recovery or fleet operations remain design-only here.
