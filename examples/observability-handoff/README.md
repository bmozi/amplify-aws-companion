# Hand over an incident without hiding uncertainty

This is a fictional, design-only assessment after unit 8. Run the linked local drills first, then work from the evidence below without opening AWS or sending notifications. It is not an account incident or a certification practice question copied from an exam.

## The situation

Maya's repair-booking service promises to assign a technician within 30 seconds after accepting an eligible request. At event time 60, the next operator takes over. A dashboard is green because the web process answers its health endpoint and the received queue readings are all zero. Two customers report delayed assignments. The outgoing operator proposes restarting all workers and declaring recovery when the health endpoint returns 200.

All seconds below use the same fictional clock. The accepted-job inventory is stipulated complete for these four jobs; completion evidence is authoritative up to time 60. These are assumptions supplied for the exercise, not facts a production operator may assume.

| Job | Accepted at | Assignment recorded at |
| --- | ---: | ---: |
| A | 0 | 20 |
| B | 0 | 40 |
| C | 0 | No assignment by time 60 |
| D | 50 | No assignment by time 60 |

The handoff packet also contains:

| Evidence | What was observed |
| --- | --- |
| Process health | A probe at time 60 returned HTTP 200 |
| Capacity | A controlled local drill showed a full business-operation slot can coexist with health 200; this does not measure the live fictional service's current slots |
| Queue telemetry | One depth reading is expected each second in [0, 60); readings for seconds 10–59 arrived and each is zero; readings for seconds 0–9 are missing |
| Publication | Release R2 occurred at time 15; no controlled comparison or causal finding exists |
| Notification | Sending alert N7 returned 503; the sender recorded an attempt but has no accepted receipt |
| Proposed instrumentation | Add every job ID as a metric dimension and retain all logs for one hour |
| Support requirement | An operator must be able to investigate the previous business day's delayed jobs |

The queue is shared with other workflows; its depth is not a count of only these four booking jobs. The complete booking-job inventory and incomplete shared-queue stream are different evidence sources. A defect in one does not automatically invalidate every other source, but real operators must verify their independence and freshness.

## Produce a one-page handoff

Write the following in ordinary language. Attach the few calculations needed to support it.

1. State what is known about the customer promise at time 60. Identify the eligible mature cohort, the on-time fraction, late completed work, overdue unfinished work and work not yet due. Give unfinished count and oldest unfinished age separately.
2. Explain exactly what the process-health probe and the received queue observations establish. State which whole-minute claims remain unknown. Do not replace missing readings with zeros.
3. Offer two plausible explanations for delayed assignment, each with a read-only observation that could help distinguish it. Explain why the release timestamp alone does not establish cause and why the capacity drill is not a current service measurement.
4. Record the notification state and a bounded recovery action for that delivery path. Name an owner and fallback route as proposed roles, not actual people you have contacted. Define what receipt and human acknowledgment would establish separately.
5. Revise the instrumentation proposal so it supports next-day investigation without unlimited metric identities. Specify which details belong in controlled events, the retention requirement, and the cost categories to estimate before any cloud run. Do not invent a universal retention duration or a current price.
6. Define recovery evidence for customer outcomes, telemetry completeness and notification delivery separately. Decide whether restarting every worker is justified by this packet. Describe the next observation and the conditions under which a bounded intervention would become justified.

Then request a critique from Codex: “Identify every sentence in this handoff that claims more than the packet proves. Recompute the cohort, list missing observations, and distinguish a proposed action from a completed action. Do not deploy, send messages or assume root cause.” Accept corrections only after checking them against the evidence.

## Change one fact

The missing queue readings arrive: every reading for seconds 0–9 has depth 60. Revise only the conclusions affected by that evidence. Calculate the complete minute's average and maximum. Does this establish which jobs were waiting, how many distinct jobs arrived, why assignment was delayed, or whether anyone received N7?

Compare your answer with [assessor notes](ASSESSOR.md). Finish by naming one conclusion that changed and one that did not. This transfer check matters more than reproducing the wording of the sample answer.
