# Assessor notes: route and verify an operational event

This is one defensible reading of the local packet, not an official answer key or AWS simulation.

## Expected event handling

| Input | Expected local result | Reason |
| --- | --- | --- |
| Account-specific AWS Health scheduled-change event for the fixture account | `NOTICE_AND_REVIEW` | It can create an informational notice and a scoped review item; it does not prove customer impact or authorize a configuration change |
| Public AWS Health event with no account resource | `NOTICE_ONLY` | It may be relevant service context, but it is not tied to an allowed resource that the workflow can mutate |
| CloudTrail security-group ingress change for the allowed account, Region and resource | `NOTICE_AND_REVIEW` | It records an API activity and creates separate notification/work records; it does not establish that the rule is harmful or still present |
| Same allowed event repeated | `DUPLICATE` | The local outbox suppresses repeat effects under the scoped fixture identity |
| Event from a different account | `OUT_OF_SCOPE` | A matching event name cannot substitute for explicit account authority |
| Event with incomplete envelope or unsupported source/type | `QUARANTINE` | Do not guess missing identity or invent a route |

For the CloudTrail case, the local workflow returns `WAIT_FOR_EVIDENCE` until a read-only inspection is recorded, then `WAIT_FOR_APPROVAL` until the fixture approval field is present. Only then does the fictional action execute. It returns `VERIFIED` only when the independent post-action check succeeds. A failed verification returns `UNVERIFIED_STOP`. If a call times out and the effect is unknown, or a post-action check fails, the next step is `INSPECT_PREVIOUS_ATTEMPT`, not another blind action. A verified effect returns `ALREADY_VERIFIED_IN_FIXTURE` on replay.

## Architecture decisions

AWS Health service events and CloudTrail API-call events describe different facts. A Health event may be public or account-specific, and the outer delivery Region is not the affected event Region. In an Organizations view, the envelope account may identify the receiving account while `detail.affectedAccount` names the affected account; this lab does not model that cross-account design. Health notices may have multiple communications/pages. CloudTrail management, data, network and Insights events have different collection requirements. Verify that the needed category was actually captured before designing a matching rule. A direct service event and a CloudTrail event about related activity should be correlated without deleting source evidence or assuming identical delivery semantics.

Choose a delivery pattern from the consumer contract. SNS fan-out or multiple EventBridge targets can notify independent subscribers. Separate SQS queues preserve independent durable work; one queue with competing workers distributes one worklist. Kinesis suits retained records with separate consumer positions and replay inside its retention window. SQS visibility, Kinesis checkpoints and workflow state each record different kinds of progress.

Use Step Functions when visible cross-service orchestration, branches, service integrations or shared workflow ownership matter. Consider Lambda durable functions for a code-first, Lambda-centered workflow with checkpoint/wait semantics. Compare supported Region/runtime, state storage, failure/replay model, observability, team ownership and total price. A small filter-and-notify path may need neither orchestrator.

## What this lab does not prove

No AWS Health account state, CloudTrail trail/event selector, EventBridge rule, SNS destination, SQS queue, Kinesis stream, Step Functions machine, Lambda function, permission, approval system, infrastructure change, notification, customer effect, price, credit or bill was inspected or changed. The local fixture does not validate service schemas, event delivery, retries, DLQ policy, actual fan-out, workflow persistence, AWS IAM, live approval identity or business recovery. It does not establish learner mastery or certification readiness.
