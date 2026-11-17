# Assessor notes: compute purchasing choices

The case is graded on matching the payment mechanism to the workload promise, not on naming a discounted option.

1. **Learning sandbox:** On-Demand is a reasonable baseline because utilization and future shape are unknown. The learner should not turn a short, variable experiment into a multi-year obligation to chase a lower displayed rate.
2. **Restartable image batch:** Spot can be a candidate because work is independent and retryable. The answer must still design durable input, partial-output handling, interruption response, retry limits and adequate alternate capacity. Spot availability is not guaranteed; cost savings do not establish that the deadline will be met.
3. **Steady service:** The history and forecast may justify comparing a Savings Plan and matching RI against On-Demand, but six months alone does not prove a long-term requirement. Check term, eligible services, family/Region/platform attributes, effective usage, payment option and change risk. Model unused commitment cost. The learner may reasonably defer a purchase if the forecast or owner approval is insufficient.
4. **Capacity promise:** A regional RI supplies a billing discount but does not reserve capacity. A zonal RI is scoped to an Availability Zone and includes a capacity reservation under its matching attributes. Unused capacity remains billable. A separate EC2 Capacity Reservation may be relevant for a capacity requirement; its cost and configuration need their own review.

Strong answers distinguish a rate discount, a usage commitment, interruptible spare capacity and an actual capacity reservation. They do not assume Savings Plans, RI benefits, credits or Spot can be combined arbitrarily. Validate current eligibility and the exact account/Region before acting. No live purchase or account-specific price was checked.
