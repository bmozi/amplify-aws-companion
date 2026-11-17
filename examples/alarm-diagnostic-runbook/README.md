# From alarm to a safe diagnostic runbook

Maya sees booking failures. Her CloudWatch alarm changes to `ALARM`, but that single fact does not show whether EventBridge matched the event, whether its target accepted the invocation, whether Systems Manager Automation ran, or whether bookings recovered. This packet follows those boundaries one at a time. It pairs with the [Unit 08 lesson](../../reader/BOOK-LOCATORS.md#book-000bf1124eccce79) and [E13](../../curriculum/EXERCISES.md#e13).

The [pattern](event-pattern.json), [fictional event](sample-event.json), [Automation document](diagnostic-runbook.json) and [target input](target-input.json) are source examples. The pattern names a **fictional** account and one alarm. The runbook calls only CloudWatch `DescribeAlarms` to read that named **metric** alarm's present state and update time. It does not repair a resource, install an agent, connect an EventBridge target, create a role, or run in AWS. The account and role ARNs are placeholders; replace them only after an authorized, cost-reviewed deployment plan. Do not paste the example into an existing rule.

Run the local drill from the repository root:

```sh
python3 examples/alarm-diagnostic-runbook/lab.py
python3 -m unittest discover -s examples/alarm-diagnostic-runbook -p 'test_*.py' -v
python3 -m json.tool examples/alarm-diagnostic-runbook/event-pattern.json >/dev/null
python3 -m json.tool examples/alarm-diagnostic-runbook/sample-event.json >/dev/null
python3 -m json.tool examples/alarm-diagnostic-runbook/diagnostic-runbook.json >/dev/null
python3 -m json.tool examples/alarm-diagnostic-runbook/target-input.json >/dev/null
```

The four JSON files can all be parsed locally with `python3 -m json.tool`; only an AWS-side test can validate the EventBridge pattern and SSM document against the services.

The Python matcher implements **only** the nested exact-string-list subset used by this pattern. It is not an EventBridge pattern engine. The classifier uses supplied fictional observations and returns the first boundary that lacks proof. It is not querying CloudWatch, EventBridge, Systems Manager or customer data. An absence in one dashboard interval might be metric latency or wrong scope; investigate before labeling the rule broken.

## When green counts belong to different events

Imagine a dispatcher sees one van sent and one repair finished. The totals match, but the finished ticket may belong to another customer. Likewise, `SuccessfulInvocationAttempts = 1` and one successful Automation execution do not identify the event that started that execution. The fixture's `evidence_links` are **invented retained receipts** for practicing the join: event ID at the target and Automation, an execution ID at start and observation, and the expected and observed booking cohort. They are not fields promised by an EventBridge metric or this static target input. An actual implementation must first determine which supported logs, execution history or explicitly passed correlation values can carry each link, then verify their permissions and retention.

The local program returns `LOCAL_EVIDENCE_ALIGNED` only when those fictional IDs agree and the supplied customer result is true. Change `observed_execution_id` to `fictional-execution-02` while leaving every counter green: it returns `CORRELATION_UNPROVEN`. Change `observed_customer_scope` instead and ask whether a successful booking for another cohort can close Maya's incident. A matching fixture is practice in *rejecting a false join*, not a real trace or recovery measurement. An unknown or absent receipt must remain unknown; never infer it from counts or nearby timestamps.

| Observation | Next distinction to investigate |
| --- | --- |
| No source event observed | Is the alarm the right kind and in the right account/Region? Does state history show the transition? |
| Event does not match | Compare exact source, detail type, account, Region, alarm name and new state. Use EventBridge's actual pattern test for a real candidate. |
| Match expected, rule metric absent | Check enabled rule, correct bus, propagation delay, metric dimensions and target configuration. No metric point is not itself a diagnosis. |
| Rule triggered, no target attempt | Inspect the rule/target and delivery metrics in the same interval; confirm target attachment. |
| Attempted, never accepted | Inspect target permissions, resource existence, retries, permanent failures and the target dead-letter queue. A queue entry means delivery still needs an owner and replay decision. |
| Target accepted, no Automation execution found | Correlate the target invocation with the exact document, parameters, account/Region and Automation execution history. Target acceptance is not runbook completion. |
| Automation succeeded, alarm still `ALARM` | The runbook only read current state. Diagnose the underlying failure and independently verify any approved repair. |
| Alarm recovered, booking still late | A green infrastructure state is not customer recovery; inspect mature booking outcomes. |

For a future bounded AWS lab, first review the [CloudWatch alarm event format](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/cloudwatch-and-eventbridge.html), [EventBridge rule troubleshooting](https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-troubleshooting.html), [delivery metrics](https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-monitoring-events-best-practices.html), [target DLQs](https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-rule-dlq.html), [EventBridge to Automation setup](https://docs.aws.amazon.com/systems-manager/latest/userguide/running-automations-event-bridge.html), and [Automation API step](https://docs.aws.amazon.com/systems-manager/latest/userguide/automation-action-executeAwsApi.html). A real target needs an exact document/version and required parameters, an EventBridge invocation role, a separate reviewed Automation role allowed to describe the selected alarm, and a scoped dead-letter queue policy. The static target input shows the parameter shape but cannot be a working role ARN until provisioned. EventBridge acceptance and Automation completion must be checked separately. Use an approved non-root identity and test both matching and nonmatching events. Keep any real repair as a separately reviewed action with approval, idempotency/uncertain-attempt handling and business verification.

Before any live run, verify current account identity, Region, plan and credit eligibility, and prices; estimate the complete route against spending and reserve limits chosen for that account. Bound event count, Automation steps, DLQ retention, logs and follow-up queries; inventory resources and teardown. Organization-wide routing or remediation remains design-only in this exercise. No live cost estimate or deployment is claimed here.

## Changed-condition cases

Write the first unproven boundary and next safe observation before reading [assessor notes](ASSESSOR.md).

1. The alarm event arrives in the expected account and Region, but its new state is `OK`. Should the diagnostic runbook start?
2. The event is an `ALARM` transition, but the account matches while the Region differs. Which field stops the rule? What if the alarm's affected resource is elsewhere?
3. The pattern matches and the rule metric grows, but `InvocationAttempts` remains zero in the same reported window. Which target and metric-scope questions come before a code change?
4. `InvocationAttempts` grows, `SuccessfulInvocationAttempts` stays zero and a message lands in the target DLQ. Is the incident resolved? Who owns inspection and replay?
5. EventBridge reports successful delivery to Systems Manager, but no corresponding Automation execution is found. What exact IDs, document/version, role and Region would you compare?
6. Automation reads `OK`, but the booking completion deadline still fails. Which source is authoritative for customer recovery, and what can Codex responsibly draft?
7. Every aggregate count is green and Automation finished. Its observed execution ID belongs to yesterday's alarm event, while today's target attempt has a different event ID. Which join is missing? What can the dashboard say without claiming today's runbook completed?
