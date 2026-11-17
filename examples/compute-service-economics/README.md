# Compare the cost of compute that can actually do the job

This original design exercise supports SAA-C03 task 4.2 skill 03. It is not an AWS exam question or a live price quote. Complete it with the current [AWS Pricing Calculator](https://calculator.aws/) and official service pricing pages; do not create AWS resources.

## The situation

A small online shop runs an image-resizing job after customers upload product photos. A queue can hold work while workers are busy. The same image-processing program has been packaged as a container, and the team also has a function-compatible version. The team is considering three bounded candidates:

- a standard Lambda event function invoked by the queue;
- an ECS task on Fargate that reads from the queue;
- an EC2 On-Demand worker group that reads from the queue.

For this exercise, assume the current program can run correctly on all three candidates. This is a deliberate simplification, not evidence of real compatibility. Each candidate must process the same work and meet the same customer promise. Do not use Lambda Managed Instances in the first comparison; add it as a fourth candidate only if you have time to investigate its separate operating and pricing model.

## Workload card

Use these fictional planning inputs for all three candidates:

| Input | Planning assumption |
| --- | --- |
| Work processed | 120,000 images each month |
| Work distribution | 90% arrives between 8 a.m. and 8 p.m.; the other 10% arrives overnight |
| Function work per image | 2.5 seconds at 1 GiB, if the function version's configured memory produces this duration |
| Container or instance worker | One worker handles one image in 2.5 seconds at its proposed resource size |
| Deadline | Each image should finish within 10 minutes of entering the queue during normal demand |
| Retries | Budget for 2% extra processing attempts; explain how poison work is contained |
| Region | Choose one Region and record it; do not mix regional prices |
| External traffic | The result is stored in S3; include only required data movement and services in your estimate |
| Availability | A single-AZ outage must not lose accepted work; recovery time is not yet agreed |

The duration and throughput are hypothetical. In a real design, measure representative image sizes, initialization, memory, queue delay, retry rate, task/instance startup and S3 access. If one candidate needs different resources or time to meet the promise, use its measured values instead of forcing equal settings.

## Your investigation

1. Write one sentence that states the customer promise and one sentence that states the missing evidence.
2. Check eligibility before cost. For each candidate, record runtime/duration/resource limits, queue integration, startup, retry behavior, interruption/recovery, network path and multi-AZ design evidence you still need.
3. Choose a Region. Record the date you checked prices, the candidate mode, OS and CPU architecture. Treat those as part of the estimate rather than hidden defaults.
4. Estimate each candidate in the AWS Pricing Calculator for one month. Start with compute. Then add the needed queue, S3 requests/storage, logs, network, addresses, image storage, load balancing or other supporting services. Mark each omitted item and explain why it is outside the comparison.
5. Model idle time and peak demand. For EC2 and Fargate, state the minimum number of workers/tasks that stay ready, the scale-out delay and how long excess capacity remains after a burst. For Lambda, check the selected function mode and any provisioned capacity or event-poller charges that apply.
6. Add one failure case: 2% retries increase work; a single-AZ event affects capacity; and a poison image repeatedly fails. Describe both the extra billable work and customer impact.
7. Compare results in a table. Keep estimate source, Region, date, workload assumptions, compute subtotal, surrounding-service subtotal, total and excluded items together. Do not rank candidates using only the compute subtotal.
8. Add operational effort: who patches images and dependencies, host operating systems (if any), queue consumers, permissions, alarms, recovery procedures and cleanup. State whether the team can perform that work reliably.
9. Recommend a provisional candidate, reject one alternative with a specific reason, and name one measured observation that would reverse your decision.
10. Ask Codex to produce an independent competing estimate plan. Require it to show the workload arithmetic, exact service mode, Region, pricing source links, included components and exclusions. Verify its current price claims yourself; an AI-generated estimate is not a quote.

## Comparison worksheet

Copy and fill this table. A missing input is “unknown,” not zero.

| Measure | Lambda event function | ECS on Fargate | EC2 On-Demand |
| --- | --- | --- | --- |
| Eligible for the promise? Evidence or unknowns | | | |
| Required configuration and monthly work | | | |
| Compute pricing dimensions | | | |
| Supporting AWS services and costs | | | |
| Peak and quiet-period capacity | | | |
| Retry/outage effect | | | |
| Monthly estimate, Region and date | | | |
| Operating work and failure recovery | | | |
| Reversal condition | | | |

## Cost guardrail

This is a calculator-only exercise. Do not deploy to “validate” a spreadsheet. For a later, separately approved run, use a scoped non-root identity, record a conservative whole-run estimate against limits chosen for the account, define a stop condition, and identify every resource to remove. Promotional credits do not make an unestimated design cost-free.

## What this exercise proves

The worksheet can show whether your comparison uses a common workload, current selected service modes, a recorded Region and date, and explicit cost exclusions. It cannot prove measured application performance, final production compatibility, an account-specific bill, learner mastery or the best service for every workload. Read [assessor notes](ASSESSOR.md) only after writing your own decision.
