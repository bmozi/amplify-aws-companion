# Two paths, two receipts

Maya's repair website is already deployed. On Tuesday morning, a customer must save a request and later read only that request. The operator has a separate job: prepare and change the AWS resources that support the site. Read [Chapter 1's two-path lesson](../../reader/BOOK-LOCATORS.md#book-ea456464f3b64452) and its [diagram](../../book/figures/control-and-data-planes.svg). Write your answers before opening the [assessor](ASSESSOR.md). This is a paper exercise; it makes no AWS calls and incurs no cloud charge.

Use three evidence labels throughout: **configuration**, **service operation**, and **customer outcome**. One observation may support more than one label, but explain the exact inference. Do not turn a missing observation into a failure or a success.

## Case 1: two green lights

The release job reports that its infrastructure update completed. The homepage returns HTTP 200. A customer presses Save, gets an error, and no authorized status readback has been recorded.

1. What does each green light establish? Which business promise remains unresolved or contradicted?
2. Name the next two bounded observations you would seek without broadening permissions or changing several resources at once.
3. What evidence would show that a second customer cannot read the first customer's photograph? Why is a hidden download button insufficient?

## Case 2: prepare before the outage

Assume a *hypothetical* disruption in which an existing object read works but an attempt to create a new storage resource fails. The repair shop's recovery target is 20 minutes. Candidate A proposes creating a replacement resource and updating configuration during the incident. Candidate B proposes a prepared recovery resource, a tested way to direct authorized work to it, sufficient capacity, and a record-reconciliation procedure. None of those preparations has yet been observed in this case.

1. Which candidate has the stronger *design hypothesis* for this failure, and what could still make it fail?
2. List the pre-incident checks, the timed customer-path recovery checks, and the stop conditions required before calling the 20-minute target met. Include who may execute the switch and who confirms the customer's record.
3. Change one fact: the prepared resource exists, but it lacks the latest accepted repair. Does a fast traffic switch satisfy recovery? State the customer-visible consequence and the reconciliation or data-loss decision needed.

## Case 3: the silent audit gap

The operator finds no suspicious action in CloudTrail Event history. The team has not established whether object-level data events were collected. A customer's photograph might have been read by the wrong principal.

1. What can Event history's management-event scope tell you? What can it not rule out here?
2. Name the configuration and access evidence you would inspect for the exact object and time window, and the separate customer or object-read observation needed. Keep an unknown as unknown if the required evidence was never collected.
3. A proposal says, “Turn on every possible event source now; then yesterday's read will appear.” Identify the time error and the cost/retention decisions the future collection plan requires.

## Make the architectural decision

Write six lines: customer promise, control-plane dependency, data-plane operation, current evidence, rejecting observation, and next bounded check. Give Candidate A one advantage under a different stated condition, then explain why it loses under this case's hypothetical failure. Ask Codex to challenge one inference in your six lines and cite current AWS primary guidance for its service claim. Preserve your first answer, AI critique and revision separately in the [learning record](../../curriculum/LEARNING-RECORD.md).

This exercise uses an invented incident, not evidence of an AWS outage. AWS service operations and recovery mechanisms differ; consult the selected service's current documentation before implementation. Do not provision an ARC cluster, replica, duplicate storage path or data-event trail as part of this paper task. A later live exercise needs its own scoped identity, current price and credit checks, full-run estimate, reserve, stop conditions and verified cleanup. Organization-dependent recovery stays design-only in this exercise.
