# Integrated release review: the discount that survives recovery

This is an original fictional evidence exercise for the [four-pass delivery lesson](../../reader/BOOK-LOCATORS.md#book-fac09bc05d613a74). It issues no commands and needs no AWS account. The supplied observations are invented; they do not describe our deployed Amplify app. Complete the individual E15 cases first or identify which prerequisites you still need.

## The promise and the change

Maya promises a ten percent discount on qualifying 1,000-cent quotes. Unexpired accepted quotes must retain their recorded price. A proposed release contains application artifact B and configuration revision C2. The prior combination is artifact A with C1. There is no claim here that either combination can run on a particular AWS service without additional configuration.

Use a six-entry release record: customer behavior; artifact/configuration identities; readers/callers; exposure evidence; recovery and completed effects; cost/cleanup. Keep absent information explicit.

## Packet 1: decide before seeing the explanation

At review time, the operator has these observations:

- The candidate starts and its health check passes.
- A candidate response identifies B/C2 and returns 1,000 cents for a qualifying quote.
- The selected frontend route sends requests to B. A nightly job's target has not been inspected.
- The error-rate chart contains no server errors, but no independent expected-price check feeds its alarm.
- A colleague proposes returning the frontend route to A and immediately deleting B's retained files.
- No current overlap estimate, running-resource inventory or verified recovery compatibility record is supplied.

Write your decision before reading Packet 2. Identify the observed defect, two important unknowns, the next evidence needed and what should stop expanding. Explain what returning the frontend route could change and what it cannot prove. Do not invent a current credit balance or declare the old combination safe merely because it is older.

## Packet 2: revise the decision

New fictional observations arrive:

- C1 contains a ten-percent discount; C2 contains zero. Both satisfy the configuration schema.
- A later frontend response identifies A/C2 and still returns 1,000 cents for the qualifying fixture.
- The nightly job calls B directly and does not use the frontend route.
- An old writer remains active. It updates a legacy contact field while newer readers prefer a previously copied replacement field.
- Invoice I17 has already been issued at the wrong price. The scenario does not supply payment status, correction policy or a complete list of affected invoices.

Revise the six-entry record. Which earlier hypothesis is weakened? Which observed defects now have distinct boundaries? Specify a candidate recovery sequence, its acceptance checks and the authority required for each action. Do not propose a single rollback command as the whole solution. Keep customer correction subject to the missing business facts.

## Packet 3: define evidence for closure

No further results are supplied. Write the evidence you would require to close the incident: serving identity and expected-price results across relevant callers; supported configuration/data combinations; reconciliation of affected records; observation of new work; and retained-resource ownership/cost. Label every item as required evidence, not a completed check. Include a condition that would make you stop recovery and escalate rather than continue changing the system.

## Change the problem

Replace the discount with an access rule. B/C2 reveals another customer's private quote, and A/C2 does the same. Explain how your containment, evidence handling and communication priorities change. State what cannot be undone by changing routing, without inventing a legal conclusion or sending a customer notification.

Only after recording your answers, ask Codex to identify an unsupported inference and a missing caller or writer. Keep its critique and your revision separate. Compare with [assessor notes](ASSESSOR.md). This is not an AWS runbook, scored mock exam or proof of learner mastery. A real run needs scoped access, an account-specific spending limit and credit check, and verified cleanup prerequisites.
