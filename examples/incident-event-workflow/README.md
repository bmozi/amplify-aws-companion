# Route and verify an operational event

This local lab tests a few event-routing and response-policy decisions using fictional AWS Health and CloudTrail records. It uses only Python's standard library and in-memory Python objects. It needs no AWS account, credentials, network, dependencies, Terraform or cleanup.

Run from the repository root:

```sh
python3 examples/incident-event-workflow/lab.py
python3 -m unittest discover -s examples/incident-event-workflow -p 'test_*.py' -v
```

Before running, predict the response to four records: an account-specific AWS Health event, a public Health notice, a CloudTrail security-group change from the allowed account and a CloudTrail event from another account. Then predict what happens when the allowed records are delivered again.

The teaching model separates three facts:

1. A **notice** can be emitted to one consumer while another consumer keeps its own response work item.
2. A **response workflow** may wait for read-only evidence or a human approval before the fictional action can run.
3. A successful local action result is not **verified** until a separate check confirms the expected state.

The model uses deliberately simplified event patterns, source identities and an in-memory outbox. It does not implement AWS Health or CloudTrail schemas in full, EventBridge pattern syntax, SNS/SQS/Kinesis delivery, retries, Step Functions, Lambda durable functions, IAM, API effects, approval authentication, event ordering, CloudTrail data-event configuration, cost or AWS service behavior. Its local `reviewer-fixture` value is not an approval token or security control.

## Try a changed case

- Change the AWS Health outer `region` while keeping `detail.eventRegion`. Which field represents where the event was delivered and which tells you about the affected resource?
- Change the Health event from `ACCOUNT_SPECIFIC` to `PUBLIC`. Why does the local policy notify but not enqueue a resource-changing action?
- Change the CloudTrail event name to a read-only operation or a data event. What must the real CloudTrail and EventBridge configuration capture before a rule can match it?
- Remove the resource ID from the event or use a resource outside the lab allowlist. Which evidence is missing, and should the response proceed?
- Make the action succeed but the verification fail. What must the workflow report and who owns the next step?
- Explain how independent SQS queues and Kinesis consumers differ from two workers competing on one SQS queue.

Then review the separate [assessor notes](ASSESSOR.md), the [illustrated lesson](../../reader/BOOK-LOCATORS.md#book-9de6aa8d009af85d), and original [E22](../../curriculum/EXERCISES.md#e22). The lab has zero AWS cost. Any future AWS exercise needs a scoped non-root identity, a reviewed whole-run estimate, account-appropriate spending and credit-reserve limits, a written cleanup inventory and current Region prices. Organization-dependent labs remain design-only unless separately authorized in a suitable environment.
