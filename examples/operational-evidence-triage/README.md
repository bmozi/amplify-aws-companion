# Operational evidence triage: five different questions

This fictional, design-only exercise supports DOP-C02 task 4.2. It is not a live account, a CloudWatch/Inspector/Config emulator, a calibrated mock exam, or a diagnosis of any real service. Use the same made-up clock for all times: October 8, UTC. Read this packet and write your answers before opening [the assessor notes](ASSESSOR.md).

## The business report

Maya's repair-booking application accepted jobs, but technicians say assignments arrived late. The team used this promise: an eligible accepted job should receive an assignment within 30 seconds. A dashboard's anomaly alarm changed from OK to ALARM at 10:06. The release log shows version R2 began at 10:02. A manager says the release caused the delay and asks for an immediate rollback.

The following rows are complete only within the boundaries stated. They are invented exercise facts, not AWS observations.

| Source | Supplied evidence | What the packet does not supply |
| --- | --- | --- |
| Business metric | In the mature cohort from 09:00–10:00, 81 of 100 eligible jobs received an assignment by 30 seconds. The prior comparable hour was 93 of 100. | Job-level assignment records for the hour after 10:00; whether the two hours had comparable work mix |
| CloudWatch metrics | ALB target 5xx count rose from 2 to 12 per five-minute period. EC2 CPU stayed near 35%. The anomaly alarm uses the completed-job metric and entered ALARM at 10:06. | Whether the data stream is complete; the exact request causes; the full alarm and missing-data configuration |
| Dashboard | A CloudWatch dashboard shows the metric and alarm state. A separate fictional analyst dashboard shows hourly accepted work by channel. | Whether the dashboards refresh from complete sources or are shared only with authorized readers |
| Trace | One sampled request took 2.4 seconds; its Lambda span waited 1.7 seconds on a database call. | How many requests had the same path; unsampled requests; whether this one request was representative |
| RDS metric | `DiskQueueDepth` averaged 14 from 10:00–10:05, compared with 3 in the previous five-minute interval. RDS reports this queue depth at one-minute intervals. | Whether this database metric corresponds to the traced call; I/O latency, affected requests and the actual customer-level cause |
| CloudTrail | At 09:58 a management event records `AuthorizeSecurityGroupIngress` by assumed role `release-runner` in `us-east-2`. | Which caller path failed; whether the rule covered the affected target; required data events or a complete cross-account trail |
| AWS Config | Rule `restricted-ingress` evaluated security group `sg-example` as `NON_COMPLIANT` at 10:01. | Whether that group served the failed requests; the last known-good configuration; other unrecorded resources |
| Inspector | The target Lambda function appears as `Not scanning`; the reason is “unsupported runtime.” Its finding list is empty. A CIS scan for the unrelated build host passed level 1 yesterday. | Vulnerability status of the target function; applicability of the build-host scan to the application |
| Real-time stream | The log subscription sends selected application events to a fictional Kinesis Data Stream. `GetRecords.IteratorAgeMilliseconds` increased from 200 ms to 25 seconds between 10:00 and 10:10. | Whether the lag delayed customer assignment or only delayed analytics; consumer failures, retries and record completeness |
| Logs and files | A bounded Logs Insights query for 09:55–10:10 shows repeated `assignment_timeout` events. A saved ALB access-log file in S3 contains corresponding 5xx responses. | Whether every log group and object was included; exact service-side cause or all affected customers |

## Write the five-part triage

1. **Alarm and dashboard:** Explain what changed, what the anomaly alarm establishes, and what the CPU measurement cannot establish. Name one missing-data or denominator check.
2. **Trace and real-time stream:** State what the one sampled trace suggests. Explain what the RDS disk queue measures and how it differs from the customer job queue. Explain whether the Kinesis delay proves that customers waited for assignment. Identify the next consumer-side measurement you would request.
3. **Audit and compliance:** Explain what the CloudTrail event and Config result each say. Decide whether the timestamps prove that the security-group change caused the 5xx increase. Specify how you would check target identity, Region, freshness and rule scope.
4. **Inspector coverage:** Explain why an empty finding list is not clearance for the unsupported Lambda runtime. State what the unrelated CIS scan does and does not say.
5. **Log analysis and action:** Choose between Logs Insights for a short incident interval and Athena for stored service-log analysis; name the access, table/data completeness and query-cost facts needed. Give the manager one safe read-only next step and the evidence required before rollback.

