# Choose a deployment method by the promise you need to keep

Run these cases after reading [the release-method lesson](../../reader/BOOK-LOCATORS.md#book-170e68d4296d3984). Try each case before opening [ASSESSOR.md](ASSESSOR.md). These are fictional, design-only cases. They create no AWS resources and do not prove a deployment configuration works in an account.

## Start with the customer promise

Imagine changing the roof while people are inside a building. An in-place deployment repairs the current room while it is being used. A blue/green deployment prepares another room, checks it, then moves people across. Canary and linear describe how much work is sent to the new room over time. Rolling deployment replaces a service's workers in batches while keeping the agreed minimum healthy capacity. Each choice has a different failure boundary.

For each case write down:

1. The deployment controller and its supported method for the selected platform.
2. The exposure unit: which instances, requests, alias weight, task set or tasks can change?
3. One health signal and one customer/business signal. State what observation would stop expansion.
4. How long it takes to observe representative work, and what “too little evidence” means.
5. Temporary capacity, traffic, artifact or data costs while old and new versions overlap.
6. The compatible recovery target, any irreversible side effect, and proof recovery worked.

Do not assume “10 percent” means 10 percent of every customer group, “healthy” means the customer's task succeeded, or a successful deployment command proves the intended business result. For ECS, name the controller and strategy separately: the ECS controller can use rolling or traffic-shifting strategies, while CodeDeploy is another controller for a replacement task set.

## Cases

### A. Appointment API on EC2

Twelve tagged instances run an appointment API behind a load balancer. A release changes request validation. The team can tolerate some instances being updated at once, but the database schema must stay compatible with both versions for one day. The old fleet is near capacity during peak hours. Choose between CodeDeploy in-place and blue/green, then state the instance deployment configuration, capacity check, health/business evidence and recovery conditions. Explain whether “one instance at a time” is equivalent to a canary request percentage.

### B. Customer pricing Lambda

An API invokes a Lambda function through the `live` alias. A new version changes discounts, and incorrect charges are high impact. The function has validation tests, CloudWatch alarms and enough representative traffic for a small initial cohort, but some customers receive only a few requests per hour. Choose canary, linear or all-at-once. State the candidate evidence needed before expansion, how quiet cohorts are handled, how the alias returns to the known version, and how charges already produced are reconciled.

### C. ECS service with two task sets

An ECS service uses an Application Load Balancer. The release changes a response format; an optional test listener and two target groups are available. Keeping both task sets running for 30 minutes is affordable. Choose the CodeDeploy ECS blue/green traffic plan and explain what the test listener proves, what it cannot prove about real customers, when the old set can be removed, and how to check that the new task set is actually healthy.

### D. ECS service with a strict task budget

A native ECS rolling service wants to replace six tasks. The team can run at most eight tasks during deployment. It requires at least five healthy tasks at all times. Some requests last several minutes. Derive the practical overlap and stopping constraints from `maximumPercent` and `minimumHealthyPercent`; decide if any task can start or stop at once. Explain what drain behavior and in-flight request evidence you need, and identify which controller detects an app-level error.

### E. Small, low-impact static tool

A static internal tool has no writes and can be redeployed quickly. Only two people use it, and a short interruption is acceptable. There is no measurable traffic for a canary sample, and duplicate old/new hosting would incur a monthly charge. Decide whether an all-at-once cutover or blue/green is justified. Name a cheap pre-release check, a user-visible verification, and a rollback option. Explain why “more gradual” is not automatically safer when the sample is empty.

### F. A team asks for “blue/green canary on Amplify”

A team assumes its Amplify Hosting branch setup automatically provides CodeDeploy's weighted traffic shifting. The application is a frontend with a separate API and database. Clarify what must be verified about the actual Amplify deployment feature and the API/data changes. Propose a safe alternative evaluation path if the desired traffic control is not available, including how to stop automatic publication. Do not invent Amplify capabilities or silently substitute a different deployment service.

### G. A team asks for an “ECS canary”

An ECS service currently uses the ECS controller's rolling strategy. The team wants to send a small share of production requests to a candidate while retaining the old revision for a measured interval. It has an Application Load Balancer and enough temporary capacity for both revisions. Compare staying with rolling replacement, selecting the ECS controller's canary strategy, and using CodeDeploy ECS blue/green with a canary traffic configuration. Name the exposure unit and routing prerequisite for each. State what the existing service configuration and Region must support, what extra resources and charges to estimate, what observation would stop the shift, and how to prove both new-request recovery and accepted-work reconciliation. Do not infer that setting `maximumPercent` creates weighted request routing.

## Transfer check

Change one condition: the old release cannot read the new schema, the peak doubles, customer traffic becomes sparse, or a business operation is irreversible. Update the chosen method, stop rule, overlap estimate and recovery proof. Keep your original reasoning and note what evidence changed it.

Ask Codex to challenge your assumptions and propose one disconfirming observation. Then check the current AWS service documentation yourself: AI suggestions are hypotheses, not a source of truth or evidence that the chosen deployment controller is enabled.

## Evidence boundary

These cases teach method selection and evidence design. The local HTTP canary exercise demonstrates one sequential loopback route with synthetic responses. Neither it nor this worksheet tests AWS weighted routing, CodeDeploy deployment events, load-balancer convergence, ECS capacity, real customer representativeness, current prices or safe production recovery. Any cloud exercise needs an approved scoped identity, a cost estimate within the project guardrails, a stop condition and verified cleanup.
