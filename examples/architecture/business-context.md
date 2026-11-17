# Business context worksheet

Copy this for one scenario. Use invented data while learning. Unknown answers are discovery work, not permission to assume a production default.

## Explain the need before choosing services

- Who needs to accomplish what?
- What happens today, and what problem should improve?
- What observable outcome would show that the solution helped?
- Who owns the business rule and can confirm it?

## Describe a valid request

- Actors and allowed actions:
- Required data and validation rules:
- Legal states and transitions:
- Duplicate request behavior:
- Cancellation, correction, refund or compensation rules:
- External systems and their failure/retry behavior:

## Put numbers and ownership on constraints

For each target, record value, unit, scenario/load, owner, evidence source and whether it is confirmed or provisional.

- Response time and workload volume/bursts:
- Acceptable interruption and recovery time (RTO):
- Acceptable data loss measured in time (RPO):
- Data sensitivity, geographic restrictions, retention and deletion:
- Required audit evidence and who may access it:
- Monthly budget and expected cost drivers:
- Team skills, support hours and incident owner:
- Existing contracts, systems and migration constraints:

## Separate configuration from architectural change

- Which established pattern fits, and why?
- Which settings can safely be parameters within documented bounds?
- Which requirement breaks an assumption and requires a different design?
- Which two approaches were compared? Why was one selected?
- What is still unknown? Who must resolve it before deployment?

## Tie the decision to a test

| Requirement | Design decision | Positive test | Denial/failure test | Evidence | Owner |
| --- | --- | --- | --- | --- | --- |
| Fill in | Fill in | Fill in | Fill in | Not run | Fill in |

## Automation and operating boundary

- What may run automatically, in which environment and account?
- What must stop for a decision, and who decides?
- How are secrets supplied without entering source control?
- How are migration, rollback and retained data handled?
- How will cleanup be verified, including retained billable resources?

Status: discovery / designed / implemented / deployed / behavior verified / learner reviewed.
Record stages separately; mark only stages with supporting evidence.

## AI collaboration for this worksheet

Ask Codex to identify unknown requirements, distinguish settings from architectural changes, and propose evidence for each rule. Give it sanitized context and current source documents. Verify the answers with the business owner and actual tests. Do not allow it to invent a retention obligation, spending limit or recovery target. Record the selected assumptions and who confirmed them.

Apply this worksheet to the [equipment-rental transfer challenge](../business-transfer/README.md). Save the first design before opening its changed business requirements; the worksheet itself is not evidence of successful transfer.
