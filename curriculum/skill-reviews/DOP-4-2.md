# Individual skill review for DOP-C02 task 4.2

Editorial review, October 24, 2026. The [current official Domain 4 page](https://docs.aws.amazon.com/aws-certification/latest/devops-engineer-professional-02/devops-engineer-professional-02-domain4.html) lists five applied skills. The teaching paths and changed-condition cases below are partial. The new small evidence-join lab runs only against fictional local JSON, not AWS telemetry.

## Skill 01 — Build CloudWatch dashboards and Amazon QuickSight visualizations

Unit 08 distinguishes an on-call operational view of metrics and alarms from a business-intelligence dashboard over prepared data. The packet requires the learner to inspect the question, data completeness, refresh, audience and authorized access.

**Remaining:** build and review selected dashboards, validate sharing/access and refresh behavior, and estimate current costs for the chosen users and data path. No dashboard was created.

## Skill 02 — Associate alarms with standard and custom metrics

The [alert section](../../reader/BOOK-LOCATORS.md#book-ce1b741acbdf8c71) identifies metric unit, statistic, period, evaluation rule, missing-data policy and action. The packet distinguishes anomaly signals from fixed thresholds and customer outcomes from instance CPU.

**Remaining:** configure selected standard/custom metrics and alarms, observe state transitions and missing-data behavior, verify destination delivery, and record current prices. No alarm was created.

## Skill 03 — Configure X-Ray tracing for supported services

The [request-path section](../../reader/BOOK-LOCATORS.md#book-5708148549f25b46) explains sampled traces and limits, then records the current X-Ray SDK/daemon maintenance transition and the need to examine OpenTelemetry instrumentation and service compatibility for new systems.

**Remaining:** select a supported API Gateway/container/Lambda path, configure IAM and sampling, trace representative requests, inspect missing spans and overhead, and record costs. No service was instrumented.

## Skill 04 — Analyze real-time log streams with Kinesis Data Streams

The [analysis-path section](../../reader/BOOK-LOCATORS.md#book-b016db366e956b98) separates delayed analytics consumer state from the customer request path. The packet changes iterator age while keeping customer delay constant and asks the learner to test consumer errors and end-to-end identity.

**Remaining:** create an authorized bounded stream or approved isolated target, validate producer and consumer records, lag, throttling, retry/duplicate handling and recovery, and estimate current charges. The synthetic packet is not a Kinesis emulator.

## Skill 05 — Analyze logs with Athena and CloudWatch Logs Insights

Unit 08 distinguishes narrow queries over retained log groups from SQL queries over stored S3 service logs. The packet changes the newest Athena partition and Logs Insights ingestion delay so that source freshness and completeness affect the conclusion.

**Remaining:** execute bounded queries on approved data, check schemas/partitions, permissions, scanned bytes, latency and current cost. No query or AWS log access occurred.

## Scope

The five cases and [small evidence-join lab](../../examples/operational-evidence-triage/README.md#run-a-small-evidence-join) are original practice, not a mock exam or learner result. Seven local tests cover source joins, stale records, incomplete logs and unresolved work; they do not implement any of the five AWS skills. All five skill mappings remain partial. The individual evidence ledger identifies current work and remaining service/Region, cost, human and learner evidence. Organization-wide dashboard variants remain design-only for this personal trial.