For each answer, label statements **observed**, **inferred**, **unknown** or **proposed**. Keep the customer impact, account event, resource configuration, vulnerability scan and analytics delay as separate evidence claims until a supported link joins them.

## Change one fact at a time

After recording your first answer, revise only the affected conclusions when:

1. The CloudTrail event targets a different security group than the application's target.
2. The Config evaluation is three days old and no configuration history is available for the incident window.
3. Inspector begins scanning the function but returns `PENDING` for its first assessment.
4. Kinesis consumer lag returns to 200 ms while customer assignment remains delayed.
5. The Athena table misses the newest S3 partition and the Logs Insights source group has a five-minute ingestion delay.
6. The next business-hour sample has 100% assignment, but the delayed jobs from the first hour remain unresolved.

Name which source changed, which statement changes, and which conclusion remains unchanged. Do not convert missing evidence into a zero, a pass or a root cause.

## Run a small evidence join

The paper packet has a 100-job denominator. The [mini-incident file](mini-incident.json) adds only **three selected job records** from that fictional cohort. Picture a detective with three receipts from a box of one hundred: matching a receipt to a log is useful, but it cannot tell you what happened to every job. The file also includes a selected ALB error, application timeout, sampled trace, CloudTrail change, Config evaluation and Inspector coverage status. All identifiers and values are invented.

Before running the script, predict four outputs: the change from 93/100 to 81/100, which request ID appears in both the ALB and application records, whether the security-group event identifies the same resource as the proposed app target, and whether those joins prove that R2 caused the delay. Write what evidence is still missing. Then run:

```sh
python3 examples/operational-evidence-triage/reconcile.py
python3 -m unittest discover -s examples/operational-evidence-triage -p 'test_*.py' -v
```

The script reports a 12-percentage-point decline, one three-source request join, a same-target audit event and a same-target Config result **at its evaluation time**. It also shows incomplete log coverage, an unscanned Inspector target and two selected jobs still unresolved. None proves a release cause or authorizes rollback. AWS documents that a [CloudTrail event records account activity](https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-concepts.html), while a [Config evaluation has its own resource and timestamps](https://docs.aws.amazon.com/config/latest/APIReference/API_EvaluationResult.html). Joining their labels is an investigative step; it does not turn either into a request trace or customer result.

Copy the JSON to a temporary file and pass it with `--fixture PATH`. Change the CloudTrail `resource_id` to `sg-other`; the audit join should disappear while the request join remains. Move the Config time three days earlier; its incident-window result should disappear. Remove the application timeout row; the three-source join should disappear while the unresolved job records remain. Finally, change the mature cohort to 100/100; the new rate improves, but the earlier unresolved jobs still require reconciliation. Compare each prediction to [the assessor notes](ASSESSOR.md#small-join-assessor). You can ask Codex to suggest a read-only check after writing your own conclusion; require it to identify the exact source, resource and time behind any claim.

This fixture exercises local set and time-window reasoning. It does not parse native AWS event schemas, configure a dashboard or alarm, instrument X-Ray, query CloudWatch Logs Insights or Athena, consume Kinesis, evaluate Config, run Inspector, measure live cost, or demonstrate that a learner can diagnose an unfamiliar incident.

## AI-assisted practice

Ask Codex to critique your answer one evidence source at a time. Have it point to exact packet rows, identify the time and resource scope, and suggest the smallest read-only test that could distinguish two explanations. Then verify service claims against current AWS primary documentation. Do not give it live customer records or ask it to execute a rollback. A fluent AI-generated incident story is not a verified finding.
