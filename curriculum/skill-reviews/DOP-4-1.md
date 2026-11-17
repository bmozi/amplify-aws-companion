# Individual skill review for DOP-C02 task 4.1

Internal editorial review, October 18, 2026. The [current official Domain 4 task page](https://docs.aws.amazon.com/aws-certification/latest/devops-engineer-professional-02/devops-engineer-professional-02-domain4.html) lists eight applied skills. Each now has a named teaching section and changed-condition assessment. The task remains partial and design-focused; these mappings do not claim a deployed CloudWatch pipeline.

## Skill 01 — Securely store and manage logs

Unit 08's [protection and retention section](../../reader/BOOK-LOCATORS.md#book-368538b501fc455d) teaches source allowlisting, separate writer/reader/deleter roles, log-group retention and the distinct handling of exported S3 objects. DOP case 1 changes the investigation retention requirement.

**Remaining:** establish an approved classification and retention policy, then test actual log access, deletion, export and recovery.

## Skill 02 — Create CloudWatch metrics from log events with metric filters

Unit 08's [metric-filter section](../../reader/BOOK-LOCATORS.md#book-40e61b066e93c914) distinguishes filter patterns from Logs Insights queries, new events from historical lines, no-match zero from missing input, dimension effects and duplicate delivery. DOP case 2 changes the event identity to a unique request ID.

**Remaining:** create and validate a selected filter on an eligible log group; observe real publication, dimensions, missing input and costs.

## Skill 03 — Create CloudWatch Metric Streams

The [separate stream-route section](../../reader/BOOK-LOCATORS.md#book-273dd1a9de20dc77) distinguishes metric updates from raw log events and connects namespace selection, Firehose and S3/external destinations. DOP case 3 changes the destination need from metrics to raw events.

**Remaining:** configure a supported stream/destination, verify IAM and output schema, observe delivery errors and price current update/destination use.

## Skill 04 — Collect custom metrics using the CloudWatch agent

Unit 08's [agent section](../../reader/BOOK-LOCATORS.md#book-c16fc77990c55e84) connects in-guest and application measurements to agent configuration, instance role and network path. DOP case 4 changes the signal from host to business behavior.

**Remaining:** install the agent, verify selected metric publication and failure behavior, and estimate full collection cost. No instance or agent was used.

## Skill 05 — Manage log storage lifecycles

The [protection and retention section](../../reader/BOOK-LOCATORS.md#book-368538b501fc455d) contrasts CloudWatch log-group retention with S3 object lifecycle and names access, deletion and evidence owners. DOP case 5 adds an approved longer archive requirement.

**Remaining:** implement the approved retention path, verify lifecycle behavior and cost, and prove required records remain retrievable for the promised interval.

## Skill 06 — Process log data with subscription filters

Unit 08's [subscription route](../../reader/BOOK-LOCATORS.md#book-273dd1a9de20dc77) discusses Kinesis, Lambda and Firehose, consumer capacity, retries, duplicate effects and log-recursion prevention. DOP case 6 adds a consumer whose own diagnostics enter the matched log group.

**Remaining:** validate selected destination throughput, delivery/retry semantics, deduplication, IAM, recursion exclusions and cost. No subscription or destination exists.

## Skill 07 — Search logs with filter/pattern syntax or CloudWatch Logs Insights

The [Logs Insights section](../../reader/BOOK-LOCATORS.md#book-7a3556fb3eeb88ad) gives a bounded query shape and explains narrow group/time selection and scan cost. DOP case 7 changes the time range and group scope.

**Remaining:** validate query syntax against representative stored logs, indexes/class eligibility where applicable, access controls and actual scan volume/cost. The local lab does not parse Logs Insights QL.

## Skill 08 — Configure encryption of log data

Unit 08 explains default service-managed encryption, optional customer-managed KMS, policy and availability dependencies, plus transport protection and S3 export boundaries. DOP case 8 disables the KMS key and asks what retrieval can still prove.

**Remaining:** configure and test actual KMS authorization, log read/write, key disable/restore and export encryption. No key or AWS data was created.

## Scope

The eight cases are original design prompts, not an exam simulator or learner result. Local telemetry tests validate only selected JSON/HTTP and arithmetic fixtures. Current AWS documentation and live behavior must be rechecked before implementation. Independent technical review and learner assessment remain pending. Organization-based log centralization is design-only.
