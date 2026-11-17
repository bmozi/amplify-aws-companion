# Database type and economics worksheet

This paper exercise practices SAA-C03 task 4.3 skill 04: choose cost-effective database types for the data and questions. It creates no AWS resources and uses no account credentials. Read [unit 25](../../reader/BOOK-LOCATORS.md#book-69c5037a3871d530), complete the worksheet, then compare your reasoning with [the assessor notes](ASSESSOR.md).

## Scenario

A factory network has 400 sensors. Each reports one observation every ten seconds. Each observation contains a timestamp, sensor ID, factory ID, machine model, temperature, and pressure. The estimated arrival rate is:

```text
400 × (60 / 10) × 60 × 24 = 3,456,000 observations/day
```

This is a scenario input, not observed AWS traffic. The business proposes keeping raw readings for 30 days and one-minute rollups for three years. Treat those retention periods as unapproved proposals: the data owner must confirm incident, audit, legal and recalculation needs before deletion or aggregation.

Two queries matter:

1. An operator opens one machine and needs its recent 15 minutes of data for a near-real-time alert.
2. An analyst compares monthly averages for all factories and machine models over three years, normally once a day.

Candidates to investigate are a managed time-series database for the recent operational path; S3 with Parquet and Athena for historical column-focused analysis; and a warehouse service only if the actual join, concurrency or repeat-query needs justify it. These are candidates, not a prescribed three-service architecture. Timestream for LiveAnalytics is not an available new-customer candidate; AWS closed new-customer access on June 20, 2025.

## Workcard

1. Separate the workload descriptions. Which facts describe time-series behavior? Which describe columnar file layout? Explain why these labels can both apply to the same system.
2. Write down each path's freshness, query shape, retention, cardinality, recovery and access requirements. Mark unknowns instead of guessing.
3. Select one primary candidate for each query, with one credible alternative. State why the alternative loses under the current assumptions and what changed fact would make you reconsider.
4. Use the current AWS Pricing Calculator for one selected Region and service configuration. Record the lookup date and input values. Estimate ingest/write activity, retained raw and aggregate storage, compute or capacity, query frequency/bytes scanned, backups, transfer, dashboards and any transformation/catalog costs. Include idle hours and minimum charges where relevant. Do not copy a price from an old article.
5. Before entering dollars for Timestream for InfluxDB 3, use AWS's [cluster-billing guide](https://docs.aws.amazon.com/timestream/latest/developerguide/influxdb3.html) to compare one active cluster for a full illustrative month at **12 GB** and **240 GB** stored. What storage-charge equivalent applies under the documented **200 GB monthly minimum**? Change 12 GB to 8 GB, then 210 GB to 190 GB. State which change can lower that storage component and which cannot. Do not treat the charge floor as provisioned capacity or extrapolate this full-month comparison into a short-run bill.
6. Add node hours and the selected edition. Enterprise has a separate per-vCPU AWS Marketplace license line; list backups, transfer and other meters that remain unknown. Verify whether your account’s credits cover each line rather than assuming they do. No live cluster or paid feature is authorized by this paper exercise.
7. Compare both candidates using the same workload, retention and reliability assumptions. Identify cost items you cannot price confidently.
8. Describe a safe late-data correction and replay plan. State when a rollup is rebuilt and how the exact raw observation can be recovered while retained.
9. Ask Codex to challenge your decision. Require it to identify the requirement, source or arithmetic behind each claimed fact. Independently recheck prices and service limits in AWS sources; an AI answer is not price evidence.

For step 5, fill in the charge-equivalent column before looking at the assessor notes. Each row assumes one active cluster for the same illustrative full month; no regional price or credit balance is supplied.

| Case | Actually stored | Monthly storage-charge equivalent | What changed from the prior row? |
| --- | ---: | ---: | --- |
| Small pilot | 12 GB | ___ GB | Starting case |
| Smaller pilot | 8 GB | ___ GB | Four GB less data |
| Just above floor | 210 GB | ___ GB | More than the floor |
| Back below floor | 190 GB | ___ GB | Twenty GB less data |
| Larger dataset | 240 GB | ___ GB | Above the floor again |

## Change one fact at a time

Repeat the recommendation after changing each condition: the queried time range grows from minutes to years; device IDs become extremely high-cardinality; analysts run frequent joins across customer and machine data; events arrive several hours late; operators require single-digit-millisecond reads; a new workload proposes LiveAnalytics; the Region lacks the preferred edition; the owner extends raw retention; or the proposed InfluxDB 3 cluster holds far less than the monthly storage-charge floor. For each change, say which candidate or cost term changes and why. Do not assume that a service feature eliminates the need to test the full workload.

## Completion evidence

Submit the assumptions, arithmetic, candidate comparison, current dated calculator inputs, decision and reversal condition. A service name without its assumptions is incomplete. This paper exercise does not show that a service was deployed, that a price was independently verified, or that a learner can operate the design.
