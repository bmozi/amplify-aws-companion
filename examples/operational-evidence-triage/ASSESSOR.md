# Assessor notes: operational evidence triage

Read the learner's first answer before using these notes. This is a reasoning guide for fictional facts, not an AWS finding, a live integration, certification scoring, or evidence that any learner has mastered the objective.

## 1. Alarm and dashboard

Observed: the mature 09:00–10:00 cohort is 81/100 within the promise, compared with 93/100 in the prior comparison hour. The ALB target 5xx values rose, EC2 CPU remained near 35%, and the supplied anomaly alarm entered ALARM at 10:06. The dashboard displays these inputs, but the packet does not prove source completeness, matching workload mix, or the alarm's full missing-data and evaluation rules. CPU is one measurement and cannot overrule the customer-outcome evidence. An anomaly band flags unusual values relative to a learned metric pattern; it does not identify a cause. Learners should request metric timestamps, statistic, denominator, population completeness and missing-data handling before comparing rates or acting.

## 2. Trace and real-time stream

The single sampled request suggests that its Lambda-to-database call dominated its 2.4-second path. It cannot establish the typical or total customer path. RDS `DiskQueueDepth` counts storage I/O requests waiting for service, not business jobs; its higher average and the sampled database wait justify a read-only correlation check but do not establish that they are the same bottleneck or that they caused all delayed assignments. Kinesis iterator age indicates the consumer is behind the latest records; it does not prove that Kinesis is in the synchronous assignment path. Check consumer errors, retries, records processed, throttling and end-to-end processing time, then join a trace or business event by a controlled correlation identity. A Kinesis stream can delay analysis without causing the original user-facing delay.

## 3. Audit and compliance

CloudTrail records a security-group ingress API action by the named assumed role in the stated Region and time. AWS Config reports that one resource failed one rule at one evaluation time. Their proximity to R2 and to the incident is temporal correlation, not causal proof. A sound follow-up checks the event's resource IDs and request parameters, the actual application load-balancer/target security-group path, the Config rule's scope and trigger, and configuration history immediately before and after the event. The packet does not establish whether relevant data events, other accounts, other Regions or a longer retention path were collected.

## 4. Inspector coverage

An empty finding list for a target that is `Not scanning` with an unsupported runtime is unknown vulnerability status, not “no vulnerability.” The CIS level-1 scan was for a different host and answers only the selected benchmark checks for that scanned host and time. It does not clear the Lambda function or establish exploitability. Verify scan coverage, target identity, supported runtime, last scan, scan type, finding status and any exception before proposing remediation. Inspector finding severity is a prioritization input; it does not by itself prove that a package is exploitable in the application context.

The task page's phrase “assessment templates” is legacy Amazon Inspector Classic terminology. [AWS's Classic guide](https://docs.aws.amazon.com/pdfs/inspector/v1/userguide/inspector-ug.pdf) says support ended May 20, 2026; current Amazon Inspector uses automated scan types and on-demand CIS scan configurations. Treat the distinction as a service-version check, not permission to use retired commands.

## 5. Log analysis and action

Logs Insights is a plausible first query for a narrow incident time range in the retained log groups. Athena is suitable for SQL analysis over stored service-log files in S3 once the table schema and partitions cover the needed interval. Neither tool compensates for missing upstream capture. Validate selected groups or buckets, UTC boundaries, event/object completeness, partition freshness, access permissions, and estimated scanned bytes before interpreting counts. Athena query charges depend on data scanned; CloudWatch ingestion/storage and query costs are separate.

The packet supports an observed customer-outcome decline, elevated ALB target errors, a sampled slow request, an account change, a rule failure, an unsupported Inspector target, a lagging analytics consumer and repeated timeout lines. It does not yet join those observations into one cause. A safe next step is read-only correlation of the exact target security-group identifiers and affected request IDs against request/target logs and the previous/current Config snapshots. A rollback would need a stated risk, compatibility and customer-impact decision; the supplied packet alone does not establish that R2 caused the condition or that rollback is safe.

## Changed-condition checks

1. A different security group breaks the proposed causal join; the CloudTrail call still occurred.
2. A stale Config result without incident-window history cannot describe the current incident resource state.
3. `PENDING` is an incomplete assessment, not an empty vulnerability result.
4. Kinesis recovery with continued business delay separates analytics lag from at least one customer-impact path; search for a different blocking dependency.
5. A missing partition and delayed log ingestion make current counts incomplete; do not compare them with complete periods as if equivalent.
6. The new healthy cohort does not erase earlier overdue jobs. Customer recovery requires resolving or explicitly accounting for the mature delayed work as well as the new rate.

## Small join assessor

The program calculates **93% → 81%**, a decline of 12 percentage points. `req-a` is present in the selected jobs, ALB errors and application timeout records. Three selected jobs cannot stand in for all 100 eligible jobs. In the base fixture, the CloudTrail event and Config evaluation name `sg-app` in `us-east-2`, matching the proposed app target, but the fixture does not show that affected traffic passed through that precise rule or that the rule change caused a timeout. The Config result describes one rule's evaluation at 10:01; it does not prove the target's behavior throughout the window. The log source declares incomplete coverage, so even a successful request-ID join cannot make the whole interval complete. The Inspector target is not scanning, so an empty finding list is unknown coverage rather than clearance. The 25-second analytics lag does not prove customer assignment waited on that consumer. Two selected jobs remain unresolved even if a later cohort improves.

Changed cases should affect only their own joins: a different security group removes the audit target match; a three-day-old Config evaluation cannot describe the incident window; removing the timeout record removes the three-source request intersection but does not erase job records; a 100/100 new cohort changes the rate, not earlier unresolved work. A sound answer keeps the next action read-only: inspect request routing and configuration history for the exact target, verify source coverage, and reconcile the customer jobs before deciding whether a release action is justified. These are fictional reasoning checks, not AWS service tests or a calibrated rubric.

## Objective boundary

The five DOP-C02 task 4.2 knowledge items and five skills are mapped to this lesson and packet as **partial**. The packet has no AWS traces, Kinesis records, CloudTrail trail, Config recorder, Inspector activation, dashboard, billing, permission check or query execution. The material requires current service/Region validation, live behavior and cost evidence, independent technical review, and a learner's changed-case attempt before stronger claims are warranted.
