# Compute purchasing choices

Design-only cases for [Unit 02](../../reader/BOOK-LOCATORS.md#book-1516e4504105c6e0). No instance, Spot request, Reserved Instance or Savings Plan is purchased. Treat all workloads as fictional.

For each case, recommend a provisional purchasing path, name a credible alternative, identify the cost or capacity promise, and state what evidence could change the choice. Do not calculate a savings percentage from memory. Compare a dated, selected-Region estimate against the same On-Demand workload, and name unknowns.

## Cases

1. **Learning sandbox:** A team is testing a new worker. Some weeks it runs for an hour; other weeks it is unused. The program and capacity need may change next month. What is the useful baseline, and what evidence should exist before any term commitment?
2. **Restartable image batch:** A backlog contains independent images. Each image can be retried from durable input, and a partial result is discarded safely. The deadline tolerates capacity changing during the job. When could Spot fit, and what still must be tested about retry, checkpoint, interruption and available capacity?
3. **Steady service:** A customer worker has six months of reliable hourly history, an approved forecast, and a stable support window. Compare On-Demand, a Savings Plan and an EC2 Reserved Instance. What usage attributes, term, Region, service eligibility and downside must be checked before a commitment?
4. **Capacity promise:** A launch requires a particular EC2 type to be available in one Availability Zone during a scheduled event. Separate the billing-discount question from the physical-capacity question. What does a regional RI promise? What additional promise does a zonal RI make? What would unused reserved capacity cost?

## Record the decision

| Field | Your answer |
|---|---|
| Workload and business promise | |
| Known steady demand and quiet periods | |
| Interruption, retry and capacity tolerance | |
| On-Demand baseline Region/date | |
| Candidate option and matched usage eligibility | |
| Commitment or reservation scope/term | |
| Estimate source and cost if usage falls | |
| Evidence that would reverse the choice | |
| Stop, owner and cleanup plan | |

Ask Codex to challenge the workload assumptions and look for a hidden fixed obligation. Verify claims against current AWS documentation yourself. The output is a design exercise; it is not an AWS quote or a purchasing recommendation.
