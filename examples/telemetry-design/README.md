# Keep telemetry useful and bounded

These are design cases and a local synthetic lab for unit 8. Use fictional data; do not create metrics, log groups or subscriptions. Before reading [the assessor notes](ASSESSOR.md), answer each case with the intended question, selected fields, cost drivers and evidence needed.

1. Two environments, three routes and two outcomes can occur in every combination. You publish two metric names using that one dimension set. Calculate the maximum distinct metric identities in this fixture. Then add a request ID that is unique across 1,000 requests, publishing both names for every request. Calculate that observed fixture's identities without multiplying by the environment/route/outcome product again. Explain why the first count is an upper bound until all combinations are observed.
2. An engineer retains request IDs as ordinary fields in embedded-metric log events but removes them from metric dimension sets. Explain what cost path has been reduced and what ingestion, storage, query and extraction costs still need review. Do not claim this makes logging or embedded metrics free.
3. The proposed route label is `/customers/812/orders/55?token=secret`. Choose a bounded route category for metrics. Decide which information, if any, belongs in a controlled investigation log. Explain why hashing every full URL can preserve both cardinality growth and sensitive linkability.
4. The trace sampler happens to capture 10 requests, two of which failed. A separate complete counter records 1,000 requests and 10 failures. Is 20% the application's error rate? Identify the different populations and which evidence supports the stated rate. Then explain the extra sampling information needed before using sampled data to estimate a population.
5. The application is healthy, but telemetry ingestion has stopped. The dashboard shows no new errors. Define an independent observation that distinguishes no failures from no evidence. Avoid making the detector depend only on the same missing event stream.
6. To reduce cost, a team proposes deleting all logs after one hour. The support team normally investigates incidents the next business day. Compare lower volume, fewer unnecessary fields, purposeful retention and controlled query windows. Which change preserves the investigation requirement? State who may read and delete the evidence, and how an exported copy is handled.

7. A queue has 60 waiting jobs in each of ten one-second observations and zero in the next fifty. Calculate the minute average, maximum and sum. Which value describes the highest observed backlog? Does the sum count distinct arrivals? Explain why a one-second dashboard refresh cannot recover detail from source measurements taken only once per minute. Distinguish observation frequency, metric resolution and aggregation period, then identify what higher resolution would cost and what decision it would support.

Transfer: a release adds a unique build ID as a metric dimension for every deployment. Decide when release-level diagnosis is useful, how identities accumulate over time, and whether logs or traces can carry detailed build provenance while a bounded metric set supports alerting. Estimate the whole telemetry path with current selected-service pricing before any cloud experiment.

## Run the missing-measurement experiment

From the repository root, run:

```sh
python3 examples/telemetry-design/lab.py
```

Before running it, predict whether 50 zero readings establish that the whole minute was quiet. The sensor is expected to report once per second. Its first ten readings are delayed; those readings contain the entire queue burst.

Read the two reports in order. The first has an observed average of zero but only 5/6 coverage and no whole-window average. The second includes the delayed readings: coverage is complete, average is 10 and maximum is 60. The earlier report was incomplete, not evidence of a quiet minute. This fixture revises an event-time window; it does not promise that any particular cloud alarm will replay an earlier decision after late data arrives.

The lab also checks exact duplicate replay, rejection of a conflicting observation, an event exactly at second 60, an empty interval and the difference between weighted and unweighted group means. Intervals include their start and exclude their end, so second 60 belongs to the next minute. Empty results stay unknown rather than becoming zero.

Change the burst to arrive on time, then remove one quiet reading. Predict the coverage and whole-window result before rerunning. The built-in assertions describe the original fixture, so revise the expected outcomes deliberately for your changed experiment; do not simply delete failing checks. Explain what evidence would justify interpolation before proposing to fill missing values.

The timestamp key is valid only for this stipulated single sensor with exactly one reading per second. Multiple sensors need separate identities; irregular observations need a different completeness model and a carefully defined time-weighting rule. The lab has no transport, clock synchronization, durable storage, retention, IAM or AWS API behavior. Its ingest function applies observations sequentially, not transactionally; it is a teaching fixture, not a production collector. Ask Codex to identify which assumptions would break with two sensors and require it to distinguish those limitations from observed local results.

## DOP-C02 task 4.1 collection and retention design route

Attempt these eight cases after reading Unit 08's [collection routes](../../reader/BOOK-LOCATORS.md#book-b7d5ab8137297b14). For each, state the question, selected data path, security/retention boundary, cost drivers, failure signal and evidence you would need before calling it configured. Then check your reasoning against the separate [task 4.1 assessor notes](ASSESSOR.md#dop-c02-task-41-assessor-notes). These are design cases; the local lab does not emulate CloudWatch.

1. **Securely store and manage logs.** The support team needs the previous business day's failed requests, while request payloads can contain names and session tokens. Choose an allowlisted event schema and access/retention boundary. Change the requirement so Security must investigate an event months later; explain which owner and retention decision must change.
2. **Create a CloudWatch metric from log events.** A JSON log records `statusCode` and a bounded route template. Propose a metric-filter pattern and metric value for server errors; explain whether a default zero is valid and what a quiet graph means if log ingestion stops. Then add a request ID as a proposed dimension and predict the cost and privacy effect.
3. **Create a metric stream.** The analytics team needs continually updated metrics in an S3 data lake. Choose namespaces and filters, then state what delivery role, Firehose path, update charges and destination evidence to verify. Change the ask to raw request events and explain why a Metric Stream no longer fits.
4. **Collect custom host metrics.** The on-call engineer needs EC2 in-guest memory or disk evidence that the selected default telemetry does not supply. Choose an agent/configuration/role path and the network access it needs. Then require application-level business counts and explain how they differ from host measurements.
5. **Manage log storage lifecycle.** Support needs next-day investigation while Finance has an approved longer archive requirement. Separate CloudWatch log-group retention from an exported S3 object's lifecycle, and identify deletion and restoration owners. Change the recovery window and recalculate which evidence must remain searchable.
6. **Process log data through a subscription.** A team wants matching events processed by Lambda and delivered with Firehose. Check throughput, retry behavior, idempotency, access and the destination's logs. Then include the consumer's own log group in the subscription and explain the recursive billing risk.
7. **Search logs with filter/pattern syntax or Logs Insights.** Find 5xx events on one route during a narrow incident window and show an aggregate by time bucket. Distinguish a Logs Insights query from a metric-filter pattern. Widen the time range and group selection; identify the additional cost and operational risk.
8. **Configure log encryption.** A log group contains sensitive but necessary support events. Compare default service-managed at-rest encryption and a customer-managed KMS key, then specify the reader, key and log-service permissions. Change the key state to disabled and explain the effect on retrieving older encrypted events.

For every case, mark organization-wide centralization or cross-account destinations as design-only. Do not create log groups, streams, metric filters, subscriptions, KMS keys or agents as part of the worksheet. Any later live lab must have a reviewed scoped identity, a current regional whole-run estimate against account-chosen spending and reserve limits, and a cleanup list.
