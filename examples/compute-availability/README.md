# Set an availability class from the business promise

This original design exercise supports SAA-C03 task 4.2 skill 04. It is not an exam question, SLO recommendation or tested AWS design. Do not create AWS resources for this exercise.

## Three requests from the same company

The owners call every system “important.” You are the architect and must turn that word into a service promise that can shape compute, data, recovery and cost decisions.

| Workload | Business schedule and consequence | Starting requirement (fictional) |
| --- | --- | --- |
| Customer booking site | Customers can book at any time; missed bookings lose revenue and trust | 99.9% monthly availability over a continuous 30-day month; continue accepting correct bookings through one Availability Zone loss; if a full regional event stops service, restore useful booking within four hours; do not lose confirmed bookings |
| Training sandbox | Six announced, internal classes each month; exercises use disposable identities and synthetic data | Must be usable at class start; after failure, an operator may rebuild it within one hour; it can be stopped outside class windows; retain the instructor's versioned lesson files, not disposable learner data |
| Overnight image/report jobs | Customers can upload until 2 a.m.; reports are needed by 6 a.m. | Accepted work must remain durable; workers may restart; all due reports must finish by 6 a.m.; a per-worker outage is acceptable if the queue drains in time |

These starting requirements are intentionally incomplete. The booking target's measurement rules, the class schedule's change process and the report workload's worst-case size are not yet defined. Identify each unknown instead of inventing an answer.

## Your design task

1. Rewrite each row as a testable customer or operator promise. Specify the measurement window, successful outcome, planned quiet time, allowed interruption, deadline, data-loss limit and recovery point.
2. For the 30-day continuous booking window, calculate the unavailable-minute allowance implied by 99.9%. Compare it with 99.99%, then explain why arithmetic alone does not show the architecture achieves either value.
3. Separate availability, RTO, RPO and batch completion deadline. Give one example of how a design could meet one measure and fail another.
4. For the booking site, draw the complete request path: DNS/entry, load balancing, compute, identity, data and any required external service. Mark a failure in one Availability Zone. State whether the remaining path is still correct and whether it has enough peak capacity.
5. Compare three candidate strategies at a design level: (a) one-zone compute with restore/rebuild, (b) compute distributed across multiple zones with enough surviving capacity, and (c) multi-region recovery. For each, identify the failed event it handles, what it still cannot handle, ongoing/capacity cost drivers and operating burden. Do not assume multi-region is required just because multi-AZ is required.
6. For the sandbox, decide what must be available during class and what can be stopped or rebuilt outside class. Include versioned teaching artifacts, restore steps, credentials, deployment configuration and the human who can perform the recovery. Keep isolation/security requirements separate from availability.
7. For the batch workload, estimate the worst-case accepted work, worker throughput, startup/replacement delay, retry allowance and time remaining before 6 a.m. State whether a zone outage still leaves enough time and capacity. Unknown load or duration is not zero.
8. Revisit the sandbox after the business announces a live customer showcase with attendees booking appointments. State which availability, isolation, data and recovery requirements change and which existing components must be reviewed.
9. Ask Codex to challenge your choices by removing one dependency, changing the failure to a whole-Region outage, and shifting the class start forward by 30 minutes. Require it to label fictional assumptions, business-approved requirements and evidence that remains untested.

## Decision worksheet

| Question | Booking site | Training sandbox | Overnight batch |
| --- | --- | --- | --- |
| Who is affected by interruption? | | | |
| Required service window | | | |
| Success definition and measurement window | | | |
| Accepted interruption / availability target | | | |
| RTO and RPO, if applicable | | | |
| Completion deadline, if applicable | | | |
| Failure domains covered | | | |
| Surviving capacity or rebuild plan | | | |
| State, queue and external dependencies | | | |
| Cost drivers and operating owner | | | |
| Evidence that would change the design | | | |

## Cost guardrail

This is a paper exercise. No AWS resources, availability measurements, service quotas or account costs are queried or changed. If a later live test is separately authorized, verify the scoped non-root identity, estimate the whole run against spending and reserve limits chosen for that account, and identify cleanup before deployment.

## Evidence boundary

The completed worksheet establishes only that you can articulate a provisional availability design and its unknowns. It does not establish an AWS service SLA, configured multi-AZ behavior, enough capacity after a failure, tested failover, measured RTO/RPO, complete cost, independent technical review or learner mastery. Read the [assessor guide](ASSESSOR.md) after recording your first design.
