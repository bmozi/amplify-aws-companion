# Individual knowledge review for DOP-C02 task 4.2

Editorial review, October 24, 2026. The [current official Domain 4 task page](https://docs.aws.amazon.com/aws-certification/latest/devops-engineer-professional-02/devops-engineer-professional-02-domain4.html) lists five concepts for auditing and analyzing operational signals. Unit 08 places them in one fictional incident, and a [local evidence-join lab](../../examples/operational-evidence-triage/README.md#run-a-small-evidence-join) tests resource, request and time scope. These are partial mappings; no AWS service was enabled or queried.

## 01 — Anomaly-detection alarms

The [signal analysis section](../../reader/BOOK-LOCATORS.md#book-8f3b72d67789ceed) distinguishes a selected threshold from a learned expected-value band. It teaches that anomaly detection finds unusual metric behavior, not its cause, and that model configuration, alarm action and cost require separate review.

**Still required:** verify the selected statistic, model/training context, excluded periods, threshold, alarm state transitions, missing-data behavior, action delivery and current price in an authorized Region.

## 02 — Common CloudWatch metrics and logs

Unit 08 ties the customer completion rate, ALB target 5xx, EC2 CPU, RDS `DiskQueueDepth`, trace duration and log events to different questions. It explains that RDS disk queue depth counts I/O requests waiting on storage, not the application's business queue. The lesson asks readers to name the measurement, resource, statistic, time window, denominator and collection completeness rather than interpreting familiar service names as a diagnosis.

**Still required:** confirm metric dimensions, resolution, actual log coverage, supported resource metrics and workload-specific limits. The values in the exercise are invented fixtures.

## 03 — Amazon Inspector assessments

The lesson connects Inspector findings to scan coverage and freshness, then compares a CIS scan with a vulnerability finding. The packet's unsupported runtime demonstrates why an empty result does not prove a target is clear. The separate build-host CIS result does not transfer to the Lambda resource. It also identifies a freshness issue in the certification objective: “assessment templates” refers to Amazon Inspector Classic, whose support [ended May 20, 2026](https://docs.aws.amazon.com/pdfs/inspector/v1/userguide/inspector-ug.pdf); current Amazon Inspector uses different scanning workflows.

**Still required:** verify supported target type/runtime, activated scan type, benchmark platform, exact resource identity, latest coverage status, finding details and cost. No Inspector assessment or template was created.

## 04 — AWS Config rules

The lesson explains that a Config rule evaluates recorded resource configuration, at a particular scope and time. A noncompliant result does not measure application performance or prove that the resource served affected requests. The packet changes the resource ID and evaluation freshness as separate facts.

**Still required:** inspect an actual recorder/rule, trigger, resource scope, historical configuration items, result time and permissions. No account configuration or compliance state was queried.

## 05 — AWS CloudTrail events

The lesson separates event-history lookup from a configured trail or event data store. It calls out Region, management-vs-data event class, time range and retention. A visible API call is a useful audit clue, not proof that it caused a customer impact.

**Still required:** verify selected event selectors, trail/event-store coverage, integrity controls, destination, retention, allowed readers and costs. No trail or event history was opened.

## Limits

These five knowledge items have individual partial mappings to Unit 08 and the [fictional triage packet](../../examples/operational-evidence-triage/README.md). No AWS resource, event, trace, configuration, vulnerability, alert or bill was inspected. Independent technical review and learner assessment remain pending; no certification readiness is inferred.
